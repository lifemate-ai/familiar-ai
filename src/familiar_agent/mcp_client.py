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

import json
import logging
import os
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG = Path.home() / ".familiar-ai.json"


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

    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path or _resolve_config_path()
        self._servers = _load_servers(self._config_path)
        self._sessions: dict[str, Any] = {}  # server_name → ClientSession
        # tool_name → server_name (for routing)
        self._tool_router: dict[str, str] = {}
        # Cached tool definitions (Anthropic format)
        self._tool_defs: list[dict[str, Any]] = []
        self._exit_stack = AsyncExitStack()
        self._started = False

    @property
    def is_started(self) -> bool:
        return self._started

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

            try:
                if server_type == "stdio":
                    command = cfg.get("command", "")
                    args: list[str] = cfg.get("args", [])
                    env: dict[str, str] | None = cfg.get("env") or None

                    if not command:
                        logger.warning("MCP server '%s': missing 'command', skipping", name)
                        continue

                    params = StdioServerParameters(command=command, args=args, env=env)
                    read, write = await self._exit_stack.enter_async_context(stdio_client(params))
                    session: Any = await self._exit_stack.enter_async_context(
                        ClientSession(read, write)
                    )
                    await session.initialize()

                elif server_type == "sse":
                    from mcp.client.sse import sse_client

                    url = cfg.get("url", "")
                    if not url:
                        logger.warning(
                            "MCP server '%s': missing 'url' for sse type, skipping", name
                        )
                        continue

                    read, write = await self._exit_stack.enter_async_context(sse_client(url=url))
                    session = await self._exit_stack.enter_async_context(ClientSession(read, write))
                    await session.initialize()

                else:
                    logger.warning(
                        "MCP server '%s': unsupported type '%s', skipping", name, server_type
                    )
                    continue

                self._sessions[name] = session
                count = await self._register_tools(name, session)
                logger.info("Connected to MCP server '%s' (%d tools)", name, count)

            except Exception as e:
                logger.warning("Failed to connect to MCP server '%s': %s", name, e)

    async def stop(self) -> None:
        """Close all MCP connections."""
        if not self._started:
            return
        try:
            await self._exit_stack.__aexit__(None, None, None)
        except Exception as e:
            logger.debug("MCP cleanup error: %s", e)

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
