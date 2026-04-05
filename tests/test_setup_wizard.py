"""Tests for Phase 6-1 setup wizard logic.

TDD: written before implementation.
Tests cover the non-GUI logic: first-run detection, .env generation,
API key validation, and camera discovery interface.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from familiar_agent.setup import (
    SetupConfig,
    generate_env_file,
    is_first_run,
    migrate_legacy_env_file,
    save_setup_config,
    validate_anthropic_key,
    validate_camera_connection,
    discover_onvif_cameras,
)


# ---------------------------------------------------------------------------
# Tests: first-run detection
# ---------------------------------------------------------------------------


def test_is_first_run_when_no_env_file(tmp_path: Path):
    """Returns True when no .env file exists in the given directory."""
    assert is_first_run(env_dir=tmp_path) is True


def test_is_not_first_run_when_env_exists(tmp_path: Path):
    """Returns False when a .env file already exists."""
    (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=sk-ant-test\n")
    assert is_first_run(env_dir=tmp_path) is False


def test_is_first_run_default_is_cwd():
    """is_first_run() without args checks the current working directory."""
    # Just verify it returns a bool without error
    result = is_first_run()
    assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Tests: SetupConfig dataclass
# ---------------------------------------------------------------------------


def test_setup_config_defaults():
    """SetupConfig has sensible defaults for optional fields."""
    config = SetupConfig(api_key="sk-ant-test")
    assert config.platform == "anthropic"
    assert config.api_key == "sk-ant-test"
    assert config.model == ""  # empty = use default
    assert config.camera_host == ""
    assert config.camera_username == ""
    assert config.camera_password == ""
    assert config.camera_onvif_port == "2020"
    assert config.elevenlabs_api_key == ""
    assert config.auto_desire is False
    assert config.auto_say is True


def test_setup_config_with_camera():
    """SetupConfig stores camera settings."""
    config = SetupConfig(
        api_key="sk-ant-test",
        camera_host="192.168.1.100",
        camera_username="admin",
        camera_password="secret",
        camera_onvif_port="2020",
    )
    assert config.camera_host == "192.168.1.100"
    assert config.camera_username == "admin"


# ---------------------------------------------------------------------------
# Tests: .env generation
# ---------------------------------------------------------------------------


def test_generate_env_contains_required_key(tmp_path: Path):
    """Generated .env contains the unified API key and platform."""
    config = SetupConfig(platform="anthropic", api_key="sk-ant-abc123")
    env_path = tmp_path / ".env"
    generate_env_file(config, path=env_path)
    content = env_path.read_text()
    assert "PLATFORM=anthropic" in content
    assert "API_KEY=sk-ant-abc123" in content


def test_generate_env_includes_camera_when_provided(tmp_path: Path):
    """Generated .env includes camera settings when camera host is given."""
    config = SetupConfig(
        api_key="sk-ant-test",
        camera_host="192.168.1.50",
        camera_username="admin",
        camera_password="pass",
    )
    env_path = tmp_path / ".env"
    generate_env_file(config, path=env_path)
    content = env_path.read_text()
    assert "CAMERA_HOST=192.168.1.50" in content
    assert "CAMERA_USERNAME=admin" in content
    assert "CAMERA_PASSWORD=pass" in content


def test_generate_env_skips_empty_optional_camera(tmp_path: Path):
    """Generated .env omits CAMERA_* lines when camera_host is empty."""
    config = SetupConfig(api_key="sk-ant-test", camera_host="")
    env_path = tmp_path / ".env"
    generate_env_file(config, path=env_path)
    content = env_path.read_text()
    assert "CAMERA_HOST" not in content


def test_generate_env_includes_elevenlabs_when_provided(tmp_path: Path):
    """Generated .env includes ElevenLabs key when provided."""
    config = SetupConfig(api_key="sk-ant-test", elevenlabs_api_key="el-key-123")
    env_path = tmp_path / ".env"
    generate_env_file(config, path=env_path)
    content = env_path.read_text()
    assert "ELEVENLABS_API_KEY=el-key-123" in content


def test_generate_env_skips_empty_elevenlabs(tmp_path: Path):
    """Generated .env omits ELEVENLABS_API_KEY when not provided."""
    config = SetupConfig(api_key="sk-ant-test", elevenlabs_api_key="")
    env_path = tmp_path / ".env"
    generate_env_file(config, path=env_path)
    content = env_path.read_text()
    assert "ELEVENLABS_API_KEY" not in content


def test_generate_env_creates_parent_dirs(tmp_path: Path):
    """generate_env_file creates parent directories if they don't exist."""
    config = SetupConfig(api_key="sk-ant-test")
    env_path = tmp_path / "subdir" / "nested" / ".env"
    generate_env_file(config, path=env_path)
    assert env_path.exists()


