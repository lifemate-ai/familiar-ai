"""Regression tests for GUI async stability (burst input, cancel, shutdown)."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections.abc import Callable
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from familiar_agent.gui import (
    ChatLog,
    FamiliarWindow,
    build_testflight_persona,
    needs_testflight_setup,
    resolve_app_icon_path,
)


class _FakeCloseEvent:
    def __init__(self) -> None:
        self.accepted = False
        self.ignored = False

    def accept(self) -> None:
        self.accepted = True

    def ignore(self) -> None:
        self.ignored = True


class _ManualRealtimeStt:
    """Minimal controllable realtime STT session stub for GUI tests."""

    def __init__(self) -> None:
        self.on_partial: Callable[[str], None] | None = None
        self.on_committed: Callable[[str], None] | None = None
        self._queue: asyncio.Queue[str | None] | None = None
        self.started = False

    async def start(
        self, _loop: asyncio.AbstractEventLoop, committed_queue: asyncio.Queue[str | None]
    ) -> None:
        self._queue = committed_queue
        self.started = True

    async def stop(self) -> None:
        self.started = False

    async def emit_committed(self, text: str) -> None:
        assert self._queue is not None
        if self.on_committed:
            self.on_committed(text)
        await self._queue.put(text)


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
    win._look_preview_task = None
    win._look_preview_until = 0.0
    win._look_preview_disabled = False
    win._realtime_stt = None
    win._realtime_stt_task = None
    win._desires = MagicMock()
    win._log = MagicMock()
    win._stream = MagicMock()
    win._stream.has_content.return_value = False
    win._send_btn = MagicMock()
    win._stop_btn = MagicMock()
    win._lag_timer = MagicMock()
    win._last_lag_tick = time.perf_counter()
    win.setEnabled = MagicMock()  # type: ignore[method-assign]
    win.setWindowTitle = MagicMock()  # type: ignore[method-assign]
    win.close = MagicMock()  # type: ignore[method-assign]
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

    log._add_bubble = _capture  # type: ignore[assignment]
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
async def test_gui_realtime_stt_callbacks_log_and_enqueue_text():
    win = _make_window_stub()
    fake_stt = _ManualRealtimeStt()
    win._realtime_stt = fake_stt  # type: ignore[assignment]

    await FamiliarWindow._start_realtime_stt(win)

    assert fake_stt.started is True
    assert fake_stt.on_partial is not None
    assert fake_stt.on_committed is not None
    win._log.append_line.assert_any_call("🎤 Realtime STT ON (ElevenLabs)")

    fake_stt.on_partial("testing partial")
    win._stream.set_status.assert_called_with("🎤 testing partial")

    await fake_stt.emit_committed("voice hello")
    win._stream.clear_status.assert_called()
    win._log.append_line.assert_any_call("[Kota] voice hello")
    assert await asyncio.wait_for(win._input_queue.get(), timeout=0.5) == "voice hello"


@pytest.mark.asyncio
async def test_gui_realtime_stt_init_failure_sets_session_none():
    win = _make_window_stub()

    class _FailRealtimeStt:
        on_partial = None
        on_committed = None

        async def start(self, _loop: asyncio.AbstractEventLoop, _queue) -> None:
            raise RuntimeError("boom")

    win._realtime_stt = _FailRealtimeStt()  # type: ignore[assignment]

    await FamiliarWindow._start_realtime_stt(win)

    assert win._realtime_stt is None
    win._log.append_line.assert_any_call("[error] Realtime STT init failed: boom")


@pytest.mark.asyncio
async def test_gui_idle_desire_logs_localized_murmur(monkeypatch):
    win = _make_window_stub()

    async def _fake_run_agent(text: str, inner_voice: str = "") -> None:
        assert text == ""
        assert inner_voice == "inner-prompt"

    win._run_agent = _fake_run_agent  # type: ignore[method-assign]

    call_count = {"n": 0}

    async def _fake_wait_for(awaitable, timeout):
        # _process_queue passes queue.get() coroutine each loop; close it here
        # because this fake doesn't await it.
        if hasattr(awaitable, "close"):
            awaitable.close()
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise asyncio.TimeoutError
        return None

    monkeypatch.setattr("familiar_agent.gui.asyncio.wait_for", _fake_wait_for)
    monkeypatch.setattr(
        "familiar_agent.gui.should_fire_idle_desire",
        lambda **kwargs: True,
    )
    monkeypatch.setattr(
        "familiar_agent.gui.desire_tick_prompt",
        lambda _desires, _peek: ("worry_companion", "inner-prompt", None),
    )
    monkeypatch.setattr(
        "familiar_agent.gui._t",
        lambda key, **kwargs: (
            "localized-worry" if key == "desire_worry_companion" else "localized-default"
        ),
    )

    await FamiliarWindow._process_queue(win)

    win._log.append_line.assert_called_with("localized-worry")
    win._desires.satisfy.assert_called_once_with("worry_companion")


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

    assert isinstance(win._log, MagicMock)
    win._log.append_line.assert_called_once_with("[Kota] hello")


def test_gui_thinking_status_text_uses_i18n_and_agent_display_name(monkeypatch) -> None:
    win = _make_window_stub()
    win._agent_display_name = "Yukine"

    def _fake_t(key: str, **kwargs: str) -> str:
        assert key == "thinking_status"
        assert kwargs["name"] == "Yukine"
        return f"{kwargs['name']}:::{kwargs['seconds']}"

    monkeypatch.setattr("familiar_agent.gui._t", _fake_t)

    assert FamiliarWindow._thinking_status_text(win, 0) == "Yukine:::0"
    assert FamiliarWindow._thinking_status_text(win, 7) == "Yukine:::7"


def test_testflight_persona_builder_uses_structured_fields() -> None:
    text = build_testflight_persona(
        agent_name="エージェントA",
        companion_name="ユーザーB",
        companion_profile="夜に作業することが多い。",
        agent_profile="観察を重視して短く話す。",
        relationship="日常的に会話する相棒。",
    )
    assert "名前：エージェントA" in text
    assert "- 名前：ユーザーB" in text
    assert "- 設定：夜に作業することが多い。" in text
    assert "観察を重視して短く話す。" in text
    assert "日常的に会話する相棒。" in text


def test_needs_testflight_setup_depends_on_flag_camera_and_persona(tmp_path) -> None:
    cfg = SimpleNamespace(
        testflight_mode=True,
        camera=SimpleNamespace(host="192.168.0.2", username="admin", password="secret"),
    )
    persona = tmp_path / "ME.md"
    persona.write_text("persona", encoding="utf-8")

    assert needs_testflight_setup(cfg, setup_flag="true", persona_path=persona) is False
    assert needs_testflight_setup(cfg, setup_flag="false", persona_path=persona) is True

    cfg_missing_cam = SimpleNamespace(
        testflight_mode=True,
        camera=SimpleNamespace(host="", username="admin", password="secret"),
    )
    assert needs_testflight_setup(cfg_missing_cam, setup_flag="true", persona_path=persona) is True

    cfg_off = SimpleNamespace(
        testflight_mode=False,
        camera=SimpleNamespace(host="", username="", password=""),
    )
    assert needs_testflight_setup(cfg_off, setup_flag="false", persona_path=persona) is False


def test_resolve_app_icon_path_prefers_env_relative_to_runtime_dir(monkeypatch, tmp_path) -> None:
    icon = tmp_path / "custom.ico"
    icon.write_bytes(b"ico")
    monkeypatch.setenv("FAMILIAR_APP_ICON", "custom.ico")
    monkeypatch.setattr("familiar_agent.gui._runtime_base_dir", lambda: tmp_path)

    assert resolve_app_icon_path() == icon


def test_gui_build_rtsp_url_encodes_credentials_and_supports_raw_url() -> None:
    built = FamiliarWindow._build_rtsp_url("192.168.0.10", "user name", "p@ss")
    assert built == "rtsp://user%20name:p%40ss@192.168.0.10:554/stream1"

    raw = FamiliarWindow._build_rtsp_url("rtsp://camera.local/stream1", "u", "p")
    assert raw == "rtsp://camera.local/stream1"


def test_gui_look_preview_seconds_are_clamped() -> None:
    assert FamiliarWindow._look_preview_seconds_for_degrees(5) >= 0.8
    assert FamiliarWindow._look_preview_seconds_for_degrees(90) <= 2.0
    assert FamiliarWindow._look_preview_seconds_for_degrees(None) >= 0.8


def test_gui_extract_jpeg_frames_parses_multiple_frames() -> None:
    frame1 = b"\xff\xd8abc\xff\xd9"
    frame2 = b"\xff\xd8xyz\xff\xd9"
    buf = bytearray(b"noise" + frame1 + b"junk" + frame2 + b"tail")

    frames = FamiliarWindow._extract_jpeg_frames(buf, max_frames=2)

    assert frames == [frame1, frame2]
    assert buf.startswith(b"tail")


def test_gui_request_look_preview_starts_task_and_extends_deadline(monkeypatch):
    win = _make_window_stub()
    win._camera_rtsp_url = lambda: "rtsp://camera/stream1"  # type: ignore[method-assign]

    class _DummyTask:
        def done(self) -> bool:
            return False

    created: list[object] = []

    def _fake_create_task(coro):
        created.append(coro)
        coro.close()
        return _DummyTask()

    win._create_task = _fake_create_task  # type: ignore[method-assign]

    ts = iter([10.0, 10.4])
    monkeypatch.setattr(time, "perf_counter", lambda: next(ts))

    FamiliarWindow._request_look_preview(win, 20)
    first_until = win._look_preview_until
    FamiliarWindow._request_look_preview(win, 90)

    assert win._look_preview_task is not None
    assert len(created) == 1
    assert win._look_preview_until > first_until
