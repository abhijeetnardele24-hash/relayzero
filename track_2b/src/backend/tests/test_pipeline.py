"""
Unit tests for RelayZero End-to-End Pipeline Stages A through D.
"""

import pytest
from track_2b.src.backend.pipeline import IncidentPipeline
from track_2b.src.backend.presets import get_synthetic_presets
from track_2b.src.backend.audit import AuditLogger


@pytest.mark.asyncio
async def test_full_pipeline_execution():
    pipeline = IncidentPipeline()
    presets = get_synthetic_presets()
    incident = presets[0]  # Alpine tunnel
    audit = AuditLogger()

    # Stage A
    claims = await pipeline.execute_stage_a_extraction(incident, audit)
    assert len(claims) >= 5
    assert any(c.field == "location_primary" for c in claims)

    # Stage B
    clusters = pipeline.execute_stage_b_reconciliation(incident, claims, audit)
    assert len(clusters) > 0
    conflict_clusters = [c for c in clusters if c.status.value == "conflict"]
    assert len(conflict_clusters) >= 1  # North vs South entrance conflict detected!

    # Stage C
    brief = pipeline.execute_stage_c_brief(incident, clusters, audit)
    assert brief.incident_id == incident.incident_id
    assert len(brief.unresolved_conflicts) >= 1
    assert "TUNNEL" in brief.executive_summary or "FIRE" in brief.executive_summary

    # Stage D
    bundle = pipeline.execute_stage_d_export(incident, audit)
    assert bundle.air_gapped_verified is True
    assert bundle.egress_zero_verified is True
    assert len(bundle.sha256_checksum) == 64
    assert audit.verify_integrity() is True
