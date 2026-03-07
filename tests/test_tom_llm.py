"""Tests for Phase 4 ToMTool LLM-based inference.

TDD: written before implementation.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_agent.tools.tom import ToMTool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_tom(
    backend_response: str | None = None,
    memories: list[dict] | None = None,
    default_person: str = "Kouta",
) -> ToMTool:
    """Create ToMTool with mocked memory and optional mocked backend."""
    memory = MagicMock()
    memory.recall_async = AsyncMock(return_value=memories or [])

    backend = None
    if backend_response is not None:
        backend = MagicMock()
        backend.complete = AsyncMock(return_value=backend_response)

    return ToMTool(memory=memory, default_person=default_person, backend=backend)


_VALID_JSON_RESPONSE = json.dumps(
    {
        "evidence": ["short message", "used casual tone"],
        "inference": [
            {"state": "tired", "confidence": 0.7},
            {"state": "wants reassurance", "confidence": 0.5},
        ],
        "policy": "Respond warmly and keep it brief",
    }
)


# ---------------------------------------------------------------------------
# Tests: backend is called
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tom_calls_backend_with_situation():
    """backend.complete() is called and situation text appears in the prompt."""
    tom = _make_tom(backend_response=_VALID_JSON_RESPONSE)
    situation = "今日しんどかった"
    await tom.call("tom", {"situation": situation})

    tom._backend.complete.assert_called_once()
    prompt_arg = tom._backend.complete.call_args[0][0]
    assert situation in prompt_arg


@pytest.mark.asyncio
async def test_tom_calls_backend_with_person_name():
    """Person name is included in the prompt sent to the backend."""
    tom = _make_tom(backend_response=_VALID_JSON_RESPONSE, default_person="Kouta")
    await tom.call("tom", {"situation": "何か悩んでる？", "person": "Kouta"})

    prompt_arg = tom._backend.complete.call_args[0][0]
    assert "Kouta" in prompt_arg


# ---------------------------------------------------------------------------
# Tests: structured output
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tom_output_has_evidence_section():
    """Output contains an evidence section."""
    tom = _make_tom(backend_response=_VALID_JSON_RESPONSE)
    result, _ = await tom.call("tom", {"situation": "ok"})
    assert "evidence" in result.lower() or "エビデンス" in result or "short message" in result


@pytest.mark.asyncio
async def test_tom_output_has_inference_section():
    """Output contains an inference section with mental states."""
    tom = _make_tom(backend_response=_VALID_JSON_RESPONSE)
    result, _ = await tom.call("tom", {"situation": "ok"})
    # "tired" and "wants reassurance" are the inferred states
    assert "tired" in result or "inference" in result.lower()


@pytest.mark.asyncio
async def test_tom_output_has_policy_section():
    """Output contains a policy / response recommendation."""
    tom = _make_tom(backend_response=_VALID_JSON_RESPONSE)
    result, _ = await tom.call("tom", {"situation": "ok"})
    assert "Respond warmly" in result or "policy" in result.lower()


@pytest.mark.asyncio
async def test_tom_shows_confidence_scores():
    """Inference entries include numeric confidence scores."""
    tom = _make_tom(backend_response=_VALID_JSON_RESPONSE)
    result, _ = await tom.call("tom", {"situation": "ok"})
    # Confidence 0.7 and 0.5 should appear in the formatted output
    assert "0.7" in result or "70" in result


# ---------------------------------------------------------------------------
# Tests: memory context
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tom_includes_memory_in_backend_prompt():
    """When memories exist, their content appears in the prompt to the backend."""
    memories = [{"summary": "Kouta tends to understate stress", "emotion": "concerned"}]
    tom = _make_tom(backend_response=_VALID_JSON_RESPONSE, memories=memories)
    await tom.call("tom", {"situation": "I'm fine"})

    prompt_arg = tom._backend.complete.call_args[0][0]
    assert "understate stress" in prompt_arg


@pytest.mark.asyncio
async def test_tom_no_memories_still_calls_backend():
    """With no memories, backend is still called (just without memory context)."""
    tom = _make_tom(backend_response=_VALID_JSON_RESPONSE, memories=[])
    result, _ = await tom.call("tom", {"situation": "hello"})
    tom._backend.complete.assert_called_once()
    assert result  # non-empty output


# ---------------------------------------------------------------------------
# Tests: fallback behaviour
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tom_malformed_json_returns_raw_response():
    """When backend returns non-JSON, output still contains the raw response text."""
    raw = "It seems Kouta is stressed and wants support."
    tom = _make_tom(backend_response=raw)
    result, _ = await tom.call("tom", {"situation": "tough day"})
    assert raw in result


@pytest.mark.asyncio
async def test_tom_no_backend_returns_template():
    """When backend=None, falls back to the static template (no LLM call)."""
    tom = _make_tom(backend_response=None)  # no backend
    result, _ = await tom.call("tom", {"situation": "hello"})
    # Template contains Japanese prompt framing keywords
    assert "投影" in result or "代入" in result or "状況" in result


# ---------------------------------------------------------------------------
# Tests: existing API unchanged
# ---------------------------------------------------------------------------


def test_get_tool_definitions_unchanged():
    """get_tool_definitions() still returns a valid tool spec list."""
    tom = _make_tom()
    defs = tom.get_tool_definitions()
    assert isinstance(defs, list)
    assert len(defs) == 1
    assert defs[0]["name"] == "tom"
    assert "input_schema" in defs[0]


@pytest.mark.asyncio
async def test_unknown_tool_name_returns_error():
    """call() with unknown tool name returns an error string."""
    tom = _make_tom()
    result, _ = await tom.call("unknown_tool", {})
    assert "unknown" in result.lower()
