"""Tests for the durable runtime task store."""

from __future__ import annotations

import pytest

from familiar_runtime.tasks import SQLiteTaskStore, TaskStatus, TaskToolProvider
from familiar_runtime.tools import SandboxPolicy


def test_task_store_creates_updates_checkpoints_and_reloads(tmp_path) -> None:
    db_path = tmp_path / "tasks.db"
    store = SQLiteTaskStore(db_path)
    task = store.create_task(
        title="Inspect repo",
        description="Run characterization",
        goal="green tests",
        acceptance_criteria=["pytest passes"],
    )
    store.update_status(task.id, TaskStatus.RUNNING)
    checkpoint = store.checkpoint_task(
        task.id,
        summary="Tests started",
        state={"command": "pytest"},
    )
    store.update_status(task.id, TaskStatus.SUCCEEDED, evidence="pytest passed")
    store.close()

    reopened = SQLiteTaskStore(db_path)
    loaded = reopened.get_task(task.id)
    checkpoints = reopened.checkpoints_for_task(task.id)
    reopened.close()

    assert loaded is not None
    assert loaded.status == TaskStatus.SUCCEEDED
    assert loaded.acceptance_criteria == ["pytest passes"]
    assert loaded.metadata["evidence"] == "pytest passed"
    assert [item.id for item in checkpoints] == [checkpoint.id]
    assert checkpoints[0].state == {"command": "pytest"}


def test_sandbox_policy_keeps_bash_disabled_by_default() -> None:
    policy = SandboxPolicy()

    assert policy.allow_bash is False
    assert "shutdown" in policy.denied_commands


@pytest.mark.asyncio
async def test_task_tool_provider_exposes_task_lifecycle(tmp_path) -> None:
    store = SQLiteTaskStore(tmp_path / "tasks.db")
    provider = TaskToolProvider(store)

    created, checkpointed, finished = provider.specs()
    assert [created.name, checkpointed.name, finished.name] == [
        "create_task",
        "checkpoint_task",
        "finish_task",
    ]

    create_result = await provider.call(
        "create_task",
        {
            "title": "runtime",
            "description": "exercise task tools",
            "acceptance_criteria": ["done"],
        },
    )
    task_id = create_result.text.removeprefix("Created task ").removesuffix(".")
    await provider.call(
        "checkpoint_task",
        {"task_id": task_id, "summary": "halfway", "state": {"step": 1}},
    )
    await provider.call("finish_task", {"task_id": task_id, "evidence": "done"})

    task = store.get_task(task_id)
    checkpoints = store.checkpoints_for_task(task_id)
    store.close()

    assert task is not None
    assert task.status == TaskStatus.SUCCEEDED
    assert checkpoints[0].summary == "halfway"
