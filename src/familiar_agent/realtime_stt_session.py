"""Realtime STT session manager — shared between REPL and TUI.

Manages the lifecycle of microphone capture → ElevenLabs Realtime STT →
asyncio.Queue, with filler filtering and deduplication.

Usage (both modes)::

    session = create_realtime_stt_session()
    if session:
        session.on_partial = lambda t: ...   # display hook
        session.on_committed = lambda t: ...  # display hook
        await session.start(loop, input_queue)
        ...
        await session.stop()
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tools.realtime_stt import RealtimeSttClient
    from .tools.mic import MicCapture

logger = logging.getLogger(__name__)

# ── Filler / short-utterance filter ──────────────────────────────────
_FILLER_WORDS = frozenset("えー ええと えっと あの その うーん んー ま はい うん ん".split())
_DEDUPE_WINDOW_SECS = 3.0
_RECONNECT_POLL_SECS = 1.0
_RECONNECT_BACKOFF_SECS = 2.0
_BRACKETED_EVENT_RE = re.compile(r"[（(［\[]([^（）()\[\]［］]{1,40})[）)］\]]")


def _dedupe_now() -> float:
    """Return the clock used for realtime transcript deduplication."""
    return time.monotonic()


def _is_only_punct_or_symbol(s: str) -> bool:
    return all(c in "。、！？…・「」『』（）()!?,." or not c.isalnum() for c in s)


def _looks_like_audio_event(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    events = _BRACKETED_EVENT_RE.findall(stripped)
    if not events:
        return False
    remainder = _BRACKETED_EVENT_RE.sub("", stripped)
    return not remainder.strip()


def should_skip_stt(text: str) -> bool:
    """Return True if the transcript should be silently discarded."""
    text = text.strip()
    if len(text) < 2:
        return True
    if _looks_like_audio_event(text):
        return True
    if _is_only_punct_or_symbol(text):
        return True
    if text in _FILLER_WORDS:
        return True
    return False


def _normalize_for_dedupe(text: str) -> str:
    """Normalize STT text for stable duplicate detection."""
    normalized = text.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip(" 　。、！？…・「」『』（）()!?,.\"'")


class RealtimeSttSession:
    """Manages microphone capture → ElevenLabs Realtime STT → output queue.

    Attributes:
        on_partial:   Optional callback ``(text) -> None`` for partial transcripts.
        on_committed: Optional callback ``(text) -> None`` for committed transcripts
                      (called *before* the text is placed on the queue).
    """

    def __init__(self, api_key: str, language_code: str = "ja") -> None:
        self._api_key = api_key
        self._language_code = language_code.strip()
        self._stt_client: RealtimeSttClient | None = None
        self._mic_capture: MicCapture | None = None
        self._relay_task: asyncio.Task | None = None
        self._partial_task: asyncio.Task | None = None
        self._monitor_task: asyncio.Task | None = None
        self._committed_queue: asyncio.Queue[str | None] | None = None
        self._incoming_committed: asyncio.Queue[str] = asyncio.Queue()
        self._incoming_partial: asyncio.Queue[str] = asyncio.Queue()
        self._connect_lock = asyncio.Lock()
        self._restart_lock = asyncio.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stopping = False

        # Deduplication state
        self._last_normalized_text = ""
        self._last_time = 0.0

        # Display callbacks (set by caller before start())
        self.on_partial: Callable[[str], None] | None = None
        self.on_committed: Callable[[str], None] | None = None
        self.on_restart: Callable[[str], None] | None = None

    @property
    def active(self) -> bool:
        """True while the session is running."""
        return self._mic_capture is not None or self._monitor_task is not None

    @property
    def connected(self) -> bool:
        """True while the websocket transport is currently live."""
        return bool(self._stt_client and self._stt_client.connected)

    async def start(
        self,
        loop: asyncio.AbstractEventLoop,
        committed_queue: asyncio.Queue[str | None],
    ) -> None:
        """Connect the STT WebSocket and start microphone capture."""
        from .tools.mic import MicCapture  # noqa: PLC0415

        if self.active:
            logger.debug("Realtime STT session already active; start() is a no-op")
            return

        self._loop = loop
        self._committed_queue = committed_queue
        self._stopping = False
        self._last_normalized_text = ""
        self._last_time = 0.0
        self._incoming_committed = asyncio.Queue()
        self._incoming_partial = asyncio.Queue()

        await self._connect_client()

        self._relay_task = asyncio.create_task(self._committed_relay())
        self._partial_task = asyncio.create_task(self._partial_relay())
        self._monitor_task = asyncio.create_task(self._monitor_connection())

        self._mic_capture = MicCapture(on_audio=self._send_audio)
        self._mic_capture.start(loop)
        logger.info("Realtime STT session started")

    async def stop(self) -> None:
        """Stop microphone capture and close the STT WebSocket."""
        self._stopping = True
        if self._mic_capture:
            self._mic_capture.stop()
            self._mic_capture = None
        for task in (self._relay_task, self._partial_task, self._monitor_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._relay_task = None
        self._partial_task = None
        self._monitor_task = None
        if self._stt_client:
            await self._stt_client.close()
            self._stt_client = None
        logger.info("Realtime STT session stopped")

    async def restart(self, reason: str = "manual") -> bool:
        """Reconnect the realtime STT session using the stored loop/queue."""
        if self._loop is None or self._committed_queue is None:
            logger.debug("Realtime STT restart skipped before initial start (%s)", reason)
            return False

        async with self._restart_lock:
            logger.warning("Restarting realtime STT session (%s)", reason)
            await self.stop()
            await self.start(self._loop, self._committed_queue)
            logger.info("Realtime STT session restarted (%s)", reason)
            return True

    # ── internal relay tasks ─────────────────────────────────────────

    async def _connect_client(self) -> None:
        from .tools.realtime_stt import RealtimeSttClient  # noqa: PLC0415

        async with self._connect_lock:
            if self._stopping:
                return

            old_client = self._stt_client
            self._stt_client = None
            if old_client is not None:
                await old_client.close()

            client = RealtimeSttClient(self._api_key, self._language_code)
            client.on_committed = self._incoming_committed
            client.on_partial = self._incoming_partial
            await client.connect()
            self._stt_client = client
            logger.info("Realtime STT transport connected")

    async def _ensure_connected(self) -> bool:
        client = self._stt_client
        if client is not None and client.connected:
            return False
        await self._connect_client()
        return True

    async def _monitor_connection(self) -> None:
        """Reconnect when the realtime websocket drops mid-session."""
        while not self._stopping:
            await asyncio.sleep(_RECONNECT_POLL_SECS)
            try:
                reconnected = await self._ensure_connected()
                if reconnected:
                    logger.warning("Realtime STT disconnected; reconnected transport")
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("Realtime STT reconnect failed: %s", exc)
                await asyncio.sleep(_RECONNECT_BACKOFF_SECS)

    async def _send_audio(self, pcm16le: bytes) -> None:
        client = self._stt_client
        if client is None:
            return
        await client.send_audio(pcm16le)

    async def _committed_relay(self) -> None:
        assert self._committed_queue is not None
        while True:
            text = await self._incoming_committed.get()
            if should_skip_stt(text):
                logger.debug("Realtime STT dropped transcript after filtering: %r", text)
                continue
            normalized = _normalize_for_dedupe(text)
            if not normalized:
                logger.debug("Realtime STT dropped blank normalized transcript: %r", text)
                continue
            now = _dedupe_now()
            if (
                normalized == self._last_normalized_text
                and now - self._last_time < _DEDUPE_WINDOW_SECS
            ):
                logger.debug("Dropped duplicate realtime STT transcript: %s", text)
                continue
            self._last_normalized_text = normalized
            self._last_time = now
            if self.on_committed:
                self.on_committed(text)
            await self._committed_queue.put(text)

    async def _partial_relay(self) -> None:
        while True:
            text = await self._incoming_partial.get()
            if _looks_like_audio_event(text):
                logger.debug("Realtime STT dropped audio-event partial: %r", text)
                continue
            if self.on_partial:
                self.on_partial(text)


def create_realtime_stt_session() -> RealtimeSttSession | None:
    """Create a session if ``REALTIME_STT=true`` and the API key is available.

    Returns ``None`` when realtime STT is not configured.
    """
    enabled = os.environ.get("REALTIME_STT", "").lower() in ("1", "true", "yes")
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    language_code = os.environ.get("STT_LANGUAGE", "ja").strip()

    if not enabled:
        return None
    if not api_key:
        logger.warning("REALTIME_STT=true but ELEVENLABS_API_KEY is not set")
        return None

    return RealtimeSttSession(api_key, language_code=language_code)


RealtimeSttController = RealtimeSttSession


def create_realtime_stt_controller() -> RealtimeSttController | None:
    """Compatibility shim for the GUI bootstrap path.

    PR2 only needs a restart-capable controller surface for GUI startup and
    diagnostics. The richer voice-guard behavior lands in PR3.
    """
    return create_realtime_stt_session()
