"""Social event ledger (selfhood/sociality Phase 1).

One append-only relational timeline in observations.db: relationship shifts,
boundaries, permissions, commitments, identity violations, and person-model
writes all land as typed events. Emission is best-effort — a broken log can
never break the emitter — and every emitter stays byte-stable when no log is
attached.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from familiar_agent.sqlite_migrations import apply_migrations, default_migration_dir
from familiar_agent.tools.social_timeline import SocialTimelineTool
from familiar_capabilities.social_timeline import (
    DEFAULT_SOCIAL_TIMELINE_TOOLS,
    SocialTimelineCapability,
)
from familiar_neighbor.mind.identity import IdentityCore, IdentityViolation
from familiar_neighbor.mind.person_model import PersonModelTracker
from familiar_neighbor.mind.relationship import RelationshipTracker
from familiar_neighbor.mind.social_events import (
    SOCIAL_EVENT_KINDS,
    SocialEvent,
    SocialEventLog,
)
from familiar_runtime.commitments import SQLiteCommitmentStore


@pytest.fixture
def log(tmp_path: Path):
    ledger = SocialEventLog(db_path=tmp_path / "obs.db", default_person="Kouta")
    yield ledger
    ledger.close()


# ── migration ──


def test_migration_creates_social_events_table_and_indexes(tmp_path: Path):
    db = sqlite3.connect(str(tmp_path / "m.db"))
    apply_migrations(db, default_migration_dir())
    apply_migrations(db, default_migration_dir())  # idempotent
    cols = [r[1] for r in db.execute("PRAGMA table_info(social_events)").fetchall()]
    assert cols == [
        "id",
        "ts",
        "source",
        "kind",
        "person_key",
        "session_id",
        "correlation_id",
        "confidence",
        "payload_json",
    ]
    indexes = {r[1] for r in db.execute("PRAGMA index_list(social_events)").fetchall()}
    assert "idx_social_events_ts" in indexes
    assert "idx_social_events_person_kind" in indexes
    applied = {r[0] for r in db.execute("SELECT id FROM schema_migrations").fetchall()}
    assert "2026-09-14-013_social_events" in applied
    db.close()


def test_shim_import_path():
    from familiar_agent.social_events import SocialEventLog as Shimmed

    assert Shimmed is SocialEventLog


# ── log CRUD ──


def test_kinds_are_a_closed_frozenset():
    assert isinstance(SOCIAL_EVENT_KINDS, frozenset)
    assert {
        "trust_shift",
        "intimacy_shift",
        "boundary_added",
        "permission_set",
        "commitment_added",
        "commitment_completed",
        "commitment_snoozed",
        "identity_violation",
        "identity_reflection",
        "person_inference",
        "repair",
        "sensitive_topic",
    } <= SOCIAL_EVENT_KINDS


def test_append_and_recent_round_trip(log: SocialEventLog):
    event = log.append(
        "trust_shift",
        source="relationship",
        confidence=0.8,
        payload={"value": 0.7, "evidence": "shared a secret"},
    )
    assert isinstance(event, SocialEvent)
    assert event.person_key == "Kouta"  # default_person fills in
    assert event.session_id == log.session_id
    assert log.count() == 1
    rows = log.recent(limit=5)
    assert len(rows) == 1
    got = rows[0]
    assert got.id == event.id
    assert got.kind == "trust_shift"
    assert got.confidence == pytest.approx(0.8)
    assert got.payload == {"value": 0.7, "evidence": "shared a secret"}
    assert got.ts == event.ts


def test_recent_orders_newest_first_and_filters(log: SocialEventLog):
    log.append("trust_shift", source="relationship", person_key="Kouta")
    log.append("commitment_added", source="commitments", person_key="Akari")
    log.append("boundary_added", source="relationship", person_key="Kouta")
    assert [e.kind for e in log.recent(limit=10)] == [
        "boundary_added",
        "commitment_added",
        "trust_shift",
    ]
    assert [e.kind for e in log.recent(limit=1)] == ["boundary_added"]
    assert [e.kind for e in log.recent(limit=10, kind="trust_shift")] == ["trust_shift"]
    assert [e.person_key for e in log.recent(limit=10, person_key="akari")] == ["Akari"]
    assert [e.kind for e in log.by_person("Kouta")] == ["boundary_added", "trust_shift"]
    assert [e.kind for e in log.by_kind("commitment_added")] == ["commitment_added"]
    assert log.count() == 3
    assert log.count(kind="boundary_added") == 1
    assert log.count(person_key="Akari") == 1


def test_unknown_kind_is_dropped_not_raised(log: SocialEventLog):
    assert log.append("not_a_kind", source="test") is None
    assert log.count() == 0


def test_append_never_raises_when_db_is_broken(tmp_path: Path, caplog):
    # A directory where the db file should be: connect() fails.
    broken = SocialEventLog(db_path=tmp_path)
    assert broken.append("repair", source="test") is None
    assert broken.recent() == []
    assert broken.count() == 0


def test_frozen_event_is_immutable(log: SocialEventLog):
    event = log.append("repair", source="test")
    assert event is not None
    with pytest.raises(Exception):
        event.kind = "trust_shift"  # type: ignore[misc]


# ── emitters ──


def test_relationship_tracker_emits_events(tmp_path: Path, log: SocialEventLog):
    tracker = RelationshipTracker(state_path=tmp_path / "rel.json", db_path=tmp_path / "rel.db")
    tracker.event_log = log
    tracker.note_trust_shift(0.8, "kept a promise", confidence=0.9)
    tracker.note_intimacy_shift(0.6, "late-night talk")
    tracker.add_boundary("no photos of the room", severity=3)
    tracker.set_permission("post_photo", False, evidence="asked not to")
    tracker.record_sensitive_topic("health", caution="handle-gently")
    tracker.record_repair("apologized for the joke", resolved=True)
    kinds = [e.kind for e in log.recent(limit=20)]
    assert kinds == [
        "repair",
        "sensitive_topic",
        "permission_set",
        "boundary_added",
        "intimacy_shift",
        "trust_shift",
    ]
    trust = log.recent(kind="trust_shift")[0]
    assert trust.source == "relationship"
    assert trust.confidence == pytest.approx(0.9)
    assert trust.payload["value"] == pytest.approx(0.8)
    assert trust.payload["evidence"] == "kept a promise"
    perm = log.recent(kind="permission_set")[0]
    assert perm.payload == {
        "permission": "post_photo",
        "allowed": False,
        "evidence": "asked not to",
    }
    tracker.close()


def test_relationship_tracker_without_log_is_unchanged(tmp_path: Path):
    tracker = RelationshipTracker(state_path=tmp_path / "rel.json", db_path=tmp_path / "rel.db")
    assert tracker.event_log is None
    tracker.note_trust_shift(0.8, "kept a promise")
    tracker.add_boundary("no photos")
    assert tracker.trust == pytest.approx(0.8)
    assert [b["text"] for b in tracker.get_boundaries()] == ["no photos"]
    tracker.close()


def test_relationship_emitter_failure_is_swallowed(tmp_path: Path):
    tracker = RelationshipTracker(state_path=tmp_path / "rel.json", db_path=tmp_path / "rel.db")
    bad = MagicMock()
    bad.append.side_effect = RuntimeError("disk on fire")
    tracker.event_log = bad
    tracker.note_trust_shift(0.8, "kept a promise")  # must not raise
    assert tracker.trust == pytest.approx(0.8)
    tracker.close()


def test_commitment_store_emits_events(tmp_path: Path, log: SocialEventLog):
    store = SQLiteCommitmentStore(tmp_path / "c.db")
    store.event_log = log
    c = store.create(summary="call back at 9", person="Kouta", priority=2)
    store.snooze(c.id, until=1.0e12)
    store.complete(c.id)
    kinds = [e.kind for e in log.recent(limit=10)]
    assert kinds == ["commitment_completed", "commitment_snoozed", "commitment_added"]
    added = log.recent(kind="commitment_added")[0]
    assert added.source == "commitments"
    assert added.correlation_id == c.id
    assert added.person_key == "Kouta"
    assert added.payload["summary"] == "call back at 9"
    assert added.payload["priority"] == 2
    snoozed = log.recent(kind="commitment_snoozed")[0]
    assert snoozed.payload["until"] == pytest.approx(1.0e12)
    store.close()


def test_commitment_store_without_log_is_unchanged(tmp_path: Path):
    store = SQLiteCommitmentStore(tmp_path / "c.db")
    assert store.event_log is None
    c = store.create(summary="x")
    assert store.complete(c.id).status.value == "done"
    store.close()


def test_person_model_emits_person_inference(tmp_path: Path, log: SocialEventLog):
    tracker = PersonModelTracker(db_path=tmp_path / "pm.db")
    tracker.event_log = log
    tracker.record_inference(
        person="Kouta",
        states=[("tired", 0.7), ("curious", 0.4)],
        evidence=["short replies"],
        policy="keep it brief",
    )
    events = log.recent(kind="person_inference")
    assert len(events) == 1
    ev = events[0]
    assert ev.source == "person_model"
    assert ev.person_key == "Kouta"
    assert ev.confidence == pytest.approx(0.7)
    assert ev.payload["states"] == [["tired", 0.7], ["curious", 0.4]]
    assert ev.payload["policy"] == "keep it brief"
    tracker.close()


def test_person_model_without_log_is_unchanged(tmp_path: Path):
    tracker = PersonModelTracker(db_path=tmp_path / "pm.db")
    assert tracker.event_log is None
    tracker.record_inference(person="Kouta", states=[("tired", 0.7)], evidence=[], policy="p")
    assert len(tracker.recent("Kouta")) == 1
    tracker.close()


def test_identity_core_emits_violation_and_reflection(tmp_path: Path, log: SocialEventLog):
    core = IdentityCore(None, state_path=tmp_path / "identity_state.json")
    core.event_log = log
    core.record_violation(
        IdentityViolation(
            assertion_key="no_lies",
            statement="I do not lie",
            severity=0.8,
            reason="agreed to fake it",
        ),
        turn_index=3,
    )
    core.resolve_reflection()
    kinds = [e.kind for e in log.recent(limit=10)]
    assert kinds == ["identity_reflection", "identity_violation"]
    violation = log.recent(kind="identity_violation")[0]
    assert violation.source == "identity"
    assert violation.payload["key"] == "no_lies"
    assert violation.payload["reason"] == "agreed to fake it"
    assert violation.payload["turn_index"] == 3
    assert violation.confidence == pytest.approx(0.8)
    reflection = log.recent(kind="identity_reflection")[0]
    assert reflection.payload["key"] == "no_lies"


def test_identity_core_without_log_is_unchanged(tmp_path: Path):
    core = IdentityCore(None, state_path=tmp_path / "identity_state.json")
    assert core.event_log is None
    core.record_violation(
        IdentityViolation(assertion_key="k", statement="s", severity=0.5, reason="r")
    )
    assert core.dissonance() > 0.0


# ── tool ──


def test_tool_definition():
    tool = SocialTimelineTool(MagicMock())
    defs = {d["name"]: d for d in tool.get_tool_definitions()}
    assert set(defs) == {"social_timeline"}
    props = defs["social_timeline"]["input_schema"]["properties"]
    assert set(props) == {"limit", "kind", "person"}
    assert props["limit"]["default"] == 10
    assert sorted(props["kind"]["enum"]) == sorted(SOCIAL_EVENT_KINDS)
    assert defs["social_timeline"]["input_schema"]["required"] == []


@pytest.mark.asyncio
async def test_tool_lists_recent_events_compactly(log: SocialEventLog):
    log.append("trust_shift", source="relationship", confidence=0.9, payload={"value": 0.8})
    log.append(
        "commitment_added",
        source="commitments",
        person_key="Kouta",
        payload={"summary": "call back at 9"},
    )
    tool = SocialTimelineTool(log)
    text, image = await tool.call("social_timeline", {})
    assert image is None
    lines = text.splitlines()
    assert lines[0].startswith("Social timeline")
    assert "2 of 2" in lines[0]
    assert "commitment_added" in lines[1] and "trust_shift" in lines[2]
    assert "Kouta" in lines[1]
    assert "call back at 9" in lines[1]
    assert "value=0.8" in lines[2]
    assert "0.90" in lines[2]


@pytest.mark.asyncio
async def test_tool_filters_and_limits(log: SocialEventLog):
    for _ in range(3):
        log.append("trust_shift", source="relationship", person_key="Kouta")
    log.append("boundary_added", source="relationship", person_key="Akari")
    tool = SocialTimelineTool(log)
    text, _ = await tool.call("social_timeline", {"limit": 2})
    assert "2 of 4" in text.splitlines()[0]
    assert len(text.splitlines()) == 3
    text, _ = await tool.call("social_timeline", {"kind": "boundary_added"})
    assert "1 of 1" in text.splitlines()[0]
    assert "Akari" in text
    text, _ = await tool.call("social_timeline", {"person": "akari"})
    assert "boundary_added" in text and "trust_shift" not in text
    text, _ = await tool.call("social_timeline", {"limit": 0})
    assert "1 of 4" in text.splitlines()[0]  # clamped to >=1
    text, _ = await tool.call("social_timeline", {"limit": 999})
    assert len(text.splitlines()) == 5  # clamped to the cap, still all 4


@pytest.mark.asyncio
async def test_tool_empty_and_unknown_cases(log: SocialEventLog):
    tool = SocialTimelineTool(log)
    text, _ = await tool.call("social_timeline", {})
    assert text == "No social events recorded yet."
    text, _ = await tool.call("social_timeline", {"kind": "nope"})
    assert text.startswith("Error: unknown kind")
    text, _ = await tool.call("nope", {})
    assert text.startswith("Error: unknown social-timeline tool")
    missing = SocialTimelineTool(None)
    text, _ = await missing.call("social_timeline", {})
    assert text == "Error: social event log is unavailable."


# ── capability + registry wiring ──


def test_capability_exposes_social_timeline():
    cap = SocialTimelineCapability(SocialTimelineTool(MagicMock()))
    assert {spec.name for spec in cap.specs()} == {"social_timeline"}
    assert DEFAULT_SOCIAL_TIMELINE_TOOLS == {"social_timeline"}


def test_capabilities_package_exports_social_timeline():
    import familiar_capabilities

    assert "SocialTimelineCapability" in familiar_capabilities.__all__


def test_build_tool_registry_includes_social_timeline(log: SocialEventLog):
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    for attr in ("_camera", "_mobility", "_tts", "_mcp"):
        setattr(agent, attr, None)
    for attr in ("_memory_tool", "_tom_tool", "_coding"):
        m = MagicMock()
        m.call = AsyncMock(return_value=("ok", None))
        setattr(agent, attr, m)
    names = {spec["name"] for spec in agent._build_tool_registry().tool_defs()}
    assert "social_timeline" not in names  # no tool attr → byte-stable registry
    agent._social_timeline_tool = SocialTimelineTool(log)
    names = {spec["name"] for spec in agent._build_tool_registry().tool_defs()}
    assert "social_timeline" in names


def test_agent_wires_one_log_into_every_emitter(tmp_path: Path):
    """The agent constructs a single SocialEventLog and hands it to each emitter."""
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent.config = MagicMock()
    agent.config.companion_name = "Kouta"
    agent._memory = MagicMock()
    agent._person_model = PersonModelTracker(db_path=tmp_path / "pm.db")
    agent._commitment_store = SQLiteCommitmentStore(tmp_path / "c.db")
    agent._identity = IdentityCore(None, state_path=tmp_path / "identity_state.json")
    agent._relationship = RelationshipTracker(
        state_path=tmp_path / "rel.json", db_path=tmp_path / "rel.db"
    )
    with patch(
        "familiar_agent.agent.SocialEventLog",
        return_value=SocialEventLog(db_path=tmp_path / "obs.db", default_person="Kouta"),
    ) as ctor:
        agent._init_social_events()
    ctor.assert_called_once()
    assert ctor.call_args.kwargs.get("default_person") == "Kouta"
    log = agent._social_events
    assert isinstance(log, SocialEventLog)
    assert agent._person_model.event_log is log
    assert agent._commitment_store.event_log is log
    assert agent._identity.event_log is log
    assert agent._relationship.event_log is log
    assert agent._social_timeline_tool._log is log
    agent._relationship.note_trust_shift(0.9, "x")
    assert log.count(kind="trust_shift") == 1
    agent._commitment_store.close()
    agent._relationship.close()
    log.close()


def test_agent_social_events_init_failure_is_dormant(tmp_path: Path):
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent.config = MagicMock()
    agent.config.companion_name = "Kouta"
    agent._relationship = RelationshipTracker(
        state_path=tmp_path / "rel.json", db_path=tmp_path / "rel.db"
    )
    with patch("familiar_agent.agent.SocialEventLog", side_effect=RuntimeError("boom")):
        agent._init_social_events()
    assert agent._social_events is None
    assert agent._social_timeline_tool is None
    assert agent._relationship.event_log is None
    agent._relationship.close()


# ── concurrency, retention, shutdown ──


def test_concurrent_appends_from_threads_all_land(tmp_path: Path):
    import threading

    ledger = SocialEventLog(db_path=tmp_path / "obs.db")
    ledger.append("repair", source="warm")  # open the connection on the main thread
    per_thread = 25
    errors: list[BaseException] = []

    def worker(idx: int) -> None:
        try:
            for j in range(per_thread):
                assert ledger.append("repair", source=f"t{idx}", payload={"j": j}) is not None
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert ledger.count() == 1 + 8 * per_thread
    ledger.close()


def test_append_prunes_rows_older_than_retention(tmp_path: Path):
    from datetime import datetime, timedelta, timezone

    from familiar_neighbor.mind.social_events import PRUNE_EVERY

    ledger = SocialEventLog(db_path=tmp_path / "obs.db", retention_days=2, max_rows=10_000)
    stale_ts = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
    fresh_ts = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    db = ledger._ensure_db()
    for i, ts in enumerate([stale_ts, stale_ts, fresh_ts]):
        db.execute(
            "INSERT INTO social_events (id, ts, source, kind, payload_json) VALUES (?, ?, ?, ?, ?)",
            (f"seed{i}", ts, "seed", "repair", "{}"),
        )
    db.commit()
    assert ledger.count() == 3
    for _ in range(PRUNE_EVERY - 1):
        ledger.append("repair", source="x")
    assert ledger.count() == 3 + PRUNE_EVERY - 1  # not yet pruned
    ledger.append("repair", source="x")  # the PRUNE_EVERY-th append prunes
    assert ledger.count() == 1 + PRUNE_EVERY
    ids = {e.id for e in ledger.recent(limit=200)}
    assert "seed2" in ids and "seed0" not in ids and "seed1" not in ids
    ledger.close()


def test_append_prunes_oldest_rows_beyond_max_rows(tmp_path: Path):
    from familiar_neighbor.mind.social_events import PRUNE_EVERY

    cap = 30
    ledger = SocialEventLog(db_path=tmp_path / "obs.db", retention_days=365, max_rows=cap)
    kept: list[str] = []
    for i in range(PRUNE_EVERY):
        ev = ledger.append("repair", source="x", payload={"i": i})
        assert ev is not None
        kept.append(ev.id)
    assert ledger.count() == cap
    survivors = {e.id for e in ledger.recent(limit=200)}
    assert survivors == set(kept[-cap:])  # newest survive, oldest dropped
    ledger.close()


@pytest.mark.asyncio
async def test_agent_close_closes_social_events_and_narrative_store():
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent._camera = None
    agent._mcp = None
    agent._memory = MagicMock()
    agent.backend = MagicMock()
    agent._utility_backend = agent.backend
    agent._drain_background_tasks = AsyncMock()  # type: ignore[method-assign]
    agent._write_today_narrative = AsyncMock(return_value="")  # type: ignore[method-assign]
    agent._write_today_daybook = AsyncMock()  # type: ignore[method-assign]
    agent._social_events = MagicMock()
    agent._narrative_store = MagicMock()
    agent._narrative_store.close.side_effect = RuntimeError("boom")  # must be swallowed
    await agent.close()
    agent._social_events.close.assert_called_once()
    agent._narrative_store.close.assert_called_once()
