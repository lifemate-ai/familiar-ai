"""Reusable capabilities for familiar runtime profiles.

Each capability wraps an existing familiar-agent tool so the runtime can
register it through the standard :class:`ToolProvider` protocol. Hardware /
state setup remains the caller's responsibility — capabilities only adapt
the calling convention.
"""

from .camera import CameraCapability
from .coding import CodingCapability
from .commitments import CommitmentCapability
from .delegation import DelegationCapability
from .identity import IdentityAnchorCapability, IdentityCapability
from .mcp import MCPCapability
from .memory import MemoryCapability
from .mobility import MobilityCapability
from .narrative import NarrativeCapability
from .routines import RoutineCapability
from .self_ledger import SelfLedgerCapability
from .social_timeline import SocialTimelineCapability
from .tom import ToMCapability
from .voice import TextOnlyVoiceCapability, VoiceCapability

__all__ = [
    "CameraCapability",
    "CodingCapability",
    "CommitmentCapability",
    "DelegationCapability",
    "IdentityAnchorCapability",
    "IdentityCapability",
    "MCPCapability",
    "MemoryCapability",
    "MobilityCapability",
    "NarrativeCapability",
    "RoutineCapability",
    "SelfLedgerCapability",
    "SocialTimelineCapability",
    "ToMCapability",
    "TextOnlyVoiceCapability",
    "VoiceCapability",
]
