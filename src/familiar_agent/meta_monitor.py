"""MetaMonitor — Phase 5: Higher-Order Theory (HOT) layer.

Records metacognitive state per ReAct step (what won workspace, what action was taken,
confidence), detects inconsistencies with self-narrative, and produces session summaries
for diary / self-model updates.

All operations are synchronous and lightweight (no LLM calls).
"""

from __future__ import annotations

from collections import Counter, deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .self_narrative import SelfNarrative
    from .workspace import Coalition


class MetaMonitor:
    """Higher-Order Theory layer: metacognitive monitoring per ReAct step.

    Lightweight structured logging of each step — no LLM calls.  Results feed
    into self_narrative diary entries and workspace competition via as_coalition().
    """

    def __init__(self, window: int = 20) -> None:
        self._window = window
        self._steps: deque[dict] = deque(maxlen=window)

    # ── Public API ────────────────────────────────────────────────────────────

    def record_step(
        self,
        workspace_winner: Coalition,
        action: str,
        confidence: float,
    ) -> None:
        """Record one ReAct step's metacognitive state."""
        self._steps.append(
            {
                "source": workspace_winner.source,
                "summary": workspace_winner.summary[:80],
                "action": action,
                "confidence": max(0.0, min(1.0, confidence)),
            }
        )

    def step_count(self) -> int:
        return len(self._steps)

    def recent_steps(self) -> list[dict]:
        return list(self._steps)

    def detect_inconsistency(self, self_narrative: SelfNarrative) -> str | None:
        """Return a description of inconsistency if current behaviour diverges from narrative.

        Returns None when no clear inconsistency is found.
        """
        if not self._steps:
            return None

        # Simple heuristic: if the narrative description and the dominant workspace
        # source have obvious semantic mismatch, flag it.
        # This is intentionally lightweight — not an LLM call.
        try:
            description = self_narrative.context_for_prompt()
        except Exception:
            return None

        if not description:
            return None

        dominant = self._dominant_source()
        if dominant is None:
            return None

        # Only flag if very confident about dominant source
        source_count = Counter(s["source"] for s in self._steps)
        if source_count[dominant] < len(self._steps) * 0.7:
            return None  # not dominant enough to flag

        # We avoid false positives by not flagging unless both conditions hold:
        # (a) narrative mentions a contrasting state keyword AND
        # (b) steps are dominated by the opposite
        contrasts = {
            "rest": {"desire", "scene"},  # resting but driven by desires/scene
        }
        for keyword, opposite_sources in contrasts.items():
            if keyword in description.lower() and dominant in opposite_sources:
                return (
                    f"Narrative mentions '{keyword}' but attention is dominated by '{dominant}' "
                    f"({source_count[dominant]}/{len(self._steps)} steps)."
                )

        return None

    def summarize_session(self) -> str:
        """Return a compact metacognitive summary of this session for diary injection."""
        if not self._steps:
            return "No steps recorded this session."

        source_count = Counter(s["source"] for s in self._steps)
        dominant = source_count.most_common(1)[0]
        avg_conf = sum(s["confidence"] for s in self._steps) / len(self._steps)

        parts = [
            f"Session: {len(self._steps)} steps.",
            f"Dominant attention: {dominant[0]} ({dominant[1]}/{len(self._steps)}).",
            f"Mean confidence: {avg_conf:.2f}.",
        ]

        # List top-3 sources
        top = source_count.most_common(3)
        top_str = ", ".join(f"{src}×{cnt}" for src, cnt in top)
        parts.append(f"Sources: {top_str}.")

        return " ".join(parts)

    def as_coalition(self) -> Coalition | None:
        """Expose meta-monitor state as a workspace Coalition (background priority)."""
        if not self._steps:
            return None

        from .workspace import Coalition

        dominant = self._dominant_source() or "mixed"
        summary = f"Meta: {len(self._steps)} steps, dominant={dominant}"
        context_block = f"[meta] {self.summarize_session()}"

        # Background process: low activation so it rarely wins workspace
        avg_conf = sum(s["confidence"] for s in self._steps) / len(self._steps)
        activation = avg_conf * 0.3  # scale down so meta doesn't dominate

        return Coalition(
            source="meta",
            summary=summary,
            activation=activation,
            urgency=0.1,
            novelty=0.1,
            context_block=context_block,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _dominant_source(self) -> str | None:
        if not self._steps:
            return None
        return Counter(s["source"] for s in self._steps).most_common(1)[0][0]
