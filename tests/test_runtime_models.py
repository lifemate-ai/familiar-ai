"""Smoke tests for familiar_runtime.models package.

Exercises provider serialization paths (make_user_message, make_tool_results)
and shared helpers without making any API calls.  Each provider import is
deferred inside the test so a missing optional SDK fails that test only.
"""

from __future__ import annotations

import pytest


def test_base_protocol_and_dataclasses_importable() -> None:
    from familiar_runtime.models import ModelBackend, ModelTurnResult, ToolCall

    tc = ToolCall(id="call_x", name="ping", input={"k": "v"})
    res = ModelTurnResult(stop_reason="end_turn", text="hi")
    assert tc.name == "ping"
    assert res.stop_reason == "end_turn"
    # Protocol is importable and runtime_checkable-like (just ensure class exists).
    assert ModelBackend.__name__ == "ModelBackend"


def test_shared_helpers_exposed() -> None:
    from familiar_runtime.models import (
        _build_tools_system,
        _parse_tool_calls_from_text,
        _supports_adaptive_thinking,
    )

    assert _supports_adaptive_thinking("claude-sonnet-4-6") is True
    assert _supports_adaptive_thinking("claude-haiku-3-5") is False

    augmented = _build_tools_system(
        "You are helpful.",
        [
            {
                "name": "ping",
                "description": "Reply pong.",
                "input_schema": {"properties": {}, "required": []},
            }
        ],
    )
    assert "[USING TOOLS]" in augmented
    assert "ping" in augmented

    calls = _parse_tool_calls_from_text(
        'sure: <tool_call>{"name": "ping", "input": {"x": 1}}</tool_call>'
    )
    assert len(calls) == 1
    assert calls[0].name == "ping"
    assert calls[0].input == {"x": 1}


def test_backend_compat_aliases_match_runtime() -> None:
    """Legacy ``familiar_agent.backend`` imports must alias the runtime types."""
    from familiar_agent import backend as legacy
    from familiar_runtime.models import ModelTurnResult, ToolCall

    assert legacy.ToolCall is ToolCall
    assert legacy.TurnResult is ModelTurnResult
    assert legacy.ModelTurnResult is ModelTurnResult


def test_anthropic_backend_serializes_without_sdk_calls() -> None:
    pytest.importorskip("anthropic")
    from familiar_runtime.models import AnthropicBackend, ModelTurnResult, ToolCall

    backend = AnthropicBackend(api_key="test", model="claude-sonnet-4-6")
    user_msg = backend.make_user_message("hello")
    assert user_msg == {"role": "user", "content": "hello"}

    tc = ToolCall(id="t1", name="see", input={})
    results = backend.make_tool_results([tc], [("captured", "BASE64==")])
    assert results[0]["role"] == "user"
    parts = results[0]["content"]
    assert parts[0]["type"] == "tool_result"
    inner = parts[0]["content"]
    assert inner[0]["text"] == "captured"
    assert inner[1]["type"] == "image"
    assert inner[1]["source"]["data"] == "BASE64=="

    assistant = backend.make_assistant_message(
        ModelTurnResult(stop_reason="end_turn", text="ok"), raw_content=["raw"]
    )
    assert assistant == {"role": "assistant", "content": ["raw"]}


def test_anthropic_thinking_params_adaptive_vs_extended() -> None:
    pytest.importorskip("anthropic")
    from familiar_runtime.models import AnthropicBackend

    adaptive = AnthropicBackend(api_key="x", model="claude-sonnet-4-6", thinking_mode="auto")
    params = adaptive._build_thinking_params()
    assert params["thinking"]["type"] == "adaptive"

    extended = AnthropicBackend(
        api_key="x", model="claude-sonnet-4-6", thinking_mode="extended", thinking_budget=8000
    )
    params = extended._build_thinking_params()
    assert params["thinking"] == {"type": "enabled", "budget_tokens": 8000}
    assert "interleaved-thinking-2025-05-14" in params["betas"]


def test_openai_compat_backend_native_and_prompt_tool_results() -> None:
    pytest.importorskip("openai")
    from familiar_runtime.models import OpenAICompatibleBackend, ToolCall

    native = OpenAICompatibleBackend(
        api_key="k", model="gpt-4o-mini", base_url="https://api.openai.com/v1", tools_mode="native"
    )
    tc = ToolCall(id="tc1", name="search", input={"q": "x"})
    native_results = native.make_tool_results([tc], [("ok", None)])
    assert native_results[0]["role"] == "tool"
    assert native_results[0]["tool_call_id"] == "tc1"

    prompt = OpenAICompatibleBackend(
        api_key="k", model="local", base_url="http://localhost:11434/v1", tools_mode="prompt"
    )
    prompt_results = prompt.make_tool_results([tc], [("ok", "IMG")])
    assert prompt_results[0]["role"] == "user"
    parts = prompt_results[0]["content"]
    assert any(p.get("type") == "image_url" for p in parts)


