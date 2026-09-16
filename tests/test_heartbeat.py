from __future__ import annotations

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from familiar_agent.heartbeat import HeartbeatRuntime
from familiar_agent.routines import QuietHoursRule, evaluate_routine_state, parse_schedule_config
from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel


def test_quiet_hours_suppress_intrusive_actions(tmp_path: Path) -> None:
    config = tmp_path / "schedule.conf"
    config.write_text("quiet_hours_start=22\nquiet_hours_end=7\n", encoding="utf-8")
    rule = parse_schedule_config(config)
    decision = evaluate_routine_state(rule, datetime(2026, 4, 15, 23, 30))

    assert decision.quiet_hours is True
    assert decision.schedule_multiplier < 1.0


def test_continuation_chain_carries_over_and_stops_at_max_depth(tmp_path: Path) -> None:
    db_path = tmp_path / "observations.db"
    with patch.object(_EmbeddingModel, "pre_warm"):
        memory = ObservationMemory(db_path=str(db_path))
        runtime = HeartbeatRuntime(memory=memory, quiet_rule=QuietHoursRule(), max_chain_depth=3)

        assert runtime.apply_status("CONTINUE:step-1").status == "CONTINUE:step-1"
        assert runtime.apply_status("CONTINUE:step-2").status == "CONTINUE:step-2"
        assert runtime.apply_status("CONTINUE:step-3").status == "CONTINUE:step-3"
        overflow = runtime.apply_status("CONTINUE:step-4")

        assert overflow.status == "DEFER:step-4"
        assert overflow.persisted_remainder is True
        open_items = memory.list_unfinished_business()
        assert len(open_items) == 1
        assert open_items[0]["summary"] == "step-4"
        memory.close()


def test_heartbeat_persists_continuation_state_across_restarts(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat.json"
    runtime = HeartbeatRuntime(
        quiet_rule=QuietHoursRule(),
        state_path=state_path,
        max_chain_depth=3,
    )
    runtime.apply_status("CONTINUE:follow-up tomorrow")

    restored = HeartbeatRuntime(
        quiet_rule=QuietHoursRule(),
        state_path=state_path,
        max_chain_depth=3,
    )

    assert "follow-up tomorrow" in restored.continuity_context_for_prompt()
