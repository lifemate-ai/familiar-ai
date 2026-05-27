"""Tests for the task-mode CLI entry point."""

from __future__ import annotations


def test_main_dispatches_task_subcommand_without_companion_bootstrap(monkeypatch) -> None:
    from familiar_agent import main as main_mod

    called: list[list[str]] = []
    monkeypatch.setattr(main_mod.sys, "argv", ["familiar", "task", "inspect", "repo"])
    monkeypatch.setattr(main_mod, "setup_logging", lambda debug=False: None)
    monkeypatch.setattr(
        main_mod, "load_app_bootstrap", lambda: (_ for _ in ()).throw(AssertionError)
    )
    monkeypatch.setattr(main_mod, "_task_command", lambda args: called.append(args))

    main_mod.main()

    assert called == [["inspect", "repo"]]
