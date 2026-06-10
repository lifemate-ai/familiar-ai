"""Wiring tests for the REPL proactive-reminder branch in main.repl().

The reminder branch must sit BEFORE the auto_desire guard so reminders fire
even when desire-driven idle turns are disabled (independent toggle).
"""

from __future__ import annotations

import asyncio
import threading
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from familiar_agent.main import repl
from familiar_runtime.commitments import SQLiteCommitmentStore


@pytest.fixture
def stdin_guard(monkeypatch):
    """Block the repl's stdin reader thread until the test finishes.

    repl() spawns a run_in_executor stdin reader; without this, pytest's
    captured stdin returns EOF instantly and the loop exits before idle.
    """
    release = threading.Event()

    def fake_readline() -> str:
        release.wait(timeout=10)
        return ""  # EOF once released

    monkeypatch.setattr("sys.stdin", SimpleNamespace(readline=fake_readline))
    yield
    release.set()


@pytest.fixture
def no_process_exit(monkeypatch):
    """repl()'s finally block calls os._exit(0); neuter it so pytest survives."""
    calls: list[int] = []
    monkeypatch.setattr("familiar_agent.main.os._exit", lambda code: calls.append(code))
    return calls


def _fake_agent(store, *, proactive: bool, auto_desire: bool = False):
    agent = SimpleNamespace(
        is_embedding_ready=True,
        config=SimpleNamespace(proactive_reminders=proactive, auto_desire=auto_desire),
        _commitment_store=store,
        _heartbeat=None,
        run=AsyncMock(),
        close=AsyncMock(),
    )
    return agent


def _fake_wait_for_factory(behaviors):
    """Pop a behavior per call: 'timeout' raises TimeoutError, 'stop' raises KeyboardInterrupt.

    Once behaviors are exhausted, delegate to the awaitable itself (covers the
    cleanup wait_for calls in repl()'s finally block).
    """
    real_wait_for = asyncio.wait_for

    async def _fake_wait_for(awaitable, timeout):
        if not behaviors:
            return await real_wait_for(awaitable, timeout)
        if hasattr(awaitable, "close"):
            awaitable.close()
        action = behaviors.pop(0)
        if action == "timeout":
            raise asyncio.TimeoutError
        raise KeyboardInterrupt

    return _fake_wait_for


@pytest.mark.asyncio
async def test_repl_reminder_fires_with_auto_desire_off(
    monkeypatch, tmp_path, stdin_guard, no_process_exit
):
    store = SQLiteCommitmentStore(tmp_path / "c.db")
    store.create(summary="meds", due_at=time.time() - 60, priority=1)
    agent = _fake_agent(store, proactive=True, auto_desire=False)

    monkeypatch.setattr("familiar_agent.main.create_realtime_stt_session", lambda: None)
    monkeypatch.setattr(
        "familiar_agent.main.asyncio.wait_for", _fake_wait_for_factory(["timeout", "stop"])
    )
    # Bypass the wall-clock idle gap (last_interaction is set to now inside repl).
    monkeypatch.setattr(
        "familiar_agent.main.should_fire_commitment_reminder",
        lambda **kw: kw["store"].list_due(now=time.time()),
    )

    await repl(agent, desires=SimpleNamespace(), debug=False)

    agent.run.assert_awaited_once()
    kwargs = agent.run.await_args.kwargs
    assert agent.run.await_args.args[0] == ""
    assert "meds" in kwargs["inner_voice"]
    # mark_reminded advanced the cadence
    assert store.list_open()[0].reminder_count == 1
    store.close()


@pytest.mark.asyncio
async def test_repl_reminder_turn_error_does_not_kill_repl(
    monkeypatch, tmp_path, stdin_guard, no_process_exit
):
    """A backend error during the reminder turn must not crash (and silently
    os._exit) the REPL; the slot is still burned so a flapping backend
    self-limits via the cadence cap."""
    store = SQLiteCommitmentStore(tmp_path / "c.db")
    store.create(summary="meds", due_at=time.time() - 60, priority=1)
    agent = _fake_agent(store, proactive=True, auto_desire=False)
    agent.run = AsyncMock(side_effect=RuntimeError("api down"))

    monkeypatch.setattr("familiar_agent.main.create_realtime_stt_session", lambda: None)
    monkeypatch.setattr(
        "familiar_agent.main.asyncio.wait_for",
        _fake_wait_for_factory(["timeout", "stop"]),
    )
    monkeypatch.setattr(
        "familiar_agent.main.should_fire_commitment_reminder",
        lambda **kw: kw["store"].list_due(now=time.time()),
    )

    # Must return normally (KeyboardInterrupt from 'stop' caught inside repl).
    await repl(agent, desires=SimpleNamespace(), debug=False)

    agent.run.assert_awaited_once()
    assert store.list_open()[0].reminder_count == 1  # slot burned despite the error
    store.close()


@pytest.mark.asyncio
async def test_repl_reminder_respects_toggle_off(
    monkeypatch, tmp_path, stdin_guard, no_process_exit
):
    store = SQLiteCommitmentStore(tmp_path / "c.db")
    store.create(summary="meds", due_at=time.time() - 60, priority=1)
    agent = _fake_agent(store, proactive=False, auto_desire=False)

    monkeypatch.setattr("familiar_agent.main.create_realtime_stt_session", lambda: None)
    monkeypatch.setattr(
        "familiar_agent.main.asyncio.wait_for", _fake_wait_for_factory(["timeout", "stop"])
    )

    await repl(agent, desires=SimpleNamespace(), debug=False)

    agent.run.assert_not_awaited()
    assert store.list_open()[0].reminder_count == 0
    store.close()
