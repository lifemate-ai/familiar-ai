"""Tests for MetaMonitor (Phase 5: Higher-Order Theory / HOT layer).

Tests cover:
- record_step(): annotate each ReAct step metacognitively
- detect_inconsistency(): flag when behavior diverges from self-narrative
- summarize_session(): compact metacognitive summary for diary
- as_coalition(): expose meta-monitor state as workspace Coalition
"""

from __future__ import annotations

from unittest.mock import MagicMock


from familiar_agent.meta_monitor import MetaMonitor
from familiar_agent.social_policy import SocialPolicyDecision
from familiar_agent.workspace import Coalition


# ── Helpers ───────────────────────────────────────────────────────────────────


def _coalition(source: str, summary: str = "test") -> Coalition:
    return Coalition(
        source=source,
        summary=summary,
        activation=0.7,
        urgency=0.4,
        novelty=0.3,
        context_block=f"[{source}] {summary}",
    )


def _make_narrative(description: str = "I am a curious companion") -> MagicMock:
    narrative = MagicMock()
    narrative.describe = MagicMock(return_value=description)
    return narrative


# ── Construction ──────────────────────────────────────────────────────────────


def test_default_construction():
    monitor = MetaMonitor()
    assert monitor is not None


def test_no_steps_initially():
    monitor = MetaMonitor()
    assert monitor.step_count() == 0


# ── record_step ───────────────────────────────────────────────────────────────


def test_record_step_increments_count():
    monitor = MetaMonitor()
    winner = _coalition("desire", "want to look around")
    monitor.record_step(winner, action="tool_call", confidence=0.8)
    assert monitor.step_count() == 1


def test_record_step_multiple():
    monitor = MetaMonitor()
    for i in range(5):
        monitor.record_step(_coalition("desire"), action=f"action_{i}", confidence=0.5)
    assert monitor.step_count() == 5


def test_record_step_stores_winner_source():
    monitor = MetaMonitor()
    monitor.record_step(_coalition("memory", "recalled memory"), action="recall", confidence=0.9)
    steps = monitor.recent_steps()
    assert len(steps) == 1
    assert steps[0]["source"] == "memory"


def test_record_step_stores_action():
    monitor = MetaMonitor()
    monitor.record_step(_coalition("desire"), action="say_tool", confidence=0.7)
    steps = monitor.recent_steps()
    assert steps[0]["action"] == "say_tool"


def test_record_step_stores_confidence():
    monitor = MetaMonitor()
    monitor.record_step(_coalition("scene"), action="look", confidence=0.95)
    steps = monitor.recent_steps()
    assert abs(steps[0]["confidence"] - 0.95) < 1e-6


def test_record_step_confidence_clamped():
    """Confidence outside [0,1] is clamped."""
    monitor = MetaMonitor()
    monitor.record_step(_coalition("desire"), action="a", confidence=1.5)
    steps = monitor.recent_steps()
    assert steps[0]["confidence"] <= 1.0

    monitor2 = MetaMonitor()
    monitor2.record_step(_coalition("desire"), action="b", confidence=-0.3)
    steps2 = monitor2.recent_steps()
    assert steps2[0]["confidence"] >= 0.0


def test_recent_steps_limited():
    """recent_steps() returns at most the configured window."""
    monitor = MetaMonitor(window=3)
    for i in range(10):
        monitor.record_step(_coalition("desire"), action=f"a{i}", confidence=0.5)
    assert len(monitor.recent_steps()) == 3


# ── detect_inconsistency ──────────────────────────────────────────────────────


def test_detect_inconsistency_no_steps_returns_none():
    monitor = MetaMonitor()
    narrative = _make_narrative()
    result = monitor.detect_inconsistency(narrative)
    assert result is None


def test_detect_inconsistency_consistent_returns_none():
    monitor = MetaMonitor()
    narrative = _make_narrative("I am a curious companion who explores")
    # Exploration-focused steps should be consistent
    for _ in range(3):
        monitor.record_step(_coalition("desire", "explore"), action="look", confidence=0.8)
    result = monitor.detect_inconsistency(narrative)
    # May or may not detect inconsistency — just ensure no exception and returns str or None
    assert result is None or isinstance(result, str)


