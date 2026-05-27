"""Memory capability adapter for the generic runtime."""

from __future__ import annotations

from familiar_agent.tools.memory import MemoryTool
from familiar_runtime.tools.legacy import LegacyToolProvider


class MemoryCapability(LegacyToolProvider):
    """Expose the existing MemoryTool through the ToolProvider protocol.

    The capability wraps an already-constructed MemoryTool so callers keep
    control over the ObservationMemory backing store (DB path, embedding model).
    """

    def __init__(self, tool: MemoryTool) -> None:
        super().__init__(
            tool,
            names={"remember", "recall", "recall_divergent", "get_working_memory"},
            category="memory",
            tags={"neighbor", "task", "memory"},
        )
