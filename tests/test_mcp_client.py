"""Tests for MCPClientManager — stdio + SSE transport, tool routing, error handling.

All tests mock the mcp package so no real MCP server is needed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


class _AsyncCM:
    """Minimal async context manager that yields a fixed value."""

    def __init__(self, value):
        self._value = value

    async def __aenter__(self):
        return self._value

    async def __aexit__(self, *args):
        pass


def _tool(name: str, description: str = "", schema: dict | None = None) -> MagicMock:
    t = MagicMock()
    t.name = name
    t.description = description
    t.inputSchema = schema or {"type": "object", "properties": {}}
    return t


def _session(*tools: MagicMock) -> AsyncMock:
    """Return a session mock that lists the given tools."""
    tools_result = MagicMock()
    tools_result.tools = list(tools)
    session = AsyncMock()
    session.initialize = AsyncMock()
    session.list_tools = AsyncMock(return_value=tools_result)
    return session


def _patch_mcp(sessions_in_order: list[AsyncMock]) -> dict:
    """
    Build a sys.modules patch dict.  ClientSession returns sessions sequentially.
    """
    call_idx = [0]

    class _ClientSessionCM:
        def __init__(self, *args, **kwargs):
            self._idx = call_idx[0]
            call_idx[0] += 1

        async def __aenter__(self):
            return sessions_in_order[self._idx]

        async def __aexit__(self, *args):
            pass

    rw = (MagicMock(), MagicMock())
    transport_cm = _AsyncCM(rw)

    mcp_mod = MagicMock()
    mcp_mod.ClientSession = _ClientSessionCM
    mcp_mod.StdioServerParameters = MagicMock()

    mcp_stdio = MagicMock()
    mcp_stdio.stdio_client = MagicMock(return_value=transport_cm)

    mcp_sse = MagicMock()
    mcp_sse.sse_client = MagicMock(return_value=transport_cm)

    return {
        "mcp": mcp_mod,
        "mcp.client": MagicMock(),
        "mcp.client.stdio": mcp_stdio,
        "mcp.client.sse": mcp_sse,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_config_file_returns_empty_tools(tmp_path: Path) -> None:
    """MCPClientManager with a non-existent config file exposes no tools."""
    from familiar_agent.mcp_client import MCPClientManager

    mgr = MCPClientManager(config_path=tmp_path / "missing.json")
    await mgr.start()
    assert mgr.get_tool_definitions() == []


@pytest.mark.asyncio
async def test_empty_mcp_servers_returns_empty_tools(tmp_path: Path) -> None:
    """Config with empty mcpServers dict connects to nothing."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"mcpServers": {}}))

    from familiar_agent.mcp_client import MCPClientManager

    mgr = MCPClientManager(config_path=cfg)
    await mgr.start()
    assert mgr.get_tool_definitions() == []


@pytest.mark.asyncio
async def test_stdio_server_registers_tools(tmp_path: Path) -> None:
    """stdio server: tools are registered and accessible via get_tool_definitions."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "fs": {
                        "type": "stdio",
                        "command": "npx",
                        "args": ["-y", "@mcp/server-fs"],
                    }
                }
            }
        )
    )
    sess = _session(_tool("read_file", "Read a file"), _tool("write_file", "Write a file"))

    from familiar_agent.mcp_client import MCPClientManager

    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules, _patch_mcp([sess])
    ):
        mgr = MCPClientManager(config_path=cfg)
        await mgr.start()

    defs = mgr.get_tool_definitions()
    names = {d["name"] for d in defs}
    assert names == {"read_file", "write_file"}


@pytest.mark.asyncio
async def test_sse_server_registers_tools(tmp_path: Path) -> None:
    """SSE server: tools are registered via sse_client transport."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "memory": {
                        "type": "sse",
                        "url": "http://localhost:3000/sse",
                    }
                }
            }
        )
    )
    sess = _session(_tool("remember", "Store a memory"), _tool("recall", "Retrieve memories"))

    from familiar_agent.mcp_client import MCPClientManager

    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules, _patch_mcp([sess])
    ):
        mgr = MCPClientManager(config_path=cfg)
        await mgr.start()

    defs = mgr.get_tool_definitions()
    names = {d["name"] for d in defs}
    assert names == {"remember", "recall"}


