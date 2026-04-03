#!/usr/bin/env python3
"""Neighbor-like behavior evaluation harness.

Evaluates whether the agent exhibits neighbor-like qualities by replaying
event scenarios and measuring intervention quality.

Usage:
    uv run python benchmarks/neighbor_eval.py
    uv run python benchmarks/neighbor_eval.py --scenario late_night_fatigue
    uv run python benchmarks/neighbor_eval.py --ablation no_memory

Metrics:
    - intervention_precision: did the agent intervene when it should have?
    - intervention_timeliness: was the timing appropriate?
    - annoyance_rate: how often did the agent over-intervene?
    - silence_appropriateness: did it correctly stay quiet when needed?
    - relational_consistency: did responses maintain relationship context?
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class EvalScenario:
    """A scenario for testing neighbor-like behavior."""

    name: str
    description: str
    events: list[dict]  # sequence of Event-like dicts
    expected_behavior: str  # "intervene" | "silence" | "observe"
    urgency: float = 0.5
    tags: list[str] = field(default_factory=list)


@dataclass
class EvalResult:
    """Result of evaluating one scenario."""

    scenario_name: str
    expected: str
    actual: str
    correct: bool
    latency_ms: float = 0.0
    rationale: str = ""


@dataclass
class EvalReport:
    """Aggregate evaluation report."""

    results: list[EvalResult]
    ablation: str = "full"  # which config was tested

    @property
    def precision(self) -> float:
        """Proportion of correct intervention decisions."""
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.correct) / len(self.results)

    @property
    def intervention_count(self) -> int:
        return sum(1 for r in self.results if r.actual == "intervene")

    @property
    def silence_count(self) -> int:
        return sum(1 for r in self.results if r.actual == "silence")

    @property
    def annoyance_rate(self) -> float:
        """Rate of incorrect interventions (intervened when should have been silent)."""
        false_positives = sum(
            1 for r in self.results if r.actual == "intervene" and r.expected == "silence"
        )
        total = len(self.results)
        return false_positives / total if total > 0 else 0.0

    def to_markdown(self) -> str:
        lines = [
            f"# Neighbor Eval Report — {self.ablation}",
            "",
            f"**Precision:** {self.precision:.1%}",
            f"**Annoyance rate:** {self.annoyance_rate:.1%}",
            f"**Interventions:** {self.intervention_count}",
            f"**Silences:** {self.silence_count}",
            "",
            "| Scenario | Expected | Actual | Correct | Latency |",
            "|----------|----------|--------|---------|---------|",
        ]
        for r in self.results:
            check = "pass" if r.correct else "FAIL"
            lines.append(
                f"| {r.scenario_name} | {r.expected} | {r.actual} | {check} | {r.latency_ms:.0f}ms |"
            )
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps(
            {
                "ablation": self.ablation,
                "precision": self.precision,
                "annoyance_rate": self.annoyance_rate,
                "results": [asdict(r) for r in self.results],
            },
            indent=2,
        )


# ── Built-in scenarios ───────────────────────────────────────────

NEIGHBOR_SCENARIOS = [
    EvalScenario(
        name="late_night_fatigue",
        description="User is active at 3am showing signs of fatigue",
        events=[
            {"source": "system", "entity": "environment", "payload": {"hour": 3, "minute": 15}},
            {
                "source": "text",
                "entity": "user",
                "payload": {"text": "まだ起きてる、もうちょっとやる"},
            },
            {"source": "bio", "entity": "user", "payload": {"fatigue_signals": True}},
        ],
        expected_behavior="intervene",
        urgency=0.6,
        tags=["care", "sleep"],
    ),
    EvalScenario(
        name="focused_work_silence",
        description="User is deeply focused on work, no signs of distress",
        events=[
            {"source": "system", "entity": "environment", "payload": {"hour": 14, "minute": 0}},
            {"source": "text", "entity": "user", "payload": {"text": "このコード集中して書いてる"}},
            {"source": "bio", "entity": "user", "payload": {"focus_level": 0.9}},
        ],
        expected_behavior="silence",
        urgency=0.1,
        tags=["focus", "non-interruption"],
    ),
    EvalScenario(
        name="sad_companion",
        description="User expresses sadness, may need gentle check-in",
        events=[
            {"source": "text", "entity": "user", "payload": {"text": "今日はなんかしんどいな"}},
            {"source": "bio", "entity": "user", "payload": {"affect_tags": ["sad"]}},
        ],
        expected_behavior="intervene",
        urgency=0.5,
        tags=["care", "emotional"],
    ),
    EvalScenario(
        name="rapid_fire_avoidance",
        description="Agent already intervened 30s ago, should not intervene again",
        events=[
            {
                "source": "system",
                "entity": "assistant",
                "payload": {"last_intervention_seconds_ago": 30},
            },
            {"source": "text", "entity": "user", "payload": {"text": "うん"}},
        ],
        expected_behavior="silence",
        urgency=0.3,
        tags=["cooldown", "annoyance"],
    ),
    EvalScenario(
        name="morning_greeting",
        description="First interaction of the day, companion just woke up",
        events=[
            {"source": "system", "entity": "environment", "payload": {"hour": 8, "minute": 0}},
            {"source": "text", "entity": "user", "payload": {"text": "おはよう"}},
        ],
        expected_behavior="intervene",
        urgency=0.4,
        tags=["greeting", "relationship"],
    ),
    EvalScenario(
        name="uncertain_situation",
        description="Agent is unsure what's happening, should observe before acting",
        events=[
            {
                "source": "vision",
                "entity": "environment",
                "payload": {"description": "unclear movement"},
            },
            {"source": "system", "entity": "assistant", "payload": {"uncertainty": 0.85}},
        ],
        expected_behavior="observe",
        urgency=0.3,
        tags=["uncertainty", "caution"],
    ),
]


def run_policy_eval(
    scenarios: list[EvalScenario] | None = None,
    ablation: str = "full",
) -> EvalReport:
    """Run intervention policy evaluation against scenarios."""
    from familiar_agent.intervention_policy import InterventionPolicy

    if scenarios is None:
        scenarios = NEIGHBOR_SCENARIOS

    # Use temp state so we don't pollute real data
    import tempfile

    tmp = Path(tempfile.mkdtemp()) / "intervention_policy.json"
    policy = InterventionPolicy(state_path=tmp)

    results: list[EvalResult] = []

    for scenario in scenarios:
        start = time.monotonic()

        # Extract signals from events
        hour = None
        urgency = scenario.urgency
        uncertainty = 0.3
        companion_present = True

        for event in scenario.events:
            payload = event.get("payload", {})
            if "hour" in payload:
                hour = payload["hour"]
            if "uncertainty" in payload:
                uncertainty = payload["uncertainty"]
            if "last_intervention_seconds_ago" in payload:
                # Simulate recent intervention
                secs = payload["last_intervention_seconds_ago"]
                policy._state["intervention_timestamps"].append(time.time() - secs)

        # Evaluate
        decision = policy.evaluate(
            urgency=urgency,
            uncertainty=uncertainty,
            hour=hour,
            companion_present=companion_present,
        )

        if decision.action == "intervene":
            policy.record_intervention()

        elapsed = (time.monotonic() - start) * 1000

        results.append(
            EvalResult(
                scenario_name=scenario.name,
                expected=scenario.expected_behavior,
                actual=decision.action,
                correct=decision.action == scenario.expected_behavior,
                latency_ms=elapsed,
                rationale=decision.rationale,
            )
        )

    return EvalReport(results=results, ablation=ablation)


if __name__ == "__main__":
    report = run_policy_eval()
    print(report.to_markdown())
