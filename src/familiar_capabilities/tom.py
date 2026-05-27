"""Theory-of-Mind capability adapter for the generic runtime."""

from __future__ import annotations

from familiar_agent.tools.tom import ToMTool
from familiar_runtime.tools.legacy import LegacyToolProvider


class ToMCapability(LegacyToolProvider):
    """Expose the existing ToMTool through the ToolProvider protocol."""

    def __init__(self, tool: ToMTool) -> None:
        super().__init__(
            tool,
            names={"tom"},
            category="cognition",
            tags={"neighbor", "social"},
        )
