"""Tests for the task-mode CLI entry point."""

from __future__ import annotations

from typing import Any

import pytest

from familiar_runtime.models import ModelTurnResult


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


class _TaskBackend:
    def make_user_message(self, content: str | list[Any]) -> dict[str, Any]:
        return {"role": "user", "content": content}

    def make_assistant_message(
        self,
        result: ModelTurnResult,
        raw_content: Any | None = None,
    ) -> dict[str, Any]:
        return {"role": "assistant", "content": result.text}

    def make_tool_results(self, tool_calls, results):
        return [{"role": "tool", "content": text} for text, _image in results]

    async def stream_turn(self, **kwargs):
        return ModelTurnResult(stop_reason="end_turn", text="task done"), None

    async def complete(self, prompt: str, max_tokens: int) -> str:
        return ""


@pytest.mark.asyncio
async def test_run_task_command_creates_durable_task_record(tmp_path, monkeypatch, capsys) -> None:
    from familiar_agent import main as main_mod
    from familiar_agent import backend as backend_mod
    from familiar_runtime.tasks import SQLiteTaskStore, TaskStatus

    # Path.home() consults HOME on POSIX and USERPROFILE on Windows, so set
    # both to keep this test green on every CI runner.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("PLATFORM", "cli")
    monkeypatch.setattr(backend_mod, "create_backend", lambda config: _TaskBackend())

    await main_mod._run_task_command(["inspect", "repo"])

    captured = capsys.readouterr()
    assert "task done" in captured.out
    db_path = tmp_path / ".familiar_ai" / "runtime_tasks.db"
    store = SQLiteTaskStore(db_path)
    rows = store._conn.execute("SELECT id FROM runtime_tasks").fetchall()
    task = store.get_task(rows[0]["id"])
    checkpoints = store.checkpoints_for_task(rows[0]["id"])
    store.close()

    assert task is not None
    assert task.status == TaskStatus.SUCCEEDED
    assert checkpoints
