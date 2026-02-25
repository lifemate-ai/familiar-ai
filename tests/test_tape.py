"""Tests for the TAPE planning mechanisms."""

from __future__ import annotations

import pytest

from familiar_agent.tape import (
    check_plan_blocked,
    generate_plan,
    generate_replan,
)


class _MockBackend:
    """Minimal mock backend for testing."""

    def __init__(self, response: str = "") -> None:
        self._response = response

    async def complete(self, prompt: str, max_tokens: int) -> str:
        return self._response


class _FailingBackend:
    async def complete(self, prompt: str, max_tokens: int) -> str:
        raise RuntimeError("network error")


# ── generate_plan ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_plan_returns_string() -> None:
    backend = _MockBackend("1. Call see() to look around.\n2. Call say() to report.")
    result = await generate_plan(backend, "Look around the room", ["see", "say", "walk"])
    assert "1." in result


@pytest.mark.asyncio
async def test_generate_plan_empty_input() -> None:
    result = await generate_plan(_MockBackend("ignored"), "   ", ["see", "say"])
    assert result == ""


@pytest.mark.asyncio
async def test_generate_plan_no_tools() -> None:
    result = await generate_plan(_MockBackend("ignored"), "Do something", [])
    assert result == ""


@pytest.mark.asyncio
async def test_generate_plan_backend_failure() -> None:
    result = await generate_plan(_FailingBackend(), "Look around", ["see"])
    assert result == ""


# ── check_plan_blocked ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_check_plan_blocked_returns_true() -> None:
    backend = _MockBackend("blocked")
    result = await check_plan_blocked(
        backend,
        plan="1. see() to find the cat\n2. say() to report",
        tool_name="see",
        tool_args={},
        result="Image captured: empty room, no animals visible.",
    )
    assert result is True


@pytest.mark.asyncio
async def test_check_plan_blocked_returns_false_on_ok() -> None:
    backend = _MockBackend("ok")
    result = await check_plan_blocked(
        backend,
        plan="1. see() to look outside\n2. say() what you see",
        tool_name="see",
        tool_args={},
        result="Image captured: sunny street with pedestrians.",
    )
    assert result is False


@pytest.mark.asyncio
async def test_check_plan_blocked_empty_plan_skips_check() -> None:
    # No plan → always returns False without calling backend
    result = await check_plan_blocked(
        _FailingBackend(),  # would raise if called
        plan="",
        tool_name="see",
        tool_args={},
        result="anything",
    )
    assert result is False


@pytest.mark.asyncio
async def test_check_plan_blocked_backend_failure_returns_false() -> None:
    result = await check_plan_blocked(
        _FailingBackend(),
        plan="1. see()\n2. say()",
        tool_name="see",
        tool_args={},
        result="some result",
    )
    assert result is False


@pytest.mark.asyncio
async def test_check_plan_blocked_ignores_unexpected_llm_output() -> None:
    # LLM returns something other than "blocked" → treated as "ok"
    backend = _MockBackend("yes it is blocked")  # not exactly "blocked"
    result = await check_plan_blocked(
        backend,
        plan="1. see()\n2. walk()",
        tool_name="see",
        tool_args={},
        result="result",
    )
    assert result is False


# ── generate_replan ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_replan_returns_suggestion() -> None:
    backend = _MockBackend("Try looking left with look(direction='left') instead.")
    result = await generate_replan(
        backend,
        plan="1. see() to find the cat\n2. say() to report",
        tool_name="see",
        tool_args={},
        result="Empty room, no cat found.",
    )
    assert len(result) > 0


@pytest.mark.asyncio
async def test_generate_replan_backend_failure_returns_empty() -> None:
    result = await generate_replan(
        _FailingBackend(),
        plan="1. walk()\n2. see()",
        tool_name="walk",
        tool_args={"direction": "forward"},
        result="some result",
    )
    assert result == ""


@pytest.mark.asyncio
async def test_generate_replan_empty_response_returns_empty() -> None:
    backend = _MockBackend("")
    result = await generate_replan(
        backend,
        plan="1. say() hello",
        tool_name="say",
        tool_args={"text": "hello"},
        result="some result",
    )
    assert result == ""
