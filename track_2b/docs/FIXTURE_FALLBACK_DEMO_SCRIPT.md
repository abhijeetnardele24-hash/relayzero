# RelayZero Offline Demonstration Script (Deterministic Fixture Mode)

**Target Duration:** Exactly 120 seconds (2:00 minutes max)  
**Execution Environment:** `APP_MODE=fixture` (Deterministic offline demonstration fixtures)  
**Format:** Screen recording with interface walkthrough + verbal voiceover  
**Scenario:** Preset 1: Alpine Tunnel Smoke Incident (Gotthard Corridor)

---

> [!CAUTION]
> **Mandatory Offline Disclosure Policy:**  
> When recording using this fallback fixture script, you **must visibly and verbally disclose** that the system is operating on deterministic offline demonstration fixtures calibrated to the 24-incident benchmark suite. The header badge `SYNTHETIC DEMO FIXTURE (OFFLINE DATA)` must remain clearly visible.

---

### Timeline & Storyboard

#### 0:00–0:15 | Introduction & Transparent Fixture Disclosure
- **Visual:** Focus on the RelayZero Field Operations Folio interface. Point cursor directly to the top status badges:
  - `SYNTHETIC DEMO FIXTURE (OFFLINE DATA)`
  - `DEPLOYMENT: AIR-GAP CAPABLE`
  - `EGRESS: MONITORED (0 EXTERNAL CALLS)`
- **Voiceover:**
  *"This demonstration shows RelayZero operating in deterministic offline fixture mode using synthetic benchmark data. RelayZero is an air-gap capable decision-support compiler designed for Swiss emergency triage using Swiss-AI Apertus."*

#### 0:15–0:35 | Heterogeneous Multilingual Field Report Ingestion
- **Visual:** Left panel (Evidence Rail) displays three raw incoming reports:
  1. `SRC-DE-01`: German police radio (*Gotthard-Strassentunnel: Starke Rauchentwicklung ca. 500m nach dem Nordportal Göschenen*).
  2. `SRC-FR-02`: French scanned operational log (*Alerte tunnel du Gothard: dégagement de fumée vers le portail sud Airolo*).
  3. `SRC-IT-03`: Italian emergency call transcript (*Chiamata di emergenza: siamo 12 persone nella nicchia 4*).
- **Voiceover:**
  *"Our scenario models a multi-cantonal Gotthard incident with contradictory field reports across German, French, and Italian. In live deployment, these are processed by Apertus-1.5-8B; here, we run our verified deterministic fixtures."*

#### 0:35–1:00 | Multi-Stage Evidence Extraction Architecture
- **Visual:** Click **"Compile Incident"**. Structured operational claims populate instantly (<1 ms). Operator hovers over claims, demonstrating verbatim substring quote attribution linking each fact to character offsets in the source text.
- **Voiceover:**
  *"Compiling the incident demonstrates our multi-stage architecture. Operational slots are extracted with character-level quote spans, ensuring that every claim is grounded directly in verbatim source text."*

#### 1:00–1:25 | Deterministic Contradiction Discovery
- **Visual:** Central canvas highlights amber contradiction badges:
  - `LOCATION_PRIMARY`: *Gotthard North Portal* vs *Gotthard South Portal*.
  - `AFFECTED_COUNT`: *20 individuals* vs *12 individuals*.
- **Voiceover:**
  *"Rather than synthesizing an artificial consensus, our reconciliation engine detects the direct contradiction between Uri and Ticino dispatchers, preventing dangerous operational errors."*

#### 1:25–1:45 | Commander Confirmation & Safety Gate Enforcement
- **Visual:** Operator attempts to approve; **"Sign & Approve Brief"** button is strictly disabled until conflicts are reviewed. Operator clicks **"✓ Confirm This Fact"** for North Portal and confirms headcount. Safety gate unlocks. Operator enters commander signature.
- **Voiceover:**
  *"RelayZero enforces human oversight. The approval safety gate blocks briefing sign-off until all contradictions are reviewed and resolved by the commanding officer."*

#### 1:45–2:00 | Tamper-Evident Export & Audit Integrity
- **Visual:** Operator downloads the JSON incident bundle. Runs CLI verifier: `python -m track_2b.src.backend.verify_bundle bundle.json`, verifying SHA-256 hash chaining and zero external egress.
- **Voiceover:**
  *"We export a tamper-evident incident bundle with an immutable audit trail. RelayZero proves that localized AI and deterministic verification deliver reliable, sovereign emergency response."*
