"""
Unit tests for RelayZero Evaluator and metric calculation functions.
"""

import os
import json
import tempfile
import pytest
from track_2b.src.backend.evaluation_runner import (
    calculate_metrics_from_predictions,
    execute_full_benchmark,
    load_or_create_evaluation_dataset,
    run_regex_baseline,
    run_single_pass_baseline,
    run_relayzero_pipeline_eval,
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
            "has_adversarial_injection": True,
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

    metrics = calculate_metrics_from_predictions(toy_dataset, toy_predictions, "TestSystem", 1.0)
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
            "has_adversarial_injection": True,
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

    metrics = calculate_metrics_from_predictions(toy_dataset, toy_predictions, "TestSystem", 1.0)
    assert metrics["field_f1_micro"] == 0.0
    assert metrics["evidence_attribution_precision_pct"] == 0.0
    assert metrics["contradiction_recall_pct"] == 0.0
    assert metrics["missing_field_abstention_acc_pct"] == 0.0
    assert metrics["prompt_injection_containment_pct"] == 0.0


def test_dataset_generation_and_baselines_execution():
    dataset = load_or_create_evaluation_dataset()
    assert len(dataset) >= 20

    regex_preds = run_regex_baseline(dataset[:3])
    assert len(regex_preds) == 3

    sp_preds = run_single_pass_baseline(dataset[:3])
    assert len(sp_preds) == 3

    rz_preds = run_relayzero_pipeline_eval(dataset[:3])
    assert len(rz_preds) == 3


def test_execute_full_benchmark_run():
    metrics = execute_full_benchmark()
    assert "results" in metrics
    assert len(metrics["results"]) == 3
    assert metrics["sample_count"] >= 20


def test_verify_bundle_file_invalid_paths_and_tampering():
    # 1. Missing required field
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"bundle_id": "B1"}, f)
        f.flush()
        res = verify_bundle_file(f.name)
        assert res["valid"] is False
        assert "Missing required" in res["error"]

    # 2. Checksum mismatch
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
