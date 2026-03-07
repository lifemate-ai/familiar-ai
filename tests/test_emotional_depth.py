"""Tests for expanded emotion vocabulary (Phase 5 — emotional depth).

Expands _infer_emotion from 6 → 12 labels, aligning _MOOD_INTENSITY
and _interoception agent mood feels to the full set.
"""

from __future__ import annotations

import time

import pytest

from familiar_agent.agent import EmbodiedAgent, _interoception


# The expected full set of emotion labels
_EXPECTED_EMOTIONS = {
    "happy",
    "sad",
    "curious",
    "excited",
    "moved",
    "surprised",
    "nostalgic",
    "relieved",
    "tender",
    "playful",
    "proud",
    "neutral",
}

_NON_NEUTRAL_EMOTIONS = _EXPECTED_EMOTIONS - {"neutral"}


# ---------------------------------------------------------------------------
# Tests: _EMOTION_PROMPT covers all labels
# ---------------------------------------------------------------------------


def test_emotion_prompt_lists_all_labels() -> None:
    from familiar_agent.agent import _EMOTION_PROMPT

    prompt = _EMOTION_PROMPT.lower()
    for label in _NON_NEUTRAL_EMOTIONS:
        assert label in prompt, f"Missing emotion '{label}' in _EMOTION_PROMPT"
    assert "neutral" in prompt


# ---------------------------------------------------------------------------
# Tests: _infer_emotion accepts all 12 labels
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_infer_emotion_accepts_all_new_labels() -> None:
    """The valid set in _infer_emotion must contain all 12 expected labels."""
    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    from unittest.mock import AsyncMock, MagicMock

    for label in _NON_NEUTRAL_EMOTIONS:
        agent._utility_backend = MagicMock()
        agent._utility_backend.complete = AsyncMock(return_value=label)
        result = await agent._infer_emotion("some text")
        assert result == label, f"_infer_emotion rejected valid label '{label}'"


@pytest.mark.asyncio
async def test_infer_emotion_rejects_unknown_label() -> None:
    from unittest.mock import AsyncMock, MagicMock

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._utility_backend = MagicMock()
    agent._utility_backend.complete = AsyncMock(return_value="furious")
    result = await agent._infer_emotion("some text")
    assert result == "neutral"


# ---------------------------------------------------------------------------
# Tests: _MOOD_INTENSITY covers all non-neutral emotions
# ---------------------------------------------------------------------------


def test_mood_intensity_has_all_non_neutral_emotions() -> None:
    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._mood = "neutral"
    agent._mood_intensity = 0.0
    agent._mood_set_at = time.time()

    for emotion in _NON_NEUTRAL_EMOTIONS:
        assert emotion in agent._MOOD_INTENSITY, f"Missing '{emotion}' in _MOOD_INTENSITY"


def test_mood_intensity_all_values_in_range() -> None:
    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._mood = "neutral"
    agent._mood_intensity = 0.0
    agent._mood_set_at = time.time()

    for emotion, intensity in agent._MOOD_INTENSITY.items():
        assert 0.0 < intensity <= 1.0, f"Invalid intensity {intensity} for '{emotion}'"


# ---------------------------------------------------------------------------
# Tests: _interoception agent mood feels covers all non-neutral emotions
# ---------------------------------------------------------------------------


def test_interoception_has_feel_for_all_non_neutral_moods() -> None:
    for emotion in _NON_NEUTRAL_EMOTIONS:
        result = _interoception(
            started_at=time.time() - 60,
            turn_count=1,
            companion_mood="engaged",
            agent_mood=emotion,
            agent_mood_intensity=0.7,
        )
        # Should produce a non-empty result that contains something about mood
        assert result, f"_interoception produced empty result for agent_mood='{emotion}'"


def test_interoception_new_emotions_produce_distinct_feels() -> None:
    """relieved, tender, playful, proud should each produce unique mood feel text."""
    results = {}
    for emotion in ("relieved", "tender", "playful", "proud"):
        results[emotion] = _interoception(
            started_at=time.time() - 60,
            turn_count=1,
            companion_mood="engaged",
            agent_mood=emotion,
            agent_mood_intensity=0.7,
        )
    # All 4 should be different strings
    unique_results = set(results.values())
    assert len(unique_results) == 4, "New emotions should produce distinct interoception text"


# ---------------------------------------------------------------------------
# Tests: _update_mood handles all new emotions
# ---------------------------------------------------------------------------


def test_update_mood_handles_all_new_emotions() -> None:
    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._mood = "neutral"
    agent._mood_intensity = 0.0
    agent._mood_set_at = time.time()

    for emotion in ("relieved", "tender", "playful", "proud"):
        agent._mood = "neutral"
        agent._mood_intensity = 0.0
        agent._update_mood(emotion)
        assert agent._mood == emotion, f"_update_mood failed for '{emotion}'"
        assert agent._mood_intensity > 0.0
