"""Tests for MobilityTool — Tuya Cloud API mocked, no real hardware."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_mobility():
    from familiar_agent.tools.mobility import MobilityTool

    tool = MobilityTool.__new__(MobilityTool)
    tool._api_region = "us"
    tool._api_key = "fake-key"
    tool._api_secret = "fake-secret"
    tool._device_id = "fake-device-id"
    tool._cloud = None
    return tool


# ---------------------------------------------------------------------------
# Tests: get_tool_definitions()
# ---------------------------------------------------------------------------


def test_get_tool_definitions_returns_walk():
    tool = _make_mobility()
    defs = tool.get_tool_definitions()
    assert len(defs) == 1
    assert defs[0]["name"] == "walk"


def test_get_tool_definitions_has_direction_enum():
    tool = _make_mobility()
    defs = tool.get_tool_definitions()
    directions = defs[0]["input_schema"]["properties"]["direction"]["enum"]
    assert set(directions) == {"forward", "backward", "left", "right", "stop"}


# ---------------------------------------------------------------------------
# Tests: move()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_move_forward_sends_correct_direction():
    """move('forward') sends the forward direction code to Tuya Cloud."""
    from familiar_agent.tools.mobility import DIRECTION_FORWARD

    tool = _make_mobility()

    sent_commands = []

    async def fake_send(direction):
        sent_commands.append(direction)

    tool._send = fake_send

    result = await tool.move("forward")

    assert sent_commands == [DIRECTION_FORWARD]
    assert "forward" in result.lower()


@pytest.mark.asyncio
async def test_move_stop_sends_stop_direction():
    from familiar_agent.tools.mobility import DIRECTION_STOP

    tool = _make_mobility()
    sent = []

    async def fake_send(direction):
        sent.append(direction)

    tool._send = fake_send

    result = await tool.move("stop")

    assert sent == [DIRECTION_STOP]
    assert "stop" in result.lower()


@pytest.mark.asyncio
async def test_move_invalid_direction_returns_error():
    tool = _make_mobility()
    tool._send = AsyncMock()

    result = await tool.move("diagonal")

    assert "invalid" in result.lower() or "diagonal" in result
    tool._send.assert_not_awaited()


@pytest.mark.asyncio
async def test_move_with_duration_sends_stop_after():
    """move() with duration sends the direction then auto-stops."""
    from familiar_agent.tools.mobility import DIRECTION_FORWARD, DIRECTION_STOP

    tool = _make_mobility()
    sent = []

    async def fake_send(direction):
        sent.append(direction)

    tool._send = fake_send

    with patch("familiar_agent.tools.mobility.asyncio.sleep", new=AsyncMock()):
        result = await tool.move("forward", duration=1.0)

    assert DIRECTION_FORWARD in sent
    assert DIRECTION_STOP in sent
    assert sent.index(DIRECTION_FORWARD) < sent.index(DIRECTION_STOP)
    assert "1.0" in result or "1" in result


@pytest.mark.asyncio
@pytest.mark.parametrize("direction", ["forward", "backward", "left", "right"])
async def test_move_each_direction(direction: str):
    """All valid directions complete without error."""
    tool = _make_mobility()
    tool._send = AsyncMock()

    result = await tool.move(direction)

    tool._send.assert_awaited_once()
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Tests: call()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_call_walk_routes_to_move():
    tool = _make_mobility()

    async def fake_move(direction, duration=None):
        return f"Moved {direction}"

    tool.move = fake_move

    result, img = await tool.call("walk", {"direction": "forward"})

    assert result == "Moved forward"
    assert img is None


@pytest.mark.asyncio
async def test_call_walk_passes_duration():
    tool = _make_mobility()
    received = {}

    async def fake_move(direction, duration=None):
        received["direction"] = direction
        received["duration"] = duration
        return "ok"

    tool.move = fake_move

    await tool.call("walk", {"direction": "left", "duration": 2.5})

    assert received["direction"] == "left"
    assert received["duration"] == 2.5


@pytest.mark.asyncio
async def test_call_unknown_tool_returns_error():
    tool = _make_mobility()
    tool._send = AsyncMock()

    result, img = await tool.call("fly", {})

    assert "Unknown" in result or "fly" in result


@pytest.mark.asyncio
async def test_call_handles_exception_gracefully():
    """If move() raises, call() returns an error string, not an exception."""
    tool = _make_mobility()

    async def bad_move(direction, duration=None):
        raise ConnectionError("Tuya unreachable")

    tool.move = bad_move

    result, img = await tool.call("walk", {"direction": "forward"})

    assert (
        "failed" in result.lower() or "error" in result.lower() or "unreachable" in result.lower()
    )


# ---------------------------------------------------------------------------
# Tests: _send() — Tuya Cloud integration mock
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_send_calls_tuya_cloud():
    """_send() creates a Tuya Cloud client and calls sendcommand."""
    tool = _make_mobility()

    mock_cloud = MagicMock()
    mock_cloud.sendcommand = MagicMock(return_value={"result": True})

    with (
        patch("familiar_agent.tools.mobility.tinytuya.Cloud", return_value=mock_cloud),
        patch("familiar_agent.tools.mobility.asyncio.to_thread", new=AsyncMock()),
    ):
        await tool._send("forward")

    # Cloud was lazily created
    assert tool._cloud is not None