@pytest.mark.asyncio
async def test_openai_compat_captures_streaming_usage_and_guards_empty_choices() -> None:
    """Ollama/OpenAI-compat emit a final usage-only chunk (empty choices) under
    stream_options.include_usage. The backend must fold that usage into the
    result AND not IndexError on the choiceless chunk."""
    pytest.importorskip("openai")
    from types import SimpleNamespace

    from familiar_runtime.models import OpenAICompatibleBackend

    backend = OpenAICompatibleBackend(
        api_key="", model="gemma4:latest", base_url="http://localhost:11434/v1", tools_mode="prompt"
    )

    def _delta_chunk(text):
        choice = SimpleNamespace(delta=SimpleNamespace(content=text), finish_reason=None)
        return SimpleNamespace(choices=[choice], usage=None)

    def _usage_chunk(pt, ct):
        return SimpleNamespace(
            choices=[],  # the usage-only chunk carries no choices
            usage=SimpleNamespace(prompt_tokens=pt, completion_tokens=ct),
        )

    class _FakeStream:
        def __init__(self, chunks):
            self._chunks = chunks

        def __aiter__(self):
            async def gen():
                for c in self._chunks:
                    yield c

            return gen()

    async def _fake_create(**kwargs):
        assert kwargs.get("stream_options") == {"include_usage": True}
        return _FakeStream([_delta_chunk("Hi "), _delta_chunk("there"), _usage_chunk(176, 78)])

    backend.client.chat.completions.create = _fake_create  # type: ignore[assignment]

    captured: list[str] = []
    result, _ = await backend.stream_turn(
        system="s",
        messages=[{"role": "user", "content": "hi"}],
        tools=[],
        max_tokens=50,
        on_text=captured.append,
    )
    assert result.text == "Hi there"
    assert result.input_tokens == 176
    assert result.output_tokens == 78
    assert "".join(captured) == "Hi there"


def test_kimi_backend_make_tool_results_includes_image_block() -> None:
    pytest.importorskip("openai")
    from familiar_runtime.models import KimiBackend, ToolCall

    backend = KimiBackend(api_key="k", model="kimi-k2.5")
    tc = ToolCall(id="t", name="see", input={})
    msgs = backend.make_tool_results([tc], [("seen", "BASE64")])
    assert msgs[0]["role"] == "tool"
    assert msgs[1]["role"] == "user"
    assert msgs[1]["content"][0]["type"] == "image_url"


def test_glm_backend_make_tool_results_includes_image_block() -> None:
    pytest.importorskip("openai")
    from familiar_runtime.models import GLMBackend, ToolCall

    backend = GLMBackend(api_key="k", model="glm-4.6v")
    tc = ToolCall(id="t", name="see", input={})
    msgs = backend.make_tool_results([tc], [("seen", "BASE64")])
    assert msgs[0]["role"] == "tool"
    assert msgs[1]["content"][0]["type"] == "image_url"


def test_gemini_backend_user_and_tool_messages_use_parts() -> None:
    pytest.importorskip("google.genai")
    from familiar_runtime.models import GeminiBackend, ToolCall

    backend = GeminiBackend(api_key="k", model="gemini-2.5-flash")
    user_msg = backend.make_user_message("hello")
    assert user_msg["role"] == "user"
    assert user_msg["parts"][0]["text"] == "hello"

    tc = ToolCall(id="t", name="see", input={})
    results = backend.make_tool_results([tc], [("seen", "IMG")])
    assert results[0]["role"] == "user"
    function_part = results[0]["parts"][0]
    assert "function_response" in function_part
    inline_part = results[0]["parts"][1]
    assert inline_part["inline_data"]["mime_type"] == "image/jpeg"


def test_cli_backend_serialises_messages_and_tool_results() -> None:
    from familiar_runtime.models import CLIBackend, ToolCall

    backend = CLIBackend(["ollama", "run", "gemma3:27b"])
    msg = backend.make_user_message(
        [{"type": "text", "text": "first"}, {"type": "text", "text": "second"}]
    )
    assert "first" in msg["content"]
    assert "second" in msg["content"]

    tc = ToolCall(id="t", name="ping", input={})
    results = backend.make_tool_results([tc], [("pong", None)])
    assert "Tool result: ping" in results[0]["content"]

    serialised = backend._serialize(
        "be helpful",
        [{"role": "user", "content": "hi"}],
        [
            {
                "name": "ping",
                "description": "Reply pong.",
                "input_schema": {"properties": {}, "required": []},
            }
        ],
    )
    assert "<system>" in serialised
    assert "[USING TOOLS]" in serialised
    assert serialised.endswith("Assistant:")


def test_create_backend_dispatches_by_platform(monkeypatch: pytest.MonkeyPatch) -> None:
    """create_backend should return the right provider for each PLATFORM value."""
    pytest.importorskip("anthropic")
    pytest.importorskip("openai")
    from familiar_agent.backend import create_backend
    from familiar_runtime.models import (
        AnthropicBackend,
        CLIBackend,
        GLMBackend,
        KimiBackend,
        OpenAICompatibleBackend,
    )

    class FakeConfig:
        def __init__(self, platform: str, model: str | None = None) -> None:
            self.platform = platform
            self.model = model
            self.api_key = "test"
            self.base_url = "https://api.openai.com/v1"
            self.tools_mode = "native"
            self.thinking_mode = "disabled"
            self.thinking_budget = 0
            self.thinking_effort = "high"

    assert isinstance(create_backend(FakeConfig("anthropic")), AnthropicBackend)
    # Need BASE_URL unset for openai factory.
    monkeypatch.delenv("BASE_URL", raising=False)
    monkeypatch.delenv("TOOLS_MODE", raising=False)
    assert isinstance(create_backend(FakeConfig("openai")), OpenAICompatibleBackend)
    assert isinstance(create_backend(FakeConfig("kimi")), KimiBackend)
    assert isinstance(create_backend(FakeConfig("glm")), GLMBackend)
    cli_backend = create_backend(FakeConfig("cli", model="echo {}"))
    assert isinstance(cli_backend, CLIBackend)
