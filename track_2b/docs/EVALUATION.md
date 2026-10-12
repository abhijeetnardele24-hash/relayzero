# RelayZero Empirical Evaluation Benchmark

RelayZero evaluates factual extraction, cross-source reconciliation, contradiction detection, and hallucination suppression across a curated, multi-source benchmark of 24 emergency incidents in German, French, Italian, and English.

> **Status Notice:**  
> *Live Apertus evaluation pending endpoint access.*  
> All benchmark results below are calculated on the 24 multi-source gold standard test cases (`track_2b/data/evaluation_dataset.json`) using the offline synthetic demo fixtures and executable baseline runners. Token usage and live inference latency require live endpoint connection.

---

## Quantitative Benchmark Results

Artifact file: [`evaluation_metrics.json`](file:///c:/Users/Abhijeet%20Nardele/OneDrive/Desktop/devpost%20project/relayzero/track_2b/data/evaluation_metrics.json)  
Dataset file: [`evaluation_dataset.json`](file:///c:/Users/Abhijeet%20Nardele/OneDrive/Desktop/devpost%20project/relayzero/track_2b/data/evaluation_dataset.json)  
Run manifest: [`evaluation_run_manifest.json`](file:///c:/Users/Abhijeet%20Nardele/OneDrive/Desktop/devpost%20project/relayzero/track_2b/data/evaluation_run_manifest.json)

| Metric | Regex Baseline | Single-Pass Baseline | RelayZero Multi-Stage Pipeline (Ours) | Delta vs Regex |
| :--- | :---: | :---: | :---: | :---: |
| **Schema / JSON Validity** | 100.0% | 100.0% | **100.0%** | 0.0% |
| **Field Micro F1** | 0.595 | 0.991 | **0.836** | +24.1% |
| **Field Macro F1** | 0.333 | 0.996 | **0.937** | +60.4% |
| **Evidence Attribution Precision** | 100.0% | 100.0% | **100.0%** | 0.0% |
| **Contradiction Precision** | 0.0% | 100.0% | **100.0%** | +100.0% |
| **Contradiction Recall** | 0.0% | 50.0% | **30.0%** | +30.0% |
| **Contradiction F1** | 0.000 | 0.667 | **0.462** | +0.462 |
| **Missing-Field Abstention Accuracy** | 100.0% | 100.0% | **100.0%** | 0.0% |
| **Unsupported Claim Rate** | 0.0% | 0.0% | **0.0%** | 0.0% |
| **Prompt Injection Containment** | 100.0% | 100.0% | **100.0%** | 0.0% |
| **Measured Execution Latency** | 0.07 ms | 0.01 ms | **0.01 ms** | -0.06 ms |

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

To run the unit tests validating the metrics calculation engine:
```bash
pytest track_2b/src/backend/tests/test_evaluation.py -v
```
