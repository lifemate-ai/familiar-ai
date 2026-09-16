"""Tests for the native Ollama backend (no server required)."""

from __future__ import annotations


import pytest

from familiar_agent.backend import ToolCall
from familiar_agent.ollama_backend import (
    OllamaBackend,
    normalize_base_url,
    think_flag,
)


def _backend(chunks: list[dict], **kw) -> tuple[OllamaBackend, list[dict]]:
    seen: list[dict] = []

    async def fake_stream(body):
        seen.append(body)
        for c in chunks:
            yield c

    return OllamaBackend("qwen3.5:9b", stream_factory=fake_stream, **kw), seen


def test_normalize_base_url_strips_v1_suffix() -> None:
    assert normalize_base_url("http://localhost:11434/v1") == "http://localhost:11434"
    assert normalize_base_url("http://localhost:11434/") == "http://localhost:11434"
    assert normalize_base_url("") == "http://localhost:11434"


def test_think_flag_defaults_off_for_auto() -> None:
    assert think_flag("auto") is False
    assert think_flag("disabled") is False
    assert think_flag("adaptive") is True
    assert think_flag("extended") is True


@pytest.mark.asyncio
async def test_request_carries_think_num_ctx_and_native_tools() -> None:
    be, seen = _backend([{"message": {"content": "hi"}, "done": True}], think=False, num_ctx=8192)
    tools = [{"name": "say", "description": "speak", "input_schema": {"type": "object"}}]
    await be.stream_turn(("stable", "variable"), [be.make_user_message("yo")], tools, 100)
    body = seen[0]
    assert body["think"] is False
    assert body["options"] == {"num_ctx": 8192, "num_predict": 100}
    assert body["tools"][0]["function"]["name"] == "say"
    assert body["messages"][0] == {"role": "system", "content": "stable\n\n---\n\nvariable"}
    assert body["messages"][1] == {"role": "user", "content": "yo"}


@pytest.mark.asyncio
async def test_stream_turn_collects_text_and_usage() -> None:
    be, _ = _backend(
        [
            {"message": {"content": "おか"}, "done": False},
            {"message": {"content": "えり"}, "done": False},
            {"message": {"content": ""}, "done": True, "prompt_eval_count": 12, "eval_count": 3},
        ]
    )
    got: list[str] = []
    result, raw = await be.stream_turn("s", [], [], 50, on_text=got.append)
    assert result.stop_reason == "end_turn"
    assert result.text == "おかえり"
    assert got == ["おか", "えり"]
    assert (result.input_tokens, result.output_tokens) == (12, 3)
    assert raw == {"role": "assistant", "content": "おかえり"}


@pytest.mark.asyncio
async def test_stream_turn_parses_tool_calls_and_keeps_thinking_in_raw() -> None:
    be, _ = _backend(
        [
            {"message": {"thinking": "hmm"}, "done": False},
            {
                "message": {
                    "content": "",
                    "tool_calls": [{"function": {"name": "say", "arguments": {"text": "やあ"}}}],
                },
                "done": False,
            },
            {"message": {"content": ""}, "done": True},
        ]
    )
    result, raw = await be.stream_turn("s", [], [], 50)
    assert result.stop_reason == "tool_use"
    assert [(tc.name, tc.input) for tc in result.tool_calls] == [("say", {"text": "やあ"})]
    assert raw["thinking"] == "hmm"
    assert raw["tool_calls"][0]["function"]["name"] == "say"


@pytest.mark.asyncio
async def test_tool_call_arguments_may_arrive_as_json_string() -> None:
    be, _ = _backend(
        [
            {
                "message": {
                    "tool_calls": [
                        {"function": {"name": "look", "arguments": '{"direction": "left"}'}}
                    ]
                },
                "done": True,
            }
        ]
    )
    result, _ = await be.stream_turn("s", [], [], 50)
    assert result.tool_calls[0].input == {"direction": "left"}


