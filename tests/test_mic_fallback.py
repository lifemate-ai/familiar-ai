"""PulseAudio (parec) STT fallback — issue #153.

On WSL2/WSLg, PortAudio often cannot enumerate the RDPSource microphone even
though PulseAudio-level capture works. Both STT paths (realtime capture and
push-to-talk batch) must fall back to parec, and the selection must be
forceable via FAMILIAR_STT_BACKEND.
"""

from __future__ import annotations

import asyncio
import io
import sys
import wave
from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_agent.tools import mic
from familiar_agent.tools.mic import (
    MicCapture,
    ParecCapture,
    create_mic_capture,
    parec_command,
    probe_parec,
)

# A fake "parec": emits 0.3 s of s16le@16k mono, then keeps the pipe open.
_FAKE_PAREC = [
    sys.executable,
    "-c",
    "import sys, time; sys.stdout.buffer.write(b'\\x01\\x02' * 4800); "
    "sys.stdout.buffer.flush(); time.sleep(30)",
]

# ---------------------------------------------------------------------------
# Probes and backend selection
# ---------------------------------------------------------------------------


def test_parec_command_and_probe(monkeypatch):
    monkeypatch.setattr(mic.shutil, "which", lambda _: "/usr/bin/parec")
    command = parec_command()
    assert command is not None and command[0] == "/usr/bin/parec"
    assert "--format=s16le" in command
    assert "--rate=16000" in command
    ok, detail = probe_parec()
    assert ok

    monkeypatch.setattr(mic.shutil, "which", lambda _: None)
    assert parec_command() is None
    ok, detail = probe_parec()
    assert not ok and "pulseaudio-utils" in detail


def test_auto_prefers_sounddevice(monkeypatch):
    monkeypatch.delenv("FAMILIAR_STT_BACKEND", raising=False)
    monkeypatch.setattr(mic, "probe_sounddevice_input", lambda: (True, "dev"))
    capture = create_mic_capture(AsyncMock())
    assert isinstance(capture, MicCapture)


def test_auto_falls_back_to_parec_when_no_input_device(monkeypatch):
    """The issue #153 situation: PortAudio empty, PulseAudio available."""
    monkeypatch.delenv("FAMILIAR_STT_BACKEND", raising=False)
    monkeypatch.setattr(mic, "probe_sounddevice_input", lambda: (False, "no input devices"))
    monkeypatch.setattr(mic.shutil, "which", lambda _: "/usr/bin/parec")
    capture = create_mic_capture(AsyncMock())
    assert isinstance(capture, ParecCapture)


def test_auto_raises_clear_error_when_both_unavailable(monkeypatch):
    monkeypatch.delenv("FAMILIAR_STT_BACKEND", raising=False)
    monkeypatch.setattr(mic, "probe_sounddevice_input", lambda: (False, "no input devices"))
    monkeypatch.setattr(mic.shutil, "which", lambda _: None)
    with pytest.raises(RuntimeError) as excinfo:
        create_mic_capture(AsyncMock())
    assert "parec" in str(excinfo.value)


def test_env_forces_backend(monkeypatch):
    monkeypatch.setenv("FAMILIAR_STT_BACKEND", "parec")
    monkeypatch.setattr(mic.shutil, "which", lambda _: "/usr/bin/parec")
    assert isinstance(create_mic_capture(AsyncMock()), ParecCapture)

    monkeypatch.setenv("FAMILIAR_STT_BACKEND", "sounddevice")
    # Forced sounddevice skips the probe entirely (start() will diagnose).
    assert isinstance(create_mic_capture(AsyncMock()), MicCapture)

    monkeypatch.setenv("FAMILIAR_STT_BACKEND", "parec")
    monkeypatch.setattr(mic.shutil, "which", lambda _: None)
    with pytest.raises(RuntimeError):
        create_mic_capture(AsyncMock())


