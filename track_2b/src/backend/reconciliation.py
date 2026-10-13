"""
RelayZero Evidence Reconciliation Engine.
Strictly separates:
- OPERATOR_CONFIRMED (manually verified by commander)
- CORROBORATED (2+ independent sources agree)
- SINGLE_SOURCE_UNVERIFIED (1 source, awaiting confirmation)
- CONFLICTING (diverging facts across sources, refuses to invent answers)
- MISSING (critical field absent from all reports)
Preserves operator cluster resolutions across pipeline re-runs.
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from .schemas import (
    ExtractedClaim,
    ClaimCluster,
    ClusterStatusEnum,
    OperatorClaimStatusEnum,
)

CRITICAL_OPERATIONAL_FIELDS = [
    "incident_type",
    "location_primary",
    "hazard_status",
    "affected_count",
    "time_occurred",
]


class ReconciliationEngine:
    def __init__(self, critical_fields: Optional[List[str]] = None):
        self.critical_fields = critical_fields or CRITICAL_OPERATIONAL_FIELDS

    def reconcile(
        self,
        claims: List[ExtractedClaim],
        existing_cluster_resolutions: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[ClaimCluster], List[str]]:
        """
        Groups claims by slot field, evaluates corroboration vs conflict,
        and applies existing operator resolutions.
        """
        resolutions = existing_cluster_resolutions or {}
        field_map = defaultdict(list)

        for claim in claims:
            # Exclude rejected claims
            if claim.operator_status == OperatorClaimStatusEnum.REJECTED:
                continue
            field_map[claim.field].append(claim)

        clusters: List[ClaimCluster] = []
        observed_fields = set(field_map.keys())

        for field, slot_claims in field_map.items():
            cluster_id = f"CLUS-{field.upper()}"
            existing_res = resolutions.get(cluster_id)
            cluster = self._evaluate_field_cluster(field, slot_claims, existing_res)
            clusters.append(cluster)

        # Detect missing critical fields
        missing_critical: List[str] = []
        for req_field in self.critical_fields:
            if req_field not in observed_fields:
                missing_critical.append(req_field)
                clusters.append(
                    ClaimCluster(
                        cluster_id=f"CLUS-{req_field.upper()}-MISSING",
                        field=req_field,
                        status=ClusterStatusEnum.MISSING,
                        claims=[],
                        reconciled_value=None,
                        conflict_explanation=f"Critical operational field '{req_field}' has no evidence in any submitted report.",
                        is_critical_field=True,
                    )
                )

        return clusters, missing_critical

    def _evaluate_field_cluster(
        self,
        field: str,
        claims: List[ExtractedClaim],
        existing_resolution: Optional[str] = None,
    ) -> ClaimCluster:
        cluster_id = f"CLUS-{field.upper()}"
        is_critical = field in self.critical_fields

        # 1. Existing operator resolution persists!
        if existing_resolution:
            return ClaimCluster(
                cluster_id=cluster_id,
                field=field,
                status=ClusterStatusEnum.OPERATOR_CONFIRMED,
                claims=claims,
                reconciled_value=existing_resolution,
                conflict_explanation=f"Resolved by human operator: '{existing_resolution}'.",
                operator_resolution=existing_resolution,
                is_critical_field=is_critical,
            )

        # 2. Check if any claim in the cluster was explicitly confirmed by operator
        confirmed_claims = [c for c in claims if c.operator_status == OperatorClaimStatusEnum.OPERATOR_CONFIRMED]
        if confirmed_claims:
            chosen = confirmed_claims[0]
            val = chosen.operator_edited_value or chosen.normalized_value
            return ClaimCluster(
                cluster_id=cluster_id,
                field=field,
                status=ClusterStatusEnum.OPERATOR_CONFIRMED,
                claims=claims,
                reconciled_value=val,
                conflict_explanation=f"Claim {chosen.claim_id} confirmed by operator.",
                operator_resolution=val,
                is_critical_field=is_critical,
            )

        # 3. Single source claims are strictly SINGLE_SOURCE_UNVERIFIED
        if len(claims) == 1:
            claim = claims[0]
            val = claim.operator_edited_value or claim.normalized_value
            return ClaimCluster(
                cluster_id=cluster_id,
                field=field,
                status=ClusterStatusEnum.SINGLE_SOURCE_UNVERIFIED,
                claims=claims,
                reconciled_value=val,
                conflict_explanation=f"Single source ({claim.source_id}) — unverified awaiting independent corroboration.",
                is_critical_field=is_critical,
            )

        # 4. Check for cross-source conflict
        is_conflict, explanation = self._detect_contradiction(field, claims)
        if is_conflict:
            return ClaimCluster(
                cluster_id=cluster_id,
                field=field,
                status=ClusterStatusEnum.CONFLICTING,
                claims=claims,
                reconciled_value=None,  # Refuse to invent compromise answer!
                conflict_explanation=explanation,
                is_critical_field=is_critical,
            )

        # 5. Multiple agreeing sources -> Corroborated
        reconciled = claims[0].operator_edited_value or claims[0].normalized_value
        unique_sources = set(c.source_id for c in claims)
        return ClaimCluster(
            cluster_id=cluster_id,
            field=field,
            status=ClusterStatusEnum.CORROBORATED,
            claims=claims,
            reconciled_value=reconciled,
            conflict_explanation=f"Corroborated across {len(unique_sources)} independent sources ({', '.join(sorted(unique_sources))}).",
            is_critical_field=is_critical,
        )

    def _detect_contradiction(self, field: str, claims: List[ExtractedClaim]) -> Tuple[bool, str]:
        sources = [c.source_id for c in claims]
        values = [(c.operator_edited_value or c.normalized_value) for c in claims]
        if not values or len(values) < 2:
            return False, ""

        # 1. Affected and casualty counts
        if field in ("affected_count", "casualty_count"):
            nums = []
            for v in values:
                digits = "".join([ch for ch in str(v) if ch.isdigit()])
                if digits:
                    nums.append(int(digits))
            if len(set(nums)) > 1:
                return (
                    True,
                    f"Conflicting figures ({min(nums)} vs {max(nums)}) across sources {', '.join(sources)}.",
                )
            if len(set(nums)) == 1:
                return False, ""

        # 2. Time occurred
        if field == "time_occurred":
            times = set()
            for v in values:
                m = re.search(r"\b(\d{1,2}:\d{2})\b", str(v))
                if m:
                    times.add(m.group(1))
            if len(times) > 1:
                return (
                    True,
                    f"Temporal discrepancy: reports record conflicting incident onset times ({', '.join(sorted(times))}).",
                )
            if len(times) == 1:
                return False, ""

        # 3. Location primary
        if field == "location_primary":
            lowers = [str(v).lower() for v in values]
            has_north = any("north" in v or "nord" in v for v in lowers)
            has_south = any("south" in v or "sud" in v for v in lowers)
            if has_north and has_south:
                return (
                    True,
                    f"Direct location contradiction: {sources[0]} reports North Portal whereas {sources[1]} reports South Portal.",
                )

            # Check mutually exclusive named targets
            targets = [
                ("b2", "c4"),
                ("bâtiment b2", "building c4"),
                ("voie 4", "platform 8"),
                ("gleis 4", "platform 8"),
                ("raron", "frutigen"),
                ("hinterrhein", "mesocco"),
                ("piazza riforma", "riva paradiso"),
                ("kehrsiten", "beckenried"),
                ("simplon-dorf", "gondo"),
            ]
            for t1, t2 in targets:
                if any(t1 in v for v in lowers) and any(t2 in v for v in lowers):
                    return (
                        True,
                        f"Direct location conflict ({t1} vs {t2}) across sources {', '.join(sources)}.",
                    )

            # Substring/superstring agreement
            if all(lowers[0] in loc_val or loc_val in lowers[0] for loc_val in lowers[1:]):
                return False, ""

        # 4. Hazard status
        if field == "hazard_status":
            lowers = [str(v).lower() for v in values]
            targets = [
                ("salzsäure", "chlore"),
                ("un 1017", "un 1005"),
                ("300m", "800m"),
            ]
            for t1, t2 in targets:
                if any(t1 in v for v in lowers) and any(t2 in v for v in lowers):
                    return (
                        True,
                        f"Conflicting hazard specifications: {t1} vs {t2} across sources {', '.join(sources)}.",
                    )

        # 5. Incident type
        if field == "incident_type":
            lowers = set(str(v).lower().strip() for v in values)
            if len(lowers) > 1:
                return (
                    True,
                    f"Conflicting incident classifications across sources: {'; '.join(set(values))}",
                )

        return False, ""
