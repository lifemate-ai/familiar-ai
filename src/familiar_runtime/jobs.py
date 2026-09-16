"""Background job management for runtime post-turn work."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Coroutine
from typing import Any

logger = logging.getLogger(__name__)


class BackgroundJobManager:
    """Track fire-and-forget jobs and drain them during shutdown."""

    def __init__(self) -> None:
        self._tasks: set[asyncio.Task[None]] = set()

    @property
    def tasks(self) -> set[asyncio.Task[None]]:
        return self._tasks

    def spawn(self, coro: Coroutine[Any, Any, None], *, name: str) -> None:
        task = asyncio.create_task(coro, name=name)
        self._tasks.add(task)

        def _done(done_task: asyncio.Task[None]) -> None:
            self._tasks.discard(done_task)
            try:
                exc = done_task.exception()
            except asyncio.CancelledError:
                return
            if exc is not None:
                logger.warning("Background task %s failed: %s", name, exc)

        task.add_done_callback(_done)

    async def drain(self, timeout: float) -> None:
        pending = {task for task in self._tasks if not task.done()}
        if not pending:
            return
        done, still_pending = await asyncio.wait(pending, timeout=timeout)
        for task in done:
            try:
                task.result()
            except asyncio.CancelledError:
                pass
            except Exception as exc:  # noqa: BLE001
                logger.warning("Background task failed during drain: %s", exc)
        if still_pending:
            for task in still_pending:
                task.cancel()
            await asyncio.gather(*still_pending, return_exceptions=True)
