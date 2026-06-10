"""Tests for the persistent person model (Phase 4: ToM accumulation).

The PersonModelTracker stores per-person mental-state inferences produced by
the ToM tool, so the agent accumulates a model of each person instead of
re-inferring from scratch every turn.
"""

from __future__ import annotations

import sqlite3

import pytest

from familiar_neighbor.mind.person_model import PersonModelTracker


@pytest.fixture
def tracker(tmp_path):
    t = PersonModelTracker(db_path=tmp_path / "observations.db")
    yield t
    t.close()


def test_record_and_recent_roundtrip(tracker):
    tracker.record_inference(
        person="kota",
        states=[("tired but satisfied", 0.8), ("wants quiet company", 0.6)],
        evidence=["said 'おつかれ'", "short replies"],
        policy="keep it brief and warm",
    )
    rows = tracker.recent("kota", n=5)
    assert len(rows) == 2
    states = {r["state"] for r in rows}
    assert states == {"tired but satisfied", "wants quiet company"}
    assert rows[0]["policy"] == "keep it brief and warm"
    assert rows[0]["confidence"] in (0.8, 0.6)


def test_recent_returns_newest_first(tracker):
    tracker.record_inference(person="kota", states=[("old", 0.5)], evidence=[], policy="")
    tracker.record_inference(person="kota", states=[("new", 0.5)], evidence=[], policy="")
    rows = tracker.recent("kota", n=2)
    assert rows[0]["state"] == "new"


def test_recent_filters_by_person(tracker):
    tracker.record_inference(person="kota", states=[("a", 0.5)], evidence=[], policy="")
    tracker.record_inference(person="akari", states=[("b", 0.5)], evidence=[], policy="")
    assert {r["state"] for r in tracker.recent("kota", n=10)} == {"a"}


def test_context_for_prompt_renders_states_and_policy(tracker):
    tracker.record_inference(
        person="kota",
        states=[("worried about deadline", 0.7)],
        evidence=[],
        policy="validate first, no advice",
    )
    ctx = tracker.context_for_prompt("kota")
    assert "Person model" in ctx
    assert "kota" in ctx
    assert "worried about deadline" in ctx
    assert "validate first, no advice" in ctx


def test_context_for_prompt_empty_for_unknown_person(tracker):
    assert tracker.context_for_prompt("nobody") == ""


def test_persists_across_reopen(tmp_path):
    path = tmp_path / "observations.db"
    t1 = PersonModelTracker(db_path=path)
    t1.record_inference(person="kota", states=[("calm", 0.9)], evidence=["tone"], policy="p")
    t1.close()

    t2 = PersonModelTracker(db_path=path)
    assert t2.recent("kota", n=1)[0]["state"] == "calm"
    t2.close()


def test_migration_creates_table(tmp_path):
    path = tmp_path / "observations.db"
    t = PersonModelTracker(db_path=path)
    t.record_inference(person="x", states=[("s", 0.1)], evidence=[], policy="")
    t.close()
    conn = sqlite3.connect(path)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert "person_inferences" in tables


# ── ToM writeback ──


class _JSONBackend:
    """Fake utility backend returning a fixed ToM JSON payload."""

    def __init__(self, payload: str) -> None:
        self._payload = payload

    async def complete(self, prompt: str, max_tokens: int) -> str:
        return self._payload


class _FakeMemory:
    async def recall_async(self, query: str, n: int = 5) -> list[dict]:
        return []


@pytest.mark.asyncio
async def test_tom_tool_writes_back_to_person_model(tmp_path):
    from familiar_agent.tools.tom import ToMTool

    tracker = PersonModelTracker(db_path=tmp_path / "observations.db")
    backend = _JSONBackend(
        '{"evidence": ["short reply"], '
        '"inference": [{"state": "exhausted", "confidence": 0.85}], '
        '"policy": "let him rest"}'
    )
    tool = ToMTool(_FakeMemory(), default_person="kota", backend=backend, person_model=tracker)

    text, image = await tool.call("tom", {"situation": "「もう寝るわ」とだけ言った"})

    assert image is None
    assert "exhausted" in text
    rows = tracker.recent("kota", n=5)
    assert len(rows) == 1
    assert rows[0]["state"] == "exhausted"
    assert rows[0]["confidence"] == pytest.approx(0.85)
    assert rows[0]["policy"] == "let him rest"
    tracker.close()


