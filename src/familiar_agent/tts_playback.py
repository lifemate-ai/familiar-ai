"""Sequential, non-blocking audio playback queue for TTS.

``TTSTool.say()`` opens the ElevenLabs *streaming* endpoint, awaits the first
audio chunk and hands the rest of the body to this queue instead of awaiting
download and local/go2rtc playback — a conversational turn no longer stalls
for the 5–7 s a full synthesis download takes, nor the 15–20 s an utterance
takes to play. One asyncio worker plays items strictly one after another, so
consecutive ``say()`` calls never overlap.

Three pieces live here:

- :class:`PlaybackQueue` — the single-worker FIFO. File items (``enqueue``)
  and streaming items (``enqueue_stream``) share the same ordering.
- :class:`AudioChunkRelay` — a background pump that drains an HTTP body into
  an asyncio queue at network speed, so the connection is released as soon as
  the download finishes regardless of how fast playback consumes it.
- :class:`PcmSink` — a thread-backed ``sounddevice`` writer that plays raw
  16-bit PCM chunks as they arrive (odd byte boundaries are carried over).

The per-item ``play`` coroutine owns the playback-boundary side effects (the
voice guard's ``on_tts_start`` / ``on_tts_end`` for STT echo suppression);
``on_done`` is a cleanup hook (temp-file unlink, relay cancel) that runs after
playback — and also when an item is dropped by ``stop()``, so nothing leaks.
"""

from __future__ import annotations

import asyncio
import logging
import queue
import threading
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

PlayFn = Callable[[str], Awaitable[list[str]]]
"""Plays ``path`` and returns the sinks it played through (empty on failure)."""

StreamPlayFn = Callable[[AsyncIterator[bytes]], Awaitable[list[str]]]
"""Consumes an audio chunk iterator and returns the sinks it played through."""

DoneFn = Callable[[list[str]], None]

CloseFn = Callable[[], Awaitable[None]]


@dataclass
class _Item:
    label: str
    run: Callable[[], Awaitable[list[str]]]
    on_done: DoneFn | None
    future: asyncio.Future[list[str]]
    played: list[str] = field(default_factory=list)


class PlaybackQueue:
    """Single-worker FIFO that plays queued audio (files or streams) sequentially."""

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

        async def run() -> list[str]:
            return await play_fn(path)

        return self._put(path, run, on_done)

    def enqueue_stream(
        self,
        chunks: AsyncIterator[bytes],
        *,
        play: StreamPlayFn,
        on_done: DoneFn | None = None,
        label: str = "<stream>",
    ) -> asyncio.Future[list[str]]:
        """Queue a chunk iterator; ``play`` consumes it when its turn comes."""

        async def run() -> list[str]:
            return await play(chunks)

        return self._put(label, run, on_done)

    def _put(
        self, label: str, run: Callable[[], Awaitable[list[str]]], on_done: DoneFn | None
    ) -> asyncio.Future[list[str]]:
        loop = asyncio.get_running_loop()
        item = _Item(label=label, run=run, on_done=on_done, future=loop.create_future())
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
                item.played = list(await item.run())
            except asyncio.CancelledError:
                self._current = None
                self._finish(item, cancelled=True)
                raise
            except Exception as exc:  # noqa: BLE001
                logger.warning("TTS playback failed for %s: %s", item.label, exc)
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


# ---------------------------------------------------------------------------
# AudioChunkRelay: drain an HTTP body in the background, hand chunks out lazily
# ---------------------------------------------------------------------------


