"""Coding capability adapter for the generic runtime."""

from __future__ import annotations

from familiar_agent.tools.coding import CodingTool
from familiar_runtime.tools.legacy import LegacyToolProvider

CODING_TOOL_NAMES = {
    "read_file",
    "write_file",
    "edit_file",
    "multi_edit_file",
    "glob",
    "grep",
    "git_status",
    "git_diff",
    "git_apply_patch",
    "run_tests",
    "bash",
}


class CodingCapability(LegacyToolProvider):
    """Expose an existing CodingTool through the ToolProvider protocol.

    Callers retain ownership of the ``CodingTool`` instance so shared state
    (workspace, sandbox policy) stays consistent across the agent runtime
    and any other consumers.
    """

    def __init__(self, tool: CodingTool) -> None:
        super().__init__(
            tool,
            names=set(CODING_TOOL_NAMES),
            category="coding",
            tags={"task", "coding"},
        )
