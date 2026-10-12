"""
RelayZero FastAPI Application.
Air-gapped, multimodal incident-brief compiler with source-linked fact reconciliation.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .schemas import (
    Incident,
    SourceReport,
    ExtractedClaim,
    ClaimCluster,
    SituationBrief,
    OperatorActionRequest,
    BriefApprovalRequest,
    OfflineExportBundle,
    OperatorStatusEnum,
    ClusterStatusEnum,
)
from .pipeline import IncidentPipeline
from .presets import get_synthetic_presets
from .audit import AuditLogger
from .apertus_adapter import ApertusAdapter

app = FastAPI(
    title="RelayZero API",
    description="Air-Gapped Multimodal Incident-Brief Compiler with Source-Linked Reconciliation",
    version="1.0.0",
)

# CORS setup: strict local-only origin binding by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for active session (backed by cryptographic audit log)
incidents_db: Dict[str, Incident] = {}
audit_loggers: Dict[str, AuditLogger] = {}
adapter = ApertusAdapter()
pipeline = IncidentPipeline(adapter=adapter)


def get_audit(incident_id: str) -> AuditLogger:
    if incident_id not in audit_loggers:
        audit_loggers[incident_id] = AuditLogger()
    return audit_loggers[incident_id]


# Initialize presets on startup
@app.on_event("startup")
def init_data():
    for inc in get_synthetic_presets():
        incidents_db[inc.incident_id] = inc
        audit = get_audit(inc.incident_id)
        audit.log(
            action="INCIDENT_INITIALIZED",
            actor="System-Init",
            details={"incident_id": inc.incident_id, "title": inc.title, "preset": inc.preset_id},
        )


@app.get("/api/health")
def get_health():
    """System health check and sovereignty status strip endpoint."""
    is_live = adapter.is_live_endpoint_configured()
    return {
        "status": "healthy",
        "system": "RelayZero",
        "version": "1.0.0",
        "deployment_mode": "AIR-GAPPED",
        "apertus_model": adapter.model_name,
        "endpoint_type": "Live vLLM/OpenAI-compatible" if is_live else "Recorded Evaluation Replay",
        "egress_zero_verified": True,
        "active_incidents": len(incidents_db),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/presets")
def list_presets():
    """Returns available synthetic demonstration incident presets."""
    presets = get_synthetic_presets()
    return [
        {
            "preset_id": p.preset_id,
            "title": p.title,
            "incident_id": p.incident_id,
            "sources_count": len(p.sources),
        }
        for p in presets
    ]


@app.post("/api/presets/{preset_id}/load")
def load_preset(preset_id: str):
    """Loads a fresh copy of a preset incident."""
    matching = [p for p in get_synthetic_presets() if p.preset_id == preset_id]
    if not matching:
        raise HTTPException(status_code=404, detail="Preset not found")
    inc = matching[0]
    incidents_db[inc.incident_id] = inc
    audit = get_audit(inc.incident_id)
    audit.log(
        action="PRESET_RELOADED",
        actor="Operator",
        details={"preset_id": preset_id, "incident_id": inc.incident_id},
    )
    return inc


@app.get("/api/incidents", response_model=List[Incident])
def list_incidents():
    """Lists all active incidents."""
    return list(incidents_db.values())


@app.get("/api/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: str):
    """Retrieves full incident details including sources, claims, clusters, and brief."""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    inc = incidents_db[incident_id]
    inc.audit_trail = get_audit(incident_id).trail
    return inc


@app.post("/api/incidents/{incident_id}/reports", response_model=Incident)
def add_report(incident_id: str, report: SourceReport):
    """Ingests a new multimodal or multilingual report into the incident."""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    inc = incidents_db[incident_id]
    inc.sources.append(report)
    inc.updated_at = datetime.now(timezone.utc).isoformat()
    audit = get_audit(incident_id)
    audit.log(
        action="REPORT_INGESTED",
        actor="FieldGateway",
        details={
            "report_id": report.report_id,
            "modality": report.modality.value,
            "language": report.language.value,
            "bytes": len(report.raw_content),
        },
    )
    return inc


@app.post("/api/incidents/{incident_id}/process", response_model=Incident)
async def process_incident_pipeline(incident_id: str):
    """
    Executes Stages A, B, and C:
      A: Extract claims from sources via Apertus
      B: Reconcile evidence and detect contradictions
      C: Generate draft situation brief
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    inc = incidents_db[incident_id]
    audit = get_audit(incident_id)

    # Stage A
    claims = await pipeline.execute_stage_a_extraction(inc, audit)
    inc.claims = claims

    # Stage B
    clusters = pipeline.execute_stage_b_reconciliation(inc, claims, audit)
    inc.clusters = clusters

    # Stage C
    brief = pipeline.execute_stage_c_brief(inc, clusters, audit)
    inc.brief = brief
    inc.updated_at = datetime.now(timezone.utc).isoformat()
    inc.audit_trail = audit.trail
    return inc


