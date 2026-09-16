"""Lightweight active concerns for autobiographical self continuity."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .prediction import PredictionSignal

_DEFAULT_PATH = Path.home() / ".familiar_ai" / "active_concerns.json"
_MAX_CONCERNS = 5
_DECAY = 0.94
_LEAK = 0.015
_MIN_INTENSITY = 0.12
_PROMPT_THRESHOLD = 0.38
_PROMPT_COOLDOWN_TURNS = 2


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass
class Concern:
    topic: str
    category: str
    intensity: float
    age_turns: int = 0
    last_activated_turn: int = 0
    last_expressed_turn: int = -999
    resolved: bool = False
    linked_episode: str = ""


class ConcernEngine:
    """Small persistent set of unresolved concerns with decay and cooldown."""

    def __init__(self, path: Path | None = None, max_concerns: int = _MAX_CONCERNS) -> None:
        self._path = path or _DEFAULT_PATH
        self._max_concerns = max(1, max_concerns)
        self._concerns: list[Concern] = []
        self._load()

    def _load(self) -> None:
        try:
            if not self._path.exists():
                return
            raw = json.loads(self._path.read_text())
            if not isinstance(raw, list):
                return
            concerns: list[Concern] = []
            for item in raw:
                if not isinstance(item, dict):
                    continue
                topic = str(item.get("topic", "")).strip()
                category = str(item.get("category", "general")).strip() or "general"
                if not topic:
                    continue
                concerns.append(
                    Concern(
                        topic=topic,
                        category=category,
                        intensity=_clamp01(float(item.get("intensity", 0.0))),
                        age_turns=max(0, int(item.get("age_turns", 0))),
                        last_activated_turn=max(0, int(item.get("last_activated_turn", 0))),
                        last_expressed_turn=int(item.get("last_expressed_turn", -999)),
                        resolved=bool(item.get("resolved", False)),
                        linked_episode=str(item.get("linked_episode", "")),
                    )
                )
            self._concerns = concerns[: self._max_concerns]
            self._sort()
        except Exception as exc:
            logger.warning("Could not load active concerns: %s", exc)

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            serializable = [asdict(c) for c in self._concerns]
            self._path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2))
        except Exception as exc:
            logger.warning("Could not save active concerns: %s", exc)

    def _sort(self) -> None:
        self._concerns.sort(
            key=lambda c: (c.resolved, -c.intensity, c.age_turns, -c.last_activated_turn)
        )
        self._concerns = [c for c in self._concerns if not c.resolved][: self._max_concerns]

    def snapshot(self) -> list[dict[str, object]]:
        return [asdict(c) for c in self._concerns]

    def decay(self) -> None:
        changed = False
        survivors: list[Concern] = []
        for concern in self._concerns:
            if concern.resolved:
                changed = True
                continue
            concern.age_turns += 1
            concern.intensity = _clamp01(concern.intensity * _DECAY - _LEAK)
            if concern.intensity >= _MIN_INTENSITY:
                survivors.append(concern)
            else:
                changed = True
        self._concerns = survivors
        self._sort()
        if changed:
            self._save()

    def _find_match(self, topic: str, category: str) -> Concern | None:
        normalized = topic.strip().lower()
        for concern in self._concerns:
            if concern.category != category:
                continue
            if concern.topic.strip().lower() == normalized:
                return concern
            if category in {"agency", "companion", "affect"}:
                return concern
        return None

    def activate(
        self,
        topic: str,
        *,
        category: str = "general",
        intensity: float = 0.4,
        turn_index: int = 0,
        linked_episode: str = "",
    ) -> None:
        cleaned = topic.strip()
        if not cleaned:
            return
        concern = self._find_match(cleaned, category)
        strength = _clamp01(float(intensity))
        if concern is None:
            concern = Concern(
                topic=cleaned,
                category=category,
                intensity=strength,
                age_turns=0,
                last_activated_turn=max(0, turn_index),
                linked_episode=linked_episode,
            )
            self._concerns.append(concern)
        else:
            concern.topic = cleaned
            concern.intensity = _clamp01(concern.intensity + strength * 0.6)
            concern.age_turns = 0
            concern.last_activated_turn = max(0, turn_index)
            concern.resolved = False
            if linked_episode:
                concern.linked_episode = linked_episode
        self._sort()
        self._save()

    def soothe(self, category: str, amount: float = 0.12) -> None:
        changed = False
        for concern in self._concerns:
            if concern.category != category:
                continue
            concern.intensity = _clamp01(concern.intensity - amount)
            concern.resolved = concern.intensity < _MIN_INTENSITY
            changed = True
        if changed:
            self._sort()
            self._save()

    def top_concern(self, min_intensity: float = 0.0) -> Concern | None:
        threshold = max(0.0, min_intensity)
        for concern in self._concerns:
            if not concern.resolved and concern.intensity >= threshold:
                return concern
        return None

    def context_for_prompt(self, *, turn_index: int) -> str | None:
        for concern in self._concerns:
            if concern.resolved or concern.intensity < _PROMPT_THRESHOLD:
                continue
            if turn_index - concern.last_expressed_turn < _PROMPT_COOLDOWN_TURNS:
                continue
            concern.last_expressed_turn = turn_index
            self._save()
            return f"[Active concern]\nSomething still carries forward for me: {concern.topic}"
        return None

    def update_from_turn(
        self,
        *,
        turn_index: int,
        emotion: str,
        companion_mood: str,
        curiosity: str | None,
        prediction_signal: PredictionSignal | None,
    ) -> None:
        self.decay()

        if prediction_signal is not None:
            if prediction_signal.agency_error >= 0.45:
                self.activate(
                    "Something about my recent action still doesn't line up.",
                    category="agency",
                    intensity=0.35 + 0.45 * prediction_signal.agency_error,
                    turn_index=turn_index,
                )
            elif prediction_signal.action_name in {"look", "walk", "see"}:
                self.soothe("agency", amount=0.16)

        if companion_mood == "frustrated":
            self.activate(
                "Kouta may need gentleness right now.",
                category="companion",
                intensity=0.5,
                turn_index=turn_index,
            )
        elif companion_mood in {"happy", "engaged"}:
            self.soothe("companion", amount=0.1)

        if curiosity:
            self.activate(
                curiosity,
                category="curiosity",
                intensity=0.45,
                turn_index=turn_index,
            )

        if emotion in {"sad", "nostalgic"}:
            self.activate(
                "A faint heaviness is still carrying over.",
                category="affect",
                intensity=0.34,
                turn_index=turn_index,
            )
        elif emotion in {"moved", "tender", "relieved"}:
            self.activate(
                "Something about this still feels worth holding onto.",
                category="affect",
                intensity=0.3,
                turn_index=turn_index,
            )
        elif emotion in {"happy", "playful", "proud"}:
            self.soothe("affect", amount=0.08)
