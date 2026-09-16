"""Reality gate: a perception claim without looking earns one honest re-ask.

Waking is maintained reality-testing — a reply that claims present-tense
perception on a turn that never called see() is generation outrunning error
correction. The gate (FAMILIAR_REALITY_GATE, default off) injects one
[REALITY] re-ask: call see() now, or reframe as memory/uncertainty. It rides
the same RetryDecision path as the identity and voice gates, runs between
them, and never fires on desire/brief turns, grounded turns, camera-less tool
surfaces, or memory-framed sentences.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_agent.backend import ToolCall
from familiar_neighbor.mind.reality import (
    GroundingTracker,
    Provenance,
    looks_like_fresh_perception_claim,
    provenance_of_coalition,
    provenance_of_memory_kind,
)

from tests.test_agent_react_loop import _make_agent, _patch_heavy, _turn


# ── Pattern library ──


@pytest.mark.parametrize(
    "text",
    [
        "I can see a red car outside the window.",
        "I see two people down on the street.",
        "I'm looking at the street below.",
        "I can see the delivery truck right now.",
        "窓の外に猫が見えます。",
        "今、見えているのは夕焼けです。",
        "部屋の奥にコウタが見えていますよ。",
        "ベランダから通りが見えます。",
    ],
)
def test_claim_patterns_positive(text):
    assert looks_like_fresh_perception_claim(text)


@pytest.mark.parametrize(
    "text",
    [
        "",
        "Good morning! How did you sleep?",
        # Memory / past framing
        "I remember I could see the park from there.",
        "Yesterday I saw a beautiful sunset.",
        "昨日、綺麗な夕焼けが窓から見えました。",
        "さっき窓の外に猫が見えた。",
        "この前見えた景色を覚えていますよ。",
        "思い出しました、あの窓から海が見えます。",
        # Uncertainty hedges (present AND past)
        "窓から海が見えた気がする。",
        "外に誰かが見える気がする。",
        "窓の外に見えるかもね。",
        # Negation
        "窓の外には何も見えない。",
        "外はカメラでは見えません。",
        "未来が見えるわけじゃない。",
        # Discourse markers / idioms / metaphors (reviewer-verified false positives)
        "I see, that makes sense.",
        "Oh, I see what you mean.",
        "I can see why you would think that.",
        "As far as I can see, the plan is fine.",
        "I'm looking forward to the weekend.",
        "I am watching the situation closely.",
        "I can see why the camera setup is confusing.",
        "I see a problem with this approach.",
        "やっと解決策が見える。",
        "希望が見えるよ。",
        "目の前にチャンスがある。",
        "この部屋の可能性が見えてきますね。",
        # Anchor-less claims — accepted false negatives (safe direction)
        "目の前に大きなトラックがあります。",
        "There is a big truck in front of me.",
        "The sea is visible from Tokyo Tower on clear days.",
    ],
)
def test_claim_patterns_negative(text):
    assert not looks_like_fresh_perception_claim(text)


def test_claim_check_caps_input_length():
    # A claim buried beyond the cap is not scanned — bounded work, ReDoS-safe.
    text = ("a" * 3000) + " I can see it."
    assert not looks_like_fresh_perception_claim(text)


# ── Provenance mappers ──


def test_provenance_of_coalition():
    assert provenance_of_coalition("scene") is Provenance.PERCEIVED
    assert provenance_of_coalition("memory") is Provenance.RECALLED
    assert provenance_of_coalition("default_mode") is Provenance.RECALLED
    assert provenance_of_coalition("monologue") is Provenance.GENERATED
    assert provenance_of_coalition("unknown_source") is Provenance.GENERATED


def test_provenance_of_memory_kind():
    assert provenance_of_memory_kind("observation") is Provenance.PERCEIVED
    assert provenance_of_memory_kind("dream") is Provenance.GENERATED
    assert provenance_of_memory_kind("conversation") is Provenance.RECALLED


# ── GroundingTracker ──


def test_grounding_tracker_ratio_and_recency():
    t = GroundingTracker(window=4)
    assert t.ratio() == 1.0  # benefit of the doubt before any turn
    t.note_turn(True)
    t.note_turn(False)
    t.note_turn(False)
    assert t.ratio() == pytest.approx(1 / 3)
    assert t.turns_since_grounded() == 2
    t.note_turn(True)
    assert t.turns_since_grounded() == 0
    # Window slides: the first True falls out, leaving F,F,T,F.
    t.note_turn(False)
    assert t.ratio() == pytest.approx(1 / 4)


# ── Gate behavior (mocked stream_turn, real loop) ──

_CLAIM_INPUT = "外の様子どうなってるかな、いま何が見えてる？"
_CLAIM_REPLY = "窓の外に赤い車が見えますよ。"


def _gate_agent(**kwargs):
    kwargs.setdefault("with_camera", True)
    agent = _make_agent(**kwargs)
    agent.config.reality_gate = True
    agent.config.voice_gate = False
    agent.config.auto_say = False
    return agent


async def _run(agent, text=_CLAIM_INPUT):
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        return await agent.run(text)
    finally:
        for p in ps:
            p.stop()


def _reality_injections(agent) -> list[str]:
    return [
        m["content"]
        for m in agent.messages
        if isinstance(m, dict)
        and m.get("role") == "user"
        and isinstance(m.get("content"), str)
        and m["content"].startswith("[REALITY]")
    ]


@pytest.mark.asyncio
async def test_claim_without_look_gets_one_retry_then_honest_reply():
    agent = _gate_agent()
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("end_turn", text=_CLAIM_REPLY), None),
            (_turn("end_turn", text="いま確認できていないので、確かなことは言えません。"), None),
        ]
    )
    result = await _run(agent)
    assert result == "いま確認できていないので、確かなことは言えません。"
    assert len(_reality_injections(agent)) == 1


@pytest.mark.asyncio
async def test_gate_fires_at_most_once_per_turn():
    agent = _gate_agent()
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("end_turn", text=_CLAIM_REPLY), None),
            (_turn("end_turn", text=_CLAIM_REPLY), None),
        ]
    )
    result = await _run(agent)
    assert result == _CLAIM_REPLY  # still-claiming second reply ships (once-latch)
    assert len(_reality_injections(agent)) == 1


@pytest.mark.asyncio
async def test_no_gate_when_flag_off():
    agent = _make_agent(with_camera=True)
    agent.config.reality_gate = False
    agent.config.voice_gate = False
    agent.config.auto_say = False
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text=_CLAIM_REPLY), None))
    result = await _run(agent)
    assert result == _CLAIM_REPLY
    assert _reality_injections(agent) == []


@pytest.mark.asyncio
async def test_no_gate_when_camera_used_this_turn():
    agent = _gate_agent()
    see_call = ToolCall(id="c1", name="see", input={})
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("tool_use", tool_calls=[see_call]), None),
            (_turn("end_turn", text=_CLAIM_REPLY), None),
        ]
    )
    result = await _run(agent)
    assert result == _CLAIM_REPLY
    assert _reality_injections(agent) == []


@pytest.mark.asyncio
async def test_failed_see_does_not_exempt_gate():
    """A see() that errored must not license perception claims — the gate
    keys on see_succeeded, not on the attempt."""
    agent = _gate_agent()
    agent._camera.call = AsyncMock(side_effect=RuntimeError("camera offline"))
    see_call = ToolCall(id="c1", name="see", input={})
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("tool_use", tool_calls=[see_call]), None),
            (_turn("end_turn", text=_CLAIM_REPLY), None),
            (_turn("end_turn", text="カメラが使えないので、確認できませんでした。"), None),
        ]
    )
    result = await _run(agent)
    assert result == "カメラが使えないので、確認できませんでした。"
    assert len(_reality_injections(agent)) == 1


@pytest.mark.asyncio
async def test_desire_turn_not_recorded_in_grounding():
    """Self-initiated reflection turns are not reality-testing-relevant —
    they must neither raise nor sink the grounding ratio."""
    from familiar_neighbor.mind.reality import GroundingTracker as _GT

    agent = _gate_agent()
    agent._grounding = _GT()
    agent.backend.stream_turn = AsyncMock(
        return_value=(_turn("end_turn", text="静かな時間に少し考えごとをしていた。"), None)
    )
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("", inner_voice="内省の時間")
    finally:
        for p in ps:
            p.stop()
    assert not agent._grounding._turns  # nothing recorded


@pytest.mark.asyncio
async def test_no_gate_without_see_tool_on_surface():
    agent = _gate_agent(with_camera=False)  # no see tool registered
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text=_CLAIM_REPLY), None))
    result = await _run(agent)
    assert result == _CLAIM_REPLY
    assert _reality_injections(agent) == []


@pytest.mark.asyncio
async def test_no_gate_on_non_claim_reply():
    agent = _gate_agent()
    agent.backend.stream_turn = AsyncMock(
        return_value=(_turn("end_turn", text="今日も一日おつかれさま。"), None)
    )
    await _run(agent)
    assert _reality_injections(agent) == []


@pytest.mark.asyncio
async def test_no_gate_on_desire_turn():
    agent = _gate_agent()
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text=_CLAIM_REPLY), None))
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("", inner_voice="外を見たい気持ちが高まっている")
    finally:
        for p in ps:
            p.stop()
    assert _reality_injections(agent) == []


@pytest.mark.asyncio
async def test_identity_gate_takes_precedence():
    """A draft violating identity AND claiming perception gets [IDENTITY] first."""
    agent = _gate_agent()
    violation = MagicMock()
    violation.severity = 1.0
    violation.statement = "I never fake perception"
    identity = MagicMock()
    identity.check_response = MagicMock(side_effect=[[violation], []])
    identity.assess = MagicMock(return_value=None)
    agent._identity = identity
    agent.backend.stream_turn = AsyncMock(
        side_effect=[
            (_turn("end_turn", text=_CLAIM_REPLY), None),
            (_turn("end_turn", text="確認できていないので分かりません。"), None),
        ]
    )
    await _run(agent)
    injected = [
        m["content"]
        for m in agent.messages
        if isinstance(m, dict)
        and m.get("role") == "user"
        and isinstance(m.get("content"), str)
        and m["content"].startswith(("[IDENTITY]", "[REALITY]"))
    ]
    assert injected and injected[0].startswith("[IDENTITY]")


# ── Config + profile wiring ──


def test_config_off_by_default(monkeypatch):
    monkeypatch.delenv("FAMILIAR_REALITY_GATE", raising=False)
    from familiar_agent.config import AgentConfig

    assert AgentConfig().reality_gate is False


def test_config_env_enables(monkeypatch):
    monkeypatch.setenv("FAMILIAR_REALITY_GATE", "1")
    from familiar_agent.config import AgentConfig

    assert AgentConfig().reality_gate is True


@pytest.mark.asyncio
async def test_grounding_feeds_consciousness_profile():
    """An agent that never looks scores lower reality_testing than one that does."""
    agent = _make_agent()
    agent.config.consciousness_profile = True
    tracker = GroundingTracker()
    for _ in range(5):
        tracker.note_turn(False)
    agent._grounding = tracker
    low = agent._update_consciousness_profile(origin="turn")

    grounded = GroundingTracker()
    for _ in range(5):
        grounded.note_turn(True)
    agent._grounding = grounded
    high = agent._update_consciousness_profile(origin="turn")

    assert high.reality_testing > low.reality_testing