# ---------------------------------------------------------------------------
# ParecCapture streaming (real subprocess, fake parec)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_parec_capture_streams_pcm_blocks():
    received: list[bytes] = []
    done = asyncio.Event()

    async def on_audio(pcm: bytes) -> None:
        received.append(pcm)
        if sum(len(b) for b in received) >= 9600:
            done.set()

    capture = ParecCapture(on_audio, command=_FAKE_PAREC)
    capture.start(asyncio.get_running_loop())
    try:
        await asyncio.wait_for(done.wait(), timeout=10)
    finally:
        capture.stop()

    total = b"".join(received)
    assert len(total) >= 9600
    assert total.startswith(b"\x01\x02")
    assert capture._process is None  # subprocess reaped


@pytest.mark.asyncio
async def test_parec_capture_stop_without_data_is_clean():
    capture = ParecCapture(
        AsyncMock(), command=[sys.executable, "-c", "import time; time.sleep(30)"]
    )
    capture.start(asyncio.get_running_loop())
    await asyncio.sleep(0.2)
    capture.stop()  # must terminate promptly, no hang
    assert capture._process is None


def test_parec_capture_missing_binary_raises():
    capture = ParecCapture(AsyncMock(), command=["/nonexistent/parec-xyz"])
    with pytest.raises(RuntimeError):
        capture.start(asyncio.new_event_loop())


# ---------------------------------------------------------------------------
# Push-to-talk batch path
# ---------------------------------------------------------------------------


def _wav_info(data: bytes) -> tuple[int, int, int]:
    with wave.open(io.BytesIO(data), "rb") as wav:
        return wav.getnchannels(), wav.getframerate(), wav.getnframes()


def test_record_parec_returns_valid_wav(monkeypatch):
    from familiar_agent.tools.stt import STTTool

    # Fake parec that emits 0.2 s of audio then exits (EOF ends the read loop).
    fake = [
        sys.executable,
        "-c",
        "import sys; sys.stdout.buffer.write(b'\\x03\\x04' * 3200)",
    ]
    monkeypatch.setattr("familiar_agent.tools.mic.shutil.which", lambda _: "unused")
    monkeypatch.setattr("familiar_agent.tools.mic.parec_command", lambda: fake)

    tool = STTTool(api_key="k")
    wav_bytes = tool._record_parec(asyncio.Event())
    assert wav_bytes is not None
    channels, rate, frames = _wav_info(wav_bytes)
    assert (channels, rate) == (1, 16000)
    assert frames == 3200


def test_record_parec_unavailable_returns_none(monkeypatch):
    from familiar_agent.tools.stt import STTTool

    monkeypatch.setattr("familiar_agent.tools.mic.shutil.which", lambda _: None)
    assert STTTool(api_key="k")._record_parec(asyncio.Event()) is None


@pytest.mark.asyncio
async def test_record_and_transcribe_falls_back_to_parec():
    from familiar_agent.tools.stt import STTTool

    tool = STTTool(api_key="k", rtsp_url="rtsp://cam/stream")
    tool._record_mic = MagicMock(return_value=None)  # PortAudio saw nothing
    tool._record_parec = MagicMock(return_value=b"fake-wav")
    tool._record_rtsp = AsyncMock()
    tool._transcribe_elevenlabs = AsyncMock(return_value="聞こえたで")

    text = await tool.record_and_transcribe(asyncio.Event())
    assert text == "聞こえたで"
    tool._record_parec.assert_called_once()
    tool._record_rtsp.assert_not_awaited()  # parec succeeded → no RTSP
    tool._transcribe_elevenlabs.assert_awaited_once_with(b"fake-wav")


@pytest.mark.asyncio
async def test_record_and_transcribe_rtsp_still_last_resort():
    from familiar_agent.tools.stt import STTTool

    tool = STTTool(api_key="k", rtsp_url="rtsp://cam/stream")
    tool._record_mic = MagicMock(return_value=None)
    tool._record_parec = MagicMock(return_value=None)
    tool._record_rtsp = AsyncMock(return_value=b"rtsp-wav")
    tool._transcribe_elevenlabs = AsyncMock(return_value="text")

    text = await tool.record_and_transcribe(asyncio.Event())
    assert text == "text"
    tool._record_rtsp.assert_awaited_once()
