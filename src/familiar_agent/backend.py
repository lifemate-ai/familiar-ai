"""LLM backend abstraction — Anthropic or OpenAI-compatible (Ollama, vllm, etc.)."""

from __future__ import annotations

import json
import logging
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

        stream = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
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

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": flat,
            "stream": True,
            # Disable Gemini thinking tokens so they don't leak into output
            "extra_body": {"generationConfig": {"thinkingConfig": {"thinkingBudget": 0}}},
        }
        if oai_tools:
            kwargs["tools"] = oai_tools

        stream = await self.client.chat.completions.create(**kwargs)

        text_chunks: list[str] = []
        raw_tcs: dict[int, dict] = {}
        finish_reason: str | None = None

        async for chunk in stream:
            choice = chunk.choices[0]
            delta = choice.delta
            finish_reason = choice.finish_reason or finish_reason

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


def create_backend(config: "AgentConfig") -> AnthropicBackend | OpenAICompatibleBackend:
    """Factory: pick backend based on LLM_BACKEND env var / config."""
    if config.llm_backend == "openai":
        model = config.llm_model or "qwen2.5vl:7b"
        logger.info(
            "Using OpenAI-compatible backend: %s @ %s (tools=%s)",
            model,
            config.llm_base_url,
            config.llm_tools_mode,
        )
        return OpenAICompatibleBackend(
            api_key=config.llm_api_key,
            model=model,
            base_url=config.llm_base_url,
            tools_mode=config.llm_tools_mode,
        )
    logger.info("Using Anthropic backend: %s", config.model)
    return AnthropicBackend(api_key=config.anthropic_api_key, model=config.model)
