"""Tests for the CommitmentTool and its capability wiring (secretary surface)."""

from __future__ import annotations

import pytest

from familiar_agent.tools.commitments import (
    CommitmentTool,
    format_commitments_for_context,
)
from familiar_capabilities.commitments import CommitmentCapability
from familiar_runtime.commitments import (
    CommitmentKind,
    CommitmentStatus,
    SQLiteCommitmentStore,
)

FIXED_NOW = 1_000_000.0


@pytest.fixture
def tool(tmp_path):
    store = SQLiteCommitmentStore(tmp_path / "commitments.db")
    yield CommitmentTool(store, clock=lambda: FIXED_NOW)
    store.close()


@pytest.mark.asyncio
async def test_add_commitment_returns_id_and_persists(tool):
    text, image = await tool.call(
        "add_commitment",
        {"summary": "call dentist", "kind": "reminder", "priority": 2},
    )
    assert image is None
    assert "call dentist" in text
    stored = tool.store.list_open()
    assert len(stored) == 1
    assert stored[0].summary == "call dentist"
    assert stored[0].priority == 2
    assert stored[0].created_by == "user"


@pytest.mark.asyncio
async def test_add_commitment_due_in_minutes_sets_due_at(tool):
    await tool.call("add_commitment", {"summary": "tea", "due_in_minutes": 30})
    c = tool.store.list_open()[0]
    assert c.due_at == pytest.approx(FIXED_NOW + 30 * 60)


@pytest.mark.asyncio
async def test_add_commitment_due_at_iso(tool):
    await tool.call(
        "add_commitment",
        {"summary": "meeting", "due_at_iso": "2026-06-11T09:00:00"},
    )
    c = tool.store.list_open()[0]
    assert c.due_at is not None and c.due_at > 0


@pytest.mark.asyncio
async def test_list_commitments_due_filter(tool):
    await tool.call("add_commitment", {"summary": "overdue", "due_in_minutes": -5})
    await tool.call("add_commitment", {"summary": "later", "due_in_minutes": 600})
    text, _ = await tool.call("list_commitments", {"filter": "due"})
    assert "overdue" in text
    assert "later" not in text


@pytest.mark.asyncio
async def test_complete_commitment(tool):
    add_text, _ = await tool.call("add_commitment", {"summary": "x"})
    cid = tool.store.list_open()[0].id
    text, _ = await tool.call("complete_commitment", {"id": cid})
    assert "✓" in text or "done" in text.lower() or "完了" in text
    assert tool.store.get(cid).status is CommitmentStatus.DONE


@pytest.mark.asyncio
async def test_snooze_commitment(tool):
    await tool.call("add_commitment", {"summary": "ping", "due_in_minutes": -1})
    cid = tool.store.list_open()[0].id
    await tool.call("snooze_commitment", {"id": cid, "minutes": 60})
    assert tool.store.get(cid).status is CommitmentStatus.SNOOZED
    assert tool.store.list_due(now=FIXED_NOW) == []


@pytest.mark.asyncio
async def test_unknown_tool_returns_error_text(tool):
    text, _ = await tool.call("nonexistent", {})
    assert "unknown" in text.lower() or "error" in text.lower()


def test_capability_exposes_four_tools(tmp_path):
    store = SQLiteCommitmentStore(tmp_path / "c.db")
    tool = CommitmentTool(store)
    cap = CommitmentCapability(tool)
    names = {spec.name for spec in cap.specs()}
    assert names == {
        "add_commitment",
        "list_commitments",
        "complete_commitment",
        "snooze_commitment",
    }
    for spec in cap.specs():
        assert spec.category == "commitment"
        assert spec.input_schema.get("type") == "object"
    store.close()


def test_format_commitments_for_context():
    store = SQLiteCommitmentStore(":memory:")
    due = [store.create(summary="overdue ping", due_at=FIXED_NOW - 10, priority=2)]
    upcoming = [store.create(summary="dentist at 3", due_at=FIXED_NOW + 3600)]
    text = format_commitments_for_context(due=due, upcoming=upcoming)
    assert "overdue ping" in text
    assert "dentist at 3" in text
    # empty input yields empty string
    assert format_commitments_for_context(due=[], upcoming=[]) == ""
    store.close()


@pytest.mark.asyncio
async def test_commitment_kind_defaults_to_reminder():
    store = SQLiteCommitmentStore(":memory:")
    tool = CommitmentTool(store)
    await tool.call("add_commitment", {"summary": "no kind"})
    assert store.list_open()[0].kind is CommitmentKind.REMINDER
    store.close()


def test_agent_commitments_context_surfaces_due(tmp_path):
    """The EmbodiedAgent surface method renders due commitments without a full boot."""
    import time
    import types

    from familiar_agent.agent import EmbodiedAgent

    store = SQLiteCommitmentStore(tmp_path / "c.db")
    store.create(summary="overdue thing", due_at=time.time() - 10, priority=2)
    store.create(summary="far thing", due_at=time.time() + 10_000_000)
    stub = types.SimpleNamespace(_commitment_store=store)

    ctx = EmbodiedAgent._commitments_context(stub)
    assert "overdue thing" in ctx
    assert "Reminders due now" in ctx
    assert "far thing" not in ctx  # outside the upcoming horizon
    store.close()


def test_agent_commitments_context_empty_without_store():
    import types

    from familiar_agent.agent import EmbodiedAgent

    stub = types.SimpleNamespace(_commitment_store=None)
    assert EmbodiedAgent._commitments_context(stub) == ""


def test_build_tool_registry_includes_commitment_tools(tmp_path):
    """When the commitment tool is present, its tools land in the registry."""
    from unittest.mock import AsyncMock, MagicMock

    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    for attr in ("_camera", "_mobility", "_tts", "_mcp"):
        setattr(agent, attr, None)
    for attr in ("_memory_tool", "_tom_tool", "_coding"):
        m = MagicMock()
        m.call = AsyncMock(return_value=("ok", None))
        setattr(agent, attr, m)
    store = SQLiteCommitmentStore(tmp_path / "c.db")
    agent._commitment_tool = CommitmentTool(store)

    registry = agent._build_tool_registry()
    names = {spec["name"] for spec in registry.tool_defs()}
    assert "add_commitment" in names
    assert "complete_commitment" in names
    store.close()


# ── today's agenda (morning secretary surface) ──


def _agenda_stub(store):
    import types

    return types.SimpleNamespace(_commitment_store=store)


def test_today_agenda_includes_due_and_today_only(tmp_path):
    import time as _time

    from familiar_agent.agent import EmbodiedAgent

    store = SQLiteCommitmentStore(tmp_path / "c.db")
    now = _time.time()
    store.create(summary="overdue call", due_at=now - 600, priority=1)
    store.create(summary="dentist 15:00", due_at=now + 3600)
    store.create(summary="next week thing", due_at=now + 8 * 86400)
    store.create(summary="no due note")

    ctx = EmbodiedAgent._today_agenda_context(_agenda_stub(store))
    assert "Today's agenda" in ctx
    assert "overdue call" in ctx
    assert "dentist 15:00" in ctx
    assert "next week thing" not in ctx
    assert "no due note" not in ctx
    store.close()


def test_today_agenda_empty_cases(tmp_path):
    import types

    from familiar_agent.agent import EmbodiedAgent

    # no store at all
    assert EmbodiedAgent._today_agenda_context(types.SimpleNamespace(_commitment_store=None)) == ""
    # empty store
    store = SQLiteCommitmentStore(tmp_path / "c.db")
    assert EmbodiedAgent._today_agenda_context(_agenda_stub(store)) == ""
    store.close()
