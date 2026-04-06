from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from familiar_agent.bootstrap import AppBootstrap
from familiar_agent.gui import FamiliarWindow


def test_main_gui_path_defers_agent_construction(monkeypatch) -> None:
    import familiar_agent.main as main_mod

    calls: list[object] = []

    class _FakeConfig:
        companion_name = "Kota"

    monkeypatch.setattr(main_mod, "setup_logging", lambda debug=False: None)
    monkeypatch.setattr(
        main_mod,
        "load_app_bootstrap",
        lambda env_path=None: AppBootstrap(
            env_path=Path(".env"),
            configured=True,
            needs_setup=False,
            legacy_config_detected=False,
        ),
    )
    monkeypatch.setattr(main_mod, "AgentConfig", lambda: _FakeConfig())
    monkeypatch.setattr(
        main_mod, "DesireSystem", lambda companion_name=None: ("desires", companion_name)
    )

    def _unexpected_agent(_config):
        raise AssertionError("EmbodiedAgent should not be constructed on the GUI path")

    monkeypatch.setattr(main_mod, "EmbodiedAgent", _unexpected_agent)

    import familiar_agent.gui as gui_mod

    monkeypatch.setattr(gui_mod, "run_gui", lambda config, desires: calls.append((config, desires)))
    monkeypatch.setattr(main_mod.sys, "argv", ["familiar", "--gui"])

    main_mod.main()

    assert len(calls) == 1
    config, desires = calls[0]
    assert isinstance(config, _FakeConfig)
    assert desires == ("desires", "Kota")


@pytest.mark.asyncio
async def test_initialize_agent_builds_agent_in_background(monkeypatch) -> None:
    class _FakeAgent:
        def __init__(self, config) -> None:
            self.config = config
            self.is_embedding_ready = True

    monkeypatch.setattr("familiar_agent.agent.EmbodiedAgent", _FakeAgent)

    win = FamiliarWindow.__new__(FamiliarWindow)
    win._config = SimpleNamespace(agent_name="Yukine", companion_name="Kota")
    win._agent = None
    win._desires = object()
    win._agent_ready = False
    win._agent_init_failed = False
    win._agent_running = False
    win._closing = False
    win._startup_status = ""
    win._realtime_stt = None
    win._realtime_stt_task = None
    win._stream = SimpleNamespace(
        has_content=lambda: False,
        set_status=lambda text: None,
        clear_status=lambda: None,
    )
    win._log = SimpleNamespace(append_line=lambda text: None)
    win._input = SimpleNamespace(setEnabled=lambda enabled: setattr(win, "_input_enabled", enabled))
    win._send_btn = SimpleNamespace(
        setEnabled=lambda enabled: setattr(win, "_send_enabled", enabled)
    )
    win.setWindowTitle = lambda title: setattr(win, "_title", title)  # type: ignore[method-assign]
    win._create_task = lambda coro: asyncio.create_task(coro)  # type: ignore[method-assign]

    async def _noop_show_init_status() -> None:
        return None

    win._show_init_status = _noop_show_init_status  # type: ignore[method-assign]

    await FamiliarWindow._initialize_agent(win)

    assert isinstance(win._agent, _FakeAgent)
    assert win._agent_ready is True
    assert win._agent_init_failed is False
    assert win._input_enabled is True
    assert win._send_enabled is True
