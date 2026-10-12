# RelayZero — Track 2B Submission: Own Project

**Air-Gapped, Multilingual, Multi-Source Incident-Brief Compiler with Source-Linked Fact Reconciliation**

- **Project Name:** RelayZero
- **Track:** Track 2B — Own Project
- **Target Model:** `swiss-ai/Apertus-v1.5-8B`
- **Target Architecture:** Air-Gapped (Mandatory) / On-Premise / Sovereign Swiss Cloud
- **Repository:** https://github.com/abhijeetnardele24-hash/relayzero
- **Technical Report:** [`RelayZero_Report.pdf`](file:///c:/Users/Abhijeet%20Nardele/OneDrive/Desktop/devpost%20project/relayzero/track_2b/RelayZero_Report.pdf) (4 pages, within official 6 pages limit)

---

## Deliverables in `track_2b/`

1. **Working Code (`src/`):**
   - `src/backend/`: FastAPI decision-support backend with Apertus adapter (live and fixture modes), deterministic reconciliation, safety gates, and SHA-256 audit logger.
   - `src/frontend/`: Field Operations Folio in React/TypeScript/Vite with zero horizontal overflow across 320px–1920px viewports and Axe accessibility compliance.
2. **Technical Report:**
   - `technical_report.md`: Complete report mapping to all judging criteria.
   - `RelayZero_Report.pdf`: Compiled 4-page PDF report.
3. **Data (`data/`):**
   - Total data size: ~27 KB (strictly under the 100 MB limit).
   - `data/evaluation_dataset.json`: 24 multi-source synthetic emergency incidents in DE, FR, IT, and EN.
   - `data/evaluation_metrics.json`: Quantitative benchmark outputs calculated from executable pipelines.
   - `data/evaluation_run_manifest.json`: Execution manifest with Git commit SHA and dataset checksums.
4. **Documentation & Screenshots (`docs/`):**
   - Architecture, Threat Model, Evaluation, Demo Script, and High-Resolution Screenshots.
5. **Reproducibility:**
   - `make run`: Starts the project from clean checkout.
   - `make test`: Runs 90% coverage unit, integration, and socket isolation tests (`--cov-fail-under=85`).
   - `make eval`: Runs the evaluation benchmark (`python track_2b/src/backend/evaluation_runner.py`).

---

## Launch Command for Judges

```bash
make run
```
Launches application at `http://localhost:8000`.
