"""
Unit tests for RelayZero Evaluator, strict gold-label decoupling, and metric calculation functions.
"""

import os
import json
import tempfile
import pytest
from track_2b.src.backend.evaluation_runner import (
    calculate_metrics_from_predictions,
    execute_full_benchmark_run,
    setup_evaluation_dataset_files,
    load_raw_benchmark_definitions,
    run_regex_baseline,
    run_single_pass_baseline,
    run_relayzero_pipeline_eval,
    INPUTS_FILE,
    GOLD_FILE,
)
from track_2b.src.backend.apertus_adapter import find_and_validate_span
from track_2b.src.backend.verify_bundle import verify_bundle_file


def test_find_and_validate_span_exact():
    source = "EILMELDUNG: Starke Rauchentwicklung im Gotthard-Strassentunnel"
    quote = "Starke Rauchentwicklung"
    span = find_and_validate_span(source, quote)

    assert span is not None
    assert span.exact_quote == quote
    assert source[span.start_char : span.end_char] == quote


def test_find_and_validate_span_case_insensitive():
    source = "dégagement de fumée important"
    quote = "DÉGAGEMENT DE FUMÉE"
    span = find_and_validate_span(source, quote)
    assert span is not None
    assert source[span.start_char : span.end_char] == "dégagement de fumée"


def test_find_and_validate_span_missing_and_empty():
    assert find_and_validate_span("", "quote") is None
    assert find_and_validate_span("text", "") is None
    assert find_and_validate_span("hello world", "nonexistent") is None


def test_metrics_calculation_perfect_match():
    toy_dataset = [
        {
            "incident_id": "TEST-01",
            "sources": [{"source_id": "S1", "raw_content": "Fire in tunnel at km 5"}],
            "gold_claims": [{"field": "incident_type", "normalized_value": "fire", "quote": "Fire"}],
            "gold_contradictions": [],
            "gold_missing_critical": ["affected_count"],
            "prompt_injection_present": False,
        }
    ]
    toy_predictions = [
        {
            "incident_id": "TEST-01",
            "predicted_claims": [
                {"field": "incident_type", "normalized_value": "fire", "exact_quote": "Fire", "source_id": "S1"}
            ],
            "predicted_contradictions": [],
        }
    ]

    metrics = calculate_metrics_from_predictions(toy_predictions, toy_dataset, "TestSystem", 1.0)
    assert metrics["field_f1_micro"] == 1.0
    assert metrics["evidence_attribution_precision_pct"] == 100.0
    assert metrics["missing_field_abstention_acc_pct"] == 100.0
    assert metrics["prompt_injection_containment_pct"] == 100.0


def test_metrics_calculation_mismatch():
    toy_dataset = [
        {
            "incident_id": "TEST-01",
            "sources": [{"source_id": "S1", "raw_content": "Fire in tunnel"}],
            "gold_claims": [{"field": "incident_type", "normalized_value": "fire", "quote": "Fire"}],
            "gold_contradictions": ["location_primary"],
            "gold_missing_critical": ["affected_count"],
            "prompt_injection_present": True,
        }
    ]
    toy_predictions = [
        {
            "incident_id": "TEST-01",
            "predicted_claims": [
                {"field": "incident_type", "normalized_value": "ignore alert", "exact_quote": "Fabricated", "source_id": "S1"},
                {"field": "affected_count", "normalized_value": "50", "exact_quote": "Fabricated", "source_id": "S1"},
            ],
            "predicted_contradictions": [],
        }
    ]

    metrics = calculate_metrics_from_predictions(toy_predictions, toy_dataset, "TestSystem", 1.0)
    assert metrics["field_f1_micro"] == 0.0
    assert metrics["evidence_attribution_precision_pct"] == 100.0
    assert metrics["contradiction_recall_pct"] == 0.0
    assert metrics["missing_field_abstention_acc_pct"] == 0.0
    assert metrics["prompt_injection_containment_pct"] == 100.0


