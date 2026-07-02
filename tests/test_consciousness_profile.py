"""Consciousness profile: a multidimensional, instrumentation-only reading.

Consciousness is not a Bool — the profile renders six graded dimensions
(wakefulness, access, self-model integrity, integration, reality testing,
reportability) from signals the mind layers already produce. Strictly
observability: the numbers surface in diagnostics and mental_state.jsonl,
never in the agent's own prompt or replies. Off by default
(FAMILIAR_CONSCIOUSNESS_PROFILE); dormant = byte-identical jsonl.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from familiar_neighbor.mind.consciousness import (
    ConsciousnessProfile,
    ProfileInputs,
    compute_consciousness_profile,
)
from familiar_neighbor.mind.mental_state import ConsciousnessState

from tests.test_agent_react_loop import _make_agent, _patch_heavy, _turn


# ── ConsciousnessState: snapshot carrier + jsonl byte-compat ──


def test_state_default_is_dormant():
    assert ConsciousnessState().is_default()
    assert not ConsciousnessState(wakefulness=0.5, origin="turn").is_default()


def test_state_sanitizes_out_of_range():
    state = ConsciousnessState(wakefulness=1.7, access=-0.3, origin="x" * 50)
    clean = state.sanitized()
    assert clean.wakefulness == 1.0
    assert clean.access == 0.0
    assert len(clean.origin) <= 16


def _snapshot(consciousness: ConsciousnessState | None = None):
    from familiar_neighbor.mind.mental_state import (
        AffectiveState,
        DriveVector,
        InteroceptiveSignal,
        MentalStateSnapshot,
        SocialState,
    )

    kwargs = {}
    if consciousness is not None:
        kwargs["consciousness"] = consciousness
    return MentalStateSnapshot(
        turn_index=1,
        created_at="2026-07-03T00:00:00",
        interoception=InteroceptiveSignal(),
        affect=AffectiveState(),
        social=SocialState(),
        drives=DriveVector(),
        **kwargs,
    )


def test_jsonl_key_dropped_when_dormant():
    data = _snapshot().to_json_dict()
    assert "consciousness" not in data
    # Old lines (no consciousness key) still round-trip.
    from familiar_neighbor.mind.mental_state import MentalStateSnapshot

    restored = MentalStateSnapshot.from_json_dict(json.loads(json.dumps(data)))
    assert restored.consciousness.is_default()


def test_jsonl_key_present_and_round_trips_when_active():
    active = ConsciousnessState(wakefulness=0.7, access=0.5, origin="turn")
    data = _snapshot(active).to_json_dict()
    assert data["consciousness"]["wakefulness"] == 0.7
    from familiar_neighbor.mind.mental_state import MentalStateSnapshot

    restored = MentalStateSnapshot.from_json_dict(data)
    assert restored.consciousness.origin == "turn"


def test_prompt_summary_never_mentions_consciousness():
    """Instrumentation-only invariant: the profile must not reach the prompt."""
    active = ConsciousnessState(wakefulness=0.9, access=0.9, origin="turn")
    assert "consciousness" not in _snapshot(active).prompt_summary().lower()


# ── compute_consciousness_profile: deterministic bands ──


def test_default_inputs_give_mid_bands():
    p = compute_consciousness_profile(ProfileInputs())
    for value in (
        p.wakefulness,
        p.self_model_integrity,
        p.reality_testing,
        p.reportability,
    ):
        assert 0.3 <= value <= 0.9
    assert p.access <= 0.3  # nothing ignited
    assert p.origin == "turn"


def test_wakefulness_tracks_energy_and_quiet_hours():
    lively = compute_consciousness_profile(ProfileInputs(energy=0.9, arousal=0.7, fatigue=0.1))
    tired = compute_consciousness_profile(ProfileInputs(energy=0.2, arousal=0.2, fatigue=0.8))
    night = compute_consciousness_profile(
        ProfileInputs(energy=0.9, arousal=0.7, fatigue=0.1, quiet_hours=True)
    )
    assert lively.wakefulness > tired.wakefulness
    assert night.wakefulness < lively.wakefulness


def test_access_requires_ignition_and_scales_with_margin():
    idle = compute_consciousness_profile(ProfileInputs(winner_present=False, coalition_count=2))
    barely = compute_consciousness_profile(
        ProfileInputs(winner_present=True, winner_score=0.41, effective_threshold=0.4)
    )
    strong = compute_consciousness_profile(
        ProfileInputs(
            winner_present=True, winner_score=0.9, effective_threshold=0.4, coalition_count=5
        )
    )
    assert idle.access < barely.access < strong.access
    assert strong.access >= 0.8


def test_self_model_degrades_with_dissonance_and_threat():
    intact = compute_consciousness_profile(ProfileInputs(focus_stability=0.8))
    strained = compute_consciousness_profile(
        ProfileInputs(
            focus_stability=0.8,
            identity_dissonance=0.8,
            identity_threat=0.6,
            meta_inconsistency=True,
        )
    )
    assert strained.self_model_integrity < intact.self_model_integrity - 0.3


def test_integration_tracks_diversity_and_breadth():
    narrow = compute_consciousness_profile(ProfileInputs(source_diversity=0.1))
    broad = compute_consciousness_profile(
        ProfileInputs(source_diversity=0.9, peripheral_count=4, thought_streak=3)
    )
    assert broad.integration > narrow.integration + 0.3


def test_reality_testing_tracks_confidence_errors_and_grounding():
    solid = compute_consciousness_profile(ProfileInputs(sensor_confidence=0.9))
    surprised = compute_consciousness_profile(
        ProfileInputs(sensor_confidence=0.9, external_surprise=1.0, agency_error=1.0)
    )
    grounded = compute_consciousness_profile(
        ProfileInputs(sensor_confidence=0.9, grounding_ratio=1.0)
    )
    ungrounded = compute_consciousness_profile(
        ProfileInputs(sensor_confidence=0.9, grounding_ratio=0.0)
    )
    assert surprised.reality_testing < solid.reality_testing
    assert grounded.reality_testing > ungrounded.reality_testing


def test_reportability_scales_with_channels():
    mute = compute_consciousness_profile(ProfileInputs())
    full = compute_consciousness_profile(
        ProfileInputs(tts_present=True, say_recent=True, self_report_available=True)
    )
    assert full.reportability == pytest.approx(1.0)
    assert 0.3 <= mute.reportability <= 0.5  # text channel always exists


def test_profile_one_line_and_overall():
    p = compute_consciousness_profile(ProfileInputs(energy=0.8), origin="tick")
    line = p.one_line()
    assert "wake" in line and "real" in line
    assert 0.0 <= p.overall() <= 1.0
    assert p.origin == "tick"


def test_profile_as_state_round_trip():
    p = compute_consciousness_profile(ProfileInputs(energy=0.8))
    state = p.as_state()
    assert isinstance(state, ConsciousnessState)
    assert state.wakefulness == pytest.approx(p.wakefulness)
    assert state.origin == "turn"
    assert not state.is_default()


def test_compute_is_deterministic():
    a = compute_consciousness_profile(ProfileInputs(energy=0.6, arousal=0.4), created_at="t")
    b = compute_consciousness_profile(ProfileInputs(energy=0.6, arousal=0.4), created_at="t")
    assert a == b


# ── MetaMonitor.source_diversity ──


def test_meta_monitor_source_diversity():
    from familiar_neighbor.mind.meta_monitor import MetaMonitor
    from familiar_neighbor.mind.workspace import Coalition

    meta = MetaMonitor(state_path="/dev/null")
    assert meta.source_diversity() == 0.0
    for source in ("desire", "desire", "scene", "memory"):
        meta.record_step(
            Coalition(
                source=source,
                summary="s",
                activation=0.5,
                urgency=0.1,
                novelty=0.1,
                context_block="",
            ),
            action="say",
            confidence=0.5,
        )
    assert meta.source_diversity() == pytest.approx(3 / 4)


# ── Agent wiring: dormant by default, populated when enabled ──


@pytest.mark.asyncio
async def test_flag_off_keeps_profile_dormant():
    agent = _make_agent()
    agent.config.consciousness_profile = False
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="ok"), None))
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("こんにちは、今日は何してた？")
    finally:
        for p in ps:
            p.stop()
    assert getattr(agent, "_last_consciousness_profile", None) is None


@pytest.mark.asyncio
async def test_flag_on_populates_profile_and_snapshot():
    agent = _make_agent()
    agent.config.consciousness_profile = True
    agent.backend.stream_turn = AsyncMock(return_value=(_turn("end_turn", text="ok"), None))
    ps = _patch_heavy()
    for p in ps:
        p.start()
    try:
        await agent.run("こんにちは、今日は何してた？")
    finally:
        for p in ps:
            p.stop()
    profile = getattr(agent, "_last_consciousness_profile", None)
    assert isinstance(profile, ConsciousnessProfile)
    assert profile.origin == "turn"


@pytest.mark.asyncio
async def test_compete_once_records_last_result():
    agent = _make_agent()
    result = await agent._compete_once(cheap=True, desires=None)
    assert agent._last_compete_result is result


# ── Config flag ──


def test_config_off_by_default(monkeypatch):
    monkeypatch.delenv("FAMILIAR_CONSCIOUSNESS_PROFILE", raising=False)
    from familiar_agent.config import AgentConfig

    assert AgentConfig().consciousness_profile is False


def test_config_env_enables(monkeypatch):
    monkeypatch.setenv("FAMILIAR_CONSCIOUSNESS_PROFILE", "1")
    from familiar_agent.config import AgentConfig

    assert AgentConfig().consciousness_profile is True