@pytest.mark.asyncio
async def test_unknown_type_is_skipped(tmp_path: Path) -> None:
    """Server with unsupported type is skipped; no crash."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "ws": {
                        "type": "websocket",
                        "url": "ws://localhost:9000",
                    }
                }
            }
        )
    )

    from familiar_agent.mcp_client import MCPClientManager

    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(sys.modules, _patch_mcp([])):
        mgr = MCPClientManager(config_path=cfg)
        await mgr.start()

    assert mgr.get_tool_definitions() == []


@pytest.mark.asyncio
async def test_stdio_missing_command_is_skipped(tmp_path: Path) -> None:
    """stdio server without 'command' is skipped gracefully."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"mcpServers": {"broken": {"type": "stdio", "args": []}}}))

    from familiar_agent.mcp_client import MCPClientManager

    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(sys.modules, _patch_mcp([])):
        mgr = MCPClientManager(config_path=cfg)
        await mgr.start()

    assert mgr.get_tool_definitions() == []


@pytest.mark.asyncio
async def test_sse_missing_url_is_skipped(tmp_path: Path) -> None:
    """SSE server without 'url' is skipped gracefully."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"mcpServers": {"broken": {"type": "sse"}}}))

    from familiar_agent.mcp_client import MCPClientManager

    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(sys.modules, _patch_mcp([])):
        mgr = MCPClientManager(config_path=cfg)
        await mgr.start()

    assert mgr.get_tool_definitions() == []


@pytest.mark.asyncio
async def test_connection_failure_is_skipped(tmp_path: Path) -> None:
    """If a server raises on connect, it is skipped; no crash."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"mcpServers": {"bad": {"type": "stdio", "command": "nonexistent"}}}))

    from unittest.mock import patch

    mcp_mod = MagicMock()
    mcp_mod.StdioServerParameters = MagicMock()

    class _BoomCM:
        async def __aenter__(self):
            raise ConnectionRefusedError("Server not found")

        async def __aexit__(self, *args):
            pass

    mcp_stdio = MagicMock()
    mcp_stdio.stdio_client = MagicMock(return_value=_BoomCM())
    # ClientSession should never be reached
    mcp_mod.ClientSession = MagicMock()

    with patch.dict(
        sys.modules,
        {
            "mcp": mcp_mod,
            "mcp.client": MagicMock(),
            "mcp.client.stdio": mcp_stdio,
            "mcp.client.sse": MagicMock(),
        },
    ):
        from familiar_agent.mcp_client import MCPClientManager

        mgr = MCPClientManager(config_path=cfg)
        await mgr.start()

    assert mgr.get_tool_definitions() == []


@pytest.mark.asyncio
async def test_tool_name_collision_first_wins(tmp_path: Path) -> None:
    """When two servers expose the same tool name, first-registered server wins."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "server_a": {"type": "stdio", "command": "cmd_a"},
                    "server_b": {"type": "stdio", "command": "cmd_b"},
                }
            }
        )
    )
    sess_a = _session(_tool("shared_tool"))
    sess_b = _session(_tool("shared_tool"))

    from familiar_agent.mcp_client import MCPClientManager

    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules, _patch_mcp([sess_a, sess_b])
    ):
        mgr = MCPClientManager(config_path=cfg)
        await mgr.start()

    # Only one definition for the shared tool
    defs = mgr.get_tool_definitions()
    assert len(defs) == 1
    assert defs[0]["name"] == "shared_tool"


@pytest.mark.asyncio
async def test_mcp_not_installed_returns_empty(tmp_path: Path) -> None:
    """If mcp package is not installed, get_tool_definitions() returns []."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"mcpServers": {"srv": {"type": "stdio", "command": "cmd"}}}))

    from unittest.mock import patch

    with patch.dict(
        sys.modules,
        {"mcp": None, "mcp.client": None, "mcp.client.stdio": None, "mcp.client.sse": None},
    ):
        from familiar_agent.mcp_client import MCPClientManager

        mgr = MCPClientManager(config_path=cfg)
        await mgr.start()

    assert mgr.get_tool_definitions() == []


