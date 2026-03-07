"""Theory of Mind tool — perspective-taking before responding."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .memory import ObservationMemory

logger = logging.getLogger(__name__)


class ToMTool:
    """Theory of Mind: perspective-taking to understand what the other person feels and wants."""

    def __init__(
        self,
        memory: "ObservationMemory",
        default_person: str = "Alex",
        backend: Any | None = None,
    ) -> None:
        self._memory = memory
        self._default_person = default_person
        self._backend = backend

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

        # No backend → return static template (backward compatible)
        if self._backend is None:
            return self._template_output(situation, person, memory_context), None

        # LLM-based inference
        return await self._llm_inference(situation, person, memory_context), None

    async def _llm_inference(self, situation: str, person: str, memory_context: str) -> str:
        assert self._backend is not None  # caller ensures this
        prompt = (
            f"You are a Theory of Mind reasoning engine. "
            f"Analyze what {person} is likely feeling and wanting based on the situation below.\n\n"
            f"Situation: {situation}\n"
            f"{memory_context}\n\n"
            f"Respond with ONLY valid JSON in this exact format:\n"
            f"{{\n"
            f'  "evidence": ["list of behavioral or textual signals you observed"],\n'
            f'  "inference": [\n'
            f'    {{"state": "what they feel or want", "confidence": 0.0}}\n'
            f"  ],\n"
            f'  "policy": "how to respond — tone, content, what to avoid"\n'
            f"}}"
        )

        try:
            raw = await self._backend.complete(prompt, 512)
        except Exception as exc:
            logger.warning("ToM backend call failed: %s", exc)
            return self._template_output(situation, person, memory_context)

        return self._format_response(raw, person)

    def _format_response(self, raw: str, person: str) -> str:
        """Parse JSON response and format as readable ToM output."""
        # Strip markdown code fences if present
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Fallback: wrap raw text in minimal structure
            return f"# ToM: {person}の視点分析\n\n{raw}"

        parts = [f"# ToM: {person}の視点分析\n"]

        evidence = data.get("evidence", [])
        if evidence:
            parts.append("## エビデンス（観察されたシグナル）")
            for item in evidence:
                parts.append(f"- {item}")
            parts.append("")

        inference = data.get("inference", [])
        if inference:
            parts.append("## 推論（心的状態と確信度）")
            for item in inference:
                state = item.get("state", "")
                conf = item.get("confidence", 0.0)
                parts.append(f"- {state} ({conf:.1f})")
            parts.append("")

        policy = data.get("policy", "")
        if policy:
            parts.append("## 応答方針")
            parts.append(policy)

        return "\n".join(parts)

    def _template_output(self, situation: str, person: str, memory_context: str) -> str:
        """Static template fallback (original behavior when no backend)."""
        return (
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
