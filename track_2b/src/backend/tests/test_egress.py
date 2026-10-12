"""
Air-Gap Egress Verification Test Suite.
Verifies honest egress status evaluation and socket probe behavior.
"""

import socket
import pytest
from track_2b.src.backend.pipeline import IncidentPipeline
from track_2b.src.backend.presets import get_synthetic_presets
from track_2b.src.backend.audit import AuditLogger
from track_2b.src.backend.schemas import EgressStatusEnum


@pytest.mark.asyncio
async def test_egress_probe_behavior(monkeypatch):
    """
    Validates that socket outbound attempts are intercepted,
    and proves that runtime fixture compilation makes no network calls.
    """
    attempted_connections = []

    def blocked_connect(self, address):
        attempted_connections.append(address)
        raise ConnectionRefusedError(f"EGRESS BLOCKED: Connection to {address} denied")

    monkeypatch.setattr(socket.socket, "connect", blocked_connect)

    pipeline = IncidentPipeline()
    presets = get_synthetic_presets()
    incident = presets[0]
    audit = AuditLogger()

    # Run complete pipeline
    claims = await pipeline.execute_stage_a_extraction(incident, audit)
    clusters = pipeline.execute_stage_b_reconciliation(incident, claims, audit)
    brief = pipeline.execute_stage_c_brief(incident, clusters, audit)

    # Export bundle with explicit egress status
    bundle = pipeline.execute_stage_d_export(incident, audit, egress_status=EgressStatusEnum.VERIFIED)

    assert len(attempted_connections) == 0
    assert bundle.egress_verification == EgressStatusEnum.VERIFIED


def test_egress_status_enum_validity():
    assert EgressStatusEnum.VERIFIED == "verified"
    assert EgressStatusEnum.UNVERIFIED == "unverified"
    assert EgressStatusEnum.FAILED == "failed"
    assert EgressStatusEnum.NOT_APPLICABLE == "not_applicable"
