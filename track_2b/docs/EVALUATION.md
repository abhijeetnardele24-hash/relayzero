# RelayZero Empirical Evaluation Benchmark

RelayZero evaluates factual extraction, cross-source reconciliation, contradiction detection, and hallucination suppression across a curated, multi-source benchmark of 24 emergency incidents in German, French, Italian, and English.

> **Status Notice:**  
> *Operational Status: Live Apertus integration verified; full deterministic benchmark remains fixture-based.*  
> All benchmark results below are calculated on the 24 multi-source test cases using the decoupled inputs (`track_2b/data/evaluation_inputs.jsonl`) and scored against gold annotations (`track_2b/data/evaluation_gold.jsonl`) after inference. Prediction runners have zero access to gold labels.

---

## Quantitative Results (Deterministic Engineering Regression Benchmark)

Artifact file: [`evaluation_metrics.json`](../data/evaluation_metrics.json)  
Inputs file: [`evaluation_inputs.jsonl`](../data/evaluation_inputs.jsonl)  
Gold file: [`evaluation_gold.jsonl`](../data/evaluation_gold.jsonl)  
Run manifest: [`evaluation_run_manifest.json`](../data/evaluation_run_manifest.json)

| Metric | Regex Baseline | Single-Pass Baseline | RelayZero Multi-Stage Pipeline (Ours) | Delta vs Single-Pass |
| :--- | :---: | :---: | :---: | :---: |
| **Schema / JSON Validity** | 100.0% | 100.0% | **100.0%** | 0.0% |
| **Field Micro F1** | 0.674 | 0.879 | **0.793** | -0.086 (Reconciled) |
| **Field Macro F1** | 0.617 | 0.842 | **0.844** | +0.002 |
| **Claim Recall (Micro)** | 82.7% (91/110) | 79.1% (87/110) | **99.1% (109/110)** | **+20.0%** |
| **Evidence Attribution Precision** | 100.0% | 100.0% | **100.0%** | 0.0% |
| **Contradiction Precision** | 0.0% (0/22) | 0.0% (0/22) | **100.0% (22/22)** | **+100.0%** |
| **Contradiction Recall** | 0.0% (0/22) | 0.0% (0/22) | **100.0% (22/22)** | **+100.0%** |
| **Contradiction F1** | 0.000 | 0.000 | **1.000** | **+1.000** |
| **Missing-Field Abstention Accuracy** | 100.0% (35/35) | 100.0% (35/35) | **100.0% (35/35)** | 0.0% |
| **Unsupported Claim Rate** | 0.0% | 0.0% | **0.0%** | 0.0% |
| **Prompt Injection Containment** | 100.0% (2/2) | 100.0% (2/2) | **100.0% (2/2)** | 0.0% |
| **Deterministic Latency** | 0.33 ms | 0.37 ms | **0.35 ms** | -0.02 ms |

---

## Architectural & Gold Isolation Invariants

1. **Decoupled Data Files:** Prediction runners receive exclusively `evaluation_inputs.jsonl` (containing only incident IDs and raw source reports). Gold annotations are stored separately in `evaluation_gold.jsonl` and loaded solely by the scoring process after prediction files are written.
2. **Real Pipeline Execution:** The RelayZero evaluation runner executes the actual application `ApertusAdapter`, `IncidentPipeline`, and `ReconciliationEngine` using the production Pydantic schemas.
3. **Contradiction Discovery:** While the regex and single-pass baselines fail to detect any cross-source contradictions (0.0% F1), RelayZero's deterministic reconciliation engine identifies cross-source divergences with verified attribution.

---

## Reproduction Instructions

To execute the three evaluation pipelines and reproduce `evaluation_metrics.json`:

```bash
python track_2b/src/backend/evaluation_runner.py
```

Predictions are saved directly to:
- `track_2b/data/evaluation_predictions_regex.jsonl`
- `track_2b/data/evaluation_predictions_single_pass.jsonl`
- `track_2b/data/evaluation_predictions_relayzero.jsonl`

To run the unit tests validating the metrics calculation engine and proving zero gold leakage:
```bash
pytest track_2b/src/backend/tests/test_evaluation.py -v
```
