"""Task management tools exposed through the generic ToolProvider protocol."""

from __future__ import annotations

from typing import Any

from familiar_runtime.tools import ToolExecutionResult, ToolSpec

from .model import TaskStatus
from .store import SQLiteTaskStore


class TaskToolProvider:
    """Expose create/checkpoint/finish operations as runtime tools."""

    def __init__(self, store: SQLiteTaskStore) -> None:
        self._store = store

    def specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(
                name="create_task",
                description="Create a durable task record.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "acceptance_criteria": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["title", "description"],
                },
                category="task",
                tags={"task"},
            ),
            ToolSpec(
                name="checkpoint_task",
                description="Persist a task checkpoint.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "summary": {"type": "string"},
                        "state": {"type": "object"},
                    },
                    "required": ["task_id", "summary", "state"],
                },
                category="task",
                tags={"task"},
            ),
            ToolSpec(
                name="finish_task",
                description="Mark a task succeeded with evidence.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "evidence": {"type": "string"},
                    },
                    "required": ["task_id", "evidence"],
                },
                category="task",
                tags={"task"},
            ),
        ]

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:
        if name == "create_task":
            task = self._store.create_task(
                title=str(tool_input.get("title", "")),
                description=str(tool_input.get("description", "")),
                acceptance_criteria=list(tool_input.get("acceptance_criteria", []) or []),
            )
            return ToolExecutionResult(text=f"Created task {task.id}.")
        if name == "checkpoint_task":
            checkpoint = self._store.checkpoint_task(
                str(tool_input["task_id"]),
                summary=str(tool_input["summary"]),
                state=dict(tool_input.get("state", {})),
            )
            return ToolExecutionResult(text=f"Checkpointed task {checkpoint.task_id}.")
        if name == "finish_task":
            task = self._store.update_status(
                str(tool_input["task_id"]),
                TaskStatus.SUCCEEDED,
                evidence=str(tool_input["evidence"]),
            )
            return ToolExecutionResult(text=f"Finished task {task.id}.")
        return ToolExecutionResult(
            text=f"Unknown task tool: {name}",
            success=False,
            error="unknown_task_tool",
        )
