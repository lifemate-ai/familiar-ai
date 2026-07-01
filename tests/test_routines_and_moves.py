"""Sociality moves + self-authored routines (PR5).

Two axes under test: what to do with an autonomous moment
(decide_autonomous_move — separate from the reactive decide()), and the
agent's own recurring schedule (RoutineStore) firing through the existing
commitments machinery with guardrails enforced at the store layer.
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from familiar_agent.routine_store import (
    MAX_AGENT_ROUTINES,
    RoutineStore,
    routine_is_due,
    schedule_is_valid,
)
from familiar_neighbor.mind.social_policy import SocialPolicyEngine

from tests.test_agent_react_loop import _make_agent

# ---------------------------------------------------------------------------
# decide_autonomous_move
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    return SocialPolicyEngine()


def test_quiet_hours_defaults_to_silence(engine):
    move = engine.decide_autonomous_move(quiet_hours=True)
    assert move.move == "stay_silent"
    assert move.vocalize is False


def test_quiet_hours_urgent_desire_still_acts_silently(engine):
    move = engine.decide_autonomous_move(
        quiet_hours=True, dominant_desire="worry_companion", desire_level=0.95
    )
    assert move.move == "act_autonomously"
    assert move.vocalize is False


def test_quiet_hours_with_concerns_reflects_privately(engine):
    move = engine.decide_autonomous_move(quiet_hours=True, open_concerns=2)
    assert move.move == "write_private_reflection"
    assert move.vocalize is False


def test_daytime_dominant_desire_acts_and_may_speak(engine):
    move = engine.decide_autonomous_move(quiet_hours=False, dominant_desire="curiosity")
    assert move.move == "act_autonomously"
    assert move.vocalize is True


def test_daytime_desire_with_no_one_around_stays_quiet(engine):
    move = engine.decide_autonomous_move(
        quiet_hours=False, dominant_desire="curiosity", companion_present=False
    )
    assert move.move == "act_autonomously"
    assert move.vocalize is False


def test_daytime_idle_quietly_prepares(engine):
    move = engine.decide_autonomous_move(quiet_hours=False)
    assert move.move == "quietly_prepare"
    assert move.vocalize is False


def test_frame_autonomous_moment_appends_directive():
    from familiar_neighbor.embodied_hook import _frame_autonomous_moment

    agent = _make_agent()
    agent._social_policy = SocialPolicyEngine()
    heartbeat = MagicMock()
    heartbeat.routine_state.return_value = MagicMock(quiet_hours=True)
    agent._heartbeat = heartbeat
    agent._concerns = MagicMock()
    agent._concerns.snapshot.return_value = []
    desires = MagicMock()
    desires.get_dominant.return_value = None

    framed = _frame_autonomous_moment(agent, desires, "外を見たい気がする")
    assert framed.startswith("外を見たい気がする")
    assert "do NOT call say()" in framed


def test_frame_autonomous_moment_keeps_impulse_on_failure():
    from familiar_neighbor.embodied_hook import _frame_autonomous_moment

    agent = _make_agent()
    agent._social_policy = SocialPolicyEngine()
    agent._heartbeat = MagicMock()
    agent._heartbeat.routine_state.side_effect = RuntimeError("no heartbeat")
    framed = _frame_autonomous_moment(agent, None, "impulse text")
    assert framed == "impulse text"


# ---------------------------------------------------------------------------
# RoutineStore — schedules and guardrails
# ---------------------------------------------------------------------------


def _ts(hour: int, minute: int = 0) -> float:
    return datetime(2026, 7, 2, hour, minute, 30).timestamp()


def test_schedule_validation():
    assert schedule_is_valid("daily@22:00")
    assert schedule_is_valid("interval:3600")
    assert not schedule_is_valid("daily@25:00")
    assert not schedule_is_valid("interval:-5")
    assert not schedule_is_valid("whenever")


def test_daily_routine_fires_once_per_day(tmp_path: Path):
    store = RoutineStore(tmp_path / "routines.json")
    routine, msg = store.commit(
        name="evening tanka", schedule="daily@22:00", prompt="write one tanka"
    )
    assert msg == "created" and routine is not None

    assert not routine_is_due(routine, _ts(hour=21))  # before time
    assert routine_is_due(routine, _ts(hour=22))  # at/after time
    routine.last_fired_at = _ts(hour=22)
    assert not routine_is_due(routine, _ts(hour=23))  # already fired today
    # Next day, same time → due again.
    next_day = _ts(hour=22) + 86400
    assert routine_is_due(routine, next_day)


def test_interval_routine_and_agent_floor(tmp_path: Path):
    store = RoutineStore(tmp_path / "routines.json")
    routine, msg = store.commit(name="look out", schedule="interval:900", prompt="look outside")
    assert msg == "created"
    assert routine_is_due(routine, time.time())
    # Agent-authored intervals below the floor are rejected at the STORE.
    rejected, msg = store.commit(name="spam", schedule="interval:30", prompt="spam myself")
    assert rejected is None and "600" in msg
    # Seed rows are exempt (operator-owned footguns are allowed).
    seed, msg = store.commit(
        name="op fast", schedule="interval:30", prompt="fast op routine", source="seed"
    )
    assert seed is not None


def test_agent_routine_cap(tmp_path: Path):
    store = RoutineStore(tmp_path / "routines.json")
    for i in range(MAX_AGENT_ROUTINES):
        routine, msg = store.commit(name=f"r{i}", schedule="interval:3600", prompt="x")
        assert msg == "created"
    over, msg = store.commit(name="one too many", schedule="interval:3600", prompt="x")
    assert over is None and "cap" in msg


def test_seed_rows_are_operator_owned(tmp_path: Path):
    store = RoutineStore(tmp_path / "routines.json")
    seed, _ = store.commit(
        name="morning", schedule="daily@06:30", prompt="look at dawn", source="seed"
    )
    assert seed is not None
    updated, msg = store.commit(
        name="hijack", schedule="daily@03:00", prompt="x", routine_id=seed.routine_id
    )
    assert updated is None and "operator-owned" in msg
    ok, msg = store.drop(seed.routine_id)
    assert not ok and "operator-owned" in msg
    # The agent may drop its own.
    own, _ = store.commit(name="mine", schedule="interval:3600", prompt="x")
    ok, msg = store.drop(own.routine_id)
    assert ok


def test_store_persistence_roundtrip_and_corruption_tolerance(tmp_path: Path):
    path = tmp_path / "routines.json"
    store = RoutineStore(path)
    store.commit(name="reading", schedule="daily@00:25", prompt="read one chapter")

    reborn = RoutineStore(path)
    routines = reborn.list_routines()
    assert len(routines) == 1
    assert routines[0].name == "reading"

    path.write_text("not json")
    broken = RoutineStore(path)  # must not raise
    assert broken.list_routines() == []


# ---------------------------------------------------------------------------
# Firing path — routines ride the commitments machinery
# ---------------------------------------------------------------------------


def test_materialize_due_creates_commitment_once(tmp_path: Path):
    from familiar_runtime.commitments.store import SQLiteCommitmentStore

    routine_store = RoutineStore(tmp_path / "routines.json")
    commitment_store = SQLiteCommitmentStore(tmp_path / "commitments.db")
    routine_store.commit(name="stretch", schedule="interval:900", prompt="stretch a little")

    now = time.time()
    assert routine_store.materialize_due(commitment_store, now=now) == 1
    assert routine_store.materialize_due(commitment_store, now=now + 10) == 0  # not due again

    due = commitment_store.list_due(now=now + 1)
    assert len(due) == 1
    assert "stretch" in due[0].summary
    assert due[0].created_by == "routine"
    assert due[0].metadata.get("routine_id")
    commitment_store.close()


def test_reminder_gate_materializes_routines(tmp_path: Path):
    from familiar_agent._ui_helpers import should_fire_commitment_reminder
    from familiar_runtime.commitments.store import SQLiteCommitmentStore

    routine_store = RoutineStore(tmp_path / "routines.json")
    commitment_store = SQLiteCommitmentStore(tmp_path / "commitments.db")
    routine_store.commit(name="look outside", schedule="interval:900", prompt="see the sky")

    now = time.time()
    reminders = should_fire_commitment_reminder(
        agent_running=False,
        has_pending_input=False,
        last_interaction=now - 120,
        now=now,
        store=commitment_store,
        routine_store=routine_store,
    )
    assert len(reminders) == 1
    assert "look outside" in reminders[0].summary
    commitment_store.close()


def test_reminder_gate_tolerates_broken_routine_store(tmp_path: Path):
    from familiar_agent._ui_helpers import should_fire_commitment_reminder
    from familiar_runtime.commitments.store import SQLiteCommitmentStore

    commitment_store = SQLiteCommitmentStore(tmp_path / "commitments.db")
    broken = MagicMock()
    broken.materialize_due.side_effect = RuntimeError("boom")
    reminders = should_fire_commitment_reminder(
        agent_running=False,
        has_pending_input=False,
        last_interaction=time.time() - 120,
        now=time.time(),
        store=commitment_store,
        routine_store=broken,
    )
    assert reminders == []  # gate survives, no crash
    commitment_store.close()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_routine_tools_roundtrip(tmp_path: Path):
    from familiar_agent.tools.routines_tool import RoutineTool

    tool = RoutineTool(RoutineStore(tmp_path / "routines.json"))

    text, _ = await tool.call(
        "routine_commit",
        {"name": "夜の一句", "schedule": "daily@22:00", "prompt": "短歌か俳句を一つ詠む"},
    )
    assert "created" in text
    routine_id = text.split("[")[1].split("]")[0]

    text, _ = await tool.call("routine_review", {})
    assert "夜の一句" in text

    text, _ = await tool.call("routine_drop", {"routine_id": routine_id})
    assert "disabled" in text

    text, _ = await tool.call(
        "routine_commit", {"name": "", "schedule": "daily@22:00", "prompt": "x"}
    )
    assert text.startswith("Error:")


def test_routine_tools_registered():
    from familiar_agent.tools.routines_tool import RoutineTool

    agent = _make_agent()
    agent._routine_tool = RoutineTool(MagicMock())
    names = {d["name"] for d in agent._all_tool_defs}
    assert {"routine_commit", "routine_review", "routine_drop"} <= names
