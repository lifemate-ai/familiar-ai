"""Tests for /btw slash command in FamiliarApp TUI."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock


class TestBtwInSlashCommands:
    """/btw must appear in the autocomplete command list."""

    def test_btw_in_slash_commands(self):
        """_SLASH_COMMANDS must contain /btw."""
        from familiar_agent.tui import _SLASH_COMMANDS

        cmds = [cmd for cmd, _ in _SLASH_COMMANDS]
        assert "/btw" in cmds, "/btw must be in _SLASH_COMMANDS"

    def test_btw_has_description(self):
        """/btw entry must have a non-empty description."""
        from familiar_agent.tui import _SLASH_COMMANDS

        for cmd, desc in _SLASH_COMMANDS:
            if cmd == "/btw":
                assert desc, "/btw must have a description"
                return
        assert False, "/btw not found in _SLASH_COMMANDS"


class TestHandleBtwCommand:
    """handle_btw_command() runs a single lightweight LLM call."""

    def test_handle_btw_command_exists(self):
        """tui module must expose handle_btw_command function."""
        import familiar_agent.tui as tui_mod

        assert hasattr(tui_mod, "handle_btw_command"), (
            "tui must define handle_btw_command(question, backend)"
        )

    def test_handle_btw_uses_backend_complete(self):
        """handle_btw_command calls backend.complete(), not agent.run()."""
        import asyncio
        from familiar_agent.tui import handle_btw_command

        backend = MagicMock()
        backend.complete = AsyncMock(return_value="quick answer")

        result = asyncio.get_event_loop().run_until_complete(
            handle_btw_command("what time is it?", backend)
        )

        backend.complete.assert_called_once()
        assert "what time is it?" in backend.complete.call_args[0][0]
        assert result == "quick answer"

    def test_handle_btw_does_not_use_agent_run(self):
        """handle_btw_command must NOT call agent.run()."""
        import asyncio
        from familiar_agent.tui import handle_btw_command

        backend = MagicMock()
        backend.complete = AsyncMock(return_value="answer")
        agent = MagicMock()

        asyncio.get_event_loop().run_until_complete(handle_btw_command("quick question", backend))

        # agent.run should not be involved
        agent.run.assert_not_called()

    def test_handle_btw_empty_question_returns_early(self):
        """handle_btw_command with empty string returns empty/None without calling LLM."""
        import asyncio
        from familiar_agent.tui import handle_btw_command

        backend = MagicMock()
        backend.complete = AsyncMock(return_value="")

        result = asyncio.get_event_loop().run_until_complete(handle_btw_command("", backend))
        # Should not call backend for empty input
        backend.complete.assert_not_called()
        assert not result


class TestBtwParsing:
    """Slash command '/btw <question>' is parsed correctly."""

    def test_btw_prefix_strips_command(self):
        """'/btw hello world' → question is 'hello world'."""
        from familiar_agent.tui import _parse_btw

        assert _parse_btw("/btw hello world") == "hello world"

    def test_btw_strips_whitespace(self):
        """/btw with extra spaces still works."""
        from familiar_agent.tui import _parse_btw

        assert _parse_btw("/btw  trimmed  ") == "trimmed"

    def test_btw_empty_returns_empty(self):
        """/btw alone (no question) → empty string."""
        from familiar_agent.tui import _parse_btw

        assert _parse_btw("/btw") == ""
        assert _parse_btw("/btw   ") == ""
