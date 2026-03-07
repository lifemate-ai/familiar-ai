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
