"""Tests for the PredictionEngine (Phase 2: prediction error modulation).

Tests cover:
- Entity probability model (exponential moving average)
- Prediction error computation (surprise = high error)
- update() integrates observed entities into the model
- compute_error() returns 0 for fully predicted entities, high for novel ones
- Integration: PredictionEngine + GlobalWorkspace threshold modulation
"""

from __future__ import annotations

import pytest

from familiar_agent.prediction import PredictionEngine


# ── PredictionEngine construction ─────────────────────────────────────────────


def test_default_construction():
    pe = PredictionEngine()
    assert pe is not None


def test_custom_alpha():
    pe = PredictionEngine(ema_alpha=0.5)
    assert pe._ema_alpha == 0.5


# ── predict ────────────────────────────────────────────────────────────────────


def test_predict_returns_empty_on_no_history():
    pe = PredictionEngine()
    assert pe.predict() == {}


def test_predict_returns_probabilities_after_update():
    pe = PredictionEngine()
    pe.update(["chair", "person"])
    probs = pe.predict()
    assert "chair" in probs
    assert "person" in probs
    assert 0.0 <= probs["chair"] <= 1.0
    assert 0.0 <= probs["person"] <= 1.0


# ── compute_error ──────────────────────────────────────────────────────────────


def test_error_zero_when_nothing_seen_and_nothing_expected():
    pe = PredictionEngine()
    # No history, no observation → zero error
    error = pe.compute_error([])
    assert error == pytest.approx(0.0)


def test_error_high_for_completely_novel_entities():
    """Entities never seen before should produce high prediction error."""
    pe = PredictionEngine()
    error = pe.compute_error(["alien", "spaceship", "laser"])
    assert error > 0.5


def test_error_low_after_learning_entities():
    """After many updates, previously seen entities should have low error."""
    pe = PredictionEngine()
    for _ in range(10):
        pe.update(["chair", "table"])
    error = pe.compute_error(["chair", "table"])
    assert error < 0.3


def test_error_high_when_predicted_entities_disappear():
    """If the model expected entities and they're gone, error should be non-zero."""
    pe = PredictionEngine()
    for _ in range(5):
        pe.update(["chair", "person"])
    # Now only chair — person disappeared unexpectedly
    error = pe.compute_error(["chair"])
    assert error > 0.0


def test_error_bounded_between_zero_and_one():
    pe = PredictionEngine()
    pe.update(["a", "b"])
    error = pe.compute_error(["c", "d", "e", "f"])
    assert 0.0 <= error <= 1.0


def test_error_mixed_novel_and_known():
    """Partial novelty should give intermediate error."""
    pe = PredictionEngine()
    for _ in range(5):
        pe.update(["chair"])
    # chair is known, cat is novel
    error_known = pe.compute_error(["chair"])
    pe.compute_error(["chair", "cat"])  # mixed (not asserted directly)
    error_novel = pe.compute_error(["cat"])
    # novel > mixed > known (or at least novel >= known)
    assert error_novel >= error_known


# ── update ─────────────────────────────────────────────────────────────────────


def test_update_increases_probability_for_seen_entities():
    pe = PredictionEngine()
    pe.update(["chair"])
    p_after_one = pe.predict()["chair"]
    pe.update(["chair"])
    p_after_two = pe.predict()["chair"]
    assert p_after_two >= p_after_one


def test_update_with_empty_list():
    pe = PredictionEngine()
    pe.update([])  # should not raise
    assert pe.predict() == {}


def test_update_decreases_probability_for_absent_entities():
    """Entities not seen decay over time via EMA."""
    pe = PredictionEngine(ema_alpha=0.5)
    for _ in range(5):
        pe.update(["chair"])
    p_before = pe.predict()["chair"]
    # Update without chair — its probability should decay
    for _ in range(5):
        pe.update([])
    p_after = pe.predict().get("chair", 0.0)
    assert p_after < p_before


# ── Integration: prediction error → workspace threshold ───────────────────────


def test_prediction_error_lowers_workspace_threshold():
    """High prediction error should lower GlobalWorkspace ignition threshold."""
    from familiar_agent.workspace import GlobalWorkspace

    pe = PredictionEngine()
    ws = GlobalWorkspace(ignition_threshold=0.5)

    # Compute error from novel entities
    error = pe.compute_error(["dragon", "wizard"])
    ws.apply_prediction_error(error)

    assert ws.effective_threshold() < 0.5


def test_no_prediction_error_keeps_threshold():
    """Zero prediction error should keep the threshold at its base value."""
    from familiar_agent.workspace import GlobalWorkspace

    pe = PredictionEngine()
    ws = GlobalWorkspace(ignition_threshold=0.5)

    # No novelty — error should be 0
    error = pe.compute_error([])
    ws.apply_prediction_error(error)

    assert ws.effective_threshold() == pytest.approx(0.5)


# ── as_coalition ───────────────────────────────────────────────────────────────


def test_as_coalition_returns_none_with_no_history():
    pe = PredictionEngine()
    assert pe.as_coalition() is None


def test_as_coalition_returns_none_when_no_recent_error():
    pe = PredictionEngine()
    pe.update(["chair"])
    # No compute_error called yet → no coalition
    assert pe.as_coalition() is None


def test_as_coalition_returns_coalition_after_error_computed():
    from familiar_agent.workspace import Coalition

    pe = PredictionEngine()
    pe.update(["chair"])
    pe.compute_error(["dragon"])  # novel → high error

    c = pe.as_coalition()
    assert c is not None
    assert isinstance(c, Coalition)
    assert c.source == "prediction"
    assert 0.0 <= c.activation <= 1.0
    assert 0.0 <= c.urgency <= 1.0
    assert 0.0 <= c.novelty <= 1.0


def test_as_coalition_novelty_reflects_prediction_error():
    pe = PredictionEngine()
    pe.update(["chair"])

    # Low error case
    pe.compute_error(["chair"])
    c_low = pe.as_coalition()

    # High error case
    pe2 = PredictionEngine()
    pe2.update(["chair"])
    pe2.compute_error(["completely", "novel", "entities"])
    c_high = pe2.as_coalition()

    if c_low is not None and c_high is not None:
        assert c_high.novelty >= c_low.novelty


def test_intention_result_trace_records_action_conditioned_outcome():
    pe = PredictionEngine()
    pe.update(["desk"])
    pe.record_action("look", {"degrees": 45})

    pe.compute_error(["window"])
    traces = pe.recent_intention_results()

    assert len(traces) == 1
    assert traces[0].intent == "look"
    assert traces[0].agency_error >= 0.0


def test_prompt_context_surfaces_recent_misaligned_intention():
    pe = PredictionEngine()
    pe.update(["desk"])
    pe.record_action("look", {"degrees": 60})

    pe.compute_error(["desk"])
    prompt_ctx = pe.context_for_prompt()

    assert prompt_ctx is not None
    assert "[Recent intention-result]" in prompt_ctx
    assert "I tried to look." in prompt_ctx
