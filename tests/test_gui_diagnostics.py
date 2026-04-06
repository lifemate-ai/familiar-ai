from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from familiar_agent.diagnostics import build_gui_diagnostics, format_gui_diagnostics
from familiar_agent.gui import FamiliarWindow


def test_build_gui_diagnostics_reports_stt_gated_and_last_error() -> None:
    window = SimpleNamespace(
        _agent=None,
        _config=SimpleNamespace(
            platform="anthropic",
            model="claude-sonnet-4-6",
            utility_platform="openai",
            utility_model="gpt-4o-mini",
            scene_platform="openai",
            scene_model="gpt-4o-mini",
        ),
        _startup_status="Ready",
        _agent_ready=True,
        _agent_running=False,
        _agent_init_failed=False,
        _last_error="boom",
        _realtime_stt=SimpleNamespace(connected=True, gated=True),
        _input_queue=SimpleNamespace(qsize=lambda: 2),
    )

    snapshot = build_gui_diagnostics(window)

    assert snapshot.phase == "stt_gated"
    assert snapshot.realtime_stt_gated is True
    assert snapshot.queue_backlog == 2
    assert snapshot.last_error == "boom"


def test_format_gui_diagnostics_includes_readiness_and_error() -> None:
    snapshot = build_gui_diagnostics(
        SimpleNamespace(
            _agent=None,
            _config=SimpleNamespace(
                platform="anthropic",
                model="claude-sonnet-4-6",
                utility_platform="",
                utility_model="",
                scene_platform="",
                scene_model="",
            ),
            _startup_status="Initializing agent...",
            _agent_ready=False,
            _agent_running=False,
            _agent_init_failed=False,
            _last_error="missing key",
            _realtime_stt=SimpleNamespace(connected=False, gated=False),
            _input_queue=SimpleNamespace(qsize=lambda: 0),
        )
    )

    rendered = format_gui_diagnostics(snapshot)

    assert "readiness:" in rendered
    assert "last_error: missing key" in rendered


def test_gui_copy_diagnostics_uses_clipboard(monkeypatch) -> None:
    captured: dict[str, str] = {}
    clipboard = SimpleNamespace(setText=lambda text: captured.setdefault("text", text))
    monkeypatch.setattr("familiar_agent.gui.QApplication.clipboard", lambda: clipboard)

    win = FamiliarWindow.__new__(FamiliarWindow)
    win._agent = None
    win._config = SimpleNamespace(
        platform="anthropic",
        model="claude-sonnet-4-6",
        utility_platform="",
        utility_model="",
        scene_platform="",
        scene_model="",
    )
    win._startup_status = "Ready"
    win._agent_ready = True
    win._agent_running = False
    win._agent_init_failed = False
    win._last_error = ""
    win._realtime_stt = SimpleNamespace(connected=False, gated=False)
    win._input_queue = SimpleNamespace(qsize=lambda: 0)
    win._log = MagicMock()

    FamiliarWindow._copy_diagnostics(win)

    assert "familiar-ai diagnostics" in captured["text"]
    win._log.append_line.assert_called_once_with("📋 Diagnostics copied")
