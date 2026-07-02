"""OpenAI-compatible backend (Ollama, vllm, lm-studio, real OpenAI, etc.)."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

from ._shared import _TOOL_CALL_RE, _build_tools_system, _parse_tool_calls_from_text
from .base import ModelTurnResult, ToolCall

logger = logging.getLogger(__name__)


def _read_usage(chunk: Any, input_tokens: int, output_tokens: int) -> tuple[int, int]:
    """Fold a streaming chunk's usage into running totals, if present.

    With ``stream_options={"include_usage": True}`` OpenAI-compatible servers
    (Ollama, vLLM, real OpenAI) emit a final usage-only chunk. Servers that
    ignore the option simply never send one, so tokens stay 0 — no regression.
    """
    usage = getattr(chunk, "usage", None)
    if usage is None:
        return input_tokens, output_tokens
    return (
        getattr(usage, "prompt_tokens", None) or input_tokens,
        getattr(usage, "completion_tokens", None) or output_tokens,
    )


class OpenAICompatibleBackend:
    """Backend for any OpenAI-compatible endpoint: Ollama, vllm, lm-studio, etc."""

    def __init__(self, api_key: str, model: str, base_url: str, tools_mode: str = "prompt") -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key or "local", base_url=base_url)
        self.model = model
        self.tools_mode = tools_mode  # "native" | "prompt"
        self._use_completion_tokens = "api.openai.com" in base_url

    # ── message factories ─────────────────────────────────────────

    def make_user_message(self, content: str | list) -> dict:
        return {"role": "user", "content": content}

    def make_assistant_message(self, result: ModelTurnResult, raw_content: Any) -> dict:  # noqa: ARG002
        return raw_content  # already an OpenAI-format dict

    def make_tool_results(
        self,
        tool_calls: list[ToolCall],
        results: list[tuple[str, str | None]],
    ) -> list[dict]:
        """Returns tool result messages. Format depends on tools_mode."""
        if self.tools_mode == "prompt":
            return self._make_prompt_tool_results(tool_calls, results)
        return self._make_native_tool_results(tool_calls, results)

    def _make_native_tool_results(
        self,
        tool_calls: list[ToolCall],
        results: list[tuple[str, str | None]],
    ) -> list[dict]:
        # Tool result messages: text only.
        # Images go in a separate user message — Gemini (and many APIs) reject
        # image_url inside "role: tool" messages.
        msgs: list[dict[str, Any]] = []
        for tc, (text, image) in zip(tool_calls, results):
            msgs.append({"role": "tool", "tool_call_id": tc.id, "content": text})
            if image:
                msgs.append(
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "(camera image attached)"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                            },
                        ],
                    }
                )
        return msgs

    def _make_prompt_tool_results(
        self,
        tool_calls: list[ToolCall],
        results: list[tuple[str, str | None]],
    ) -> list[dict]:
        """For prompt-based tool calling: inject results as a user message."""
        parts: list[dict] = []
        for tc, (text, image) in zip(tool_calls, results):
            parts.append({"type": "text", "text": f"[Tool result: {tc.name}]\n{text}"})
            if image:
                parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                    }
                )
        return [{"role": "user", "content": parts}]

    # ── API calls ─────────────────────────────────────────────────

    def _convert_tools(self, tool_defs: list[dict]) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                },
            }
            for t in tool_defs
        ]

    def _flatten_messages(self, system: str | tuple[str, str], messages: list) -> list[dict]:
        """Build flat OpenAI message list with system prepended.

        Accepts a (stable, variable) tuple from _system_prompt() and joins it
        into a single system string — OpenAI-compatible APIs don't support
        multi-block system prompts with cache_control.
        """
        if isinstance(system, tuple):
            system = "\n\n---\n\n".join(s for s in system if s)
        flat: list[dict] = [{"role": "system", "content": system}]
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
        sys_str: str = (
            "\n\n---\n\n".join(s for s in system if s) if isinstance(system, tuple) else system
        )
        if self.tools_mode == "prompt":
            return await self._stream_turn_prompt(sys_str, messages, tools, max_tokens, on_text)
        return await self._stream_turn_native(sys_str, messages, tools, max_tokens, on_text)

    def _build_tools_system(self, system: str, tools: list[dict]) -> str:
        return _build_tools_system(system, tools)

    def _parse_tool_calls_from_text(self, text: str) -> list[ToolCall]:
        return _parse_tool_calls_from_text(text)

    async def _stream_turn_prompt(
        self,
        system: str,
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> tuple[ModelTurnResult, Any]:
        """Prompt-based tool calling: tools injected into system prompt, parse <tool_call> tags."""
        augmented_system = self._build_tools_system(system, tools)
        flat = self._flatten_messages(augmented_system, messages)

        tokens_key = "max_completion_tokens" if self._use_completion_tokens else "max_tokens"
        stream = await self.client.chat.completions.create(  # type: ignore[call-overload]
            model=self.model,
            **{tokens_key: max_tokens},
            messages=flat,
            stream=True,
            stream_options={"include_usage": True},
        )

        text_chunks: list[str] = []
        input_tokens = 0
        output_tokens = 0
        async for chunk in stream:
            input_tokens, output_tokens = _read_usage(chunk, input_tokens, output_tokens)
            # The final usage-only chunk (and any keep-alive) carries no choices.
            if not chunk.choices:
                continue
            if chunk.choices[0].delta.content:
                chunk_text = chunk.choices[0].delta.content
                text_chunks.append(chunk_text)
                if on_text:
                    on_text(chunk_text)

        text = "".join(text_chunks)
        tool_calls = self._parse_tool_calls_from_text(text)

        clean_text = _TOOL_CALL_RE.sub("", text).strip()

        stop = "tool_use" if tool_calls else "end_turn"
        raw_assistant = {"role": "assistant", "content": text or ""}
        return (
            ModelTurnResult(
                stop_reason=stop,
                text=clean_text,
                tool_calls=tool_calls,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ),
            raw_assistant,
        )

    async def _stream_turn_native(
        self,
        system: str,
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> tuple[ModelTurnResult, Any]:
        """Native OpenAI function-calling API."""
        flat = self._flatten_messages(system, messages)
        oai_tools = self._convert_tools(tools) if tools else None

        tokens_key = "max_completion_tokens" if self._use_completion_tokens else "max_tokens"
        kwargs: dict[str, Any] = {
            "model": self.model,
            tokens_key: max_tokens,
            "messages": flat,
            "stream": True,
        }
        if oai_tools:
            kwargs["tools"] = oai_tools
        kwargs["stream_options"] = {"include_usage": True}

        stream = await self.client.chat.completions.create(**kwargs)

        text_chunks: list[str] = []
        raw_tcs: dict[int, dict] = {}
        finish_reason: str | None = None
        input_tokens = 0
        output_tokens = 0
        # Filter Gemini thinking tokens: buffer until thinking block ends.
        _thinking_buf: str = ""
        _in_thinking: bool | None = None

        async for chunk in stream:
            input_tokens, output_tokens = _read_usage(chunk, input_tokens, output_tokens)
            # The final usage-only chunk (and any keep-alive) carries no choices.
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            delta = choice.delta
            finish_reason = choice.finish_reason or finish_reason

            if delta.content:
                chunk_text = delta.content

                if _in_thinking is None:
                    _thinking_buf += chunk_text
                    if _thinking_buf.startswith("THOUGHT"):
                        _in_thinking = True
                    elif len(_thinking_buf) >= 7:
                        _in_thinking = False
                        text_chunks.append(_thinking_buf)
                        if on_text:
                            on_text(_thinking_buf)
                        _thinking_buf = ""
                elif _in_thinking:
                    _thinking_buf += chunk_text
                    end_idx = _thinking_buf.find("\n\n")
                    if end_idx != -1:
                        _in_thinking = False
                        real_text = _thinking_buf[end_idx + 2 :]
                        _thinking_buf = ""
                        if real_text:
                            text_chunks.append(real_text)
                            if on_text:
                                on_text(real_text)
                else:
                    text_chunks.append(chunk_text)
                    if on_text:
                        on_text(chunk_text)

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
        raw_assistant: dict[str, Any] = {"role": "assistant", "content": text or ""}
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
            ModelTurnResult(
                stop_reason=stop,
                text=text,
                tool_calls=tool_calls,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ),
            raw_assistant,
        )

    async def complete(self, prompt: str, max_tokens: int) -> str:
        tokens_key = "max_completion_tokens" if self._use_completion_tokens else "max_tokens"
        try:
            resp = await self.client.chat.completions.create(  # type: ignore[call-overload]
                model=self.model,
                **{tokens_key: max_tokens},
                messages=[{"role": "user", "content": prompt}],
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            logger.warning("complete() failed: %s", e)
            return ""
