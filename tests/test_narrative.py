"""Narrative arcs, daybook and self summary (selfhood/sociality Phase 2).

Arcs are the bounded set of storylines the agent holds about its own life;
the daybook is one merged record per day; the self summary aggregates arcs,
today's daybook and the recent self-narrative into one bounded paragraph.
Every wiring point is getattr-guarded: with no arcs the prompt is byte-stable.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from familiar_agent.sqlite_migrations import apply_migrations, default_migration_dir
from familiar_agent.tools.narrative import NarrativeTool
from familiar_capabilities.narrative import DEFAULT_NARRATIVE_TOOLS, NarrativeCapability
from familiar_neighbor.mind.narrative import (
    MAX_ACTIVE_ARCS,
    Daybook,
    DaybookRecord,
    NarrativeArc,
    NarrativeStore,
    build_self_summary,
)
from familiar_neighbor.mind.social_events import SOCIAL_EVENT_KINDS, SocialEventLog


@pytest.fixture
def store(tmp_path: Path):
    s = NarrativeStore(db_path=tmp_path / "obs.db")
    yield s
    s.close()


@pytest.fixture
def daybook(tmp_path: Path) -> Daybook:
    return Daybook(path=tmp_path / "daybook.jsonl")


# ── migration + shim ──


def test_migration_creates_narrative_arcs_table_and_index(tmp_path: Path):
    db = sqlite3.connect(str(tmp_path / "m.db"))
    apply_migrations(db, default_migration_dir())
    apply_migrations(db, default_migration_dir())  # idempotent
    cols = [r[1] for r in db.execute("PRAGMA table_info(narrative_arcs)").fetchall()]
    assert cols == [
        "id",
        "arc_key",
        "title",
        "summary",
        "importance",
        "status",
        "created_at",
        "updated_at",
    ]
    indexes = {r[1] for r in db.execute("PRAGMA index_list(narrative_arcs)").fetchall()}
    assert "idx_narrative_arcs_status_importance" in indexes
    applied = {r[0] for r in db.execute("SELECT id FROM schema_migrations").fetchall()}
    assert "2026-09-14-014_narrative_arcs" in applied
    # arc_key is UNIQUE
    db.execute("INSERT INTO narrative_arcs VALUES ('a', 'k', 't', '', 0.5, 'active', 'x', 'x')")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO narrative_arcs VALUES ('b', 'k', 't', '', 0.5, 'active', 'x', 'x')")
    db.close()


def test_shim_import_path():
    from familiar_agent.narrative import NarrativeStore as Shimmed

    assert Shimmed is NarrativeStore


def test_arc_updated_is_a_known_social_event_kind():
    assert "arc_updated" in SOCIAL_EVENT_KINDS


# ── arcs ──


def test_upsert_creates_then_updates_same_key(store: NarrativeStore):
    first = store.upsert_arc("onion", "Onion refactor", "started the pipeline split", 0.8)
    assert isinstance(first, NarrativeArc)
    assert first.status == "active"
    second = store.upsert_arc("onion", "Onion refactor", "pipeline split landed", 0.9)
    assert second.id == first.id
    assert second.summary == "pipeline split landed"
    assert second.importance == 0.9
    assert second.created_at == first.created_at
    assert second.updated_at >= first.updated_at
    assert len(store.active_arcs()) == 1


def test_importance_is_clamped_and_key_normalized(store: NarrativeStore):
    arc = store.upsert_arc("  Onion  ", "t", "s", 7.0)
    assert arc.arc_key == "onion"
    assert arc.importance == 1.0
    assert store.upsert_arc("onion", "t", "s", -3).importance == 0.0


def test_upsert_rejects_empty_key_or_title(store: NarrativeStore):
    with pytest.raises(ValueError):
        store.upsert_arc("", "t", "s", 0.5)
    with pytest.raises(ValueError):
        store.upsert_arc("k", "  ", "s", 0.5)


def test_active_arcs_bounded_lowest_importance_goes_dormant(store: NarrativeStore):
    for i in range(MAX_ACTIVE_ARCS):
        store.upsert_arc(f"arc{i}", f"Arc {i}", "s", 0.3 + i * 0.05)
    assert len(store.active_arcs()) == MAX_ACTIVE_ARCS
    eighth = store.upsert_arc("big", "Big one", "s", 0.95)
    assert eighth.status == "active"
    active = store.active_arcs()
    assert len(active) == MAX_ACTIVE_ARCS
    assert "arc0" not in {a.arc_key for a in active}  # lowest importance demoted
    dormant = store.dormant_arcs()
    assert [a.arc_key for a in dormant] == ["arc0"]
    # newest-highest first
    assert active[0].arc_key == "big"


def test_low_importance_eighth_arc_is_itself_demoted(store: NarrativeStore):
    for i in range(MAX_ACTIVE_ARCS):
        store.upsert_arc(f"arc{i}", f"Arc {i}", "s", 0.5)
    weak = store.upsert_arc("weak", "Weak", "s", 0.1)
    assert weak.status == "dormant"
    assert len(store.active_arcs()) == MAX_ACTIVE_ARCS


def test_upsert_reactivates_dormant_or_closed_arc(store: NarrativeStore):
    store.upsert_arc("k", "t", "s", 0.5)
    assert store.close_arc("k") is True
    assert store.get_arc("k").status == "closed"
    assert store.active_arcs() == []
    revived = store.upsert_arc("k", "t", "back again", 0.6)
    assert revived.status == "active"
    assert [a.arc_key for a in store.active_arcs()] == ["k"]


def test_close_unknown_arc_returns_false(store: NarrativeStore):
    assert store.close_arc("nope") is False
    assert store.get_arc("nope") is None


def test_active_arcs_limit_and_ordering(store: NarrativeStore):
    store.upsert_arc("a", "A", "s", 0.2)
    store.upsert_arc("b", "B", "s", 0.9)
    store.upsert_arc("c", "C", "s", 0.5)
    assert [a.arc_key for a in store.active_arcs()] == ["b", "c", "a"]
    assert [a.arc_key for a in store.active_arcs(limit=2)] == ["b", "c"]


def test_context_block_empty_when_no_arcs(store: NarrativeStore):
    assert store.context_block() == ""
    store.upsert_arc("k", "t", "s", 0.5)
    store.close_arc("k")
    assert store.context_block() == ""


def test_context_block_lists_active_arcs_bounded(store: NarrativeStore):
    store.upsert_arc("onion", "Onion refactor", "pipeline split landed", 0.9)
    store.upsert_arc("walk", "Outside walks", "x" * 2000, 0.4)
    block = store.context_block()
    assert block.startswith("[Life arcs]")
    assert "Onion refactor" in block
    assert "pipeline split landed" in block
    assert block.index("Onion refactor") < block.index("Outside walks")
    assert len(block) <= 1500


def test_store_emits_arc_updated_events(tmp_path: Path):
    log = SocialEventLog(db_path=tmp_path / "obs.db")
    s = NarrativeStore(db_path=tmp_path / "obs.db", event_log=log)
    s.upsert_arc("k", "T", "s", 0.5)
    s.close_arc("k")
    events = log.recent(10, kind="arc_updated")
    assert [e.payload["action"] for e in events] == ["close", "upsert"]
    assert events[0].payload["arc_key"] == "k"
    assert events[0].payload["status"] == "closed"
    assert events[0].source == "narrative"
    s.close()
    log.close()


def test_store_emits_demotion_event(tmp_path: Path):
    log = SocialEventLog(db_path=tmp_path / "obs.db")
    s = NarrativeStore(db_path=tmp_path / "obs.db", event_log=log)
    for i in range(MAX_ACTIVE_ARCS + 1):
        s.upsert_arc(f"arc{i}", f"Arc {i}", "s", 0.3 + i * 0.05)
    actions = [e.payload["action"] for e in log.recent(50, kind="arc_updated")]
    assert actions.count("demote") == 1
    s.close()
    log.close()


def test_store_without_log_and_with_broken_log_is_fine(tmp_path: Path):
    broken = MagicMock()
    broken.append.side_effect = RuntimeError("boom")
    s = NarrativeStore(db_path=tmp_path / "obs.db", event_log=broken)
    arc = s.upsert_arc("k", "t", "s", 0.5)
    assert arc.status == "active"
    assert broken.append.called
    s.close()


def test_store_reads_never_raise_on_broken_db(tmp_path: Path):
    bad = tmp_path / "dir"
    bad.mkdir()
    s = NarrativeStore(db_path=bad)  # a directory: connect fails
    assert s.active_arcs() == []
    assert s.dormant_arcs() == []
    assert s.get_arc("k") is None
    assert s.context_block() == ""
    assert s.close_arc("k") is False


# ── daybook ──


def test_daybook_empty(daybook: Daybook):
    assert daybook.latest() is None


def test_daybook_append_today_merges_and_dedups(daybook: Daybook, tmp_path: Path):
    daybook.append_today(events=["woke", "talked"], open_loops=["reply to mail"])
    daybook.append_today(events=["talked", "walked"], next_actions=["push PR"])
    rec = daybook.latest()
    assert isinstance(rec, DaybookRecord)
    assert rec.events == ["woke", "talked", "walked"]
    assert rec.open_loops == ["reply to mail"]
    assert rec.next_actions == ["push PR"]
    assert rec.boundary_moments == []
    assert rec.private_reflections == []
    lines = (tmp_path / "daybook.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1  # one record per day
    data = json.loads(lines[0])
    assert set(data) == {
        "date",
        "events",
        "boundary_moments",
        "open_loops",
        "private_reflections",
        "next_actions",
    }


def test_daybook_keeps_older_days_and_latest_is_newest(daybook: Daybook, tmp_path: Path):
    daybook.append_today(events=["today"])
    with patch("familiar_neighbor.mind.narrative._today", return_value="2001-01-01"):
        daybook.append_today(events=["long ago"])
    assert daybook.latest().date != "2001-01-01"
    assert daybook.latest().events == ["today"]
    assert daybook.record_for("2001-01-01").events == ["long ago"]
    lines = (tmp_path / "daybook.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2


def test_daybook_ignores_blank_and_bounds_length(daybook: Daybook):
    daybook.append_today(events=["", "  ", "x" * 1000])
    rec = daybook.latest()
    assert len(rec.events) == 1
    assert len(rec.events[0]) <= 300


def test_daybook_no_fields_is_noop(daybook: Daybook):
    daybook.append_today()
    assert daybook.latest() is None


def test_daybook_survives_corrupt_line(daybook: Daybook, tmp_path: Path):
    (tmp_path / "daybook.jsonl").write_text("not json\n", encoding="utf-8")
    daybook.append_today(events=["fine"])
    assert daybook.latest().events == ["fine"]


def test_daybook_write_failure_is_swallowed(tmp_path: Path, caplog):
    bad = tmp_path / "d"
    bad.mkdir()
    Daybook(path=bad).append_today(events=["x"])  # path is a directory
    assert Daybook(path=bad).latest() is None


# ── self summary ──


def test_build_self_summary_empty_is_empty_string(store: NarrativeStore, daybook: Daybook):
    assert build_self_summary(store, daybook, []) == ""
    assert build_self_summary(None, None, []) == ""


def test_build_self_summary_aggregates_and_bounds(store: NarrativeStore, daybook: Daybook):
    store.upsert_arc("onion", "Onion refactor", "pipeline split landed", 0.9)
    daybook.append_today(events=["talked about arcs"], open_loops=["finish Phase 2"])
    text = build_self_summary(store, daybook, ["[2026-09-13] I built a ledger."])
    assert "Onion refactor" in text
    assert "talked about arcs" in text
    assert "finish Phase 2" in text
    assert "I built a ledger." in text
    assert text.index("Onion refactor") < text.index("talked about arcs") < text.index("ledger")
    long = build_self_summary(store, daybook, ["y" * 5000] * 5)
    assert len(long) <= 1800


def test_build_self_summary_tolerates_broken_parts(daybook: Daybook):
    broken = MagicMock()
    broken.active_arcs.side_effect = RuntimeError("boom")
    daybook.append_today(events=["ok"])
    text = build_self_summary(broken, daybook, [])
    assert "ok" in text


# ── tool ──


def test_tool_definitions(store: NarrativeStore, daybook: Daybook):
    tool = NarrativeTool(store, daybook)
    defs = {d["name"]: d for d in tool.get_tool_definitions()}
    assert set(defs) == {"arc_commit", "arc_review", "arc_close", "self_summary"}
    assert set(defs["arc_commit"]["input_schema"]["required"]) == {"key", "title", "summary"}
    assert defs["arc_close"]["input_schema"]["required"] == ["key"]
    assert defs["arc_review"]["input_schema"]["required"] == []


@pytest.mark.asyncio
async def test_tool_commit_review_close_cycle(store: NarrativeStore, daybook: Daybook):
    tool = NarrativeTool(store, daybook)
    out, _ = await tool.call(
        "arc_commit",
        {"key": "onion", "title": "Onion refactor", "summary": "split landed", "importance": 0.8},
    )
    assert "onion" in out and "active" in out
    out, _ = await tool.call("arc_review", {})
    assert "Onion refactor" in out and "split landed" in out
    out, _ = await tool.call("arc_close", {"key": "onion"})
    assert "closed" in out
    out, _ = await tool.call("arc_review", {})
    assert "No arcs" in out
    out, _ = await tool.call("arc_close", {"key": "onion"})
    assert "No arc" in out


@pytest.mark.asyncio
async def test_tool_review_shows_dormant_separately(store: NarrativeStore, daybook: Daybook):
    tool = NarrativeTool(store, daybook)
    for i in range(MAX_ACTIVE_ARCS + 1):
        await tool.call(
            "arc_commit",
            {"key": f"a{i}", "title": f"Arc {i}", "summary": "s", "importance": 0.3 + i * 0.05},
        )
    out, _ = await tool.call("arc_review", {})
    assert "Active" in out and "Dormant" in out
    assert out.index("Active") < out.index("Dormant")


@pytest.mark.asyncio
async def test_tool_commit_validation_and_default_importance(
    store: NarrativeStore, daybook: Daybook
):
    tool = NarrativeTool(store, daybook)
    out, _ = await tool.call("arc_commit", {"key": "", "title": "t", "summary": "s"})
    assert out.startswith("Error")
    out, _ = await tool.call("arc_commit", {"key": "k", "title": "t", "summary": "s"})
    assert "0.5" in out
    out, _ = await tool.call(
        "arc_commit", {"key": "k", "title": "t", "summary": "s", "importance": "x"}
    )
    assert out.startswith("Error")
    out, _ = await tool.call("nope", {})
    assert out.startswith("Error")


@pytest.mark.asyncio
async def test_tool_self_summary(store: NarrativeStore, daybook: Daybook):
    narrative = MagicMock()
    narrative.read_recent.return_value = []
    tool = NarrativeTool(store, daybook, narrative=narrative)
    out, _ = await tool.call("self_summary", {})
    assert "No self summary" in out
    narrative.read_recent.return_value = [
        MagicMock(date="2026-09-13", text="I built a ledger.", mood="calm", trigger="x")
    ]
    store.upsert_arc("onion", "Onion refactor", "split landed", 0.8)
    out, _ = await tool.call("self_summary", {})
    assert "Onion refactor" in out and "I built a ledger." in out


@pytest.mark.asyncio
async def test_tool_calls_on_change_after_writes(store: NarrativeStore, daybook: Daybook):
    on_change = MagicMock()
    tool = NarrativeTool(store, daybook, on_change=on_change)
    await tool.call("arc_review", {})
    on_change.assert_not_called()
    await tool.call("arc_commit", {"key": "k", "title": "t", "summary": "s"})
    await tool.call("arc_close", {"key": "k"})
    assert on_change.call_count == 2


@pytest.mark.asyncio
async def test_tool_without_store_reports_unavailable(daybook: Daybook):
    tool = NarrativeTool(None, daybook)
    out, _ = await tool.call("arc_review", {})
    assert "unavailable" in out


# ── capability + registry ──


def test_capability_exposes_narrative_tools(store: NarrativeStore, daybook: Daybook):
    cap = NarrativeCapability(NarrativeTool(store, daybook))
    assert {spec.name for spec in cap.specs()} == DEFAULT_NARRATIVE_TOOLS
    assert DEFAULT_NARRATIVE_TOOLS == {"arc_commit", "arc_review", "arc_close", "self_summary"}


def test_capabilities_package_exports_narrative():
    import familiar_capabilities

    assert "NarrativeCapability" in familiar_capabilities.__all__


def test_build_tool_registry_includes_narrative(store: NarrativeStore, daybook: Daybook):
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    for attr in ("_camera", "_mobility", "_tts", "_mcp"):
        setattr(agent, attr, None)
    for attr in ("_memory_tool", "_tom_tool", "_coding"):
        m = MagicMock()
        m.call = AsyncMock(return_value=("ok", None))
        setattr(agent, attr, m)
    names = {spec["name"] for spec in agent._build_tool_registry().tool_defs()}
    assert "arc_commit" not in names  # no tool attr → byte-stable registry
    agent._narrative_tool = NarrativeTool(store, daybook)
    names = {spec["name"] for spec in agent._build_tool_registry().tool_defs()}
    assert DEFAULT_NARRATIVE_TOOLS <= names


# ── agent wiring ──


def _bare_agent(tmp_path: Path):
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent.config = MagicMock()
    agent.config.companion_name = "Kouta"
    agent._social_events = SocialEventLog(db_path=tmp_path / "obs.db")
    agent._self_narrative = MagicMock()
    return agent


def test_agent_init_narrative_wires_store_daybook_and_tool(tmp_path: Path):
    agent = _bare_agent(tmp_path)
    with (
        patch(
            "familiar_agent.agent.NarrativeStore",
            return_value=NarrativeStore(db_path=tmp_path / "obs.db"),
        ) as ctor,
        patch("familiar_agent.agent.Daybook", return_value=Daybook(path=tmp_path / "d.jsonl")),
    ):
        agent._init_narrative()
    assert ctor.call_args.kwargs.get("event_log") is agent._social_events
    assert isinstance(agent._narrative_store, NarrativeStore)
    assert isinstance(agent._daybook, Daybook)
    assert isinstance(agent._narrative_tool, NarrativeTool)
    assert agent._arcs_block is None
    agent._narrative_store.close()
    agent._social_events.close()


def test_agent_init_narrative_failure_is_dormant(tmp_path: Path):
    agent = _bare_agent(tmp_path)
    with patch("familiar_agent.agent.NarrativeStore", side_effect=RuntimeError("boom")):
        agent._init_narrative()
    assert agent._narrative_store is None
    assert agent._narrative_tool is None
    assert agent._life_arcs_block() == ""
    agent._social_events.close()


def test_life_arcs_block_cached_and_invalidated_by_tool(tmp_path: Path):
    agent = _bare_agent(tmp_path)
    s = NarrativeStore(db_path=tmp_path / "obs.db")
    with (
        patch("familiar_agent.agent.NarrativeStore", return_value=s),
        patch("familiar_agent.agent.Daybook", return_value=Daybook(path=tmp_path / "d.jsonl")),
    ):
        agent._init_narrative()
    assert agent._life_arcs_block() == ""  # empty → byte-stable prompt
    s.upsert_arc("k", "Title", "s", 0.5)
    assert agent._life_arcs_block() == ""  # cached for the session…
    agent._narrative_tool._on_change()  # …until the agent itself commits
    block = agent._life_arcs_block()
    assert block.startswith("[Life arcs]") and "Title" in block
    s.close()
    agent._social_events.close()


@pytest.mark.asyncio
async def test_life_arcs_block_joins_stable_prompt_half(tmp_path: Path):
    from tests.test_agent_react_loop import _make_agent

    agent = _make_agent()
    agent.config.prompt_profile = "full"
    agent._identity = None
    agent._lessons_block = None
    agent._constitution_block = None
    agent._arcs_block = None
    stable_before, _ = agent._system_prompt()
    assert "[Life arcs]" not in stable_before  # no store → byte-stable
    s = NarrativeStore(db_path=tmp_path / "obs.db")
    s.upsert_arc("k", "Arc title here", "s", 0.5)
    agent._narrative_store = s
    agent._arcs_block = None
    stable, _variable = agent._system_prompt()
    assert "[Life arcs]" in stable
    assert "Arc title here" in stable
    assert stable == stable_before + "\n\n---\n\n" + agent._life_arcs_block()
    s.close()


@pytest.mark.asyncio
async def test_write_today_daybook_appends_narrative_and_open_loops(tmp_path: Path):
    agent = _bare_agent(tmp_path)
    agent._turn_count = 3
    agent._daybook = Daybook(path=tmp_path / "d.jsonl")
    agent._memory = MagicMock()
    agent._memory.list_unfinished_business_async = AsyncMock(
        return_value=[{"thread": "reply to mail"}, {"content": "buy batteries"}]
    )
    await agent._write_today_daybook("Today I built arcs.")
    rec = agent._daybook.latest()
    assert rec.events == ["Today I built arcs."]
    assert rec.open_loops == ["reply to mail", "buy batteries"]
    agent._social_events.close()


@pytest.mark.asyncio
async def test_write_today_daybook_skips_without_turns_or_daybook(tmp_path: Path):
    agent = _bare_agent(tmp_path)
    agent._turn_count = 0
    agent._daybook = Daybook(path=tmp_path / "d.jsonl")
    await agent._write_today_daybook("x")
    assert agent._daybook.latest() is None
    agent._turn_count = 2
    agent._daybook = None
    await agent._write_today_daybook("x")  # no daybook → no-op, no raise
    agent._social_events.close()


@pytest.mark.asyncio
async def test_write_today_daybook_never_raises(tmp_path: Path):
    agent = _bare_agent(tmp_path)
    agent._turn_count = 2
    agent._daybook = MagicMock()
    agent._daybook.append_today.side_effect = RuntimeError("boom")
    agent._memory = MagicMock()
    agent._memory.list_unfinished_business_async = AsyncMock(side_effect=RuntimeError("x"))
    await agent._write_today_daybook("x")  # append raised inside; must not propagate
    agent._daybook.append_today.assert_called_once()
    agent._social_events.close()


def test_narrative_store_concurrent_upserts_from_threads(tmp_path: Path):
    import threading

    store = NarrativeStore(db_path=tmp_path / "obs.db", max_active=100)
    store.upsert_arc("warm", "Warm", "", 0.5)  # open the connection on the main thread
    errors: list[BaseException] = []

    def worker(idx: int) -> None:
        try:
            for j in range(10):
                store.upsert_arc(f"arc-{idx}-{j}", f"Arc {idx}-{j}", "s", 0.5)
                store.active_arcs(limit=100)
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert len(store.active_arcs(limit=100)) == 1 + 80
    store.close()
