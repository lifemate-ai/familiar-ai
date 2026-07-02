"""Sleep consolidation: nightly memory hygiene as lossy compression.

FAMILIAR_SLEEP_CONSOLIDATION (default off) runs a once-per-night background
job during quiet hours: dedup near-duplicates, decay importance, distill
yesterday's observations into semantic facts (one bounded utility call),
expire stale working memory. FAMILIAR_DREAM adds a few ungrounded generative
cycles journaled as kind="dream" with a not-perception label. The job never
fires a turn — idle precedence is untouched.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from familiar_agent._ui_helpers import night_key_for, should_run_sleep_consolidation

from tests.test_agent_react_loop import _make_agent


# ── Gate ──


def _gate(**overrides):
    kwargs = {
        "enabled": True,
        "agent_running": False,
        "has_pending_input": False,
        "quiet_hours": True,
        "now_dt": datetime(2026, 7, 3, 2, 30),
        "last_night_key": None,
    }
    kwargs.update(overrides)
    return should_run_sleep_consolidation(**kwargs)


def test_gate_fires_only_when_quiet_idle_enabled_and_fresh():
    assert _gate()
    assert not _gate(enabled=False)
    assert not _gate(agent_running=True)
    assert not _gate(has_pending_input=True)
    assert not _gate(quiet_hours=False)


def test_gate_once_per_night_marker():
    now = datetime(2026, 7, 3, 2, 30)
    key = night_key_for(now)
    assert not _gate(now_dt=now, last_night_key=key)
    assert _gate(now_dt=now, last_night_key="2026-06-30")


def test_night_key_groups_before_and_after_midnight():
    before_midnight = datetime(2026, 7, 2, 23, 30)
    after_midnight = datetime(2026, 7, 3, 3, 0)
    next_night = datetime(2026, 7, 3, 23, 30)
    assert night_key_for(before_midnight) == night_key_for(after_midnight)
    assert night_key_for(next_night) != night_key_for(after_midnight)


# ── Job orchestration ──


def _job_agent(tmp_path, *, dream: bool = False):
    agent = _make_agent()
    agent.config.sleep_consolidation = True
    agent.config.dream_mode = dream
    mem = MagicMock()
    mem.consolidate_memories_async = AsyncMock(return_value=2)
    mem.decay_importance_async = AsyncMock(return_value=5)
    mem.expire_working_memory_async = AsyncMock(return_value=3)
    mem.upsert_semantic_fact_async = AsyncMock()
    mem.get_observations_for_date = MagicMock(
        return_value=[{"content": "companion works late on Tuesdays"}]
    )
    mem.save_async = AsyncMock(return_value=True)
    agent._memory = mem
    agent._utility_backend = MagicMock()
    agent._utility_backend.complete = AsyncMock(
        return_value="tuesday-rhythm: companion tends to work late on Tuesdays"
    )
    # Marker writes go under tmp via monkey-style patching of the state path.
    agent._consolidation_night_key = None
    agent._mark_consolidation_night = MagicMock(
        side_effect=lambda key: setattr(agent, "_consolidation_night_key", key)
    )
    agent._dmn = MagicMock()
    agent._dmn.wander = AsyncMock(return_value=None)
    return agent


@pytest.mark.asyncio
async def test_job_runs_all_steps_and_marks_before_llm(tmp_path):
    agent = _job_agent(tmp_path)
    await agent._run_sleep_consolidation()
    agent._memory.consolidate_memories_async.assert_awaited_once()
    agent._memory.decay_importance_async.assert_awaited_once()
    agent._memory.expire_working_memory_async.assert_awaited_once()
    agent._memory.upsert_semantic_fact_async.assert_awaited_once()
    args = agent._memory.upsert_semantic_fact_async.await_args
    assert args.args[0].startswith("night:")
    assert agent._consolidation_night_key is not None  # marked


@pytest.mark.asyncio
async def test_job_skips_distillation_when_utility_is_main(tmp_path):
    agent = _job_agent(tmp_path)
    agent._utility_backend = agent.backend  # no separate utility model
    await agent._run_sleep_consolidation()
    agent._memory.upsert_semantic_fact_async.assert_not_awaited()
    agent._memory.consolidate_memories_async.assert_awaited_once()  # rest still runs


@pytest.mark.asyncio
async def test_job_noop_when_flag_off(tmp_path):
    agent = _job_agent(tmp_path)
    agent.config.sleep_consolidation = False
    await agent._run_sleep_consolidation()
    agent._memory.consolidate_memories_async.assert_not_awaited()
    agent._mark_consolidation_night.assert_not_called()


@pytest.mark.asyncio
async def test_job_aborts_when_turn_starts(tmp_path):
    agent = _job_agent(tmp_path)

    async def dedup_then_turn():
        agent._turn_active = True
        return 0

    agent._memory.consolidate_memories_async = AsyncMock(side_effect=dedup_then_turn)
    await agent._run_sleep_consolidation()
    agent._memory.decay_importance_async.assert_not_awaited()  # yielded to the turn


@pytest.mark.asyncio
async def test_job_step_failures_do_not_stop_later_steps(tmp_path):
    agent = _job_agent(tmp_path)
    agent._memory.consolidate_memories_async = AsyncMock(side_effect=RuntimeError("db"))
    await agent._run_sleep_consolidation()
    agent._memory.decay_importance_async.assert_awaited_once()
    agent._memory.expire_working_memory_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_distillation_caps_at_three_facts(tmp_path):
    agent = _job_agent(tmp_path)
    agent._utility_backend.complete = AsyncMock(
        return_value="\n".join(f"fact-{i}: text {i}" for i in range(6))
    )
    await agent._run_sleep_consolidation()
    assert agent._memory.upsert_semantic_fact_async.await_count == 3


# ── Dream mode (cut-line) ──


def _dream_coalition():
    from familiar_neighbor.mind.workspace import Coalition

    return Coalition(
        source="default_mode",
        summary="the balcony at dusk",
        activation=0.6,
        urgency=0.1,
        novelty=0.4,
        context_block="[DMN] Spontaneous recall: the balcony at dusk",
    )


@pytest.mark.asyncio
async def test_dream_cycles_journal_with_dream_kind(tmp_path):
    agent = _job_agent(tmp_path, dream=True)
    agent._inner_backend = MagicMock()  # dreams require the small model
    agent._dmn.wander = AsyncMock(return_value=_dream_coalition())
    agent._verbalize_focus = AsyncMock(return_value="a quiet balcony, the city humming")
    await agent._run_sleep_consolidation()
    assert agent._memory.save_async.await_count == 3  # K=3 cycles
    kwargs = agent._memory.save_async.await_args.kwargs
    assert kwargs["kind"] == "dream"
    agent._verbalize_focus.assert_awaited_with(_dream_coalition(), bypass_rate_limit=True)


@pytest.mark.asyncio
async def test_no_dreams_when_flag_off(tmp_path):
    agent = _job_agent(tmp_path, dream=False)
    agent._dmn.wander = AsyncMock(return_value=_dream_coalition())
    await agent._run_sleep_consolidation()
    agent._memory.save_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_dream_stops_when_dmn_dry(tmp_path):
    agent = _job_agent(tmp_path, dream=True)
    agent._dmn.wander = AsyncMock(return_value=None)
    await agent._run_sleep_consolidation()
    agent._memory.save_async.assert_not_awaited()


# ── Memory wrappers (real store) ──


def test_upsert_semantic_fact_public_wrapper_writes_revisions(tmp_path):
    from unittest.mock import patch

    from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel

    with patch.object(_EmbeddingModel, "pre_warm"):
        store = ObservationMemory(db_path=str(tmp_path / "obs.db"))
    try:
        store.upsert_semantic_fact("night:test", "fact one", confidence=0.55)
        store.upsert_semantic_fact("night:test", "fact two", confidence=0.6)
        facts = store.recall_semantic_facts("", n=5)
        assert any(f["key"] == "night:test" for f in facts)
    finally:
        store.close()


def test_expire_working_memory_deletes_stale_rows(tmp_path):
    from unittest.mock import patch

    from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel

    with patch.object(_EmbeddingModel, "pre_warm"):
        store = ObservationMemory(db_path=str(tmp_path / "obs.db"))
    try:
        with store._db_lock:
            db = store._ensure_connected()
            for mid in ("m1", "m2"):
                db.execute(
                    "INSERT INTO observations (id, content, timestamp, date, time) "
                    "VALUES (?, 'x', '2020-01-01T00:00:00', '2020-01-01', '00:00')",
                    (mid,),
                )
            db.execute(
                "INSERT INTO memory_activation (id, memory_id, activation, activated_at) "
                "VALUES ('a1', 'm1', 0.5, '2020-01-01T00:00:00')"
            )
            db.execute(
                "INSERT INTO memory_activation (id, memory_id, activation, activated_at) "
                "VALUES ('a2', 'm2', 0.5, ?)",
                (datetime.now().isoformat(),),
            )
            db.commit()
        assert store.expire_working_memory(days=2.0) == 1
    finally:
        store.close()


# ── Review-round regressions ──


def test_gate_and_job_agree_on_configured_quiet_end():
    """quiet_hours_end=9: inside the 07:00-09:00 window the gate (with the
    configured hour threaded through) must compute the SAME night key the job
    marked — or it re-spawns the job on every tick for two hours."""
    now = datetime(2026, 7, 3, 8, 30)  # still quiet with end_hour=9
    job_key = night_key_for(now, quiet_end_hour=9)
    assert not should_run_sleep_consolidation(
        enabled=True,
        agent_running=False,
        has_pending_input=False,
        quiet_hours=True,
        now_dt=now,
        last_night_key=job_key,
        quiet_end_hour=9,  # the call sites must thread this
    )
    # The old bug: gate at default 7 diverges and would re-fire.
    assert night_key_for(now, quiet_end_hour=7) != job_key


def test_start_sleep_consolidation_is_single_flight(tmp_path):
    import asyncio

    async def scenario():
        agent = _job_agent(tmp_path)
        never_done = asyncio.get_event_loop().create_future()

        async def hang():
            await never_done

        agent._run_sleep_consolidation = hang  # type: ignore[method-assign]
        agent._background_tasks = set()
        agent.start_sleep_consolidation()
        agent.start_sleep_consolidation()  # second spawn must be refused
        count = sum(1 for t in agent._background_tasks if t.get_name() == "sleep-consolidation")
        for t in agent._background_tasks:
            t.cancel()
        return count

    assert asyncio.run(scenario()) == 1


def test_recall_excludes_dreams_by_default(tmp_path):
    from unittest.mock import patch

    from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel

    with patch.object(_EmbeddingModel, "pre_warm"):
        store = ObservationMemory(db_path=str(tmp_path / "obs.db"))
    try:
        store.save("the balcony at dusk, city humming", kind="observation")
        store.save("a dream of the balcony at dusk", kind="dream")
        general = store.recall("balcony dusk", n=5)
        assert general and all(r["kind"] != "dream" for r in general)
        dreams = store.recall("balcony", n=5, kind="dream")
        assert dreams and all(r["kind"] == "dream" for r in dreams)
    finally:
        store.close()


def test_find_near_duplicates_ignores_dreams(tmp_path):
    from unittest.mock import patch

    from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel

    with patch.object(_EmbeddingModel, "pre_warm"):
        store = ObservationMemory(db_path=str(tmp_path / "obs.db"))
    try:
        store.save("identical text about the desk lamp", kind="observation")
        store.save("identical text about the desk lamp", kind="dream")
        pairs = store.find_near_duplicates(threshold=0.99)
        assert pairs == []  # a dream can never evict the real memory
    finally:
        store.close()


def test_recall_recent_by_kind_orders_by_recency(tmp_path):
    from unittest.mock import patch

    from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel

    with patch.object(_EmbeddingModel, "pre_warm"):
        store = ObservationMemory(db_path=str(tmp_path / "obs.db"))
    try:
        store.save("old dream", kind="dream", override_date="2026-06-01")
        store.save("new dream", kind="dream")
        recent = store.recall_recent_by_kind("dream", 1)
        assert recent[0]["content"] == "new dream"
    finally:
        store.close()


def test_dream_cycles_require_inner_backend(tmp_path):
    import asyncio

    agent = _job_agent(tmp_path, dream=True)
    agent._inner_backend = None
    agent._dmn.wander = AsyncMock(return_value=_dream_coalition())
    assert asyncio.run(agent._run_dream_cycles()) == 0
    agent._memory.save_async.assert_not_awaited()


@pytest.mark.asyncio
async def test_distillation_parser_strips_bullets_and_bold(tmp_path):
    agent = _job_agent(tmp_path)
    agent._utility_backend.complete = AsyncMock(
        return_value="- tuesday-rhythm: works late Tuesdays\n**lighting**: lamp stays on"
    )
    await agent._run_sleep_consolidation()
    keys = [c.args[0] for c in agent._memory.upsert_semantic_fact_async.await_args_list]
    assert "night:tuesday-rhythm" in keys
    assert "night:lighting" in keys


# ── Config ──


def test_config_flags_off_by_default(monkeypatch):
    monkeypatch.delenv("FAMILIAR_SLEEP_CONSOLIDATION", raising=False)
    monkeypatch.delenv("FAMILIAR_DREAM", raising=False)
    from familiar_agent.config import AgentConfig

    cfg = AgentConfig()
    assert cfg.sleep_consolidation is False
    assert cfg.dream_mode is False


def test_utility_backend_honors_base_url_override(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("UTILITY_PLATFORM", "openai")
    monkeypatch.setenv("UTILITY_API_KEY", "ollama")
    monkeypatch.setenv("UTILITY_MODEL", "gemma4:latest")
    monkeypatch.setenv("UTILITY_BASE_URL", "http://localhost:11434/v1")
    from familiar_agent.backend import create_utility_backend
    from familiar_agent.config import AgentConfig

    backend = create_utility_backend(AgentConfig())
    assert backend is not None
    assert "localhost:11434" in str(backend.client.base_url)


def test_utility_backend_defaults_to_openai_without_override(monkeypatch):
    pytest.importorskip("openai")
    monkeypatch.setenv("UTILITY_PLATFORM", "openai")
    monkeypatch.setenv("UTILITY_API_KEY", "sk-x")
    monkeypatch.delenv("UTILITY_BASE_URL", raising=False)
    from familiar_agent.backend import create_utility_backend
    from familiar_agent.config import AgentConfig

    backend = create_utility_backend(AgentConfig())
    assert backend is not None
    assert "api.openai.com" in str(backend.client.base_url)