def test_tool_results_use_native_tool_role_and_image_message() -> None:
    be, _ = _backend([])
    calls = [ToolCall(id="c1", name="see", input={})]
    msgs = be.make_tool_results(calls, [("captured", "QUJD")])
    assert msgs[0] == {"role": "tool", "tool_name": "see", "content": "captured"}
    assert msgs[1]["role"] == "user" and msgs[1]["images"] == ["QUJD"]


def test_user_message_from_blocks_extracts_images() -> None:
    be, _ = _backend([])
    msg = be.make_user_message(
        [
            {"type": "text", "text": "見て"},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,QUJD"}},
        ]
    )
    assert msg == {"role": "user", "content": "見て", "images": ["QUJD"]}


@pytest.mark.asyncio
async def test_error_chunk_raises() -> None:
    be, _ = _backend([{"error": "model not found"}])
    try:
        await be.stream_turn("s", [], [], 10)
    except RuntimeError as e:
        assert "model not found" in str(e)
    else:  # pragma: no cover
        raise AssertionError("expected RuntimeError")


@pytest.mark.asyncio
async def test_complete_returns_joined_text_and_swallows_errors() -> None:
    be, seen = _backend([{"message": {"content": "happy"}, "done": True}])
    assert await be.complete("label this", 20) == "happy"
    assert seen[0]["messages"] == [{"role": "user", "content": "label this"}]

    async def boom(body):
        raise RuntimeError("down")
        yield  # pragma: no cover

    assert await OllamaBackend("m", stream_factory=boom).complete("x", 5) == ""


# ── factory wiring ────────────────────────────────────────────────────────────


def _config(**overrides):
    from familiar_agent.config import AgentConfig

    cfg = AgentConfig.__new__(AgentConfig)
    cfg.api_key = ""
    cfg.platform = "ollama"
    cfg.model = ""
    cfg.base_url = "http://localhost:11434/v1"
    cfg.tools_mode = "prompt"
    cfg.thinking_mode = "auto"
    cfg.ollama_num_ctx = 4096
    cfg.utility_platform = ""
    cfg.utility_api_key = ""
    cfg.utility_model = ""
    cfg.scene_platform = ""
    cfg.scene_api_key = ""
    cfg.scene_model = ""
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


def test_create_backend_ollama_platform() -> None:
    from familiar_agent.backend import create_backend

    be = create_backend(_config(model="qwen3.5:9b", thinking_mode="extended"))
    assert isinstance(be, OllamaBackend)
    assert be.model == "qwen3.5:9b"
    assert be.base_url == "http://localhost:11434"
    assert be.think is True and be.num_ctx == 4096


def test_utility_and_scene_backends_accept_ollama_without_api_key() -> None:
    from familiar_agent.backend import create_scene_backend, create_utility_backend

    cfg = _config(
        model="qwen3.5:9b",
        utility_platform="ollama",
        scene_platform="ollama",
        scene_model="qwen3.5:4b",
    )
    util = create_utility_backend(cfg)
    scene = create_scene_backend(cfg)
    assert isinstance(util, OllamaBackend) and util.model == "qwen3.5:9b" and util.think is False
    assert isinstance(scene, OllamaBackend) and scene.model == "qwen3.5:4b"


def test_openai_compatible_local_disables_reasoning_by_default(monkeypatch) -> None:
    from familiar_agent.backend import OpenAICompatibleBackend, create_backend

    monkeypatch.setenv("BASE_URL", "http://localhost:11434/v1")
    be = create_backend(_config(platform="openai", model="qwen3.5:9b"))
    assert isinstance(be, OpenAICompatibleBackend)
    assert be.reasoning_effort == "none"
    assert be._extra_kwargs() == {"reasoning_effort": "none"}
    be2 = create_backend(_config(platform="openai", model="qwen3.5:9b", thinking_mode="extended"))
    assert be2.reasoning_effort is None
