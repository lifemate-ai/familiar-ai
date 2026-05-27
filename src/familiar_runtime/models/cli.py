"""CLI backend (shell out to any CLI LLM tool via stdin/stdout)."""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Callable
from typing import Any

from ._shared import _TOOL_CALL_RE, _build_tools_system, _parse_tool_calls_from_text
from .base import ModelTurnResult, ToolCall

logger = logging.getLogger(__name__)


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

    def make_assistant_message(self, result: ModelTurnResult, raw_content: Any) -> dict:  # noqa: ARG002
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
        max_tokens: int,  # noqa: ARG002
        on_text: Callable[[str], None] | None,
    ) -> tuple[ModelTurnResult, Any]:
        prompt = self._serialize(system, messages, tools)
        text = await self._run(prompt)
        if on_text:
            on_text(text)
        tool_calls = _parse_tool_calls_from_text(text)
        clean_text = _TOOL_CALL_RE.sub("", text).strip()
        stop = "tool_use" if tool_calls else "end_turn"
        raw: dict[str, Any] = {"role": "assistant", "content": text}
        return ModelTurnResult(stop_reason=stop, text=clean_text, tool_calls=tool_calls), raw

    async def complete(self, prompt: str, max_tokens: int) -> str:  # noqa: ARG002
        return await self._run(prompt)
