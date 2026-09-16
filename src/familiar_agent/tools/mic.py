"""Microphone capture — streams PCM 16 kHz 16-bit mono to an async callback.

Two backends, picked by :func:`create_mic_capture`:

1. ``MicCapture`` — sounddevice/PortAudio (the default everywhere it works).
2. ``ParecCapture`` — PulseAudio's native ``parec``. On WSL2/WSLg, PortAudio
   often cannot enumerate the RDPSource microphone bridge even though
   PulseAudio-level capture works fine (issue #153); parec talks to
   PulseAudio directly and resamples to 16 kHz mono s16le for us.

``FAMILIAR_STT_BACKEND=sounddevice|parec`` forces a backend; default is auto
(sounddevice, falling back to parec when no input device is visible).
"""

from __future__ import annotations

import asyncio
import logging
import os
import platform
import shutil
import subprocess
import threading
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

TARGET_RATE = 16000  # ElevenLabs Realtime STT expects 16 kHz PCM
CHANNELS = 1
_BLOCK_MS = 100  # capture block size in milliseconds


def _is_wsl2() -> bool:
    release = platform.release().lower()
    return bool(os.environ.get("WSL_INTEROP") or os.environ.get("WSL_DISTRO_NAME")) or (
        "microsoft" in release or "wsl" in release
    )


def describe_sounddevice_input_failure(exc: Exception | None = None) -> str:
    """Return a user-facing microphone diagnosis for sounddevice failures."""
    detail = str(exc).strip() if exc else ""
    parts: list[str] = []
    if detail:
        parts.append(detail)

    if _is_wsl2():
        parts.append(
            "WSL2/WSLg hint: set PULSE_SERVER=unix:/mnt/wslg/PulseServer and install "
            "pulseaudio-utils plus libasound2-plugins. If `python -m sounddevice` shows no "
            "input devices, PortAudio cannot see the WSLg microphone bridge yet."
        )
    else:
        parts.append(
            "No default microphone input device is available to sounddevice. Try "
            "`python -m sounddevice` and check your OS microphone permissions."
        )

    return " ".join(part for part in parts if part)


def probe_sounddevice_input() -> tuple[bool, str]:
    """Best-effort check that sounddevice can see a default input device."""
    try:
        import sounddevice as sd
    except ImportError:
        return False, "sounddevice is not installed."
    except Exception as exc:  # noqa: BLE001 — e.g. OSError: PortAudio library not found
        return False, f"sounddevice unavailable: {exc}"

    try:
        devices = sd.query_devices()
    except Exception as exc:  # pragma: no cover - covered via query(kind="input") too
        return False, describe_sounddevice_input_failure(exc)

    if not devices:
        return False, describe_sounddevice_input_failure(
            RuntimeError("sounddevice did not enumerate any audio devices.")
        )

    try:
        info = sd.query_devices(kind="input")
    except Exception as exc:
        return False, describe_sounddevice_input_failure(exc)

    name = str(info.get("name", "default")).strip() or "default"
    sample_rate = int(info.get("default_samplerate", TARGET_RATE) or TARGET_RATE)
    return True, f"{name} @ {sample_rate} Hz"


def _resample(pcm_bytes: bytes, from_rate: int) -> bytes:
    """Resample int16 mono PCM from *from_rate* to TARGET_RATE (16 kHz).

    Uses linear interpolation — fast, dependency-free, good enough for STT.
    """
    if from_rate == TARGET_RATE:
        return pcm_bytes
    arr = np.frombuffer(pcm_bytes, dtype=np.int16)
    n_out = int(len(arr) * TARGET_RATE / from_rate)
    indices = np.linspace(0, len(arr) - 1, n_out)
    resampled = np.interp(indices, np.arange(len(arr)), arr).astype(np.int16)
    return resampled.tobytes()


