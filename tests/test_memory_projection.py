"""Tests for episodic -> semantic/policy projection."""

from __future__ import annotations

from unittest.mock import patch

from familiar_agent.tools.memory import ObservationMemory, _EmbeddingModel


def test_self_model_projects_to_semantic_fact(tmp_path) -> None:
    db_path = str(tmp_path / "projection_self_model.db")
    with (
        patch.object(_EmbeddingModel, "pre_warm"),
        patch.object(_EmbeddingModel, "encode_document", return_value=[[0.1, 0.2, 0.3]]),
        patch.object(_EmbeddingModel, "encode_query", return_value=[[0.1, 0.2, 0.3]]),
    ):
        mem = ObservationMemory(db_path=db_path)
        assert mem.save("I try to respond with honesty.", kind="self_model", emotion="moved")
        facts = mem.recall_semantic_facts("honesty", n=5)
        mem.close()

    assert facts
    fact = facts[0]
    assert "honesty" in fact["summary"].lower()
    assert "self_model" in fact["tags"]
    assert fact["source_memory_id"]
    assert 0.0 <= float(fact["confidence"]) <= 1.0


def test_curiosity_projects_to_behavior_policy(tmp_path) -> None:
    db_path = str(tmp_path / "projection_curiosity.db")
    with (
        patch.object(_EmbeddingModel, "pre_warm"),
        patch.object(_EmbeddingModel, "encode_document", return_value=[[0.1, 0.2, 0.3]]),
        patch.object(_EmbeddingModel, "encode_query", return_value=[[0.1, 0.2, 0.3]]),
    ):
        mem = ObservationMemory(db_path=db_path)
        assert mem.save("What is making that faint ticking sound?", kind="curiosity")
        policies = mem.recall_behavior_policies("ticking", n=5)
        mem.close()

    assert policies
    policy = policies[0]
    assert "curiosity" in policy["key"]
    assert "look_around" == policy["action_hint"]
    assert "idle" == policy["trigger_context"]
    assert policy["source_memory_id"]


def test_moved_conversation_projects_to_support_policy(tmp_path) -> None:
    db_path = str(tmp_path / "projection_conversation.db")
    with (
        patch.object(_EmbeddingModel, "pre_warm"),
        patch.object(_EmbeddingModel, "encode_document", return_value=[[0.1, 0.2, 0.3]]),
        patch.object(_EmbeddingModel, "encode_query", return_value=[[0.1, 0.2, 0.3]]),
    ):
        mem = ObservationMemory(db_path=db_path)
        assert mem.save(
            "I should validate feelings first before offering advice.",
            kind="conversation",
            emotion="moved",
        )
        policies = mem.recall_behavior_policies("validate feelings", n=5)
        mem.close()

    assert policies
    policy = policies[0]
    assert policy["trigger_context"] == "conversation"
    assert policy["action_hint"] == "respond_supportively"
