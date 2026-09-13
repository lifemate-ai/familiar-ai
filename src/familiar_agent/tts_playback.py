"""Sequential, non-blocking audio playback queue for TTS.

``TTSTool.say()`` awaits synthesis (the HTTP call) inline but hands the
resulting file to this queue instead of awaiting local/go2rtc playback — a
conversational turn no longer stalls for the 15–20 s an utterance takes to
play. One asyncio worker plays items strictly one after another, so
consecutive ``say()`` calls never overlap.

The per-item ``play`` coroutine owns the playback-boundary side effects (the
voice guard's ``on_tts_start`` / ``on_tts_end`` for STT echo suppression);
``on_done`` is a cleanup hook (temp-file unlink) that runs after playback —
and also when an item is dropped by ``stop()``, so files never leak.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

PlayFn = Callable[[str], Awaitable[list[str]]]
"""Plays ``path`` and returns the sinks it played through (empty on failure)."""

DoneFn = Callable[[list[str]], None]


@dataclass
class _Item:
    path: str
    play: PlayFn
    on_done: DoneFn | None
    future: asyncio.Future[list[str]]
    played: list[str] = field(default_factory=list)


class PlaybackQueue:
    """Single-worker FIFO that plays queued audio files sequentially."""

    def __init__(self, play: PlayFn | None = None) -> None:
        self._default_play = play
        self._queue: asyncio.Queue[_Item] = asyncio.Queue()
        self._current: _Item | None = None
        self._worker: asyncio.Task[None] | None = None
        self._idle = asyncio.Event()
        self._idle.set()

    # ------------------------------------------------------------------ state

    @property
    def is_speaking(self) -> bool:
        """True while an item is playing or waiting to play."""
        return self._current is not None or not self._queue.empty()

    # ---------------------------------------------------------------- control

    def enqueue(
        self,
        path: str,
        on_done: DoneFn | None = None,
        *,
        play: PlayFn | None = None,
    ) -> asyncio.Future[list[str]]:
        """Queue ``path`` for playback; returns a future of the sinks used.

        Never blocks. The worker is started lazily on the running loop.
        """
        play_fn = play or self._default_play
        if play_fn is None:
            raise ValueError("PlaybackQueue.enqueue needs a play callable")
        loop = asyncio.get_running_loop()
        item = _Item(path=path, play=play_fn, on_done=on_done, future=loop.create_future())
        self._idle.clear()
        self._queue.put_nowait(item)
        self._ensure_worker()
        return item.future

    async def wait_idle(self, timeout: float | None = None) -> bool:
        """Wait until nothing is playing or pending. False on timeout."""
        if not self.is_speaking:
            return True
        try:
            await asyncio.wait_for(self._idle.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return False
        return True

    async def stop(self) -> None:
        """Cancel the current item and drop pending ones (cleanup hooks still run)."""
        worker = self._worker
        self._worker = None
        if worker is not None and not worker.done():
            worker.cancel()
            try:
                await worker
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        while not self._queue.empty():
            item = self._queue.get_nowait()
            self._finish(item, cancelled=True)
        self._current = None
        self._idle.set()

    # ----------------------------------------------------------------- worker

    def _ensure_worker(self) -> None:
        if self._worker is None or self._worker.done():
            self._worker = asyncio.get_running_loop().create_task(self._run())

    async def _run(self) -> None:
        while True:
            item = await self._queue.get()
            self._current = item
            try:
                item.played = list(await item.play(item.path))
            except asyncio.CancelledError:
                self._current = None
                self._finish(item, cancelled=True)
                raise
            except Exception as exc:  # noqa: BLE001
                logger.warning("TTS playback failed for %s: %s", item.path, exc)
            self._current = None
            self._finish(item, cancelled=False)
            if self._queue.empty():
                self._idle.set()

    @staticmethod
    def _finish(item: _Item, *, cancelled: bool) -> None:
        if item.on_done is not None:
            try:
                item.on_done(item.played)
            except Exception as exc:  # noqa: BLE001
                logger.debug("playback on_done hook failed: %s", exc)
        if item.future.done():
            return
        if cancelled:
            item.future.cancel()
        else:
            item.future.set_result(item.played)
