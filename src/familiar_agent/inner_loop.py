"""Background driver for the inner loop — the workspace cycling between turns.

Phase 2 of the ego/identity → GWT roadmap. Today the global workspace competes
only when a turn fires; the inner loop runs a cheap workspace cycle during idle
so the agent has a sub-verbal inner life — a "train of thought" with continuity
that occasionally crystallizes a thought worth keeping. It produces no
user-visible output and (on cheap ticks) costs zero LLM/embedding calls.

This module owns only cadence and lifecycle (shaped exactly like
``MemoryJobWorker``). The actual per-tick work lives on ``EmbodiedAgent`` as
``_inner_loop_tick`` because it needs the agent's private coalition sources;
the driver just calls a ``tick`` callable, so it stays import-free of the agent
and trivially unit-testable.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from familiar_neighbor.mind.workspace import Coalition

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class InnerLoopConfig:
    interval_sec: float = 20.0
    # Run the full (embedding-backed) cycle once every N ticks; the rest are
    # the zero-cost sync-only cheap cycle.
    full_cycle_every: int = 5


@dataclass(slots=True)
class InnerThought:
    """One crystallized idle thought — the winning coalition, compressed."""

    summary: str
    source: str
    ts: float
    score: float


@dataclass
class TrainOfThought:
    """Recurrence: the last ignited winner re-competes next tick, decayed.

    Gives idle thought momentum — one focus biases toward related follow-ups
    instead of every cycle restarting from a blank slate — while decaying so a
    stronger coalition can always displace it. A run of the same source winning
    increments ``streak`` (used to decide a thought is worth persisting).
    """

    last: "Coalition | None" = None
    streak: int = 0
    decay: float = 0.7
    floor: float = 0.1

    def observe(self, winner: "Coalition") -> None:
        if self.last is not None and winner.source == self.last.source:
            self.streak += 1
        else:
            self.streak = 1
        self.last = winner

    def as_coalition(self) -> "Coalition | None":
        """Return the decayed re-injection for the next competition, or None."""
        if self.last is None:
            return None
        from familiar_neighbor.mind.workspace import Coalition

        activation = self.last.activation * self.decay
        if activation < self.floor:
            self.reset()
            return None
        return Coalition(
            source="train_of_thought",
            summary=self.last.summary,
            activation=activation,
            urgency=self.last.urgency * self.decay,
            novelty=self.last.novelty * self.decay,
            context_block=self.last.context_block,
        )

    def reset(self) -> None:
        self.last = None
        self.streak = 0


@dataclass(slots=True)
class CompeteResult:
    """Structured outcome of one workspace competition."""

    winner: "Coalition | None"
    others: list = field(default_factory=list)
    coalitions: list = field(default_factory=list)


class InnerLoop:
    """Cadence + lifecycle for the idle workspace cycle.

    Delegates the per-tick work to a ``tick`` coroutine (= ``agent
    ._inner_loop_tick``). Owns no agent reference, so it is import-free of the
    agent and easy to test with a fake tick.
    """

    def __init__(
        self,
        tick: Callable[[], Awaitable[None]],
        config: InnerLoopConfig | None = None,
    ) -> None:
        self._tick = tick
        self._config = config or InnerLoopConfig()
        self._task: asyncio.Task[None] | None = None

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self) -> None:
        if self.is_running:
            return
        self._task = asyncio.create_task(self._run_loop(), name="inner-loop")

    async def stop(self) -> None:
        if not self._task:
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task
        self._task = None

    async def run_once(self) -> None:
        """Run a single tick. Errors are logged, never raised into the loop."""
        try:
            await self._tick()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.warning("Inner-loop tick failed: %s", exc)

    async def _run_loop(self) -> None:
        while True:
            await self.run_once()
            await asyncio.sleep(max(self._config.interval_sec, 1.0))
