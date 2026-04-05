from __future__ import annotations

from pathlib import Path

from familiar_agent.bootstrap import load_app_bootstrap


def _clear_runtime_env(monkeypatch) -> None:
    for key in ("PLATFORM", "API_KEY", "MODEL", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"):
        monkeypatch.delenv(key, raising=False)


def test_load_app_bootstrap_needs_setup_when_env_missing(tmp_path: Path, monkeypatch) -> None:
    _clear_runtime_env(monkeypatch)

    state = load_app_bootstrap(tmp_path / ".env")

    assert state.env_path == tmp_path / ".env"
    assert state.configured is False
    assert state.needs_setup is True
    assert state.legacy_config_detected is False


def test_load_app_bootstrap_migrates_legacy_anthropic_env(tmp_path: Path, monkeypatch) -> None:
    _clear_runtime_env(monkeypatch)
    env_path = tmp_path / ".env"
    env_path.write_text("ANTHROPIC_API_KEY=sk-ant-old\nANTHROPIC_MODEL=claude-haiku\n")

    state = load_app_bootstrap(env_path)

    content = env_path.read_text(encoding="utf-8")
    assert state.configured is True
    assert state.needs_setup is False
    assert state.legacy_config_detected is True
    assert state.migrated is True
    assert "API_KEY=sk-ant-old" in content
    assert "MODEL=claude-haiku" in content
    assert "PLATFORM=anthropic" in content