class AudioChunkRelay:
    """Async iterator over audio chunks fed by a background pump task.

    The pump reads ``source`` (e.g. ``resp.content.iter_chunked(n)``) as fast
    as the network delivers it and calls ``close`` (release the HTTP response
    and session) once the body is exhausted — so the connection never waits on
    playback. ``head`` is a chunk already read by the caller (the first chunk
    ``say()`` awaited before returning) and is yielded first.
    """

    def __init__(
        self,
        source: AsyncIterator[bytes],
        *,
        head: bytes | None = None,
        close: CloseFn | None = None,
    ) -> None:
        self._source = source
        self._close = close
        self._chunks: asyncio.Queue[bytes | None] = asyncio.Queue()
        if head:
            self._chunks.put_nowait(head)
        self._task: asyncio.Task[None] | None = None
        self.error: BaseException | None = None

    def start(self) -> None:
        """Start draining ``source`` on the running loop (idempotent)."""
        if self._task is None:
            self._task = asyncio.get_running_loop().create_task(self._pump())

    async def _pump(self) -> None:
        try:
            async for chunk in self._source:
                if chunk:
                    self._chunks.put_nowait(bytes(chunk))
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            self.error = exc
            logger.warning("TTS stream download failed mid-way: %s", exc)
        finally:
            self._chunks.put_nowait(None)
            if self._close is not None:
                try:
                    await self._close()
                except Exception as exc:  # noqa: BLE001
                    logger.debug("TTS stream close failed: %s", exc)

    def __aiter__(self) -> AudioChunkRelay:
        return self

    async def __anext__(self) -> bytes:
        chunk = await self._chunks.get()
        if chunk is None:
            self._chunks.put_nowait(None)  # stay terminal for any later iteration
            raise StopAsyncIteration
        return chunk

    def cancel(self) -> None:
        """Abort the download (the pump's ``finally`` still releases the HTTP session)."""
        if self._task is not None and not self._task.done():
            self._task.cancel()

    async def aclose(self) -> None:
        """Cancel the pump if still running and wait for it to release resources."""
        self.cancel()
        if self._task is not None:
            try:
                await self._task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass


# ---------------------------------------------------------------------------
# PcmSink: thread-backed sounddevice writer for raw 16-bit mono PCM
# ---------------------------------------------------------------------------

_SENTINEL: bytes | None = None


class PcmSink:
    """Plays raw 16-bit PCM chunks as they arrive through ``sounddevice``.

    ``sounddevice.RawOutputStream.write`` blocks until the device buffer has
    room, so writes run on one dedicated thread fed by a ``queue.Queue`` —
    the event loop only enqueues. Chunks may split a 16-bit frame; the odd
    remainder is carried into the next write. ``bytes_played`` counts input
    bytes handed to the device so a caller can resume from the unplayed
    remainder if the device fails mid-stream.

    Raises ``ImportError`` when ``sounddevice`` is missing and whatever the
    stream constructor raises when no output device can be opened.
    """

    def __init__(
        self,
        *,
        sample_rate: int = 16000,
        channels: int = 1,
        stream_factory: Callable[[], Any] | None = None,
    ) -> None:
        if stream_factory is None:
            import sounddevice as sd

            def stream_factory() -> Any:
                return sd.RawOutputStream(samplerate=sample_rate, channels=channels, dtype="int16")

        self._stream = stream_factory()
        self._stream.start()
        self._frame_bytes = 2 * channels
        self._queue: queue.Queue[bytes | None] = queue.Queue()
        self._remainder = b""
        self.bytes_played = 0
        self.error: BaseException | None = None
        self._thread = threading.Thread(target=self._run, name="tts-pcm-sink", daemon=True)
        self._thread.start()

    def write(self, chunk: bytes) -> None:
        """Hand a chunk to the writer thread (non-blocking; dropped after an error)."""
        if self.error is None and chunk:
            self._queue.put(chunk)

    def _run(self) -> None:
        try:
            while True:
                chunk = self._queue.get()
                if chunk is None:
                    break
                data = self._remainder + chunk
                usable = len(data) - len(data) % self._frame_bytes
                self._remainder = data[usable:]
                if usable:
                    self._stream.write(data[:usable])
                    self.bytes_played += usable
        except Exception as exc:  # noqa: BLE001
            self.error = exc
            logger.warning("sounddevice stream write failed: %s", exc)
        finally:
            for method in ("stop", "close"):
                try:
                    getattr(self._stream, method)()
                except Exception:  # noqa: BLE001
                    pass

    async def close(self) -> bool:
        """Flush, wait for the writer thread to drain, and report success."""
        self._queue.put(_SENTINEL)
        await asyncio.to_thread(self._thread.join)
        return self.error is None

    def abort(self) -> None:
        """Stop feeding without waiting (used on cancellation)."""
        self.error = self.error or asyncio.CancelledError()
        self._queue.put(_SENTINEL)
