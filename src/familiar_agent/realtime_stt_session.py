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
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)

# ── Filler / short-utterance filter ──────────────────────────────────
_FILLER_WORDS = frozenset("えー ええと えっと あの その うーん んー ま はい うん ん".split())


def _is_only_punct_or_symbol(s: str) -> bool:
    return all(c in "。、！？…・「」『』（）()!?,." or not c.isalnum() for c in s)


def should_skip_stt(text: str) -> bool:
    """Return True if the transcript should be silently discarded."""
    text = text.strip()
    if len(text) < 2:
        return True
    if _is_only_punct_or_symbol(text):
        return True
    if text in _FILLER_WORDS:
        return True
    return False


class RealtimeSttSession:
    """Manages microphone capture → ElevenLabs Realtime STT → output queue.

    Attributes:
        on_partial:   Optional callback ``(text) -> None`` for partial transcripts.
        on_committed: Optional callback ``(text) -> None`` for committed transcripts
                      (called *before* the text is placed on the queue).
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._stt_client = None
        self._mic_capture = None
        self._relay_task: asyncio.Task | None = None
        self._partial_task: asyncio.Task | None = None
        self._committed_queue: asyncio.Queue[str] | None = None

        # Deduplication state
        self._last_text = ""
        self._last_time = 0.0

        # Display callbacks (set by caller before start())
        self.on_partial: Callable[[str], None] | None = None
        self.on_committed: Callable[[str], None] | None = None

    @property
    def active(self) -> bool:
        """True while the session is running."""
        return self._stt_client is not None

    async def start(
        self,
        loop: asyncio.AbstractEventLoop,
        committed_queue: asyncio.Queue[str],
    ) -> None:
        """Connect the STT WebSocket and start microphone capture."""
        from .tools.realtime_stt import RealtimeSttClient  # noqa: PLC0415
        from .tools.mic import MicCapture  # noqa: PLC0415

        self._committed_queue = committed_queue

        self._stt_client = RealtimeSttClient(self._api_key)
        self._stt_client.on_committed = asyncio.Queue()
        self._stt_client.on_partial = asyncio.Queue()
        await self._stt_client.connect()

        self._relay_task = asyncio.create_task(self._committed_relay())
        self._partial_task = asyncio.create_task(self._partial_relay())

        self._mic_capture = MicCapture(on_audio=self._stt_client.send_audio)
        self._mic_capture.start(loop)
        logger.info("Realtime STT session started")

    async def stop(self) -> None:
        """Stop microphone capture and close the STT WebSocket."""
        if self._mic_capture:
            self._mic_capture.stop()
            self._mic_capture = None
        for task in (self._relay_task, self._partial_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._relay_task = None
        self._partial_task = None
        if self._stt_client:
            await self._stt_client.close()
            self._stt_client = None
        logger.info("Realtime STT session stopped")

    # ── internal relay tasks ─────────────────────────────────────────

    async def _committed_relay(self) -> None:
        assert self._stt_client is not None
        assert self._committed_queue is not None
        while True:
            text = await self._stt_client.on_committed.get()
            if should_skip_stt(text):
                continue
            now = time.time()
            if text == self._last_text and now - self._last_time < 1.2:
                continue
            self._last_text = text
            self._last_time = now
            if self.on_committed:
                self.on_committed(text)
            await self._committed_queue.put(text)

    async def _partial_relay(self) -> None:
        assert self._stt_client is not None
        while True:
            text = await self._stt_client.on_partial.get()
            if self.on_partial:
                self.on_partial(text)


def create_realtime_stt_session() -> RealtimeSttSession | None:
    """Create a session if ``REALTIME_STT=true`` and the API key is available.

    Returns ``None`` when realtime STT is not configured.
    """
    enabled = os.environ.get("REALTIME_STT", "").lower() in ("1", "true", "yes")
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")

    if not enabled:
        return None
    if not api_key:
        logger.warning("REALTIME_STT=true but ELEVENLABS_API_KEY is not set")
        return None

    return RealtimeSttSession(api_key)
