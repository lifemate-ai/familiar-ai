"""Desire system - autonomous motivations for the embodied agent."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

from ._i18n import _t

logger = logging.getLogger(__name__)

DEFAULT_DESIRES = {
    "look_around": 0.1,
    "explore": 0.1,
    "greet_companion": 0.0,
    "rest": 0.0,
    "worry_companion": 0.0,  # grows only via detect_worry_signal(), not over time
}

# How fast each desire grows per second of inactivity
GROWTH_RATES = {
    "look_around": 0.005,  # reaches 0.6 after ~2 min (was 40sec — too eager, caused spam)
    "explore": 0.008,  # reaches 0.6 after ~75 sec — explore should fire more often
    "greet_companion": 0.002,  # slow build; fires after ~5 min of silence
    "rest": 0.002,  # baseline; night modulation (×1.8) makes it grow meaningfully only at night
    # worry_companion intentionally omitted — only grows via boost()
}

# ── Worry signal detection ─────────────────────────────────────────────────────

# Strong signals: sleep deprivation, illness → boost 0.4
_STRONG_WORRY_PATTERNS: list[str] = [
    "寝不足",
    "眠れない",
    "眠れなくて",
    "眠れなかった",
    "熱が",
    "熱出",
    "風邪",
    "体調悪",
    "具合悪",
    "疲れ果て",
    "限界",
    "倒れ",
    "slept only",
    "no sleep",
    "can't sleep",
    "haven't slept",
]

# Weak signals: general fatigue, stress → boost 0.2
_WEAK_WORRY_PATTERNS: list[str] = [
    "疲れた",
    "しんどい",
    "しんどくて",
    "つらい",
    "大変",
    "残業",
    "tired",
    "exhausted",
    "stressed",
]


def detect_worry_signal(text: str) -> float:
    """Analyse conversation text and return a worry boost amount (0.0–1.0).

    Uses deterministic keyword matching so the result is always testable.
    Strong signals (sleep deprivation, illness) return 0.4.
    Weak signals (general fatigue) return 0.2.
    Multiple matches accumulate, capped at 1.0.
    """
    if not text:
        return 0.0

    lower = text.lower()
    total = 0.0

    for pattern in _STRONG_WORRY_PATTERNS:
        if pattern.lower() in lower:
            total += 0.4

    for pattern in _WEAK_WORRY_PATTERNS:
        if pattern.lower() in lower:
            total += 0.2

    return min(1.0, total)


TRIGGER_THRESHOLD = 0.6
DECAY_ON_SATISFY = 0.5  # drop hard so it can rebuild and fire again


class DesireSystem:
    """Manages autonomous desires that drive self-initiated behavior."""

    def __init__(self, state_path: Path | None = None, companion_name: str | None = None):
        self._state_path = state_path or Path.home() / ".familiar_ai" / "desires.json"
        self._desires: dict[str, float] = {}
        self._last_tick: float = time.time()
        default_name = _t("default_companion_name")
        resolved_name = (
            (companion_name or "").strip()
            or os.environ.get("COMPANION_NAME", "").strip()
            or default_name
        )
        self._companion_name = resolved_name or default_name
        self.curiosity_target: str | None = None  # What the agent wants to investigate next
        self._load()

    def _load(self) -> None:
        try:
            if self._state_path.exists():
                self._desires = json.loads(self._state_path.read_text())
            else:
                self._desires = dict(DEFAULT_DESIRES)
        except Exception:
            self._desires = dict(DEFAULT_DESIRES)

    def _save(self) -> None:
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(json.dumps(self._desires, indent=2))
        except Exception as e:
            logger.warning("Could not save desires: %s", e)

    # ------------------------------------------------------------------
    # Phase 3-1: circadian modulation
    # ------------------------------------------------------------------

    @staticmethod
    def _time_modulation(hour: int) -> dict[str, float]:
        """Return per-desire growth-rate multipliers based on time of day.

        Night  (22–6):  rest ×1.8, explore ×0.4, look_around ×0.4
        Morning (6–10): greet_companion ×1.3, explore ×1.2
        Day   (10–18):  all default (×1.0)
        Evening(18–22): no special modulation (worry sensitivity rises naturally via boost)
        """
        if 22 <= hour or hour < 6:  # night
            return {
                "rest": 1.8,
                "explore": 0.4,
                "look_around": 0.4,
                "greet_companion": 1.0,
                "worry_companion": 1.0,
            }
        if 6 <= hour < 10:  # morning
            return {
                "rest": 1.0,
                "explore": 1.2,
                "look_around": 1.0,
                "greet_companion": 1.3,
                "worry_companion": 1.0,
            }
        return {}  # default: no modulation (all ×1.0)

    # ------------------------------------------------------------------
    # Phase 3-2: drive suppression
    # ------------------------------------------------------------------

    def _rest_suppression_factor(self) -> float:
        """When rest is high, return a < 1.0 factor to suppress active drives.

        rest ≥ 0.5 → suppression factor 0.5 (half-speed growth for explore/look_around)
        rest < 0.5 → no suppression (factor 1.0)
        """
        rest = self._desires.get("rest", 0.0)
        if rest >= 0.5:
            return 0.5
        return 1.0

    # ------------------------------------------------------------------

    def tick(self) -> None:
        """Update desire levels based on elapsed time.

        Applies Phase 3-1 circadian modulation and Phase 3-2 drive suppression.
        """
        now = time.time()
        dt = now - self._last_tick
        self._last_tick = now

        hour = datetime.now().hour
        modulation = self._time_modulation(hour)
        rest_factor = self._rest_suppression_factor()

        # Drives suppressed by rest level
        _rest_suppressed = {"explore", "look_around"}

        for name, rate in GROWTH_RATES.items():
            current = self._desires.get(name, 0.0)
            effective_rate = rate * modulation.get(name, 1.0)
            if name in _rest_suppressed:
                effective_rate *= rest_factor
            self._desires[name] = min(1.0, current + effective_rate * dt)

        self._save()

    def satisfy(self, desire_name: str) -> None:
        """Reduce a desire after acting on it using DECAY_ON_SATISFY multiplier.

        Phase 3-3: was a full reset to DEFAULT; now decays by DECAY_ON_SATISFY
        so the desire can rebuild naturally without immediately spiking again.
        """
        if desire_name in self._desires:
            current = self._desires[desire_name]
            self._desires[desire_name] = max(0.0, current * DECAY_ON_SATISFY)
            self._save()

    def level(self, desire_name: str) -> float:
        """Return the current level of a desire (0.0–1.0)."""
        return self._desires.get(desire_name, 0.0)

    def boost(self, desire_name: str, amount: float = 0.2) -> None:
        """Boost a desire (e.g., dopamine response to novelty)."""
        current = self._desires.get(desire_name, 0.0)
        self._desires[desire_name] = min(1.0, current + amount)
        self._save()

    def get_dominant(self) -> tuple[str, float] | None:
        """Return the strongest desire if it exceeds the trigger threshold."""
        self.tick()
        candidates = [
            (name, level) for name, level in self._desires.items() if level >= TRIGGER_THRESHOLD
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda x: x[1])

    def dominant_as_prompt(self) -> str | None:
        """Return a natural-language prompt for the dominant desire, if any."""
        result = self.get_dominant()
        if result is None:
            return None
        name, _ = result

        # If there's a curiosity target, use it for look_around/explore
        if name in ("look_around", "explore") and self.curiosity_target:
            return _t("desire_prompt_curiosity_target", target=self.curiosity_target)

        # These are INTERNAL IMPULSES — the agent acts on them autonomously.
        # Framed in first person so the model knows this is its own desire, not a user request.
        prompts = {
            "look_around": _t("desire_prompt_look_around"),
            "explore": _t("desire_prompt_explore"),
            "greet_companion": _t(
                "desire_prompt_greet_companion",
                companion=self._companion_name,
            ),
            "rest": _t("desire_prompt_rest"),
            "worry_companion": _t(
                "desire_prompt_worry_companion",
                companion=self._companion_name,
            ),
        }
        return prompts.get(name)
