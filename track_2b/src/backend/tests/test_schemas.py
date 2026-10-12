"""
Unit tests for RelayZero Pydantic schemas.
"""

import pytest
from pydantic import ValidationError
from track_2b.src.backend.schemas import (
    SourceReport,
    ExtractedClaim,
    ClaimCluster,
    ModalityEnum,
    LanguageEnum,
    ExtractionStatusEnum,
    OperatorStatusEnum,
    ClusterStatusEnum,
)


def test_source_report_schema_valid():
    report = SourceReport(
        report_id="SRC-DE-01",
        incident_id="INC-01",
        modality=ModalityEnum.TEXT,
        language=LanguageEnum.DE,
        author_role="Uri Police Dispatch",
        received_at="2026-10-12T14:05:00Z",
        source_channel="TETRA",
        reliability_tier="Emergency Services",
        raw_content="Rauchentwicklung im Gotthard Nordportal",
    )
    assert report.report_id == "SRC-DE-01"
    assert report.modality == ModalityEnum.TEXT
    assert report.language == LanguageEnum.DE


def test_source_report_schema_invalid():
    with pytest.raises(ValidationError):
        # Missing required fields
        SourceReport(
            report_id="SRC-01",
            incident_id="INC-01",
        )


def test_extracted_claim_schema():
    claim = ExtractedClaim(
        claim_id="CLM-001",
        incident_id="INC-01",
        source_id="SRC-DE-01",
        field="location_primary",
        normalized_value="Gotthard Tunnel North Portal",
        original_value="Nordportal Göschenen",
        evidence_pointer="ca. 500m nach dem Nordportal Göschenen",
        language=LanguageEnum.DE,
        confidence=0.98,
        timestamp="2026-10-12T14:06:00Z",
    )
    assert claim.confidence == 0.98
    assert claim.operator_status == OperatorStatusEnum.UNREVIEWED


def test_claim_cluster_schema():
    cluster = ClaimCluster(
        cluster_id="CLUS-LOC",
        field="location_primary",
        status=ClusterStatusEnum.CONFLICT,
        claims=[],
        conflict_explanation="Conflicting locations",
        is_critical_field=True,
    )
    assert cluster.status == ClusterStatusEnum.CONFLICT
    assert cluster.is_critical_field is True
