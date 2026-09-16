"""ADR 0004: LLM fallback for speech-act classification.

The regex layer stays the deterministic fast path. An LLM hint applies in
exactly two zones — pattern fallthrough and the {delight, distress, repair,
boundary} conflict zone — and is ignored everywhere else, so existing
decisions stay byte-stable when no hint is supplied.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from familiar_neighbor.embodied_hook import _classify_speech_act_llm
from familiar_neighbor.mind.interoception import InteroceptivePressure
from familiar_neighbor.mind.mental_state import AffectiveState
from familiar_neighbor.mind.social_policy import (
    SPEECH_ACT_VOCABULARY,
    SocialPolicyEngine,
    assess_classification,
)


def _affect(**kwargs) -> AffectiveState:
    defaults = dict(
        valence=0.0,
        arousal=0.3,
        dominance=0.0,
        attachment_pull=0.3,
        tenderness=0.3,
        threat=0.1,
        uncertainty=0.2,
        frustration=0.1,
        loneliness=0.2,
        summary="",
    )
    defaults.update(kwargs)
    return AffectiveState(**defaults)


def _intero() -> InteroceptivePressure:
    return InteroceptivePressure(
        need_rest=0.2,
        caution=0.3,
        expressivity=0.4,
        social_receptivity=0.6,
        frustration_bias=0.2,
        quiet_mode=False,
    )


def _decide(text: str, *, hint: str | None = None, **kwargs):
    engine = SocialPolicyEngine()
    params = dict(
        user_text=text,
        affect=_affect(),
        trust=0.6,
        intimacy=0.6,
        interoception=_intero(),
    )
    params.update(kwargs)
    return engine.decide(llm_act_hint=hint, **params)


# ── assess_classification ──


def test_pure_delight_is_not_a_conflict():
    a = assess_classification("やったー！ついに完成したで！")
    assert a.conflict_groups == ()
    assert not a.is_pattern_fallthrough


def test_mixed_delight_and_distress_is_a_conflict():
    a = assess_classification("最悪や、最高の誕生日になるはずやったのに")
    assert "delight" in a.conflict_groups
    assert "distress" in a.conflict_groups
    assert a.wants_llm


def test_neutral_substantive_text_is_fallthrough():
    a = assess_classification("今日は新しいカメラの設定をいじっててん")
    assert a.is_pattern_fallthrough
    assert a.wants_llm


def test_greeting_is_neither():
    a = assess_classification("おはよう")
    assert not a.is_pattern_fallthrough
    assert a.conflict_groups == ()
    assert not a.wants_llm


def test_empty_text_is_not_fallthrough():
    a = assess_classification("   ")
    assert not a.is_pattern_fallthrough
    assert not a.wants_llm


# ── decide() with llm_act_hint ──


def test_fallthrough_hint_adopts_act():
    text = "今日は新しいカメラの設定をいじっててん"
    without = _decide(text)
    assert without.primary_act == "bid_for_connection"  # trailing default
    with_hint = _decide(text, hint="venting")
    assert with_hint.primary_act == "venting"
    assert with_hint.response_mode == "validate"


def test_fallthrough_hint_matches_pattern_branch_shape():
    """A hinted act must produce the same decision shape as the pattern branch."""
    hinted = _decide("今日は新しいカメラの設定をいじっててん", hint="grief_signal")
    patterned = _decide("じいちゃんが亡くなってん")
    assert patterned.primary_act == "grief_signal"
    assert hinted.response_mode == patterned.response_mode
    assert hinted.softness == patterned.softness
    assert hinted.should_use_tom == patterned.should_use_tom


def test_invalid_hint_keeps_default():
    text = "今日は新しいカメラの設定をいじっててん"
    assert _decide(text, hint="not_a_real_act").primary_act == "bid_for_connection"


def test_hint_ignored_when_unique_pattern_matched():
    decision = _decide("おはよう", hint="venting")
    assert decision.primary_act == "greeting"


def test_conflict_hint_arbitrates():
    text = "最悪や、最高の誕生日になるはずやったのに"
    baseline = _decide(text)
    assert baseline.primary_act in {"venting", "grief_signal"}  # distress wins today
    hinted = _decide(text, hint="delight_share")
    assert hinted.primary_act == "delight_share"


def test_conflict_hint_outside_conflict_set_ignored():
    text = "最悪や、最高の誕生日になるはずやったのに"
    hinted = _decide(text, hint="playful_probe")
    assert hinted.primary_act in {"venting", "grief_signal"}


def test_previous_response_hurt_beats_conflict_hint():
    text = "最悪や、最高の誕生日になるはずやったのに"
    hinted = _decide(text, hint="delight_share", previous_response_hurt=True)
    assert hinted.primary_act == "repair_attempt"


def test_delight_hint_cannot_override_negation_veto():
    """The hint arbitrates branch order, never the deterministic guards —
    a negated positive must not celebrate, whatever the LLM says."""
    text = "うれしくない、最悪や。ほんま今日はついてへんわ"
    hinted = _decide(text, hint="delight_share")
    assert hinted.primary_act != "delight_share"


def test_delight_hint_blocked_by_negative_valence():
    text = "最悪や、最高の誕生日になるはずやったのに"
    hinted = _decide(text, hint="delight_share", affect=_affect(valence=-0.6))
    assert hinted.primary_act != "delight_share"


def test_correction_is_neither_fallthrough_nor_conflict():
    a = assess_classification("いや、そうじゃなくて")
    assert not a.is_pattern_fallthrough
    assert a.conflict_groups == ()


def test_no_hint_is_byte_stable():
    """Default-None hint must leave historical decisions untouched."""
    for text in ("おはよう", "むかつくわ、ほんまに最悪な一日や", "明日どうしたらええと思う？"):
        assert _decide(text) == _decide(text, hint=None)


# ── _classify_speech_act_llm ──


def _agent_with_utility(reply):
    if isinstance(reply, Exception):
        complete = AsyncMock(side_effect=reply)
    else:
        complete = AsyncMock(return_value=reply)
    return SimpleNamespace(_utility_backend=SimpleNamespace(complete=complete))


@pytest.mark.asyncio
async def test_classify_returns_vocabulary_act():
    agent = _agent_with_utility("venting")
    assert await _classify_speech_act_llm(agent, "なんか色々あってな…") == "venting"


@pytest.mark.asyncio
async def test_classify_normalizes_quotes_and_case():
    agent = _agent_with_utility('  "Grief_Signal" ')
    assert await _classify_speech_act_llm(agent, "x") == "grief_signal"


@pytest.mark.asyncio
async def test_classify_rejects_out_of_vocabulary():
    agent = _agent_with_utility("I think this is venting because...")
    assert await _classify_speech_act_llm(agent, "x") is None


@pytest.mark.asyncio
async def test_classify_backend_failure_returns_none():
    agent = _agent_with_utility(RuntimeError("down"))
    assert await _classify_speech_act_llm(agent, "x") is None


@pytest.mark.asyncio
async def test_classify_timeout_returns_none():
    async def _slow(*args, **kwargs):
        await asyncio.sleep(5)
        return "venting"

    agent = SimpleNamespace(_utility_backend=SimpleNamespace(complete=_slow))
    assert await _classify_speech_act_llm(agent, "x", timeout_s=0.01) is None


def test_vocabulary_covers_all_engine_acts():
    assert {
        "repair_attempt",
        "boundary_assertion",
        "delight_share",
        "grief_signal",
        "venting",
        "fatigue_signal",
        "request_for_action",
        "request_for_advice",
        "meta_conversation",
        "playful_probe",
        "bid_for_connection",
        "greeting",
        "acknowledgement",
        "clarification",
        "conflict_signal",
    } <= SPEECH_ACT_VOCABULARY
