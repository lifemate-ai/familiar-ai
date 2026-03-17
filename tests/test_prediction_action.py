"""Tests for action-conditioned prediction and agency error."""

from __future__ import annotations

import pytest

from familiar_agent.prediction import PredictionEngine


def _learn(pe: PredictionEngine, entities: list[str], repeats: int = 8) -> None:
    for _ in range(repeats):
        pe.update(entities)


def test_record_action_stores_previous_entities() -> None:
    pe = PredictionEngine()
    pe.update(["desk"])

    pe.record_action("look", {"direction": "left", "degrees": 45})

    trace = pe.recent_actions()[-1]
    assert trace.action_name == "look"
    assert trace.previous_entities == ("desk",)


def test_look_action_suppresses_external_surprise_on_view_change() -> None:
    pe = PredictionEngine()
    _learn(pe, ["desk"])

    pe.record_action("look", {"direction": "left", "degrees": 90})
    total = pe.compute_error(["window"])
    signal = pe.last_signal()

    assert signal is not None
    assert signal.action_name == "look"
    assert signal.agency_error == pytest.approx(0.0)
    assert signal.external_surprise < 0.3
    assert total < 0.3


def test_look_action_no_change_raises_agency_error() -> None:
    pe = PredictionEngine()
    _learn(pe, ["desk"])

    pe.record_action("look", {"direction": "left", "degrees": 90})
    pe.compute_error(["desk"])
    signal = pe.last_signal()

    assert signal is not None
    assert signal.agency_error > 0.6
    assert signal.total_error > 0.6


def test_walk_action_view_change_is_treated_as_agency_error() -> None:
    pe = PredictionEngine()
    _learn(pe, ["desk"])

    pe.record_action("walk", {"direction": "forward"})
    pe.compute_error(["window"])
    signal = pe.last_signal()

    assert signal is not None
    assert signal.action_name == "walk"
    assert signal.agency_error > signal.external_surprise


def test_as_coalition_includes_action_conditioning_context() -> None:
    pe = PredictionEngine()
    _learn(pe, ["desk"])

    pe.record_action("walk", {"direction": "forward"})
    pe.compute_error(["window"])
    coalition = pe.as_coalition()

    assert coalition is not None
    assert "agency" in coalition.summary
    assert "walk" in coalition.summary
