"""
Integration tests for RelayZero FastAPI REST endpoints.
"""

import pytest
from starlette.testclient import TestClient
from track_2b.src.backend.main import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["deployment_mode"] == "AIR-GAPPED"
    assert "Apertus" in data["apertus_model"]
    assert data["egress_zero_verified"] is True


def test_api_presets():
    res = client.get("/api/presets")
    assert res.status_code == 200
    presets = res.json()
    assert len(presets) >= 3
    assert any(p["preset_id"] == "alpine_tunnel_smoke" for p in presets)


def test_api_process_and_operator_action():
    # Load preset
    client.post("/api/presets/alpine_tunnel_smoke/load")

    # Process pipeline
    proc_res = client.post("/api/incidents/INC-2026-CH-01/process")
    assert proc_res.status_code == 200
    incident = proc_res.json()
    assert len(incident["claims"]) >= 5
    assert incident["brief"] is not None

    # Find a conflicting cluster and resolve it
    conflict_cluster = next((c for c in incident["clusters"] if c["status"] == "conflict"), None)
    if conflict_cluster:
        action_res = client.post(
            "/api/incidents/INC-2026-CH-01/operator-action",
            json={
                "cluster_id": conflict_cluster["cluster_id"],
                "action": "resolve_cluster",
                "new_value": "Gotthard North Portal (Göschenen)",
                "notes": "Confirmed by drone camera telemetry",
                "operator_id": "OP-COMMANDER-01",
            },
        )
        assert action_res.status_code == 200

    # Operator approves situation brief
    approve_res = client.post(
        "/api/incidents/INC-2026-CH-01/approve-brief",
        json={
            "approved": True,
            "operator_notes": "Authorizing emergency ventilation protocol",
            "operator_id": "OP-COMMANDER-01",
        },
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["brief"]["approved_by_operator"] is True

    # Export bundle
    export_res = client.get("/api/incidents/INC-2026-CH-01/export")
    assert export_res.status_code == 200
    bundle = export_res.json()
    assert bundle["air_gapped_verified"] is True
    assert len(bundle["sha256_checksum"]) == 64

    # Verify audit chain
    audit_res = client.get("/api/incidents/INC-2026-CH-01/audit-verify")
    assert audit_res.status_code == 200
    assert audit_res.json()["chain_intact"] is True
