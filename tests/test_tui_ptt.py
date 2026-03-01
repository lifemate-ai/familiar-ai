"""Tests for Push-to-Talk (Space key recording) in FamiliarApp TUI."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


class TestPushToTalkAttributes:
    """FamiliarApp must have PTT state attributes."""

    def _make_app(self):
        from familiar_agent.tui import FamiliarApp

        agent = MagicMock()
        agent.config.agent_name = "A"
        agent.config.companion_name = "U"
        desires = MagicMock()

        with patch("familiar_agent.tui._make_banner", return_value=""):
            return FamiliarApp(agent, desires)

    def test_ptt_active_attribute_exists(self):
        """FamiliarApp must have _ptt_active boolean attribute."""
        app = self._make_app()
        assert hasattr(app, "_ptt_active"), "FamiliarApp must have _ptt_active"
        assert app._ptt_active is False

    def test_action_start_ptt_exists(self):
        """FamiliarApp must have action_start_ptt() method."""
        from familiar_agent.tui import FamiliarApp

        assert hasattr(FamiliarApp, "action_start_ptt")
        assert callable(FamiliarApp.action_start_ptt)

    def test_action_stop_ptt_exists(self):
        """FamiliarApp must have action_stop_ptt() method."""
        from familiar_agent.tui import FamiliarApp

        assert hasattr(FamiliarApp, "action_stop_ptt")
        assert callable(FamiliarApp.action_stop_ptt)


class TestSpaceKeyBinding:
    """Space key must trigger PTT when STT is configured."""

    def test_space_binding_exists(self):
        """FamiliarApp.BINDINGS includes a space binding."""
        from familiar_agent.tui import FamiliarApp

        keys = [b.key for b in FamiliarApp.BINDINGS]
        assert "space" in keys, "space binding must exist for PTT"

    def test_ptt_starts_recording(self):
        """action_start_ptt() sets _ptt_active to True and starts recording."""
        from familiar_agent.tui import FamiliarApp

        agent = MagicMock()
        agent.config.agent_name = "A"
        agent.config.companion_name = "U"
        agent.stt = MagicMock()
        desires = MagicMock()

        with patch("familiar_agent.tui._make_banner", return_value=""):
            app = FamiliarApp(agent, desires)

        app._log_system = MagicMock()
        app._recording = False
        app._ptt_active = False
        app.run_worker = MagicMock()
        app.query_one = MagicMock(return_value=MagicMock())

        # action_start_ptt should set _ptt_active
        app.action_start_ptt()
        assert app._ptt_active is True

    def test_ptt_stop_sets_stop_event(self):
        """action_stop_ptt() sets _stop_recording event to stop STT."""
        from familiar_agent.tui import FamiliarApp

        agent = MagicMock()
        agent.config.agent_name = "A"
        agent.config.companion_name = "U"
        agent.stt = MagicMock()
        desires = MagicMock()

        with patch("familiar_agent.tui._make_banner", return_value=""):
            app = FamiliarApp(agent, desires)

        app._log_system = MagicMock()
        app._ptt_active = True
        app._recording = True

        app.action_stop_ptt()
        assert app._ptt_active is False

    def test_ptt_noop_without_stt(self):
        """action_start_ptt() does nothing when STT is not configured."""
        from familiar_agent.tui import FamiliarApp

        agent = MagicMock()
        agent.config.agent_name = "A"
        agent.config.companion_name = "U"
        agent.stt = None
        desires = MagicMock()

        with patch("familiar_agent.tui._make_banner", return_value=""):
            app = FamiliarApp(agent, desires)

        app._log_system = MagicMock()
        app._ptt_active = False

        app.action_start_ptt()
        assert app._ptt_active is False  # Must not change if no STT
