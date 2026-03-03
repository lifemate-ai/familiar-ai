"""Tests for evidence-backed memory recall metadata."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from unittest.mock import patch

from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def test_recall_semantic_includes_evidence_metadata(tmp_path) -> None:
    db_path = str(tmp_path / "recall_semantic.db")
    with (
        patch.object(_EmbeddingModel, "pre_warm"),
        patch.object(_EmbeddingModel, "encode_document", return_value=[[1.0, 0.0, 0.0]]),
        patch.object(_EmbeddingModel, "encode_query", return_value=[[1.0, 0.0, 0.0]]),
    ):
        mem = ObservationMemory(db_path=db_path)
        assert mem.save("saw a cat by the window", kind="observation", emotion="curious")
        rows = mem.recall("cat", n=1)
        mem.close()

    assert len(rows) == 1
    row = rows[0]
    assert row["retrieval_method"] == "semantic"
    assert row["memory_id"]
    assert row["timestamp"]
    assert row["source_kind"] == "observation"
    assert "score" in row
    assert 0.0 <= float(row["confidence"]) <= 1.0


def test_recall_fallback_includes_metadata_and_low_confidence(tmp_path) -> None:
    db_path = str(tmp_path / "recall_fallback.db")
    with patch.object(_EmbeddingModel, "pre_warm"):
        mem = ObservationMemory(db_path=db_path)
        mem.append_memory_event("memory.save", {"content": "seed"}, queue_job=False)
        now = datetime.now()
        with _connect(db_path) as conn:
            conn.execute(
                """
                INSERT INTO observations
                (id, content, timestamp, date, time, direction, kind, emotion, image_path, image_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "legacy-row-1",
                    "older memory without embedding",
                    now.isoformat(),
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M"),
                    "unknown",
                    "conversation",
                    "neutral",
                    None,
                    None,
                ),
            )
            conn.commit()

        rows = mem.recall("", n=1)
        mem.close()

    assert len(rows) == 1
    row = rows[0]
    assert row["retrieval_method"] == "recency"
    assert row["memory_id"] == "legacy-row-1"
    assert row["source_kind"] == "conversation"
    assert float(row["confidence"]) <= 0.55


def test_format_for_context_includes_confidence_guidance() -> None:
    with patch.object(_EmbeddingModel, "pre_warm"):
        mem = ObservationMemory(db_path=":memory:")
    text = mem.format_for_context(
        [
            {
                "memory_id": "abcde12345",
                "date": "2026-03-03",
                "time": "10:00",
                "direction": "unknown",
                "source_kind": "conversation",
                "emotion": "neutral",
                "summary": "something uncertain happened",
                "confidence": 0.3,
            }
        ]
    )
    mem.close()

    assert "conf<0.55" in text
    assert "id:abcde123" in text
    assert "low-confidence" in text