@pytest.mark.asyncio
async def test_tom_tool_without_person_model_still_works(tmp_path):
    from familiar_agent.tools.tom import ToMTool

    backend = _JSONBackend('{"evidence": [], "inference": [], "policy": "p"}')
    tool = ToMTool(_FakeMemory(), default_person="kota", backend=backend)
    text, _ = await tool.call("tom", {"situation": "hello"})
    assert "kota" in text


@pytest.mark.asyncio
async def test_tom_writeback_failure_does_not_break_tool(tmp_path):
    from familiar_agent.tools.tom import ToMTool

    class _BrokenTracker:
        def record_inference(self, **kwargs):
            raise RuntimeError("db locked")

    backend = _JSONBackend(
        '{"evidence": [], "inference": [{"state": "ok", "confidence": 0.5}], "policy": "p"}'
    )
    tool = ToMTool(
        _FakeMemory(), default_person="kota", backend=backend, person_model=_BrokenTracker()
    )
    text, _ = await tool.call("tom", {"situation": "hello"})
    assert "ok" in text  # tool output unaffected by writeback failure


# ── agent surface ──


def test_agent_person_model_context_surfaces(tmp_path):
    import types

    from familiar_agent.agent import EmbodiedAgent

    tracker = PersonModelTracker(db_path=tmp_path / "observations.db")
    tracker.record_inference(
        person="kota", states=[("misses conversation", 0.7)], evidence=[], policy="reach out"
    )
    stub = types.SimpleNamespace(
        _person_model=tracker,
        config=types.SimpleNamespace(companion_name="kota"),
    )
    ctx = EmbodiedAgent._person_model_context(stub)
    assert "misses conversation" in ctx
    tracker.close()


def test_agent_person_model_context_empty_without_tracker():
    import types

    from familiar_agent.agent import EmbodiedAgent

    stub = types.SimpleNamespace(
        _person_model=None,
        config=types.SimpleNamespace(companion_name="kota"),
    )
    assert EmbodiedAgent._person_model_context(stub) == ""


@pytest.mark.asyncio
async def test_tom_canonicalizes_companion_case_variants(tmp_path):
    """'Kota' must be stored under the canonical companion key 'kota' so the
    accumulated model actually surfaces (person-key fragmentation guard)."""
    from familiar_agent.tools.tom import ToMTool

    tracker = PersonModelTracker(db_path=tmp_path / "observations.db")
    backend = _JSONBackend(
        '{"evidence": [], "inference": [{"state": "cheerful", "confidence": 0.6}], "policy": ""}'
    )
    tool = ToMTool(_FakeMemory(), default_person="kota", backend=backend, person_model=tracker)

    await tool.call("tom", {"situation": "smiled", "person": "Kota"})

    assert tracker.recent("kota", n=5)[0]["state"] == "cheerful"
    tracker.close()


def test_recent_reads_case_insensitively(tracker):
    tracker.record_inference(person="Kota", states=[("calm", 0.5)], evidence=[], policy="")
    assert tracker.recent("kota", n=5)[0]["state"] == "calm"


def test_context_for_prompt_excludes_stale_inferences(tracker):
    """Inferences older than the max age must not steer the agent."""
    from datetime import datetime, timedelta, timezone

    tracker.record_inference(person="kota", states=[("fresh mood", 0.6)], evidence=[], policy="")
    # Inject an old row directly (record_inference always stamps now).
    old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    db = tracker._ensure_db()
    db.execute(
        "INSERT INTO person_inferences (id, person, state, confidence, evidence_json,"
        " policy, source, created_at) VALUES ('pinf_old', 'kota', 'ancient mood', 0.9,"
        " '[]', '', 'tom', ?)",
        (old,),
    )
    db.commit()

    ctx = tracker.context_for_prompt("kota")
    assert "fresh mood" in ctx
    assert "ancient mood" not in ctx


def test_unparseable_created_at_treated_as_stale(tracker):
    tracker.record_inference(person="kota", states=[("fresh", 0.5)], evidence=[], policy="")
    db = tracker._ensure_db()
    db.execute(
        "INSERT INTO person_inferences (id, person, state, confidence, evidence_json,"
        " policy, source, created_at) VALUES ('pinf_bad', 'kota', 'garbled', 0.9,"
        " '[]', '', 'tom', 'not-a-timestamp')"
    )
    db.commit()
    ctx = tracker.context_for_prompt("kota")
    assert "fresh" in ctx
    assert "garbled" not in ctx
