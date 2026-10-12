# RelayZero Empirical Evaluation Benchmark

RelayZero evaluates factual extraction, cross-source reconciliation, contradiction detection, and hallucination suppression across a curated, multi-source benchmark of 24 emergency incidents in German, French, Italian, and English.

> **Status Notice:**  
> *Deterministic engineering regression tests.*  
> *Live Apertus evaluation pending endpoint access.*  
> All benchmark results below are calculated on the 24 multi-source test cases using the decoupled inputs (`track_2b/data/evaluation_inputs.jsonl`) and scored against gold annotations (`track_2b/data/evaluation_gold.jsonl`) after inference. Prediction runners have zero access to gold labels.

---

## Quantitative Results (Deterministic Engineering Regression Benchmark)

Artifact file: [`evaluation_metrics.json`](file:///c:/Users/Abhijeet%20Nardele/OneDrive/Desktop/devpost%20project/relayzero/track_2b/data/evaluation_metrics.json)  
Inputs file: [`evaluation_inputs.jsonl`](file:///c:/Users/Abhijeet%20Nardele/OneDrive/Desktop/devpost%20project/relayzero/track_2b/data/evaluation_inputs.jsonl)  
Gold file: [`evaluation_gold.jsonl`](file:///c:/Users/Abhijeet%20Nardele/OneDrive/Desktop/devpost%20project/relayzero/track_2b/data/evaluation_gold.jsonl)  
Run manifest: [`evaluation_run_manifest.json`](file:///c:/Users/Abhijeet%20Nardele/OneDrive/Desktop/devpost%20project/relayzero/track_2b/data/evaluation_run_manifest.json)

| Metric | Regex Baseline | Single-Pass Baseline | RelayZero Multi-Stage Pipeline (Ours) |
| :--- | :---: | :---: | :---: |
| **Schema / JSON Validity** | 100.0% | 100.0% | **100.0%** |
| **Field Micro F1** | 0.690 | 0.278 | **0.311** |
| **Field Macro F1** | 0.599 | 0.242 | **0.273** |
| **Evidence Attribution Precision** | 100.0% | 100.0% | **100.0%** |
| **Contradiction Precision** | 0.0% | 0.0% | **100.0%** |
| **Contradiction Recall** | 0.0% | 0.0% | **20.0%** |
| **Contradiction F1** | 0.000 | 0.000 | **0.333** |
| **Missing-Field Abstention Accuracy** | 100.0% | 100.0% | **100.0%** |
| **Unsupported Claim Rate** | 0.0% | 0.0% | **0.0%** |
| **Prompt Injection Containment** | 100.0% | 100.0% | **100.0%** |
| **Measured Execution Latency** | 0.12 ms | 0.02 ms | **0.11 ms** |

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
