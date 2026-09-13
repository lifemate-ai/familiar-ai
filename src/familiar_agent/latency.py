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
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_LATENCY_PATH = Path.home() / ".familiar_ai" / "latency.jsonl"


_USAGE_FIELDS: tuple[tuple[str, str], ...] = (
    ("input_tokens", "input_tokens"),
    ("output_tokens", "output_tokens"),
    ("cache_read_tokens", "cache_read_tokens"),
    ("cache_creation_tokens", "cache_creation_tokens"),
)


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
        self._usage: dict[str, int] = {}

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

    def note_model_call(self, result: Any) -> None:
        """Accumulate one model call's token usage (cache hits included)."""
        if not self.enabled:
            return
        usage = self._usage
        usage["model_calls"] = usage.get("model_calls", 0) + 1
        for key, attr in _USAGE_FIELDS:
            usage[key] = usage.get(key, 0) + int(getattr(result, attr, 0) or 0)

    def model_usage(self) -> dict[str, int]:
        """This turn's accumulated token usage (empty when no model call ran)."""
        return dict(self._usage)

    def flush_turn(self, *, turn: int, extra: dict | None = None) -> None:
        """Append this turn's buckets (and token usage) as one JSON line and reset."""
        if not self.enabled:
            return
        buckets = self._buckets
        counts = self._counts
        usage = self._usage
        self._buckets = {}
        self._counts = {}
        self._usage = {}
        if not buckets:
            return
        record: dict[str, Any] = {
            "ts": time.time(),
            "turn": turn,
            "total_sec": round(sum(buckets.values()), 4),
            "buckets_sec": {k: round(v, 4) for k, v in buckets.items()},
            "counts": counts,
        }
        record.update(usage)
        if extra:
            record.update(extra)
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as exc:  # noqa: BLE001
            logger.debug("latency flush failed: %s", exc)


def record_retry(agent: Any, kind: str) -> None:
    """Count one re-ask of ``kind`` (coherence / identity / reality / voice).

    Zero-duration on purpose — the count is the signal; the re-ask's own cost
    shows up as an extra ``model_call``. Silently ignored when the agent has
    no recorder or it is disabled.
    """
    recorder = getattr(agent, "_latency", None)
    if recorder is None or not getattr(recorder, "enabled", False):
        return
    recorder.record(f"retry:{kind}", 0.0)


class LatencyBackendProxy:
    """Thin proxy over a model backend that times each ``stream_turn``.

    Every other attribute is delegated untouched, so the substrate loop sees
    the same serialization surface. Only installed when the recorder is
    enabled — a disabled recorder leaves the raw backend on the loop.
    """

    def __init__(self, backend: Any, recorder: LatencyRecorder) -> None:
        self._backend = backend
        self._recorder = recorder

    def __getattr__(self, name: str) -> Any:
        return getattr(self._backend, name)

    async def stream_turn(self, *args: Any, **kwargs: Any) -> Any:
        stream_turn: Callable[..., Any] = self._backend.stream_turn
        with self._recorder.span("model_call"):
            result, raw_content = await stream_turn(*args, **kwargs)
        self._recorder.note_model_call(result)
        return result, raw_content


def instrument_backend(backend: Any, recorder: LatencyRecorder) -> Any:
    """Return ``backend`` wrapped for timing when ``recorder`` is enabled."""
    if not recorder.enabled:
        return backend
    return LatencyBackendProxy(backend, recorder)
