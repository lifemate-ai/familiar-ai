"""Tests for the Global Workspace (GWT/GNWT) implementation.

Tests cover:
- Coalition dataclass and scoring
- GlobalWorkspace: gather, compete, ignition threshold, broadcast
- on_broadcast callbacks (feedback loop)
- Default-mode fallback when nothing ignites
- Peripheral awareness summary for non-winning coalitions
"""

from __future__ import annotations


import pytest

from familiar_agent.workspace import Coalition, GlobalWorkspace


# ── Coalition ─────────────────────────────────────────────────────────────────


def test_coalition_score_basic():
    c = Coalition(
        source="desire",
        summary="want to look around",
        activation=1.0,
        urgency=1.0,
        novelty=1.0,
        context_block="(desire look_around)",
    )
    assert c.score() == pytest.approx(1.0)


def test_coalition_score_zero_activation():
    c = Coalition(
        source="memory",
        summary="nothing",
        activation=0.0,
        urgency=1.0,
        novelty=1.0,
        context_block="",
    )
    assert c.score() == pytest.approx(0.0)


def test_coalition_score_weights():
    # score = activation * (0.4*urgency + 0.3*novelty + 0.3*1.0)
    c = Coalition(
        source="scene",
        summary="person appeared",
        activation=0.8,
        urgency=1.0,
        novelty=0.0,
        context_block="...",
    )
    expected = 0.8 * (0.4 * 1.0 + 0.3 * 0.0 + 0.3)
    assert c.score() == pytest.approx(expected)


# ── GlobalWorkspace.compete ────────────────────────────────────────────────────


def test_compete_returns_highest_score():
    low = Coalition(
        "memory", "old memory", activation=0.3, urgency=0.0, novelty=0.0, context_block="mem"
    )
    high = Coalition(
        "desire", "urgent desire", activation=0.9, urgency=1.0, novelty=0.5, context_block="des"
    )
    medium = Coalition(
        "scene", "scene update", activation=0.6, urgency=0.5, novelty=0.3, context_block="sc"
    )

    ws = GlobalWorkspace()
    winner = ws.compete([low, high, medium])
    assert winner is not None
    assert winner.source == "desire"


def test_compete_returns_none_below_threshold():
    ws = GlobalWorkspace(ignition_threshold=0.5)
    weak = Coalition(
        "memory", "faint memory", activation=0.1, urgency=0.0, novelty=0.0, context_block="m"
    )
    assert ws.compete([weak]) is None


def test_compete_returns_none_on_empty_list():
    ws = GlobalWorkspace()
    assert ws.compete([]) is None


def test_compete_ignition_threshold_boundary():
    ws = GlobalWorkspace(ignition_threshold=0.4)
    # activation=0.5, urgency=0, novelty=0 → score = 0.5 * 0.3 = 0.15 → below threshold
    below = Coalition("x", "x", activation=0.5, urgency=0.0, novelty=0.0, context_block="")
    assert ws.compete([below]) is None

    # activation=1.0, urgency=0.5, novelty=0.5 → score = 1.0*(0.2+0.15+0.3)=0.65 → above
    above = Coalition("y", "y", activation=1.0, urgency=0.5, novelty=0.5, context_block="y")
    assert ws.compete([above]) is not None


# ── GlobalWorkspace.broadcast ──────────────────────────────────────────────────


def test_broadcast_returns_winner_context_block():
    ws = GlobalWorkspace()
    winner = Coalition(
        "desire",
        "look_around",
        activation=0.9,
        urgency=1.0,
        novelty=0.5,
        context_block="(desire look_around)",
    )
    others = [
        Coalition(
            "scene",
            "empty room",
            activation=0.3,
            urgency=0.1,
            novelty=0.1,
            context_block="(scene empty)",
        ),
    ]
    result = ws.broadcast(winner, others)
    assert "(desire look_around)" in result