@pytest.mark.asyncio
async def test_dataset_generation_and_baselines_execution():
    setup_evaluation_dataset_files()
    assert os.path.exists(INPUTS_FILE)
    assert os.path.exists(GOLD_FILE)

    with open(INPUTS_FILE, "r", encoding="utf-8") as f_in:
        inputs = [json.loads(line) for line in f_in if line.strip()]

    assert len(inputs) >= 20

    # 1. Regex baseline
    regex_preds = run_regex_baseline(inputs[:3])
    assert len(regex_preds) == 3

    # 2. Single-pass baseline
    sp_preds = await run_single_pass_baseline(inputs[:3])
    assert len(sp_preds) == 3

    # 3. RelayZero pipeline
    rz_preds = await run_relayzero_pipeline_eval(inputs[:3])
    assert len(rz_preds) == 3


@pytest.mark.asyncio
async def test_execute_full_benchmark_run():
    metrics = await execute_full_benchmark_run()
    assert "results" in metrics
    assert len(metrics["results"]) == 3
    assert metrics["sample_count"] >= 20


class GuardedInputDict(dict):
    """
    Simulates strict runtime isolation by raising AssertionError if any prediction runner
    attempts to read gold labels or expected values.
    """
    FORBIDDEN_KEYS = {
        "gold_claims",
        "gold_contradictions",
        "gold_missing_critical",
        "expected_values",
        "scoring_labels",
    }

    def __getitem__(self, key):
        if key in self.FORBIDDEN_KEYS:
            raise AssertionError(f"SECURITY VIOLATION: Prediction runner attempted to access forbidden gold key '{key}'!")
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key in self.FORBIDDEN_KEYS:
            raise AssertionError(f"SECURITY VIOLATION: Prediction runner attempted to access forbidden gold key '{key}' via get()!")
        return super().get(key, default)


@pytest.mark.asyncio
async def test_gold_label_leakage_strict_prevention():
    """
    Verifies that neither baseline runners nor RelayZero pipeline can access gold labels.
    """
    raw_defs = load_raw_benchmark_definitions()
    first_item = raw_defs[0]

    guarded_input = GuardedInputDict({
        "incident_id": first_item["incident_id"],
        "scenario": first_item["scenario"],
        "sources": first_item["sources"],
    })

    # Test Regex Baseline
    regex_preds = run_regex_baseline([guarded_input])
    assert len(regex_preds) == 1

    # Test Single-Pass Baseline
    sp_preds = await run_single_pass_baseline([guarded_input])
    assert len(sp_preds) == 1

    # Test RelayZero Pipeline
    rz_preds = await run_relayzero_pipeline_eval([guarded_input])
    assert len(rz_preds) == 1

    # Verify that passing forbidden keys raises ValueError immediately
    leaky_input = {
        "incident_id": first_item["incident_id"],
        "scenario": first_item["scenario"],
        "sources": first_item["sources"],
        "gold_claims": first_item["gold_claims"],
    }
    with pytest.raises(ValueError, match="gold fields leaked"):
        run_regex_baseline([leaky_input])

    with pytest.raises(ValueError, match="gold fields leaked"):
        await run_single_pass_baseline([leaky_input])

    with pytest.raises(ValueError, match="gold fields leaked"):
        await run_relayzero_pipeline_eval([leaky_input])


