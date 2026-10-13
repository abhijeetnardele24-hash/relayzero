# RelayZero Demonstration Script & Video Shot List

**Target Duration:** Exactly 120 seconds (2:00 minutes max)  
**Format:** Screen recording + voiceover walkthrough  
**Scenario:** Preset 1: Alpine Tunnel Smoke Incident (Gotthard Corridor)

---

## Storyboard & Shot List

### 0:00–0:12 | The Problem & Sovereignty Promise
- **Visual:** Fast zoom into emergency operations title card, transitioning to RelayZero Field Operations Folio.
- **Voiceover:** *"In catastrophic emergencies like tunnel fires or floods, Swiss operations centers receive contradictory reports across text messages, scanned forms, and voice notes in multiple languages. Sending this sensitive data to foreign cloud APIs violates civil sovereignty, while monolithic LLMs hallucinate false consensus. Enter RelayZero."*

### 0:12–0:27 | Air-Gapped Status & Scenario Selection
- **Visual:** Cursor highlights the top status strip: `AIR-GAP CAPABLE (SOVEREIGN)`, `SYNTHETIC DEMO FIXTURE` (or `LIVE APERTUS`), `EGRESS: MONITORED`. Switcher selects *Alpine Tunnel Smoke (Gotthard)*.
- **Voiceover:** *"RelayZero runs locally on premise with verified network isolation, designed for Swiss-AI Apertus. We load our Alpine tunnel incident."*

### 0:27–0:48 | Ingest Multilingual Text, Scanned Form, and Voice Audio
- **Visual:** Left evidence rail displays three reports:
  1. `SRC-DE-01`: German dispatch text (smoke near North Portal Göschenen at 14:05).
  2. `SRC-FR-02`: French scanned protocol form (smoke near South Portal Airolo, 20 people in safety niches).
  3. `SRC-IT-03`: Italian emergency call transcript (12 trapped people in niche 4).
- **Voiceover:** *"Here we have three conflicting field reports: German police dispatch, a French scanned intervention sheet, and an Italian emergency radio transcript."*

### 0:48–1:15 | Source-Linked Claim Extraction
- **Visual:** Operator clicks **"Compile Incident"**. The central canvas populates with structured claims. Clicking any claim reveals its exact verbatim evidence pointer quote and source tag.
- **Voiceover:** *"Clicking 'Compile Incident', Apertus extracts structured operational facts in isolated inference. Every claim is strictly linked to its original source with exact character-level substring quotes, reducing prompt-injection propagation."*

### 1:15–1:34 | Contradiction & Missing-Data Discovery
- **Visual:** Amber contradiction alert badge appears on `LOCATION_PRIMARY` (North Portal vs South Portal) and `AFFECTED_COUNT` (20 persons vs 12 persons). Purple badge flags missing fields.
- **Voiceover:** *"Instead of hallucinating an answer, RelayZero's reconciliation engine flags the direct conflict: Uri police reported North Portal, while Ticino reported South Portal. Headcounts also conflict between 12 and 20."*

### 1:34–1:49 | Human Review & Operator Confirmation
- **Visual:** Operator clicks **"✓ Confirm This Fact"** on North Portal (turning it teal) and resolves the headcount to 12. Operator clicks **"Sign & Approve"** in the right panel.
- **Voiceover:** *"RelayZero empowers the human operator to inspect the evidence and confirm verified ground truth. The brief instantly updates across German, French, Italian, and English."*

### 1:49–2:00 | Tamper-Evident Offline Export & Measured Impact
- **Visual:** Operator clicks **"Bundle"** to download the checksummed tamper-evident bundle. Clicks **"Verify Chain"** showing intact SHA-256 hash trail. Closes on evaluation table showing reproducible benchmark metrics.
- **Voiceover:** *"We export a checksummed, tamper-evident incident bundle with an unbroken SHA-256 audit trail. RelayZero achieves 100% precision on detected contradictions, 100% evidence attribution with zero unsupported claims—delivering sovereign, trustworthy emergency intelligence."*
