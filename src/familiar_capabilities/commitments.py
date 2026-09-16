"""Commitment capability adapter for the generic runtime (secretary tools)."""

from __future__ import annotations

from familiar_agent.tools.commitments import CommitmentTool
from familiar_runtime.tools.legacy import LegacyToolProvider

DEFAULT_COMMITMENT_TOOLS = {
    "add_commitment",
    "list_commitments",
    "complete_commitment",
    "snooze_commitment",
}


class CommitmentCapability(LegacyToolProvider):
    """Expose the CommitmentTool through the ToolProvider protocol."""

    def __init__(self, tool: CommitmentTool, *, names: set[str] | None = None) -> None:
        super().__init__(
            tool,
            names=set(names) if names is not None else set(DEFAULT_COMMITMENT_TOOLS),
            category="commitment",
            tags={"neighbor", "task", "secretary"},
        )
