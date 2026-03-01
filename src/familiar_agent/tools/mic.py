"""Microphone capture — streams PCM 16 kHz 16-bit mono to an async callback."""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 1600  # 100 ms at 16 kHz


class MicCapture:
    """Capture audio from the default microphone using *sounddevice*.

    The callback converts raw CFFI buffer data to ``bytes`` and schedules
    the async *on_audio* coroutine on the event loop.
    """

    def __init__(self, on_audio) -> None:  # noqa: ANN001 – Callable[[bytes], Awaitable]
        self._on_audio = on_audio
        self._stream = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        """Start capturing from the default input device."""
        import sounddevice as sd

        self._loop = loop

        def _callback(indata, frames, time_info, status):  # noqa: ANN001, ARG001
            if status:
                logger.debug("Mic status: %s", status)
            # indata is a CFFI buffer from RawInputStream
            pcm_bytes = bytes(indata)
            if self._loop and not self._loop.is_closed():
                self._loop.call_soon_threadsafe(
                    lambda b=pcm_bytes: self._loop.create_task(self._on_audio(b))
                )

        self._stream = sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=CHANNELS,
            dtype="int16",
            callback=_callback,
        )
        self._stream.start()
        logger.info("Microphone capture started (device: default)")

    def stop(self) -> None:
        """Stop capturing."""
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            logger.info("Microphone capture stopped")
