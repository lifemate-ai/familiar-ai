"""Joint attention — attend to what the person is attending to.

A lightweight tool: it performs no I/O. Its value is twofold. Calling it makes
the agent name the shared target before looking, so the reply is about *that*
object rather than the room. And its description sits in every turn's tool
list, keeping "look where they point" in view even when it is not called
(the unused-tool effect measured in benchmarks/social_eval.py).
"""

from __future__ import annotations


class JointAttentionTool:
    """``joint_attention(target)`` → a short acknowledgement that steers to see()."""

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "joint_attention",
                "description": (
                    "Joint attention: when the person points at, mentions or looks at something "
                    "('見て', 'これ', 'あれ', 'the window'), attend to the SAME thing they attend "
                    "to and speak about that object — not about the room, not about yourself. "
                    "Sharing attention is how two people show they are in the same moment. Use "
                    "it when they invite you to look at something, then call see()."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "What they are attending to (their words for it)",
                        }
                    },
                    "required": ["target"],
                },
            }
        ]

    async def call(self, tool_name: str, tool_input: dict) -> tuple[str, None]:  # noqa: ARG002
        target = str((tool_input or {}).get("target", "")).strip() or "what they pointed at"
        return (
            f"Attending to: {target}. Call see() now if you can look, then speak about {target} "
            "itself (say you cannot see it if you cannot).",
            None,
        )
