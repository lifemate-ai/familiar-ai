from __future__ import annotations

from familiar_agent.config import CameraConfig


def test_camera_config_ptz_fields_fall_back_to_camera_settings(monkeypatch) -> None:
    monkeypatch.setenv("CAMERA_HOST", "rtsp://user:pass@192.168.1.206/live0")
    monkeypatch.setenv("CAMERA_USERNAME", "admin")
    monkeypatch.setenv("CAMERA_PASSWORD", "secret")
    monkeypatch.setenv("CAMERA_ONVIF_PORT", "2020")
    monkeypatch.delenv("CAMERA_PTZ_HOST", raising=False)
    monkeypatch.delenv("CAMERA_PTZ_USERNAME", raising=False)
    monkeypatch.delenv("CAMERA_PTZ_PASSWORD", raising=False)
    monkeypatch.delenv("CAMERA_PTZ_PORT", raising=False)

    config = CameraConfig()

    assert config.ptz_host == "rtsp://user:pass@192.168.1.206/live0"
    assert config.ptz_username == "admin"
    assert config.ptz_password == "secret"
    assert config.ptz_port == 2020


def test_camera_config_ptz_fields_use_explicit_overrides(monkeypatch) -> None:
    monkeypatch.setenv("CAMERA_HOST", "rtsp://user:pass@192.168.1.206/live0")
    monkeypatch.setenv("CAMERA_USERNAME", "admin")
    monkeypatch.setenv("CAMERA_PASSWORD", "secret")
    monkeypatch.setenv("CAMERA_ONVIF_PORT", "2020")
    monkeypatch.setenv("CAMERA_PTZ_HOST", "192.168.1.145")
    monkeypatch.setenv("CAMERA_PTZ_USERNAME", "ptz-user")
    monkeypatch.setenv("CAMERA_PTZ_PASSWORD", "ptz-pass")
    monkeypatch.setenv("CAMERA_PTZ_PORT", "8899")

    config = CameraConfig()

    assert config.ptz_host_override == "192.168.1.145"
    assert config.ptz_username_override == "ptz-user"
    assert config.ptz_password_override == "ptz-pass"
    assert config.ptz_port_override == 8899
    assert config.ptz_host == "192.168.1.145"
    assert config.ptz_username == "ptz-user"
    assert config.ptz_password == "ptz-pass"
    assert config.ptz_port == 8899


def test_camera_config_empty_ptz_override_falls_back(monkeypatch) -> None:
    monkeypatch.setenv("CAMERA_HOST", "192.168.1.206")
    monkeypatch.setenv("CAMERA_USERNAME", "admin")
    monkeypatch.setenv("CAMERA_PASSWORD", "secret")
    monkeypatch.setenv("CAMERA_PTZ_HOST", "")
    monkeypatch.setenv("CAMERA_PTZ_USERNAME", "")
    monkeypatch.setenv("CAMERA_PTZ_PASSWORD", "")
    monkeypatch.setenv("CAMERA_PTZ_PORT", "")

    config = CameraConfig()

    assert config.ptz_host == "192.168.1.206"
    assert config.ptz_username == "admin"
    assert config.ptz_password == "secret"
    assert config.ptz_port == config.port
