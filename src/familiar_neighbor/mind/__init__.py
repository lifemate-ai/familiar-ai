"""Neighbor cognition modules.

The classes here used to live under ``familiar_agent.<module>``; they were
re-located in PR-followup #2.  Compatibility shims at
``src/familiar_agent/<module>.py`` keep the old import paths working.
"""

from .attention_schema import AttentionSchema
from .concern_engine import ConcernEngine
from .default_mode import DefaultModeProcessor
from .desires import DesireSystem
from .mental_state import MentalStateBus
from .meta_monitor import MetaMonitor
from .person_model import PersonModelTracker
from .prediction import PredictionEngine
from .relationship import RelationshipTracker
from .scene import SceneTracker
from .self_narrative import SelfNarrative
from .self_state import SelfState
from .workspace import GlobalWorkspace

__all__ = [
    "AttentionSchema",
    "ConcernEngine",
    "DefaultModeProcessor",
    "DesireSystem",
    "GlobalWorkspace",
    "MentalStateBus",
    "MetaMonitor",
    "PersonModelTracker",
    "PredictionEngine",
    "RelationshipTracker",
    "SceneTracker",
    "SelfNarrative",
    "SelfState",
]
