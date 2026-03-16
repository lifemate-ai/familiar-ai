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

import logging
from typing import TYPE_CHECKING

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

    # ── Probability model ──────────────────────────────────────────────────

    def predict(self) -> dict[str, float]:
        """Return current probability estimates for all tracked entities."""
        return dict(self._probs)

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

    # ── Prediction error ───────────────────────────────────────────────────

    def compute_error(self, observed: list[str]) -> float:
        """Compute prediction error between current model and new observation.

        Error = average surprise across both:
        1. Novel entities (predicted 0, saw 1) — positive surprise
        2. Expected entities that disappeared (predicted high, saw 0) — negative surprise

        Returns a scalar in [0.0, 1.0].
        """
        if not observed and not self._probs:
            self._last_error = 0.0
            return 0.0

        observed_set = set(observed)
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
            self._last_error = 0.0
            return 0.0

        # Mean error, bounded to [0, 1]
        error = min(1.0, sum(errors) / len(errors))
        self._last_error = error
        logger.debug("Prediction error: %.3f (observed=%s)", error, sorted(observed_set))
        return error

    # ── Workspace Coalition ────────────────────────────────────────────────

    def as_coalition(self) -> Coalition | None:
        """Return a workspace Coalition from the most recent prediction error.

        Returns None if no error has been computed yet (compute_error not called).
        High prediction error → high activation + high novelty in the coalition.
        """
        from .workspace import Coalition

        if self._last_error is None:
            return None

        error = self._last_error
        # Only surface as a coalition if there's meaningful surprise
        if error < 0.05:
            return None

        # Map error to coalition fields
        # High error = high activation (demands attention) + high novelty
        activation = min(1.0, error * 1.2)  # slight amplification
        novelty = error
        urgency = min(1.0, error * 0.8)  # urgency slightly below activation

        n_tracked = len(self._probs)
        summary = f"prediction error={error:.2f} ({n_tracked} tracked entities)"
        context = (
            f"[Prediction error: {error:.2f}]\n"
            f"High surprise detected. {n_tracked} entities tracked. "
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
