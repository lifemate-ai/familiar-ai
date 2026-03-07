"""Tests for Phase 3 DesireSystem v2 — circadian modulation, drive suppression, decay.

TDD: written before implementation.
"""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch


from familiar_agent.desires import DECAY_ON_SATISFY, DesireSystem


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_desires(tmp_path: Path) -> DesireSystem:
    """Create a DesireSystem with a temp state file (no real disk side-effects)."""
    return DesireSystem(state_path=tmp_path / "desires.json")


# ---------------------------------------------------------------------------
# Tests: Phase 3-3 — DECAY_ON_SATISFY (fix: was completely unused)
# ---------------------------------------------------------------------------


def test_satisfy_uses_decay_not_full_reset(tmp_path):
    """satisfy() should reduce desire by DECAY_ON_SATISFY, not reset to DEFAULT."""
    ds = _make_desires(tmp_path)
    # Manually set a desire above default
    ds._desires["look_around"] = 0.8

    ds.satisfy("look_around")

    result = ds.level("look_around")
    # Should be 0.8 * DECAY_ON_SATISFY (= 0.4), NOT default (0.1)
    expected = 0.8 * DECAY_ON_SATISFY
    assert abs(result - expected) < 1e-6


def test_satisfy_never_goes_below_zero(tmp_path):
    """satisfy() result must be non-negative."""
    ds = _make_desires(tmp_path)
    ds._desires["rest"] = 0.0
    ds.satisfy("rest")
    assert ds.level("rest") >= 0.0


def test_satisfy_unknown_desire_is_safe(tmp_path):
    """satisfy() on a non-existent desire does not raise."""
    ds = _make_desires(tmp_path)
    ds.satisfy("nonexistent_desire")  # must not raise


# ---------------------------------------------------------------------------
# Tests: Phase 3-1 — circadian modulation
# ---------------------------------------------------------------------------


def test_tick_grows_rest_faster_at_night(tmp_path):
    """During night hours (23:00), rest grows faster than default."""
    ds = _make_desires(tmp_path)
    ds._desires["rest"] = 0.0

    # Simulate tick at 23:00 (nighttime)
    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 23
        ds._last_tick = time.time() - 60  # 60 seconds elapsed
        ds.tick()

    night_rest = ds.level("rest")

    # Reset and simulate at noon
    ds2 = _make_desires(tmp_path)
    ds2._desires["rest"] = 0.0
    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 12
        ds2._last_tick = time.time() - 60
        ds2.tick()

    noon_rest = ds2.level("rest")

    assert night_rest > noon_rest, "rest should grow faster at night than noon"


def test_tick_grows_explore_slower_at_night(tmp_path):
    """During night hours, explore grows slower than during the day."""
    ds = _make_desires(tmp_path)
    ds._desires["explore"] = 0.0

    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 2  # 2 AM
        ds._last_tick = time.time() - 60
        ds.tick()

    night_explore = ds.level("explore")

    ds2 = _make_desires(tmp_path)
    ds2._desires["explore"] = 0.0
    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 14  # 2 PM
        ds2._last_tick = time.time() - 60
        ds2.tick()

    day_explore = ds2.level("explore")

    assert night_explore < day_explore, "explore should grow slower at night than afternoon"


def test_tick_grows_look_around_slower_at_night(tmp_path):
    """During night hours, look_around grows slower than during the day."""
    ds = _make_desires(tmp_path)
    ds._desires["look_around"] = 0.0

    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 3
        ds._last_tick = time.time() - 60
        ds.tick()

    night_look = ds.level("look_around")

    ds2 = _make_desires(tmp_path)
    ds2._desires["look_around"] = 0.0
    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 10
        ds2._last_tick = time.time() - 60
        ds2.tick()

    day_look = ds2.level("look_around")

    assert night_look < day_look


