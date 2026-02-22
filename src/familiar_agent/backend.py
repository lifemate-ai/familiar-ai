"""LLM backend abstraction — Anthropic or OpenAI-compatible (Ollama, vllm, etc.)."""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .config import AgentConfig

# ── Prompt-based tool calling ─────────────────────────────────────
# Used when the model doesn't support native function calling (most local VLMs).
# Tools are injected into the system prompt; the model outputs <tool_call> JSON.

_TOOLS_PROMPT_HEADER = """\

---
[USING TOOLS]
You MUST use tools by outputting a <tool_call> block. This is the ONLY way to take actions.

RULE: When you want to use a tool, output EXACTLY this pattern and nothing after it:
<tool_call>{{"name": "...", "input": {{...}}}}</tool_call>

Then STOP. Do not write anything after the closing tag. The result will be given to you next.

CONCRETE EXAMPLES:
{examples}

Available tools:
{tools_desc}
[/USING TOOLS]
"""

_TOOL_CALL_RE = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL)

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class TurnResult:
    stop_reason: str  # "end_turn" | "tool_use"
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)


class AnthropicBackend:
    """Backend using the official Anthropic SDK."""

    def __init__(self, api_key: str, model: str) -> None:
        import anthropic

        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    # ── message factories ─────────────────────────────────────────

    def make_user_message(self, content: str | list) -> dict:
        return {"role": "user", "content": content}

    def make_assistant_message(self, result: TurnResult, raw_content: Any) -> dict:  # noqa: ARG002
        return {"role": "assistant", "content": raw_content}

    def make_tool_results(
        self,
        tool_calls: list[ToolCall],
        results: list[tuple[str, str | None]],
    ) -> list[dict]:
        """Returns a one-element list containing the Anthropic tool_result user message."""
        content = []
        for tc, (text, image) in zip(tool_calls, results):
            result_content: list[dict] = [{"type": "text", "text": text}]
            if image:
                result_content.append(
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/jpeg", "data": image},
                    }
                )
            content.append({"type": "tool_result", "tool_use_id": tc.id, "content": result_content})
        return [{"role": "user", "content": content}]

    # ── API calls ─────────────────────────────────────────────────

    def _convert_tools(self, tool_defs: list[dict]) -> list[dict]:
        return tool_defs  # already in Anthropic format

    def _flatten_messages(self, messages: list) -> list[dict]:
        """Expand nested lists (from make_tool_results) into a flat message list."""
        flat: list[dict] = []
        for msg in messages:
            if isinstance(msg, list):
                flat.extend(msg)
            else:
                flat.append(msg)
        return flat

    async def stream_turn(
        self,
        system: str,
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> tuple[TurnResult, Any]:
        """Stream one agent turn. Returns (result, raw_content_for_assistant_message)."""
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            tools=self._convert_tools(tools),
            messages=self._flatten_messages(messages),
        ) as stream:
            async for chunk in stream.text_stream:
                if on_text:
                    on_text(chunk)
            response = await stream.get_final_message()

        text = "".join(b.text for b in response.content if hasattr(b, "text"))
        tool_calls = [
            ToolCall(id=b.id, name=b.name, input=b.input)
            for b in response.content
            if b.type == "tool_use"
        ]
        stop = "end_turn" if response.stop_reason == "end_turn" else "tool_use"
        return TurnResult(stop_reason=stop, text=text, tool_calls=tool_calls), response.content

    async def complete(self, prompt: str, max_tokens: int) -> str:
        """Simple completion (no tools, no streaming) for utility calls."""
        try:
            resp = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text.strip() if resp.content else ""
        except Exception as e:
            logger.warning("complete() failed: %s", e)
            return ""


