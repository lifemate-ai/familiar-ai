"""MCP (Model Context Protocol) client manager.

Connects to external MCP servers and exposes their tools to the agent.
Body-related tools (camera, TTS, mobility) stay as built-in; MCP is for everything else.

Supported transports
--------------------
* **stdio** — launch a local subprocess (default)
* **sse** — connect to an HTTP+SSE server

Config file: ~/.familiar-ai.json  (same mcpServers format as Claude Code's ~/.claude.json)
Override:    MCP_CONFIG=/path/to/config.json

Example config:
    {
      "mcpServers": {
        "filesystem": {
          "type": "stdio",
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user"]
        },
        "memory": {
          "type": "sse",
          "url": "http://localhost:3000/sse"
        }
      }
    }
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
from contextlib import AsyncExitStack
from pathlib import Path
from typing import IO, Any

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG = Path.home() / ".familiar-ai.json"
# MCP server stderr goes to a real file, never to sys.stderr: under the Textual
# TUI sys.stderr is replaced by an object without a usable fileno(), which
# breaks anyio's subprocess spawn inside stdio_client (issue #188) — and even
# when it works, server banners scribble over the TUI screen.
_DEFAULT_ERRLOG_PATH = Path.home() / ".familiar_ai" / "logs" / "mcp-stderr.log"
_DEFAULT_CONNECT_TIMEOUT_SEC = 45.0


def _resolve_config_path() -> Path:
    env = os.environ.get("MCP_CONFIG", "")
    return Path(env) if env else _DEFAULT_CONFIG


def _load_servers(config_path: Path) -> dict[str, dict[str, Any]]:
    """Read mcpServers from the config file. Returns {} if file absent or malformed."""
    if not config_path.exists():
        return {}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        servers = data.get("mcpServers", {})
        if not isinstance(servers, dict):
            logger.warning("MCP config: mcpServers must be an object, ignoring")
            return {}
        return servers
    except Exception as e:
        logger.warning("Failed to load MCP config %s: %s", config_path, e)
        return {}


class MCPClientManager:
    """Manages MCP server connections (stdio and SSE) for the duration of the agent session."""

    def __init__(
        self,
        config_path: Path | None = None,
        *,
        errlog_path: str | Path | None = None,
        connect_timeout_seconds: float | None = None,
    ) -> None:
        self._config_path = config_path or _resolve_config_path()
        self._servers = _load_servers(self._config_path)
        self._sessions: dict[str, Any] = {}  # server_name → ClientSession
        # tool_name → server_name (for routing)
        self._tool_router: dict[str, str] = {}
        # Cached tool definitions (Anthropic format)
        self._tool_defs: list[dict[str, Any]] = []
        self._exit_stack = AsyncExitStack()
        self._started = False
        self._errlog_path = Path(errlog_path).expanduser() if errlog_path else _DEFAULT_ERRLOG_PATH
        self._errlog: IO[str] | None = None
        if connect_timeout_seconds is None:
            raw = os.environ.get("MCP_CONNECT_TIMEOUT", "").strip()
            connect_timeout_seconds = float(raw) if raw else _DEFAULT_CONNECT_TIMEOUT_SEC
        self._connect_timeout = max(1.0, float(connect_timeout_seconds))

    @property
    def is_started(self) -> bool:
        return self._started

    def _ensure_errlog(self) -> IO[str]:
        """Open the stderr sink for stdio servers — a real file, always.

        stdio_client's default errlog is sys.stderr, which the Textual TUI
        replaces with an object lacking a usable fileno(); anyio's subprocess
        spawn then fails with 'fileno' and the server silently never registers
        (issue #188). A dedicated log file fixes that and keeps server noise
        off the screen; devnull is the fallback if the file can't be opened.
        """
        if self._errlog is None or self._errlog.closed:
            try:
                self._errlog_path.parent.mkdir(parents=True, exist_ok=True)
                self._errlog = self._errlog_path.open("a", encoding="utf-8", errors="replace")
            except Exception as exc:  # noqa: BLE001
                logger.debug("MCP errlog file unavailable (%s); using devnull", exc)
                self._errlog = open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115
        return self._errlog

    @staticmethod
    async def _close_quietly(stack: AsyncExitStack) -> None:
        """Best-effort cleanup of a failed server's contexts, bounded in time."""
        with contextlib.suppress(Exception, asyncio.TimeoutError):
            await asyncio.wait_for(stack.aclose(), timeout=5.0)

    async def _register_tools(self, name: str, session: Any) -> int:
        """Register tools from a connected session. Returns count of registered tools."""
        tools_result = await session.list_tools()
        tools = tools_result.tools if hasattr(tools_result, "tools") else []
        count = 0
        for tool in tools:
            tool_name: str = tool.name
            if tool_name in self._tool_router:
                existing = self._tool_router[tool_name]
                logger.warning(
                    "MCP tool name collision: '%s' provided by both '%s' and '%s'; '%s' wins",
                    tool_name,
                    existing,
                    name,
                    existing,
                )
                continue

            self._tool_router[tool_name] = name
            self._tool_defs.append(
                {
                    "name": tool_name,
                    "description": tool.description or "",
                    "input_schema": (
                        tool.inputSchema
                        if isinstance(tool.inputSchema, dict)
                        else {"type": "object", "properties": {}}
                    ),
                }
            )
            count += 1
        return count

    async def start(self) -> None:
        """Connect to all configured servers. Skips servers that fail to connect."""
        if self._started:
            return
        self._started = True

        if not self._servers:
            return

        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError:
            logger.warning("mcp package not installed; MCP support disabled")
            return

        await self._exit_stack.__aenter__()

        for name, cfg in self._servers.items():
            server_type = cfg.get("type", "stdio")

            if server_type == "stdio" and not cfg.get("command", ""):
                logger.warning("MCP server '%s': missing 'command', skipping", name)
                continue
            if server_type == "sse" and not cfg.get("url", ""):
                logger.warning("MCP server '%s': missing 'url' for sse type, skipping", name)
                continue
            if server_type not in ("stdio", "sse"):
                logger.warning(
                    "MCP server '%s': unsupported type '%s', skipping", name, server_type
                )
                continue

            # Per-server stack: a failed/hung server is cleaned up immediately
            # and never wedges the others (or the whole start()) with it.
            server_stack = AsyncExitStack()
            await server_stack.__aenter__()
            try:
                session, count = await asyncio.wait_for(
                    self._connect_and_register(
                        server_stack,
                        name,
                        cfg,
                        server_type,
                        ClientSession,
                        StdioServerParameters,
                        stdio_client,
                    ),
                    timeout=self._connect_timeout,
                )
                self._sessions[name] = session
                self._exit_stack.push_async_callback(server_stack.aclose)
                logger.info("Connected to MCP server '%s' (%d tools)", name, count)
            except asyncio.TimeoutError:
                logger.warning(
                    "MCP server '%s': handshake timed out after %.0fs, skipping",
                    name,
                    self._connect_timeout,
                )
                await self._close_quietly(server_stack)
            except Exception as e:
                logger.warning("Failed to connect to MCP server '%s': %s", name, e)
                await self._close_quietly(server_stack)

    async def _connect_and_register(
        self,
        stack: AsyncExitStack,
        name: str,
        cfg: dict[str, Any],
        server_type: str,
        client_session_cls: Any,
        stdio_params_cls: Any,
        stdio_client_fn: Any,
    ) -> tuple[Any, int]:
        """Enter transport + session contexts on ``stack``, handshake, register."""
        if server_type == "stdio":
            params = stdio_params_cls(
                command=cfg.get("command", ""),
                args=cfg.get("args", []),
                env=cfg.get("env") or None,
            )
            read, write = await stack.enter_async_context(
                stdio_client_fn(params, errlog=self._ensure_errlog())
            )
        else:  # sse — validated by the caller
            from mcp.client.sse import sse_client

            read, write = await stack.enter_async_context(sse_client(url=cfg.get("url", "")))

        session: Any = await stack.enter_async_context(client_session_cls(read, write))
        await session.initialize()
        count = await self._register_tools(name, session)
        return session, count

    async def stop(self) -> None:
        """Close all MCP connections."""
        if not self._started:
            return
        try:
            await self._exit_stack.__aexit__(None, None, None)
        except Exception as e:
            logger.debug("MCP cleanup error: %s", e)
        if self._errlog is not None:
            with contextlib.suppress(Exception):
                self._errlog.close()
            self._errlog = None

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Return Anthropic-format tool definitions from all connected servers."""
        return list(self._tool_defs)

    async def call(self, tool_name: str, tool_input: dict[str, Any]) -> tuple[str, str | None]:
        """Call a tool on the appropriate MCP server. Never raises — returns error as text."""
        server_name = self._tool_router.get(tool_name)
        if server_name is None:
            return f"MCP tool '{tool_name}' not found.", None

        session = self._sessions.get(server_name)
        if session is None:
            return f"MCP server '{server_name}' is not connected.", None

        try:
            result = await session.call_tool(tool_name, arguments=tool_input)
        except Exception as e:
            logger.warning("MCP tool '%s' call failed: %s", tool_name, e)
            return f"MCP tool '{tool_name}' error: {e}", None

        # Extract text and optional image from content blocks
        text_parts: list[str] = []
        image_b64: str | None = None

        content = result.content if hasattr(result, "content") else []
        for item in content:
            item_type = getattr(item, "type", None)
            if item_type == "text":
                text_parts.append(item.text)
            elif item_type == "image":
                # item.data is already base64, item.mimeType e.g. "image/jpeg"
                image_b64 = item.data

        text = "\n".join(text_parts) if text_parts else "(no output)"
        return text, image_b64
