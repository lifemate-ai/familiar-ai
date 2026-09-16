"""Narrative capability — life arcs, daybook and self summary as tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

from familiar_runtime.tools.legacy import LegacyToolProvider

if TYPE_CHECKING:
    from familiar_agent.tools.narrative import NarrativeTool

DEFAULT_NARRATIVE_TOOLS = {"arc_commit", "arc_review", "arc_close", "self_summary"}


class NarrativeCapability(LegacyToolProvider):
    """Expose the NarrativeTool through the ToolProvider protocol."""

    def __init__(self, tool: NarrativeTool, *, names: set[str] | None = None) -> None:
        super().__init__(
            tool,
            names=set(names) if names is not None else set(DEFAULT_NARRATIVE_TOOLS),
            category="identity",
            tags={"neighbor", "reflect", "identity", "self", "narrative"},
        )
