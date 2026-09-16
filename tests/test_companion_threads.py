"""Companion-thread capture: "I have a presentation tomorrow" must resurface.

After each conversational turn the agent asks the utility LLM whether the
companion mentioned an upcoming event or ongoing situation in THEIR life worth
following up on later.  Detected threads are stored as unfinished business
(source "companion_thread") so the existing surfacing + resolve loop applies —
no new resolution machinery.  Stale threads expire automatically.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from familiar_agent._i18n import _t
from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel


# ── Store: stale-thread expiry ──


@pytest.fixture
def store(tmp_path):
    with patch.object(_EmbeddingModel, "pre_warm"):
        s = ObservationMemory(db_path=str(tmp_path / "obs.db"))
    yield s
    s.close()


def _insert_business(store, *, business_id, source, status, created_at):
    with store._db_lock:
        db = store._ensure_connected()
        db.execute(
            "INSERT INTO unfinished_business "
            "(id, summary, status, source, related_memory_id, metadata_json, created_at, resolved_at) "
            "VALUES (?, ?, ?, ?, NULL, '{}', ?, NULL)",
            (business_id, f"item {business_id}", status, source, created_at),
        )
        db.commit()


def test_expire_stale_companion_threads(store):
    old = (datetime.now() - timedelta(days=20)).isoformat()
    fresh = datetime.now().isoformat()
    _insert_business(
        store, business_id="t-old", source="companion_thread", status="open", created_at=old
    )
    _insert_business(
        store, business_id="t-new", source="companion_thread", status="open", created_at=fresh
    )
    _insert_business(store, business_id="d-old", source="deferral", status="open", created_at=old)
    _insert_business(
        store, business_id="t-done", source="companion_thread", status="resolved", created_at=old
    )

    expired = store.expire_stale_companion_threads(max_age_days=14.0)

    assert expired == 1
    open_ids = {b["id"] for b in store.list_unfinished_business(limit=20)}
    assert "t-old" not in open_ids
    assert {"t-new", "d-old"} <= open_ids


def test_expire_noop_when_nothing_stale(store):
    fresh = datetime.now().isoformat()
    _insert_business(
        store, business_id="t-new", source="companion_thread", status="open", created_at=fresh
    )
    assert store.expire_stale_companion_threads(max_age_days=14.0) == 0


@pytest.mark.asyncio
async def test_expire_async_wrapper(store):
    old = (datetime.now() - timedelta(days=20)).isoformat()
    _insert_business(
        store, business_id="t-old", source="companion_thread", status="open", created_at=old
    )
    assert await store.expire_stale_companion_threads_async(max_age_days=14.0) == 1


# ── Extraction: extract_companion_thread ──


def _extraction_agent(reply: str | Exception):
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    if isinstance(reply, Exception):
        agent._utility_backend = SimpleNamespace(complete=AsyncMock(side_effect=reply))
    else:
        agent._utility_backend = SimpleNamespace(complete=AsyncMock(return_value=reply))
    return agent


@pytest.mark.asyncio
async def test_extracts_followup_thread():
    agent = _extraction_agent("明日プレゼンがあるらしい。")
    thread = await agent.extract_companion_thread("明日大事なプレゼンあるねん、緊張するわ")
    assert thread == "明日プレゼンがあるらしい。"


@pytest.mark.asyncio
async def test_none_word_means_no_thread():
    agent = _extraction_agent(_t("curiosity_none"))
    assert await agent.extract_companion_thread("おはよう、ええ天気やな") is None


@pytest.mark.asyncio
async def test_overlong_reply_rejected():
    agent = _extraction_agent("x" * 200)
    assert await agent.extract_companion_thread("明日プレゼンあるねん") is None


@pytest.mark.asyncio
async def test_extraction_failure_degrades_to_none():
    agent = _extraction_agent(RuntimeError("backend down"))
    assert await agent.extract_companion_thread("明日プレゼンあるねん") is None


@pytest.mark.asyncio
async def test_empty_input_skips_llm_call():
    agent = _extraction_agent("should not be called")
    assert await agent.extract_companion_thread("   ") is None
    agent._utility_backend.complete.assert_not_awaited()


# ── Capture: _capture_companion_thread (dedup, cap, expiry, drive boost) ──


def _capture_agent(*, thread: str | None, open_items: list[dict] | None = None):
    from familiar_agent.agent import EmbodiedAgent

    agent = EmbodiedAgent.__new__(EmbodiedAgent)
    agent.extract_companion_thread = AsyncMock(return_value=thread)
    mem = MagicMock()
    mem.expire_stale_companion_threads_async = AsyncMock(return_value=0)
    mem.list_unfinished_business_async = AsyncMock(return_value=open_items or [])
    mem.open_unfinished_business_async = AsyncMock(return_value="biz-1")
    agent._memory = mem
    return agent


@pytest.mark.asyncio
async def test_capture_opens_thread_with_source():
    agent = _capture_agent(thread="presentation tomorrow")
    desires = MagicMock()

    await agent._capture_companion_thread("明日プレゼンあるねん", desires)

    agent._memory.open_unfinished_business_async.assert_awaited_once()
    args = agent._memory.open_unfinished_business_async.await_args
    assert args.args[0] == "presentation tomorrow"
    assert args.kwargs.get("source") == "companion_thread"
    desires.boost.assert_called_once()
    assert desires.boost.call_args.args[0] == "worry_companion"


@pytest.mark.asyncio
async def test_capture_expires_stale_threads_first():
    agent = _capture_agent(thread=None)
    await agent._capture_companion_thread("おはよう", None)
    agent._memory.expire_stale_companion_threads_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_no_thread_opens_nothing():
    agent = _capture_agent(thread=None)
    await agent._capture_companion_thread("おはよう", None)
    agent._memory.open_unfinished_business_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_duplicate_summary_not_reopened():
    existing = [{"id": "b1", "summary": "presentation tomorrow", "source": "companion_thread"}]
    agent = _capture_agent(thread="presentation tomorrow", open_items=existing)
    await agent._capture_companion_thread("明日プレゼンあるねん", None)
    agent._memory.open_unfinished_business_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_open_thread_cap_respected():
    existing = [
        {"id": f"b{i}", "summary": f"thread {i}", "source": "companion_thread"} for i in range(3)
    ]
    agent = _capture_agent(thread="a fourth thread", open_items=existing)
    await agent._capture_companion_thread("また別の話", None)
    agent._memory.open_unfinished_business_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_other_sources_do_not_count_toward_cap():
    existing = [{"id": f"b{i}", "summary": f"deferred {i}", "source": "deferral"} for i in range(5)]
    agent = _capture_agent(thread="presentation tomorrow", open_items=existing)
    await agent._capture_companion_thread("明日プレゼンあるねん", None)
    agent._memory.open_unfinished_business_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_capture_survives_store_failure():
    agent = _capture_agent(thread="presentation tomorrow")
    agent._memory.list_unfinished_business_async = AsyncMock(side_effect=RuntimeError("db locked"))
    await agent._capture_companion_thread("明日プレゼンあるねん", None)  # must not raise
    agent._memory.open_unfinished_business_async.assert_not_awaited()
