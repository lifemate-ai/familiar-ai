"""Tests for CameraTool — OpenCV mocked, no real hardware required."""

from __future__ import annotations

import base64
import threading
from unittest.mock import patch

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_camera_tool(host: str = "192.168.1.100"):
    """Create a CameraTool with the capture thread patched out."""
    from familiar_agent.tools.camera import CameraTool

    with patch.object(CameraTool, "start"):
        cam = CameraTool.__new__(CameraTool)
        cam.host = host
        cam.username = "admin"
        cam.password = "password"
        cam.port = 2020
        cam.preview = False
        cam.ptz_host = host
        cam.ptz_username = "admin"
        cam.ptz_password = "password"
        cam.ptz_port = 2020
        cam._cam_onvif = None
        cam._ptz = None
        cam._profile_token = None
        cam._cap = None
        cam._last_frame = None
        cam._running = False
        cam._thread = None
        cam._lock = threading.Lock()
    return cam


def _make_fake_frame(height: int = 480, width: int = 640) -> "np.ndarray":
    """Create a fake BGR numpy frame."""
    return np.zeros((height, width, 3), dtype=np.uint8)


# ---------------------------------------------------------------------------
# Tests: capture()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_capture_returns_none_when_no_frame():
    """capture() returns (None, None) when no frame has been grabbed yet."""
    cam = _make_camera_tool()
    cam._last_frame = None

    b64, path = await cam.capture()

    assert b64 is None
    assert path is None


@pytest.mark.asyncio
async def test_capture_returns_base64_jpeg_on_valid_frame():
    """capture() encodes a valid frame to base64 JPEG."""
    cam = _make_camera_tool()
    cam._last_frame = _make_fake_frame()

    b64, path = await cam.capture()

    assert b64 is not None
    # Should be valid base64
    decoded = base64.b64decode(b64)
    # JPEG magic bytes: FF D8 FF
    assert decoded[:2] == b"\xff\xd8"


@pytest.mark.asyncio
async def test_capture_saves_file_to_disk(tmp_path):
    """capture() writes the JPEG to disk and returns the path."""
    import familiar_agent.tools.camera as camera_module

    cam = _make_camera_tool()
    cam._last_frame = _make_fake_frame()

    original_dir = camera_module.CAPTURE_DIR
    camera_module.CAPTURE_DIR = tmp_path
    try:
        b64, path = await cam.capture()
    finally:
        camera_module.CAPTURE_DIR = original_dir

    assert path is not None
    assert b64 is not None
    assert (tmp_path / path.split("/")[-1]).exists()


@pytest.mark.asyncio
async def test_capture_resizes_large_frame():
    """capture() resizes frames taller than 640px."""
    cam = _make_camera_tool()
    cam._last_frame = _make_fake_frame(height=1080, width=1920)

    b64, _ = await cam.capture()

    assert b64 is not None
    # Decode and verify the JPEG was produced (resize didn't crash)
    decoded = base64.b64decode(b64)
    assert decoded[:2] == b"\xff\xd8"


# ---------------------------------------------------------------------------
# Tests: call()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_call_see_returns_image_on_success():
    """call('see', {}) returns (description, base64_image) on success."""
    cam = _make_camera_tool()

    async def _fake_capture():
        return "fakeb64", "/tmp/capture_123.jpg"

    cam.capture = _fake_capture

    result, img = await cam.call("see", {})

    assert img == "fakeb64"
    assert "saved to" in result


@pytest.mark.asyncio
async def test_call_see_returns_error_when_capture_fails():
    """call('see', {}) returns failure message when capture returns (None, None)."""
    cam = _make_camera_tool()

    async def _fake_capture():
        return None, None

    cam.capture = _fake_capture

    result, img = await cam.call("see", {})

    assert img is None
    assert "failed" in result.lower()


@pytest.mark.asyncio
async def test_call_look_delegates_to_move():
    """call('look', ...) delegates to move() and returns its result."""
    cam = _make_camera_tool()

    async def _fake_move(direction, degrees=30):
        return f"Moved {direction} by {degrees}°"

    cam.move = _fake_move

    result, img = await cam.call("look", {"direction": "left", "degrees": 45})

    assert "left" in result
    assert "45" in result
    assert img is None


