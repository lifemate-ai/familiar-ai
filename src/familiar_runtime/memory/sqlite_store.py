"""SQLite-backed ``MemoryStore`` adapter around the legacy ObservationMemory.

This adapter does not duplicate the existing schema; it wraps a live
``familiar_agent.tools.memory.ObservationMemory`` instance and translates
its API to the narrow runtime protocol (:class:`MemoryStore`). Callers
keep ownership of the underlying store and remain responsible for opening
/ closing it.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from .base import MemoryStore, ObservationRecord, RecallResult

if TYPE_CHECKING:
    from familiar_agent.tools.memory import ObservationMemory


_KNOWN_KINDS = {"observation", "feeling", "conversation"}
_KNOWN_EMOTIONS = {"neutral", "happy", "sad", "curious", "excited", "moved"}


def _record_from_row(row: Any) -> ObservationRecord:
    """Build an ObservationRecord from either a sqlite Row or a recall dict."""
    if hasattr(row, "keys"):
        keys = set(row.keys())
        record_id = row["memory_id"] if "memory_id" in keys else row["id"]
        text = row["summary"] if "summary" in keys else row["content"]
        timestamp = row["timestamp"] if "timestamp" in keys else ""
        metadata = {
            key: row[key]
            for key in keys
            if key not in {"id", "memory_id", "content", "summary", "timestamp"}
        }
        return ObservationRecord(
            id=str(record_id),
            text=str(text),
            created_at=str(timestamp),
            metadata=metadata,
        )
    raise TypeError(f"Unsupported row type for ObservationRecord: {type(row).__name__}")


class SQLiteMemoryStore(MemoryStore):
    """MemoryStore that delegates to an existing ObservationMemory.

    The wrapped store keeps its full neighbour-specific surface (semantic facts,
    behavior policies, importance decay, supersession). The adapter exposes only
    the three operations the runtime contract requires.
    """

    def __init__(self, store: "ObservationMemory") -> None:
        self._store = store

    async def save_observation(
        self,
        text: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        meta = dict(metadata or {})
        direction = str(meta.pop("direction", "unknown"))
        kind = str(meta.pop("kind", "observation"))
        emotion = str(meta.pop("emotion", "neutral"))
        image_path = meta.pop("image_path", None)
        if kind not in _KNOWN_KINDS:
            kind = "observation"
        if emotion not in _KNOWN_EMOTIONS:
            emotion = "neutral"
        observation_id, ok = await self._store.save_async_with_id(
            text,
            direction=direction,
            kind=kind,
            emotion=emotion,
            image_path=image_path,
        )
        if not ok or observation_id is None:
            raise RuntimeError("ObservationMemory.save_async_with_id failed")
        return str(observation_id)

    async def recall(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[RecallResult]:
        rows = await self._store.recall_async(query, n=limit)
        results: list[RecallResult] = []
        for row in rows:
            record = ObservationRecord(
                id=str(row.get("memory_id", row.get("id", ""))),
                text=str(row.get("summary", row.get("content", ""))),
                created_at=str(row.get("timestamp", "")),
                metadata={
                    key: value
                    for key, value in row.items()
                    if key not in {"memory_id", "id", "summary", "content", "timestamp", "score"}
                },
            )
            score = float(row.get("score", row.get("similarity", 1.0)) or 1.0)
            results.append(RecallResult(record=record, score=score))
        return results

    async def recent(self, *, limit: int = 10) -> list[ObservationRecord]:
        def _query() -> list[ObservationRecord]:
            with self._store._db_lock:  # type: ignore[attr-defined]
                conn = self._store._ensure_connected()  # type: ignore[attr-defined]
                rows = conn.execute(
                    "SELECT id, content, timestamp, date, time, direction, kind, emotion, "
                    "image_path FROM observations WHERE superseded_by IS NULL "
                    "ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [_record_from_row(row) for row in rows]

        return await asyncio.to_thread(_query)
