"""Voice (TTS) capability adapter for the generic runtime."""

from __future__ import annotations

from familiar_agent.tools.tts import TTSTool
from familiar_runtime.tools.legacy import LegacyToolProvider


class VoiceCapability(LegacyToolProvider):
    """Expose the existing TTSTool through the ToolProvider protocol."""

    def __init__(self, tool: TTSTool) -> None:
        super().__init__(
            tool,
            names={"say"},
            category="voice",
            tags={"neighbor", "speech"},
        )
