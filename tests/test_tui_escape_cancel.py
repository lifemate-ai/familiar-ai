"""Tests for ESC-key cancel feature in FamiliarApp TUI."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch


class TestFamiliarAppHasCancelEvent:
    """FamiliarApp должен иметь _cancel_event и action_cancel_turn()."""

    def test_cancel_event_attribute_exists(self):
        """FamiliarApp.__init__ initialises _cancel_event as asyncio.Event."""
        from familiar_agent.tui import FamiliarApp

        agent = MagicMock()
        agent.config.agent_name = "TestAgent"
        agent.config.companion_name = "TestUser"
        desires = MagicMock()

        with patch("familiar_agent.tui._make_banner", return_value="banner"):
            app = FamiliarApp(agent, desires)

        assert hasattr(app, "_cancel_event"), "FamiliarApp must have _cancel_event"
        assert isinstance(app._cancel_event, asyncio.Event)

    def test_agent_task_attribute_exists(self):
        """FamiliarApp.__init__ initialises _agent_task as None."""
        from familiar_agent.tui import FamiliarApp

        agent = MagicMock()
        agent.config.agent_name = "TestAgent"
        agent.config.companion_name = "TestUser"
        desires = MagicMock()

        with patch("familiar_agent.tui._make_banner", return_value="banner"):
            app = FamiliarApp(agent, desires)

        assert hasattr(app, "_agent_task"), "FamiliarApp must have _agent_task"
        assert app._agent_task is None

    def test_escape_binding_exists(self):
        """FamiliarApp.BINDINGS includes an 'escape' binding."""
        from familiar_agent.tui import FamiliarApp

        keys = [b.key for b in FamiliarApp.BINDINGS]
        assert "escape" in keys, "escape binding must exist in FamiliarApp.BINDINGS"

    def test_action_cancel_turn_method_exists(self):
        """FamiliarApp.action_cancel_turn is a method."""
        from familiar_agent.tui import FamiliarApp

        assert hasattr(FamiliarApp, "action_cancel_turn"), (
            "FamiliarApp must have action_cancel_turn method"
        )
        assert callable(FamiliarApp.action_cancel_turn)


class TestCancelTurnSetsEvent:
    """action_cancel_turn() sets _cancel_event and logs a system message."""

    def test_action_cancel_turn_sets_event(self):
        """action_cancel_turn() should set _cancel_event."""
        from familiar_agent.tui import FamiliarApp

        agent = MagicMock()
        agent.config.agent_name = "A"
        agent.config.companion_name = "U"
        desires = MagicMock()

        with patch("familiar_agent.tui._make_banner", return_value=""):
            app = FamiliarApp(agent, desires)

        # Patch _log_system so we don't need a real Textual DOM
        app._log_system = MagicMock()
        app._agent_running = True

        app.action_cancel_turn()
        assert app._cancel_event.is_set(), "_cancel_event must be set after action_cancel_turn"

    def test_action_cancel_turn_noop_when_not_running(self):
        """action_cancel_turn() does nothing meaningful when agent is not running."""
        from familiar_agent.tui import FamiliarApp

        agent = MagicMock()
        agent.config.agent_name = "A"
        agent.config.companion_name = "U"
        desires = MagicMock()

        with patch("familiar_agent.tui._make_banner", return_value=""):
            app = FamiliarApp(agent, desires)

        app._log_system = MagicMock()
        app._agent_running = False

        # Should not raise
        app.action_cancel_turn()
        # No assertion on event — just must not crash


class TestInterruptMessageConstant:
    """The CC-style interrupt message constant must exist."""

    def test_interrupt_message_in_tui(self):
        """tui module exports INTERRUPT_MSG constant matching CC convention."""
        import familiar_agent.tui as tui_mod

        assert hasattr(tui_mod, "INTERRUPT_MSG"), "tui must define INTERRUPT_MSG"
        assert "[Request interrupted" in tui_mod.INTERRUPT_MSG
