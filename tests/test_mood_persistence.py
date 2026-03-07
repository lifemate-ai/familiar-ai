"""Tests for mood persistence in EmbodiedAgent.

Phase 2 of companion-likeness improvements.
The agent maintains a mood state that persists across turns with exponential decay.
"""

from __future__ import annotations

import time


from familiar_agent.agent import EmbodiedAgent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_agent() -> EmbodiedAgent:
    """Create an EmbodiedAgent with mocked backend (no real API calls)."""
    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._mood = "neutral"
    agent._mood_intensity = 0.0
    agent._mood_set_at = time.time()
    return agent


# ---------------------------------------------------------------------------
# Tests: _update_mood
# ---------------------------------------------------------------------------


def test_update_mood_sets_mood_for_excited() -> None:
    agent = _mock_agent()
    agent._update_mood("excited")
    assert agent._mood == "excited"
    assert agent._mood_intensity > 0.0


def test_update_mood_sets_mood_for_moved() -> None:
    agent = _mock_agent()
    agent._update_mood("moved")
    assert agent._mood == "moved"
    assert agent._mood_intensity >= 0.8


def test_update_mood_sets_mood_for_happy() -> None:
    agent = _mock_agent()
    agent._update_mood("happy")
    assert agent._mood == "happy"
    assert agent._mood_intensity >= 0.6


def test_update_mood_sets_mood_for_curious() -> None:
    agent = _mock_agent()
    agent._update_mood("curious")
    assert agent._mood == "curious"
    assert agent._mood_intensity >= 0.6


def test_update_mood_sets_mood_for_sad() -> None:
    agent = _mock_agent()
    agent._update_mood("sad")
    assert agent._mood == "sad"
    assert agent._mood_intensity >= 0.6


def test_update_mood_neutral_does_not_overwrite() -> None:
    """Neutral emotion should not reset a pre-existing mood."""
    agent = _mock_agent()
    agent._update_mood("excited")
    prev_mood = agent._mood
    prev_intensity = agent._mood_intensity

    agent._update_mood("neutral")

    assert agent._mood == prev_mood
    assert agent._mood_intensity == prev_intensity


def test_update_mood_same_emotion_reinforces_intensity() -> None:
    agent = _mock_agent()
    agent._update_mood("happy")
    first_intensity = agent._mood_intensity

    agent._update_mood("happy")

    assert agent._mood_intensity >= first_intensity
    assert agent._mood_intensity <= 1.0


def test_update_mood_intensity_capped_at_1() -> None:
    agent = _mock_agent()
    for _ in range(20):
        agent._update_mood("excited")
    assert agent._mood_intensity <= 1.0


def test_update_mood_different_strong_emotion_replaces() -> None:
    agent = _mock_agent()
    agent._update_mood("happy")
    agent._update_mood("sad")
    assert agent._mood == "sad"


# ---------------------------------------------------------------------------
# Tests: _decayed_mood
# ---------------------------------------------------------------------------


def test_decayed_mood_fresh_returns_mood() -> None:
    agent = _mock_agent()
    agent._update_mood("excited")
    mood, intensity = agent._decayed_mood()
    assert mood == "excited"
    assert intensity > 0.0


def test_decayed_mood_neutral_when_none_set() -> None:
    agent = _mock_agent()
    mood, intensity = agent._decayed_mood()
    assert mood == "neutral"
    assert intensity == 0.0


def test_decayed_mood_returns_neutral_after_long_time() -> None:
    """After many minutes, mood should have decayed to neutral."""
    agent = _mock_agent()
    agent._update_mood("excited")
    # Simulate 30 minutes having passed
    agent._mood_set_at = time.time() - 1800
    mood, intensity = agent._decayed_mood()
    assert mood == "neutral"
    assert intensity == 0.0


def test_decayed_mood_partial_decay() -> None:
    """After ~138 seconds (one half-life), intensity should be ~half of original."""
    agent = _mock_agent()
    agent._update_mood("excited")
    original_intensity = agent._mood_intensity
    # Simulate one half-life elapsed
    agent._mood_set_at = time.time() - 138
    mood, intensity = agent._decayed_mood()
    # Should be significantly less than original but still positive
    assert mood == "excited"
    assert intensity < original_intensity


# ---------------------------------------------------------------------------
# Tests: interoception includes mood feel
# ---------------------------------------------------------------------------


def test_interoception_includes_mood_feel_when_non_neutral() -> None:
    from familiar_agent.agent import _interoception

    result = _interoception(
        started_at=time.time() - 60,
        turn_count=2,
        companion_mood="engaged",
        agent_mood="excited",
        agent_mood_intensity=0.8,
    )
    assert "excited" in result.lower() or "buzzing" in result.lower() or "mood" in result.lower()


def test_interoception_no_mood_line_when_neutral() -> None:
    from familiar_agent.agent import _interoception

    result = _interoception(
        started_at=time.time() - 60,
        turn_count=2,
        companion_mood="engaged",
        agent_mood="neutral",
        agent_mood_intensity=0.0,
    )
    # Should not add spurious mood content for neutral
    assert "buzzing" not in result
    assert "lingers" not in result
