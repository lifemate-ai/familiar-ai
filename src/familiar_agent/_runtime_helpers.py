"""Shared runtime constants and async helpers.

These were originally defined at module level in
``familiar_agent.agent``; they were lifted here so the embodied hook
extracted in PR3 of the runtime reorg can reuse them without setting up
a circular import against ``agent.py``.
"""

from __future__ import annotations

import inspect
from typing import Any


async def _noop_str() -> str:
    """Async no-op that returns an empty string (used as a placeholder in asyncio.gather)."""
    return ""


async def _noop_list() -> list:
    """Async no-op list placeholder."""
    return []


async def _call_optional_async(
    method: Any | None,
    *args: Any,
    fallback: Any,
    **kwargs: Any,
) -> Any:
    """Call optional async-like method; gracefully fall back for mocks/missing methods."""
    if method is None:
        return fallback
    try:
        result = method(*args, **kwargs)
    except Exception:
        return fallback
    if inspect.isawaitable(result):
        return await result
    if result.__class__.__module__.startswith("unittest.mock"):
        return fallback
    return result


MAX_ITERATIONS = 50
_MORNING_CONTEXT_MAX_CHARS = 2600
_BRIEF_REPLY_MAX_ITERATIONS = 2
_BRIEF_REPLY_MAX_TOKENS = 120
