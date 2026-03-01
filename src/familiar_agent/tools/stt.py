"""Speech-to-Text tool using ElevenLabs Scribe API.

Records audio from:
1. Local PC microphone (via sounddevice) — primary
2. Camera RTSP stream (via ffmpeg) — fallback when no mic is available

Transcription is done via the ElevenLabs /v1/speech-to-text endpoint.
"""

from __future__ import annotations

import asyncio
import io
import logging
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING

import aiohttp

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

_SAMPLE_RATE = 16000  # Hz — ElevenLabs Scribe works well at 16kHz
_CHANNELS = 1  # mono
_ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"


class STTTool:
    """Record audio and transcribe via ElevenLabs Scribe."""

    def __init__(self, api_key: str, language: str = "ja", rtsp_url: str = "") -> None:
        self._api_key = api_key
        self._language = language
        self._rtsp_url = rtsp_url

    # ── public API ────────────────────────────────────────────────────────

    async def record_and_transcribe(self, stop_event: asyncio.Event) -> str:
        """Record until stop_event is set, then transcribe and return text."""
        # Try PC mic first
        audio_bytes = await asyncio.to_thread(self._record_mic, stop_event)

        # Fallback to RTSP camera mic
        if audio_bytes is None and self._rtsp_url:
            logger.info("STT: no local mic, falling back to RTSP camera mic")
            audio_bytes = await self._record_rtsp(stop_event)

        if not audio_bytes:
            return ""

        return await self._transcribe_elevenlabs(audio_bytes)

    # ── recording helpers ─────────────────────────────────────────────────

    def _record_mic(self, stop_event: asyncio.Event) -> bytes | None:
        """Block and record from the default microphone until stop_event is set.

        Returns WAV bytes, or None if no microphone is available.
        """
        try:
            import numpy as np
            import sounddevice as sd
            import soundfile as sf
        except ImportError:
            logger.warning("STT: sounddevice/soundfile not installed")
            return None

        chunks: list = []

        try:
            with sd.InputStream(
                samplerate=_SAMPLE_RATE,
                channels=_CHANNELS,
                dtype="float32",
            ) as stream:
                logger.info("STT: recording from local mic...")
                while not stop_event.is_set():
                    chunk, _ = stream.read(1024)
                    chunks.append(chunk)
                    time.sleep(0.01)  # yield slightly; this is already in a thread
        except sd.PortAudioError as e:
            logger.warning("STT: PortAudio error (no mic?): %s", e)
            return None

        if not chunks:
            return None

        audio = np.concatenate(chunks, axis=0)
        buf = io.BytesIO()
        sf.write(buf, audio, _SAMPLE_RATE, format="WAV", subtype="PCM_16")
        return buf.getvalue()

    async def _record_rtsp(self, stop_event: asyncio.Event) -> bytes:
        """Record audio from the RTSP stream using ffmpeg until stop_event is set."""
        tmp = Path(tempfile.mktemp(suffix=".wav"))
        start = asyncio.get_event_loop().time()

        # Start ffmpeg recording in the background
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-loglevel",
            "error",
            "-rtsp_transport",
            "tcp",
            "-i",
            self._rtsp_url,
            "-ar",
            str(_SAMPLE_RATE),
            "-ac",
            str(_CHANNELS),
            "-y",
            str(tmp),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )

        # Wait for stop_event
        while not stop_event.is_set():
            await asyncio.sleep(0.1)

        duration = asyncio.get_event_loop().time() - start
        logger.info("STT: RTSP recording stopped after %.1fs", duration)

        try:
            proc.terminate()
        except ProcessLookupError:
            pass  # ffmpeg already exited on its own
        try:
            await asyncio.wait_for(proc.communicate(), timeout=5.0)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except ProcessLookupError:
                pass

        try:
            data = tmp.read_bytes()
        except FileNotFoundError:
            logger.warning("STT: RTSP ffmpeg produced no output")
            data = b""
        finally:
            tmp.unlink(missing_ok=True)

        return data

    # ── transcription ─────────────────────────────────────────────────────

    async def _transcribe_elevenlabs(self, audio_bytes: bytes) -> str:
        """Send audio to ElevenLabs Scribe and return the transcript."""
        if not audio_bytes:
            return ""

        headers = {"xi-api-key": self._api_key}
        form = aiohttp.FormData()
        form.add_field(
            "file",
            audio_bytes,
            filename="audio.wav",
            content_type="audio/wav",
        )
        form.add_field("model_id", "scribe_v1")
        if self._language:
            form.add_field("language_code", self._language)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(_ELEVENLABS_STT_URL, headers=headers, data=form) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        logger.warning("STT: ElevenLabs error %d: %s", resp.status, body[:200])
                        return ""
                    data = await resp.json()
                    text: str = data.get("text", "")
                    logger.info("STT: transcribed %d chars", len(text))
                    return text
        except Exception as e:
            logger.warning("STT: transcription failed: %s", e)
            return ""
