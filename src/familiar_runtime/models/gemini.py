"""Google Gemini backend (native google-genai SDK)."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from typing import Any

from .base import ModelTurnResult, ToolCall

logger = logging.getLogger(__name__)


class GeminiBackend:
    """Backend using the official Google Generative AI SDK (google-generativeai).

    Advantages over OpenAI-compatible endpoint:
    - Native function calling without format hacks
    - thinkingBudget can be set properly (no thinking token leakage)
    - Access to Gemini-specific features
    """

    def __init__(self, api_key: str, model: str) -> None:
        from google import genai
        from google.genai import types

        self._client = genai.Client(api_key=api_key)
        self._types = types
        self.model = model

    # ── message factories ─────────────────────────────────────────

    def make_user_message(self, content: str | list) -> dict:
        if isinstance(content, str):
            return {"role": "user", "parts": [{"text": content}]}
        parts: list[dict[str, Any]] = []
        for item in content:
            if isinstance(item, str):
                parts.append({"text": item})
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append({"text": item["text"]})
                elif item.get("type") == "image":
                    src = item["source"]
                    parts.append(
                        {"inline_data": {"mime_type": src["media_type"], "data": src["data"]}}
                    )
        return {"role": "user", "parts": parts}

    def make_assistant_message(self, result: ModelTurnResult, raw_content: Any) -> dict:  # noqa: ARG002
        return raw_content  # already Gemini-format Content dict

    def make_tool_results(
        self,
        tool_calls: list[ToolCall],
        results: list[tuple[str, str | None]],
    ) -> list[dict]:
        parts: list[dict[str, Any]] = []
        for tc, (text, image) in zip(tool_calls, results):
            parts.append({"function_response": {"name": tc.name, "response": {"result": text}}})
            if image:
                parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image}})
        return [{"role": "user", "parts": parts}]

    # ── API calls ─────────────────────────────────────────────────

    def _convert_tools(self, tool_defs: list[dict]) -> list:
        types = self._types
        declarations = [
            types.FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters=t["input_schema"],
            )
            for t in tool_defs
        ]
        return [types.Tool(function_declarations=declarations)]

    def _flatten_messages(self, messages: list) -> list[dict]:
        flat: list[dict] = []
        for msg in messages:
            if isinstance(msg, list):
                flat.extend(msg)
            else:
                flat.append(msg)
        return flat

    async def stream_turn(
        self,
        system: str | tuple[str, str],
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> tuple[ModelTurnResult, Any]:
        if isinstance(system, tuple):
            system = "\n\n---\n\n".join(s for s in system if s)
        types = self._types
        config = types.GenerateContentConfig(
            system_instruction=system,
            tools=self._convert_tools(tools) if tools else None,
            max_output_tokens=max_tokens,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
        contents = self._flatten_messages(messages)

        text_chunks: list[str] = []
        tool_calls: list[ToolCall] = []
        raw_parts: list = []

        async for chunk in await self._client.aio.models.generate_content_stream(
            model=self.model,
            contents=contents,  # type: ignore[arg-type]
            config=config,
        ):
            if not chunk.candidates:
                continue
            content = chunk.candidates[0].content
            if content is None or content.parts is None:
                continue
            for part in content.parts:
                raw_parts.append(part)
                if part.text:
                    text_chunks.append(part.text)
                    if on_text:
                        on_text(part.text)
                if part.function_call:
                    fc = part.function_call
                    if fc.name is None:
                        continue
                    tool_calls.append(
                        ToolCall(
                            id=f"call_{uuid.uuid4().hex[:8]}",
                            name=fc.name,
                            input=dict(fc.args or {}),
                        )
                    )

        text = "".join(text_chunks)
        stop = "tool_use" if tool_calls else "end_turn"
        raw_assistant = {"role": "model", "parts": raw_parts}
        return (
            ModelTurnResult(stop_reason=stop, text=text, tool_calls=tool_calls),
            raw_assistant,
        )

    async def complete(self, prompt: str, max_tokens: int) -> str:
        types = self._types
        try:
            resp = await self._client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
            return (resp.text or "").strip()
        except Exception as e:
            logger.warning("complete() failed: %s", e)
            return ""