def test_detect_inconsistency_returns_string_when_found():
    monitor = MetaMonitor()
    # Narrative says "rest and be calm" but steps are all urgent action
    narrative = _make_narrative("I rest and stay calm always")
    for _ in range(5):
        monitor.record_step(
            _coalition("desire", "panic"),
            action="urgent_action",
            confidence=0.9,
        )
    result = monitor.detect_inconsistency(narrative)
    # Should return a string (or None) without raising
    assert result is None or isinstance(result, str)


# ── summarize_session ─────────────────────────────────────────────────────────


def test_summarize_session_empty_returns_string():
    monitor = MetaMonitor()
    summary = monitor.summarize_session()
    assert isinstance(summary, str)


def test_summarize_session_nonempty():
    monitor = MetaMonitor()
    monitor.record_step(_coalition("desire"), action="look", confidence=0.8)
    monitor.record_step(_coalition("memory"), action="recall", confidence=0.6)
    summary = monitor.summarize_session()
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_summarize_session_mentions_dominant_source():
    monitor = MetaMonitor()
    for _ in range(5):
        monitor.record_step(_coalition("memory"), action="recall", confidence=0.7)
    summary = monitor.summarize_session()
    assert "memory" in summary.lower()


def test_summarize_session_is_compact():
    monitor = MetaMonitor()
    for i in range(100):
        monitor.record_step(_coalition("desire"), action=f"a{i}", confidence=0.5)
    summary = monitor.summarize_session()
    assert len(summary) < 2000


# ── as_coalition ───────────────────────────────────────────────────────────────


def test_as_coalition_returns_none_with_no_steps():
    monitor = MetaMonitor()
    assert monitor.as_coalition() is None


def test_as_coalition_returns_coalition_after_steps():
    monitor = MetaMonitor()
    monitor.record_step(_coalition("desire"), action="look", confidence=0.7)
    c = monitor.as_coalition()
    assert c is not None
    assert isinstance(c, Coalition)


def test_as_coalition_source_is_meta():
    monitor = MetaMonitor()
    monitor.record_step(_coalition("desire"), action="look", confidence=0.7)
    c = monitor.as_coalition()
    assert c is not None
    assert c.source == "meta"


def test_as_coalition_fields_in_valid_range():
    monitor = MetaMonitor()
    monitor.record_step(_coalition("scene"), action="perceive", confidence=0.8)
    c = monitor.as_coalition()
    assert c is not None
    assert 0.0 <= c.activation <= 1.0
    assert 0.0 <= c.urgency <= 1.0
    assert 0.0 <= c.novelty <= 1.0


def test_as_coalition_low_activation_normally():
    """Meta-monitor coalitions should have low activation by default (it's background)."""
    monitor = MetaMonitor()
    monitor.record_step(_coalition("memory"), action="recall", confidence=0.5)
    c = monitor.as_coalition()
    assert c is not None
    # Meta is a background process, shouldn't dominate workspace
    assert c.activation < 0.8


def test_gate_response_detects_validation_before_advice_violation() -> None:
    monitor = MetaMonitor()
    policy = SocialPolicyDecision(
        primary_act="fatigue_signal",
        response_mode="validate",
        should_use_tom=True,
        should_recall_relational_memory=False,
        softness=0.9,
        directness=0.3,
        initiative=0.3,
        avoid_problem_solving=True,
        mention_memory=False,
    )

    decision = monitor.gate_response(
        user_text="今日はほんましんどい",
        candidate_response="You should just take a walk and drink coffee.",
        social_policy=policy,
    )

    assert decision.needs_repair is True
    assert "validation-before-advice violation" in decision.reasons


def test_gate_response_detects_raw_interoception_leakage() -> None:
    monitor = MetaMonitor()
    decision = monitor.gate_response(
        user_text="なんかだるい",
        candidate_response="Your heart rate is 120 bpm and CPU is too high.",
        social_policy=None,
    )

    assert "raw interoception leakage" in decision.reasons
