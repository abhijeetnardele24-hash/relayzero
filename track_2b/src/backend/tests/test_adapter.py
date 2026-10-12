"""
Unit tests for Apertus Adapter live and fixture mode separation.
"""

import pytest
from track_2b.src.backend.apertus_adapter import (
    ApertusAdapter,
    LiveEndpointError,
)
from track_2b.src.backend.schemas import AppModeEnum


@pytest.mark.asyncio
async def test_adapter_live_mode_without_endpoint_raises_error():
    # Live mode with no base_url MUST raise LiveEndpointError, never fall back silently!
    adapter = ApertusAdapter(app_mode=AppModeEnum.LIVE, base_url="")
    with pytest.raises(LiveEndpointError):
        await adapter.extract_claims_from_report(
            report_id="SRC-01",
            incident_id="INC-01",
            content="Smoke in Gotthard tunnel",
            language="de",
            modality="text",
        )


@pytest.mark.asyncio
async def test_adapter_live_mode_connection_failure():
    # Live mode with unreachable endpoint MUST raise LiveEndpointError
    adapter = ApertusAdapter(app_mode=AppModeEnum.LIVE, base_url="http://127.0.0.1:59999", timeout_seconds=1.0)
    with pytest.raises(LiveEndpointError):
        await adapter.extract_claims_from_report(
            report_id="SRC-01",
            incident_id="INC-01",
            content="Smoke in Gotthard tunnel",
            language="de",
            modality="text",
        )


def test_adapter_effective_model_identifier():
    fixture_adapter = ApertusAdapter(app_mode=AppModeEnum.FIXTURE)
    assert fixture_adapter.get_effective_model_identifier() == "Synthetic Demo Fixture"

    live_adapter = ApertusAdapter(app_mode=AppModeEnum.LIVE, model_name="swiss-ai/Apertus-v1.5-8B")
    assert live_adapter.get_effective_model_identifier() == "swiss-ai/Apertus-v1.5-8B"


def test_prompt_formatting_boundary_enclosure():
    adapter = ApertusAdapter()
    prompt = adapter.format_untrusted_evidence_prompt("TEST CONTENT", {"report_id": "SRC-01", "language": "de"})
    assert "<untrusted_field_evidence>" in prompt
    assert "</untrusted_field_evidence>" in prompt
    assert "TEST CONTENT" in prompt
