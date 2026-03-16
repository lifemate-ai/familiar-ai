"""Global Workspace — GWT/GNWT-inspired integration layer.

Architecture based on:
- Global Workspace Theory (Baars): specialized processors compete for a shared
  workspace; the winner broadcasts its content to all other processors.
- Global Neuronal Workspace Theory (Dehaene/Changeux): adds an ignition
  threshold — only coalitions above the threshold reach "consciousness."
- Prediction error modulation (Friston): high prediction error lowers the
  ignition threshold, making the system more sensitive to surprising inputs.

Key concepts:
- Coalition: a candidate for workspace access from one specialized processor.
- compete(): score all coalitions, apply ignition threshold, return winner.
- broadcast(): format the winner for LLM injection + peripheral summary.
- notify_listeners(): call all registered on_broadcast callbacks (feedback loop).
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Awaitable, Callable

logger = logging.getLogger(__name__)

# Minimum ignition threshold floor (prevents runaway suppression)
_MIN_THRESHOLD = 0.05

# How much each unit of prediction error lowers the threshold
_ERROR_SENSITIVITY = 0.15


@dataclass
class Coalition:
    """A candidate for workspace access from one specialized processor.

    Attributes:
        source: Name of the originating processor (e.g. "desire", "scene").
        summary: Short natural-language description of the content.
        activation: Base strength from the source processor (0.0–1.0).
        urgency: Time-sensitivity (e.g. "person appeared" = high urgency).
        novelty: How unexpected this content is (connects to prediction error).
        context_block: Formatted text for LLM prompt injection if this wins.
    """

    source: str
    summary: str
    activation: float
    urgency: float
    novelty: float
    context_block: str

    def score(self) -> float:
        """Composite score used in workspace competition.

        score = activation × (0.4×urgency + 0.3×novelty + 0.3)

        The constant 0.3 ensures coalitions with zero urgency/novelty can
        still compete if activation is high enough.
        """
        return self.activation * (0.4 * self.urgency + 0.3 * self.novelty + 0.3)


BroadcastListener = Callable[["Coalition"], Awaitable[None]]


class GlobalWorkspace:
    """Central bottleneck where specialized processors compete for broadcast.

    Usage:
        ws = GlobalWorkspace()
        winner = ws.compete(coalitions)
        if winner:
            prompt_context = ws.broadcast(winner, others)
            await ws.notify_listeners(winner)
        else:
            # Nothing ignited — activate default mode
            ...
    """

    def __init__(self, ignition_threshold: float = 0.4) -> None:
        self._base_threshold = ignition_threshold
        self._prediction_error: float = 0.0
        self._listeners: list[BroadcastListener] = []

    # ── Ignition threshold ─────────────────────────────────────────────────

    def apply_prediction_error(self, error: float) -> None:
        """Register a prediction error signal.

        High error lowers the ignition threshold (system becomes more
        sensitive — more things reach "consciousness").
        """
        self._prediction_error = max(0.0, error)

    def effective_threshold(self) -> float:
        """Current ignition threshold after prediction error modulation.

        threshold = base - sensitivity × tanh(error)

        tanh keeps the adjustment bounded. At error=0, threshold = base.
        At error=∞, threshold approaches (base - sensitivity).
        """
        adjustment = _ERROR_SENSITIVITY * math.tanh(self._prediction_error)
        return max(_MIN_THRESHOLD, self._base_threshold - adjustment)

    # ── Competition ───────────────────────────────────────────────────────

    def compete(self, coalitions: list[Coalition]) -> Coalition | None:
        """Score all coalitions and return the winner above ignition threshold.

        Returns None if no coalition reaches the effective threshold (the
        system enters a resting / default-mode state).
        """
        threshold = self.effective_threshold()
        candidates = [(c, c.score()) for c in coalitions if c.score() >= threshold]
        if not candidates:
            return None
        winner, best_score = max(candidates, key=lambda x: x[1])
        logger.debug(
            "Workspace winner: %s (score=%.3f, threshold=%.3f)",
            winner.source,
            best_score,
            threshold,
        )
        return winner

    # ── Broadcast ─────────────────────────────────────────────────────────

    def broadcast(self, winner: Coalition, others: list[Coalition]) -> str:
        """Format the winning coalition as a prompt context block.

        The result contains:
        1. The winner's full context_block (primary workspace content).
        2. A compact peripheral-awareness summary of non-winning coalitions.
        """
        parts: list[str] = [winner.context_block]
        peripheral = self.peripheral_summary(others)
        if peripheral:
            parts.append(peripheral)
        return "\n".join(parts)

    def peripheral_summary(self, others: list[Coalition]) -> str:
        """One-line summary per non-winning coalition (peripheral awareness).

        These are the coalitions that didn't win workspace access this cycle.
        They are represented with minimal detail — just enough to stay "in
        the background" without consuming workspace bandwidth.
        """
        if not others:
            return ""
        lines = [f"[bg:{c.source}] {c.summary}" for c in others if c.summary]
        return "\n".join(lines)

    # ── Listeners (feedback loop) ─────────────────────────────────────────

    def register_broadcast_listener(self, listener: BroadcastListener) -> None:
        """Register a callback to be called after each broadcast.

        This implements the GWT feedback loop: when the workspace broadcasts,
        ALL specialized processors are notified so they can update their state.
        """
        self._listeners.append(listener)

    async def notify_listeners(self, winner: Coalition) -> None:
        """Notify all registered listeners of the broadcast winner."""
        import asyncio

        if not self._listeners:
            return
        await asyncio.gather(*(listener(winner) for listener in self._listeners))
