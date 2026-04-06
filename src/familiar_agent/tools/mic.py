"""Microphone capture — streams PCM 16 kHz 16-bit mono to an async callback."""

from __future__ import annotations

import asyncio
import logging
import os
import platform
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
