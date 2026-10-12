"""
RelayZero Evidence Reconciliation Engine.
Performs cross-source claim clustering, detects direct factual contradictions,
flags missing critical operational slots, and computes corroboration matrices.
"""

from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from .schemas import (
    ExtractedClaim,
    ClaimCluster,
    ClusterStatusEnum,
    OperatorStatusEnum,
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

    def reconcile(self, claims: List[ExtractedClaim]) -> Tuple[List[ClaimCluster], List[str]]:
        """
        Groups claims by slot field, evaluates corroboration vs conflict,
        and returns the active clusters alongside missing critical fields.
        """
        field_map = defaultdict(list)
        for claim in claims:
            # Skip claims explicitly rejected by the human operator
            if claim.operator_status == OperatorStatusEnum.REJECTED:
                continue
            field_map[claim.field].append(claim)

        clusters: List[ClaimCluster] = []
        observed_fields = set(field_map.keys())

        # Evaluate observed fields
        for field, slot_claims in field_map.items():
            cluster = self._evaluate_field_cluster(field, slot_claims)
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

    def _evaluate_field_cluster(self, field: str, claims: List[ExtractedClaim]) -> ClaimCluster:
        cluster_id = f"CLUS-{field.upper()}"
        is_critical = field in self.critical_fields

        if len(claims) == 1:
            claim = claims[0]
            val = claim.operator_edited_value or claim.normalized_value
            return ClaimCluster(
                cluster_id=cluster_id,
                field=field,
                status=ClusterStatusEnum.SINGLE_SOURCE,
                claims=claims,
                reconciled_value=val,
                conflict_explanation="Single source report — awaiting independent corroboration.",
                is_critical_field=is_critical,
            )

        # Check for conflicts across claims
        distinct_values = {}
        for c in claims:
            val = (c.operator_edited_value or c.normalized_value).strip().lower()
            distinct_values[val] = c

        # If human operator already confirmed a specific claim, that value overrides
        confirmed_claims = [c for c in claims if c.operator_status == OperatorStatusEnum.CONFIRMED]
        if confirmed_claims:
            chosen = confirmed_claims[0]
            val = chosen.operator_edited_value or chosen.normalized_value
            return ClaimCluster(
                cluster_id=cluster_id,
                field=field,
                status=ClusterStatusEnum.CORROBORATED,
                claims=claims,
                reconciled_value=val,
                conflict_explanation=f"Resolved by operator {chosen.operator_status.value.upper()}.",
                operator_resolution=val,
                is_critical_field=is_critical,
            )

        # Evaluate if distinct values represent true contradictions
        is_conflict, explanation = self._detect_contradiction(field, claims)

        if is_conflict:
            return ClaimCluster(
                cluster_id=cluster_id,
                field=field,
                status=ClusterStatusEnum.CONFLICT,
                claims=claims,
                reconciled_value=None,  # Refuse to invent answer on conflict!
                conflict_explanation=explanation,
                is_critical_field=is_critical,
            )
        else:
            # Corroborated
            reconciled = claims[0].operator_edited_value or claims[0].normalized_value
            return ClaimCluster(
                cluster_id=cluster_id,
                field=field,
                status=ClusterStatusEnum.CORROBORATED,
                claims=claims,
                reconciled_value=reconciled,
                conflict_explanation=f"Corroborated by {len(claims)} independent sources.",
                is_critical_field=is_critical,
            )

    def _detect_contradiction(self, field: str, claims: List[ExtractedClaim]) -> Tuple[bool, str]:
        """Examines field semantics to detect factual divergence."""
        sources = [c.source_id for c in claims]
        values = [c.normalized_value for c in claims]

        if field == "location_primary":
            # e.g., North Portal vs South Portal
            has_north = any("north" in v.lower() or "nord" in v.lower() for v in values)
            has_south = any("south" in v.lower() or "sud" in v.lower() for v in values)
            if has_north and has_south:
                return (
                    True,
                    f"Direct location contradiction: {sources[0]} reports North Entrance whereas {sources[1]} reports South Entrance.",
                )

        if field in ("affected_count", "casualty_count"):
            # e.g., 20 persons vs 12 persons
            nums = []
            for v in values:
                digits = "".join([ch for ch in v if ch.isdigit()])
                if digits:
                    nums.append(int(digits))
            if len(set(nums)) > 1:
                return (
                    True,
                    f"Conflicting casualty/headcount figures: values range between {min(nums)} and {max(nums)} across sources {', '.join(sources)}.",
                )

        if field == "time_occurred":
            times = set(v.lower().strip() for v in values)
            if len(times) > 1:
                return (
                    True,
                    f"Temporal discrepancy: reports record conflicting incident onset times ({', '.join(times)}).",
                )

        # Generic value equality check
        canonical = [v.strip().lower() for v in values]
        if len(set(canonical)) > 1:
            return (
                True,
                f"Contradictory claims observed across sources {', '.join(sources)}: {'; '.join(set(values))}",
            )

        return False, ""
