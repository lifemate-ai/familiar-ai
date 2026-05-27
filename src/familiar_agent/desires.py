"""Desire system - autonomous motivations for the embodied agent."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from ._i18n import _t

if TYPE_CHECKING:
    from .workspace import Coalition

logger = logging.getLogger(__name__)

DEFAULT_DESIRES = {
    "look_around": 0.1,
    "explore": 0.1,
    "greet_companion": 0.0,
    "rest": 0.0,
    "worry_companion": 0.0,  # grows only via detect_worry_signal(), not over time
    "share_memory": 0.0,  # spontaneous "remember when..." sharing; fires every ~3 min idle
    "curiosity": 0.0,
    "attachment": 0.0,
    "care": 0.0,
    "reflect": 0.0,
    "consolidate": 0.0,
    "repair": 0.0,
    "play": 0.0,
    "self_protect": 0.0,
}

# How fast each desire grows per second of inactivity
GROWTH_RATES = {
    "look_around": 0.005,  # reaches 0.6 after ~2 min (was 40sec — too eager, caused spam)
    "explore": 0.008,  # reaches 0.6 after ~75 sec — explore should fire more often
    "greet_companion": 0.002,  # slow build; fires after ~5 min of silence
    "rest": 0.002,  # baseline; night modulation (×1.8) makes it grow meaningfully only at night
    "share_memory": 0.003,  # reaches 0.6 after ~3.3 min idle; evening ×1.4 makes it ~2.4 min
    "curiosity": 0.0025,
    "attachment": 0.0015,
    "care": 0.0015,
    "reflect": 0.0010,
    "consolidate": 0.0010,
    "repair": 0.0,
    "play": 0.0012,
    "self_protect": 0.0,
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


@dataclass(slots=True)
class DriveSpec:
    name: str
    growth_rate_per_second: float
    prompt_text: str
    tags: tuple[str, ...] = ()
    min_interval_seconds: int = 0


class DesireSystem:
    """Manages autonomous desires that drive self-initiated behavior."""

    def __init__(
        self,
        state_path: Path | None = None,
        companion_name: str | None = None,
        drive_config_path: Path | None = None,
    ):
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
        self._drive_config_path = drive_config_path
        self._last_fired: dict[str, float] = {}
        self._schedule_multiplier = 1.0
        self._social_permission = 1.0
        self._energy_budget = 1.0
        self._unfinished_business_bonus = 0.0
        self._context_affordances: dict[str, float] = {}
        self.curiosity_target: str | None = None  # What the agent wants to investigate next
        self._load()
        self._drive_specs = self._build_default_drive_specs()
        self._drive_specs.update(self._load_external_drive_specs())
        for name in self._drive_specs:
            self._desires.setdefault(name, DEFAULT_DESIRES.get(name, 0.0))

    def _build_default_drive_specs(self) -> dict[str, DriveSpec]:
        return {
            "look_around": DriveSpec(
                "look_around",
                GROWTH_RATES["look_around"],
                _t("desire_prompt_look_around"),
                ("legacy", "explore"),
                20,
            ),
            "explore": DriveSpec(
                "explore",
                GROWTH_RATES["explore"],
                _t("desire_prompt_explore"),
                ("legacy", "explore"),
                20,
            ),
            "greet_companion": DriveSpec(
                "greet_companion",
                GROWTH_RATES["greet_companion"],
                _t("desire_prompt_greet_companion", companion=self._companion_name),
                ("legacy", "social"),
                60,
            ),
            "rest": DriveSpec(
                "rest", GROWTH_RATES["rest"], _t("desire_prompt_rest"), ("legacy", "rest"), 60
            ),
            "worry_companion": DriveSpec(
                "worry_companion",
                0.0,
                _t("desire_prompt_worry_companion", companion=self._companion_name),
                ("legacy", "care"),
                60,
            ),
            "share_memory": DriveSpec(
                "share_memory",
                GROWTH_RATES["share_memory"],
                _t("desire_prompt_share_memory", companion=self._companion_name),
                ("legacy", "reflect"),
                90,
            ),
            "curiosity": DriveSpec(
                "curiosity",
                GROWTH_RATES["curiosity"],
                "Internal impulse: investigate what feels unclear or newly interesting.",
                ("curiosity",),
                45,
            ),
            "attachment": DriveSpec(
                "attachment",
                GROWTH_RATES["attachment"],
                f"Internal impulse: stay connected to {self._companion_name} without becoming clingy.",
                ("social",),
                60,
            ),
            "care": DriveSpec(
                "care",
                GROWTH_RATES["care"],
                f"Internal impulse: offer grounded care to {self._companion_name} if it fits the moment.",
                ("social", "care"),
                60,
            ),
            "reflect": DriveSpec(
                "reflect",
                GROWTH_RATES["reflect"],
                "Internal impulse: pause and integrate what just happened before rushing onward.",
                ("reflect",),
                90,
            ),
            "consolidate": DriveSpec(
                "consolidate",
                GROWTH_RATES["consolidate"],
                "Internal impulse: consolidate related memories and unfinished threads.",
                ("memory",),
                120,
            ),
            "repair": DriveSpec(
                "repair",
                0.0,
                "Internal impulse: repair relational strain before trying to solve anything else.",
                ("social", "repair"),
                45,
            ),
            "play": DriveSpec(
                "play",
                GROWTH_RATES["play"],
                "Internal impulse: keep some lightness and play where it is welcome.",
                ("play",),
                45,
            ),
            "self_protect": DriveSpec(
                "self_protect",
                0.0,
                "Internal impulse: reduce exposure when repeated failure or overload keeps building.",
                ("protect",),
                30,
            ),
        }

    def _load_external_drive_specs(self) -> dict[str, DriveSpec]:
        path = self._drive_config_path
        if path is None:
            env = os.environ.get("FAMILIAR_AI_DESIRES_CONFIG", "").strip()
            if env:
                path = Path(env).expanduser()
        if path is None or not path.exists():
            return {}

        specs: dict[str, DriveSpec] = {}
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                parts = [part.strip() for part in stripped.split("|")]
                if len(parts) != 5:
                    continue
                name, growth_rate, prompt_text, tags, min_interval = parts
                specs[name] = DriveSpec(
                    name=name,
                    growth_rate_per_second=float(growth_rate),
                    prompt_text=prompt_text,
                    tags=tuple(tag.strip() for tag in tags.split(",") if tag.strip()),
                    min_interval_seconds=int(min_interval),
                )
        except Exception as e:
            logger.warning("Could not load external desires config: %s", e)
            return {}
        return specs

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

        Night  (22–6):  rest ×1.8, explore ×0.4, look_around ×0.4, share_memory ×0.3
        Morning (6–10): greet_companion ×1.3, explore ×1.2
        Day   (10–18):  all default (×1.0)
        Evening(18–22): share_memory ×1.4 (nostalgic hour)
        """
        if 22 <= hour or hour < 6:  # night
            return {
                "rest": 1.8,
                "explore": 0.4,
                "look_around": 0.4,
                "greet_companion": 1.0,
                "worry_companion": 1.0,
                "share_memory": 0.3,  # late night: quiet, not the time for reminiscing
            }
        if 6 <= hour < 10:  # morning
            return {
                "rest": 1.0,
                "explore": 1.2,
                "look_around": 1.0,
                "greet_companion": 1.3,
                "worry_companion": 1.0,
                "share_memory": 1.0,
            }
        if 18 <= hour < 22:  # evening — nostalgic hour
            return {
                "share_memory": 1.4,
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

        for name, spec in self._drive_specs.items():
            rate = spec.growth_rate_per_second
            current = self._desires.get(name, 0.0)
            effective_rate = rate * modulation.get(name, 1.0) * self._schedule_multiplier
            if name in _rest_suppressed:
                effective_rate *= rest_factor * self._energy_budget
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
            self._last_fired[desire_name] = time.time()
            self._save()

    def level(self, desire_name: str) -> float:
        """Return the current level of a desire (0.0–1.0)."""
        return self._desires.get(desire_name, 0.0)

    def boost(self, desire_name: str, amount: float = 0.2) -> None:
        """Boost a desire (e.g., dopamine response to novelty)."""
        current = self._desires.get(desire_name, 0.0)
        self._desires[desire_name] = min(1.0, current + amount)
        self._save()

    def update_context(
        self,
        *,
        schedule_multiplier: float = 1.0,
        social_permission: float = 1.0,
        energy_budget: float = 1.0,
        unfinished_business_bonus: float = 0.0,
        context_affordances: dict[str, float] | None = None,
    ) -> None:
        self._schedule_multiplier = max(0.0, float(schedule_multiplier))
        self._social_permission = max(0.0, min(1.0, float(social_permission)))
        self._energy_budget = max(0.0, min(1.0, float(energy_budget)))
        self._unfinished_business_bonus = max(0.0, min(1.0, float(unfinished_business_bonus)))
        self._context_affordances = {
            str(k): max(0.0, min(1.5, float(v))) for k, v in (context_affordances or {}).items()
        }

    def _effective_score(self, name: str, level: float) -> float:
        affordance = self._context_affordances.get(name, 1.0)
        permission = (
            self._social_permission
            if {"social", "care", "repair"}
            & set(self._drive_specs.get(name, DriveSpec(name, 0.0, "")).tags)
            else 1.0
        )
        energy = self._energy_budget if name in {"explore", "look_around", "play"} else 1.0
        interval = self._drive_specs.get(name)
        if interval is not None:
            last = self._last_fired.get(name)
            if last is not None and interval.min_interval_seconds > 0:
                if time.time() - last < interval.min_interval_seconds:
                    return 0.0
        bonus = (
            self._unfinished_business_bonus
            if name in {"repair", "consolidate", "reflect", "self_protect"}
            else 0.0
        )
        return min(1.5, level * affordance * permission * energy + bonus)

    def get_dominant(self) -> tuple[str, float] | None:
        """Return the strongest desire if it exceeds the trigger threshold."""
        self.tick()
        candidates = []
        for name, level in self._desires.items():
            score = self._effective_score(name, level)
            if score >= TRIGGER_THRESHOLD:
                candidates.append((name, score))
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
        spec = self._drive_specs.get(name)
        return spec.prompt_text if spec is not None else None

    def drive_vector(self) -> dict[str, float]:
        self.tick()
        return dict(self._desires)

    def as_coalition(self) -> Coalition | None:
        """Return a workspace Coalition from the dominant desire, if any."""
        from .workspace import Coalition

        result = self.get_dominant()
        if result is None:
            return None
        name, level = result
        prompt = self.dominant_as_prompt() or name
        urgency_map = {
            "worry_companion": 0.9,
            "repair": 0.9,
            "self_protect": 0.8,
            "care": 0.7,
            "greet_companion": 0.7,
            "attachment": 0.6,
            "curiosity": 0.5,
            "look_around": 0.4,
            "explore": 0.4,
            "share_memory": 0.3,
            "reflect": 0.3,
            "consolidate": 0.3,
            "play": 0.3,
            "rest": 0.1,
        }
        return Coalition(
            source="desire",
            summary=f"{name} ({level:.2f})",
            activation=level,
            urgency=urgency_map.get(name, 0.3),
            novelty=0.0,
            context_block=f"[inner-voice] {prompt}",
        )
