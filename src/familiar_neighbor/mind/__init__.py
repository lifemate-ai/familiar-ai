"""Compatibility re-exports for neighbor cognition modules.

The physical move of cognition modules is intentionally deferred; this package marks the intended
dependency direction while `familiar_agent.*` imports remain stable.
"""

from familiar_agent.attention_schema import AttentionSchema
from familiar_agent.concern_engine import ConcernEngine
from familiar_agent.default_mode import DefaultModeProcessor
from familiar_agent.desires import DesireSystem
from familiar_agent.meta_monitor import MetaMonitor
from familiar_agent.prediction import PredictionEngine
from familiar_agent.relationship import RelationshipTracker
from familiar_agent.scene import SceneTracker
from familiar_agent.self_narrative import SelfNarrative
from familiar_agent.self_state import SelfState
from familiar_agent.workspace import GlobalWorkspace

__all__ = [
    "AttentionSchema",
    "ConcernEngine",
    "DefaultModeProcessor",
    "DesireSystem",
    "GlobalWorkspace",
    "MetaMonitor",
    "PredictionEngine",
    "RelationshipTracker",
    "SceneTracker",
    "SelfNarrative",
    "SelfState",
]
