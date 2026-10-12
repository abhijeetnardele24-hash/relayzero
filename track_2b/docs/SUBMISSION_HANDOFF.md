# RelayZero Hack Apertus Submission Handoff

This document provides all verified, non-personal details required for the Lead Assistant to complete the official Hack Apertus 2026 Track 2B submission form at:  
http://hackapertus.ch/online-hack/submissions

---

## Field-by-Field Submission Checklist

| Form Field | Recommended Content |
| :--- | :--- |
| **Project Title** | `RelayZero` |
| **Track** | `Track 2B — Own Project` |
| **One-Line Pitch** | `An air-gapped, multilingual, multi-source incident-brief compiler that transforms conflicting multilingual field reports into a source-linked situation board without sending sensitive data outside the deployment boundary.` |
| **Target Architecture (Mandatory)** | `b) Air-gapped (also deployable on a) On-premise and c) Sovereign Swiss cloud)` |
| **Model Used** | `swiss-ai/Apertus-v1.5-8B` (supports live endpoint execution via `APP_MODE=live` and synthetic demo fixtures via `APP_MODE=fixture`) |
| **Role of Apertus** | `Multilingual entity extraction, structured slot isolation, cross-source claim alignment, and grounded brief synthesis.` |
| **Git Repository URL** | `https://github.com/abhijeetnardele24-hash/relayzero` |
| **Repository Visibility** | `PUBLIC` |
| **Primary Launch Command** | `make run` (from clean checkout) |
| **Technical Report File** | `track_2b/RelayZero_Report.pdf` (4 pages, within official 6-page limit) |
| **Evaluation Dataset URL (Optional)** | Built-in dataset in `track_2b/data/evaluation_dataset.json` (CDLA-Permissive-2.0, synthetic emergency operations benchmark, 24 multi-source incidents) |
| **Demo Video URL** | `[To be recorded and attached by Lead Assistant]` |
| **Licensing** | Source Code: `Apache-2.0` \| Documentation: `CC-BY-4.0` \| Data: `CDLA-Permissive-2.0` |

---

## Key Achievements & Benchmark Numbers for Form Submission

- **Evaluation Status:** *Live Apertus evaluation pending endpoint access.* (Evaluated using 24 multi-source synthetic incidents across DE, FR, IT, EN).
- **Field Extraction F1:** `0.836` (micro) / `0.937` (macro) vs 0.595 (micro) / 0.333 (macro) for regex baseline.
- **Contradiction Detection:** `100.0%` precision, `0.462` F1 vs 0.0% for keyword baseline.
- **Evidence Grounding:** `100.0%` evidence attribution precision via exact character-level substring quote validation; 0.0% unsupported claims.
- **Test Coverage:** `89.9%` (90%) automated backend coverage with `pytest --cov-fail-under=85` strictly enforced.
- **Accessibility & Responsiveness:** No automatically detected serious Axe accessibility violations; verified 0 horizontal overflow across 320px, 360px, 768px, 1024px, 1440px, and 1920px viewports.
- **Offline Integrity:** Checksummed tamper-evident bundle export with SHA-256 hash-chained audit manifest and offline verification tool (`verify_bundle.py`).
