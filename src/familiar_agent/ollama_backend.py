"""Ollama native backend — talks to ``/api/chat`` directly.

Why not the OpenAI-compatible ``/v1`` route?

- ``num_ctx`` cannot be set through ``/v1``; Ollama then loads the model with its
  4096-token default and long system prompts fail with HTTP 500 "EOF".
- Reasoning models (qwen3.x) always think on ``/v1`` unless a vendor-specific
  ``reasoning_effort`` hint is sent.  The native API has a first-class ``think`` flag.
- Prompt-mode ``<tool_call>`` JSON collides with Ollama's built-in tool parsers.
  The native API returns structured ``tool_calls`` instead.
"""

from __future__ import annotations

import contextlib
import json
import logging
import uuid
from collections.abc import AsyncGenerator, Callable
from typing import Any

from .backend import ToolCall, TurnResult

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_NUM_CTX = 16384

StreamFactory = Callable[[dict[str, Any]], AsyncGenerator[dict[str, Any], None]]


def normalize_base_url(url: str) -> str:
    """Accept ``http://host:11434`` or ``http://host:11434/v1`` and return the host root."""
    url = (url or DEFAULT_BASE_URL).rstrip("/")
    if url.endswith("/v1"):
        url = url[: -len("/v1")]
    return url


def think_flag(thinking_mode: str) -> bool:
    """Map THINKING_MODE onto Ollama's boolean ``think``.

    ``auto`` resolves to *off*: local models are chosen for latency, and an
    unbounded think block routinely eats the whole ``max_tokens`` budget.
    """
    return thinking_mode in ("adaptive", "extended")


def _convert_tools(tool_defs: list[dict]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
            },
        }
        for t in tool_defs
    ]


def _content_blocks_to_message(content: str | list) -> dict[str, Any]:
    """Turn a plain string or Anthropic-style block list into an Ollama user message."""
    if isinstance(content, str):
        return {"role": "user", "content": content}
    texts: list[str] = []
    images: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        kind = block.get("type")
        if kind == "text":
            texts.append(str(block.get("text", "")))
        elif kind == "image_url":
            url = str(block.get("image_url", {}).get("url", ""))
            images.append(url.split(",", 1)[-1] if "," in url else url)
        elif kind == "image":
            images.append(str(block.get("source", {}).get("data", "")))
    msg: dict[str, Any] = {"role": "user", "content": "\n".join(texts)}
    if images:
        msg["images"] = images
    return msg


