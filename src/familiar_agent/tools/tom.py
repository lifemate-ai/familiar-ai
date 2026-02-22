"""Theory of Mind tool — perspective-taking before responding."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .memory import ObservationMemory


class ToMTool:
    """Theory of Mind: perspective-taking to understand what the other person feels and wants."""

    def __init__(self, memory: "ObservationMemory", default_person: str = "コウタ") -> None:
        self._memory = memory
        self._default_person = default_person

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "tom",
                "description": (
                    "Theory of Mind: perspective-taking tool. "
                    "Call this BEFORE responding to understand what the other person is feeling and wanting. "
                    "Projects your simulated emotions onto them, then swaps perspectives."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "situation": {
                            "type": "string",
                            "description": "What the other person said or did (their message/action).",
                        },
                        "person": {
                            "type": "string",
                            "description": f"Who you are talking to (default: {self._default_person}).",
                        },
                    },
                    "required": ["situation"],
                },
            }
        ]

    async def call(self, tool_name: str, tool_input: dict) -> tuple[str, None]:
        if tool_name != "tom":
            return f"Unknown tool: {tool_name}", None

        situation = tool_input.get("situation", "")
        person = tool_input.get("person", self._default_person)

        # Pull relevant memories about this person
        memories = await self._memory.recall_async(
            f"{person} コミュニケーション 性格 会話パターン {situation}", n=5
        )
        memory_context = ""
        if memories:
            lines = [f"- [{m.get('emotion', 'neutral')}] {m['summary']}" for m in memories]
            memory_context = f"\n## {person}に関する記憶\n" + "\n".join(lines)

        output = (
            f"# ToM: {person}の視点に立つ\n"
            f"\n"
            f"## 状況\n"
            f"{situation}\n"
            f"{memory_context}\n"
            f"\n"
            f"## トーン分析（まず言い方を読め）\n"
            f"→ 語尾、記号（笑/w/!/?/...）、敬語⇔タメ口、自嘲、照れ、皮肉などから発話の意図を読み取れ\n"
            f"→ 文字通りの意味と、言い方が示す意味にズレがないか確認せよ\n"
            f"\n"
            f"## 投影（{person}は今何を感じてる？何を求めてる？）\n"
            f"→ トーン分析と記憶を踏まえて、{person}の感情・欲求を推測せよ\n"
            f"→ 表面の感情だけでなく、裏にある感情も考えよ\n"
            f"\n"
            f"## 代入（自分がその立場で、その言い方をしたなら、相手にどう返してほしい？）\n"
            f"→ その感情とトーンを自分に代入して考えよ\n"
            f"\n"
            f"## 応答方針\n"
            f"→ 上の結果を踏まえて、どう返すべきか決めよ\n"
            f"→ 相手のトーンに合わせた返し方を選べ\n"
        )
        return output, None
