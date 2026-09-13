"""Social timeline capability — the relational event ledger as a tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

from familiar_runtime.tools.legacy import LegacyToolProvider

if TYPE_CHECKING:
    from familiar_agent.tools.social_timeline import SocialTimelineTool

DEFAULT_SOCIAL_TIMELINE_TOOLS = {"social_timeline"}


class SocialTimelineCapability(LegacyToolProvider):
    """Expose the SocialTimelineTool through the ToolProvider protocol."""

    def __init__(self, tool: SocialTimelineTool, *, names: set[str] | None = None) -> None:
        super().__init__(
            tool,
            names=set(names) if names is not None else set(DEFAULT_SOCIAL_TIMELINE_TOOLS),
            category="social",
            tags={"neighbor", "reflect", "relationship", "social"},
        )
