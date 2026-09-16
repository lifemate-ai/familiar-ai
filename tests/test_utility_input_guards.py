"""Utility LLM calls must not fire on empty input (small models ask back, and that
answer used to be persisted as a self-narrative)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_agent.agent import EmbodiedAgent, _looks_like_self_narrative
from familiar_agent.ollama_backend import OllamaBackend


def _agent(recall_summaries=None, recall=None, reply=""):
    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._turn_count = 2
    mem = MagicMock()
    mem.recall_day_summaries_async = AsyncMock(return_value=recall_summaries or [])
    mem.recall_async = AsyncMock(return_value=recall or [])
    agent._memory = mem
    agent._utility_backend = MagicMock(complete=AsyncMock(return_value=reply))
    agent.backend = MagicMock()
    agent._self_narrative = MagicMock()
    agent._decayed_mood = lambda: ("neutral", 0.0)
    return agent


@pytest.mark.asyncio
async def test_today_narrative_skips_when_there_is_nothing_to_narrate() -> None:
    agent = _agent()
    await agent._write_today_narrative()
    agent._utility_backend.complete.assert_not_awaited()
    agent._self_narrative.write.assert_not_called()


@pytest.mark.asyncio
async def test_today_narrative_rejects_a_request_for_input() -> None:
    agent = _agent(
        recall=[{"content": "窓の外を見た"}],
        reply="**「今日起きたこと（要約）」を教えていただければ",
    )
    await agent._write_today_narrative()
    agent._utility_backend.complete.assert_awaited_once()
    agent._self_narrative.write.assert_not_called()


@pytest.mark.asyncio
async def test_today_narrative_writes_a_real_sentence() -> None:
    agent = _agent(
        recall=[{"content": "窓の外を見た"}], reply="ウチは今日、窓の外の夕日をじっと見てた。"
    )
    await agent._write_today_narrative()
    agent._self_narrative.write.assert_called_once()


def test_looks_like_self_narrative() -> None:
    assert _looks_like_self_narrative("ウチは今日、静かな部屋で待ってた。")
    assert not _looks_like_self_narrative("")
    assert not _looks_like_self_narrative("今日の要約を教えてください。")
    assert not _looks_like_self_narrative("Could you provide the summary?")
    assert not _looks_like_self_narrative("# 今日\n- 項目")
    assert not _looks_like_self_narrative("ウチは" * 60)


@pytest.mark.asyncio
async def test_infer_emotion_and_curiosity_skip_blank_input() -> None:
    agent = _agent()
    assert await agent._infer_emotion("   ") == "neutral"
    assert await agent.extract_curiosity("") is None
    agent._utility_backend.complete.assert_not_awaited()


@pytest.mark.asyncio
async def test_ollama_complete_ignores_blank_prompt() -> None:
    calls = []

    async def spy(body):
        calls.append(body)
        yield {"message": {"content": "?"}, "done": True}

    be = OllamaBackend("m", stream_factory=spy)
    assert await be.complete("  \n", 10) == ""
    assert calls == []
