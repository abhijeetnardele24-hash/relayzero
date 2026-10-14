"""
RelayZero Live Apertus Smoke & Evidence Runner.
Executes real inference requests against the live swiss-ai/Apertus-v1.5-8B endpoint
(via Public AI OpenAI-compatible API) for representative multilingual Swiss emergency reports.
Generates sanitized, verifiable evidence artifacts without leaking API keys or secrets.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

try:
    from dotenv import load_dotenv
    load_dotenv()
    for candidate in [".env", "track_2b/.env", "../.env", "../../.env"]:
        if os.path.exists(candidate):
            load_dotenv(candidate)
except ImportError:
    pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from track_2b.src.backend.schemas import AppModeEnum
from track_2b.src.backend.apertus_adapter import ApertusAdapter, get_git_commit_sha

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("relayzero.live_smoke")

REPRESENTATIVE_REPORTS = [
    {
        "language": "de",
        "incident_id": "EVAL-INC-001",
        "report_id": "SRC-DE-01",
        "modality": "text",
        "content": "Gotthard-Strassentunnel: Starke Rauchentwicklung ca. 500m nach dem Nordportal Göschenen um 14:05 Uhr gemeldet. Tunnel gesperrt.",
    },
    {
        "language": "fr",
        "incident_id": "EVAL-INC-002",
        "report_id": "SRC-FR-04",
        "modality": "text",
        "content": "Crue subite du Rhône à Sion: Gymnase des Collines ouvert comme abri d'urgence. 150 personnes évacuées accueillies.",
    },
    {
        "language": "it",
        "incident_id": "EVAL-INC-001",
        "report_id": "SRC-IT-03",
        "modality": "voice_transcript",
        "content": "Chiamata di emergenza: siamo bloccati nella galleria del San Gottardo, siamo 12 persone nella nicchia 4 con fumo denso.",
    },
]

OUTPUT_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "live_smoke_evidence.json")
)


async def run_live_smoke() -> Dict[str, Any]:
    logger.info("Initializing ApertusAdapter in LIVE mode...")
    adapter = ApertusAdapter(app_mode=AppModeEnum.LIVE, timeout_seconds=90.0)

    if not adapter.api_key:
        raise RuntimeError("LLM_API_KEY is not set in environment or .env. Cannot run live smoke test.")
    if not adapter.base_url:
        raise RuntimeError("LLM_BASE_URL is not set. Cannot run live smoke test.")

    code_sha = get_git_commit_sha()
    evidence_records: List[Dict[str, Any]] = []

    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_latency_ms = 0.0

    logger.info("Starting controlled live smoke inference against: %s", adapter.base_url)
    logger.info("Target model: %s | Evaluated code commit: %s", adapter.model_name, code_sha)

    for idx, rep in enumerate(REPRESENTATIVE_REPORTS, 1):
        lang = rep["language"].upper()
        logger.info(
            "[%d/%d] Executing Live Apertus extraction for [%s] (Report: %s, Incident: %s)...",
            idx,
            len(REPRESENTATIVE_REPORTS),
            lang,
            rep["report_id"],
            rep["incident_id"],
        )

        res = await adapter.extract_claims_from_report(
            report_id=rep["report_id"],
            incident_id=rep["incident_id"],
            content=rep["content"],
            language=rep["language"],
            modality=rep["modality"],
        )

        evidence = res["evidence_artifact"]
        evidence["source_report_id"] = rep["report_id"]
        evidence["source_language"] = rep["language"]
        evidence["source_modality"] = rep["modality"]
        evidence["source_incident_id"] = rep["incident_id"]
        evidence["evaluated_code_sha"] = code_sha

        # Aggregate metrics
        usage = evidence.get("token_usage") or {}
        p_tok = usage.get("prompt_tokens", 0)
        c_tok = usage.get("completion_tokens", 0)
        total_prompt_tokens += p_tok
        total_completion_tokens += c_tok
        total_latency_ms += evidence.get("latency_ms", 0.0)

        claims_count = len(evidence.get("parsed_structured_output", {}).get("claims", []))
        logger.info(
            "[%s] Completed in %.2f ms | Claims: %d | Tokens: (P:%d, C:%d, Total:%d)",
            lang,
            evidence.get("latency_ms", 0.0),
            claims_count,
            p_tok,
            c_tok,
            p_tok + c_tok,
        )

        evidence_records.append(evidence)

    summary_artifact = {
        "benchmark_type": "Controlled Live Apertus Integration Smoke Test",
        "status": "Live Apertus integration verified; full deterministic benchmark remains fixture-based.",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "model_identifier": adapter.get_effective_model_identifier(),
        "endpoint_host": adapter.generate_sanitized_evidence("", "", {}, 0)["endpoint_base"],
        "evaluated_code_sha": code_sha,
        "sample_count": len(evidence_records),
        "total_latency_ms": round(total_latency_ms, 2),
        "average_latency_ms": round(total_latency_ms / len(evidence_records), 2),
        "token_usage_aggregate": {
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "total_tokens": total_prompt_tokens + total_completion_tokens,
        },
        "records": evidence_records,
    }

    # Strict secret scan on serialized JSON
    serialized = json.dumps(summary_artifact, indent=2, ensure_ascii=False)
    if adapter.api_key and adapter.api_key in serialized:
        raise ValueError("CRITICAL SECURITY ERROR: API key detected in output evidence! Halting.")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(serialized)

    logger.info("Successfully wrote sanitized live evidence artifact to: %s", OUTPUT_FILE)
    return summary_artifact


if __name__ == "__main__":
    asyncio.run(run_live_smoke())
