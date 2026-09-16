"""Consciousness profile — a multidimensional, instrumentation-only reading.

Consciousness is not a Bool. This module renders six graded dimensions from
signals the mind layers already produce (interoception, workspace ignition,
identity, metacognition, prediction, voice) — no new cognition, zero I/O,
fully deterministic. The profile is strictly observability: it feeds
diagnostics surfaces and mental_state.jsonl, and must never be rendered into
the agent's prompt or spoken text (raw self-quantification reads as leakage,
and the numbers would contaminate the behaviour they measure).

The formulas below are documented engineering heuristics, not theory: each
dimension is a monotone blend of its inputs, clamped to [0, 1]. Tests pin
bands and orderings, not magic constants.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .mental_state import ConsciousnessState, _clamp01

__all__ = [
    "ConsciousnessProfile",
    "ProfileInputs",
    "compute_consciousness_profile",
]


@dataclass(slots=True, frozen=True)
class ProfileInputs:
    """Raw signals feeding one profile computation (all primitives, no objects)."""

    # wakefulness
    energy: float = 0.5
    quiet_hours: bool = False
    arousal: float = 0.35
    fatigue: float = 0.2
    # access (workspace ignition)
    winner_present: bool = False
    winner_score: float = 0.0
    effective_threshold: float = 0.4
    coalition_count: int = 0
    # self-model integrity
    identity_dissonance: float = 0.0
    identity_threat: float = 0.0
    meta_inconsistency: bool = False
    focus_stability: float = 0.5
    # integration
    source_diversity: float = 0.0
    peripheral_count: int = 0
    thought_streak: int = 0
    # reality testing
    sensor_confidence: float = 0.7
    external_surprise: float = 0.0
    agency_error: float = 0.0
    grounding_ratio: float | None = None
    # reportability
    tts_present: bool = False
    say_recent: bool = False
    self_report_available: bool = False


@dataclass(slots=True, frozen=True)
class ConsciousnessProfile:
    """One computed profile. Immutable so surfaces can share it by reference."""

    wakefulness: float
    access: float
    self_model_integrity: float
    integration: float
    reality_testing: float
    reportability: float
    origin: str = "turn"
    created_at: str = ""

    def overall(self) -> float:
        """Unweighted mean — a convenience scalar, not 'the' consciousness level."""
        return (
            self.wakefulness
            + self.access
            + self.self_model_integrity
            + self.integration
            + self.reality_testing
            + self.reportability
        ) / 6.0

    def one_line(self) -> str:
        return (
            f"wake {self.wakefulness:.2f} | access {self.access:.2f} | "
            f"self {self.self_model_integrity:.2f} | integ {self.integration:.2f} | "
            f"real {self.reality_testing:.2f} | rep {self.reportability:.2f}"
        )

    def as_state(self) -> ConsciousnessState:
        return ConsciousnessState(
            wakefulness=self.wakefulness,
            access=self.access,
            self_model_integrity=self.self_model_integrity,
            integration=self.integration,
            reality_testing=self.reality_testing,
            reportability=self.reportability,
            origin=self.origin,
        )


def compute_consciousness_profile(
    inputs: ProfileInputs,
    *,
    origin: str = "turn",
    created_at: str | None = None,
) -> ConsciousnessProfile:
    """Blend existing signals into the six dimensions. Pure and deterministic."""
    wakefulness = _clamp01(
        0.55 * inputs.energy + 0.25 * inputs.arousal + 0.20 * (1.0 - inputs.fatigue)
    )
    if inputs.quiet_hours:
        wakefulness *= 0.8

    if inputs.winner_present:
        margin = max(0.0, inputs.winner_score - inputs.effective_threshold)
        access = _clamp01(0.5 + 1.5 * margin + 0.05 * min(inputs.coalition_count, 4))
    else:
        # Content circulating but nothing ignited — low access, not zero.
        access = _clamp01(0.08 * min(inputs.coalition_count, 3))

    self_model = _clamp01(
        0.5
        + 0.5 * inputs.focus_stability
        - 0.4 * inputs.identity_dissonance
        - 0.25 * inputs.identity_threat
        - (0.15 if inputs.meta_inconsistency else 0.0)
    )

    integration = _clamp01(
        0.6 * _clamp01(inputs.source_diversity)
        + 0.25 * (min(inputs.peripheral_count, 4) / 4.0)
        + 0.15 * (min(inputs.thought_streak, 3) / 3.0)
    )

    error = _clamp01(0.5 * inputs.external_surprise + 0.5 * inputs.agency_error)
    reality = _clamp01(0.6 * inputs.sensor_confidence + 0.4 * (1.0 - error))
    if inputs.grounding_ratio is not None:
        reality = _clamp01(0.7 * reality + 0.3 * _clamp01(inputs.grounding_ratio))

    reportability = _clamp01(
        0.4  # the text channel always exists
        + (0.3 if inputs.tts_present else 0.0)
        + (0.2 if inputs.say_recent else 0.0)
        + (0.1 if inputs.self_report_available else 0.0)
    )

    return ConsciousnessProfile(
        wakefulness=wakefulness,
        access=access,
        self_model_integrity=self_model,
        integration=integration,
        reality_testing=reality,
        reportability=reportability,
        origin=origin,
        created_at=created_at or datetime.utcnow().isoformat(),
    )
