"""Compatibility tests for backend dataclasses moved to familiar_runtime."""

from __future__ import annotations

from familiar_agent.backend import ToolCall, TurnResult
from familiar_runtime.models import ModelTurnResult, ToolCall as RuntimeToolCall


def test_backend_tool_call_is_runtime_tool_call_alias() -> None:
    call = ToolCall(id="tc1", name="read_file", input={"path": "README.md"})

    assert isinstance(call, RuntimeToolCall)
    assert call.name == "read_file"


def test_backend_turn_result_is_runtime_model_turn_result_alias() -> None:
    result = TurnResult(stop_reason="end_turn", text="done", input_tokens=1, output_tokens=2)

    assert isinstance(result, ModelTurnResult)
    assert result.raw is None
