"""Sandbox policy primitives for process-like tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class SandboxPolicy:
    """Policy object for shell/process capabilities.

    The first implementation preserves the existing opt-in bash behavior while making the policy
    explicit for future supervision or sidecar work.
    """

    allow_bash: bool = False
    workdir: Path | None = None
    network: str = "inherit"
    max_timeout_seconds: int = 120
    allowed_commands: set[str] | None = None
    denied_commands: set[str] = field(default_factory=lambda: {"rm -rf /", "shutdown", "reboot"})
