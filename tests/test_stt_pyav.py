"""Tests for ffmpeg-free STT RTSP audio recording via PyAV.

The _record_rtsp() method must use PyAV (av package) instead of
shelling out to ffmpeg subprocess.
"""

from __future__ import annotations

import asyncio
import inspect
from unittest.mock import MagicMock, patch

import pytest

from familiar_agent.tools.stt import STTTool


# ---------------------------------------------------------------------------
# Tests: ffmpeg subprocess NOT used in _record_rtsp
# ---------------------------------------------------------------------------


def test_record_rtsp_does_not_call_ffmpeg_subprocess() -> None:
    """_record_rtsp must not shell out to the ffmpeg binary."""
    source = inspect.getsource(STTTool._record_rtsp)
    assert "create_subprocess_exec" not in source, "_record_rtsp still uses subprocess for ffmpeg"
    assert '"ffmpeg"' not in source, "_record_rtsp still calls ffmpeg directly"


def test_record_rtsp_uses_av() -> None:
    """_record_rtsp should import/use the av (PyAV) library."""
    source = inspect.getsource(STTTool._record_rtsp)
    assert "av" in source, "_record_rtsp should use PyAV (import av)"


# ---------------------------------------------------------------------------
# Tests: _record_rtsp returns WAV bytes with PyAV mock
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_record_rtsp_returns_wav_bytes_on_success() -> None:
    """_record_rtsp should return non-empty WAV bytes when PyAV succeeds."""
    tool = STTTool.__new__(STTTool)
    tool._rtsp_url = "rtsp://fake/stream"

    # Do NOT pre-set stop_event — let the mock stream naturally exhaust its frames
    stop_event = asyncio.Event()

    import numpy as np

    # Build a minimal mock frame
    mock_frame = MagicMock()
    mock_frame.to_ndarray.return_value = np.zeros((1, 160), dtype="int16")

    mock_resampled = [mock_frame]

    mock_resampler = MagicMock()
    mock_resampler.resample.return_value = mock_resampled

    mock_audio_stream = MagicMock()
    mock_audio_stream.type = "audio"

    mock_container = MagicMock()
    mock_container.streams = [mock_audio_stream]
    # Decode returns 1 frame; loop exits naturally after processing it
    mock_container.decode.return_value = [mock_frame]

    mock_av = MagicMock()
    mock_av.open.return_value = mock_container
    mock_av.AudioResampler.return_value = mock_resampler

    with patch.dict("sys.modules", {"av": mock_av}):
        result = await tool._record_rtsp(stop_event)

    # Result should be non-empty bytes (WAV)
    assert isinstance(result, bytes)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_record_rtsp_returns_empty_bytes_when_av_unavailable() -> None:
    """If PyAV is not installed, _record_rtsp should return empty bytes gracefully."""
    tool = STTTool.__new__(STTTool)
    tool._rtsp_url = "rtsp://fake/stream"

    stop_event = asyncio.Event()
    stop_event.set()

    with patch.dict("sys.modules", {"av": None}):
        result = await tool._record_rtsp(stop_event)

    assert result == b""


@pytest.mark.asyncio
async def test_record_rtsp_returns_empty_bytes_on_connection_error() -> None:
    """If RTSP connection fails, _record_rtsp should return empty bytes."""
    tool = STTTool.__new__(STTTool)
    tool._rtsp_url = "rtsp://nonexistent/stream"

    stop_event = asyncio.Event()
    stop_event.set()

    mock_av = MagicMock()
    mock_av.open.side_effect = Exception("Connection refused")

    with patch.dict("sys.modules", {"av": mock_av}):
        result = await tool._record_rtsp(stop_event)

    assert result == b""
