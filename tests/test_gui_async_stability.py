"""Regression tests for GUI async stability (burst input, cancel, shutdown)."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from unittest.mock import MagicMock

import pytest

from familiar_agent.gui import ChatLog, FamiliarWindow


class _FakeCloseEvent:
    def __init__(self) -> None:
        self.accepted = False
        self.ignored = False

    def accept(self) -> None:
        self.accepted = True

    def ignore(self) -> None:
        self.ignored = True


def _make_window_stub() -> FamiliarWindow:
    win = FamiliarWindow.__new__(FamiliarWindow)
    win._agent_display_name = "Yukine"
    win._companion_display_name = "Kota"
    win._input_queue = asyncio.Queue()
    win._agent_running = False
    win._closing = False
    win._shutdown_requested = False
    win._shutdown_done = False
    win._shutdown_task = None
    win._cancel_requested = False
    win._agent_task = None
    win._queue_task = None
    win._init_task = None
    win._desires = MagicMock()
    win._log = MagicMock()
    win._send_btn = MagicMock()
    win._stop_btn = MagicMock()
    win._lag_timer = MagicMock()
    win._last_lag_tick = time.perf_counter()
    win.setEnabled = MagicMock()
    win.setWindowTitle = MagicMock()
    win.close = MagicMock()
    return win


def _make_chat_log_stub(
    *, agent_label: str = "Yukine", companion_label: str = "Kota"
) -> tuple[ChatLog, list[tuple[str, dict]]]:
    log = ChatLog.__new__(ChatLog)
    log._agent_label = agent_label
    log._companion_label = companion_label
    captured: list[tuple[str, dict]] = []

    def _capture(text: str, **kwargs) -> None:
        captured.append((text, kwargs))

    log._add_bubble = _capture  # type: ignore[method-assign]
    return log, captured


@pytest.mark.asyncio
async def test_gui_process_queue_handles_burst_in_order():
    win = _make_window_stub()
    processed: list[str] = []

    async def _fake_run_agent(text: str, inner_voice: str = "") -> None:
        assert inner_voice == ""
        processed.append(text)
        await asyncio.sleep(0)

    win._run_agent = _fake_run_agent  # type: ignore[method-assign]

    burst = [f"msg-{i}" for i in range(30)]
    for msg in burst:
        await win._input_queue.put(msg)
    await win._input_queue.put(None)

    await asyncio.wait_for(FamiliarWindow._process_queue(win), timeout=1.0)
    assert processed == burst


@pytest.mark.asyncio
async def test_gui_cancel_turn_cancels_running_task_and_logs():
    win = _make_window_stub()
    win._agent_running = True
    win._agent_task = asyncio.create_task(asyncio.sleep(10))

    FamiliarWindow._cancel_turn(win, reason="user")
    assert win._cancel_requested is True
    win._log.append_line.assert_called_with("[interrupted]")

    if win._agent_task:
        with contextlib.suppress(asyncio.CancelledError):
            await win._agent_task
        assert win._agent_task.cancelled()


@pytest.mark.asyncio
async def test_gui_close_event_waits_shutdown_before_accepting():
    win = _make_window_stub()

    async def _fake_shutdown() -> None:
        await asyncio.sleep(0)
        win._shutdown_done = True

    win._shutdown = _fake_shutdown  # type: ignore[method-assign]

    first = _FakeCloseEvent()
    FamiliarWindow.closeEvent(win, first)
    assert first.ignored is True
    assert win._shutdown_requested is True
    assert win._closing is True
    assert win._shutdown_task is not None

    await asyncio.wait_for(win._shutdown_task, timeout=1.0)
    await asyncio.sleep(0)
    win.close.assert_called_once()

    second = _FakeCloseEvent()
    FamiliarWindow.closeEvent(win, second)
    assert second.accepted is True


def test_gui_event_loop_lag_warning_emits_log(caplog: pytest.LogCaptureFixture):
    win = _make_window_stub()
    win._agent_running = True
    win._last_lag_tick = time.perf_counter() - 2.0
    win._input_queue.put_nowait("pending")

    with caplog.at_level(logging.WARNING):
        FamiliarWindow._report_event_loop_lag(win)

    assert "event-loop lag detected" in caplog.text


def test_gui_create_task_falls_back_when_no_running_loop(monkeypatch):
    win = _make_window_stub()

    class _DummyTask:
        pass

    class _DummyLoop:
        def __init__(self) -> None:
            self.created = False

        def create_task(self, coro):
            self.created = True
            coro.close()
            return _DummyTask()

    dummy_loop = _DummyLoop()

    def _raise_no_running_loop():
        raise RuntimeError("no running event loop")

    monkeypatch.setattr(asyncio, "get_running_loop", _raise_no_running_loop)
    monkeypatch.setattr(asyncio, "get_event_loop", lambda: dummy_loop)

    async def _noop() -> None:
        return None

    task = FamiliarWindow._create_task(win, _noop())
    assert isinstance(task, _DummyTask)
    assert dummy_loop.created is True


def test_chatlog_uses_configured_labels_for_user_and_agent_prefixes() -> None:
    log, captured = _make_chat_log_stub(agent_label="ゆきね", companion_label="コウタ")

    ChatLog.append_line(log, "[コウタ] こんにちは")
    ChatLog.append_line(log, "[ゆきね] おはよう")

    assert captured[0][0] == "こんにちは"
    assert captured[0][1]["prefix"] == "コウタ"
    assert captured[1][0] == "おはよう"
    assert captured[1][1]["prefix"] == "ゆきね"


def test_chatlog_accepts_legacy_you_agent_markers_with_custom_labels() -> None:
    log, captured = _make_chat_log_stub(agent_label="ゆきね", companion_label="コウタ")

    ChatLog.append_line(log, "[You] legacy user")
    ChatLog.append_line(log, "[Agent] legacy agent")

    assert captured[0][0] == "legacy user"
    assert captured[0][1]["prefix"] == "コウタ"
    assert captured[1][0] == "legacy agent"
    assert captured[1][1]["prefix"] == "ゆきね"


def test_gui_on_send_uses_companion_display_name() -> None:
    win = _make_window_stub()
    win._input = MagicMock()
    win._input.text.return_value = "hello"
    win._input.clear = MagicMock()

    FamiliarWindow._on_send(win)

    win._log.append_line.assert_called_once_with("[Kota] hello")
