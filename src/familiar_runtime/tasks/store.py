"""SQLite-backed durable task store."""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

from .model import Task, TaskCheckpoint, TaskStatus


class SQLiteTaskStore:
    """Persist tasks and checkpoints in SQLite."""

    def __init__(self, db_path: str | Path) -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS runtime_tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                goal TEXT NOT NULL,
                constraints_json TEXT NOT NULL,
                acceptance_criteria_json TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                metadata_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS runtime_task_checkpoints (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                summary TEXT NOT NULL,
                state_json TEXT NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY(task_id) REFERENCES runtime_tasks(id)
            );
            """
        )
        self._conn.commit()

    def create_task(
        self,
        *,
        title: str,
        description: str,
        goal: str = "",
        constraints: list[str] | None = None,
        acceptance_criteria: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Task:
        now = time.time()
        task = Task(
            id=f"task_{uuid.uuid4().hex}",
            title=title,
            description=description,
            goal=goal,
            constraints=constraints or [],
            acceptance_criteria=acceptance_criteria or [],
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )
        self.save_task(task)
        return task

    def save_task(self, task: Task) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO runtime_tasks (
                id, title, description, status, goal, constraints_json,
                acceptance_criteria_json, created_at, updated_at, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.id,
                task.title,
                task.description,
                task.status.value,
                task.goal,
                json.dumps(task.constraints, ensure_ascii=False),
                json.dumps(task.acceptance_criteria, ensure_ascii=False),
                task.created_at,
                task.updated_at,
                json.dumps(task.metadata, ensure_ascii=False),
            ),
        )
        self._conn.commit()

    def get_task(self, task_id: str) -> Task | None:
        row = self._conn.execute(
            "SELECT * FROM runtime_tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        return self._task_from_row(row) if row else None

    def update_status(self, task_id: str, status: TaskStatus, **metadata: Any) -> Task:
        task = self.get_task(task_id)
        if task is None:
            raise KeyError(f"task not found: {task_id}")
        task.status = status
        task.updated_at = time.time()
        task.metadata.update(metadata)
        self.save_task(task)
        return task

    def checkpoint_task(
        self,
        task_id: str,
        *,
        summary: str,
        state: dict[str, Any],
    ) -> TaskCheckpoint:
        checkpoint = TaskCheckpoint(
            id=f"checkpoint_{uuid.uuid4().hex}",
            task_id=task_id,
            summary=summary,
            state=state,
            created_at=time.time(),
        )
        self._conn.execute(
            """
            INSERT INTO runtime_task_checkpoints (id, task_id, summary, state_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                checkpoint.id,
                checkpoint.task_id,
                checkpoint.summary,
                json.dumps(checkpoint.state, ensure_ascii=False),
                checkpoint.created_at,
            ),
        )
        self._conn.commit()
        return checkpoint

    def checkpoints_for_task(self, task_id: str) -> list[TaskCheckpoint]:
        rows = self._conn.execute(
            """
            SELECT * FROM runtime_task_checkpoints
            WHERE task_id = ?
            ORDER BY created_at, rowid
            """,
            (task_id,),
        ).fetchall()
        return [
            TaskCheckpoint(
                id=row["id"],
                task_id=row["task_id"],
                summary=row["summary"],
                state=json.loads(row["state_json"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def _task_from_row(self, row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            status=TaskStatus(row["status"]),
            goal=row["goal"],
            constraints=json.loads(row["constraints_json"]),
            acceptance_criteria=json.loads(row["acceptance_criteria_json"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            metadata=json.loads(row["metadata_json"]),
        )

    def close(self) -> None:
        self._conn.close()
