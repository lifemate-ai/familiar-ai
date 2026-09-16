"""Prediction Error Engine — Friston-inspired free-energy signal.

Architecture based on:
- Free Energy Principle (Friston): the brain minimises prediction error.
  Surprise = high prediction error = demands global processing.
- Exponential Moving Average (EMA): each entity maintains a probability
  estimate that rises when observed and decays when absent.

Key concepts:
- predict(): return current probability estimate for all known entities.
- compute_error(): compare prediction against observation; return scalar
  surprise signal in [0.0, 1.0].
- update(): integrate new observations into the probability model.
- as_coalition(): expose current error as a workspace Coalition.

Integration:
- scene.py calls compute_error() + update() after entity extraction.
- workspace.py receives the error via apply_prediction_error() to
  dynamically modulate the ignition threshold.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import logging
import time
from typing import TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .workspace import Coalition

# Default EMA smoothing factor: 0.3 means 30% weight on new observation.
# Higher alpha → faster adaptation (less stable model).
_DEFAULT_EMA_ALPHA = 0.3

# Probability assigned to a newly encountered (never-seen) entity.
_NOVEL_ENTITY_PROB = 0.0

# Floor probability so known entities never fully vanish from the model.
_PROB_FLOOR = 0.01

# How many recent embodied actions to retain for debugging / inspection.
_ACTION_HISTORY_SIZE = 12
_INTENTION_TRACE_SIZE = 10


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass(frozen=True)
class ActionTrace:
    """One embodied action that may condition the next observation."""

    action_name: str
    action_input: dict[str, Any]
    previous_entities: tuple[str, ...]
    timestamp: float


@dataclass(frozen=True)
class PredictionSignal:
    """Breakdown of the latest prediction signal."""

    total_error: float
    external_surprise: float
    agency_error: float
    action_name: str | None
    observed_entities: tuple[str, ...]
    previous_entities: tuple[str, ...]
    change_ratio: float


@dataclass(frozen=True)
class IntentionResult:
    """Compact trace of what I meant to do and what actually happened."""

    intent: str
    predicted_outcome: str
    actual_outcome: str
    agency_error: float
    valence: str
    timestamp: float


class PredictionEngine:
    """Entity-level prediction error engine using exponential moving average.

    The model tracks P(entity | context) for each label it has observed.
    On each update() call the probabilities are adjusted:
      - Observed entities: P ← α·1 + (1-α)·P  (pulled toward 1)
      - Absent entities:   P ← α·0 + (1-α)·P  (pulled toward 0)

    compute_error() then compares the current predictions against a new
    observation set and returns a scalar surprise in [0.0, 1.0].
    """

    def __init__(self, ema_alpha: float = _DEFAULT_EMA_ALPHA) -> None:
        self._ema_alpha = ema_alpha
        self._probs: dict[str, float] = {}
        self._last_error: float | None = None
        self._last_signal: PredictionSignal | None = None
        self._last_observed: tuple[str, ...] = ()
        self._pending_action: ActionTrace | None = None
        self._action_history: deque[ActionTrace] = deque(maxlen=_ACTION_HISTORY_SIZE)
        self._intention_history: deque[IntentionResult] = deque(maxlen=_INTENTION_TRACE_SIZE)

    # ── Probability model ──────────────────────────────────────────────────

    def predict(self) -> dict[str, float]:
        """Return current probability estimates for all tracked entities."""
        return dict(self._probs)

    def record_action(self, action_name: str, action_input: dict[str, Any] | None = None) -> None:
        """Record an embodied action that should condition the next observation."""
        if not action_name:
            return
        trace = ActionTrace(
            action_name=action_name,
            action_input=dict(action_input or {}),
            previous_entities=tuple(sorted(set(self._last_observed))),
            timestamp=time.time(),
        )
        self._pending_action = trace
        self._action_history.append(trace)

    def recent_actions(self, n: int = 5) -> list[ActionTrace]:
        """Return recent embodied actions, oldest first."""
        if n <= 0:
            return []
        return list(self._action_history)[-n:]

    def last_signal(self) -> PredictionSignal | None:
        """Return the latest prediction signal breakdown."""
        return self._last_signal

    def recent_intention_results(self, n: int = 3) -> list[IntentionResult]:
        """Return recent intention-result traces, oldest first."""
        if n <= 0:
            return []
        return list(self._intention_history)[-n:]

    def update(self, observed: list[str]) -> None:
        """Integrate a new observation into the entity probability model.

        Observed entities are pulled toward P=1; absent ones toward P=0.
        """
        observed_set = set(observed)

        # Update all known entities
        for label in list(self._probs):
            target = 1.0 if label in observed_set else 0.0
            self._probs[label] = (
                self._ema_alpha * target + (1 - self._ema_alpha) * self._probs[label]
            )
            # Apply floor to prevent complete forgetting
            self._probs[label] = max(_PROB_FLOOR, self._probs[label])

        # Register newly seen entities
        for label in observed_set:
            if label not in self._probs:
                # New entity: start at alpha (one observation worth of weight)
                self._probs[label] = self._ema_alpha
        self._last_observed = tuple(sorted(observed_set))

    # ── Prediction error ───────────────────────────────────────────────────

    def _base_error(self, observed_set: set[str]) -> float:
        """Compute raw world-model surprise before action conditioning."""
        if not observed_set and not self._probs:
            return 0.0

        errors: list[float] = []

        # Surprise for each known entity (expected but absent, or observed)
        for label, prob in self._probs.items():
            actual = 1.0 if label in observed_set else 0.0
            # Binary cross-entropy style error, simplified to absolute difference
            errors.append(abs(actual - prob))

        # Novel entities (completely unexpected — predicted 0, saw 1)
        novel = observed_set - self._probs.keys()
        for _ in novel:
            errors.append(1.0 - _NOVEL_ENTITY_PROB)  # max surprise

        if not errors:
            return 0.0

        # Mean error, bounded to [0, 1]
        return min(1.0, sum(errors) / len(errors))

    @staticmethod
    def _change_ratio(previous: set[str], current: set[str]) -> float:
        """Return how much the entity set changed, 0.0–1.0."""
        union = previous | current
        if not union:
            return 0.0
        intersection = previous & current
        return 1.0 - (len(intersection) / len(union))

    def _condition_signal(self, base_error: float, observed_set: set[str]) -> PredictionSignal:
        action = self._pending_action
        self._pending_action = None

        action_name = action.action_name if action is not None else None
        previous_entities = (
            action.previous_entities
            if action is not None
            else tuple(sorted(set(self._last_observed)))
        )
        previous_set = set(previous_entities)
        change_ratio = self._change_ratio(previous_set, observed_set)

        external_surprise = _clamp01(base_error)
        agency_error = 0.0

        if action_name == "look":
            degrees_raw = action.action_input.get("degrees", 30) if action is not None else 30
            try:
                degrees = float(degrees_raw)
            except (TypeError, ValueError):
                degrees = 30.0
            expected_change = _clamp01(max(0.25, degrees / 90.0))
            external_surprise = _clamp01(base_error * 0.25)
            agency_error = _clamp01(max(0.0, expected_change - change_ratio))
        elif action_name == "walk":
            # The camera view should stay mostly stable across walk().
            external_surprise = _clamp01(base_error * 0.25)
            agency_error = _clamp01(change_ratio)
        elif action_name == "see":
            external_surprise = _clamp01(base_error)
        else:
            external_surprise = _clamp01(base_error)

        total_error = _clamp01(external_surprise + 0.7 * agency_error)

        return PredictionSignal(
            total_error=total_error,
            external_surprise=external_surprise,
            agency_error=agency_error,
            action_name=action_name,
            observed_entities=tuple(sorted(observed_set)),
            previous_entities=previous_entities,
            change_ratio=change_ratio,
        )

    @staticmethod
    def _predicted_outcome(action_name: str) -> str:
        if action_name == "look":
            return "the camera view should shift after I reoriented my gaze"
        if action_name == "walk":
            return "walking should not directly alter the camera's point of view"
        if action_name == "see":
            return "another glance should mostly confirm the current scene"
        return "the next observation should fit what I just tried to do"

    @staticmethod
    def _actual_outcome(signal: PredictionSignal) -> str:
        count = len(signal.observed_entities)
        return f"I observed {count} entities and the scene changed by {signal.change_ratio:.2f}"

    @staticmethod
    def _valence(signal: PredictionSignal) -> str:
        if signal.agency_error >= 0.45:
            return "misaligned"
        if signal.agency_error >= 0.15 or signal.external_surprise >= 0.25:
            return "uncertain"
        return "aligned"

    def _record_intention_result(self, signal: PredictionSignal) -> None:
        if not signal.action_name:
            return
        self._intention_history.append(
            IntentionResult(
                intent=signal.action_name,
                predicted_outcome=self._predicted_outcome(signal.action_name),
                actual_outcome=self._actual_outcome(signal),
                agency_error=signal.agency_error,
                valence=self._valence(signal),
                timestamp=time.time(),
            )
        )

    def context_for_prompt(self) -> str | None:
        """Return a compact recent intention-result trace when it is informative."""
        trace = self._intention_history[-1] if self._intention_history else None
        if trace is None:
            return None
        if trace.agency_error < 0.15 and trace.valence == "aligned":
            return None
        return (
            "[Recent intention-result]\n"
            f"I tried to {trace.intent}. I expected {trace.predicted_outcome}, "
            f"but {trace.actual_outcome} (agency error {trace.agency_error:.2f})."
        )

    def compute_error(self, observed: list[str]) -> float:
        """Compute action-conditioned prediction error for a new observation.

        The signal is split into:
        1. external_surprise: the world differs from expectation
        2. agency_error: the result of my own action differed from expectation

        Returns a scalar in [0.0, 1.0].
        """
        observed_set = set(observed)
        base_error = self._base_error(observed_set)
        signal = self._condition_signal(base_error, observed_set)
        self._last_signal = signal
        self._last_error = signal.total_error
        self._record_intention_result(signal)
        logger.debug(
            "Prediction error: total=%.3f ext=%.3f agency=%.3f action=%s observed=%s",
            signal.total_error,
            signal.external_surprise,
            signal.agency_error,
            signal.action_name or "-",
            sorted(observed_set),
        )
        return signal.total_error

    # ── Workspace Coalition ────────────────────────────────────────────────

    def as_coalition(self) -> Coalition | None:
        """Return a workspace Coalition from the most recent prediction error.

        Returns None if no error has been computed yet (compute_error not called).
        High prediction error → high activation + high novelty in the coalition.
        """
        from .workspace import Coalition

        signal = self._last_signal
        if signal is None or self._last_error is None:
            return None

        error = self._last_error
        # Only surface as a coalition if there's meaningful surprise
        if error < 0.05:
            return None

        # Map error to coalition fields
        # High error = high activation (demands attention) + high novelty
        activation = min(1.0, error * 1.2)  # slight amplification
        novelty = error
        urgency = min(1.0, max(error * 0.8, signal.agency_error))

        n_tracked = len(self._probs)
        if signal.action_name:
            summary = (
                f"prediction error={error:.2f} ext={signal.external_surprise:.2f} "
                f"agency={signal.agency_error:.2f} action={signal.action_name}"
            )
        else:
            summary = f"prediction error={error:.2f} ({n_tracked} tracked entities)"
        context = (
            f"[Prediction error: {error:.2f}]\n"
            f"External surprise={signal.external_surprise:.2f}; "
            f"agency error={signal.agency_error:.2f}. "
            f"{n_tracked} entities tracked. "
            f"The world differs from expectation — attend carefully."
        )

        return Coalition(
            source="prediction",
            summary=summary,
            activation=activation,
            urgency=urgency,
            novelty=novelty,
            context_block=context,
        )