def test_broadcast_includes_peripheral_summary():
    ws = GlobalWorkspace()
    winner = Coalition(
        "desire",
        "look_around",
        activation=0.9,
        urgency=1.0,
        novelty=0.5,
        context_block="(desire look_around)",
    )
    others = [
        Coalition(
            "scene",
            "empty room",
            activation=0.3,
            urgency=0.1,
            novelty=0.1,
            context_block="(scene empty)",
        ),
        Coalition(
            "memory",
            "old memory",
            activation=0.2,
            urgency=0.0,
            novelty=0.0,
            context_block="(memory old)",
        ),
    ]
    result = ws.broadcast(winner, others)
    # Peripheral awareness summary should mention non-winning sources
    assert "scene" in result.lower() or "memory" in result.lower()


def test_broadcast_without_others():
    ws = GlobalWorkspace()
    winner = Coalition(
        "desire",
        "look_around",
        activation=0.9,
        urgency=1.0,
        novelty=0.5,
        context_block="(desire look_around)",
    )
    result = ws.broadcast(winner, [])
    assert "(desire look_around)" in result


# ── on_broadcast callbacks ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_on_broadcast_callbacks_called():
    ws = GlobalWorkspace()
    received = []

    async def handler(winner: Coalition) -> None:
        received.append(winner.source)

    ws.register_broadcast_listener(handler)

    winner = Coalition(
        "desire", "look", activation=0.9, urgency=1.0, novelty=0.5, context_block="d"
    )
    await ws.notify_listeners(winner)

    assert received == ["desire"]


@pytest.mark.asyncio
async def test_multiple_listeners_all_called():
    ws = GlobalWorkspace()
    log: list[str] = []

    async def l1(w: Coalition) -> None:
        log.append("l1")

    async def l2(w: Coalition) -> None:
        log.append("l2")

    ws.register_broadcast_listener(l1)
    ws.register_broadcast_listener(l2)

    winner = Coalition(
        "scene", "person", activation=0.9, urgency=1.0, novelty=0.8, context_block="s"
    )
    await ws.notify_listeners(winner)

    assert "l1" in log and "l2" in log


# ── Ignition threshold modulation ─────────────────────────────────────────────


def test_lower_threshold_on_high_prediction_error():
    ws = GlobalWorkspace(ignition_threshold=0.6)
    # With high prediction error, threshold should lower
    ws.apply_prediction_error(1.0)
    # A coalition that wouldn't fire at 0.6 should now fire
    # score = 0.5 * 0.3 = 0.15 < 0.6, but with error adjustment...
    # The effective threshold should be lower than 0.6
    assert ws.effective_threshold() < 0.6


def test_prediction_error_zero_keeps_threshold():
    ws = GlobalWorkspace(ignition_threshold=0.5)
    ws.apply_prediction_error(0.0)
    assert ws.effective_threshold() == pytest.approx(0.5)


def test_prediction_error_caps_at_minimum():
    ws = GlobalWorkspace(ignition_threshold=0.5)
    ws.apply_prediction_error(10.0)  # extreme value
    # Threshold should not go below a minimum floor
    assert ws.effective_threshold() >= 0.05


# ── Peripheral awareness formatting ───────────────────────────────────────────


def test_peripheral_summary_one_liner_per_source():
    ws = GlobalWorkspace()
    others = [
        Coalition(
            "scene", "empty room", activation=0.3, urgency=0.1, novelty=0.1, context_block="sc"
        ),
        Coalition(
            "memory",
            "lunch yesterday",
            activation=0.2,
            urgency=0.0,
            novelty=0.0,
            context_block="me",
        ),
    ]
    summary = ws.peripheral_summary(others)
    lines = [line for line in summary.split("\n") if line.strip()]
    # Each non-winning source should appear as one line
    assert len(lines) >= 2


def test_peripheral_summary_empty():
    ws = GlobalWorkspace()
    assert ws.peripheral_summary([]) == ""
