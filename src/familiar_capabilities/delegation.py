"""Delegation capability adapter for the generic runtime (background tasks)."""

from __future__ import annotations

from familiar_agent.tools.delegation import DelegationTool
from familiar_runtime.tools.legacy import LegacyToolProvider

DEFAULT_DELEGATION_TOOLS = {
    "delegate_task",
    "check_delegated_tasks",
}


class DelegationCapability(LegacyToolProvider):
    """Expose the DelegationTool through the ToolProvider protocol."""

    def __init__(self, tool: DelegationTool, *, names: set[str] | None = None) -> None:
        super().__init__(
            tool,
            names=set(names) if names is not None else set(DEFAULT_DELEGATION_TOOLS),
            category="delegation",
            tags={"neighbor", "secretary"},
        )
