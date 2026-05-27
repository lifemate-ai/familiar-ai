from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel


def _memory(tmp_path: Path) -> ObservationMemory:
    with patch.object(_EmbeddingModel, "pre_warm"):
        return ObservationMemory(db_path=str(tmp_path / "memory.db"))


def test_memory_episodes_and_associative_recall_work(tmp_path: Path) -> None:
    mem = _memory(tmp_path)
    first_id, ok1 = mem.save_with_id("雨の散歩のことを覚えておく", kind="conversation")
    second_id, ok2 = mem.save_with_id("散歩中に古い喫茶店を見つけた", kind="observation")
    assert ok1 is True and ok2 is True
    assert first_id is not None and second_id is not None

    episode_id = mem.create_episode("雨の日の散歩", summary="雨の散歩と喫茶店の記憶")
    assert episode_id is not None
    assert mem.append_to_episode(episode_id, first_id) is True
    assert mem.append_to_episode(episode_id, second_id) is True
    assert mem.link_memories(first_id, second_id, link_type="related") is True

    recalled = mem.recall_divergent("雨 散歩", n=4)
    assert recalled
    assert any(item.get("memory_id") == second_id for item in recalled)
    assert any(item.get("episode_id") == episode_id for item in recalled)

    working = mem.refresh_working_memory("雨 散歩", n=4)
    assert working
    assert mem.get_working_memory()
    mem.close()


def test_conflicting_semantic_facts_create_revisions(tmp_path: Path) -> None:
    mem = _memory(tmp_path)
    with mem._db_lock:  # noqa: SLF001
        db = mem._ensure_connected()  # noqa: SLF001
        mem._upsert_semantic_fact_locked(
            db, "favorite_drink", "Coffee is the favorite", confidence=0.7
        )  # noqa: SLF001
        mem._upsert_semantic_fact_locked(
            db, "favorite_drink", "Tea is the favorite", confidence=0.8
        )  # noqa: SLF001
        db.commit()

    revisions = mem.recall_revisions(entity_type="semantic_fact", entity_key="favorite_drink")
    assert revisions
    assert revisions[0]["previous_text"] == "Coffee is the favorite"
    assert revisions[0]["new_text"] == "Tea is the favorite"
    mem.close()
