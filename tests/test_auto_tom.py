"""Deterministic perspective-taking: should_use_tom actually runs the ToM tool.

SocialPolicyEngine sets should_use_tom on emotionally loaded turns, but the
flag used to be consumed by nobody — perspective-taking only happened if the
model spontaneously called the tool. These tests pin the new deterministic
path: flag → ToM inference → prompt injection → person-model accumulation.
"""

from __future__ import annotations

import asyncio
import types
from unittest.mock import AsyncMock

import pytest

from familiar_agent.agent import EmbodiedAgent
from familiar_neighbor.embodied_hook import _should_auto_tom


def _policy(should_use_tom: bool):
    return types.SimpleNamespace(should_use_tom=should_use_tom)


class TestShouldAutoTom:
    def test_fires_when_flagged_normal_turn(self):
        assert _should_auto_tom(
            _policy(True), brief_reply_turn=False, is_desire_turn=False, user_input="つらいわ"
        )

    def test_skips_when_not_flagged(self):
        assert not _should_auto_tom(
            _policy(False), brief_reply_turn=False, is_desire_turn=False, user_input="つらいわ"
        )

    def test_skips_brief_reply_turn(self):
        assert not _should_auto_tom(
            _policy(True), brief_reply_turn=True, is_desire_turn=False, user_input="つらいわ"
        )

    def test_skips_desire_turn(self):
        assert not _should_auto_tom(
            _policy(True), brief_reply_turn=False, is_desire_turn=True, user_input=""
        )

    def test_skips_empty_input(self):
        assert not _should_auto_tom(
            _policy(True), brief_reply_turn=False, is_desire_turn=False, user_input="  "
        )


def _agent_stub(tom_tool):
    return types.SimpleNamespace(_tom_tool=tom_tool)


class TestRunAutoTom:
    @pytest.mark.asyncio
    async def test_returns_tool_output(self):
        tom = types.SimpleNamespace(call=AsyncMock(return_value=("# ToM: analysis", None)))
        out = await EmbodiedAgent._run_auto_tom(_agent_stub(tom), "しんどいわ")
        assert "analysis" in out
        situation = tom.call.await_args.args[1]["situation"]
        assert "しんどいわ" in situation

    @pytest.mark.asyncio
    async def test_empty_when_tool_missing(self):
        out = await EmbodiedAgent._run_auto_tom(types.SimpleNamespace(_tom_tool=None), "x")
        assert out == ""

    @pytest.mark.asyncio
    async def test_empty_when_tool_raises(self):
        tom = types.SimpleNamespace(call=AsyncMock(side_effect=RuntimeError("backend down")))
        out = await EmbodiedAgent._run_auto_tom(_agent_stub(tom), "x")
        assert out == ""

    @pytest.mark.asyncio
    async def test_empty_on_timeout(self):
        async def _slow(name, payload):
            await asyncio.sleep(5)
            return "late", None

        tom = types.SimpleNamespace(call=_slow)
        out = await EmbodiedAgent._run_auto_tom(_agent_stub(tom), "x", timeout=0.05)
        assert out == ""

    @pytest.mark.asyncio
    async def test_long_situation_is_truncated(self):
        tom = types.SimpleNamespace(call=AsyncMock(return_value=("ok", None)))
        await EmbodiedAgent._run_auto_tom(_agent_stub(tom), "あ" * 2000)
        situation = tom.call.await_args.args[1]["situation"]
        assert len(situation) <= 600

    @pytest.mark.asyncio
    async def test_long_output_is_trimmed(self):
        tom = types.SimpleNamespace(call=AsyncMock(return_value=("x" * 5000, None)))
        out = await EmbodiedAgent._run_auto_tom(_agent_stub(tom), "y")
        assert len(out) <= 1300


class TestAutoTomCooldown:
    def test_same_act_within_cooldown_blocked(self):
        assert not _should_auto_tom(
            types.SimpleNamespace(should_use_tom=True, primary_act="venting"),
            brief_reply_turn=False,
            is_desire_turn=False,
            user_input="まだむかつくわ",
            turns_since_last=1,
            last_act="venting",
        )

    def test_act_change_bypasses_cooldown(self):
        assert _should_auto_tom(
            types.SimpleNamespace(should_use_tom=True, primary_act="grief_signal"),
            brief_reply_turn=False,
            is_desire_turn=False,
            user_input="ほんまは悲しいんよ",
            turns_since_last=1,
            last_act="venting",
        )

    def test_cooldown_expires_after_enough_turns(self):
        assert _should_auto_tom(
            types.SimpleNamespace(should_use_tom=True, primary_act="venting"),
            brief_reply_turn=False,
            is_desire_turn=False,
            user_input="まだむかつくわ",
            turns_since_last=3,
            last_act="venting",
        )

    def test_no_history_fires(self):
        assert _should_auto_tom(
            types.SimpleNamespace(should_use_tom=True, primary_act="venting"),
            brief_reply_turn=False,
            is_desire_turn=False,
            user_input="むかつく",
            turns_since_last=None,
            last_act=None,
        )
