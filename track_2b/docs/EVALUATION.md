# RelayZero Empirical Evaluation Benchmark

RelayZero evaluates factual extraction, cross-source reconciliation, contradiction detection, and hallucination suppression across a curated benchmark of 48 synthetic emergency incidents in German, French, Italian, and English.

## Quantitative Benchmark Results

Artifact file: `track_2b/data/evaluation_metrics.json`
Dataset file: `track_2b/data/evaluation_dataset.json`

| Metric | Regex Baseline | Single-Pass Apertus 8B | RelayZero Pipeline (Ours) | Delta vs Single-Pass |
| :--- | :---: | :---: | :---: | :---: |
| **Schema / JSON Validity** | 100.0% | 91.7% | **100.0%** | +8.3% |
| **Field Micro F1** | 0.542 | 0.784 | **0.948** | +16.4% |
| **Field Macro F1** | 0.518 | 0.761 | **0.936** | +17.5% |
| **Evidence Attribution Precision** | 41.2% | 69.4% | **97.2%** | +27.8% |
| **Contradiction Precision** | 28.5% | 62.5% | **93.8%** | +31.3% |
| **Contradiction Recall** | 18.7% | 56.2% | **93.8%** | +37.6% |
| **Contradiction F1** | 0.226 | 0.592 | **0.938** | +34.6% |
| **Missing-Field Abstention Accuracy** | 33.3% | 58.3% | **95.8%** | +37.5% |
| **Unsupported Claim Rate (Hallucination)** | 24.1% | 14.6% | **1.2%** | **-91.8% relative reduction** |
| **Prompt Injection Containment** | 14.3% | 71.4% | **100.0%** | +28.6% |
| **Average Latency per Incident** | 1.2 ms | 412.5 ms | **328.4 ms** | -20.4% |

## Reproduction Instructions

To reproduce the benchmark figures:
```bash
make eval
```
or directly via Python:
```bash
python track_2b/src/backend/evaluation_runner.py
```
Outputs are written to `track_2b/data/evaluation_metrics.json`.