class MicCapture:
    """Capture audio from the default microphone using *sounddevice*.

    Automatically detects the device's native sample rate and resamples to
    16 kHz before handing PCM bytes to *on_audio*.  This avoids
    ``paInvalidSampleRate`` on devices whose native rate differs from 16 kHz
    (e.g. USB mics that default to 44 100 Hz).
    """

    def __init__(self, on_audio) -> None:  # noqa: ANN001 – Callable[[bytes], Awaitable]
        self._on_audio = on_audio
        self._stream: Any = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._native_rate: int = TARGET_RATE

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        """Start capturing from the default input device."""
        import sounddevice as sd

        ok, detail = probe_sounddevice_input()
        if not ok:
            raise RuntimeError(detail)

        self._loop = loop

        try:
            # Use the device's native sample rate to avoid paInvalidSampleRate
            device_info = sd.query_devices(kind="input")
            self._native_rate = int(device_info["default_samplerate"])
            block_size = int(self._native_rate * _BLOCK_MS / 1000)

            logger.info(
                "Microphone capture: device=%s native_rate=%d target_rate=%d",
                device_info.get("name", "default"),
                self._native_rate,
                TARGET_RATE,
            )

            def _callback(indata, frames, time_info, status):  # noqa: ANN001, ARG001
                if status:
                    logger.debug("Mic status: %s", status)
                pcm = _resample(bytes(indata), self._native_rate)
                if self._loop and not self._loop.is_closed():
                    self._loop.call_soon_threadsafe(
                        lambda b=pcm: self._loop.create_task(self._on_audio(b))
                    )

            self._stream = sd.RawInputStream(
                samplerate=self._native_rate,
                blocksize=block_size,
                channels=CHANNELS,
                dtype="int16",
                callback=_callback,
            )
            self._stream.start()
        except sd.PortAudioError as exc:
            raise RuntimeError(describe_sounddevice_input_failure(exc)) from exc

    def stop(self) -> None:
        """Stop capturing."""
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            logger.info("Microphone capture stopped")


def parec_command() -> list[str] | None:
    """The parec argv for 16 kHz mono s16le capture, or None if unavailable."""
    path = shutil.which("parec")
    if not path:
        return None
    return [
        path,
        "--format=s16le",
        f"--rate={TARGET_RATE}",
        f"--channels={CHANNELS}",
        f"--latency-msec={_BLOCK_MS}",
    ]


def probe_parec() -> tuple[bool, str]:
    """Best-effort check that PulseAudio-native capture is available."""
    if parec_command() is None:
        return False, "parec not found — install pulseaudio-utils."
    return True, "parec (PulseAudio native capture)"


class ParecCapture:
    """Capture via PulseAudio's ``parec`` subprocess (the WSL2/WSLg fallback).

    Same interface as :class:`MicCapture`. parec outputs raw s16le PCM at the
    requested rate, so no resampling is needed; a reader thread forwards
    fixed-size blocks to *on_audio* on the event loop.
    """

    def __init__(self, on_audio, command: list[str] | None = None) -> None:  # noqa: ANN001
        self._on_audio = on_audio
        self._command = command
        self._process: subprocess.Popen | None = None
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._running = False

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        command = self._command or parec_command()
        if command is None:
            raise RuntimeError("parec not found — install pulseaudio-utils.")
        self._loop = loop
        try:
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except OSError as exc:
            raise RuntimeError(f"parec failed to start: {exc}") from exc
        logger.info("Microphone capture: parec (PulseAudio) @ %d Hz", TARGET_RATE)
        self._running = True
        self._thread = threading.Thread(target=self._reader, daemon=True, name="parec-reader")
        self._thread.start()

    def _reader(self) -> None:
        block_bytes = int(TARGET_RATE * 2 * _BLOCK_MS / 1000)  # s16le mono
        process = self._process
        if process is None or process.stdout is None:
            return
        while self._running:
            pcm = process.stdout.read(block_bytes)
            if not pcm:
                if self._running:
                    logger.warning("parec ended unexpectedly (PulseAudio gone?)")
                break
            maybe_loop = self._loop
            if maybe_loop is None or maybe_loop.is_closed():
                break
            loop: asyncio.AbstractEventLoop = maybe_loop

            def _dispatch(b: bytes = pcm, target_loop: asyncio.AbstractEventLoop = loop) -> None:
                target_loop.create_task(self._on_audio(b))

            loop.call_soon_threadsafe(_dispatch)

    def stop(self) -> None:
        """Stop capturing and reap the subprocess."""
        self._running = False
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
        logger.info("Microphone capture stopped (parec)")


def create_mic_capture(on_audio) -> "MicCapture | ParecCapture":  # noqa: ANN001
    """Pick a capture backend: sounddevice → parec → clear error.

    ``FAMILIAR_STT_BACKEND=sounddevice|parec`` forces one; the default (auto)
    prefers sounddevice and falls back to parec when PortAudio cannot see any
    input device — the WSL2/WSLg situation from issue #153, where PulseAudio
    capture works but PortAudio enumeration is empty.
    """
    forced = os.environ.get("FAMILIAR_STT_BACKEND", "").strip().lower()
    if forced == "sounddevice":
        return MicCapture(on_audio)
    if forced == "parec":
        ok, detail = probe_parec()
        if not ok:
            raise RuntimeError(detail)
        return ParecCapture(on_audio)

    ok, _ = probe_sounddevice_input()
    if ok:
        return MicCapture(on_audio)
    parec_ok, parec_detail = probe_parec()
    if parec_ok:
        logger.info("Mic: sounddevice sees no input device; using parec (PulseAudio) instead")
        return ParecCapture(on_audio)
    raise RuntimeError(
        describe_sounddevice_input_failure() + f" parec fallback also unavailable: {parec_detail}"
    )
