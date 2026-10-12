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
    OperatorClaimStatusEnum,
    ClusterStatusEnum,
    EvidenceSpan,
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
        SourceReport(
            report_id="SRC-01",
            incident_id="INC-01",
        )


def test_evidence_span_validation():
    span = EvidenceSpan(
        exact_quote="Gotthard",
        start_char=5,
        end_char=13,
    )
    assert span.exact_quote == "Gotthard"
    assert span.start_char == 5

    # Invalid span: end <= start
    with pytest.raises(ValidationError):
        EvidenceSpan(exact_quote="A", start_char=5, end_char=5)

    # Invalid span: length mismatch
    with pytest.raises(ValidationError):
        EvidenceSpan(exact_quote="Too long", start_char=0, end_char=2)


def test_extracted_claim_schema():
    span = EvidenceSpan(exact_quote="Nordportal", start_char=0, end_char=10)
    claim = ExtractedClaim(
        claim_id="CLM-001",
        incident_id="INC-01",
        source_id="SRC-DE-01",
        field="location_primary",
        normalized_value="Gotthard Tunnel North Portal",
        original_value="Nordportal",
        evidence_span=span,
        language=LanguageEnum.DE,
        confidence=None,  # Confidence honestly None if omitted
        timestamp="2026-10-12T14:06:00Z",
    )
    assert claim.evidence_span.exact_quote == "Nordportal"
    assert claim.operator_status == OperatorClaimStatusEnum.UNREVIEWED


def test_claim_cluster_schema():
    cluster = ClaimCluster(
        cluster_id="CLUS-LOC",
        field="location_primary",
        status=ClusterStatusEnum.CONFLICTING,
        claims=[],
        conflict_explanation="Conflicting locations",
        is_critical_field=True,
    )
    assert cluster.status == ClusterStatusEnum.CONFLICTING
    assert cluster.is_critical_field is True
