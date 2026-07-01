"""Cortex-side client for familiard's wake socket.

A wake event only *accelerates* the idle poll: whichever UI loop receives one
runs exactly the same gate checks it would have run at its next 10-second
tick (reminder backoff, quiet hours, auto_desire, input precedence). The
daemon cannot know cortex-local state, so it never decides — it nudges.

Degrades to nothing: when the daemon is off, absent, or the platform has no
Unix sockets, ``wait()`` behaves like a plain timeout and the UI loops keep
their historical polling behavior byte-for-byte.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_SOCKET_PATH = Path.home() / ".familiar_ai" / "familiard.sock"
_RECONNECT_MIN_SEC = 5.0
_RECONNECT_MAX_SEC = 300.0


@dataclass(slots=True, frozen=True)
class WakeEvent:
    reason: str
    ts: float


class WakeListener:
    """Reads newline-delimited JSON wake events from the familiard socket.

    Lazily connects on first ``wait()``; reconnects with exponential backoff
    while the daemon is down. Safe to construct unconditionally — when
    ``enabled`` is False every call is a cheap no-op.
    """

    def __init__(
        self,
        socket_path: str | Path | None = None,
        *,
        enabled: bool | None = None,
    ) -> None:
        if enabled is None:
            enabled = os.environ.get("FAMILIAR_DAEMON", "").strip().lower() in (
                "1",
                "true",
                "yes",
                "on",
            )
        self._enabled = bool(enabled) and sys.platform != "win32"
        raw_path = socket_path or os.environ.get("FAMILIAR_DAEMON_SOCKET", "").strip() or None
        self._path = Path(raw_path).expanduser() if raw_path else _DEFAULT_SOCKET_PATH
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._next_connect_at = 0.0
        self._backoff = _RECONNECT_MIN_SEC

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def connected(self) -> bool:
        return self._reader is not None and not self._reader.at_eof()

    async def _try_connect(self) -> bool:
        if self.connected:
            return True
        now = time.monotonic()
        if now < self._next_connect_at:
            return False
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_unix_connection(str(self._path)), timeout=1.0
            )
            self._backoff = _RECONNECT_MIN_SEC
            logger.info("connected to familiard at %s", self._path)
            return True
        except (ConnectionError, FileNotFoundError, OSError, asyncio.TimeoutError):
            self._reader = None
            self._writer = None
            self._next_connect_at = now + self._backoff
            self._backoff = min(self._backoff * 2, _RECONNECT_MAX_SEC)
            return False

    async def wait(self, timeout: float) -> WakeEvent | None:
        """Wait up to ``timeout`` seconds for one wake event.

        Returns None on timeout, when disabled, or while the daemon is
        unreachable — indistinguishable from a plain idle-poll timeout,
        which is exactly the degradation contract.
        """
        if not self._enabled:
            await asyncio.sleep(timeout)
            return None
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            if not await self._try_connect():
                await asyncio.sleep(min(remaining, 1.0))
                continue
            assert self._reader is not None
            try:
                line = await asyncio.wait_for(self._reader.readline(), timeout=remaining)
            except asyncio.TimeoutError:
                return None
            except (ConnectionError, OSError):
                self._drop_connection()
                continue
            if not line:  # EOF — daemon went away
                self._drop_connection()
                continue
            try:
                payload = json.loads(line.decode("utf-8"))
            except Exception:  # noqa: BLE001
                continue
            if isinstance(payload, dict) and payload.get("type") == "wake":
                return WakeEvent(
                    reason=str(payload.get("reason", "unknown")),
                    ts=float(payload.get("ts", time.time())),
                )

    def _drop_connection(self) -> None:
        if self._writer is not None:
            with contextlib.suppress(Exception):
                self._writer.close()
        self._reader = None
        self._writer = None

    def close(self) -> None:
        self._drop_connection()


async def wait_input_or_wake(
    input_queue: asyncio.Queue,
    wake: WakeListener | None,
    timeout: float,
) -> tuple[str, Any]:
    """Wait for user input, a wake event, or the poll timeout — in that order.

    Returns ``(kind, item)`` with kind in {"input", "wake", "timeout"}.
    "input" carries the dequeued item verbatim — including a queue's None
    shutdown sentinel, which must stay distinguishable from a timeout. With
    no listener (or a disabled one) this is exactly
    ``wait_for(queue.get(), timeout)`` — the historical idle-poll behavior.
    """
    if wake is None or not wake.enabled:
        try:
            item = await asyncio.wait_for(input_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return "timeout", None
        return "input", item

    queue_task = asyncio.ensure_future(input_queue.get())
    wake_task = asyncio.ensure_future(wake.wait(timeout))
    try:
        done, _ = await asyncio.wait(
            {queue_task, wake_task},
            timeout=timeout,
            return_when=asyncio.FIRST_COMPLETED,
        )
        # Input wins whenever both raced to completion (idle precedence).
        if queue_task in done:
            return "input", queue_task.result()
        if wake_task in done and wake_task.result() is not None:
            return "wake", wake_task.result()
        return "timeout", None
    finally:
        for task in (queue_task, wake_task):
            if not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError, Exception):
                    await task
