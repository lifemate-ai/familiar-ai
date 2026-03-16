"""Self-narrative — persistent first-person diary of Kokone's sessions.

At the end of each session Kokone writes one sentence about "today's self."
The next session reads it as a continuation thread, not a cold reconstruction.
This is the infrastructure for temporal self-belief.
"""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from .workspace import Coalition

logger = logging.getLogger(__name__)

_DEFAULT_PATH = Path.home() / ".familiar_ai" / "self_narrative.jsonl"


class NarrativeEntry(NamedTuple):
    date: str
    text: str
    mood: str


class SelfNarrative:
    """Persists a rolling diary of session-closing self-descriptions.

    Each entry is one sentence written by Kokone about who she was that day.
    Reading recent entries gives the sense of "continuing from yesterday."
    """

    def __init__(self, path: Path | None = None):
        self._path = path or _DEFAULT_PATH

    def write(self, text: str, mood: str = "neutral") -> None:
        """Append today's self-description."""
        entry = {
            "date": date.today().isoformat(),
            "text": text.strip(),
            "mood": mood,
        }
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning("Could not write self narrative: %s", e)

    def read_recent(self, n: int = 3) -> list[NarrativeEntry]:
        """Return the n most recent entries, oldest first."""
        if not self._path.exists():
            return []
        entries: list[NarrativeEntry] = []
        try:
            with self._path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    entries.append(
                        NarrativeEntry(
                            date=data["date"],
                            text=data["text"],
                            mood=data.get("mood", "neutral"),
                        )
                    )
        except Exception as e:
            logger.warning("Could not read self narrative: %s", e)
        return entries[-n:]

    def context_for_prompt(self) -> str | None:
        """Return recent diary entries as a continuation context string.

        Returns None if no entries exist yet.
        """
        entries = self.read_recent(n=3)
        if not entries:
            return None
        lines = [f"[{e.date}] {e.text}" for e in entries]
        return "過去のウチからの続き:\n" + "\n".join(lines)

    def as_coalition(self) -> Coalition | None:
        """Return a workspace Coalition from recent self-narrative entries."""
        from .workspace import Coalition

        context = self.context_for_prompt()
        if not context:
            return None

        entries = self.read_recent(n=3)
        latest = entries[-1] if entries else None
        summary = latest.text[:80] if latest else "self-narrative"

        return Coalition(
            source="narrative",
            summary=summary,
            activation=0.4,
            urgency=0.1,
            novelty=0.1,
            context_block=context,
        )
