#!/usr/bin/env python3
"""Task-mode evaluation harness for the generic runtime.

Runs the scripted scenarios under ``benchmarks.task_scenarios`` through
:class:`familiar_runtime.runtime.AgentRuntime`, collects per-scenario
metrics, and emits a JSON report. No API calls are made; the backend is
replayed from scripts so the suite is fully deterministic.

Usage::

    uv run python benchmarks/task_eval.py
    uv run python benchmarks/task_eval.py --scenario simple_file_read
    uv run python benchmarks/task_eval.py --json reports/task_eval.json

Reported metrics per scenario:
    - success: whether all expected tools fired AND the final text matched
    - tool_calls: number of tool invocations
    - tool_success_rate: fraction of tool calls that returned success
    - input_tokens / output_tokens
    - turn_duration_ms
    - time_to_first_tool_ms
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

# Add project root so direct ``python benchmarks/task_eval.py`` works:
# - the project root gives access to the ``benchmarks`` package
# - the ``src`` directory gives access to ``familiar_runtime`` when
#   the script is run outside ``uv run`` context.
_PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from familiar_runtime.runtime import AgentRuntime  # noqa: E402

from benchmarks.task_scenarios import (  # noqa: E402
    ScriptedBackend,
    TaskScenario,
    all_scenarios,
    build_registry,
)


@dataclass(slots=True)
class ScenarioMetrics:
    name: str
    success: bool
    tool_calls: int
    tool_success_rate: float
    input_tokens: int
    output_tokens: int
    turn_duration_ms: float
    time_to_first_tool_ms: float | None
    final_text: str
    failure_reason: str | None = None


async def run_scenario(scenario: TaskScenario) -> ScenarioMetrics:
    backend = ScriptedBackend(scenario.backend_turns)
    registry, tools = build_registry(scenario.tool_factories)
    runtime = AgentRuntime(backend=backend, tools=registry)

    first_tool_at: float | None = None

    # Wrap registry.call to capture the first tool latency.
    original_call = registry.call

    async def timed_call(name: str, tool_input: dict):  # type: ignore[no-untyped-def]
        nonlocal first_tool_at
        if first_tool_at is None:
            first_tool_at = time.perf_counter()
        return await original_call(name, tool_input)

    registry.call = timed_call  # type: ignore[assignment]

    start = time.perf_counter()
    result = await runtime.run_turn(scenario.user_input, profile="task")
    elapsed = (time.perf_counter() - start) * 1000.0

    tool_call_total = len(result.tool_calls)
    tool_success_total = sum(1 for tool in tools for _ in tool.calls)
    tool_success_rate = tool_success_total / tool_call_total if tool_call_total else 1.0

    actual_tool_names = [tool_call.name for tool_call in result.tool_calls]
    tools_ok = actual_tool_names == scenario.expected_tool_names
    text_ok = (
        scenario.expected_final_substring in result.final_text
        if scenario.expected_final_substring
        else True
    )
    success = tools_ok and text_ok

    failure_reason: str | None = None
    if not tools_ok:
        failure_reason = (
            f"tool sequence mismatch: expected {scenario.expected_tool_names!r}, "
            f"got {actual_tool_names!r}"
        )
    elif not text_ok:
        failure_reason = (
            f"final text missing substring {scenario.expected_final_substring!r}: "
            f"{result.final_text!r}"
        )

    return ScenarioMetrics(
        name=scenario.name,
        success=success,
        tool_calls=tool_call_total,
        tool_success_rate=tool_success_rate,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        turn_duration_ms=elapsed,
        time_to_first_tool_ms=(first_tool_at - start) * 1000.0 if first_tool_at else None,
        final_text=result.final_text,
        failure_reason=failure_reason,
    )


async def run_all(scenarios: list[TaskScenario]) -> list[ScenarioMetrics]:
    return [await run_scenario(scenario) for scenario in scenarios]


def _format_report(metrics: list[ScenarioMetrics]) -> str:
    lines = ["# Task eval report", ""]
    success = sum(1 for metric in metrics if metric.success)
    total = len(metrics)
    lines.append(f"Pass rate: {success}/{total}")
    lines.append("")
    for metric in metrics:
        status = "✅" if metric.success else "❌"
        lines.append(f"{status} {metric.name}")
        lines.append(f"    tool_calls = {metric.tool_calls}")
        lines.append(f"    tool_success_rate = {metric.tool_success_rate:.2f}")
        lines.append(f"    tokens = in:{metric.input_tokens} out:{metric.output_tokens}")
        lines.append(f"    turn_duration_ms = {metric.turn_duration_ms:.2f}")
        if metric.time_to_first_tool_ms is not None:
            lines.append(f"    time_to_first_tool_ms = {metric.time_to_first_tool_ms:.2f}")
        lines.append(f"    final_text = {metric.final_text!r}")
        if metric.failure_reason:
            lines.append(f"    failure_reason = {metric.failure_reason}")
        lines.append("")
    return "\n".join(lines)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Task-mode evaluation harness.")
    parser.add_argument(
        "--scenario",
        action="append",
        help="Restrict to one or more scenario names (default: all).",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Optional path to write the metrics JSON report.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    scenarios = all_scenarios()
    if args.scenario:
        wanted = set(args.scenario)
        scenarios = [scenario for scenario in scenarios if scenario.name in wanted]
        if not scenarios:
            print(f"No scenarios matched {sorted(wanted)!r}", file=sys.stderr)
            return 2

    metrics = asyncio.run(run_all(scenarios))
    print(_format_report(metrics))

    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps([asdict(metric) for metric in metrics], indent=2))

    failed = sum(1 for metric in metrics if not metric.success)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
