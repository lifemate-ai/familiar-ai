"""Tests for the durable runtime task store."""

from __future__ import annotations

from familiar_runtime.tasks import SQLiteTaskStore, TaskStatus


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
