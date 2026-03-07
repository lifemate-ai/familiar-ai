"""Tests for ffmpeg-free TTS audio pipeline.

Ensures ElevenLabs PCM output + WAV header generation + sounddevice playback
replace all ffmpeg/ffplay subprocess calls.
"""

from __future__ import annotations

import struct
import wave
from unittest.mock import AsyncMock, patch

import pytest

from familiar_agent.tools.tts import _write_pcm_as_wav


# ---------------------------------------------------------------------------
# Tests: _write_pcm_as_wav
# ---------------------------------------------------------------------------


def _make_pcm(num_samples: int = 1600) -> bytes:
    """Generate silent 16-bit PCM samples."""
    return b"\x00\x00" * num_samples  # 16-bit silence


def test_write_pcm_as_wav_returns_path(tmp_path) -> None:
    pcm = _make_pcm()
    path = _write_pcm_as_wav(pcm, sample_rate=16000, tmp_dir=str(tmp_path))
    assert path.endswith(".wav")


def test_write_pcm_as_wav_readable_by_wave_module(tmp_path) -> None:
    """Standard library wave module must be able to parse the file."""
    pcm = _make_pcm(3200)  # 0.2s at 16kHz
    path = _write_pcm_as_wav(pcm, sample_rate=16000, tmp_dir=str(tmp_path))
    with wave.open(path, "rb") as w:
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        assert w.getframerate() == 16000
        assert w.getnframes() == 3200


def test_write_pcm_as_wav_correct_header(tmp_path) -> None:
    """WAV header must be exactly 44 bytes with correct RIFF/WAVE magic."""
    pcm = _make_pcm(100)
    path = _write_pcm_as_wav(pcm, sample_rate=16000, tmp_dir=str(tmp_path))
    with open(path, "rb") as f:
        header = f.read(44)
    assert header[:4] == b"RIFF"
    assert header[8:12] == b"WAVE"
    assert header[12:16] == b"fmt "
    assert header[36:40] == b"data"


def test_write_pcm_as_wav_correct_data_size(tmp_path) -> None:
    """Data size field in header must match actual PCM byte length."""
    pcm = _make_pcm(800)
    path = _write_pcm_as_wav(pcm, sample_rate=16000, tmp_dir=str(tmp_path))
    with open(path, "rb") as f:
        data = f.read()
    data_size = struct.unpack_from("<I", data, 40)[0]
    assert data_size == len(pcm)


def test_write_pcm_as_wav_different_sample_rates(tmp_path) -> None:
    """Should work for 22050 and 44100 Hz as well."""
    for sr in (22050, 44100):
        pcm = _make_pcm(sr)  # 1 second
        path = _write_pcm_as_wav(pcm, sample_rate=sr, tmp_dir=str(tmp_path))
        with wave.open(path, "rb") as w:
            assert w.getframerate() == sr


# ---------------------------------------------------------------------------
# Tests: ElevenLabs API payload uses pcm_16000
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tts_payload_requests_pcm_format() -> None:
    """TTSTool.say() must request pcm_16000 from ElevenLabs, not MP3."""
    from familiar_agent.tools.tts import TTSTool

    tool = TTSTool.__new__(TTSTool)
    tool.api_key = "test"
    tool.voice_id = "test_voice"
    tool.output = "local"
    tool.go2rtc_url = "http://localhost:1984"
    tool.go2rtc_stream = "test"
    tool._lock = __import__("asyncio").Lock()

    captured_payload: dict = {}

    class FakeResp:
        status = 200

        async def read(self):
            return _make_pcm(1600)

        async def text(self):
            return ""

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            pass

    class FakePost:
        def __init__(self, *a, **kw):
            captured_payload.update(kw.get("json", {}))

        async def __aenter__(self):
            return FakeResp()

        async def __aexit__(self, *a):
            pass

    class FakeSession:
        def post(self, *a, **kw):
            return FakePost(*a, **kw)

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            pass

    with patch("familiar_agent.tools.tts._play_local", new=AsyncMock(return_value=True)):
        with patch("aiohttp.ClientSession", return_value=FakeSession()):
            await tool.say("テスト")

    assert captured_payload.get("output_format") == "pcm_16000", (
        f"Expected output_format=pcm_16000, got: {captured_payload.get('output_format')}"
    )


# ---------------------------------------------------------------------------
# Tests: ffplay is NOT in the fallback chain
# ---------------------------------------------------------------------------


def test_ffplay_not_imported_or_called_in_play_local() -> None:
    """_play_local must not shell out to ffplay."""
    import inspect

    from familiar_agent.tools import tts

    source = inspect.getsource(tts._play_local)
    assert "ffplay" not in source, "_play_local still references ffplay"


# ---------------------------------------------------------------------------
# Tests: sounddevice fallback works
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_play_via_sounddevice_called_as_fallback(tmp_path) -> None:
    """When paplay and mpv are unavailable, sounddevice should be tried."""
    from familiar_agent.tools.tts import _play_local

    pcm = _make_pcm(1600)

    wav_path = _write_pcm_as_wav(pcm, sample_rate=16000, tmp_dir=str(tmp_path))

    # All external players unavailable
    with patch("shutil.which", return_value=None):
        with patch(
            "familiar_agent.tools.tts._play_via_sounddevice", new=AsyncMock(return_value=True)
        ) as mock_sd:
            result = await _play_local(wav_path)

    assert result is True
    mock_sd.assert_called_once()
