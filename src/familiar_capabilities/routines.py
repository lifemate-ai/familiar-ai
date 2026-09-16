"""Routine capability — self-authored recurring schedule tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

from familiar_runtime.tools.legacy import LegacyToolProvider

if TYPE_CHECKING:
    from familiar_agent.tools.routines_tool import RoutineTool

DEFAULT_ROUTINE_TOOLS = {"routine_commit", "routine_review", "routine_drop"}


class RoutineCapability(LegacyToolProvider):
    """Expose the routine tools through the runtime tool registry."""

    def __init__(self, tool: RoutineTool, *, names: set[str] | None = None) -> None:
        super().__init__(
            tool,
            names=set(names) if names is not None else set(DEFAULT_ROUTINE_TOOLS),
            category="identity",
            tags={"neighbor", "routine", "self"},
        )
