"""Generic memory interfaces for the agent runtime.

Task mode and neighbour mode share the same store boundaries even though
neighbour mode layers an autobiographical / relational projection on top.
The protocols defined here capture only what runtime hooks and task tools
need; the neighbour-specific projection (self-narrative, relationship,
unfinished business) keeps living in :mod:`familiar_agent`.
"""

from .base import (
    MemoryStore,
    ObservationRecord,
    RecallResult,
)

__all__ = [
    "MemoryStore",
    "ObservationRecord",
    "RecallResult",
]
