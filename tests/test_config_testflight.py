from __future__ import annotations

import importlib


def test_testflight_defaults_disable_mobility(monkeypatch) -> None:
    monkeypatch.setenv("TESTFLIGHT_MODE", "true")
    monkeypatch.delenv("MOBILITY_ENABLED", raising=False)

    import familiar_agent.config as cfg

    importlib.reload(cfg)
    loaded = cfg.AgentConfig()
    assert loaded.testflight_mode is True
    assert loaded.mobility_enabled is False


def test_mobility_enabled_env_overrides_testflight_default(monkeypatch) -> None:
    monkeypatch.setenv("TESTFLIGHT_MODE", "true")
    monkeypatch.setenv("MOBILITY_ENABLED", "true")

    import familiar_agent.config as cfg

    importlib.reload(cfg)
    loaded = cfg.AgentConfig()
    assert loaded.testflight_mode is True
    assert loaded.mobility_enabled is True
