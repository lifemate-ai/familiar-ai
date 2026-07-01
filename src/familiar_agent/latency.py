"""Per-turn latency instrumentation — opt-in, dark by default.

The selfhood roadmap's latency audit had to be done by hand because nothing
records where a turn's wall-clock goes. This gives the critical path named
buckets (prepare / react_loop / finalize) and appends one JSON line per turn
to ``~/.familiar_ai/latency.jsonl`` when ``FAMILIAR_LATENCY=1``. Disabled,
every call is a cheap no-op — nothing on the hot path.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import time
from collections.abc import Iterator
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_LATENCY_PATH = Path.home() / ".familiar_ai" / "latency.jsonl"


class LatencyRecorder:
    """Named wall-clock buckets for one turn at a time."""

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        path: str | Path | None = None,
    ) -> None:
        if enabled is None:
            enabled = os.environ.get("FAMILIAR_LATENCY", "").strip().lower() in (
                "1",
                "true",
                "yes",
                "on",
            )
        self.enabled = bool(enabled)
        self._path = Path(path).expanduser() if path else DEFAULT_LATENCY_PATH
        self._buckets: dict[str, float] = {}
        self._counts: dict[str, int] = {}

    @contextlib.contextmanager
    def span(self, name: str) -> Iterator[None]:
        """Measure one named span; no-op when disabled."""
        if not self.enabled:
            yield
            return
        started = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - started
            self._buckets[name] = self._buckets.get(name, 0.0) + elapsed
            self._counts[name] = self._counts.get(name, 0) + 1

    def record(self, name: str, seconds: float) -> None:
        """Add an externally-measured duration to a bucket; no-op when disabled."""
        if not self.enabled:
            return
        self._buckets[name] = self._buckets.get(name, 0.0) + max(0.0, float(seconds))
        self._counts[name] = self._counts.get(name, 0) + 1

    def flush_turn(self, *, turn: int, extra: dict | None = None) -> None:
        """Append this turn's buckets as one JSON line and reset."""
        if not self.enabled:
            return
        buckets = self._buckets
        counts = self._counts
        self._buckets = {}
        self._counts = {}
        if not buckets:
            return
        record = {
            "ts": time.time(),
            "turn": turn,
            "total_sec": round(sum(buckets.values()), 4),
            "buckets_sec": {k: round(v, 4) for k, v in buckets.items()},
            "counts": counts,
        }
        if extra:
            record.update(extra)
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as exc:  # noqa: BLE001
            logger.debug("latency flush failed: %s", exc)
