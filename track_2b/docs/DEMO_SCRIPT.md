# RelayZero Demonstration Scripts & Video Guidelines

This directory contains the official competition video demonstration scripts for RelayZero (Hack Apertus 2026, Track 2B).

## Demonstration Scripts

1. **[Live Apertus Demonstration Script](file:///c:/Users/Abhijeet%20Nardele/OneDrive/Desktop/devpost%20project/relayzero/track_2b/docs/LIVE_APERTUS_DEMO_SCRIPT.md)**  
   *Use when running in `APP_MODE=live` with valid credentials against `swiss-ai/Apertus-v1.5-8B`.*  
   Demonstrates real-time model inference, prompt boundary defense, token metrics, and character-grounded extraction.

2. **[Deterministic Offline Demonstration Script](file:///c:/Users/Abhijeet%20Nardele/OneDrive/Desktop/devpost%20project/relayzero/track_2b/docs/FIXTURE_FALLBACK_DEMO_SCRIPT.md)**  
   *Use when recording in `APP_MODE=fixture` without live network access.*  
   Demonstrates the identical multi-stage UI, reconciliation engine, and safety gate, with explicit visual and verbal disclosure that offline benchmark fixtures are active.

---

## Video Submission Requirements

- **Maximum Duration:** 120 seconds (2:00 minutes).
- **Core Workflow Demonstrated:**
  1. Ingestion of multi-source Swiss emergency reports (DE, FR, IT).
  2. Character-grounded factual extraction linked to source spans (`source[start:end] == quote`).
  3. Contradiction discovery (Uri vs. Ticino dispatchers).
  4. Blocked approval safety gate & commander fact confirmation.
  5. Cryptographic bundle export with SHA-256 audit chaining.
