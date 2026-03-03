"""Tests for append-only memory event log and pending job queue."""

from __future__ import annotations

import json
import sqlite3
from unittest.mock import patch

from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def test_save_appends_event_and_pending_job(tmp_path) -> None:
    db_path = str(tmp_path / "memory_events.db")
    with (
        patch.object(_EmbeddingModel, "pre_warm"),
        patch.object(_EmbeddingModel, "encode_document", return_value=[[0.1, 0.2, 0.3]]),
    ):
        mem = ObservationMemory(db_path=db_path)
        assert mem.save("hello world", kind="conversation", emotion="curious")
        mem.close()

    with _connect(db_path) as conn:
        event = conn.execute(
            "SELECT event_id, event_type, payload_json FROM memory_events"
        ).fetchone()
        assert event is not None
        assert event["event_type"] == "memory.save"

        payload = json.loads(event["payload_json"])
        assert payload["content"] == "hello world"
        assert payload["kind"] == "conversation"
        assert payload["emotion"] == "curious"

        job = conn.execute(
            "SELECT job_type, status, attempts FROM memory_jobs WHERE event_id = ?",
            (event["event_id"],),
        ).fetchone()
        assert job is not None
        assert job["job_type"] == "materialize_observation"
        assert job["status"] == "pending"
        assert job["attempts"] == 0


def test_save_with_dedupe_key_is_idempotent(tmp_path) -> None:
    db_path = str(tmp_path / "memory_dedupe.db")
    with (
        patch.object(_EmbeddingModel, "pre_warm"),
        patch.object(_EmbeddingModel, "encode_document", return_value=[[0.1, 0.2, 0.3]]),
    ):
        mem = ObservationMemory(db_path=db_path)
        assert mem.save("same payload", kind="conversation", dedupe_key="turn-1-conversation")
        assert mem.save("same payload", kind="conversation", dedupe_key="turn-1-conversation")
        mem.close()

    with _connect(db_path) as conn:
        event_count = conn.execute("SELECT COUNT(*) FROM memory_events").fetchone()[0]
        job_count = conn.execute("SELECT COUNT(*) FROM memory_jobs").fetchone()[0]
        observation_count = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]

    assert event_count == 1
    assert job_count == 1
    assert observation_count == 1


def test_save_can_enqueue_without_immediate_materialization(tmp_path) -> None:
    db_path = str(tmp_path / "memory_async_queue.db")
    with (
        patch.object(_EmbeddingModel, "pre_warm"),
        patch.object(_EmbeddingModel, "encode_document", return_value=[[0.1, 0.2, 0.3]]),
    ):
        mem = ObservationMemory(db_path=db_path)
        assert mem.save("queued only", kind="conversation", materialize_now=False)
        mem.close()

    with _connect(db_path) as conn:
        event_count = conn.execute("SELECT COUNT(*) FROM memory_events").fetchone()[0]
        job_row = conn.execute("SELECT status FROM memory_jobs").fetchone()
        observation_count = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]

    assert event_count == 1
    assert job_row is not None
    assert job_row["status"] == "pending"
    assert observation_count == 0


def test_save_continues_when_event_append_fails(tmp_path) -> None:
    db_path = str(tmp_path / "memory_fail_open.db")
    with (
        patch.object(_EmbeddingModel, "pre_warm"),
        patch.object(_EmbeddingModel, "encode_document", return_value=[[0.1, 0.2, 0.3]]),
    ):
        mem = ObservationMemory(db_path=db_path)
        with patch.object(mem, "append_memory_event", side_effect=RuntimeError("boom")):
            assert mem.save("still stored despite event failure")
        mem.close()

    with _connect(db_path) as conn:
        event_count = conn.execute("SELECT COUNT(*) FROM memory_events").fetchone()[0]
        observation_count = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]

    assert event_count == 0
    assert observation_count == 1
