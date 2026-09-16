"""Delegated background tasks — the secretary actually does the legwork.

"Look into X for me" mid-conversation spawns an independent, non-embodied
task-mode :class:`AgentRuntime` (the same construction as ``familiar task``,
minus MCP) in a background asyncio task. The conversation continues
unblocked. When the task finishes or fails, a *due* follow-up commitment is
created, so the existing turn-context surfacing and proactive-reminder
machinery deliver the report — even if the companion has stepped away.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from familiar_runtime.commitments.model import CommitmentKind

if TYPE_CHECKING:
    from familiar_runtime.commitments import SQLiteCommitmentStore

    from ..config import AgentConfig

logger = logging.getLogger(__name__)

# At most this many delegated tasks run at once: they share the model
# backend's rate limits with the live conversation.
MAX_CONCURRENT_DELEGATED = 2

# Recent results kept for check_delegated_tasks (id -> record).
_RESULT_WINDOW = 10

_DELEGATED_SYSTEM_PROMPT = (
    "You are familiar task mode: a non-embodied task execution agent working "
    "on a goal delegated from a live conversation. Use coding tools when "
    "useful. Do not assume camera, voice, mobility, or neighbor-only state "
    "exists. If bash is not listed as a tool, do not claim you can run shell "
    "commands. Finish with a concise, self-contained summary of findings or "
    "actions taken — it will be relayed to the companion verbatim."
)

ExecuteFn = Callable[[str], Awaitable[tuple[bool, str, str]]]


class DelegatedTaskRunner:
    """Run delegated goals in the background and report back via commitments."""

    def __init__(
        self,
        *,
        config: AgentConfig,
        commitment_store: SQLiteCommitmentStore,
        execute: ExecuteFn | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._config = config
        self._commitments = commitment_store
        self._execute = execute or self._execute_task
        self._clock = clock
        self._running: dict[str, asyncio.Task[None]] = {}
        self._results: OrderedDict[str, dict[str, Any]] = OrderedDict()

    # ── public API ──

    def active_count(self) -> int:
        return sum(1 for t in self._running.values() if not t.done())

    def delegate(self, goal: str) -> str:
        """Start a background run for ``goal``; returns a short handle id.

        Raises ValueError on an empty goal and RuntimeError when the
        concurrency cap is reached.
        """
        goal = goal.strip()
        if not goal:
            raise ValueError("goal is required")
        if self.active_count() >= MAX_CONCURRENT_DELEGATED:
            raise RuntimeError(
                f"already running {MAX_CONCURRENT_DELEGATED} delegated tasks — "
                "wait for one to finish before delegating more"
            )
        handle = uuid.uuid4().hex[:8]
        self._results[handle] = {"goal": goal, "status": "running", "result": ""}
        self._trim_results()
        task = asyncio.get_running_loop().create_task(self._run(handle, goal))
        self._running[handle] = task
        task.add_done_callback(lambda _t: self._running.pop(handle, None))
        return handle

    def status_report(self) -> str:
        if not self._results:
            return "No delegated tasks."
        lines = []
        for handle, rec in reversed(self._results.items()):
            line = f"- [{handle}] {rec['status']}: {rec['goal'][:120]}"
            if rec["result"]:
                line += f"\n  → {rec['result'][:600]}"
            lines.append(line)
        return "\n".join(lines)

    async def wait_idle(self) -> None:
        """Wait for all running delegated tasks to finish (tests, shutdown)."""
        tasks = [t for t in self._running.values() if not t.done()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def shutdown(self) -> None:
        for task in self._running.values():
            if not task.done():
                task.cancel()
        await self.wait_idle()
        self._running.clear()

    # ── internals ──

    def _trim_results(self) -> None:
        while len(self._results) > _RESULT_WINDOW:
            self._results.popitem(last=False)

    async def _run(self, handle: str, goal: str) -> None:
        ok = False
        report = ""
        task_id = ""
        try:
            ok, report, task_id = await self._execute(goal)
        except asyncio.CancelledError:
            self._record(handle, status="cancelled", result="")
            raise
        except Exception as exc:  # noqa: BLE001
            report = str(exc)
            logger.warning("Delegated task failed: %s", exc)
        self._record(handle, status="done" if ok else "failed", result=report[:2000])
        self._create_followup(goal, ok=ok, report=report, task_id=task_id)

    def _record(self, handle: str, *, status: str, result: str) -> None:
        rec = self._results.get(handle)
        if rec is not None:
            rec["status"] = status
            rec["result"] = result

    def _create_followup(self, goal: str, *, ok: bool, report: str, task_id: str) -> None:
        # Quoted so the task agent's output reads as data, not as part of the
        # surfaced commitment line it gets embedded into.
        gist = " ".join(report.split())[:140]
        if ok:
            summary = f'Report back: delegated task finished — {goal[:80]}: "{gist}"'
        else:
            summary = f'Tell the companion the delegated task failed — {goal[:80]}: "{gist}"'
        try:
            self._commitments.create(
                summary=summary[:300],
                kind=CommitmentKind.FOLLOWUP,
                due_at=self._clock(),
                priority=1 if ok else 2,
                created_by="delegation",
                metadata={"task_id": task_id, "ok": ok},
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to create follow-up commitment: %s", exc)

    async def _execute_task(self, goal: str) -> tuple[bool, str, str]:
        """Run the goal on a fresh non-embodied task runtime.

        Mirrors the ``familiar task`` CLI construction minus MCP (a second
        in-process MCP manager would respawn server subprocesses) and minus
        the event bus (no console to stream to).
        """
        from familiar_capabilities import CodingCapability
        from familiar_runtime.models import ModelBackend
        from familiar_runtime.runtime import AgentRuntime
        from familiar_runtime.tasks import SQLiteTaskStore, TaskStatus, TaskToolProvider
        from familiar_runtime.tools.registry import ToolRegistry

        from ..backend import create_backend
        from .coding import CodingTool

        backend = cast("ModelBackend", create_backend(self._config))
        registry = ToolRegistry()
        registry.register(CodingCapability(CodingTool(self._config.coding)))

        task_dir = Path.home() / ".familiar_ai"
        task_dir.mkdir(parents=True, exist_ok=True)
        task_store = SQLiteTaskStore(task_dir / "runtime_tasks.db")
        try:
            task = task_store.create_task(
                title=goal[:80] or "Delegated task",
                description=goal,
                goal=goal,
                acceptance_criteria=["Provide a final summary with actions taken and evidence."],
            )
            task_store.update_status(task.id, TaskStatus.RUNNING)
            registry.register(TaskToolProvider(task_store))
            try:
                runtime = AgentRuntime(backend=backend, tools=registry)
                result = await runtime.run_turn(
                    goal,
                    profile="task",
                    task_id=task.id,
                    system_prompt=_DELEGATED_SYSTEM_PROMPT,
                    max_tokens=self._config.max_tokens,
                )
            except Exception as exc:
                task_store.update_status(task.id, TaskStatus.FAILED, error=str(exc))
                raise
            task_store.update_status(
                task.id, TaskStatus.SUCCEEDED, evidence=result.final_text[:500]
            )
            return True, result.final_text, task.id
        finally:
            task_store.close()


class DelegationTool:
    """Expose delegated background tasks to the conversational agent."""

    def __init__(self, runner: DelegatedTaskRunner) -> None:
        self.runner = runner

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "delegate_task",
                "description": (
                    "Delegate a research or coding goal to a background task agent. "
                    "It runs independently while the conversation continues; when it "
                    "finishes, a due follow-up commitment is created so you can "
                    "report the result. Use when the companion asks you to look "
                    "into something that would take a while — do NOT block the "
                    "conversation doing it yourself."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": (
                                "Self-contained goal statement with all context the "
                                "background agent needs (it cannot see this conversation)."
                            ),
                        },
                    },
                    "required": ["goal"],
                },
            },
            {
                "name": "check_delegated_tasks",
                "description": (
                    "List running and recently finished delegated background tasks "
                    "with their results."
                ),
                "input_schema": {"type": "object", "properties": {}},
            },
        ]

    async def call(self, name: str, tool_input: dict) -> tuple[str, None]:
        if name == "delegate_task":
            goal = str(tool_input.get("goal", "")).strip()
            try:
                handle = self.runner.delegate(goal)
            except (ValueError, RuntimeError) as exc:
                return f"Error: {exc}", None
            return (
                f"Delegated [{handle}]: {goal[:120]} — running in the background. "
                "A follow-up will surface when it finishes; you can also call "
                "check_delegated_tasks.",
                None,
            )
        if name == "check_delegated_tasks":
            return self.runner.status_report(), None
        return f"Error: unknown delegation tool '{name}'", None
