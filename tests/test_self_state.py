"""Tests for persistent latent self state."""

from __future__ import annotations

import pytest

from familiar_agent.self_state import SelfState
from familiar_agent.workspace import Coalition, GlobalWorkspace


def _coalition(source: str, *, activation: float = 0.8, urgency: float = 0.5, novelty: float = 0.4):
    return Coalition(
        source=source,
        summary=f"{source} event",
        activation=activation,
        urgency=urgency,
        novelty=novelty,
        context_block=f"[{source}]",
    )


def test_prediction_broadcast_raises_arousal_and_tension(tmp_path):
    state = SelfState(path=tmp_path / "self_state.json")
    before = state.snapshot()

    state.apply_broadcast(_coalition("prediction", novelty=0.9, urgency=0.8))
    after = state.snapshot()

    assert after["arousal"] > before["arousal"]
    assert after["unresolved_tension"] > before["unresolved_tension"]
    assert after["sensor_confidence"] < before["sensor_confidence"]


def test_memory_broadcast_strengthens_social_pull_and_focus(tmp_path):
    state = SelfState(path=tmp_path / "self_state.json")
    before = state.snapshot()

    state.apply_broadcast(_coalition("memory", activation=0.9))
    after = state.snapshot()

    assert after["social_pull"] > before["social_pull"]
    assert after["focus_stability"] > before["focus_stability"]
    assert after["unresolved_tension"] < before["unresolved_tension"]


def test_default_mode_broadcast_settles_arousal(tmp_path):
    state = SelfState(path=tmp_path / "self_state.json")
    state.apply_broadcast(_coalition("prediction", novelty=1.0, urgency=1.0))
    activated = state.snapshot()["arousal"]

    state.apply_broadcast(_coalition("default_mode", activation=0.5, urgency=0.1, novelty=0.0))
    settled = state.snapshot()["arousal"]

    assert settled < activated


def test_state_persists_to_disk(tmp_path):
    path = tmp_path / "self_state.json"
    state = SelfState(path=path)
    state.apply_broadcast(_coalition("memory", activation=0.95))

    reloaded = SelfState(path=path)
    assert reloaded.snapshot() == state.snapshot()


@pytest.mark.asyncio
async def test_workspace_listener_updates_self_state(tmp_path):
    state = SelfState(path=tmp_path / "self_state.json")
    ws = GlobalWorkspace()
    ws.register_broadcast_listener(state.on_broadcast)

    before = state.snapshot()
    await ws.notify_listeners(_coalition("prediction", novelty=0.8))
    after = state.snapshot()

    assert after != before
