"""
RelayZero FastAPI Application.
Air-gapped, multilingual, multi-source incident-brief compiler.
Hardened endpoints with strict CORS, lifespan management, and safety gates.
"""

import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .schemas import (
    Incident,
    SourceReport,
    OperatorActionRequest,
    OperatorActionTypeEnum,
    OperatorClaimStatusEnum,
    ClusterStatusEnum,
    BriefApprovalRequest,
    ChecksummedExportBundle,
    EgressStatusEnum,
)
from .pipeline import IncidentPipeline
from .presets import get_synthetic_presets
from .audit import AuditLogger
from .apertus_adapter import ApertusAdapter, LiveEndpointError

# In-memory incident and audit stores
incidents_db: Dict[str, Incident] = {}
audit_loggers: Dict[str, AuditLogger] = {}
adapter = ApertusAdapter()
pipeline = IncidentPipeline(adapter=adapter)


def get_audit(incident_id: str) -> AuditLogger:
    if incident_id not in audit_loggers:
        audit_loggers[incident_id] = AuditLogger()
    return audit_loggers[incident_id]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize presets on startup
    for inc in get_synthetic_presets(app_mode=adapter.app_mode):
        incidents_db[inc.incident_id] = inc
        audit = get_audit(inc.incident_id)
        audit.log(
            action="INCIDENT_INITIALIZED",
            actor="System-Init",
            details={"incident_id": inc.incident_id, "title": inc.title, "preset": inc.preset_id, "app_mode": adapter.app_mode.value},
        )
    yield
    # Clean shutdown tasks if any
    pass


app = FastAPI(
    title="RelayZero API",
    description="Air-Gapped Multilingual Multi-Source Incident-Brief Compiler",
    version="1.0.0",
    lifespan=lifespan,
)