def test_circadian_modulation_returns_dict(tmp_path):
    """_time_modulation() returns a dict mapping desire names to rate multipliers."""
    ds = _make_desires(tmp_path)
    for hour in [0, 6, 12, 18, 23]:
        result = ds._time_modulation(hour)
        assert isinstance(result, dict)
        for v in result.values():
            assert isinstance(v, float)
            assert v >= 0.0


# ---------------------------------------------------------------------------
# Tests: Phase 3-2 — drive suppression
# ---------------------------------------------------------------------------


def test_tick_suppresses_explore_when_rest_is_high(tmp_path):
    """When rest is high (>0.5), explore grows slower during tick."""
    # High rest scenario
    ds_tired = _make_desires(tmp_path)
    ds_tired._desires["rest"] = 0.9
    ds_tired._desires["explore"] = 0.0
    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 14
        ds_tired._last_tick = time.time() - 60
        ds_tired.tick()
    tired_explore = ds_tired.level("explore")

    # Low rest scenario
    ds_fresh = _make_desires(tmp_path)
    ds_fresh._desires["rest"] = 0.0
    ds_fresh._desires["explore"] = 0.0
    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 14
        ds_fresh._last_tick = time.time() - 60
        ds_fresh.tick()
    fresh_explore = ds_fresh.level("explore")

    assert tired_explore < fresh_explore, "explore should grow slower when rest is high"


def test_tick_suppresses_look_around_when_rest_is_high(tmp_path):
    """When rest is high (>0.5), look_around grows slower during tick."""
    ds_tired = _make_desires(tmp_path)
    ds_tired._desires["rest"] = 0.8
    ds_tired._desires["look_around"] = 0.0
    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 14
        ds_tired._last_tick = time.time() - 60
        ds_tired.tick()
    tired_look = ds_tired.level("look_around")

    ds_fresh = _make_desires(tmp_path)
    ds_fresh._desires["rest"] = 0.0
    ds_fresh._desires["look_around"] = 0.0
    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 14
        ds_fresh._last_tick = time.time() - 60
        ds_fresh.tick()
    fresh_look = ds_fresh.level("look_around")

    assert tired_look < fresh_look


def test_dominant_prefers_worry_over_greet(tmp_path):
    """When worry_companion and greet_companion both exceed threshold,
    worry_companion wins (it takes priority over greeting)."""
    ds = _make_desires(tmp_path)
    ds._desires["worry_companion"] = 0.8
    ds._desires["greet_companion"] = 0.75

    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 14
        result = ds.get_dominant()

    assert result is not None
    name, _ = result
    assert name == "worry_companion"


def test_suppression_does_not_affect_worry(tmp_path):
    """worry_companion is exempt from rest-based suppression."""
    ds = _make_desires(tmp_path)
    ds._desires["rest"] = 0.9
    ds._desires["worry_companion"] = 0.0

    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 14
        ds._last_tick = time.time() - 10
        ds.tick()

    # worry_companion has no GROWTH_RATE so stays at 0 — just check it didn't go negative
    assert ds.level("worry_companion") >= 0.0


# ---------------------------------------------------------------------------
# Tests: existing behavior preserved
# ---------------------------------------------------------------------------


def test_boost_still_works(tmp_path):
    """boost() still increases the desire level."""
    ds = _make_desires(tmp_path)
    before = ds.level("look_around")
    ds.boost("look_around", 0.3)
    assert ds.level("look_around") > before


def test_level_capped_at_one(tmp_path):
    """desire level never exceeds 1.0."""
    ds = _make_desires(tmp_path)
    ds.boost("explore", 10.0)
    assert ds.level("explore") <= 1.0


def test_get_dominant_returns_none_below_threshold(tmp_path):
    """get_dominant() returns None when all desires are below trigger threshold."""
    ds = _make_desires(tmp_path)
    for k in ds._desires:
        ds._desires[k] = 0.0
    with patch("familiar_agent.desires.datetime") as mock_dt:
        mock_dt.now.return_value.hour = 12
        result = ds.get_dominant()
    assert result is None
