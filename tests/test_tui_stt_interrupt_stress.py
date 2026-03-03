"""Stress tests for TUI with realtime STT + rapid input + ESC spam."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest


class _ManualRealtimeStt:
    """Minimal controllable realtime STT session stub for TUI tests."""

    def __init__(self) -> None:
        self.on_partial = None
        self.on_committed = None
        self._queue: asyncio.Queue[str | None] | None = None
        self.started = False

    async def start(self, _loop: asyncio.AbstractEventLoop, committed_queue) -> None:
        self._queue = committed_queue
        self.started = True

    async def stop(self) -> None:
        self.started = False

    async def emit_committed(self, text: str) -> None:
        assert self._queue is not None
        if self.on_committed:
            self.on_committed(text)
        await self._queue.put(text)


def _make_app():
    from familiar_agent.tui import FamiliarApp

    agent = MagicMock()
    agent.config.agent_name = "A"
    agent.config.companion_name = "U"
    desires = MagicMock()

    with patch("familiar_agent.tui._make_banner", return_value=""):
        return FamiliarApp(agent, desires)


@pytest.mark.asyncio
async def test_stt_on_rapid_inputs_and_escape_spam_no_drop_no_crash():
    """With STT ON, rapid typed+voice inputs should survive ESC spam while running."""
    app = _make_app()
    fake_stt = _ManualRealtimeStt()
    app._realtime_stt = fake_stt  # type: ignore[assignment]

    processed: list[str] = []

    async def _fake_run_agent(text: str) -> None:
        processed.append(text)
        await asyncio.sleep(0)

    app._run_agent = _fake_run_agent  # type: ignore[method-assign]
    app._write_log = MagicMock()
    fake_stream = MagicMock()
    app.query_one = MagicMock(return_value=fake_stream)

    await app._start_realtime_stt()
    assert fake_stt.started

    app._agent_running = True
    app._agent_task = asyncio.create_task(asyncio.sleep(10))
    queue_worker = asyncio.create_task(app._process_queue())

    burst = [
        ("typed", "typed-0"),
        ("stt", "voice-0"),
        ("typed", "typed-1"),
        ("stt", "voice-1"),
        ("typed", "typed-2"),
        ("stt", "voice-2"),
    ]

    for source, text in burst:
        if source == "typed":
            await app._input_queue.put(text)
        else:
            await fake_stt.emit_committed(text)

    for _ in range(40):
        app.action_cancel_turn()

    await asyncio.sleep(0.1)
    assert app._cancel_event.is_set()
    assert processed == []

    if app._agent_task:
        try:
            await app._agent_task
        except asyncio.CancelledError:
            pass

    app._agent_running = False
    await asyncio.sleep(0.2)
    await app._input_queue.put(None)
    await asyncio.wait_for(queue_worker, timeout=2.0)

    expected = [text for _, text in burst]
    assert processed == expected