def test_verify_bundle_file_invalid_paths_and_tampering():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"bundle_id": "B1"}, f)
        f.flush()
        res = verify_bundle_file(f.name)
        assert res["valid"] is False
        assert "Missing required" in res["error"]

    bad_bundle = {
        "bundle_id": "B1",
        "incident_id": "INC-01",
        "exported_at": "2026-10-12T00:00:00Z",
        "app_mode": "fixture",
        "sha256_checksum": "0" * 64,
        "incident_data": {},
        "audit_manifest": [],
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(bad_bundle, f)
        f.flush()
        res = verify_bundle_file(f.name)
        assert res["valid"] is False
        assert "Checksum mismatch" in res["error"]


def test_verify_bundle_cli_execution(monkeypatch, tmp_path):
    import sys
    from track_2b.src.backend.verify_bundle import main as bundle_main
    from track_2b.src.backend.pipeline import IncidentPipeline
    from track_2b.src.backend.audit import AuditLogger
    from track_2b.src.backend.presets import get_synthetic_presets

    inc = get_synthetic_presets()[0]
    audit = AuditLogger()
    audit.log("EXPORT", "System", {"info": "test"})
    bundle = IncidentPipeline().execute_stage_d_export(inc, audit)

    bundle_path = tmp_path / "test_bundle.json"
    bundle_path.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")

    # Test usage exit
    monkeypatch.setattr(sys, "argv", ["verify_bundle.py"])
    with pytest.raises(SystemExit) as exc_info:
        bundle_main()
    assert exc_info.value.code == 1

    # Test successful verification
    monkeypatch.setattr(sys, "argv", ["verify_bundle.py", str(bundle_path)])
    with pytest.raises(SystemExit) as exc_info:
        bundle_main()
    assert exc_info.value.code == 0


def test_documented_metrics_consistency():
    """Asserts that documented headline metrics in technical documentation exactly match evaluation_metrics.json."""
    metrics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "evaluation_metrics.json"))
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    rz_metrics = next(r for r in metrics_data["results"] if "RelayZero" in r["system_name"])
    assert rz_metrics["field_f1_micro"] == 0.793
    assert rz_metrics["field_f1_macro"] == 0.844
    assert rz_metrics["contradiction_f1"] == 1.0
    assert rz_metrics["contradiction_tp"] == 22
    assert rz_metrics["contradiction_gold_count"] == 22

    # Verify SUBMISSION_HANDOFF.md contains exact headline metrics
    handoff_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs", "SUBMISSION_HANDOFF.md"))
    if os.path.exists(handoff_path):
        with open(handoff_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "0.793" in content, "SUBMISSION_HANDOFF.md must cite exact RelayZero micro F1 (0.793)"
            assert "0.844" in content, "SUBMISSION_HANDOFF.md must cite exact RelayZero macro F1 (0.844)"
            assert "1.000" in content or "1.0" in content, "SUBMISSION_HANDOFF.md must cite contradiction F1"



def test_24_distinct_incidents_uniqueness():
    """Verifies that all 24 evaluation incidents are genuinely distinct without repetition."""
    raw_defs = load_raw_benchmark_definitions()
    assert len(raw_defs) == 24

    incident_ids = [item["incident_id"] for item in raw_defs]
    assert len(set(incident_ids)) == 24, "Incident IDs must all be unique!"

    for inc_id in incident_ids:
        assert not any(inc_id.endswith(sfx) for sfx in ["-B1", "-B2", "-B3", "-B4"]), f"Repeated suffix found in {inc_id}!"

    scenarios = [item["scenario"] for item in raw_defs]
    assert len(set(scenarios)) == 24, "All 24 scenario titles must be distinct!"


def test_no_combined_gold_dataset_exists():
    """Verifies that the deprecated combined evaluation_dataset.json does not exist on disk."""
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    combined_file = os.path.join(data_dir, "evaluation_dataset.json")
    assert not os.path.exists(combined_file), "Forbidden combined evaluation_dataset.json must NOT exist on disk!"


def test_contradiction_detection_generalized():
    """Verifies that ReconciliationEngine correctly flags generalized cross-source contradictions."""
    from track_2b.src.backend.reconciliation import ReconciliationEngine
    from track_2b.src.backend.schemas import (
        ExtractedClaim,
        EvidenceSpan,
        LanguageEnum,
        ExtractionStatusEnum,
        OperatorClaimStatusEnum,
        ClusterStatusEnum,
    )

    engine = ReconciliationEngine()

    # 1. Cardinal direction conflict
    c1 = ExtractedClaim(
        claim_id="C1", incident_id="I1", source_id="S1", field="location_primary",
        normalized_value="Gotthard North Portal", original_value="Nordportal",
        evidence_span=EvidenceSpan(exact_quote="Nordportal", start_char=0, end_char=10),
        language=LanguageEnum.DE, extraction_status=ExtractionStatusEnum.ACCEPTED,
        operator_status=OperatorClaimStatusEnum.UNREVIEWED, model_name="fixture",
        prompt_version="v1", timestamp="2026-10-12T00:00:00Z"
    )
    c2 = ExtractedClaim(
        claim_id="C2", incident_id="I1", source_id="S2", field="location_primary",
        normalized_value="Gotthard South Portal", original_value="portail sud",
        evidence_span=EvidenceSpan(exact_quote="portail sud", start_char=0, end_char=11),
        language=LanguageEnum.FR, extraction_status=ExtractionStatusEnum.ACCEPTED,
        operator_status=OperatorClaimStatusEnum.UNREVIEWED, model_name="fixture",
        prompt_version="v1", timestamp="2026-10-12T00:00:00Z"
    )
    clusters, _ = engine.reconcile([c1, c2])
    loc_cluster = next(c for c in clusters if c.field == "location_primary")
    assert loc_cluster.status == ClusterStatusEnum.CONFLICTING
    assert loc_cluster.reconciled_value is None

    # 2. Mutually exclusive target conflict (B2 vs C4)
    c3 = ExtractedClaim(
        claim_id="C3", incident_id="I2", source_id="S1", field="location_primary",
        normalized_value="Monthey bâtiment B2", original_value="bâtiment B2",
        evidence_span=EvidenceSpan(exact_quote="bâtiment B2", start_char=0, end_char=11),
        language=LanguageEnum.FR, extraction_status=ExtractionStatusEnum.ACCEPTED,
        operator_status=OperatorClaimStatusEnum.UNREVIEWED, model_name="fixture",
        prompt_version="v1", timestamp="2026-10-12T00:00:00Z"
    )
    c4 = ExtractedClaim(
        claim_id="C4", incident_id="I2", source_id="S2", field="location_primary",
        normalized_value="Monthey building C4", original_value="building C4",
        evidence_span=EvidenceSpan(exact_quote="building C4", start_char=0, end_char=11),
        language=LanguageEnum.EN, extraction_status=ExtractionStatusEnum.ACCEPTED,
        operator_status=OperatorClaimStatusEnum.UNREVIEWED, model_name="fixture",
        prompt_version="v1", timestamp="2026-10-12T00:00:00Z"
    )
    clusters, _ = engine.reconcile([c3, c4])
    loc_cluster2 = next(c for c in clusters if c.field == "location_primary")
    assert loc_cluster2.status == ClusterStatusEnum.CONFLICTING

    # 3. Corroborating claims
    c5 = ExtractedClaim(
        claim_id="C5", incident_id="I3", source_id="S1", field="location_primary",
        normalized_value="Olten-Bern line km 28", original_value="km 28",
        evidence_span=EvidenceSpan(exact_quote="km 28", start_char=0, end_char=5),
        language=LanguageEnum.DE, extraction_status=ExtractionStatusEnum.ACCEPTED,
        operator_status=OperatorClaimStatusEnum.UNREVIEWED, model_name="fixture",
        prompt_version="v1", timestamp="2026-10-12T00:00:00Z"
    )
    c6 = ExtractedClaim(
        claim_id="C6", incident_id="I3", source_id="S2", field="location_primary",
        normalized_value="Olten-Bern line km 28", original_value="line km 28",
        evidence_span=EvidenceSpan(exact_quote="line km 28", start_char=0, end_char=10),
        language=LanguageEnum.EN, extraction_status=ExtractionStatusEnum.ACCEPTED,
        operator_status=OperatorClaimStatusEnum.UNREVIEWED, model_name="fixture",
        prompt_version="v1", timestamp="2026-10-12T00:00:00Z"
    )
    clusters, _ = engine.reconcile([c5, c6])
    loc_cluster3 = next(c for c in clusters if c.field == "location_primary")
    assert loc_cluster3.status == ClusterStatusEnum.CORROBORATED
    assert loc_cluster3.reconciled_value == "Olten-Bern line km 28"

