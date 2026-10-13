"""
Integration tests for RelayZero FastAPI REST endpoints and safety gates.
"""

from starlette.testclient import TestClient
from track_2b.src.backend.main import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["app_mode"] in ("fixture", "live")
    assert data["egress_verification"] == "unverified"


def test_api_duplicate_report_rejected():
    client.post("/api/presets/alpine_tunnel_smoke/load")
    # Attempting to add report with existing ID SRC-DE-01
    dup_report = {
        "report_id": "SRC-DE-01",
        "incident_id": "INC-2026-CH-01",
        "modality": "text",
        "language": "de",
        "author_role": "Dispatcher",
        "received_at": "2026-10-12T14:10:00Z",
        "source_channel": "Radio",
        "reliability_tier": "Unit",
        "raw_content": "Duplicate content",
    }
    res = client.post("/api/incidents/INC-2026-CH-01/reports", json=dup_report)
    assert res.status_code == 409


def test_api_process_and_safety_approval_gate():
    # Load preset
    client.post("/api/presets/alpine_tunnel_smoke/load")

    # Process pipeline
    proc_res = client.post("/api/incidents/INC-2026-CH-01/process")
    assert proc_res.status_code == 200
    incident = proc_res.json()
    assert len(incident["claims"]) >= 5

    # 1. SAFETY GATE: Approval must fail because unresolved conflicts/missing fields remain
    blocked_approval = client.post(
        "/api/incidents/INC-2026-CH-01/approve-brief",
        json={
            "approved": True,
            "operator_notes": "Attempting sign-off without resolving conflicts",
            "operator_id": "OP-COMMANDER",
            "emergency_override": False,
        },
    )
    assert blocked_approval.status_code == 400
    assert "Approval blocked" in blocked_approval.json()["detail"]

    # 2. EMERGENCY OVERRIDE: Must fail if reason is missing or trivial
    invalid_override = client.post(
        "/api/incidents/INC-2026-CH-01/approve-brief",
        json={
            "approved": True,
            "operator_id": "OP-COMMANDER",
            "emergency_override": True,
            "override_reason": "abc",  # Too short
        },
    )
    assert invalid_override.status_code == 400

    # 3. Valid emergency override approval
    valid_override = client.post(
        "/api/incidents/INC-2026-CH-01/approve-brief",
        json={
            "approved": True,
            "operator_id": "OP-COMMANDER",
            "emergency_override": True,
            "override_reason": "Immediate life-safety ventilation order required prior to second report corroboration.",
        },
    )
    assert valid_override.status_code == 200
    assert valid_override.json()["brief"]["approved_by_operator"] is True
    assert valid_override.json()["brief"]["emergency_override"] is True


def test_api_cluster_resolution_persistence():
    client.post("/api/presets/alpine_tunnel_smoke/load")
    client.post("/api/incidents/INC-2026-CH-01/process")

    # Operator resolves conflict
    action_res = client.post(
        "/api/incidents/INC-2026-CH-01/operator-action",
        json={
            "action": "resolve_cluster",
            "cluster_id": "CLUS-LOCATION_PRIMARY",
            "new_value": "Gotthard North Portal (Confirmed by Command)",
            "notes": "Verified by optical sensors",
            "operator_id": "OP-COMMANDER",
        },
    )
    assert action_res.status_code == 200
    inc_after_res = action_res.json()
    loc_c = next(c for c in inc_after_res["clusters"] if c["field"] == "location_primary")
    assert loc_c["status"] == "operator_confirmed"
    assert loc_c["reconciled_value"] == "Gotthard North Portal (Confirmed by Command)"

    # Reprocess incident -> Resolution persists!
    reproc_res = client.post("/api/incidents/INC-2026-CH-01/process")
    loc_c2 = next(c for c in reproc_res.json()["clusters"] if c["field"] == "location_primary")
    assert loc_c2["status"] == "operator_confirmed"
    assert loc_c2["reconciled_value"] == "Gotthard North Portal (Confirmed by Command)"


def test_api_additional_endpoints_coverage():
    # 1. Presets list
    presets_res = client.get("/api/presets")
    assert presets_res.status_code == 200
    presets = presets_res.json()
    assert len(presets) >= 1

    # 2. Preset load 404
    bad_preset = client.post("/api/presets/non_existent_preset/load")
    assert bad_preset.status_code == 404

    # 3. Incidents list & get
    inc_list = client.get("/api/incidents")
    assert inc_list.status_code == 200
    assert len(inc_list.json()) >= 1

    inc_get = client.get("/api/incidents/INC-2026-CH-01")
    assert inc_get.status_code == 200
    assert inc_get.json()["incident_id"] == "INC-2026-CH-01"

    inc_404 = client.get("/api/incidents/INC-DOES-NOT-EXIST")
    assert inc_404.status_code == 404

    # 4. Process convenience endpoint
    proc_convenience = client.post("/api/process", json={"preset_id": "alpine_tunnel_smoke"})
    assert proc_convenience.status_code == 200

    # 5. Operator claim actions (confirm, reject, edit)
    client.post("/api/presets/alpine_tunnel_smoke/load")
    client.post("/api/incidents/INC-2026-CH-01/process")
    first_claim = client.get("/api/incidents/INC-2026-CH-01").json()["claims"][0]
    cid = first_claim["claim_id"]

    confirm_res = client.post(
        "/api/incidents/INC-2026-CH-01/operator-action",
        json={"action": "confirm_claim", "claim_id": cid, "operator_id": "OP-1"},
    )
    assert confirm_res.status_code == 200

    reject_res = client.post(
        "/api/incidents/INC-2026-CH-01/operator-action",
        json={"action": "reject_claim", "claim_id": cid, "operator_id": "OP-1"},
    )
    assert reject_res.status_code == 200

    edit_res = client.post(
        "/api/incidents/INC-2026-CH-01/operator-action",
        json={"action": "edit_claim", "claim_id": cid, "new_value": "Edited Value", "operator_id": "OP-1"},
    )
    assert edit_res.status_code == 200

    # 6. Export bundle & Audit verification
    export_res = client.get("/api/incidents/INC-2026-CH-01/export")
    assert export_res.status_code == 200
    assert "sha256_checksum" in export_res.json()

    audit_verify_res = client.get("/api/incidents/INC-2026-CH-01/audit-verify")
    assert audit_verify_res.status_code == 200
    assert audit_verify_res.json()["chain_intact"] is True

