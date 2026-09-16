"""Generic memory store protocol shared by neighbour and task profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class ObservationRecord:
    """A stored observation visible to runtime hooks and task tools.

    Mirrors the historical familiar_agent observation row in spirit but only
    exposes the fields the runtime cares about. Provider-specific metadata
    (importance decay, superseded_by, embeddings) lives in ``metadata``.
    """

    id: str
    text: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RecallResult:
    """A single recall hit with a similarity score."""

    record: ObservationRecord
    score: float


class MemoryStore(Protocol):
    """Minimum surface a runtime profile needs from a memory backend.

    Concrete implementations may expose additional methods (semantic facts,
    episode tracking, working-memory windows, behaviour policies). The
    protocol intentionally stays narrow so task mode can run without ever
    pulling in neighbour-specific projections.
    """

    async def save_observation(
        self,
        text: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Persist a new observation and return its identifier."""

    async def recall(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[RecallResult]:
        """Return observations semantically similar to ``query``."""

    async def recent(self, *, limit: int = 10) -> list[ObservationRecord]:
        """Return the ``limit`` most recently stored observations."""
