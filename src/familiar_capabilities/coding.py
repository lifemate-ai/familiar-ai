"""Coding capability adapter for the generic runtime."""

from __future__ import annotations

from familiar_agent.config import CodingConfig
from familiar_agent.tools.coding import CodingTool
from familiar_runtime.tools.legacy import LegacyToolProvider


class CodingCapability(LegacyToolProvider):
    """Expose existing familiar-agent coding tools through ToolProvider."""

    def __init__(self, config: CodingConfig) -> None:
        super().__init__(
            CodingTool(config),
            names={
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
            },
            category="coding",
            tags={"task", "coding"},
        )
