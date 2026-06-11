"""Delegated background tasks: "調べといて" runs while the conversation continues.

`delegate_task` spawns an independent, non-embodied task-mode runtime in the
background. When it finishes (or fails), a due follow-up commitment is created
so the existing proactive-reminder machinery delivers the report — even if the
companion has stepped away.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_agent.tools.delegation import DelegatedTaskRunner, DelegationTool
from familiar_runtime.commitments import SQLiteCommitmentStore
from familiar_runtime.commitments.model import CommitmentKind


@pytest.fixture
def commitments(tmp_path):
    store = SQLiteCommitmentStore(tmp_path / "commitments.db")
    yield store
    store.close()


def _runner(commitments, execute):
    return DelegatedTaskRunner(
        config=MagicMock(),
        commitment_store=commitments,
        execute=execute,
    )


async def _drain(runner):
    await runner.wait_idle()


# ── Runner: completion -> follow-up commitment ──


@pytest.mark.asyncio
async def test_success_creates_due_followup_commitment(commitments):
    execute = AsyncMock(return_value=(True, "Found 3 papers; summary attached.", "task-1"))
    runner = _runner(commitments, execute)

    handle = runner.delegate("survey recent ToM papers")
    assert handle
    await _drain(runner)

    open_items = commitments.list_open()
    assert len(open_items) == 1
    c = open_items[0]
    assert c.kind is CommitmentKind.FOLLOWUP
    assert c.due_at is not None and c.is_due(now=c.due_at + 1)
    assert "survey recent ToM papers"[:40] in c.summary
    assert c.priority == 1
    assert c.created_by == "delegation"
    assert c.metadata.get("task_id") == "task-1"
    assert c.metadata.get("ok") is True


@pytest.mark.asyncio
async def test_failure_creates_higher_priority_commitment(commitments):
    execute = AsyncMock(side_effect=RuntimeError("backend exploded"))
    runner = _runner(commitments, execute)

    runner.delegate("doomed goal")
    await _drain(runner)

    open_items = commitments.list_open()
    assert len(open_items) == 1
    c = open_items[0]
    assert c.priority == 2
    assert "failed" in c.summary.lower()
    assert c.metadata.get("ok") is False


@pytest.mark.asyncio
async def test_result_text_available_in_status_report(commitments):
    execute = AsyncMock(return_value=(True, "The answer is 42.", "task-9"))
    runner = _runner(commitments, execute)

    runner.delegate("compute the answer")
    await _drain(runner)

    report = runner.status_report()
    assert "compute the answer" in report
    assert "The answer is 42." in report


@pytest.mark.asyncio
async def test_running_task_shows_as_running(commitments):
    gate = asyncio.Event()

    async def execute(goal):
        await gate.wait()
        return True, "done", "task-1"

    runner = _runner(commitments, execute)
    runner.delegate("slow goal")
    try:
        assert runner.active_count() == 1
        assert "running" in runner.status_report()
    finally:
        gate.set()
        await _drain(runner)
    assert runner.active_count() == 0


# ── Runner: guards ──


@pytest.mark.asyncio
async def test_concurrency_cap(commitments):
    gate = asyncio.Event()

    async def execute(goal):
        await gate.wait()
        return True, "done", "t"

    runner = _runner(commitments, execute)
    runner.delegate("one")
    runner.delegate("two")
    with pytest.raises(RuntimeError):
        runner.delegate("three")
    gate.set()
    await _drain(runner)
    # Slots free up after completion
    runner.delegate("four")
    await _drain(runner)


@pytest.mark.asyncio
async def test_empty_goal_rejected(commitments):
    runner = _runner(commitments, AsyncMock())
    with pytest.raises(ValueError):
        runner.delegate("   ")


@pytest.mark.asyncio
async def test_shutdown_cancels_running_tasks(commitments):
    gate = asyncio.Event()

    async def execute(goal):
        await gate.wait()
        return True, "done", "t"

    runner = _runner(commitments, execute)
    runner.delegate("will be cancelled")
    await runner.shutdown()
    assert runner.active_count() == 0


@pytest.mark.asyncio
async def test_commitment_store_failure_does_not_raise(commitments):
    execute = AsyncMock(return_value=(True, "done", "t"))
    broken = MagicMock()
    broken.create = MagicMock(side_effect=RuntimeError("db locked"))
    runner = DelegatedTaskRunner(config=MagicMock(), commitment_store=broken, execute=execute)

    runner.delegate("goal")
    await _drain(runner)  # must not raise; failure is logged

    assert "goal" in runner.status_report()


# ── Tool: definitions and calls ──


@pytest.mark.asyncio
async def test_tool_definitions():
    runner = DelegatedTaskRunner(
        config=MagicMock(), commitment_store=MagicMock(), execute=AsyncMock()
    )
    tool = DelegationTool(runner)
    defs = {d["name"]: d for d in tool.get_tool_definitions()}
    assert "delegate_task" in defs
    assert "check_delegated_tasks" in defs
    assert "goal" in defs["delegate_task"]["input_schema"]["properties"]
    assert "goal" in defs["delegate_task"]["input_schema"]["required"]


@pytest.mark.asyncio
async def test_delegate_tool_call_confirms(commitments):
    execute = AsyncMock(return_value=(True, "done", "t"))
    runner = _runner(commitments, execute)
    tool = DelegationTool(runner)

    text, image = await tool.call("delegate_task", {"goal": "research something"})

    assert image is None
    assert "research something" in text
    assert "background" in text.lower()
    await _drain(runner)


@pytest.mark.asyncio
async def test_delegate_tool_cap_returns_error_string(commitments):
    gate = asyncio.Event()

    async def execute(goal):
        await gate.wait()
        return True, "done", "t"

    runner = _runner(commitments, execute)
    tool = DelegationTool(runner)
    await tool.call("delegate_task", {"goal": "one"})
    await tool.call("delegate_task", {"goal": "two"})

    text, _ = await tool.call("delegate_task", {"goal": "three"})

    assert "error" in text.lower() or "already" in text.lower()
    gate.set()
    await _drain(runner)


@pytest.mark.asyncio
async def test_empty_goal_tool_call_returns_error_string():
    runner = DelegatedTaskRunner(
        config=MagicMock(), commitment_store=MagicMock(), execute=AsyncMock()
    )
    tool = DelegationTool(runner)
    text, _ = await tool.call("delegate_task", {"goal": ""})
    assert "error" in text.lower()


@pytest.mark.asyncio
async def test_check_tool_reports_status(commitments):
    execute = AsyncMock(return_value=(True, "all done", "t"))
    runner = _runner(commitments, execute)
    tool = DelegationTool(runner)
    await tool.call("delegate_task", {"goal": "some goal"})
    await _drain(runner)

    text, _ = await tool.call("check_delegated_tasks", {})
    assert "some goal" in text
    assert "all done" in text


@pytest.mark.asyncio
async def test_check_tool_empty():
    runner = DelegatedTaskRunner(
        config=MagicMock(), commitment_store=MagicMock(), execute=AsyncMock()
    )
    tool = DelegationTool(runner)
    text, _ = await tool.call("check_delegated_tasks", {})
    assert "no delegated tasks" in text.lower()


# ── Real _execute_task path: backend faked, task store real ──


class _FakeBackend:
    def __init__(self, *, fail: bool = False) -> None:
        self._fail = fail

    def make_user_message(self, content):
        return {"role": "user", "content": content}

    def make_assistant_message(self, result, raw_content=None):
        return {"role": "assistant", "content": result.text}

    def make_tool_results(self, tool_calls, results):
        return [{"role": "tool", "content": text} for text, _image in results]

    async def stream_turn(self, **kwargs):
        from familiar_runtime.models import ModelTurnResult

        if self._fail:
            raise RuntimeError("model unavailable")
        return ModelTurnResult(stop_reason="end_turn", text="background task done"), None

    async def complete(self, prompt: str, max_tokens: int) -> str:
        return ""


@pytest.fixture
def _task_home(tmp_path, monkeypatch):
    # Path.home() consults HOME on POSIX and USERPROFILE on Windows.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("PLATFORM", "cli")
    return tmp_path


@pytest.mark.asyncio
async def test_execute_task_real_path_succeeds(_task_home, monkeypatch, commitments):
    from familiar_agent import backend as backend_mod
    from familiar_agent.config import AgentConfig
    from familiar_runtime.tasks import SQLiteTaskStore, TaskStatus

    monkeypatch.setattr(backend_mod, "create_backend", lambda config: _FakeBackend())
    runner = DelegatedTaskRunner(config=AgentConfig(), commitment_store=commitments)

    runner.delegate("summarize the repo")
    await runner.wait_idle()

    open_items = commitments.list_open()
    assert len(open_items) == 1
    assert open_items[0].priority == 1
    task_id = open_items[0].metadata["task_id"]
    assert task_id

    store = SQLiteTaskStore(_task_home / ".familiar_ai" / "runtime_tasks.db")
    try:
        task = store.get_task(task_id)
    finally:
        store.close()
    assert task is not None
    assert task.status == TaskStatus.SUCCEEDED
    assert "background task done" in runner.status_report()


@pytest.mark.asyncio
async def test_execute_task_failure_marks_task_failed(_task_home, monkeypatch, commitments):
    from familiar_agent import backend as backend_mod
    from familiar_agent.config import AgentConfig
    from familiar_runtime.tasks import SQLiteTaskStore, TaskStatus

    monkeypatch.setattr(backend_mod, "create_backend", lambda config: _FakeBackend(fail=True))
    runner = DelegatedTaskRunner(config=AgentConfig(), commitment_store=commitments)

    runner.delegate("doomed real goal")
    await runner.wait_idle()

    open_items = commitments.list_open()
    assert len(open_items) == 1
    assert open_items[0].priority == 2
    assert "failed" in open_items[0].summary.lower()

    store = SQLiteTaskStore(_task_home / ".familiar_ai" / "runtime_tasks.db")
    try:
        rows = store._conn.execute("SELECT id FROM runtime_tasks").fetchall()
        task = store.get_task(rows[0]["id"])
    finally:
        store.close()
    assert task is not None
    assert task.status == TaskStatus.FAILED


# ── Agent wiring: registry exposes the delegation tools ──


def test_agent_registry_includes_delegation_tools():
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._camera = None
    agent._mobility = None
    agent._tts = None
    agent._mcp = None
    for attr in ("_memory_tool", "_tom_tool", "_coding"):
        stub = MagicMock()
        stub.get_tool_definitions = MagicMock(return_value=[])
        setattr(agent, attr, stub)
    agent._exploration = MagicMock()

    runner = DelegatedTaskRunner(
        config=MagicMock(), commitment_store=MagicMock(), execute=AsyncMock()
    )
    agent._delegation_tool = DelegationTool(runner)

    names = {d["name"] for d in agent._all_tool_defs}
    assert "delegate_task" in names
    assert "check_delegated_tasks" in names


def test_agent_registry_survives_missing_delegation_tool():
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._camera = None
    agent._mobility = None
    agent._tts = None
    agent._mcp = None
    for attr in ("_memory_tool", "_tom_tool", "_coding"):
        stub = MagicMock()
        stub.get_tool_definitions = MagicMock(return_value=[])
        setattr(agent, attr, stub)
    agent._exploration = MagicMock()

    names = {d["name"] for d in agent._all_tool_defs}
    assert "delegate_task" not in names
