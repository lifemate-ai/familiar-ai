"""Scripted task scenarios for the generic runtime evaluation harness.

Each scenario is a self-contained recipe: it ships its own
``ScriptedBackend`` turn list, the tool providers it expects to be
registered, and the success criteria. The eval driver (``task_eval``)
runs them through :class:`familiar_runtime.runtime.AgentRuntime` with
zero API calls.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from familiar_runtime.models.base import ModelTurnResult, ToolCall
from familiar_runtime.tools.base import ToolExecutionResult, ToolSpec
from familiar_runtime.tools.registry import ToolRegistry


# ── Scripted backend (independent of any provider SDK) ─────────────


class ScriptedBackend:
    """Replay a fixed sequence of model turns; no network involved."""

    def __init__(self, turns: list[ModelTurnResult]) -> None:
        self.turns = list(turns)

    def make_user_message(self, content: str | list[Any]) -> dict[str, Any]:
        return {"role": "user", "content": content}

    def make_assistant_message(
        self,
        result: ModelTurnResult,
        raw_content: Any | None = None,
    ) -> dict[str, Any]:
        return {"role": "assistant", "content": result.text, "raw": raw_content}

    def make_tool_results(
        self,
        tool_calls: list[ToolCall],
        results: list[tuple[str, str | None]],
    ) -> list[dict[str, Any]]:
        return [
            {"role": "tool", "name": tc.name, "content": text}
            for tc, (text, _image) in zip(tool_calls, results)
        ]

    async def stream_turn(self, **kwargs: Any) -> tuple[ModelTurnResult, Any]:  # noqa: ARG002
        if not self.turns:
            return ModelTurnResult(stop_reason="end_turn", text="(no more turns)"), None
        result = self.turns.pop(0)
        return result, {"raw": result.text}

    async def complete(self, prompt: str, max_tokens: int) -> str:  # noqa: ARG002
        return ""


# ── Tool providers used by scenarios ───────────────────────────────


class _FixedTool:
    """Return a canned response for a given tool name."""

    def __init__(self, name: str, response_text: str, *, fail: bool = False) -> None:
        self._name = name
        self._response_text = response_text
        self._fail = fail
        self.calls: list[dict[str, Any]] = []

    def specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(
                name=self._name,
                description=f"Test tool {self._name}",
                input_schema={"type": "object", "properties": {}},
            )
        ]

    async def call(self, name: str, tool_input: dict[str, Any]) -> ToolExecutionResult:  # noqa: ARG002
        self.calls.append(dict(tool_input))
        if self._fail:
            return ToolExecutionResult(
                text=f"Tool {self._name} failed.", success=False, error="forced_failure"
            )
        return ToolExecutionResult(text=self._response_text)


# ── Scenario definitions ────────────────────────────────────────────


@dataclass(slots=True)
class TaskScenario:
    """One scripted scenario passed to ``run_scenario``."""

    name: str
    description: str
    user_input: str
    backend_turns: list[ModelTurnResult]
    tool_factories: list[Any] = field(default_factory=list)
    expected_tool_names: list[str] = field(default_factory=list)
    expected_final_substring: str = ""


def _tool(name: str, response: str, *, fail: bool = False) -> _FixedTool:
    return _FixedTool(name, response, fail=fail)


def scenario_simple_file_read() -> TaskScenario:
    return TaskScenario(
        name="simple_file_read",
        description="Model reads a file once and reports back.",
        user_input="Read README and summarise it.",
        backend_turns=[
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[
                    ToolCall(id="tc1", name="read_file", input={"path": "README.md"}),
                ],
                input_tokens=12,
                output_tokens=3,
            ),
            ModelTurnResult(
                stop_reason="end_turn",
                text="README describes familiar-ai.",
                input_tokens=14,
                output_tokens=8,
            ),
        ],
        tool_factories=[lambda: _tool("read_file", "# familiar-ai\nA companion agent.")],
        expected_tool_names=["read_file"],
        expected_final_substring="familiar-ai",
    )


def scenario_search_and_replace() -> TaskScenario:
    return TaskScenario(
        name="search_and_replace",
        description="Glob → grep → edit_file chain.",
        user_input="Find and rename the legacy_helper symbol.",
        backend_turns=[
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[ToolCall(id="g1", name="glob", input={"pattern": "src/**/*.py"})],
            ),
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[
                    ToolCall(
                        id="g2",
                        name="grep",
                        input={"pattern": "legacy_helper", "path": "src/"},
                    )
                ],
            ),
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[
                    ToolCall(
                        id="e1",
                        name="edit_file",
                        input={
                            "path": "src/x.py",
                            "old_string": "legacy_helper",
                            "new_string": "modern_helper",
                        },
                    )
                ],
            ),
            ModelTurnResult(stop_reason="end_turn", text="Renamed legacy_helper everywhere."),
        ],
        tool_factories=[
            lambda: _tool("glob", "src/x.py\nsrc/y.py"),
            lambda: _tool("grep", "src/x.py:42:legacy_helper(...)"),
            lambda: _tool("edit_file", "1 edit applied."),
        ],
        expected_tool_names=["glob", "grep", "edit_file"],
        expected_final_substring="Renamed",
    )


def scenario_tool_error_recovery() -> TaskScenario:
    return TaskScenario(
        name="tool_error_recovery",
        description="First tool fails; model retries with a fallback.",
        user_input="Run the tests.",
        backend_turns=[
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[ToolCall(id="r1", name="run_tests", input={"command": "pytest"})],
            ),
            ModelTurnResult(
                stop_reason="tool_use",
                text="",
                tool_calls=[
                    ToolCall(
                        id="b1",
                        name="bash",
                        input={"command": "pytest -q"},
                    )
                ],
            ),
            ModelTurnResult(stop_reason="end_turn", text="All tests passed."),
        ],
        tool_factories=[
            lambda: _tool("run_tests", "internal failure", fail=True),
            lambda: _tool("bash", "12 passed"),
        ],
        expected_tool_names=["run_tests", "bash"],
        expected_final_substring="passed",
    )


def all_scenarios() -> list[TaskScenario]:
    return [
        scenario_simple_file_read(),
        scenario_search_and_replace(),
        scenario_tool_error_recovery(),
    ]


def build_registry(tool_factories: Iterable[Any]) -> tuple[ToolRegistry, list[_FixedTool]]:
    registry = ToolRegistry()
    tools: list[_FixedTool] = []
    for factory in tool_factories:
        tool = factory()
        tools.append(tool)
        registry.register(tool)
    return registry, tools