class OpenAICompatibleBackend:
    """Backend for any OpenAI-compatible endpoint: Ollama, vllm, lm-studio, etc."""

    def __init__(self, api_key: str, model: str, base_url: str, tools_mode: str = "prompt") -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key or "local", base_url=base_url)
        self.model = model
        self.tools_mode = tools_mode  # "native" | "prompt"
        # Real OpenAI API uses max_completion_tokens; local models use max_tokens
        self._use_completion_tokens = "api.openai.com" in base_url

    # ── message factories ─────────────────────────────────────────

    def make_user_message(self, content: str | list) -> dict:
        return {"role": "user", "content": content}

    def make_assistant_message(self, result: TurnResult, raw_content: Any) -> dict:  # noqa: ARG002
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
        msgs = []
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

    def _flatten_messages(self, system: str, messages: list) -> list[dict]:
        """Build flat OpenAI message list with system prepended."""
        flat: list[dict] = [{"role": "system", "content": system}]
        for msg in messages:
            if isinstance(msg, list):
                flat.extend(msg)
            else:
                flat.append(msg)
        return flat

    async def stream_turn(
        self,
        system: str,
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> tuple[TurnResult, Any]:
        if self.tools_mode == "prompt":
            return await self._stream_turn_prompt(system, messages, tools, max_tokens, on_text)
        return await self._stream_turn_native(system, messages, tools, max_tokens, on_text)

    def _build_tools_system(self, system: str, tools: list[dict]) -> str:
        """Append tool descriptions to the system prompt."""
        if not tools:
            return system

        desc_lines = []
        example_lines = []
        for t in tools:
            props = t.get("input_schema", {}).get("properties", {})
            required = t.get("input_schema", {}).get("required", [])
            desc_lines.append(f"- {t['name']}: {t['description']}")

            # Build a minimal example input with only required fields
            example_input: dict = {}
            for k in required:
                prop = props.get(k, {})
                ptype = prop.get("type", "string")
                enum = prop.get("enum")
                if enum:
                    example_input[k] = enum[0]
                elif ptype == "integer":
                    example_input[k] = prop.get("default", 30)
                else:
                    example_input[k] = f"<{k}>"
            example_json = json.dumps(
                {"name": t["name"], "input": example_input}, ensure_ascii=False
            )
            example_lines.append(f"<tool_call>{example_json}</tool_call>")

        tools_desc = "\n".join(desc_lines)
        examples = "\n".join(example_lines)
        return system + _TOOLS_PROMPT_HEADER.format(tools_desc=tools_desc, examples=examples)

    def _parse_tool_calls_from_text(self, text: str) -> list[ToolCall]:
        """Extract <tool_call> JSON blocks from model output."""
        tool_calls = []
        for match in _TOOL_CALL_RE.finditer(text):
            try:
                data = json.loads(match.group(1).strip())
                tool_calls.append(
                    ToolCall(
                        id=f"call_{uuid.uuid4().hex[:8]}",
                        name=data["name"],
                        input=data.get("input", {}),
                    )
                )
            except (json.JSONDecodeError, KeyError):
                logger.warning("Failed to parse tool_call: %s", match.group(1))
        return tool_calls

    async def _stream_turn_prompt(
        self,
        system: str,
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> tuple[TurnResult, Any]:
        """Prompt-based tool calling: tools injected into system prompt, parse <tool_call> tags."""
        augmented_system = self._build_tools_system(system, tools)
        flat = self._flatten_messages(augmented_system, messages)

        tokens_key = "max_completion_tokens" if self._use_completion_tokens else "max_tokens"
        stream = await self.client.chat.completions.create(
            model=self.model,
            **{tokens_key: max_tokens},
            messages=flat,
            stream=True,
        )

        text_chunks: list[str] = []
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                chunk_text = chunk.choices[0].delta.content
                text_chunks.append(chunk_text)
                if on_text:
                    on_text(chunk_text)

        text = "".join(text_chunks)
        tool_calls = self._parse_tool_calls_from_text(text)

        # Strip the <tool_call> block from displayed text
        clean_text = _TOOL_CALL_RE.sub("", text).strip()

        stop = "tool_use" if tool_calls else "end_turn"
        raw_assistant = {"role": "assistant", "content": text or None}
        return TurnResult(stop_reason=stop, text=clean_text, tool_calls=tool_calls), raw_assistant

    async def _stream_turn_native(
        self,
        system: str,
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> tuple[TurnResult, Any]:
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

        stream = await self.client.chat.completions.create(**kwargs)

        text_chunks: list[str] = []
        raw_tcs: dict[int, dict] = {}
        finish_reason: str | None = None
        # Filter Gemini thinking tokens: buffer until thinking block ends.
        # Thinking content starts with "THOUGHT\n" and ends before the actual response.
        _thinking_buf: str = ""
        _in_thinking: bool | None = None  # None = undecided, True = in thinking, False = done

        async for chunk in stream:
            choice = chunk.choices[0]
            delta = choice.delta
            finish_reason = choice.finish_reason or finish_reason

            if delta.content:
                chunk_text = delta.content

                if _in_thinking is None:
                    # First content chunk — decide if we're in a thinking block
                    _thinking_buf += chunk_text
                    if _thinking_buf.startswith("THOUGHT"):
                        _in_thinking = True
                    elif len(_thinking_buf) >= 7:
                        # Enough chars to decide — not a thinking block
                        _in_thinking = False
                        text_chunks.append(_thinking_buf)
                        if on_text:
                            on_text(_thinking_buf)
                        _thinking_buf = ""
                elif _in_thinking:
                    # Still inside thinking block — look for the end
                    _thinking_buf += chunk_text
                    # Thinking ends when we see a blank line after THOUGHT content
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
        raw_assistant: dict[str, Any] = {"role": "assistant", "content": text or None}
        if tool_calls:
            raw_assistant["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": json.dumps(tc.input)},
                }
                for tc in tool_calls
            ]
        return TurnResult(stop_reason=stop, text=text, tool_calls=tool_calls), raw_assistant

    async def complete(self, prompt: str, max_tokens: int) -> str:
        tokens_key = "max_completion_tokens" if self._use_completion_tokens else "max_tokens"
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                **{tokens_key: max_tokens},
                messages=[{"role": "user", "content": prompt}],
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            logger.warning("complete() failed: %s", e)
            return ""


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

    def make_assistant_message(self, result: TurnResult, raw_content: Any) -> dict:  # noqa: ARG002
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

    async def stream(
        self,
        system: str,
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None = None,
    ) -> tuple[TurnResult, Any]:
        flat_messages = [{"role": "system", "content": system}] + messages

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
        return TurnResult(stop_reason=stop, text=text, tool_calls=tool_calls), raw_assistant

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
        parts = []
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

    def make_assistant_message(self, result: TurnResult, raw_content: Any) -> dict:  # noqa: ARG002
        return raw_content  # already Gemini-format Content dict

    def make_tool_results(
        self,
        tool_calls: list[ToolCall],
        results: list[tuple[str, str | None]],
    ) -> list[dict]:
        parts = []
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
        system: str,
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> tuple[TurnResult, Any]:
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
            contents=contents,
            config=config,
        ):
            if not chunk.candidates:
                continue
            for part in chunk.candidates[0].content.parts:
                raw_parts.append(part)
                if part.text:
                    text_chunks.append(part.text)
                    if on_text:
                        on_text(part.text)
                if part.function_call:
                    fc = part.function_call
                    tool_calls.append(
                        ToolCall(
                            id=f"call_{uuid.uuid4().hex[:8]}",
                            name=fc.name,
                            input=dict(fc.args),
                        )
                    )

        text = "".join(text_chunks)
        stop = "tool_use" if tool_calls else "end_turn"
        raw_assistant = {"role": "model", "parts": raw_parts}
        return TurnResult(stop_reason=stop, text=text, tool_calls=tool_calls), raw_assistant

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