@pytest.mark.asyncio
async def test_call_unknown_tool_returns_error(tmp_path: Path) -> None:
    """call() for a tool that was never registered returns an error string, no exception."""
    from familiar_agent.mcp_client import MCPClientManager

    mgr = MCPClientManager(config_path=tmp_path / "missing.json")
    text, image = await mgr.call("nonexistent_tool", {})
    assert "not found" in text.lower() or "nonexistent_tool" in text
    assert image is None


@pytest.mark.asyncio
async def test_call_routes_to_correct_server_and_returns_text(tmp_path: Path) -> None:
    """call() routes to the right session and extracts text from content blocks."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps({"mcpServers": {"mem": {"type": "sse", "url": "http://localhost:9000/sse"}}})
    )
    sess = _session(_tool("remember"))

    # Fake call_tool result
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "Stored successfully."
    call_result = MagicMock()
    call_result.content = [text_block]
    sess.call_tool = AsyncMock(return_value=call_result)

    from familiar_agent.mcp_client import MCPClientManager

    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules, _patch_mcp([sess])
    ):
        mgr = MCPClientManager(config_path=cfg)
        await mgr.start()
        text, image = await mgr.call("remember", {"text": "hello"})

    assert text == "Stored successfully."
    assert image is None
    sess.call_tool.assert_awaited_once_with("remember", arguments={"text": "hello"})


# ---------------------------------------------------------------------------
# Issue #188 — TUI-safe stderr handling + hung-server containment
# ---------------------------------------------------------------------------


_FASTMCP_SERVER = """\
import sys
from mcp.server.fastmcp import FastMCP

print("Test MCP server running on stdio", file=sys.stderr, flush=True)
mcp = FastMCP("test-server")


@mcp.tool()
def echo_tool(text: str) -> str:
    \"\"\"Echo the input text back.\"\"\"
    return f"echo: {text}"


if __name__ == "__main__":
    mcp.run()
