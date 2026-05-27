"""Typed mental-state bus for compact closed-loop state persistence."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from .workspace import Coalition

MENTAL_STATE_PATH = Path.home() / ".familiar_ai" / "mental_state.jsonl"


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(slots=True)
class InteroceptiveSignal:
    provider: str = "noop"
    observed_at: str = ""
    local_hour: int = 12
    quiet_hours: bool = False
    energy: float = 0.5
    cognitive_load: float = 0.3
    body_stress: float = 0.2
    social_openness: float = 0.5
    raw_metrics: dict[str, float] = field(default_factory=dict)

    def sanitized(self) -> "InteroceptiveSignal":
        return InteroceptiveSignal(
            provider=self.provider,
            observed_at=self.observed_at,
            local_hour=int(self.local_hour),
            quiet_hours=bool(self.quiet_hours),
            energy=_clamp01(self.energy),
            cognitive_load=_clamp01(self.cognitive_load),
            body_stress=_clamp01(self.body_stress),
            social_openness=_clamp01(self.social_openness),
            raw_metrics={k: float(v) for k, v in self.raw_metrics.items()},
        )

    def prompt_summary(self) -> str:
        parts: list[str] = []
        if self.quiet_hours:
            parts.append("quiet-hours")
        if self.energy < 0.35:
            parts.append("low-energy")
        elif self.energy > 0.72:
            parts.append("energized")
        if self.cognitive_load > 0.7:
            parts.append("high-load")
        if self.body_stress > 0.65:
            parts.append("body-tense")
        if self.social_openness < 0.35:
            parts.append("socially-guarded")
        elif self.social_openness > 0.7:
            parts.append("socially-open")
        return ", ".join(parts) if parts else "steady"


@dataclass(slots=True)
class AffectiveState:
    valence: float = 0.0
    arousal: float = 0.0
    dominance: float = 0.0
    uncertainty: float = 0.0
    attachment_pull: float = 0.0
    threat: float = 0.0
    tenderness: float = 0.0
    frustration: float = 0.0
    loneliness: float = 0.0
    summary: str = ""

    def sanitized(self) -> "AffectiveState":
        return AffectiveState(
            valence=max(-1.0, min(1.0, float(self.valence))),
            arousal=_clamp01(self.arousal),
            dominance=max(-1.0, min(1.0, float(self.dominance))),
            uncertainty=_clamp01(self.uncertainty),
            attachment_pull=_clamp01(self.attachment_pull),
            threat=_clamp01(self.threat),
            tenderness=_clamp01(self.tenderness),
            frustration=_clamp01(self.frustration),
            loneliness=_clamp01(self.loneliness),
            summary=self.summary[:240],
        )

    def prompt_summary(self) -> str:
        labels: list[str] = []
        if self.summary:
            labels.append(self.summary)
        if self.threat > 0.55:
            labels.append("guarded")
        if self.frustration > 0.55:
            labels.append("frustrated")
        if self.tenderness > 0.55:
            labels.append("tender")
        if self.loneliness > 0.55:
            labels.append("lonely")
        if self.attachment_pull > 0.6:
            labels.append("pulled-toward-connection")
        if self.uncertainty > 0.6:
            labels.append("uncertain")
        if not labels:
            labels.append("even")
        return ", ".join(dict.fromkeys(labels))

    def as_coalition(self) -> Coalition | None:
        sanitized = self.sanitized()
        strength = max(
            abs(sanitized.valence),
            sanitized.arousal,
            sanitized.attachment_pull,
            sanitized.threat,
            sanitized.tenderness,
            sanitized.frustration,
            sanitized.loneliness,
        )
        if strength < 0.28:
            return None
        summary = sanitized.prompt_summary()
        urgency = max(sanitized.threat, sanitized.frustration, sanitized.loneliness)
        novelty = min(1.0, sanitized.uncertainty + abs(sanitized.valence) * 0.25)
        return Coalition(
            source="affect",
            summary=summary[:80],
            activation=_clamp01(strength),
            urgency=_clamp01(urgency),
            novelty=_clamp01(novelty),
            context_block=f"[Affective state]\n{summary}",
        )


@dataclass(slots=True)
class SocialState:
    primary_act: str = "silence_or_low_presence"
    response_mode: str = "attuned"
    trust: float = 0.5
    intimacy: float = 0.4
    repair_needed: bool = False
    recall_relational_memory: bool = False
    mention_memory: bool = False
    initiative: float = 0.3
    directness: float = 0.4
    softness: float = 0.6

    def sanitized(self) -> "SocialState":
        return SocialState(
            primary_act=self.primary_act,
            response_mode=self.response_mode,
            trust=_clamp01(self.trust),
            intimacy=_clamp01(self.intimacy),
            repair_needed=bool(self.repair_needed),
            recall_relational_memory=bool(self.recall_relational_memory),
            mention_memory=bool(self.mention_memory),
            initiative=_clamp01(self.initiative),
            directness=_clamp01(self.directness),
            softness=_clamp01(self.softness),
        )

    def prompt_summary(self) -> str:
        sanitized = self.sanitized()
        tags = [
            f"act={sanitized.primary_act}",
            f"mode={sanitized.response_mode}",
        ]
        if sanitized.repair_needed:
            tags.append("repair-needed")
        if sanitized.recall_relational_memory:
            tags.append("recall-relationship")
        return ", ".join(tags)


@dataclass(slots=True)
class DriveVector:
    levels: dict[str, float] = field(default_factory=dict)
    dominant_drive: str | None = None
    dominant_level: float = 0.0

    def sanitized(self) -> "DriveVector":
        levels = {str(k): _clamp01(v) for k, v in self.levels.items()}
        dominant = self.dominant_drive
        dominant_level = (
            _clamp01(self.levels.get(dominant, self.dominant_level)) if dominant else 0.0
        )
        return DriveVector(levels=levels, dominant_drive=dominant, dominant_level=dominant_level)

    def prompt_summary(self, limit: int = 4) -> str:
        sanitized = self.sanitized()
        ranked = sorted(sanitized.levels.items(), key=lambda item: item[1], reverse=True)[:limit]
        return ", ".join(f"{name}:{level:.2f}" for name, level in ranked) if ranked else "none"


@dataclass(slots=True)
class WorkingMemoryItem:
    memory_id: str
    summary: str
    source_kind: str
    salience: float = 0.5
    tags: tuple[str, ...] = ()
    episode_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def sanitized(self) -> "WorkingMemoryItem":
        return WorkingMemoryItem(
            memory_id=self.memory_id,
            summary=self.summary[:240],
            source_kind=self.source_kind,
            salience=_clamp01(self.salience),
            tags=tuple(self.tags[:8]),
            episode_id=self.episode_id,
            created_at=self.created_at,
        )


@dataclass(slots=True)
class MentalStateSnapshot:
    turn_index: int
    created_at: str
    interoception: InteroceptiveSignal
    affect: AffectiveState
    social: SocialState
    drives: DriveVector
    working_memory: list[WorkingMemoryItem] = field(default_factory=list)
    continuity_note: str = ""

    def sanitized(self) -> "MentalStateSnapshot":
        return MentalStateSnapshot(
            turn_index=int(self.turn_index),
            created_at=self.created_at,
            interoception=self.interoception.sanitized(),
            affect=self.affect.sanitized(),
            social=self.social.sanitized(),
            drives=self.drives.sanitized(),
            working_memory=[item.sanitized() for item in self.working_memory[:6]],
            continuity_note=self.continuity_note[:240],
        )

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self.sanitized())
        return data

    @classmethod
    def from_json_dict(cls, data: dict[str, Any]) -> "MentalStateSnapshot":
        return cls(
            turn_index=int(data.get("turn_index", 0)),
            created_at=str(data.get("created_at") or datetime.utcnow().isoformat()),
            interoception=InteroceptiveSignal(**dict(data.get("interoception", {}))),
            affect=AffectiveState(**dict(data.get("affect", {}))),
            social=SocialState(**dict(data.get("social", {}))),
            drives=DriveVector(**dict(data.get("drives", {}))),
            working_memory=[
                WorkingMemoryItem(**dict(item)) for item in list(data.get("working_memory", []))
            ],
            continuity_note=str(data.get("continuity_note", "")),
        )

    def prompt_summary(self) -> str:
        wm = ", ".join(item.summary[:48] for item in self.working_memory[:3])
        parts = [
            "[Mental state]",
            f"- interoception: {self.interoception.prompt_summary()}",
            f"- affect: {self.affect.prompt_summary()}",
            f"- social: {self.social.prompt_summary()}",
            f"- drives: {self.drives.prompt_summary()}",
        ]
        if wm:
            parts.append(f"- working-memory: {wm}")
        if self.continuity_note:
            parts.append(f"- continuity: {self.continuity_note[:160]}")
        return "\n".join(parts)


class MentalStateBus:
    """Append-only JSONL bus for compact mental-state snapshots."""

    def __init__(self, path: Path = MENTAL_STATE_PATH):
        self._path = path

    def append(self, snapshot: MentalStateSnapshot) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(snapshot.to_json_dict(), ensure_ascii=False, separators=(",", ":"))
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def recent(self, n: int = 5) -> list[MentalStateSnapshot]:
        if not self._path.exists() or n <= 0:
            return []
        lines = self._path.read_text(encoding="utf-8").splitlines()[-n:]
        snapshots: list[MentalStateSnapshot] = []
        for line in lines:
            try:
                snapshots.append(MentalStateSnapshot.from_json_dict(json.loads(line)))
            except Exception:
                continue
        return snapshots

    def summarize_recent_for_prompt(self, n: int = 3) -> str:
        snapshots = self.recent(n)
        if not snapshots:
            return ""
        lines = ["[Recent mental continuity]"]
        for snap in snapshots:
            lines.append(
                f"- turn {snap.turn_index}: {snap.affect.prompt_summary()} | "
                f"{snap.social.prompt_summary()} | {snap.drives.prompt_summary(limit=3)}"
            )
        return "\n".join(lines)
