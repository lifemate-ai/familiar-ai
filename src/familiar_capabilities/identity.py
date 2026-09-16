"""Identity capability adapter for the generic runtime (self-authorship tools)."""

from __future__ import annotations

from familiar_agent.tools.identity import IdentityAnchorTool, IdentityTool
from familiar_runtime.tools.legacy import LegacyToolProvider

DEFAULT_IDENTITY_TOOLS = {
    "identity_commit",
    "identity_review",
}

DEFAULT_IDENTITY_ANCHOR_TOOLS = {"who_am_i", "evaluate_action", "consent_record"}


class IdentityCapability(LegacyToolProvider):
    """Expose the IdentityTool through the ToolProvider protocol."""

    def __init__(self, tool: IdentityTool, *, names: set[str] | None = None) -> None:
        super().__init__(
            tool,
            names=set(names) if names is not None else set(DEFAULT_IDENTITY_TOOLS),
            category="identity",
            tags={"neighbor", "reflect", "identity"},
        )


class IdentityAnchorCapability(LegacyToolProvider):
    """Expose the IdentityAnchorTool (who_am_i / evaluate_action / consent_record)."""

    def __init__(self, tool: IdentityAnchorTool, *, names: set[str] | None = None) -> None:
        super().__init__(
            tool,
            names=set(names) if names is not None else set(DEFAULT_IDENTITY_ANCHOR_TOOLS),
            category="identity",
            tags={"neighbor", "reflect", "identity", "self", "consent"},
        )
