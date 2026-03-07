"""Tests for scene-event-driven greeting behavior.

Phase 1 of companion-likeness improvements.
When SceneTracker detects "person appeared", greet_companion desire is boosted.
"""

from __future__ import annotations


from familiar_agent.desires import TRIGGER_THRESHOLD, DesireSystem


def _desires(tmp_path) -> DesireSystem:
    """DesireSystem with persistent state in tmp_path."""
    return DesireSystem(state_path=tmp_path / "desires.json")


def _react(events: list[dict], desires: DesireSystem | None) -> None:
    """Call _react_to_scene_events via the module-level helper (to be implemented)."""
    from familiar_agent.agent import _react_to_scene_events

    _react_to_scene_events(events, desires)


# ---------------------------------------------------------------------------
# Tests: person appeared → greet_companion boosted
# ---------------------------------------------------------------------------


def test_person_appeared_boosts_greet_companion_above_threshold(tmp_path) -> None:
    desires = _desires(tmp_path)
    initial = desires.level("greet_companion")
    events = [{"event_type": "appeared", "entity_label": "person", "entity_id": None}]

    _react(events, desires)

    assert desires.level("greet_companion") > initial
    assert desires.level("greet_companion") >= TRIGGER_THRESHOLD


def test_non_person_appeared_does_not_boost_greet(tmp_path) -> None:
    desires = _desires(tmp_path)
    events = [{"event_type": "appeared", "entity_label": "chair", "entity_id": None}]

    _react(events, desires)

    # greet_companion stays at default (0.0)
    assert desires.level("greet_companion") < TRIGGER_THRESHOLD


def test_object_appeared_does_not_boost_greet(tmp_path) -> None:
    desires = _desires(tmp_path)
    events = [{"event_type": "appeared", "entity_label": "laptop", "entity_id": None}]

    _react(events, desires)

    assert desires.level("greet_companion") < TRIGGER_THRESHOLD


# ---------------------------------------------------------------------------
# Tests: person disappeared → worry_companion gentle boost
# ---------------------------------------------------------------------------


def test_person_disappeared_boosts_worry_companion(tmp_path) -> None:
    desires = _desires(tmp_path)
    initial = desires.level("worry_companion")
    events = [{"event_type": "disappeared", "entity_label": "person", "entity_id": "e1"}]

    _react(events, desires)

    assert desires.level("worry_companion") > initial


def test_person_disappeared_boost_is_gentle(tmp_path) -> None:
    """worry_companion gets only a small boost (< 0.5) from disappearance."""
    desires = _desires(tmp_path)
    events = [{"event_type": "disappeared", "entity_label": "person", "entity_id": "e1"}]

    _react(events, desires)

    assert desires.level("worry_companion") < 0.5


def test_non_person_disappeared_does_not_boost_worry(tmp_path) -> None:
    desires = _desires(tmp_path)
    events = [{"event_type": "disappeared", "entity_label": "bottle", "entity_id": "e2"}]

    _react(events, desires)

    assert desires.level("worry_companion") == 0.0


# ---------------------------------------------------------------------------
# Tests: edge cases
# ---------------------------------------------------------------------------


def test_multiple_person_appeared_events_capped_at_1(tmp_path) -> None:
    desires = _desires(tmp_path)
    events = [
        {"event_type": "appeared", "entity_label": "person", "entity_id": None},
        {"event_type": "appeared", "entity_label": "person", "entity_id": None},
        {"event_type": "appeared", "entity_label": "person", "entity_id": None},
    ]

    _react(events, desires)

    assert desires.level("greet_companion") <= 1.0


def test_none_desires_does_not_crash() -> None:
    events = [{"event_type": "appeared", "entity_label": "person", "entity_id": None}]

    # Must not raise
    _react(events, None)


def test_empty_events_no_effect(tmp_path) -> None:
    desires = _desires(tmp_path)
    before_greet = desires.level("greet_companion")
    before_worry = desires.level("worry_companion")

    _react([], desires)

    assert desires.level("greet_companion") == before_greet
    assert desires.level("worry_companion") == before_worry
