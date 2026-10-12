"""
Unit tests for RelayZero Reconciliation Engine.
"""

from track_2b.src.backend.reconciliation import ReconciliationEngine
from track_2b.src.backend.schemas import (
    ExtractedClaim,
    LanguageEnum,
    ClusterStatusEnum,
    EvidenceSpan,
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
            evidence_span=EvidenceSpan(exact_quote="Nordportal Göschenen", start_char=0, end_char=20),
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
            evidence_span=EvidenceSpan(exact_quote="portail sud Airolo", start_char=0, end_char=18),
            language=LanguageEnum.FR,
            confidence=0.95,
            timestamp="2026-10-12T14:14:00Z",
        ),
    ]

    clusters, missing = engine.reconcile(claims)
    loc_cluster = next(c for c in clusters if c.field == "location_primary")
    assert loc_cluster.status == ClusterStatusEnum.CONFLICTING
    assert loc_cluster.reconciled_value is None
    assert "contradiction" in loc_cluster.conflict_explanation.lower()


def test_reconciliation_single_source_unverified():
    engine = ReconciliationEngine()
    claims = [
        ExtractedClaim(
            claim_id="CLM-01",
            incident_id="INC-01",
            source_id="SRC-01",
            field="hazard_status",
            normalized_value="dense smoke",
            original_value="dense smoke",
            evidence_span=EvidenceSpan(exact_quote="dense smoke", start_char=0, end_char=11),
            language=LanguageEnum.EN,
            timestamp="2026-10-12T14:00:00Z",
        )
    ]
    clusters, missing = engine.reconcile(claims)
    haz_cluster = next(c for c in clusters if c.field == "hazard_status")
    assert haz_cluster.status == ClusterStatusEnum.SINGLE_SOURCE_UNVERIFIED
    assert "single source" in haz_cluster.conflict_explanation.lower()


def test_reconciliation_cluster_resolution_persistence():
    engine = ReconciliationEngine()
    claims = [
        ExtractedClaim(
            claim_id="CLM-01",
            incident_id="INC-01",
            source_id="SRC-01",
            field="location_primary",
            normalized_value="North Portal",
            original_value="North",
            evidence_span=EvidenceSpan(exact_quote="North", start_char=0, end_char=5),
            language=LanguageEnum.EN,
            timestamp="2026-10-12T14:00:00Z",
        ),
        ExtractedClaim(
            claim_id="CLM-02",
            incident_id="INC-01",
            source_id="SRC-02",
            field="location_primary",
            normalized_value="South Portal",
            original_value="South",
            evidence_span=EvidenceSpan(exact_quote="South", start_char=0, end_char=5),
            language=LanguageEnum.EN,
            timestamp="2026-10-12T14:00:00Z",
        ),
    ]

    # Without persistent resolution -> CONFLICTING
    clusters, _ = engine.reconcile(claims)
    assert next(c for c in clusters if c.field == "location_primary").status == ClusterStatusEnum.CONFLICTING

    # With operator persistent resolution
    resolutions = {"CLUS-LOCATION_PRIMARY": "North Portal (Resolved by Commander)"}
    clusters_res, _ = engine.reconcile(claims, existing_cluster_resolutions=resolutions)
    loc_c = next(c for c in clusters_res if c.field == "location_primary")
    assert loc_c.status == ClusterStatusEnum.OPERATOR_CONFIRMED
    assert loc_c.reconciled_value == "North Portal (Resolved by Commander)"