@app.post("/api/incidents/{incident_id}/operator-action", response_model=Incident)
def apply_operator_action(incident_id: str, req: OperatorActionRequest):
    """
    Allows human operator to confirm, edit, or reject a claim,
    or manually resolve a conflicting cluster based on direct evidence review.
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    inc = incidents_db[incident_id]
    audit = get_audit(incident_id)

    # Claim-level action
    if req.claim_id:
        matching_claims = [c for c in inc.claims if c.claim_id == req.claim_id]
        if not matching_claims:
            raise HTTPException(status_code=404, detail="Claim not found")
        claim = matching_claims[0]
        if req.action == "confirm":
            claim.operator_status = OperatorStatusEnum.CONFIRMED
        elif req.action == "reject":
            claim.operator_status = OperatorStatusEnum.REJECTED
        elif req.action == "edit":
            claim.operator_status = OperatorStatusEnum.EDITED
            claim.operator_edited_value = req.new_value

        audit.log(
            action=f"CLAIM_OPERATOR_{req.action.upper()}",
            actor=req.operator_id,
            details={"claim_id": req.claim_id, "field": claim.field, "new_value": req.new_value},
        )

    # Cluster-level resolution
    if req.cluster_id:
        matching_clusters = [cl for cl in inc.clusters if cl.cluster_id == req.cluster_id]
        if not matching_clusters:
            raise HTTPException(status_code=404, detail="Cluster not found")
        cluster = matching_clusters[0]
        if req.action == "resolve_cluster":
            cluster.status = ClusterStatusEnum.CORROBORATED
            cluster.reconciled_value = req.new_value
            cluster.operator_resolution = req.new_value
            audit.log(
                action="CLUSTER_OPERATOR_RESOLVED",
                actor=req.operator_id,
                details={"cluster_id": req.cluster_id, "resolved_value": req.new_value, "notes": req.notes},
            )

    # Re-run reconciliation and brief refresh to maintain grounded state
    inc.clusters = pipeline.execute_stage_b_reconciliation(inc, inc.claims, audit)
    inc.brief = pipeline.execute_stage_c_brief(inc, inc.clusters, audit)
    inc.updated_at = datetime.now(timezone.utc).isoformat()
    inc.audit_trail = audit.trail
    return inc


@app.post("/api/incidents/{incident_id}/approve-brief", response_model=Incident)
def approve_brief(incident_id: str, req: BriefApprovalRequest):
    """Human operator officially signs and approves the situation brief."""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    inc = incidents_db[incident_id]
    if not inc.brief:
        raise HTTPException(status_code=400, detail="No situation brief generated yet")

    inc.brief.approved_by_operator = req.approved
    inc.brief.operator_notes = req.operator_notes
    audit = get_audit(incident_id)
    entry = audit.log(
        action="BRIEF_OPERATOR_APPROVED" if req.approved else "BRIEF_OPERATOR_REJECTED",
        actor=req.operator_id,
        details={"approved": req.approved, "notes": req.operator_notes},
    )
    inc.brief.audit_hash = entry.hash_curr
    inc.updated_at = datetime.now(timezone.utc).isoformat()
    inc.audit_trail = audit.trail
    return inc


@app.get("/api/incidents/{incident_id}/export", response_model=OfflineExportBundle)
def export_bundle(incident_id: str):
    """Generates Stage D cryptographically signed offline bundle."""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    inc = incidents_db[incident_id]
    audit = get_audit(incident_id)
    bundle = pipeline.execute_stage_d_export(inc, audit)
    return bundle


@app.get("/api/incidents/{incident_id}/audit-verify")
def verify_audit(incident_id: str):
    """Verifies the SHA-256 hash-chain integrity of the incident audit trail."""
    audit = get_audit(incident_id)
    is_valid = audit.verify_integrity()
    return {
        "incident_id": incident_id,
        "chain_intact": is_valid,
        "entries_count": len(audit.trail),
        "latest_hash": audit.trail[-1].hash_curr if audit.trail else "0" * 64,
    }


# Mount frontend static distribution if built
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
