"""Stress tests for TUI interrupt handling under rapid input and ESC spam."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest


def _make_app():
    from familiar_agent.tui import FamiliarApp

    agent = MagicMock()
    agent.config.agent_name = "A"
    agent.config.companion_name = "U"
    desires = MagicMock()

    with patch("familiar_agent.tui._make_banner", return_value=""):
        return FamiliarApp(agent, desires)


@pytest.mark.asyncio
async def test_rapid_inputs_and_escape_spam_keep_inputs_for_processing():
    """Rapid input during a running turn must remain queued for later processing."""
    app = _make_app()

    processed: list[str] = []

    async def _fake_run_agent(text: str) -> None:
        processed.append(text)
        await asyncio.sleep(0)

    app._run_agent = _fake_run_agent  # type: ignore[method-assign]
    app._log_system = MagicMock()
    app._agent_running = True
    app._agent_task = asyncio.create_task(asyncio.sleep(10))

    queue_worker = asyncio.create_task(app._process_queue())

    burst = [f"msg-{i}" for i in range(25)]
    for msg in burst:
        await app._input_queue.put(msg)

    # ESC spam while a turn is considered running.
    for _ in range(30):
        app.action_cancel_turn()

    await asyncio.sleep(0.1)
    assert processed == []
    assert app._cancel_event.is_set()

    # Let cancellation propagate to the dummy running task.
    if app._agent_task:
        try:
            await app._agent_task
        except asyncio.CancelledError:
            pass

    # Release queue processing and verify all queued inputs are processed in order.
    app._agent_running = False
    await asyncio.sleep(0.2)
    await app._input_queue.put(None)
    await asyncio.wait_for(queue_worker, timeout=2.0)

    assert processed == burst