"""


def _stdio_config(tmp_path: Path, command: str, args: list[str]) -> Path:
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps({"mcpServers": {"test": {"type": "stdio", "command": command, "args": args}}})
    )
    return cfg


@pytest.mark.asyncio
async def test_stdio_registers_tools_when_stderr_has_no_fileno(tmp_path: Path) -> None:
    """Regression for #188: under Textual, sys.stderr lacks a usable fileno and
    stdio_client's default errlog broke the subprocess spawn — tools silently
    never registered. The explicit errlog file must make this work."""
    import io

    server = tmp_path / "server.py"
    server.write_text(_FASTMCP_SERVER)
    cfg = _stdio_config(tmp_path, sys.executable, [str(server)])

    from familiar_agent.mcp_client import MCPClientManager

    real_stderr = sys.stderr
    sys.stderr = io.StringIO()  # Textual-like stderr replacement
    try:
        mgr = MCPClientManager(
            config_path=cfg,
            errlog_path=tmp_path / "mcp-stderr.log",
            connect_timeout_seconds=30,
        )
        await mgr.start()
    finally:
        sys.stderr = real_stderr

    try:
        names = {d["name"] for d in mgr.get_tool_definitions()}
        assert names == {"echo_tool"}
        text, image = await mgr.call("echo_tool", {"text": "hi"})
        assert text == "echo: hi"
        assert image is None
        # The server's stderr banner landed in the log file, not on screen.
        assert "running on stdio" in (tmp_path / "mcp-stderr.log").read_text()
    finally:
        await mgr.stop()


@pytest.mark.asyncio
async def test_hung_server_times_out_and_is_skipped(tmp_path: Path) -> None:
    """A server that never completes the MCP handshake must not wedge start()."""
    import time as _time

    cfg = _stdio_config(tmp_path, sys.executable, ["-c", "import time; time.sleep(60)"])

    from familiar_agent.mcp_client import MCPClientManager

    mgr = MCPClientManager(
        config_path=cfg,
        errlog_path=tmp_path / "mcp-stderr.log",
        connect_timeout_seconds=1.5,
    )
    started = _time.monotonic()
    await mgr.start()
    elapsed = _time.monotonic() - started

    try:
        assert mgr.get_tool_definitions() == []
        # 1.5s handshake budget + bounded cleanup — far below the 60s sleep.
        assert elapsed < 15
    finally:
        await mgr.stop()


@pytest.mark.asyncio
async def test_stdio_client_receives_real_file_errlog(tmp_path: Path) -> None:
    """The mocked transport must be invoked with an errlog that has a fileno."""
    cfg = _stdio_config(tmp_path, "some-command", [])
    sess = _session(_tool("t"))

    from unittest.mock import patch

    from familiar_agent.mcp_client import MCPClientManager

    modules = _patch_mcp([sess])
    with patch.dict(sys.modules, modules):
        mgr = MCPClientManager(config_path=cfg, errlog_path=tmp_path / "err.log")
        await mgr.start()

    stdio_mock = modules["mcp.client.stdio"].stdio_client
    assert stdio_mock.call_count == 1
    errlog = stdio_mock.call_args.kwargs["errlog"]
    errlog.fileno()  # must not raise — a real file, never sys.stderr


@pytest.mark.asyncio
async def test_start_mcp_early_is_idempotent() -> None:
    """start_mcp_early creates at most one in-flight handshake task."""
    import asyncio

    from tests.test_agent_react_loop import _make_agent

    agent = _make_agent()
    mcp = MagicMock()
    mcp.is_started = False
    started = asyncio.Event()

    async def _slow_start():
        await started.wait()

    mcp.start = _slow_start
    agent._mcp = mcp
    agent._mcp_start_task = None

    agent.start_mcp_early()
    task1 = agent._mcp_start_task
    assert task1 is not None
    agent.start_mcp_early()
    assert agent._mcp_start_task is task1  # no second task while in flight

    started.set()
    await task1
    mcp.is_started = True
    agent.start_mcp_early()
    assert agent._mcp_start_task is task1  # started manager → no new task

    # Without an MCP manager it is a no-op.
    agent._mcp = None
    agent._mcp_start_task = None
    agent.start_mcp_early()
    assert agent._mcp_start_task is None


@pytest.mark.asyncio
async def test_call_extracts_image_from_content(tmp_path: Path) -> None:
    """call() extracts base64 image data when content includes an image block."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"mcpServers": {"cam": {"type": "stdio", "command": "cam_cmd"}}}))
    sess = _session(_tool("capture"))

    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "Image captured."
    img_block = MagicMock()
    img_block.type = "image"
    img_block.data = "base64encodedimagedata=="
    call_result = MagicMock()
    call_result.content = [text_block, img_block]
    sess.call_tool = AsyncMock(return_value=call_result)

    from familiar_agent.mcp_client import MCPClientManager

    with __import__("unittest.mock", fromlist=["patch"]).patch.dict(
        sys.modules, _patch_mcp([sess])
    ):
        mgr = MCPClientManager(config_path=cfg)
        await mgr.start()
        text, image = await mgr.call("capture", {})

    assert text == "Image captured."
    assert image == "base64encodedimagedata=="
