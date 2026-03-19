"""Realtime Speech-to-Text using ElevenLabs WebSocket API (Scribe v2 Realtime).

Unlike the batch STT in ``stt.py`` (record → file → REST), this module keeps a
persistent WebSocket open and streams PCM audio in real time.  ElevenLabs VAD
detects speech boundaries and commits transcripts automatically — no button
press required.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
from urllib.parse import urlencode

import aiohttp

logger = logging.getLogger(__name__)

_STT_WS_BASE_URL = "wss://api.elevenlabs.io/v1/speech-to-text/realtime"


def _build_stt_ws_url(language_code: str = "") -> str:
    params = {
        "model_id": "scribe_v2_realtime",
        "audio_format": "pcm_16000",
        "commit_strategy": "vad",
        "vad_silence_threshold_secs": "1.0",
        # Experimental: batch STT already disables audio-event tagging.
        # If realtime accepts the same flag, this suppresses non-speech tags.
        "tag_audio_events": "false",
    }
    if language_code:
        params["language_code"] = language_code
    return f"{_STT_WS_BASE_URL}?{urlencode(params)}"


def _extract_transcript_text(data: dict) -> str:
    value = data.get("text")
    if isinstance(value, str):
        return value.strip()
    value = data.get("transcript")
    if isinstance(value, str):
        return value.strip()
    return ""


class RealtimeSttClient:
    """ElevenLabs Realtime STT WebSocket client.

    Streams PCM audio and fires callbacks on partial/committed transcripts.
    """

    def __init__(self, api_key: str, language_code: str = "") -> None:
        self.api_key = api_key
        self.language_code = language_code.strip()
        self._session: aiohttp.ClientSession | None = None
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._recv_task: asyncio.Task | None = None
        self._connected = False

        # Queues for transcript events
        self.on_partial: asyncio.Queue[str] | None = None
        self.on_committed: asyncio.Queue[str] | None = None

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        """Connect to ElevenLabs Realtime STT WebSocket."""
        await self._cleanup()
        self._session = aiohttp.ClientSession()
        headers = {"xi-api-key": self.api_key}
        ws_url = _build_stt_ws_url(self.language_code)
        try:
            self._ws = await self._session.ws_connect(ws_url, headers=headers)
            self._connected = True
            self._recv_task = asyncio.create_task(self._recv_loop())
            logger.info(
                "Realtime STT WebSocket connected (language=%s)",
                self.language_code or "auto",
            )
        except Exception as e:
            logger.error("Realtime STT WebSocket connection failed: %s", e)
            await self._cleanup()
            raise

    async def send_audio(self, pcm16le: bytes) -> None:
        """Send a chunk of PCM 16-bit LE audio at 16 kHz."""
        if not self._connected or self._ws is None:
            return
        payload = {
            "message_type": "input_audio_chunk",
            "audio_base_64": base64.b64encode(pcm16le).decode("ascii"),
            "commit": False,
            "sample_rate": 16000,
        }
        try:
            await self._ws.send_str(json.dumps(payload))
        except Exception as e:
            self._connected = False
            logger.warning("Realtime STT send failed: %s", e)

    async def _recv_loop(self) -> None:
        """Receive loop for WebSocket messages."""
        if self._ws is None:
            return
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        msg_type = data.get("message_type", "")
                        if msg_type == "session_started":
                            logger.info("Realtime STT session started payload: %s", msg.data[:300])
                        elif msg_type == "partial_transcript":
                            text = _extract_transcript_text(data)
                            if text and self.on_partial:
                                await self.on_partial.put(text)
                            elif self.on_partial:
                                logger.debug(
                                    "Realtime STT partial_transcript missing text: %s",
                                    msg.data[:300],
                                )
                        elif msg_type in (
                            "committed_transcript",
                            "committed_transcript_with_timestamps",
                        ):
                            text = _extract_transcript_text(data)
                            if text and self.on_committed:
                                await self.on_committed.put(text)
                            elif self.on_committed:
                                logger.debug(
                                    "Realtime STT committed transcript missing text: %s",
                                    msg.data[:300],
                                )
                        elif msg_type and "error" in msg_type.lower():
                            logger.warning("Realtime STT error: %s", msg.data)
                        elif msg_type:
                            logger.debug(
                                "Realtime STT ignored event %s: %s", msg_type, msg.data[:300]
                            )
                    except json.JSONDecodeError:
                        logger.debug(
                            "Realtime STT received non-JSON text frame: %r", msg.data[:200]
                        )
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    logger.warning("Realtime STT websocket closed: type=%s", msg.type.name)
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.warning("Realtime STT recv loop error: %s", e)
        finally:
            self._connected = False

    async def close(self) -> None:
        """Close the WebSocket connection."""
        self._connected = False
        if self._recv_task:
            self._recv_task.cancel()
            try:
                await self._recv_task
            except asyncio.CancelledError:
                pass
        await self._cleanup()
        logger.info("Realtime STT WebSocket closed")

    async def _cleanup(self) -> None:
        if self._ws and not self._ws.closed:
            await self._ws.close()
        if self._session and not self._session.closed:
            await self._session.close()
        self._ws = None
        self._session = None
