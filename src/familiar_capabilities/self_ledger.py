"""Self-ledger capability — who_am_i / note_interpretation_shift."""

from __future__ import annotations

from typing import TYPE_CHECKING

from familiar_runtime.tools.legacy import LegacyToolProvider

if TYPE_CHECKING:
    from familiar_agent.tools.self_ledger import SelfLedgerTool

DEFAULT_SELF_LEDGER_TOOLS = {"who_am_i", "note_interpretation_shift"}


class SelfLedgerCapability(LegacyToolProvider):
    """Expose the self-ledger tools through the runtime tool registry."""

    def __init__(self, tool: SelfLedgerTool, *, names: set[str] | None = None) -> None:
        super().__init__(
            tool,
            names=set(names) if names is not None else set(DEFAULT_SELF_LEDGER_TOOLS),
            category="identity",
            tags={"neighbor", "reflect", "identity", "self"},
        )
