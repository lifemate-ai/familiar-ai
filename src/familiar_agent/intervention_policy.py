"""Intervention Policy — neighbor-core Layer D.

Decides whether the agent should speak, observe more, or stay silent.
Prevents over-intervention (annoyance) while ensuring timely care.

Works alongside concern_engine.py and desires.py to gate all autonomous output.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_PATH = Path.home() / ".familiar_ai" / "intervention_policy.json"

# Cooldown: minimum seconds between autonomous interventions
_MIN_INTERVENTION_GAP = 120.0  # 2 minutes
# Maximum interventions per hour
_MAX_INTERVENTIONS_PER_HOUR = 10
# Silence threshold: if uncertainty > this, prefer observation over intervention
_UNCERTAINTY_SILENCE_THRESHOLD = 0.7
# Night hours (reduce intervention frequency)
_NIGHT_HOURS = range(0, 7)


@dataclass
class InterventionDecision:
    """Result of the intervention policy evaluation."""

    action: str  # "intervene" | "observe" | "silence" | "escalate"
    rationale: str
    confidence: float = 0.5


class InterventionPolicy:
    """Gates autonomous agent interventions to prevent annoyance.

    Tracks intervention history and enforces cooldowns, rate limits,
    and uncertainty-based silence.
    """

    def __init__(self, state_path: Path | None = None):
        self._state_path = state_path or _DEFAULT_PATH
        self._state = self._load()

    def _load(self) -> dict:
        default = {
            "intervention_timestamps": [],  # list of float timestamps
            "total_interventions": 0,
            "silenced_count": 0,  # times we chose to stay quiet
        }
        try:
            if self._state_path.exists():
                return {**default, **json.loads(self._state_path.read_text())}
        except Exception as e:
            logger.warning("Could not load intervention policy state: %s", e)
        return default

    def _save(self) -> None:
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(json.dumps(self._state, indent=2))
        except Exception as e:
            logger.warning("Could not save intervention policy state: %s", e)

    def _prune_old_timestamps(self) -> None:
        """Remove timestamps older than 1 hour."""
        cutoff = time.time() - 3600
        self._state["intervention_timestamps"] = [
            ts for ts in self._state["intervention_timestamps"] if ts > cutoff
        ]

    def _recent_count(self) -> int:
        """Count interventions in the last hour."""
        self._prune_old_timestamps()
        return len(self._state["intervention_timestamps"])

    def _seconds_since_last(self) -> float:
        """Seconds since last intervention, or inf if none."""
        timestamps = self._state["intervention_timestamps"]
        if not timestamps:
            return float("inf")
        return time.time() - max(timestamps)

    def evaluate(
        self,
        *,
        urgency: float = 0.5,
        uncertainty: float = 0.3,
        hour: int | None = None,
        companion_present: bool = True,
    ) -> InterventionDecision:
        """Decide whether to intervene, observe, or stay silent.

        Args:
            urgency: How urgent the intervention is (0-1).
            uncertainty: How uncertain we are about the situation (0-1).
            hour: Current hour (0-23). If None, uses current time.
            companion_present: Whether the companion is actively engaged.
        """
        if hour is None:
            import datetime

            hour = datetime.datetime.now().hour

        # High uncertainty → observe more
        if uncertainty > _UNCERTAINTY_SILENCE_THRESHOLD and urgency < 0.8:
            return InterventionDecision(
                action="observe",
                rationale="High uncertainty; gathering more information first",
                confidence=0.6,
            )

        # Cooldown check
        gap = self._seconds_since_last()
        if gap < _MIN_INTERVENTION_GAP and urgency < 0.7:
            self._state["silenced_count"] = self._state.get("silenced_count", 0) + 1
            self._save()
            return InterventionDecision(
                action="silence",
                rationale=f"Cooldown: {gap:.0f}s since last intervention (<{_MIN_INTERVENTION_GAP}s)",
                confidence=0.8,
            )

        # Rate limit check
        recent = self._recent_count()
        if recent >= _MAX_INTERVENTIONS_PER_HOUR and urgency < 0.8:
            self._state["silenced_count"] = self._state.get("silenced_count", 0) + 1
            self._save()
            return InterventionDecision(
                action="silence",
                rationale=f"Rate limit: {recent} interventions in last hour",
                confidence=0.7,
            )

        # Night suppression
        if hour in _NIGHT_HOURS and urgency < 0.6:
            return InterventionDecision(
                action="silence",
                rationale="Night hours; suppressing non-urgent intervention",
                confidence=0.6,
            )

        # Companion not present → lower threshold for silence
        if not companion_present and urgency < 0.5:
            return InterventionDecision(
                action="silence",
                rationale="Companion not present; deferring",
                confidence=0.5,
            )

        # OK to intervene
        return InterventionDecision(
            action="intervene",
            rationale="Intervention approved",
            confidence=min(1.0, urgency),
        )

    def record_intervention(self) -> None:
        """Record that an intervention was made."""
        self._state["intervention_timestamps"].append(time.time())
        self._state["total_interventions"] = self._state.get("total_interventions", 0) + 1
        self._prune_old_timestamps()
        self._save()

    @property
    def total_interventions(self) -> int:
        return self._state.get("total_interventions", 0)

    @property
    def silenced_count(self) -> int:
        return self._state.get("silenced_count", 0)

    @property
    def annoyance_ratio(self) -> float:
        """Ratio of interventions to silenced decisions (lower is less annoying)."""
        total = self.total_interventions + self.silenced_count
        if total == 0:
            return 0.0
        return self.total_interventions / total
