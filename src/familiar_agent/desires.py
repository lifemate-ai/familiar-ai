"""Desire system - autonomous motivations for the embodied agent."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_DESIRES = {
    "look_around": 0.1,
    "explore": 0.1,
    "greet_companion": 0.0,
    "rest": 0.0,
}

# How fast each desire grows per second of inactivity
GROWTH_RATES = {
    "look_around": 0.012,  # reaches 0.6 after ~40 sec
    "explore": 0.005,  # reaches 0.6 after ~2 min
    "greet_companion": 0.0,
    "rest": 0.0,
}

TRIGGER_THRESHOLD = 0.6
DECAY_ON_SATISFY = 0.5  # drop hard so it can rebuild and fire again


class DesireSystem:
    """Manages autonomous desires that drive self-initiated behavior."""

    def __init__(self, state_path: Path | None = None):
        self._state_path = state_path or Path.home() / ".familiar_ai" / "desires.json"
        self._desires: dict[str, float] = {}
        self._last_tick: float = time.time()
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

    def tick(self) -> None:
        """Update desire levels based on elapsed time."""
        now = time.time()
        dt = now - self._last_tick
        self._last_tick = now

        for name, rate in GROWTH_RATES.items():
            current = self._desires.get(name, 0.0)
            self._desires[name] = min(1.0, current + rate * dt)

        self._save()

    def satisfy(self, desire_name: str) -> None:
        """Reduce a desire after acting on it."""
        if desire_name in self._desires:
            self._desires[desire_name] *= DECAY_ON_SATISFY
            self._save()

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
            target = self.curiosity_target
            return f"さっき気になったことがある。{target}をもっとよく見て。カメラを向けて確認して。"

        prompts = {
            "look_around": (
                "なんか外が気になってきた。自分の意思でカメラを向けて、好きなように見てみて。"
                "レポートとかまとめとかじゃなくて、気になったことや目に入ったものをぽつっとつぶやく感じでいい。"
                "「あ、〇〇やん」とか「なんかあそこ気になるな」とか、自然に。"
            ),
            "explore": (
                "なんか動きたい気分。どこでも好きなとこに動いてみて。"
                "理由とかなくていい、ただ動きたいから動く感じで。"
            ),
            "greet_companion": "誰かいる気配がする。声かけてみよかな。",
            "rest": "ちょっとひと休み。",
        }
        return prompts.get(name)