def create_backend(
    config: "AgentConfig",
) -> AnthropicBackend | OpenAICompatibleBackend | KimiBackend | GeminiBackend:
    """Factory: pick backend based on PLATFORM env var / config.

    Supported values for PLATFORM:
      anthropic  — Anthropic Claude (default)
      gemini     — Google Gemini via native google-genai SDK
      openai     — OpenAI API (or compatible via BASE_URL)
      kimi       — Moonshot AI Kimi K2.5 (api.moonshot.ai/v1)
    """
    if config.platform == "gemini":
        model = config.model or "gemini-2.5-flash"
        logger.info("Using Gemini backend: %s", model)
        return GeminiBackend(api_key=config.api_key, model=model)
    if config.platform == "openai":
        model = config.model or "gpt-4o-mini"
        # If BASE_URL not explicitly set, use the real OpenAI endpoint
        base_url = config.base_url
        if not os.environ.get("BASE_URL"):
            base_url = "https://api.openai.com/v1"
        tools_mode = config.tools_mode if os.environ.get("TOOLS_MODE") else "native"
        logger.info(
            "Using OpenAI backend: %s @ %s (tools=%s)",
            model,
            base_url,
            tools_mode,
        )
        return OpenAICompatibleBackend(
            api_key=config.api_key,
            model=model,
            base_url=base_url,
            tools_mode=tools_mode,
        )
    if config.platform == "kimi":
        # Moonshot AI Kimi K2.5 — needs its own backend to handle reasoning_content
        # See: https://platform.moonshot.ai / https://github.com/MoonshotAI/Kimi-K2.5
        model = config.model or "kimi-k2.5"
        logger.info("Using Kimi backend: %s", model)
        return KimiBackend(api_key=config.api_key, model=model)
    model = config.model or "claude-haiku-4-5-20251001"
    logger.info("Using Anthropic backend: %s", model)
    return AnthropicBackend(api_key=config.api_key, model=model)
