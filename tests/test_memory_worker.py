"""Tests for background memory job worker."""

from __future__ import annotations

import sqlite3
from unittest.mock import patch

import pytest

from familiar_agent.memory_worker import MemoryJobWorker, MemoryWorkerConfig
from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@pytest.mark.asyncio
async def test_worker_materializes_memory_save_jobs(tmp_path) -> None:
    db_path = str(tmp_path / "worker_ok.db")
    with (
        patch.object(_EmbeddingModel, "pre_warm"),
        patch.object(_EmbeddingModel, "encode_document", return_value=[[0.1, 0.2, 0.3]]),
    ):
        mem = ObservationMemory(db_path=db_path)
        payload = {
            "content": "queued memory",
            "direction": "unknown",
            "kind": "conversation",
            "emotion": "neutral",
            "image_path": None,
            "override_date": None,
        }
        event_id, created = mem.append_memory_event("memory.save", payload, queue_job=True)
        assert created is True
        assert event_id is not None

        worker = MemoryJobWorker(mem, MemoryWorkerConfig(batch_size=4, retry_delay_sec=0.0))
        processed = await worker.run_once()
        assert processed == 1
        mem.close()

    with _connect(db_path) as conn:
        obs = conn.execute("SELECT content FROM observations WHERE id = ?", (event_id,)).fetchone()
        job = conn.execute("SELECT status, attempts FROM memory_jobs").fetchone()
    assert obs is not None
    assert obs["content"] == "queued memory"
    assert job["status"] == "done"
    assert job["attempts"] == 1


@pytest.mark.asyncio
async def test_worker_retries_then_dead_letters_failed_jobs(tmp_path) -> None:
    db_path = str(tmp_path / "worker_retry.db")
    with (
        patch.object(_EmbeddingModel, "pre_warm"),
        patch.object(_EmbeddingModel, "encode_document", return_value=[[0.1, 0.2, 0.3]]),
    ):
        mem = ObservationMemory(db_path=db_path)
        event_id, created = mem.append_memory_event(
            "memory.unknown",
            {"content": "bad event"},
            queue_job=True,
        )
        assert created is True
        assert event_id is not None

        worker = MemoryJobWorker(
            mem,
            MemoryWorkerConfig(batch_size=2, retry_delay_sec=0.0, max_attempts=2),
        )
        first = await worker.run_once()
        second = await worker.run_once()
        assert first == 1
        assert second == 1
        mem.close()

    with _connect(db_path) as conn:
        row = conn.execute("SELECT status, attempts, last_error FROM memory_jobs").fetchone()
    assert row is not None
    assert row["status"] == "dead_letter"
    assert row["attempts"] == 2
    assert row["last_error"]