class OllamaBackend:
    """Backend for Ollama's native ``/api/chat`` endpoint."""

    def __init__(
        self,
        model: str,
        base_url: str = DEFAULT_BASE_URL,
        *,
        think: bool = False,
        num_ctx: int = DEFAULT_NUM_CTX,
        stream_factory: StreamFactory | None = None,
    ) -> None:
        self.model = model
        self.base_url = normalize_base_url(base_url)
        self.think = think
        self.num_ctx = num_ctx
        self._stream_factory = stream_factory or self._http_stream

    # ── message factories ─────────────────────────────────────────

    def make_user_message(self, content: str | list) -> dict:
        return _content_blocks_to_message(content)

    def make_assistant_message(self, result: TurnResult, raw_content: Any) -> dict:  # noqa: ARG002
        return raw_content

    def make_tool_results(
        self,
        tool_calls: list[ToolCall],
        results: list[tuple[str, str | None]],
    ) -> list[dict]:
        msgs: list[dict[str, Any]] = []
        for tc, (text, image) in zip(tool_calls, results):
            msgs.append({"role": "tool", "tool_name": tc.name, "content": text})
            if image:
                msgs.append(
                    {"role": "user", "content": "(camera image attached)", "images": [image]}
                )
        return msgs

    def make_system_message(self, content: str) -> dict:
        return {"role": "system", "content": content}

    # ── request building ──────────────────────────────────────────

    def _flatten(self, system: str | tuple[str, str], messages: list) -> list[dict]:
        if isinstance(system, tuple):
            system = "\n\n---\n\n".join(s for s in system if s)
        flat: list[dict] = [{"role": "system", "content": system}]
        for msg in messages:
            if isinstance(msg, list):
                flat.extend(msg)
            else:
                flat.append(msg)
        return flat

    def build_request(
        self,
        system: str | tuple[str, str],
        messages: list,
        tools: list[dict],
        max_tokens: int,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": self.model,
            "messages": self._flatten(system, messages),
            "stream": True,
            "think": self.think,
            "options": {"num_ctx": self.num_ctx, "num_predict": max_tokens},
        }
        if tools:
            body["tools"] = _convert_tools(tools)
        return body

    # ── HTTP ──────────────────────────────────────────────────────

    async def _http_stream(self, body: dict[str, Any]) -> AsyncGenerator[dict[str, Any], None]:
        import aiohttp

        timeout = aiohttp.ClientTimeout(total=None, sock_read=600)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(f"{self.base_url}/api/chat", json=body) as resp:
                if resp.status != 200:
                    detail = await resp.text()
                    raise RuntimeError(f"Ollama /api/chat HTTP {resp.status}: {detail[:300]}")
                async for raw_line in resp.content:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        logger.debug("Skipping non-JSON Ollama line: %s", line[:120])

    # ── turn ──────────────────────────────────────────────────────

    async def stream_turn(
        self,
        system: str | tuple[str, str],
        messages: list,
        tools: list[dict],
        max_tokens: int,
        on_text: Callable[[str], None] | None = None,
    ) -> tuple[TurnResult, Any]:
        body = self.build_request(system, messages, tools, max_tokens)
        try:
            return await self._stream_once(body, on_text)
        except RuntimeError as e:
            # Ollama's built-in tool-call parsers occasionally choke on a malformed
            # generation ("XML syntax error…").  One resample usually succeeds.
            if not _is_parse_glitch(str(e)):
                raise
            logger.warning("Ollama tool-call parse glitch, retrying once: %s", e)
            return await self._stream_once(body, on_text)

    async def _stream_once(
        self,
        body: dict[str, Any],
        on_text: Callable[[str], None] | None,
    ) -> tuple[TurnResult, Any]:
        text_chunks: list[str] = []
        thinking_chunks: list[str] = []
        raw_tool_calls: list[dict[str, Any]] = []
        input_tokens = 0
        output_tokens = 0

        # aclosing() guarantees the HTTP session inside the generator is closed
        # even when we stop early (error chunk, cancellation, consumer exception).
        async with contextlib.aclosing(self._stream_factory(body)) as stream:
            async for chunk in stream:
                await self._absorb_chunk(
                    chunk, text_chunks, thinking_chunks, raw_tool_calls, on_text
                )
                if chunk.get("done"):
                    input_tokens = int(chunk.get("prompt_eval_count") or 0)
                    output_tokens = int(chunk.get("eval_count") or 0)

        tool_calls = [
            ToolCall(
                id=f"call_{uuid.uuid4().hex[:8]}",
                name=str(tc.get("function", {}).get("name", "")),
                input=_coerce_arguments(tc.get("function", {}).get("arguments")),
            )
            for tc in raw_tool_calls
        ]
        text = "".join(text_chunks)

        raw_assistant: dict[str, Any] = {"role": "assistant", "content": text}
        if thinking_chunks:
            raw_assistant["thinking"] = "".join(thinking_chunks)
        if raw_tool_calls:
            raw_assistant["tool_calls"] = raw_tool_calls

        stop = "tool_use" if tool_calls else "end_turn"
        return (
            TurnResult(
                stop_reason=stop,
                text=text,
                tool_calls=tool_calls,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ),
            raw_assistant,
        )

    @staticmethod
    async def _absorb_chunk(
        chunk: dict[str, Any],
        text_chunks: list[str],
        thinking_chunks: list[str],
        raw_tool_calls: list[dict[str, Any]],
        on_text: Callable[[str], None] | None,
    ) -> None:
        if "error" in chunk:
            raise RuntimeError(f"Ollama error: {chunk['error']}")
        msg = chunk.get("message") or {}
        if msg.get("thinking"):
            thinking_chunks.append(msg["thinking"])
        if msg.get("content"):
            text_chunks.append(msg["content"])
            if on_text:
                on_text(msg["content"])
        for tc in msg.get("tool_calls") or []:
            raw_tool_calls.append(tc)

    async def complete(self, prompt: str, max_tokens: int) -> str:
        if not prompt or not prompt.strip():
            return ""  # never ask a model to complete nothing — it asks back
        body = self.build_request("", [{"role": "user", "content": prompt}], [], max_tokens)
        body["messages"] = [m for m in body["messages"] if m["content"]]
        try:
            chunks: list[str] = []
            async with contextlib.aclosing(self._stream_factory(body)) as stream:
                async for chunk in stream:
                    content = (chunk.get("message") or {}).get("content")
                    if content:
                        chunks.append(content)
            return "".join(chunks).strip()
        except Exception as e:
            logger.warning("complete() failed: %s", e)
            return ""


def _is_parse_glitch(message: str) -> bool:
    lowered = message.lower()
    return "syntax error" in lowered or "parsing" in lowered or "unexpected eof" in lowered


def _coerce_arguments(raw: Any) -> dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}
