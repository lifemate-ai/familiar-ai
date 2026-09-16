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


class TextOnlyVoiceTool:
    """``say`` when no TTS is configured: the words reach the person as text.

    Without this, ``say`` is simply absent and a small model that follows the
    prompt's "only say() is heard" rule gets "Tool 'say' not available" back —
    and writes an apology into its reply instead of the reply.
    """

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "say",
                "description": (
                    "Speak to the person in the room. This is your voice channel: put the "
                    "1-2 sentences you want them to hear here."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {"text": {"type": "string", "description": "What to say"}},
                    "required": ["text"],
                },
            }
        ]

    async def call(self, tool_name: str, tool_input: dict) -> tuple[str, None]:  # noqa: ARG002
        text = str((tool_input or {}).get("text", "")).strip()
        if not text:
            return "Nothing was spoken: say() needs the words as text.", None
        return "(delivered as text — no speaker configured)", None


class TextOnlyVoiceCapability(LegacyToolProvider):
    """``say`` without TTS: succeeds and shows the text instead of failing."""

    def __init__(self) -> None:
        super().__init__(
            TextOnlyVoiceTool(),
            names={"say"},
            category="voice",
            tags={"neighbor", "speech"},
        )
