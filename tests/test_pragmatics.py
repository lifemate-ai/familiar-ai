"""Pragmatic read: parsing, bounded call, and prompt injection."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_neighbor.mind.pragmatics import PragmaticRead, parse_pragmatic_read, pragmatic_read


def test_parse_three_lines_and_vocabulary_guard() -> None:
    raw = "implicature: 悔しさを隠している\nact: venting\nmove: 気持ちを受け止める。器用さの話に乗らない。"
    read = parse_pragmatic_read(raw)
    assert read == PragmaticRead(
        "悔しさを隠している", "venting", "気持ちを受け止める。器用さの話に乗らない。"
    )
    assert parse_pragmatic_read("**Implicature:** x\n**act:** made_up_label\nmove: y").act is None
    assert parse_pragmatic_read("random prose") is None
    assert read.prompt_lines() == ["- move: 気持ちを受け止める"]  # move only, first clause


@pytest.mark.asyncio
async def test_pragmatic_read_is_bounded_and_degrades_to_none() -> None:
    ok = MagicMock(complete=AsyncMock(return_value="implicature: a\nact: greeting\nmove: b"))
    read = await pragmatic_read(ok, "ただいま")
    assert read is not None and read.act == "greeting"
    assert await pragmatic_read(ok, "   ") is None
    ok.complete.assert_awaited_once()

    async def boom(prompt, max_tokens):
        raise RuntimeError("down")

    assert await pragmatic_read(MagicMock(complete=boom), "x") is None


def test_policy_prompt_carries_the_read() -> None:
    from types import SimpleNamespace

    from familiar_agent.agent import EmbodiedAgent

    policy = SimpleNamespace(
        primary_act="venting",
        response_mode="attuned",
        softness=0.9,
        directness=0.3,
        initiative=0.2,
        avoid_problem_solving=True,
        should_recall_relational_memory=False,
        mention_memory=False,
        avoid_raw_interoception_numbers=True,
        acknowledge_capacity=False,
    )
    text = EmbodiedAgent._format_social_policy_prompt(
        policy, PragmaticRead("悔しい", "venting", "受け止める")
    )
    assert text.endswith("- move: 受け止める")
    assert "implicature" not in EmbodiedAgent._format_social_policy_prompt(policy)
