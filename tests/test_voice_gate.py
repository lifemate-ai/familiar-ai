"""Voice gate: a silent conversational reply earns one say() re-ask.

Small local models write text but forget to call say(). auto_say would pipe
the whole reply — stage directions and all — into TTS; the voice gate instead
re-asks once so the model itself composes the short line to speak aloud,
keeping say() as the deliberate voice channel. Off by default
(FAMILIAR_VOICE_GATE); well-behaved models never trip it.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from familiar_agent.backend import ToolCall

from tests.test_agent_react_loop import _make_agent, _patch_heavy, _turn


def _user_texts(agent) -> list[str]:
    return [
        m["content"]
        for m in agent.messages
        if isinstance(m, dict) and m.get("role") == "user" and isinstance(m.get("content"), str)
    ]


def _voice_injections(agent) -> list[str]:
    return [t for t in _user_texts(agent) if t.startswith("[VOICE]")]


def _gate_agent(**kwargs):
    agent = _make_agent(with_tts=True, **kwargs)
    agent.config.voice_gate = True
    agent.config.auto_say = False
    return agent


# Long enough to dodge the brief-turn classifier (greetings are exempt by design).
_CHATTY_INPUT = "今日は新しいカメラの設定をいじっていたんだけど、なかなか難しくてね"


@pytest.mark.asyncio
async def test_silent_reply_gets_one_voice_retry_then_speaks():
    agent = _gate_agent()
    say_call = ToolCall(id="s1", name="say", input={"text": "おつかれさま。"})
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("end_turn", text="（微笑みながら）大変だったね。"), None),
            (_turn("tool_use", tool_calls=[say_call]), None),
            (_turn("end_turn", text="大変だったね。"), None),
        ]
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run(_CHATTY_INPUT)
    finally:
        for p in ps:
            p.stop()

    assert result == "大変だったね。"
    assert len(_voice_injections(agent)) == 1
    agent._tts.call.assert_awaited()  # say actually executed


@pytest.mark.asyncio
async def test_gate_fires_at_most_once_per_turn():
    """A model that stays silent even after the re-ask is not retried again."""
    agent = _gate_agent()
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("end_turn", text="silent one"), None),
            (_turn("end_turn", text="still silent"), None),
        ]
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run(_CHATTY_INPUT)
    finally:
        for p in ps:
            p.stop()

    assert result == "still silent"
    assert len(_voice_injections(agent)) == 1


@pytest.mark.asyncio
async def test_no_gate_when_flag_off():
    agent = _make_agent(with_tts=True)
    agent.config.voice_gate = False
    agent.config.auto_say = False
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="quiet"), None))

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run(_CHATTY_INPUT)
    finally:
        for p in ps:
            p.stop()

    assert result == "quiet"
    assert _voice_injections(agent) == []


@pytest.mark.asyncio
async def test_no_gate_without_tts():
    agent = _make_agent(with_tts=False)
    agent.config.voice_gate = True
    agent.config.auto_say = False
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="quiet"), None))

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run(_CHATTY_INPUT)
    finally:
        for p in ps:
            p.stop()

    assert _voice_injections(agent) == []


@pytest.mark.asyncio
async def test_no_gate_when_say_already_used():
    agent = _gate_agent()
    say_call = ToolCall(id="s1", name="say", input={"text": "きこえてる？"})
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("tool_use", tool_calls=[say_call]), None),
            (_turn("end_turn", text="どうかな。"), None),
        ]
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        result = await agent.run(_CHATTY_INPUT)
    finally:
        for p in ps:
            p.stop()

    assert result == "どうかな。"
    assert _voice_injections(agent) == []


@pytest.mark.asyncio
async def test_no_gate_on_desire_turn():
    """Private self-initiated turns (e.g. reflection) must not be forced to speak."""
    agent = _gate_agent()
    agent.backend.stream_turn = AsyncMock(
        return_value=(_turn("end_turn", text="内面の独白のようなもの"), None)
    )

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("", inner_voice="内なる衝動")
    finally:
        for p in ps:
            p.stop()

    assert _voice_injections(agent) == []


@pytest.mark.asyncio
async def test_no_gate_on_brief_turn():
    """Greetings ride the brief say-first path (2-iteration cap) — exempt."""
    agent = _gate_agent()
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="おはよう。"), None))

    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("おはよう")
    finally:
        for p in ps:
            p.stop()

    assert _voice_injections(agent) == []


def test_voice_gate_off_by_default(monkeypatch):
    monkeypatch.delenv("FAMILIAR_VOICE_GATE", raising=False)
    from familiar_agent.config import AgentConfig

    assert AgentConfig().voice_gate is False


def test_voice_gate_env_enables(monkeypatch):
    monkeypatch.setenv("FAMILIAR_VOICE_GATE", "1")
    from familiar_agent.config import AgentConfig

    assert AgentConfig().voice_gate is True
