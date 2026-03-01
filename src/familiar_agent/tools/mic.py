"""Microphone capture — streams PCM 16 kHz 16-bit mono to an async callback."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

TARGET_RATE = 16000  # ElevenLabs Realtime STT expects 16 kHz PCM
CHANNELS = 1
_BLOCK_MS = 100  # capture block size in milliseconds


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

        self._loop = loop

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

    def stop(self) -> None:
        """Stop capturing."""
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            logger.info("Microphone capture stopped")
