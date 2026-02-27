"""Tests for the desire system, including worry_companion."""

from __future__ import annotations

from pathlib import Path

import pytest

from familiar_agent.desires import (
    DEFAULT_DESIRES,
    GROWTH_RATES,
    TRIGGER_THRESHOLD,
    DesireSystem,
    detect_worry_signal,
)


# ── detect_worry_signal ────────────────────────────────────────────────────────


def test_detect_worry_no_signal_on_neutral_text() -> None:
    assert detect_worry_signal("今日はいい天気やね") == 0.0


def test_detect_worry_no_signal_on_empty() -> None:
    assert detect_worry_signal("") == 0.0


def test_detect_worry_strong_signal_sleep_deprivation() -> None:
    assert detect_worry_signal("昨日も寝不足でしんどい") >= 0.4


def test_detect_worry_strong_signal_cant_sleep() -> None:
    assert detect_worry_signal("全然眠れなくて") >= 0.4


def test_detect_worry_strong_signal_health() -> None:
    assert detect_worry_signal("熱が出てきた気がする") >= 0.4


def test_detect_worry_strong_signal_cold() -> None:
    assert detect_worry_signal("風邪ひいたかも") >= 0.4


def test_detect_worry_strong_signal_exhausted() -> None:
    assert detect_worry_signal("疲れ果てた、もう限界かも") >= 0.4


def test_detect_worry_weak_signal_tired() -> None:
    result = detect_worry_signal("今日ちょっと疲れたわ")
    assert 0.0 < result < 0.4


def test_detect_worry_weak_signal_stressed() -> None:
    result = detect_worry_signal("仕事がしんどくてさ")
    assert 0.0 < result < 0.4


def test_detect_worry_english_sleep_deprivation() -> None:
    assert detect_worry_signal("I slept only 3 hours") >= 0.4


def test_detect_worry_returns_float() -> None:
    result = detect_worry_signal("なんかしんどい")
    assert isinstance(result, float)


def test_detect_worry_caps_at_one() -> None:
    # Even with many signals, should not exceed 1.0
    text = "寝不足で風邪ひいて熱もあって眠れなくてしんどい疲れた"
    assert detect_worry_signal(text) <= 1.0


# ── worry_companion desire defaults ───────────────────────────────────────────


def test_worry_companion_in_default_desires() -> None:
    assert "worry_companion" in DEFAULT_DESIRES


def test_worry_companion_default_is_zero() -> None:
    assert DEFAULT_DESIRES["worry_companion"] == 0.0


def test_worry_companion_has_no_growth_rate() -> None:
    # worry should only grow via boost(), not via time
    assert GROWTH_RATES.get("worry_companion", 0.0) == 0.0


# ── DesireSystem with worry_companion ─────────────────────────────────────────


@pytest.fixture
def desires(tmp_path: Path) -> DesireSystem:
    return DesireSystem(state_path=tmp_path / "desires.json")


def test_worry_starts_at_zero(desires: DesireSystem) -> None:
    assert desires.level("worry_companion") == 0.0


def test_worry_does_not_grow_over_time(desires: DesireSystem) -> None:
    desires.tick()
    assert desires.level("worry_companion") == 0.0


def test_worry_boost_raises_level(desires: DesireSystem) -> None:
    desires.boost("worry_companion", 0.4)
    assert desires.level("worry_companion") == pytest.approx(0.4)


def test_worry_boost_accumulates(desires: DesireSystem) -> None:
    desires.boost("worry_companion", 0.3)
    desires.boost("worry_companion", 0.2)
    assert desires.level("worry_companion") == pytest.approx(0.5)


def test_worry_boost_caps_at_one(desires: DesireSystem) -> None:
    desires.boost("worry_companion", 0.9)
    desires.boost("worry_companion", 0.9)
    assert desires.level("worry_companion") == pytest.approx(1.0)


def test_worry_fires_as_dominant_above_threshold(desires: DesireSystem) -> None:
    desires.boost("worry_companion", TRIGGER_THRESHOLD)
    result = desires.get_dominant()
    assert result is not None
    name, level = result
    assert name == "worry_companion"
    assert level >= TRIGGER_THRESHOLD


def test_worry_does_not_fire_below_threshold(desires: DesireSystem) -> None:
    desires.boost("worry_companion", TRIGGER_THRESHOLD - 0.1)
    # other desires are also below threshold by default
    result = desires.get_dominant()
    # worry specifically should not dominate — but others may fire from time
    # so check only that worry alone below threshold wouldn't be dominant
    if result is not None:
        name, _ = result
        assert name != "worry_companion"


def test_worry_satisfy_resets_to_zero(desires: DesireSystem) -> None:
    desires.boost("worry_companion", 0.8)
    desires.satisfy("worry_companion")
    assert desires.level("worry_companion") == 0.0


def test_worry_prompt_returned_when_dominant(desires: DesireSystem) -> None:
    desires.boost("worry_companion", TRIGGER_THRESHOLD)
    prompt = desires.dominant_as_prompt()
    assert prompt is not None
    assert "心配" in prompt or "コウタ" in prompt


def test_worry_prompt_contains_action_hint(desires: DesireSystem) -> None:
    desires.boost("worry_companion", TRIGGER_THRESHOLD)
    prompt = desires.dominant_as_prompt()
    assert prompt is not None
    # Should hint at taking action (say or check in)
    assert "say()" in prompt or "声" in prompt or "確認" in prompt


def test_worry_persists_across_reload(desires: DesireSystem, tmp_path: Path) -> None:
    desires.boost("worry_companion", 0.7)
    # reload from same path
    desires2 = DesireSystem(state_path=tmp_path / "desires.json")
    assert desires2.level("worry_companion") == pytest.approx(0.7)