@pytest.mark.asyncio
async def test_call_unknown_tool_returns_error():
    """call() with an unrecognized tool name returns an error string."""
    cam = _make_camera_tool()

    result, img = await cam.call("nonexistent", {})

    assert "Unknown" in result or "nonexistent" in result


def test_ptz_params_fall_back_to_stream_url_credentials():
    cam = _make_camera_tool("rtsp://stream-user:stream-pass@192.168.1.206/live0")
    cam.username = ""
    cam.password = ""
    cam.ptz_host = cam.host
    cam.ptz_username = ""
    cam.ptz_password = ""

    host, username, password, port = cam._get_ptz_connection_params()

    assert host == "192.168.1.206"
    assert username == "stream-user"
    assert password == "stream-pass"
    assert port == 2020


def test_ptz_params_prefer_explicit_overrides():
    cam = _make_camera_tool("rtsp://stream-user:stream-pass@192.168.1.206/live0")
    cam.ptz_host = "192.168.1.145"
    cam.ptz_username = "ptz-user"
    cam.ptz_password = "ptz-pass"
    cam.ptz_port = 8899

    host, username, password, port = cam._get_ptz_connection_params()

    assert host == "192.168.1.145"
    assert username == "ptz-user"
    assert password == "ptz-pass"
    assert port == 8899


@pytest.mark.asyncio
async def test_aclose_closes_onvif_transports() -> None:
    """aclose() must close the ONVIF client (aiohttp sessions) and drop PTZ handles."""
    from unittest.mock import AsyncMock, MagicMock

    from familiar_agent.tools.camera import CameraTool

    tool = CameraTool.__new__(CameraTool)
    cam = MagicMock()
    cam.close = AsyncMock()
    tool._cam_onvif = cam
    tool._ptz = MagicMock()
    await tool.aclose()
    cam.close.assert_awaited_once()
    assert tool._cam_onvif is None and tool._ptz is None
    await tool.aclose()  # idempotent
    cam.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_move_closes_the_onvif_client() -> None:
    """A dropped PTZ client must have its transports closed (no unclosed sessions)."""
    from unittest.mock import AsyncMock, MagicMock

    from familiar_agent.tools.camera import CameraTool

    tool = CameraTool.__new__(CameraTool)
    cam = MagicMock()
    cam.close = AsyncMock()
    tool._cam_onvif = cam
    tool._ptz = MagicMock()
    tool._ptz.RelativeMove = AsyncMock(side_effect=RuntimeError("no ptz"))
    tool._profile_token = "p"
    text = await tool.move("left", 30)
    assert "failed" in text.lower()
    cam.close.assert_awaited_once()
    assert tool._cam_onvif is None and tool._ptz is None


@pytest.mark.asyncio
async def test_onvif_probe_failure_is_cached_and_sweeps_transports(monkeypatch) -> None:
    """A camera without PTZ: probe once, close every transport, don't re-probe on each look()."""
    from unittest.mock import AsyncMock, MagicMock

    from familiar_agent.tools import camera as cam_mod

    stray = MagicMock()
    stray.close = AsyncMock()

    class FakeONVIF:
        instances: list = []

        def __init__(self, *a, **kw):
            self.services = {}
            self.devicemgmt = stray  # created by the library before update_xaddrs failed
            FakeONVIF.instances.append(self)

        async def close(self):
            pass

        async def update_xaddrs(self):
            raise RuntimeError("no ONVIF here")

    monkeypatch.setattr(cam_mod, "ONVIFCamera", FakeONVIF)
    tool = cam_mod.CameraTool.__new__(cam_mod.CameraTool)
    tool._cam_onvif = None
    tool._ptz = None
    tool._ptz_probe_failed_at = 0.0
    tool._get_ptz_connection_params = lambda: ("192.168.1.145", "u", "p", 2020)  # type: ignore[method-assign]

    assert await tool._ensure_connected() is False
    assert len(FakeONVIF.instances) == 3  # 2020, 8080, 80
    assert stray.close.await_count == 3  # every half-built transport closed
    assert await tool._ensure_connected() is False
    assert len(FakeONVIF.instances) == 3  # negative cache: no re-probe
