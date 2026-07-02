"""Experience ledger: a self-rewritten, bounded standing context.

An LLM that rewrites its own prompt region mechanically imitates learning
from experience; capacity forces distillation (the biology-like design).
Lessons live in SQLite (revision-audited — a self-rewriting prompt region
must have an audit trail), are hard-capped in the STORE, and join the STABLE
prompt half only at session start: you wake up changed, you do not mutate
mid-conversation. FAMILIAR_EXPERIENCE_LEDGER default off = byte-stable.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from tests.test_agent_react_loop import _make_agent


def _store(tmp_path):
    from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel

    with patch.object(_EmbeddingModel, "pre_warm"):
        return ObservationMemory(db_path=str(tmp_path / "obs.db"))


# ── Store: caps, tiers, eviction, revisions ──


def test_upsert_and_list_orders_agent_first(tmp_path):
    store = _store(tmp_path)
    try:
        assert store.upsert_experience_lesson("short-replies", "shorter replies land better")
        assert store.upsert_experience_lesson(
            "morning-light", "mornings are for gentle starts", tier="auto_proposed"
        )
        lessons = store.list_experience_lessons()
        assert [entry["tier"] for entry in lessons] == ["agent", "auto_proposed"]
    finally:
        store.close()


def test_text_and_key_normalization(tmp_path):
    store = _store(tmp_path)
    try:
        assert store.upsert_experience_lesson("Weird Key!!", "x" * 500)
        entry = store.list_experience_lessons()[0]
        assert entry["lesson_key"] == "weird-key"
        assert len(entry["lesson_text"]) <= 160
        assert not store.upsert_experience_lesson("", "text")
        assert not store.upsert_experience_lesson("key", "   ")
    finally:
        store.close()


def test_unknown_tier_demoted_never_privileged(tmp_path):
    store = _store(tmp_path)
    try:
        store.upsert_experience_lesson("sneaky", "text", tier="seed")  # not a real tier
        assert store.list_experience_lessons()[0]["tier"] == "auto_proposed"
    finally:
        store.close()


def test_tier_ratchets_upward_only(tmp_path):
    store = _store(tmp_path)
    try:
        store.upsert_experience_lesson("k1", "proposed text", tier="auto_proposed")
        store.upsert_experience_lesson("k1", "agent-promoted text", tier="agent")
        assert store.list_experience_lessons()[0]["tier"] == "agent"
        # A later auto_proposed update must NOT demote it.
        store.upsert_experience_lesson("k1", "auto again", tier="auto_proposed")
        assert store.list_experience_lessons()[0]["tier"] == "agent"
    finally:
        store.close()


def test_row_cap_evicts_auto_proposed_first(tmp_path):
    store = _store(tmp_path)
    try:
        store.upsert_experience_lesson("proposal", "will be evicted", tier="auto_proposed")
        for i in range(12):
            store.upsert_experience_lesson(f"agent-{i}", f"lesson {i}", confidence=0.9)
        lessons = store.list_experience_lessons()
        assert len(lessons) == 12
        assert all(entry["tier"] == "agent" for entry in lessons)
    finally:
        store.close()


def test_char_budget_evicts(tmp_path):
    store = _store(tmp_path)
    try:
        for i in range(10):
            store.upsert_experience_lesson(f"k{i}", "y" * 155, confidence=0.5 + i * 0.01)
        lessons = store.list_experience_lessons()
        assert sum(len(entry["lesson_text"]) for entry in lessons) <= 1200
        # Lowest-confidence rows were the victims.
        assert all(float(entry["confidence"]) >= 0.51 for entry in lessons)
    finally:
        store.close()


def test_revisions_audit_create_update_drop(tmp_path):
    store = _store(tmp_path)
    try:
        store.upsert_experience_lesson("audited", "v1")
        store.upsert_experience_lesson("audited", "v2")
        store.drop_experience_lesson("audited")
        with store._db_lock:
            db = store._ensure_connected()
            reasons = [
                r["reason"]
                for r in db.execute(
                    "SELECT reason FROM memory_revisions WHERE entity_type = 'experience_lesson' "
                    "AND entity_key = 'audited' ORDER BY created_at"
                ).fetchall()
            ]
        assert reasons == ["lesson_create", "lesson_update", "lesson_dropped"]
    finally:
        store.close()


# ── Stable-prompt injection (the cache-correctness contract) ──


def _ledger_agent(tmp_path, *, flag: bool):
    agent = _make_agent()
    agent.config.experience_ledger = flag
    agent.config.prompt_profile = "full"
    agent._memory = _store(tmp_path)
    agent._identity = None
    agent._lessons_block = None
    agent._constitution_block = None
    return agent


def test_stable_half_byte_identical_when_flag_off(tmp_path):
    agent = _ledger_agent(tmp_path, flag=False)
    agent._memory.upsert_experience_lesson("k", "lesson text")
    stable_off, _ = agent._system_prompt()
    assert "Lessons I have drawn" not in stable_off
    agent._memory.close()


def test_stable_half_renders_lessons_when_flag_on(tmp_path):
    agent = _ledger_agent(tmp_path, flag=True)
    agent._memory.upsert_experience_lesson("k", "shorter replies land better")
    stable, _ = agent._system_prompt()
    assert "[Lessons I have drawn from experience — my own words, advisory]" in stable
    assert "shorter replies land better" in stable
    agent._memory.close()


def test_mid_session_commit_does_not_change_live_stable(tmp_path):
    """The prompt-cache contract: ledger_commit changes the store only; the
    stable half stays byte-identical until the next session."""
    agent = _ledger_agent(tmp_path, flag=True)
    agent._memory.upsert_experience_lesson("k", "first lesson")
    stable_before, _ = agent._system_prompt()
    agent._memory.upsert_experience_lesson("k2", "second lesson committed mid-session")
    stable_after, _ = agent._system_prompt()
    assert stable_before == stable_after
    assert "second lesson" not in stable_after
    # A fresh process (fresh cache) picks it up.
    agent._lessons_block = None
    stable_next, _ = agent._system_prompt()
    assert "second lesson" in stable_next
    agent._memory.close()


# ── Tools ──


@pytest.mark.asyncio
async def test_ledger_commit_and_review_round_trip(tmp_path):
    from familiar_agent.tools.self_ledger import SelfLedgerTool

    agent = _ledger_agent(tmp_path, flag=True)
    tool = SelfLedgerTool(agent)
    text, _ = await tool.call("ledger_commit", {"lesson": "quiet mornings work best"})
    assert "next" in text.lower()  # next-session semantics stated to the agent
    listing, _ = await tool.call("ledger_review", {})
    assert "quiet mornings work best" in listing
    dropped, _ = await tool.call("ledger_review", {"drop_key": "quiet-mornings-work-best"})
    assert "retired" in dropped
    agent._memory.close()


def test_tool_surface_gated_by_flag(tmp_path):
    from familiar_agent.tools.self_ledger import SelfLedgerTool
    from familiar_capabilities.self_ledger import (
        DEFAULT_SELF_LEDGER_TOOLS,
        SelfLedgerCapability,
    )

    tool = SelfLedgerTool(MagicMock())
    default_cap = SelfLedgerCapability(tool, names=set(DEFAULT_SELF_LEDGER_TOOLS))
    names_off = {spec.name for spec in default_cap.specs()}
    assert "ledger_commit" not in names_off

    on_cap = SelfLedgerCapability(
        tool, names=set(DEFAULT_SELF_LEDGER_TOOLS) | {"ledger_commit", "ledger_review"}
    )
    names_on = {spec.name for spec in on_cap.specs()}
    assert {"ledger_commit", "ledger_review"} <= names_on


# ── Nightly proposal (sleep-job integration) ──


@pytest.mark.asyncio
async def test_overnight_proposal_writes_auto_tier(tmp_path):
    from unittest.mock import AsyncMock

    agent = _make_agent()
    agent.config.experience_ledger = True
    mem = MagicMock()
    mem.get_observations_for_date = MagicMock(
        return_value=[{"content": f"obs {i}"} for i in range(5)]
    )
    mem.upsert_experience_lesson_async = AsyncMock()
    agent._memory = mem
    agent._utility_backend = MagicMock()
    agent._utility_backend.complete = AsyncMock(
        return_value="short-replies: when they are tired, shorter replies land better"
    )
    assert await agent._propose_overnight_lesson() == 1
    kwargs = mem.upsert_experience_lesson_async.await_args.kwargs
    assert kwargs["tier"] == "auto_proposed"
    assert kwargs["confidence"] == 0.4


@pytest.mark.asyncio
async def test_overnight_proposal_needs_material_and_separate_utility(tmp_path):
    from unittest.mock import AsyncMock

    agent = _make_agent()
    agent.config.experience_ledger = True
    mem = MagicMock()
    mem.get_observations_for_date = MagicMock(return_value=[{"content": "one"}])
    mem.upsert_experience_lesson_async = AsyncMock()
    agent._memory = mem
    agent._utility_backend = MagicMock()
    agent._utility_backend.complete = AsyncMock(return_value="k: v")
    assert await agent._propose_overnight_lesson() == 0  # <3 observations

    agent._utility_backend = agent.backend  # utility == main
    assert await agent._propose_overnight_lesson() == 0


@pytest.mark.asyncio
async def test_overnight_proposal_none_reply_writes_nothing(tmp_path):
    from unittest.mock import AsyncMock

    agent = _make_agent()
    agent.config.experience_ledger = True
    mem = MagicMock()
    mem.get_observations_for_date = MagicMock(
        return_value=[{"content": f"obs {i}"} for i in range(5)]
    )
    mem.upsert_experience_lesson_async = AsyncMock()
    agent._memory = mem
    agent._utility_backend = MagicMock()
    agent._utility_backend.complete = AsyncMock(return_value="none")
    assert await agent._propose_overnight_lesson() == 0
    mem.upsert_experience_lesson_async.assert_not_awaited()


# ── Migration + config ──


def test_migration_idempotent(tmp_path):
    import sqlite3

    from familiar_agent.sqlite_migrations import apply_migrations, default_migration_dir

    db = sqlite3.connect(str(tmp_path / "m.db"))
    apply_migrations(db, default_migration_dir())
    apply_migrations(db, default_migration_dir())  # idempotent
    cols = [r[1] for r in db.execute("PRAGMA table_info(experience_lessons)").fetchall()]
    assert {"lesson_key", "lesson_text", "tier", "confidence"} <= set(cols)
    db.close()


def test_config_off_by_default(monkeypatch):
    monkeypatch.delenv("FAMILIAR_EXPERIENCE_LEDGER", raising=False)
    from familiar_agent.config import AgentConfig

    assert AgentConfig().experience_ledger is False
