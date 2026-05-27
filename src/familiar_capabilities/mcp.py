"""MCP capability adapter for the generic runtime."""

from __future__ import annotations

from familiar_agent.mcp_client import MCPClientManager
from familiar_runtime.tools.legacy import LegacyToolProvider


class MCPCapability(LegacyToolProvider):
    """Expose MCPClientManager tools through ToolProvider."""

    def __init__(self, manager: MCPClientManager) -> None:
        super().__init__(manager, category="mcp", tags={"task", "neighbor"})
