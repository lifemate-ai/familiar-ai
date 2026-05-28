"""Interoception bridge — provider collection plus semantic pressure mapping."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path
import time
from typing import Protocol

from .mental_state import InteroceptiveSignal


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(slots=True, frozen=True)
class InteroceptivePressure:
    need_rest: float
    caution: float
    expressivity: float
    social_receptivity: float
    frustration_bias: float
    quiet_mode: bool


class InteroceptionProvider(Protocol):
    def collect(self) -> InteroceptiveSignal:
        """Collect current interoceptive signal."""


class NoopInteroceptionProvider:
    def collect(self) -> InteroceptiveSignal:
        return InteroceptiveSignal(
            provider="noop",
            observed_at=datetime.utcnow().isoformat(),
        )


class RuntimeInteroceptionProvider:
    """Derive semantic body signal from runtime facts only."""

    def __init__(
        self,
        *,
        started_at: float | None = None,
        turn_count: int = 0,
        pending_tasks: int = 0,
        quiet_hours: tuple[int, int] = (23, 7),
    ) -> None:
        self._started_at = started_at or time.time()
        self._turn_count = turn_count
        self._pending_tasks = pending_tasks
        self._quiet_hours = quiet_hours

    def collect(self) -> InteroceptiveSignal:
        now = datetime.now()
        hour = now.hour
        quiet = hour >= self._quiet_hours[0] or hour < self._quiet_hours[1]
        uptime_minutes = max(0.0, (time.time() - self._started_at) / 60.0)
        cognitive_load = _clamp01((self._pending_tasks * 0.15) + min(uptime_minutes / 240.0, 0.35))
        energy = 0.68
        if quiet:
            energy -= 0.23
        if uptime_minutes > 180:
            energy -= 0.15
        if self._turn_count > 12:
            energy -= 0.08
        body_stress = _clamp01(cognitive_load * 0.7 + (0.15 if quiet else 0.0))
        social_openness = _clamp01(0.58 - (0.18 if quiet else 0.0) - body_stress * 0.25)
        return InteroceptiveSignal(
            provider="runtime",
            observed_at=datetime.utcnow().isoformat(),
            local_hour=hour,
            quiet_hours=quiet,
            energy=_clamp01(energy),
            cognitive_load=cognitive_load,
            body_stress=body_stress,
            social_openness=social_openness,
            raw_metrics={
                "uptime_minutes": uptime_minutes,
                "pending_tasks": float(self._pending_tasks),
                "turn_count": float(self._turn_count),
            },
        )


class MCPInteroceptionProvider:
    """Optional lightweight MCP-style provider via JSON or JSONL handoff."""

    def __init__(
        self,
        payload_path: str | Path | None = None,
        *,
        max_staleness_seconds: int = 45,
    ) -> None:
        self._path = Path(payload_path).expanduser() if payload_path else None
        self._max_staleness_seconds = max(1, int(max_staleness_seconds))

    def _read_payload(self) -> dict | None:
        if self._path is None or not self._path.exists():
            return None
        try:
            text = self._path.read_text(encoding="utf-8").strip()
        except Exception:
            return None
        if not text:
            return None
        if self._path.suffix == ".jsonl":
            for line in reversed(text.splitlines()):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    payload = json.loads(stripped)
                except Exception:
                    continue
                if isinstance(payload, dict):
                    return payload
            return None
        try:
            payload = json.loads(text)
        except Exception:
            return None
        return payload if isinstance(payload, dict) else None

    def _payload_is_fresh(self, observed_at: str) -> bool:
        if not observed_at:
            return True
        try:
            observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        except ValueError:
            return True
        now = datetime.now(observed.tzinfo) if observed.tzinfo else datetime.utcnow()
        return observed >= now - timedelta(seconds=self._max_staleness_seconds)

    def collect(self) -> InteroceptiveSignal:
        payload = self._read_payload()
        if payload is None:
            return NoopInteroceptionProvider().collect()
        signal_payload = dict(payload.get("signal", payload))
        observed_at = str(
            signal_payload.get("observed_at")
            or signal_payload.get("timestamp")
            or payload.get("observed_at")
            or payload.get("timestamp")
            or datetime.utcnow().isoformat()
        )
        if not self._payload_is_fresh(observed_at):
            return NoopInteroceptionProvider().collect()
        return InteroceptiveSignal(
            provider="mcp",
            observed_at=observed_at,
            local_hour=int(signal_payload.get("local_hour", datetime.now().hour)),
            quiet_hours=bool(signal_payload.get("quiet_hours", False)),
            energy=_clamp01(signal_payload.get("energy", 0.5)),
            cognitive_load=_clamp01(signal_payload.get("cognitive_load", 0.3)),
            body_stress=_clamp01(signal_payload.get("body_stress", 0.2)),
            social_openness=_clamp01(signal_payload.get("social_openness", 0.5)),
            raw_metrics={
                str(k): float(v)
                for k, v in dict(signal_payload.get("raw_metrics", {})).items()
                if isinstance(v, (int, float))
            },
        )


def semantic_pressure(signal: InteroceptiveSignal) -> InteroceptivePressure:
    """Translate internal body signal into coarse behavioral pressure."""
    sanitized = signal.sanitized()
    need_rest = _clamp01((1.0 - sanitized.energy) * 0.75 + sanitized.body_stress * 0.25)
    caution = _clamp01(sanitized.body_stress * 0.6 + sanitized.cognitive_load * 0.4)
    expressivity = _clamp01(sanitized.energy * 0.55 + sanitized.social_openness * 0.45)
    if sanitized.quiet_hours:
        expressivity = _clamp01(expressivity * 0.55)
    social_receptivity = _clamp01(sanitized.social_openness - sanitized.body_stress * 0.15)
    frustration_bias = _clamp01(sanitized.cognitive_load * 0.55 + sanitized.body_stress * 0.45)
    return InteroceptivePressure(
        need_rest=need_rest,
        caution=caution,
        expressivity=expressivity,
        social_receptivity=social_receptivity,
        frustration_bias=frustration_bias,
        quiet_mode=sanitized.quiet_hours,
    )
