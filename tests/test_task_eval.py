"""Tests for the task-mode evaluation harness."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make ``benchmarks`` importable regardless of how pytest is invoked.
_PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from benchmarks import task_eval, task_scenarios  # noqa: E402


@pytest.mark.asyncio
async def test_simple_file_read_scenario_succeeds() -> None:
    scenario = task_scenarios.scenario_simple_file_read()
    metric = await task_eval.run_scenario(scenario)
    assert metric.success
    assert metric.tool_calls == 1
    assert metric.tool_success_rate == pytest.approx(1.0)
    assert metric.final_text == "README describes familiar-ai."
    assert metric.time_to_first_tool_ms is not None and metric.time_to_first_tool_ms >= 0


@pytest.mark.asyncio
async def test_search_and_replace_scenario_succeeds() -> None:
    scenario = task_scenarios.scenario_search_and_replace()
    metric = await task_eval.run_scenario(scenario)
    assert metric.success
    assert metric.tool_calls == 3


@pytest.mark.asyncio
async def test_tool_error_recovery_scenario_succeeds() -> None:
    scenario = task_scenarios.scenario_tool_error_recovery()
    metric = await task_eval.run_scenario(scenario)
    assert metric.success
    assert metric.tool_calls == 2


def test_main_emits_json_report(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    exit_code = task_eval.main(["--json", str(out)])
    assert exit_code == 0
    data = json.loads(out.read_text())
    assert {entry["name"] for entry in data} == {
        "simple_file_read",
        "search_and_replace",
        "tool_error_recovery",
    }
    assert all(entry["success"] for entry in data)


def test_main_returns_nonzero_when_scenario_filter_misses() -> None:
    exit_code = task_eval.main(["--scenario", "does_not_exist"])
    assert exit_code == 2


@pytest.mark.asyncio
async def test_failed_tool_sequence_reports_failure_reason() -> None:
    """If the scripted backend deviates from expected_tool_names, success is False."""
    scenario = task_scenarios.scenario_simple_file_read()
    # Mutate the expected sequence so the scenario is forced to fail.
    scenario.expected_tool_names = ["grep"]
    metric = await task_eval.run_scenario(scenario)
    assert not metric.success
    assert metric.failure_reason is not None
    assert "tool sequence mismatch" in metric.failure_reason
