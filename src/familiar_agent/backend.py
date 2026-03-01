"""LLM backend abstraction — Anthropic, OpenAI-compatible, Gemini, Kimi, or CLI."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shlex
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

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

# ── Thinking support ───────────────────────────────────────────────────────

_ADAPTIVE_THINKING_MODELS = ("sonnet-4", "opus-4")


def _supports_adaptive_thinking(model: str) -> bool:
    """Return True if the model supports adaptive thinking (Sonnet 4.x / Opus 4.x)."""
    return any(m in model for m in _ADAPTIVE_THINKING_MODELS)


# ── Shared helpers (used by OpenAICompatibleBackend and CLIBackend) ───────────


def _build_tools_system(system: str, tools: list[dict]) -> str:
    """Append tool descriptions + usage instructions to a system prompt."""
    if not tools:
        return system

    desc_lines = []
    example_lines = []
    for t in tools:
        props = t.get("input_schema", {}).get("properties", {})
        required = t.get("input_schema", {}).get("required", [])
        desc_lines.append(f"- {t['name']}: {t['description']}")

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
        example_json = json.dumps({"name": t["name"], "input": example_input}, ensure_ascii=False)
        example_lines.append(f"<tool_call>{example_json}</tool_call>")

    tools_desc = "\n".join(desc_lines)
    examples = "\n".join(example_lines)
    return system + _TOOLS_PROMPT_HEADER.format(tools_desc=tools_desc, examples=examples)


def _parse_tool_calls_from_text(text: str) -> list[ToolCall]:
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
    input_tokens: int = 0
    output_tokens: int = 0


class AnthropicBackend:
    """Backend using the official Anthropic SDK."""

    def __init__(
        self,
        api_key: str,
        model: str,
        thinking_mode: str = "auto",
        thinking_budget: int = 10000,
        thinking_effort: str = "high",
    ) -> None:
        import anthropic

        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self.thinking_mode = thinking_mode
        self.thinking_budget = thinking_budget
        self.thinking_effort = thinking_effort

    def _build_thinking_params(self) -> dict:
        """Return thinking kwargs for the Anthropic API call.

        Per official docs (https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking):
        - adaptive thinking: no beta header needed (GA feature since Opus/Sonnet 4.6)
        - adaptive mode automatically enables interleaved thinking
        - extended mode on Sonnet 4.6 needs interleaved-thinking-2025-05-14 beta for interleaved support
        - extended mode on Opus 4.6 does NOT support interleaved thinking even with beta header

        Returns a dict that may contain:
          - "thinking": thinking config
          - "output_config": effort level (adaptive mode only)
          - "betas": list of beta header strings (extended mode on Sonnet 4.6 only)
        """
        mode = self.thinking_mode
        if mode == "auto":
            mode = "adaptive" if _supports_adaptive_thinking(self.model) else "disabled"

        if mode == "adaptive":
            # No beta header required — adaptive thinking is GA on Opus 4.6 / Sonnet 4.6.
            # Interleaved thinking is automatically enabled in adaptive mode.
            params: dict = {"thinking": {"type": "adaptive"}}
            if self.thinking_effort != "high":  # "high" is the default; skip if default
                params["output_config"] = {"effort": self.thinking_effort}
            return params

        if mode == "extended":
            # budget_tokens is deprecated on Opus 4.6 / Sonnet 4.6 but still accepted.
            # interleaved-thinking-2025-05-14 beta enables interleaved thinking on Sonnet 4.6
            # only (Opus 4.6 extended mode does not support interleaved thinking).
            params = {"thinking": {"type": "enabled", "budget_tokens": self.thinking_budget}}
            if "sonnet-4" in self.model:
                params["betas"] = ["interleaved-thinking-2025-05-14"]
            return params

        # disabled (or unknown)
        return {}

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
        content: list[dict[str, Any]] = []
        for tc, (text, image) in zip(tool_calls, results):
            result_content: list[dict[str, Any]] = [{"type": "text", "text": text}]
            if image:
                result_content.append(
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/jpeg", "data": image},
                    }
                )
            content.append({"type": "tool_result", "tool_use_id": tc.id, "content": result_content})
        msgs: list[dict[str, Any]] = [{"role": "user", "content": content}]
        return msgs

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

    @staticmethod
    def compact_images(messages: list[dict], keep_last: int = 3) -> list[dict]:
        """Strip base64 image data from old tool results, keeping the last `keep_last`.

        Human-like forgetting: the text description of what was seen is preserved;
        only the raw pixel data (base64) is dropped from older turns.

        Inspired by Claude Code's Dk() microcompact (KEEP_LAST=3).
        """
        import copy

        # Collect (msg_idx, tool_result_idx, sub_idx) for every image sub-item
        positions: list[tuple[int, int, int]] = []
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict) or msg.get("role") != "user":
                continue
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for j, item in enumerate(content):
                if not isinstance(item, dict) or item.get("type") != "tool_result":
                    continue
                for k, sub in enumerate(item.get("content", [])):
                    if isinstance(sub, dict) and sub.get("type") == "image":
                        positions.append((i, j, k))

        n_clear = max(0, len(positions) - keep_last)
        to_clear = positions[:n_clear]
        if not to_clear:
            return messages

        messages = copy.deepcopy(messages)
        for msg_i, item_j, sub_k in to_clear:
            messages[msg_i]["content"][item_j]["content"][sub_k] = {
                "type": "text",
                "text": "[image cleared]",
            }
        return messages

    @staticmethod
    def _build_system_param(system: str | tuple[str, str]) -> str | list[dict]:
        """Convert system prompt to Anthropic API format, adding cache_control when possible.

        If system is a (stable, variable) tuple, the stable block gets
        cache_control so it is reused across turns within the 5-minute window.
        If system is a plain string (e.g. from tests or other callers), pass as-is.
        """
        if not isinstance(system, tuple):
            return system
        stable, variable = system
        blocks: list[dict] = []
        if stable:
            blocks.append({"type": "text", "text": stable, "cache_control": {"type": "ephemeral"}})
        if variable:
            blocks.append({"type": "text", "text": variable})
        # Degenerate: if only one block, return as plain string (no cache_control needed)
        if len(blocks) == 1 and "cache_control" not in blocks[0]:
            return blocks[0]["text"]
        return blocks

    async def stream_turn(
        self,
        system: str | tuple[str, str],
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> tuple[TurnResult, Any]:
        """Stream one agent turn. Returns (result, raw_content_for_assistant_message)."""
        from anthropic.types import MessageParam, ToolParam

        thinking_params = self._build_thinking_params()
        betas = thinking_params.pop("betas", [])

        sys_param = self._build_system_param(system)
        # Build kwargs separately so we only add keys when they have meaningful values.
        # Passing thinking=None, output_config=None, or extra_headers=None are not valid.
        stream_kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": sys_param,
            "tools": cast(list[ToolParam], self._convert_tools(tools)),
            "messages": cast(list[MessageParam], self._flatten_messages(messages)),
        }
        if betas:
            stream_kwargs["extra_headers"] = {"anthropic-beta": ",".join(betas)}
        if "thinking" in thinking_params:
            stream_kwargs["thinking"] = thinking_params["thinking"]
        if "output_config" in thinking_params:
            stream_kwargs["output_config"] = thinking_params["output_config"]
        flat_messages = self._flatten_messages(messages)
        flat_messages = self.compact_images(flat_messages)
        stream_kwargs["messages"] = cast(list[MessageParam], flat_messages)
        async with self.client.messages.stream(**stream_kwargs) as stream:  # type: ignore[arg-type]
            async for chunk in stream.text_stream:
                if on_text:
                    on_text(chunk)
            response = await stream.get_final_message()

        # ThinkingBlock has no .text attribute — hasattr check excludes it automatically
        text = "".join(b.text for b in response.content if hasattr(b, "text"))
        tool_calls = [
            ToolCall(id=b.id, name=b.name, input=b.input)
            for b in response.content
            if b.type == "tool_use"
        ]
        stop = "end_turn" if response.stop_reason == "end_turn" else "tool_use"
        in_tok = getattr(response.usage, "input_tokens", 0) if response.usage else 0
        out_tok = getattr(response.usage, "output_tokens", 0) if response.usage else 0
        # Return response.content (including ThinkingBlocks) so interleaved thinking
        # tokens are round-tripped correctly in multi-turn conversations.
        return (
            TurnResult(
                stop_reason=stop,
                text=text,
                tool_calls=tool_calls,
                input_tokens=in_tok,
                output_tokens=out_tok,
            ),
            response.content,
        )

    async def complete(self, prompt: str, max_tokens: int) -> str:
        """Simple completion (no tools, no streaming) for utility calls."""
        try:
            resp = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            from anthropic.types import TextBlock

            first = resp.content[0] if resp.content else None
            return first.text.strip() if isinstance(first, TextBlock) else ""
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
    ) -> tuple[TurnResult, Any]:
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
    ) -> tuple[TurnResult, Any]:
        """Prompt-based tool calling: tools injected into system prompt, parse <tool_call> tags."""
        augmented_system = self._build_tools_system(system, tools)
        flat = self._flatten_messages(augmented_system, messages)

        tokens_key = "max_completion_tokens" if self._use_completion_tokens else "max_tokens"
        stream = await self.client.chat.completions.create(  # type: ignore[call-overload]
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
        raw_assistant = {"role": "assistant", "content": text or ""}
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
            resp = await self.client.chat.completions.create(  # type: ignore[call-overload]
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

    async def stream_turn(
        self,
        system: str | tuple[str, str],
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None = None,
    ) -> tuple[TurnResult, Any]:
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


class GLMBackend:
    """Backend for Z.AI GLM API (https://api.z.ai).

    GLM-4.7 and similar models produce a ``reasoning_content`` (thinking) field
    before the actual response, similar to Kimi K2.5.  That field must be
    round-tripped in subsequent turns to keep the conversation valid.

    Configuration::

        PLATFORM=glm
        API_KEY=<your-key>              # from bigmodel.cn / api.z.ai
        MODEL=glm-4.7                   # default
    """

    _BASE_URL = "https://api.z.ai/api/paas/v4"

    def __init__(self, api_key: str, model: str) -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key, base_url=self._BASE_URL)
        self.model = model

    # ── message factories ─────────────────────────────────────────

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

    async def stream_turn(
        self,
        system: str | tuple[str, str],
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None = None,
    ) -> tuple[TurnResult, Any]:
        if isinstance(system, tuple):
            system = "\n\n---\n\n".join(s for s in system if s)

        flat_messages: list[dict] = [{"role": "system", "content": system}]
        for msg in messages:
            if isinstance(msg, list):
                flat_messages.extend(msg)
            else:
                flat_messages.append(msg)

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

        # Build raw_assistant — include reasoning_content so GLM accepts it next turn
        raw_assistant: dict[str, Any] = {"role": "assistant", "content": text or ""}
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

    def make_assistant_message(self, result: TurnResult, raw_content: Any) -> dict:  # noqa: ARG002
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
    ) -> tuple[TurnResult, Any]:
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


class CLIBackend:
    """Backend that shells out to any CLI LLM tool via stdin/stdout.

    Tool calling uses prompt injection + <tool_call> tag parsing (same mechanism
    as OpenAICompatibleBackend with tools_mode="prompt").  Images are text-only
    — binary data from camera tools is dropped silently.

    Config::

        PLATFORM=cli
        MODEL=claude -p {}            # Claude Code — {} is replaced with the prompt
        MODEL=ollama run gemma3:27b   # stdin-based (no {} needed)
        MODEL=llm -m gpt-4o {}        # Simon Willison's llm CLI

    If the command contains ``{}``, the serialised prompt is injected there as a
    positional argument (good for ``claude -p`` which doesn't read stdin).
    Otherwise the prompt is written to **stdin** (good for ``ollama run``).
    """

    def __init__(self, command: list[str]) -> None:
        self._cmd = command

    # ── message factories ─────────────────────────────────────────

    def make_user_message(self, content: str | list) -> dict:
        if isinstance(content, list):
            text = "\n".join(
                item["text"]
                for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            )
            return {"role": "user", "content": text}
        return {"role": "user", "content": content}

    def make_assistant_message(self, result: TurnResult, raw_content: Any) -> dict:  # noqa: ARG002
        return raw_content

    def make_tool_results(
        self,
        tool_calls: list[ToolCall],
        results: list[tuple[str, str | None]],
    ) -> list[dict]:
        parts = [f"[Tool result: {tc.name}]\n{text}" for tc, (text, _) in zip(tool_calls, results)]
        return [{"role": "user", "content": "\n\n".join(parts)}]

    # ── conversation serialisation ────────────────────────────────

    def _fmt_msg(self, msg: dict) -> str:
        role = msg.get("role", "user")
        content = msg.get("content") or ""
        if isinstance(content, list):
            text = "\n".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict) and item.get("type") in ("text",)
            )
        else:
            text = str(content)
        prefix = "User" if role == "user" else "Assistant"
        return f"{prefix}:\n{text}"

    def _serialize(self, system: str | tuple[str, str], messages: list, tools: list[dict]) -> str:
        if isinstance(system, tuple):
            system = "\n\n---\n\n".join(s for s in system if s)
        parts: list[str] = []
        augmented = _build_tools_system(system, tools)
        if augmented:
            parts.append(f"<system>\n{augmented}\n</system>")

        for msg in messages:
            if isinstance(msg, list):
                for m in msg:
                    parts.append(self._fmt_msg(m))
            elif isinstance(msg, dict):
                parts.append(self._fmt_msg(msg))

        parts.append("Assistant:")
        return "\n\n".join(parts)

    # ── subprocess I/O ────────────────────────────────────────────

    async def _run(self, prompt: str) -> str:
        """Run the CLI command with the prompt.

        If ``{}`` appears anywhere in the command, the prompt is injected
        there as a positional argument (e.g. ``claude -p {}``).
        Otherwise the prompt is written to stdin (e.g. ``ollama run model``).
        """
        # Strip CLAUDECODE so nested `claude -p` invocations are allowed
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        use_arg = "{}" in self._cmd
        if use_arg:
            cmd = [prompt if tok == "{}" else tok for tok in self._cmd]
            stdin_data: bytes | None = None
        else:
            cmd = self._cmd
            stdin_data = prompt.encode("utf-8")

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE
                if stdin_data is not None
                else asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            stdout, stderr = await proc.communicate(stdin_data)
            if proc.returncode != 0:
                logger.warning(
                    "CLI backend stderr: %s",
                    stderr.decode("utf-8", errors="replace")[:300],
                )
            return stdout.decode("utf-8", errors="replace").strip()
        except Exception as e:
            logger.error("CLI backend failed: %s", e)
            return f"[CLI backend error: {e}]"

    # ── backend interface ─────────────────────────────────────────

    async def stream_turn(
        self,
        system: str | tuple[str, str],
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None,
    ) -> tuple[TurnResult, Any]:
        prompt = self._serialize(system, messages, tools)
        text = await self._run(prompt)
        if on_text:
            on_text(text)
        tool_calls = _parse_tool_calls_from_text(text)
        clean_text = _TOOL_CALL_RE.sub("", text).strip()
        stop = "tool_use" if tool_calls else "end_turn"
        raw: dict[str, Any] = {"role": "assistant", "content": text}
        return TurnResult(stop_reason=stop, text=clean_text, tool_calls=tool_calls), raw

    async def complete(self, prompt: str, max_tokens: int) -> str:
        return await self._run(prompt)


def create_backend(
    config: "AgentConfig",
) -> (
    AnthropicBackend
    | OpenAICompatibleBackend
    | KimiBackend
    | GLMBackend
    | GeminiBackend
    | CLIBackend
):
    """Factory: pick backend based on PLATFORM env var / config.

    Supported values for PLATFORM:
      anthropic  — Anthropic Claude (default)
      gemini     — Google Gemini via native google-genai SDK
      openai     — OpenAI API (or compatible via BASE_URL)
      kimi       — Moonshot AI Kimi K2.5 (api.moonshot.ai/v1)
      glm        — Z.AI GLM API (api.z.ai/api/paas/v4); set ZAI_API_KEY
      cli        — any CLI LLM tool via stdin/stdout (MODEL = the command)
                   e.g. MODEL="claude -p"  or  MODEL="ollama run gemma3:27b"
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
        # Default to "prompt" for local/compatible endpoints; "native" only for real OpenAI.
        # Local model servers (LM Studio, Ollama, vllm, etc.) often hang or timeout when
        # they receive the `tools` parameter without proper support — causing Request timed out.
        is_real_openai = "api.openai.com" in base_url
        tools_mode = (
            config.tools_mode
            if os.environ.get("TOOLS_MODE")
            else ("native" if is_real_openai else "prompt")
        )
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
    if config.platform == "glm":
        # Z.AI GLM — OpenAI-compatible, native tool calling
        model = config.model or "glm-4.7"
        logger.info("Using GLM backend: %s", model)
        return GLMBackend(api_key=config.api_key, model=model)
    if config.platform == "cli":
        raw_cmd = config.model.strip() if config.model else "claude -p {}"
        cmd = shlex.split(raw_cmd)
        logger.info("Using CLI backend: %s", " ".join(cmd))
        return CLIBackend(cmd)
    model = config.model or "claude-haiku-4-5-20251001"
    logger.info("Using Anthropic backend: %s", model)
    return AnthropicBackend(
        api_key=config.api_key,
        model=model,
        thinking_mode=config.thinking_mode,
        thinking_budget=config.thinking_budget,
        thinking_effort=config.thinking_effort,
    )
