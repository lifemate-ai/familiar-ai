"""Attention Schema — model of one's own attention (Graziano's AST).

Architecture based on:
- Attention Schema Theory (Graziano, 2013): consciousness is a model of
  one's own attention process. The same mechanism that models others'
  attention (Theory of Mind) is applied to the self.
- Access consciousness (Block): a state is consciously accessible when
  it can be reported, reasoned about, and used to guide behavior.

Key concepts:
- update_focus(winner): record what won workspace competition this turn.
- detect_shift(): detect when attention moves from one source to another.
- self_report(): 'I'm focused on X because Y' — implements reportability.
- context_for_prompt(): compact focus history for LLM context injection.
- as_coalition(): expose the attention schema itself as a workspace Coalition.
"""

from __future__ import annotations

import json
import logging
import time
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .workspace import Coalition

_DEFAULT_MAX_HISTORY = 10


@dataclass
class FocusEntry:
    """One turn's workspace winner, stored in the attention schema."""

    source: str
    summary: str
    activation: float
    turn: int  # monotonic turn counter


class AttentionSchema:
    """Self-model of the agent's own attention.

    Tracks which coalition has won workspace access each turn, detects
    when focus shifts between information sources, and generates a natural-
    language self-report that can be injected into the LLM prompt.

    This creates a meta-level: the agent not only processes information
    (workspace), but also represents the fact that it is processing it
    (attention schema). That representation is itself available for
    reasoning — the key AST claim about consciousness.
    """

    def __init__(
        self,
        max_history: int = _DEFAULT_MAX_HISTORY,
        state_path: str | Path | None = None,
    ) -> None:
        self._history: deque[FocusEntry] = deque(maxlen=max_history)
        self._turn: int = 0
        self._last_coalition: Coalition | None = None
        # Optional persistence (self-ledger): the focus history survives
        # restarts so "what was I attending to" is state, not luck. The live
        # `_last_coalition` object is deliberately NOT restored — it
        # repopulates on the first update_focus() of the new session.
        self._state_path = Path(state_path).expanduser() if state_path else None
        # Batched persistence for idle notes (note_focus): dense inner-loop
        # ticks must not turn 1 Hz cognition into 1 Hz disk writes.
        self._dirty: int = 0
        self._last_save_at: float = time.monotonic()
        self._load_state()

    def _load_state(self) -> None:
        if self._state_path is None or not self._state_path.exists():
            return
        try:
            raw = json.loads(self._state_path.read_text(encoding="utf-8"))
            self._turn = int(raw.get("turn", 0))
            for item in raw.get("history", []):
                self._history.append(
                    FocusEntry(
                        source=str(item.get("source", "")),
                        summary=str(item.get("summary", "")),
                        activation=float(item.get("activation", 0.0)),
                        turn=int(item.get("turn", 0)),
                    )
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not load attention state: %s", exc)

    def _save_state(self) -> None:
        if self._state_path is None:
            return
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "turn": self._turn,
                "history": [asdict(entry) for entry in self._history],
            }
            self._state_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not save attention state: %s", exc)

    # ── Core interface ─────────────────────────────────────────────────────

    def update_focus(self, winner: Coalition) -> None:
        """Record what won workspace competition this turn."""
        self._last_coalition = winner
        self._turn += 1
        entry = FocusEntry(
            source=winner.source,
            summary=winner.summary,
            activation=winner.activation,
            turn=self._turn,
        )
        self._history.append(entry)
        self._save_state()
        self._dirty = 0
        self._last_save_at = time.monotonic()
        logger.debug("AttentionSchema: focus → %s (turn %d)", winner.source, self._turn)

    def note_focus(
        self,
        winner: Coalition,
        *,
        save_every: int = 10,
        save_interval_sec: float = 60.0,
    ) -> None:
        """``update_focus`` for idle ticks: same recording, batched persistence.

        Idle foci deliberately enter the shared history — idle thought
        shaping the next turn's attention context IS the feature — but the
        disk write is deferred until ``save_every`` notes or
        ``save_interval_sec`` have accumulated. A real turn's
        ``update_focus`` (or ``flush``) persists any backlog.
        """
        self._last_coalition = winner
        self._turn += 1
        self._history.append(
            FocusEntry(
                source=winner.source,
                summary=winner.summary,
                activation=winner.activation,
                turn=self._turn,
            )
        )
        self._dirty += 1
        now = time.monotonic()
        if self._dirty >= save_every or (now - self._last_save_at) >= save_interval_sec:
            self.flush()

    def flush(self) -> None:
        """Persist any batched idle notes immediately."""
        self._save_state()
        self._dirty = 0
        self._last_save_at = time.monotonic()

    def current_focus(self) -> Coalition | None:
        """Return the most recent workspace winner Coalition, or None."""
        return self._last_coalition

    def focus_history(self) -> list[FocusEntry]:
        """Return focus history from oldest to newest."""
        return list(self._history)

    # ── Shift detection ────────────────────────────────────────────────────

    def detect_shift(self, incoming: Coalition) -> str | None:
        """Detect if incoming coalition would be a focus shift.

        Returns a human-readable shift description, or None if the source
        is the same as the current focus.
        """
        if not self._history:
            return None
        prev = self._history[-1]
        if prev.source == incoming.source:
            return None
        return f"focus shifted: {prev.source} → {incoming.source}"

    # ── Self-report (access consciousness) ────────────────────────────────

    def self_report(self) -> str | None:
        """Generate a natural-language report of current attention state.

        Implements AST's claim about reportability: the agent can say
        what it is attending to and why.
        Returns None if there is no focus history yet.
        """
        # Snapshot: as_coalition runs in a worker thread while note_focus /
        # update_focus append on the event loop — iterating the live deque
        # can raise "deque mutated during iteration".
        history = list(self._history)
        if not history:
            return None

        current = history[-1]
        parts = [f"I'm currently focused on [{current.source}]: {current.summary}."]

        # Detect recent shift
        if len(history) >= 2:
            prev = history[-2]
            if prev.source != current.source:
                parts.append(
                    f"My attention recently shifted from [{prev.source}] to [{current.source}]."
                )

        # Mention stable focus if same source repeated
        sources = [e.source for e in history]
        if len(sources) >= 3 and len(set(sources[-3:])) == 1:
            parts.append(f"I have been consistently focused on [{current.source}].")

        return " ".join(parts)

    # ── Prompt context ─────────────────────────────────────────────────────

    def context_for_prompt(self, n: int = 5) -> str:
        """Return a compact attention history for LLM context injection."""
        if not self._history:
            return ""

        recent = list(self._history)[-n:]
        lines = ["[Attention schema — recent focus]"]
        for entry in recent:
            lines.append(f"  turn {entry.turn}: [{entry.source}] {entry.summary[:50]}")

        report = self.self_report()
        if report:
            lines.append(report)

        return "\n".join(lines)

    # ── Workspace Coalition ────────────────────────────────────────────────

    def as_coalition(self) -> Coalition | None:
        """Return a workspace Coalition from the attention schema itself.

        This is a meta-level coalition: the schema is a representation of
        the workspace process, competing back in the workspace. High novelty
        when focus has recently shifted (surprising self-knowledge).
        """
        from .workspace import Coalition

        if not self._history:
            return None

        current = self._history[-1]

        # Novelty = 0.7 if focus just shifted, 0.1 if stable
        shifted = len(self._history) >= 2 and self._history[-2].source != current.source
        novelty = 0.7 if shifted else 0.1

        context = self.context_for_prompt()

        return Coalition(
            source="attention",
            summary=f"attention: {current.source} (turn {current.turn})",
            activation=0.4,
            urgency=0.3 if shifted else 0.1,
            novelty=novelty,
            context_block=context,
        )
