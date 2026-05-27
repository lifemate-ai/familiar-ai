"""Memory capability adapter for the generic runtime."""

from __future__ import annotations

from familiar_agent.tools.memory import MemoryTool
from familiar_runtime.tools.legacy import LegacyToolProvider

DEFAULT_MEMORY_TOOLS = {"remember", "recall", "recall_divergent", "get_working_memory"}


class MemoryCapability(LegacyToolProvider):
    """Expose the existing MemoryTool through the ToolProvider protocol.

    The capability wraps an already-constructed MemoryTool so callers keep
    control over the ObservationMemory backing store (DB path, embedding model).
    The optional ``names`` argument lets profiles expose a subset (e.g. the
    neighbour profile historically only registers ``{"remember", "recall"}``).
    """

    def __init__(self, tool: MemoryTool, *, names: set[str] | None = None) -> None:
        super().__init__(
            tool,
            names=set(names) if names is not None else set(DEFAULT_MEMORY_TOOLS),
            category="memory",
            tags={"neighbor", "task", "memory"},
        )
