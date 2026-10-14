# RelayZero Hack Apertus Submission Handoff

This document provides all verified, non-personal details required for the Lead Assistant to complete the official Hack Apertus 2026 Track 2B submission form at:  
http://hackapertus.ch/online-hack/submissions

---

## Field-by-Field Submission Checklist

| Form Field | Recommended Content |
| :--- | :--- |
| **Team Name** | `RelayZero Labs` (Solo participation: Abhijeet Nardele) |
| **Project Title** | `RelayZero` |
| **Track** | `Track 2B — Own Project` |
| **One-Line Pitch** | `An air-gap capable, multilingual, multi-source incident-brief compiler that transforms conflicting field reports into a source-linked situation board without sending sensitive operational data outside the deployment boundary.` |
| **Target Architecture (Mandatory)** | `b) Air-gapped (also deployable on a) On-premise and c) Sovereign Swiss cloud)` |
| **Model Used** | `swiss-ai/Apertus-v1.5-8B` (supports verified live endpoint execution via `APP_MODE=live` and deterministic synthetic demo fixtures via `APP_MODE=fixture`) |
| **Role of Apertus** | `Multilingual entity extraction, structured slot isolation, cross-source claim alignment, and grounded brief synthesis.` |
| **Git Repository URL** | `https://github.com/abhijeetnardele24-hash/relayzero` |
| **Repository Visibility** | `PUBLIC` |
| **Primary Launch Command** | `make run` (from clean checkout) |
| **Technical Report File** | `track_2b/RelayZero_Report.pdf` (strictly 4 pages, within official 6-page limit) |
| **Evaluation Dataset Files** | Separated strictly: `track_2b/data/evaluation_inputs.jsonl` (prediction inputs) and `track_2b/data/evaluation_gold.jsonl` (scoring only). Deprecated combined `evaluation_dataset.json` has been permanently deleted. (CDLA-Permissive-2.0, synthetic emergency operations benchmark, 24 genuinely distinct multi-source incidents across Switzerland in DE/FR/IT/EN) |
| **Demo Video URL** | `https://youtu.be/YoXeo-TnTsg` (Unlisted, 1:42, checks passed) |
| **Licensing** | Source Code: `Apache-2.0` \| Documentation: `CC-BY-4.0` \| Data: `CDLA-Permissive-2.0` |

---

## Key Achievements & Benchmark Numbers for Form Submission

- **Operational Status:** *Live Apertus integration verified through a three-report controlled smoke run; the 24-incident comparative benchmark remains deterministic fixture-based.* (Evaluation performed across 24 genuinely distinct Swiss emergency scenarios with physical separation of input and gold standard files).
- **Live Apertus Smoke Verification:** Controlled real-endpoint verification executed against `swiss-ai/apertus-v1.5-8b` via Public AI OpenAI-compatible endpoint across 3 representative Swiss emergency reports (DE, FR, IT). Successfully generated valid structured extractions (9 claims per report, ~30.3s average latency, 2,732 total tokens) with sanitized, verifiable artifacts in `track_2b/data/live_smoke_evidence.json`.
- **Field Extraction F1:** `0.793` (micro) / `0.844` (macro) on multi-source synthesis with 99.1% claim recall (109/110 gold claims) vs 0.674 micro / 0.617 macro (Regex baseline) and 0.879 micro / 0.842 macro (Single-pass extraction baseline without cross-source reconciliation).
- **Contradiction Detection:** `100.0%` precision (22/22), `100.0%` recall (22/22), `1.000` F1 vs 0.0% for regex (0/22) and single-pass (0/22) baselines.
- **Evidence Grounding:** `100.0%` evidence attribution precision via exact character-level substring quote validation (`source[start:end] == quote`); 0.0% unsupported claims; 100.0% missing-field abstention accuracy (35/35); 100.0% prompt injection containment (2/2).
- **Test Coverage:** 36 automated unit and integration tests with **93.53%** verified backend coverage (exceeding `pytest --cov-fail-under=85` requirement).
- **Latency Accounting:** <1 ms deterministic reconciliation/post-processing on the recorded local run; Apertus model inference measured approximately 30.3 seconds average through the Public AI endpoint (exact machine-readable measurements recorded in `evaluation_metrics.json` and `live_smoke_evidence.json`).
- **Infrastructure & Governance:** Architecture designed to support deployments under Swiss data-residency and governance requirements, subject to deployment-specific legal review. Designed for air-gapped operations with monitored egress. Local execution avoids external per-token API billing, while hardware, electricity, maintenance, and operational costs still apply.
- **Offline Integrity:** Checksummed tamper-evident bundle export with SHA-256 hash-chained audit manifest and offline verification CLI (`python -m track_2b.src.backend.verify_bundle <bundle.json>`).
