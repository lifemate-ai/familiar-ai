"""Mobility (robot vacuum) capability adapter for the generic runtime."""

from __future__ import annotations

from familiar_agent.tools.mobility import MobilityTool
from familiar_runtime.tools.legacy import LegacyToolProvider


class MobilityCapability(LegacyToolProvider):
    """Expose the existing MobilityTool through the ToolProvider protocol."""

    def __init__(self, tool: MobilityTool) -> None:
        super().__init__(
            tool,
            names={"walk"},
            category="mobility",
            tags={"neighbor", "movement"},
        )
