"""Persistent latent self state updated by workspace broadcasts."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .workspace import Coalition

logger = logging.getLogger(__name__)

_DEFAULT_PATH = Path.home() / ".familiar_ai" / "self_state.json"

_BASELINES: dict[str, float] = {
    "arousal": 0.35,
    "fatigue": 0.2,
    "social_pull": 0.35,
    "sensor_confidence": 0.7,
    "unresolved_tension": 0.2,
    "focus_stability": 0.5,
}


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


class SelfState:
    """Small persistent latent state for embodied continuity."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or _DEFAULT_PATH
        self._values = dict(_BASELINES)
        self._load()

    def _load(self) -> None:
        try:
            if not self._path.exists():
                return
            raw = json.loads(self._path.read_text())
            if not isinstance(raw, dict):
                return
            for key, baseline in _BASELINES.items():
                value = raw.get(key, baseline)
                if isinstance(value, (int, float)):
                    self._values[key] = _clamp(float(value))
        except Exception as exc:
            logger.warning("Could not load self state: %s", exc)

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(self._values, indent=2))
        except Exception as exc:
            logger.warning("Could not save self state: %s", exc)

    def snapshot(self) -> dict[str, float]:
        return dict(self._values)

    def _settle_toward_baseline(self) -> None:
        for key, baseline in _BASELINES.items():
            current = self._values[key]
            self._values[key] = _clamp(current + (baseline - current) * 0.08)

    def _nudge(self, key: str, delta: float) -> None:
        self._values[key] = _clamp(self._values[key] + delta)

    def apply_broadcast(self, winner: "Coalition") -> None:
        """Update latent state from the latest workspace winner."""
        self._settle_toward_baseline()

        activation = _clamp(float(winner.activation))
        urgency = _clamp(float(winner.urgency))
        novelty = _clamp(float(winner.novelty))

        self._nudge("fatigue", 0.01 * activation + 0.01 * urgency)

        match winner.source:
            case "prediction":
                self._nudge("arousal", 0.12 + 0.18 * novelty)
                self._nudge("unresolved_tension", 0.08 + 0.18 * novelty)
                self._nudge("sensor_confidence", -(0.05 + 0.14 * novelty))
                self._nudge("focus_stability", -(0.03 + 0.06 * novelty))
            case "scene":
                self._nudge("arousal", 0.04 + 0.12 * urgency)
                self._nudge("sensor_confidence", 0.03 + 0.05 * activation)
                self._nudge("focus_stability", 0.02)
            case "desire":
                self._nudge("arousal", 0.03 + 0.08 * activation)
                self._nudge("unresolved_tension", 0.05 + 0.1 * urgency)
                self._nudge("focus_stability", -(0.04 + 0.05 * urgency))
            case "memory":
                self._nudge("social_pull", 0.04 + 0.08 * activation)
                self._nudge("focus_stability", 0.03 + 0.04 * activation)
                self._nudge("unresolved_tension", -0.04)
            case "narrative":
                self._nudge("social_pull", 0.03 + 0.05 * activation)
                self._nudge("focus_stability", 0.05 + 0.05 * activation)
                self._nudge("unresolved_tension", -0.05)
            case "attention":
                self._nudge("focus_stability", 0.04 + 0.08 * activation)
                self._nudge("unresolved_tension", -0.02)
            case "meta":
                self._nudge("focus_stability", 0.02 + 0.03 * activation)
            case "default_mode":
                self._nudge("arousal", -0.06)
                self._nudge("focus_stability", 0.03)
                self._nudge("unresolved_tension", -0.04)
            case _:
                self._nudge("arousal", 0.02 * activation)
                self._nudge("focus_stability", 0.01 * activation)

        self._save()

    async def on_broadcast(self, winner: "Coalition") -> None:
        self.apply_broadcast(winner)
