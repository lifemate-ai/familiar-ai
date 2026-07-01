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
from .identity import IdentityCapability
from .mcp import MCPCapability
from .memory import MemoryCapability
from .mobility import MobilityCapability
from .self_ledger import SelfLedgerCapability
from .tom import ToMCapability
from .voice import VoiceCapability

__all__ = [
    "CameraCapability",
    "CodingCapability",
    "CommitmentCapability",
    "DelegationCapability",
    "IdentityCapability",
    "MCPCapability",
    "MemoryCapability",
    "MobilityCapability",
    "SelfLedgerCapability",
    "ToMCapability",
    "VoiceCapability",
]
