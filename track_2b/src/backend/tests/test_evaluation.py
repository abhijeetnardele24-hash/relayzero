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
