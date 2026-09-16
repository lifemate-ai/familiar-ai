"""Default Mode Network processor — spontaneous memory recall during idle time.

Inspired by the brain's Default Mode Network (DMN), which activates when the
mind is not focused on external tasks.  The processor wanders through past
memories, surfaces associations as workspace Coalitions, and consolidates
near-duplicate memories.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tools.memory import ObservationMemory
    from .workspace import Coalition

logger = logging.getLogger(__name__)

# Near-duplicate similarity threshold for consolidation
_SIMILARITY_THRESHOLD = 0.85


class DefaultModeProcessor:
    """Generates spontaneous associations from stored memories.

    Parameters
    ----------
    memory:
        A memory backend exposing ``recall_curiosities_async()`` and
        ``find_near_duplicates_async()`` coroutines.
    """

    def __init__(self, memory: ObservationMemory) -> None:
        self._memory = memory
        self._last_coalition: Coalition | None = None

    # ── Public API ────────────────────────────────────────────────────────

    async def wander(self) -> Coalition | None:
        """Recall memories and build a Coalition from the strongest one.

        Returns ``None`` when no memories are available.
        """
        from .workspace import Coalition

        memories = await self._memory.recall_curiosities_async()
        if not memories:
            self._last_coalition = None
            return None

        primary = memories[0]
        summary = primary.get("summary", "")
        importance = float(primary.get("confidence", 0.5))

        activation = max(0.0, min(1.0, importance))
        urgency = 0.1  # wandering is never urgent
        novelty = max(0.0, min(1.0, importance * 0.6))

        context_block = f"[DMN] Spontaneous recall: {summary}"

        coalition = Coalition(
            source="default_mode",
            summary=summary,
            activation=activation,
            urgency=urgency,
            novelty=novelty,
            context_block=context_block,
        )
        self._last_coalition = coalition
        return coalition

    async def consolidate(self) -> int:
        """Find near-duplicate memories and return the count of processable pairs.

        Returns 0 when no duplicates are found.  Never raises on empty memory.
        """
        duplicates = await self._memory.find_near_duplicates_async()
        if not duplicates:
            return 0

        # Each entry is (id_a, id_b, similarity)
        processed = [pair for pair in duplicates if pair[2] >= _SIMILARITY_THRESHOLD]
        return len(processed)

    def as_coalition(self) -> Coalition | None:
        """Return the most recent Coalition produced by :meth:`wander`, or ``None``."""
        return self._last_coalition
