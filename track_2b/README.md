# RelayZero — Track 2B Submission: Own Project

**Air-Gapped, Multimodal Incident-Brief Compiler with Source-Linked Fact Reconciliation**

- **Project Name:** RelayZero
- **Track:** Track 2B — Own Project
- **Target Model:** `swiss-ai/Apertus-v1.5-8B`
- **Target Architecture:** Air-Gapped (Mandatory) / On-Premise / Sovereign Swiss Cloud
- **Repository:** https://github.com/abhijeetnardele24-hash/relayzero
- **Technical Report:** [RelayZero_Report.pdf](RelayZero_Report.pdf) (2 pages, max 6 pages limit compliant)

---

## Deliverables in `track_2b/`

1. **Working Code (`src/`):**
   - `src/backend/`: FastAPI decision-support backend with Apertus adapter, deterministic reconciliation, and SHA-256 audit logger.
   - `src/frontend/`: Field Operations Folio in React/TypeScript/Vite with zero horizontal overflow across 320px–1920px viewports.
2. **Technical Report:**
   - `technical_report.md`: Complete report mapping to all 5 judging criteria.
   - `RelayZero_Report.pdf`: Compiled 2-page academic PDF report.
3. **Data (`data/`):**
   - Total data size: ~25 KB (strictly under the 100 MB limit).
   - `data/evaluation_dataset.json`: 48 synthetic emergency incidents in DE, FR, IT, and EN.
   - `data/evaluation_metrics.json`: Quantitative benchmark outputs.
4. **Documentation & Screenshots (`docs/`):**
   - Architecture, Threat Model, Evaluation, Demo Script, and High-Resolution Screenshots.
5. **Reproducibility:**
   - `make run`: Starts the project in a Docker container from clean checkout.
   - `make test`: Runs 88%+ coverage unit, integration, and socket-level EGRESS 0 tests.
   - `make eval`: Runs the evaluation benchmark.

---

## Launch Command for Judges

```bash
make run
```
Launches container at `http://localhost:8000`.
