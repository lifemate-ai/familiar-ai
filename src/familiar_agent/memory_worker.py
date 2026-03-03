"""Background worker for durable memory jobs."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from dataclasses import dataclass
from typing import Any

from .tools.memory import ObservationMemory

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MemoryWorkerConfig:
    poll_interval_sec: float = 0.5
    batch_size: int = 8
    retry_delay_sec: float = 10.0
    max_attempts: int = 3


class MemoryJobWorker:
    """Executes pending jobs from ObservationMemory.memory_jobs."""

    def __init__(self, memory: ObservationMemory, config: MemoryWorkerConfig | None = None) -> None:
        self._memory = memory
        self._config = config or MemoryWorkerConfig()
        self._task: asyncio.Task[None] | None = None

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self) -> None:
        """Start the worker loop if not already running."""
        if self.is_running:
            return
        self._task = asyncio.create_task(self._run_loop(), name="memory-job-worker")

    async def stop(self) -> None:
        """Stop the worker loop and wait for cancellation."""
        if not self._task:
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task
        self._task = None

    async def run_once(self) -> int:
        """Claim and process one batch of jobs. Returns processed job count."""
        jobs = await asyncio.to_thread(self._memory.claim_pending_jobs, self._config.batch_size)
        for job in jobs:
            job_id = str(job["job_id"])
            try:
                await self._process_job(job)
                await asyncio.to_thread(self._memory.mark_job_done, job_id)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                status = await asyncio.to_thread(
                    self._memory.mark_job_failed,
                    job_id,
                    str(e),
                    self._config.retry_delay_sec,
                    self._config.max_attempts,
                )
                logger.warning("Memory job failed (job_id=%s, status=%s): %s", job_id, status, e)
        return len(jobs)

    async def _run_loop(self) -> None:
        while True:
            processed = await self.run_once()
            sleep_s = 0.0 if processed > 0 else max(self._config.poll_interval_sec, 0.05)
            await asyncio.sleep(sleep_s)

    async def _process_job(self, job: dict[str, Any]) -> None:
        job_type = str(job.get("job_type", ""))
        event_id = str(job.get("event_id", ""))
        if not event_id:
            raise RuntimeError("memory job missing event_id")

        if job_type != "materialize_observation":
            raise RuntimeError(f"unsupported memory job_type: {job_type}")

        ok = await asyncio.to_thread(self._memory.materialize_event, event_id)
        if not ok:
            raise RuntimeError(f"failed to materialize event: {event_id}")
