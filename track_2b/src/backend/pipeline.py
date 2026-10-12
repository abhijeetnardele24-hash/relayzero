"""
RelayZero Multi-Stage Incident Compilation Pipeline.
Executes Stages A, B, C, and D with strict evidence span validation
and distinct confirmation boundaries.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional

from .schemas import (
    Incident,
    ExtractedClaim,
    ClaimCluster,
    SituationBrief,
    ClusterStatusEnum,
    OperatorClaimStatusEnum,
    ChecksummedExportBundle,
    ExtractionStatusEnum,
    EvidenceSpan,
    EgressStatusEnum,
)
from .apertus_adapter import ApertusAdapter, find_and_validate_span
from .reconciliation import ReconciliationEngine
from .audit import AuditLogger


class IncidentPipeline:
    def __init__(self, adapter: Optional[ApertusAdapter] = None):
        self.adapter = adapter or ApertusAdapter()
        self.reconciliation_engine = ReconciliationEngine()
        # In-memory persistence of operator cluster resolutions per incident
        self.cluster_resolutions_store: Dict[str, Dict[str, str]] = {}

    def set_cluster_resolution(self, incident_id: str, cluster_id: str, resolved_value: str):
        if incident_id not in self.cluster_resolutions_store:
            self.cluster_resolutions_store[incident_id] = {}
        self.cluster_resolutions_store[incident_id][cluster_id] = resolved_value

    def get_cluster_resolutions(self, incident_id: str) -> Dict[str, str]:
        return self.cluster_resolutions_store.get(incident_id, {})

    async def execute_stage_a_extraction(self, incident: Incident, audit: AuditLogger) -> List[ExtractedClaim]:
        """
        Stage A: Extract structured claims independently from each source report.
        Strictly validates evidence spans against source text.
        """
        all_claims: List[ExtractedClaim] = []
        claim_counter = 1

        for report in incident.sources:
            extraction_result = await self.adapter.extract_claims_from_report(
                report_id=report.report_id,
                incident_id=incident.incident_id,
                content=report.raw_content,
                language=report.language.value,
                modality=report.modality.value,
            )

            claims_data = extraction_result.get("parsed_json", {}).get("claims", [])
            for c_raw in claims_data:
                quote = c_raw.get("exact_quote") or c_raw.get("original_value") or ""
                span = find_and_validate_span(report.raw_content, quote)

                extraction_status = ExtractionStatusEnum.ACCEPTED
                if not span:
                    # If span cannot be found in source, flag as review required
                    extraction_status = ExtractionStatusEnum.REVIEW_REQUIRED
                    # Fallback slice for schema validation
                    fallback_quote = report.raw_content[:min(30, len(report.raw_content))]
                    span = EvidenceSpan(
                        exact_quote=fallback_quote,
                        start_char=0,
                        end_char=len(fallback_quote),
                    )

                claim = ExtractedClaim(
                    claim_id=f"CLM-{claim_counter:03d}",
                    incident_id=incident.incident_id,
                    source_id=report.report_id,
                    field=c_raw.get("field", "unknown_field"),
                    normalized_value=c_raw.get("normalized_value", ""),
                    original_value=c_raw.get("original_value", span.exact_quote),
                    evidence_span=span,
                    language=report.language,
                    confidence=c_raw.get("confidence"),  # None if omitted
                    extraction_status=extraction_status,
                    operator_status=OperatorClaimStatusEnum.UNREVIEWED,
                    model_name=extraction_result.get("model_name", self.adapter.get_effective_model_identifier()),
                    prompt_version="v1.2-airgap-strict",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                all_claims.append(claim)
                claim_counter += 1

        audit.log(
            action="STAGE_A_EXTRACTION_COMPLETED",
            actor=self.adapter.get_effective_model_identifier(),
            details={
                "extracted_claims_count": len(all_claims),
                "sources_processed": len(incident.sources),
                "app_mode": self.adapter.app_mode.value,
            },
        )
        return all_claims

    def execute_stage_b_reconciliation(
        self, incident: Incident, claims: List[ExtractedClaim], audit: AuditLogger
    ) -> List[ClaimCluster]:
        """
        Stage B: Compares claims, detects contradictions, identifies missing critical fields,
        and applies persistent cluster resolutions.
        """
        existing_res = self.get_cluster_resolutions(incident.incident_id)
        clusters, missing_fields = self.reconciliation_engine.reconcile(claims, existing_res)

        conflicts = [c for c in clusters if c.status == ClusterStatusEnum.CONFLICTING]
        corroborated = [c for c in clusters if c.status in (ClusterStatusEnum.CORROBORATED, ClusterStatusEnum.OPERATOR_CONFIRMED)]

        audit.log(
            action="STAGE_B_RECONCILIATION_COMPLETED",
            actor="RelayZero-ReconciliationEngine",
            details={
                "total_clusters": len(clusters),
                "conflicts_count": len(conflicts),
                "corroborated_or_confirmed_count": len(corroborated),
                "missing_critical_fields": missing_fields,
            },
        )
        return clusters

    def execute_stage_c_brief(
        self,
        incident: Incident,
        clusters: List[ClaimCluster],
        audit: AuditLogger,
    ) -> SituationBrief:
        """
        Stage C: Generates grounded situation brief.
        Confirmed facts contain ONLY operator_confirmed or corroborated facts.
        Single-source claims are kept separate under unverified_single_source_facts.
        """
        confirmed_facts: Dict[str, str] = {}
        unverified_single_source: Dict[str, str] = {}
        unresolved_conflicts: List[str] = []
        critical_missing: List[str] = []
        priorities: List[str] = []

        for cluster in clusters:
            if cluster.status in (ClusterStatusEnum.OPERATOR_CONFIRMED, ClusterStatusEnum.CORROBORATED) and cluster.reconciled_value:
                confirmed_facts[cluster.field] = cluster.reconciled_value
            elif cluster.status == ClusterStatusEnum.SINGLE_SOURCE_UNVERIFIED and cluster.reconciled_value:
                unverified_single_source[cluster.field] = cluster.reconciled_value
            elif cluster.status == ClusterStatusEnum.CONFLICTING:
                unresolved_conflicts.append(f"{cluster.field.upper()}: {cluster.conflict_explanation}")
            elif cluster.status == ClusterStatusEnum.MISSING:
                critical_missing.append(cluster.field)

        # Summary lines
        summary_lines = []
        inc_type = confirmed_facts.get("incident_type") or unverified_single_source.get("incident_type", "Operational Incident")
        loc = confirmed_facts.get("location_primary") or unverified_single_source.get("location_primary", "Unverified location")
        hazard = confirmed_facts.get("hazard_status") or unverified_single_source.get("hazard_status", "Active hazard")

        summary_lines.append(f"INCIDENT: {inc_type.upper().replace('_', ' ')}.")
        summary_lines.append(f"LOCATION: {loc}.")
        summary_lines.append(f"HAZARD: {hazard}.")

        if unresolved_conflicts:
            summary_lines.append(f"CRITICAL WARNING: {len(unresolved_conflicts)} contradiction(s) require operator resolution.")
            for conf in unresolved_conflicts:
                priorities.append(f"RESOLVE CONFLICT: {conf}")

        if critical_missing:
            summary_lines.append(f"DATA GAP: Missing verified reports for: {', '.join(critical_missing)}.")
            for miss in critical_missing:
                priorities.append(f"FIELD RECONNAISSANCE: Collect data on '{miss}'.")

        executive_summary = " ".join(summary_lines)

        multilingual = {
            "de": f"LAGEBERICHT: {inc_type}. Status: {hazard}. " + (f"Widerspruch: {unresolved_conflicts[0]}" if unresolved_conflicts else "Fakten konsolidiert."),
            "fr": f"BULLETIN DE SITUATION: {inc_type}. État: {hazard}. " + (f"Contradiction: {unresolved_conflicts[0]}" if unresolved_conflicts else "Faits corroborés."),
            "it": f"BOLLETTINO OPERATIVO: {inc_type}. Condizione: {hazard}. " + (f"Conflitto: {unresolved_conflicts[0]}" if unresolved_conflicts else "Fatti consolidati."),
            "en": executive_summary,
        }

        brief = SituationBrief(
            incident_id=incident.incident_id,
            title=f"Tactical Situation Brief — {incident.title}",
            executive_summary=executive_summary,
            confirmed_facts=confirmed_facts,
            unverified_single_source_facts=unverified_single_source,
            unresolved_conflicts=unresolved_conflicts,
            critical_missing_fields=critical_missing,
            recommended_priorities=priorities,
            multilingual_summaries=multilingual,
            generated_at=datetime.now(timezone.utc).isoformat(),
            model_name=self.adapter.get_effective_model_identifier(),
            approved_by_operator=False,
        )

        audit.log(
            action="STAGE_C_BRIEF_GENERATED",
            actor="RelayZero-BriefCompiler",
            details={
                "confirmed_facts_count": len(confirmed_facts),
                "unverified_single_source_count": len(unverified_single_source),
                "unresolved_conflicts_count": len(unresolved_conflicts),
                "critical_missing_count": len(critical_missing),
            },
        )
        return brief

    def execute_stage_d_export(
        self,
        incident: Incident,
        audit: AuditLogger,
        egress_status: EgressStatusEnum = EgressStatusEnum.UNVERIFIED,
    ) -> ChecksummedExportBundle:
        """
        Stage D: Generates canonical checksummed tamper-evident bundle.
        """
        export_time = datetime.now(timezone.utc).isoformat()
        bundle_id = f"EXP-{incident.incident_id}-{int(datetime.now().timestamp())}"

        data_dict = incident.model_dump(mode="json")
        audit_manifest = [entry.model_dump(mode="json") for entry in audit.trail]

        payload_to_hash = {
            "bundle_id": bundle_id,
            "incident_id": incident.incident_id,
            "exported_at": export_time,
            "app_mode": incident.app_mode.value,
            "incident_data": data_dict,
            "audit_manifest": audit_manifest,
        }
        serialized = json.dumps(payload_to_hash, sort_keys=True)
        sha256_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        bundle = ChecksummedExportBundle(
            bundle_id=bundle_id,
            incident_id=incident.incident_id,
            exported_at=export_time,
            system_version="RelayZero v1.0.0",
            app_mode=incident.app_mode,
            model_name=self.adapter.get_effective_model_identifier(),
            egress_verification=egress_status,
            incident_data=data_dict,
            audit_manifest=audit_manifest,
            sha256_checksum=sha256_hash,
        )

        audit.log(
            action="STAGE_D_BUNDLE_EXPORTED",
            actor="RelayZero-ExportEngine",
            details={
                "bundle_id": bundle_id,
                "sha256_checksum": sha256_hash,
                "app_mode": incident.app_mode.value,
                "egress_verification": egress_status.value,
            },
        )
        return bundle
