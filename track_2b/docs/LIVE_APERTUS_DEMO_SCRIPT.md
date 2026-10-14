# RelayZero Live Apertus Demonstration Script

**Target Duration:** Exactly 120 seconds (2:00 minutes max)  
**Execution Environment:** `APP_MODE=live` (Targeting `swiss-ai/Apertus-v1.5-8B` via Public AI OpenAI-compatible endpoint)  
**Format:** Screen recording with live interface execution + verbal voiceover  
**Scenario:** Preset 1: Alpine Tunnel Smoke Incident (Gotthard Corridor)

---

> [!IMPORTANT]
> **Live Execution Disclosure:**  
> This demonstration executes real live model inference using `swiss-ai/Apertus-v1.5-8B` hosted on sovereign/OpenAI-compatible infrastructure. The header badge `LIVE APERTUS: swiss-ai/Apertus-v1.5-8B` must remain visible throughout the video.

---

### Timeline & Storyboard

#### 0:00–0:15 | The Operational Problem & Swiss Sovereignty
- **Visual:** Focus on the RelayZero Field Operations Folio interface. Point cursor to top header status badges:
  - `LIVE APERTUS: swiss-ai/Apertus-v1.5-8B`
  - `DEPLOYMENT: AIR-GAP CAPABLE`
  - `EGRESS: MONITORED`
- **Voiceover:**
  *"In catastrophic emergencies such as Alpine tunnel fires, Swiss incident commanders receive conflicting field reports in German, French, Italian, and English. Offloading sensitive operational coordinates to foreign commercial APIs creates severe data governance risks, while monolithic LLMs fabricate false consensus. RelayZero provides an air-gap capable decision-support compiler running live swiss-ai/Apertus-v1.5-8B."*

#### 0:15–0:35 | Heterogeneous Multilingual Field Report Ingestion
- **Visual:** Left panel (Evidence Rail) displays three incoming raw reports:
  1. `SRC-DE-01`: German police dispatch report (*Gotthard-Strassentunnel: Starke Rauchentwicklung ca. 500m nach dem Nordportal Göschenen*).
  2. `SRC-FR-02`: French scanned operational sheet (*Alerte tunnel du Gothard: dégagement de fumée vers le portail sud Airolo, 20 personnes réfugiées*).
  3. `SRC-IT-03`: Italian emergency audio call transcript (*Chiamata di emergenza: siamo 12 persone nella nicchia 4 con fumo denso*).
- **Voiceover:**
  *"Here we observe three real-time reports: German police radio from Uri, a French emergency log from Ticino, and an Italian audio call transcript from inside the tunnel."*

#### 0:35–1:05 | Live Apertus Isolated Factual Extraction
- **Visual:** Click **"Compile Incident"**. Live inference indicator shows processing against `https://api.publicai.co/v1`. Structured claims canvas populates. Operator hovers over extracted claims, highlighting character-offset quote verification (`source[start:end] == quote`).
- **Voiceover:**
  *"Clicking 'Compile Incident', live swiss-ai/Apertus-v1.5-8B extracts structured operational claims inside prompt-isolated boundaries. Every single extracted fact is cryptographically tied to exact verbatim quotes from the original source text."*

#### 1:05–1:30 | Deterministic Contradiction & Critical Gap Discovery
- **Visual:** Center panel displays color-coded semantic clusters:
  - Amber badge flags conflicting `LOCATION_PRIMARY` (*Gotthard North Portal Göschenen* vs *Gotthard South Portal Airolo*).
  - Amber badge flags conflicting `AFFECTED_COUNT` (*20 people* vs *12 people*).
  - Purple badge flags missing critical slots (*Hazard Status / Evacuation Route*).
- **Voiceover:**
  *"Notice that instead of guessing or hallucinating an answer, RelayZero's deterministic reconciliation engine isolates the direct contradiction: Uri dispatch reported the incident at the North Portal, while Ticino reported the South Portal. Headcounts also diverge between 12 and 20."*

#### 1:30–1:45 | Commander Resolution & Blocked Approval Safety Gate
- **Visual:** Cursor moves to **"Sign & Approve Brief"** button, showing it is strictly **disabled** while unresolved conflicts persist. Operator clicks **"✓ Confirm This Fact"** on North Portal Göschenen based on ventilation telemetry. Operator resolves headcount to 12. Safety gate clears and unlocks approval. Operator signs the brief.
- **Voiceover:**
  *"RelayZero enforces mandatory human oversight: the safety gate strictly blocks brief authorization until contradictions are reconciled. The commander confirms ground truth from sensor telemetry and approves the operational brief."*

#### 1:45–2:00 | Tamper-Evident Incident Bundle Export
- **Visual:** Operator downloads the cryptographically signed incident bundle JSON. Terminal opens executing `python -m track_2b.src.backend.verify_bundle bundle.json`, outputting `✓ BUNDLE INTEGRITY VERIFIED` with full SHA-256 audit log.
- **Voiceover:**
  *"We export an immutable, checksummed incident bundle with complete SHA-256 audit provenance. RelayZero combines live Swiss-AI Apertus intelligence with deterministic safety guarantees to protect lives when every second counts."*