def test_generate_env_includes_custom_model(tmp_path: Path):
    """Generated .env includes MODEL when specified."""
    config = SetupConfig(api_key="sk-ant-test", model="claude-sonnet-4-6")
    env_path = tmp_path / ".env"
    generate_env_file(config, path=env_path)
    content = env_path.read_text()
    assert "MODEL=claude-sonnet-4-6" in content


def test_save_setup_config_preserves_blank_sensitive_fields(tmp_path: Path):
    env_path = tmp_path / ".env"
    env_path.write_text("API_KEY=keep-me\nCAMERA_PASSWORD=secret\n", encoding="utf-8")

    save_setup_config(
        SetupConfig(platform="anthropic", api_key="", camera_password=""),
        path=env_path,
        preserve_empty_sensitive=True,
    )

    content = env_path.read_text(encoding="utf-8")
    assert "API_KEY=keep-me" in content
    assert "CAMERA_PASSWORD=secret" in content


def test_migrate_legacy_env_file_adds_unified_keys(tmp_path: Path):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "ANTHROPIC_API_KEY=sk-ant-old\nANTHROPIC_MODEL=claude-sonnet-4-6\n",
        encoding="utf-8",
    )

    migrated, notes = migrate_legacy_env_file(env_path)

    content = env_path.read_text(encoding="utf-8")
    assert migrated is True
    assert notes
    assert "PLATFORM=anthropic" in content
    assert "API_KEY=sk-ant-old" in content
    assert "MODEL=claude-sonnet-4-6" in content


# ---------------------------------------------------------------------------
# Tests: API key validation
# ---------------------------------------------------------------------------


def test_validate_anthropic_key_accepts_valid_format():
    """Valid sk-ant-... key passes format check."""
    ok, _ = validate_anthropic_key("sk-ant-api03-abc123")
    assert ok is True


def test_validate_anthropic_key_rejects_empty():
    """Empty key fails validation."""
    ok, msg = validate_anthropic_key("")
    assert ok is False
    assert msg  # error message provided


def test_validate_anthropic_key_rejects_wrong_prefix():
    """Key without sk-ant- prefix fails validation."""
    ok, msg = validate_anthropic_key("openai-key-xyz")
    assert ok is False
    assert msg


def test_validate_anthropic_key_returns_error_message():
    """validate_anthropic_key returns (False, non-empty message) on failure."""
    ok, msg = validate_anthropic_key("")
    assert isinstance(ok, bool)
    assert isinstance(msg, str)


# ---------------------------------------------------------------------------
# Tests: camera connection validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_camera_connection_success():
    """Returns (True, '') when ONVIF camera responds."""
    with patch("familiar_agent.setup.ONVIFCamera") as mock_cls:
        mock_cam = MagicMock()
        mock_cam.create_devicemgmt_service = MagicMock()
        mock_cls.return_value = mock_cam

        ok, msg = await validate_camera_connection(
            host="192.168.1.1", username="admin", password="pass", port=2020
        )
    assert ok is True
    assert msg == ""


@pytest.mark.asyncio
async def test_validate_camera_connection_failure():
    """Returns (False, error_msg) when camera connection raises."""
    with patch("familiar_agent.setup.ONVIFCamera") as mock_cls:
        mock_cls.side_effect = Exception("Connection refused")

        ok, msg = await validate_camera_connection(
            host="192.168.1.1", username="admin", password="wrong", port=2020
        )
    assert ok is False
    assert "Connection refused" in msg


# ---------------------------------------------------------------------------
# Tests: camera discovery
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_discover_onvif_cameras_returns_list():
    """discover_onvif_cameras() returns a list (possibly empty if no cameras)."""
    with patch("familiar_agent.setup._ws_discover") as mock_discover:
        mock_discover.return_value = []
        result = await discover_onvif_cameras()
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_discover_onvif_cameras_parses_host():
    """Discovered camera entries include a 'host' field."""
    fake_service = MagicMock()
    fake_service.getXAddrs.return_value = ["http://192.168.1.42:80/onvif/device_service"]

    with patch("familiar_agent.setup._ws_discover") as mock_discover:
        mock_discover.return_value = [fake_service]
        result = await discover_onvif_cameras()

    assert len(result) == 1
    assert result[0]["host"] == "192.168.1.42"


@pytest.mark.asyncio
async def test_discover_onvif_cameras_handles_discovery_error():
    """discover_onvif_cameras() returns empty list when discovery raises."""
    with patch("familiar_agent.setup._ws_discover") as mock_discover:
        mock_discover.side_effect = Exception("Network error")
        result = await discover_onvif_cameras()
    assert result == []
