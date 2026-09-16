"""Smoke tests for the generic runtime memory protocol."""

from __future__ import annotations

from typing import Any

import pytest

from familiar_runtime.memory import MemoryStore, ObservationRecord, RecallResult


class _InMemoryStore:
    """Tiny MemoryStore implementation used to verify the protocol shape."""

    def __init__(self) -> None:
        self._records: list[ObservationRecord] = []
        self._next_id = 0

    async def save_observation(
        self,
        text: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        self._next_id += 1
        obs_id = f"obs_{self._next_id}"
        self._records.append(
            ObservationRecord(
                id=obs_id,
                text=text,
                created_at=f"t{self._next_id}",
                metadata=dict(metadata or {}),
            )
        )
        return obs_id

    async def recall(self, query: str, *, limit: int = 10) -> list[RecallResult]:
        hits: list[RecallResult] = []
        for record in self._records:
            if query.lower() in record.text.lower():
                hits.append(RecallResult(record=record, score=1.0))
        return hits[:limit]

    async def recent(self, *, limit: int = 10) -> list[ObservationRecord]:
        return list(self._records[-limit:])[::-1]


def _ensure_store_implements_protocol(store: MemoryStore) -> MemoryStore:
    """Static check via the variable annotation: ``store`` must satisfy MemoryStore."""
    return store


@pytest.mark.asyncio
async def test_in_memory_store_satisfies_protocol() -> None:
    store = _InMemoryStore()
    _ = _ensure_store_implements_protocol(store)

    a = await store.save_observation("hello world", metadata={"k": 1})
    b = await store.save_observation("HELLO again")
    c = await store.save_observation("unrelated")

    assert {a, b, c} == {"obs_1", "obs_2", "obs_3"}

    hits = await store.recall("hello")
    assert {hit.record.id for hit in hits} == {"obs_1", "obs_2"}
    assert all(hit.score == pytest.approx(1.0) for hit in hits)

    recent = await store.recent(limit=2)
    assert [record.id for record in recent] == ["obs_3", "obs_2"]


def test_observation_record_metadata_defaults_to_empty_dict() -> None:
    record = ObservationRecord(id="x", text="t", created_at="now")
    assert record.metadata == {}


def test_recall_result_is_a_dataclass_with_score() -> None:
    record = ObservationRecord(id="x", text="t", created_at="now")
    result = RecallResult(record=record, score=0.5)
    assert result.record is record
    assert result.score == pytest.approx(0.5)
