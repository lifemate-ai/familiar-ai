"""Moonshot AI Kimi K2.5 backend (reasoning_content round-trip)."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

from .base import ModelTurnResult, ToolCall

logger = logging.getLogger(__name__)


class KimiBackend:
    """Backend for Moonshot AI Kimi K2.5.

    Kimi K2.5 uses an OpenAI-compatible API but includes a ``reasoning_content``
    field on assistant messages when thinking is active.  That field must be
    round-tripped back in subsequent turns or the API returns:
      "thinking is enabled but reasoning_content is missing in assistant
       tool call message"

    This backend captures ``reasoning_content`` from each streaming chunk
    and preserves it in the raw assistant dict so the conversation history
    stays valid across multi-turn tool-call loops.
    """

    _BASE_URL = "https://api.moonshot.ai/v1"

    def __init__(self, api_key: str, model: str) -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key, base_url=self._BASE_URL)
        self.model = model

    # ── message factories (same as OpenAICompatibleBackend) ────────

    def make_user_message(self, content: str | list) -> dict:
        return {"role": "user", "content": content}

    def make_assistant_message(self, result: ModelTurnResult, raw_content: Any) -> dict:  # noqa: ARG002
        return raw_content

    def make_tool_results(
        self,
        tool_calls: list[ToolCall],
        results: list[tuple[str, str | None]],
    ) -> list[dict]:
        msgs: list[dict] = []
        for tc, (text, image) in zip(tool_calls, results):
            msgs.append({"role": "tool", "tool_call_id": tc.id, "content": text})
            if image:
                msgs.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                            }
                        ],
                    }
                )
        return msgs

    def make_system_message(self, content: str) -> dict:
        return {"role": "system", "content": content}

    # ── streaming turn ─────────────────────────────────────────────

    async def stream_turn(
        self,
        system: str | tuple[str, str],
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None = None,
    ) -> tuple[ModelTurnResult, Any]:
        if isinstance(system, tuple):
            system = "\n\n---\n\n".join(s for s in system if s)
        # Flatten nested lists (tool results are appended as lists by agent.py)
        flat_messages: list[dict] = [{"role": "system", "content": system}]
        for msg in messages:
            if isinstance(msg, list):
                flat_messages.extend(msg)
            else:
                flat_messages.append(msg)

        logger.debug(
            "KimiBackend request messages: %s",
            json.dumps(flat_messages, ensure_ascii=False, default=str),
        )

        oai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", {}),
                },
            }
            for t in tools
        ]

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": flat_messages,
            "stream": True,
        }
        if oai_tools:
            kwargs["tools"] = oai_tools

        stream = await self.client.chat.completions.create(**kwargs)

        text_chunks: list[str] = []
        reasoning_chunks: list[str] = []
        raw_tcs: dict[int, dict] = {}
        finish_reason: str | None = None

        async for chunk in stream:
            choice = chunk.choices[0]
            delta = choice.delta
            finish_reason = choice.finish_reason or finish_reason

            # Capture reasoning_content (thinking tokens) — must be round-tripped
            rc = getattr(delta, "reasoning_content", None)
            if rc:
                reasoning_chunks.append(rc)

            if delta.content:
                text_chunks.append(delta.content)
                if on_text:
                    on_text(delta.content)

            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    if idx not in raw_tcs:
                        raw_tcs[idx] = {"id": "", "name": "", "arguments": ""}
                    if tc_delta.id:
                        raw_tcs[idx]["id"] = tc_delta.id
                    if tc_delta.function and tc_delta.function.name:
                        raw_tcs[idx]["name"] = tc_delta.function.name
                    if tc_delta.function and tc_delta.function.arguments:
                        raw_tcs[idx]["arguments"] += tc_delta.function.arguments

        text = "".join(text_chunks)
        tool_calls: list[ToolCall] = []
        for idx in sorted(raw_tcs.keys()):
            tc = raw_tcs[idx]
            try:
                input_data = json.loads(tc["arguments"])
            except (json.JSONDecodeError, KeyError):
                input_data = {}
            tool_calls.append(ToolCall(id=tc["id"], name=tc["name"], input=input_data))

        stop = "tool_use" if finish_reason == "tool_calls" else "end_turn"

        # Build raw_assistant — include reasoning_content so Kimi accepts it next turn
        raw_assistant: dict[str, Any] = {"role": "assistant", "content": text or None}
        if reasoning_chunks:
            raw_assistant["reasoning_content"] = "".join(reasoning_chunks)
        if tool_calls:
            raw_assistant["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": json.dumps(tc.input)},
                }
                for tc in tool_calls
            ]
        return (
            ModelTurnResult(stop_reason=stop, text=text, tool_calls=tool_calls),
            raw_assistant,
        )

    async def complete(self, prompt: str, max_tokens: int) -> str:
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            logger.warning("complete() failed: %s", e)
            return ""
