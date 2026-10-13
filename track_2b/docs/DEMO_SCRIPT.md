# RelayZero Demonstration Script & Video Storyboards

**Target Duration:** Exactly 120 seconds (2:00 minutes max)  
**Format:** Screen recording + voiceover walkthrough  
**Scenario:** Preset 1: Alpine Tunnel Smoke Incident (Gotthard Corridor)

---

> [!IMPORTANT]
> **Demo Truthfulness Policy:**  
> RelayZero maintains strict honesty between live foundation model execution and offline deterministic demonstration fixtures.  
> - **Do NOT record the final competition submission video until a live model run succeeds unless hackathon organizers explicitly permit a fixture demonstration.**  
> - When recording using the fallback fixture script, you **must visibly and verbally disclose** that the system is operating on deterministic offline demo fixtures.

---

## SCRIPT 1: LIVE_APERTUS_DEMO_SCRIPT (Primary Competition Target)

*Use this script ONLY when `APP_MODE=live` is configured with active endpoint access (`LLM_BASE_URL` and `LLM_API_KEY`) and genuine `swiss-ai/Apertus-v1.5-8B` inference is executing.*

### 0:00–0:15 | The Problem & Sovereignty
- **Visual:** Focus on RelayZero Field Operations Folio. Point to top badge: `LIVE APERTUS: swiss-ai/Apertus-v1.5-8B`, `DEPLOYMENT: AIR-GAP CAPABLE`, `EGRESS: MONITORED`.
- **Voiceover:** *"In catastrophic emergencies like alpine tunnel fires, Swiss response centers receive contradictory field reports in German, French, Italian, and English. Sending operational coordinates to foreign cloud APIs creates data leakage risks, while monolithic LLMs fabricate consensus. RelayZero provides an air-gap capable decision-support system running live swiss-ai/Apertus-v1.5-8B."*

### 0:15–0:35 | Ingest Heterogeneous Multilingual Reports
- **Visual:** Evidence Rail displays three distinct reports:
  1. `SRC-DE-01`: German police dispatch (smoke near North Portal Göschenen at 14:05).
  2. `SRC-FR-02`: French scanned intervention sheet (smoke near South Portal Airolo, 20 people in safety niches).
  3. `SRC-IT-03`: Italian emergency call transcript (12 people in niche 4).
- **Voiceover:** *"Here we have three incoming field reports: German police radio, a French scanned operational sheet, and an Italian emergency audio transcript."*

### 0:35–1:00 | Live Isolated Apertus Extraction
- **Visual:** Click **"Compile Incident"**. Live inference spinner appears for ~1.5 seconds. Central claims canvas populates. Operator hovers over extracted claims, highlighting character-offset quote verification (`source[start:end] == quote`).
- **Voiceover:** *"Clicking 'Compile Incident', our live Apertus 8B model extracts structured operational slots inside isolated prompt boundaries. Every extracted claim is programmatically verified against exact verbatim quotes from the raw source text."*

### 1:00–1:25 | Deterministic Contradiction & Gap Detection
- **Visual:** Amber contradiction alert badges highlight conflicting `LOCATION_PRIMARY` (Gotthard North Portal vs Gotthard South Portal) and `AFFECTED_COUNT` (20 vs 12). Purple badge flags missing fields.
- **Voiceover:** *"Notice that instead of guessing or hallucinating an answer, RelayZero's reconciliation engine isolates the direct contradiction: Uri reported the North Portal, while Ticino reported the South Portal. Headcounts also diverge between 12 and 20."*

### 1:25–1:45 | Human Commander Review & Sign-Off Gate
- **Visual:** Operator clicks **"✓ Confirm This Fact"** on North Portal based on sensor telemetry, turning it confirmed (teal). Resolves headcount to 12. Operator clicks **"Sign & Approve"**. Safety gate shows verified pass.
- **Voiceover:** *"RelayZero enforces human oversight. The commander confirms ground truth from sensor telemetry. The approval safety gate validates that all critical contradictions are addressed before compiling the final multilingual brief."*

### 1:45–2:00 | Offline Tamper-Evident Export
- **Visual:** Operator downloads the checksummed bundle. Runs `python -m track_2b.src.backend.verify_bundle <bundle.json>` in terminal showing `✓ BUNDLE INTEGRITY VERIFIED` with SHA-256 hash-chain audit log.
- **Voiceover:** *"We export a checksummed, tamper-evident incident bundle with an immutable SHA-256 audit trail. RelayZero achieves 100% precision on contradiction discovery with exact evidence attribution—delivering sovereign, trustworthy emergency intelligence."*

---

## SCRIPT 2: FIXTURE_FALLBACK_DEMO_SCRIPT (Offline / Deterministic Review)

*Use this script when presenting offline or prior to live endpoint provisioning. You must clearly state the deterministic fixture status.*

### 0:00–0:15 | Introduction & Fixture Disclosure
- **Visual:** Focus on RelayZero Field Operations Folio. Point to top badge: `SYNTHETIC DEMO FIXTURE (OFFLINE DATA)`, `EGRESS: MONITORED`.
- **Voiceover:** *"This demonstration shows RelayZero operating in deterministic offline fixture mode using synthetic benchmark data. RelayZero is an air-gap capable decision-support compiler designed for Swiss emergency triage with Swiss-AI Apertus."*

### 0:15–0:35 | Multilingual Multi-Source Field Reports
- **Visual:** Load preset: *Alpine Tunnel Smoke Incident*. Show evidence rail with German dispatch, French scanned sheet, and Italian audio transcript.
- **Voiceover:** *"Our scenario models a multi-cantonal Gotthard incident with contradictory field reports across German, French, and Italian. In production, these are processed by Apertus-1.5-8B; in this demonstration, we use deterministic offline fixtures calibrated to our 24-incident benchmark."*

### 0:35–1:00 | Multi-Stage Evidence Architecture
- **Visual:** Click **"Compile Incident"**. Structured claims appear instantly (<1 ms). Show evidence pointer quote popup.
- **Voiceover:** *"Compiling the incident demonstrates our multi-stage architecture. Operational slots are extracted with character-level quote spans, ensuring that every claim is grounded directly in verbatim source text."*

### 1:00–1:25 | Contradiction Discovery
- **Visual:** Amber contradiction badges appear on `LOCATION_PRIMARY` (North Portal vs South Portal) and `AFFECTED_COUNT` (20 vs 12).
- **Voiceover:** *"Rather than synthesizing an artificial consensus, our reconciliation engine detects the direct contradiction between Uri and Ticino dispatchers, preventing dangerous operational errors."*

### 1:25–1:45 | Operator Confirmation & Safety Approval Gate
- **Visual:** Operator attempts approval—blocked by safety gate. Operator confirms North Portal and resolves headcount. Re-attempts approval—succeeds.
- **Voiceover:** *"The approval safety gate blocks brief sign-off until the commander confirms verified ground truth, ensuring human-in-the-loop operational safety."*

### 1:45–2:00 | Tamper-Evident Export & Reproducibility
- **Visual:** Download checksummed bundle. Terminal shows `verify_bundle` verification with SHA-256 hash chain.
- **Voiceover:** *"The incident exports as a checksummed JSON bundle with a cryptographic SHA-256 audit trail. All benchmarks are reproducible via `make eval`. RelayZero brings sovereign, verifiable AI to critical Swiss infrastructure."*
