"""
Air-Gap Egress Zero Verification Test.
Ensures that the RelayZero inference and compilation pipeline operates
with ZERO outbound network calls during runtime execution.
"""

import socket
import pytest
from track_2b.src.backend.pipeline import IncidentPipeline
from track_2b.src.backend.presets import get_synthetic_presets
from track_2b.src.backend.audit import AuditLogger


@pytest.mark.asyncio
async def test_egress_zero_verification(monkeypatch):
    """
    Hooks socket.create_connection and socket.socket.connect
    to detect any attempt to initiate outbound network egress.
    """
    attempted_connections = []

    orig_connect = socket.socket.connect

    def blocked_connect(self, address):
        attempted_connections.append(address)
        raise ConnectionRefusedError(f"EGRESS VIOLATION: Attempted outbound call to {address}")

    monkeypatch.setattr(socket.socket, "connect", blocked_connect)

    pipeline = IncidentPipeline()
    presets = get_synthetic_presets()
    incident = presets[0]
    audit = AuditLogger()

    # Run complete multi-stage pipeline
    claims = await pipeline.execute_stage_a_extraction(incident, audit)
    clusters = pipeline.execute_stage_b_reconciliation(incident, claims, audit)
    brief = pipeline.execute_stage_c_brief(incident, clusters, audit)
    bundle = pipeline.execute_stage_d_export(incident, audit)

    # Assert zero external network connections were attempted
    assert len(attempted_connections) == 0, f"Outbound calls detected: {attempted_connections}"
    assert bundle.egress_zero_verified is True
    assert bundle.air_gapped_verified is True