# Hardened CORS: Explicit local origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/health")
def get_health():
    """System health check and sovereignty status strip endpoint."""
    return {
        "status": "healthy",
        "system": "RelayZero",
        "version": "1.0.0",
        "app_mode": adapter.app_mode.value,
        "model_identifier": adapter.get_effective_model_identifier(),
        "live_endpoint_configured": adapter.is_live_endpoint_available(),
        "egress_verification": EgressStatusEnum.UNVERIFIED.value,
        "active_incidents": len(incidents_db),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/presets")
def list_presets():
    """Returns available synthetic demonstration incident presets."""
    presets = get_synthetic_presets(app_mode=adapter.app_mode)
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
    matching = [p for p in get_synthetic_presets(app_mode=adapter.app_mode) if p.preset_id == preset_id]
    if not matching:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")
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
    """Retrieves full incident details."""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    inc = incidents_db[incident_id]
    inc.audit_trail = get_audit(incident_id).trail
    return inc


@app.post("/api/incidents/{incident_id}/reports", response_model=Incident)
def add_report(incident_id: str, report: SourceReport):
    """Ingests a new report into the incident."""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    if report.incident_id != incident_id:
        raise HTTPException(status_code=400, detail="Report incident_id does not match target incident")

    inc = incidents_db[incident_id]
    # Check for duplicate report IDs
    if any(s.report_id == report.report_id for s in inc.sources):
        raise HTTPException(status_code=409, detail=f"Report with ID '{report.report_id}' already exists")

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
      A: Extract claims from sources
      B: Reconcile evidence and detect contradictions
      C: Generate draft situation brief
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    inc = incidents_db[incident_id]
    audit = get_audit(incident_id)

    try:
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
    except LiveEndpointError as exc:
        raise HTTPException(status_code=502, detail=f"Apertus live endpoint error: {str(exc)}")


@app.post("/api/process", response_model=Incident)
async def process_preset_workflow(payload: Dict[str, Any] = Body(default={})):
    """Convenience endpoint to trigger pipeline for a preset or default incident."""
    preset_id = payload.get("preset_id", "preset_alpine_tunnel")
    target_id = "INC-2026-CH-01"
    for inc in incidents_db.values():
        if inc.preset_id in (preset_id, "alpine_tunnel_smoke"):
            target_id = inc.incident_id
            break
    return await process_incident_pipeline(target_id)


@app.post("/api/incidents/{incident_id}/operator-action", response_model=Incident)
def apply_operator_action(incident_id: str, req: OperatorActionRequest):
    """
    Applies operator action (confirm, edit, reject, or resolve cluster).
    Cluster resolutions are persisted across future reconciliation re-runs.
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    inc = incidents_db[incident_id]
    audit = get_audit(incident_id)

    # Claim-level action
    if req.action == OperatorActionTypeEnum.CONFIRM_CLAIM:
        matching = [c for c in inc.claims if c.claim_id == req.claim_id]
        if not matching:
            raise HTTPException(status_code=404, detail=f"Claim '{req.claim_id}' not found")
        matching[0].operator_status = OperatorClaimStatusEnum.OPERATOR_CONFIRMED
        audit.log(
            action="CLAIM_OPERATOR_CONFIRMED",
            actor=req.operator_id,
            details={"claim_id": req.claim_id, "field": matching[0].field},
        )

    elif req.action == OperatorActionTypeEnum.REJECT_CLAIM:
        matching = [c for c in inc.claims if c.claim_id == req.claim_id]
        if not matching:
            raise HTTPException(status_code=404, detail=f"Claim '{req.claim_id}' not found")
        matching[0].operator_status = OperatorClaimStatusEnum.REJECTED
        audit.log(
            action="CLAIM_OPERATOR_REJECTED",
            actor=req.operator_id,
            details={"claim_id": req.claim_id, "field": matching[0].field},
        )

    elif req.action == OperatorActionTypeEnum.EDIT_CLAIM:
        matching = [c for c in inc.claims if c.claim_id == req.claim_id]
        if not matching:
            raise HTTPException(status_code=404, detail=f"Claim '{req.claim_id}' not found")
        if not req.new_value:
            raise HTTPException(status_code=400, detail="new_value must be provided for edit action")
        matching[0].operator_status = OperatorClaimStatusEnum.EDITED
        matching[0].operator_edited_value = req.new_value
        audit.log(
            action="CLAIM_OPERATOR_EDITED",
            actor=req.operator_id,
            details={"claim_id": req.claim_id, "field": matching[0].field, "new_value": req.new_value},
        )

    elif req.action == OperatorActionTypeEnum.RESOLVE_CLUSTER:
        if not req.cluster_id or not req.new_value:
            raise HTTPException(status_code=400, detail="cluster_id and new_value required for resolve_cluster")
        pipeline.set_cluster_resolution(incident_id, req.cluster_id, req.new_value)
        audit.log(
            action="CLUSTER_OPERATOR_RESOLVED",
            actor=req.operator_id,
            details={"cluster_id": req.cluster_id, "resolved_value": req.new_value, "notes": req.notes},
        )

    # Re-run reconciliation and brief refresh
    inc.clusters = pipeline.execute_stage_b_reconciliation(inc, inc.claims, audit)
    inc.brief = pipeline.execute_stage_c_brief(inc, inc.clusters, audit)
    inc.updated_at = datetime.now(timezone.utc).isoformat()
    inc.audit_trail = audit.trail
    return inc


@app.post("/api/incidents/{incident_id}/approve-brief", response_model=Incident)
def approve_brief(incident_id: str, req: BriefApprovalRequest):
    """
    Approves and signs the situation brief.
    SAFETY GATE: Rejects approval if unresolved critical conflicts or missing fields remain,
    unless explicit emergency_override is provided with mandatory override_reason!
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    inc = incidents_db[incident_id]
    if not inc.brief:
        raise HTTPException(status_code=400, detail="No situation brief generated yet")

    # Safety check: are there critical conflicts or missing fields?
    unresolved_conflicts = [c for c in inc.clusters if c.status == ClusterStatusEnum.CONFLICTING and c.is_critical_field]
    missing_critical = [c for c in inc.clusters if c.status == ClusterStatusEnum.MISSING and c.is_critical_field]

    if req.approved and (unresolved_conflicts or missing_critical):
        if not req.emergency_override:
            raise HTTPException(
                status_code=400,
                detail="Approval blocked: Critical factual contradictions or missing fields remain. "
                       "Emergency override required with justification.",
            )
        if not req.override_reason or len(req.override_reason.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="Emergency override requires a substantive override_reason.",
            )

    inc.brief.approved_by_operator = req.approved
    inc.brief.operator_notes = req.operator_notes
    inc.brief.emergency_override = req.emergency_override
    inc.brief.override_reason = req.override_reason

    audit = get_audit(incident_id)
    entry = audit.log(
        action="BRIEF_EMERGENCY_OVERRIDE_APPROVED" if req.emergency_override else ("BRIEF_OPERATOR_APPROVED" if req.approved else "BRIEF_OPERATOR_REJECTED"),
        actor=req.operator_id,
        details={
            "approved": req.approved,
            "emergency_override": req.emergency_override,
            "override_reason": req.override_reason,
            "notes": req.operator_notes,
        },
    )
    inc.brief.audit_hash = entry.hash_curr
    inc.updated_at = datetime.now(timezone.utc).isoformat()
    inc.audit_trail = audit.trail
    return inc


@app.get("/api/incidents/{incident_id}/export", response_model=ChecksummedExportBundle)
def export_bundle(incident_id: str):
    """Generates Stage D checksummed tamper-evident bundle."""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    inc = incidents_db[incident_id]
    audit = get_audit(incident_id)
    bundle = pipeline.execute_stage_d_export(inc, audit, egress_status=EgressStatusEnum.UNVERIFIED)
    return bundle


@app.get("/api/incidents/{incident_id}/audit-verify")
def verify_audit(incident_id: str):
    """Verifies the SHA-256 hash-chain integrity of the incident audit trail."""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
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
