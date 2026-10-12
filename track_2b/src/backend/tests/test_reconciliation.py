"""
Unit tests for RelayZero Reconciliation Engine.
"""

from track_2b.src.backend.reconciliation import ReconciliationEngine
from track_2b.src.backend.schemas import (
    ExtractedClaim,
    LanguageEnum,
    OperatorStatusEnum,
    ClusterStatusEnum,
)


def test_reconciliation_conflict_detection():
    engine = ReconciliationEngine()

    claims = [
        ExtractedClaim(
            claim_id="CLM-01",
            incident_id="INC-01",
            source_id="SRC-DE-01",
            field="location_primary",
            normalized_value="Gotthard Road Tunnel - North Portal (Göschenen)",
            original_value="Nordportal Göschenen",
            evidence_pointer="Nordportal",
            language=LanguageEnum.DE,
            confidence=0.98,
            timestamp="2026-10-12T14:06:00Z",
        ),
        ExtractedClaim(
            claim_id="CLM-02",
            incident_id="INC-01",
            source_id="SRC-FR-02",
            field="location_primary",
            normalized_value="Gotthard Road Tunnel - South Portal (Airolo)",
            original_value="portail sud Airolo",
            evidence_pointer="portail sud",
            language=LanguageEnum.FR,
            confidence=0.95,
            timestamp="2026-10-12T14:14:00Z",
        ),
    ]

    clusters, missing = engine.reconcile(claims)
    loc_cluster = next(c for c in clusters if c.field == "location_primary")
    assert loc_cluster.status == ClusterStatusEnum.CONFLICT
    assert loc_cluster.reconciled_value is None
    assert "contradiction" in loc_cluster.conflict_explanation.lower()


def test_reconciliation_missing_critical_fields():
    engine = ReconciliationEngine()
    claims = [
        ExtractedClaim(
            claim_id="CLM-01",
            incident_id="INC-01",
            source_id="SRC-01",
            field="incident_type",
            normalized_value="fire",
            original_value="fire",
            evidence_pointer="fire",
            language=LanguageEnum.EN,
            confidence=0.95,
            timestamp="2026-10-12T14:00:00Z",
        )
    ]

    clusters, missing = engine.reconcile(claims)
    assert "location_primary" in missing
    assert "hazard_status" in missing
    missing_clusters = [c for c in clusters if c.status == ClusterStatusEnum.MISSING]
    assert len(missing_clusters) >= 2


def test_reconciliation_operator_confirmation_override():
    engine = ReconciliationEngine()
    claim1 = ExtractedClaim(
        claim_id="CLM-01",
        incident_id="INC-01",
        source_id="SRC-DE-01",
        field="location_primary",
        normalized_value="Gotthard North Portal",
        original_value="Nordportal",
        evidence_pointer="Nordportal",
        language=LanguageEnum.DE,
        confidence=0.98,
        operator_status=OperatorStatusEnum.CONFIRMED,
        timestamp="2026-10-12T14:06:00Z",
    )
    claim2 = ExtractedClaim(
        claim_id="CLM-02",
        incident_id="INC-01",
        source_id="SRC-FR-02",
        field="location_primary",
        normalized_value="Gotthard South Portal",
        original_value="Sud",
        evidence_pointer="Sud",
        language=LanguageEnum.FR,
        confidence=0.95,
        timestamp="2026-10-12T14:14:00Z",
    )

    clusters, missing = engine.reconcile([claim1, claim2])
    loc_cluster = next(c for c in clusters if c.field == "location_primary")
    assert loc_cluster.status == ClusterStatusEnum.CORROBORATED
    assert loc_cluster.reconciled_value == "Gotthard North Portal"
