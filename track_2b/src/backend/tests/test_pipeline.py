"""
Unit tests for RelayZero End-to-End Pipeline Stages A through D.
"""

import pytest
from track_2b.src.backend.pipeline import IncidentPipeline
from track_2b.src.backend.presets import get_synthetic_presets
from track_2b.src.backend.audit import AuditLogger
from track_2b.src.backend.verify_bundle import verify_bundle_file
import json
import tempfile


@pytest.mark.asyncio
async def test_full_pipeline_execution():
    pipeline = IncidentPipeline()
    presets = get_synthetic_presets()
    incident = presets[0]  # Alpine tunnel
    audit = AuditLogger()

    # Stage A
    claims = await pipeline.execute_stage_a_extraction(incident, audit)
    assert len(claims) >= 5
    assert all(c.evidence_span is not None for c in claims)
    # Check that evidence span strictly matches source slice
    for c in claims:
        src = next(s for s in incident.sources if s.report_id == c.source_id)
        assert src.raw_content[c.evidence_span.start_char : c.evidence_span.end_char] == c.evidence_span.exact_quote

    # Stage B
    clusters = pipeline.execute_stage_b_reconciliation(incident, claims, audit)
    conflict_clusters = [c for c in clusters if c.status.value == "conflicting"]
    assert len(conflict_clusters) >= 1  # North vs South entrance conflict detected

    # Stage C
    brief = pipeline.execute_stage_c_brief(incident, clusters, audit)
    assert brief.incident_id == incident.incident_id
    assert len(brief.unresolved_conflicts) >= 1

    # Stage D
    bundle = pipeline.execute_stage_d_export(incident, audit)
    assert len(bundle.sha256_checksum) == 64
    assert audit.verify_integrity() is True

    # Test independent verification CLI
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write(json.dumps(bundle.model_dump(mode="json")))
        f.flush()
        res = verify_bundle_file(f.name)
        assert res["valid"] is True
