"""Voice-loop guard for TTS -> realtime STT echo suppression."""

from __future__ import annotations

import re
import time
from collections import deque
from dataclasses import dataclass
from difflib import SequenceMatcher

_SUPPRESSION_WINDOW_SECS = 1.2
_FINGERPRINT_TTL_SECS = 15.0
_LOOP_WINDOW_SECS = 8.0
_LOOP_TRIGGER_COUNT = 3
_SIMILARITY_THRESHOLD = 0.88
_TAG_RE = re.compile(r"\[[^\[\]]+\]")


def _guard_now() -> float:
    """Return the monotonic clock used by the voice guard."""
    return time.monotonic()


def _normalize_voice_text(text: str) -> str:
    """Normalize spoken text for fuzzy self-echo detection."""
    normalized = _TAG_RE.sub(" ", text or "")
    normalized = normalized.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.strip(" 　。、！？…・「」『』（）()!?,.\"'")
    return normalized


@dataclass(frozen=True)
class VoiceGuardDecision:
    """Result of checking whether a transcript should be suppressed."""

    blocked: bool
    reason: str | None = None
    should_restart: bool = False


class VoiceLoopGuard:
    """Small state machine for preventing TTS from looping back into realtime STT."""

    def __init__(
        self,
        *,
        suppression_window_secs: float = _SUPPRESSION_WINDOW_SECS,
        fingerprint_ttl_secs: float = _FINGERPRINT_TTL_SECS,
        loop_window_secs: float = _LOOP_WINDOW_SECS,
        loop_trigger_count: int = _LOOP_TRIGGER_COUNT,
    ) -> None:
        self._suppression_window_secs = suppression_window_secs
        self._fingerprint_ttl_secs = fingerprint_ttl_secs
        self._loop_window_secs = loop_window_secs
        self._loop_trigger_count = loop_trigger_count
        self._speaking_count = 0
        self._suppressed_until = 0.0
        self._recent_tts_fingerprints: deque[tuple[str, float]] = deque()
        self._loop_fingerprint = ""
        self._loop_counter = 0
        self._loop_last_time = 0.0

    @property
    def speaking(self) -> bool:
        """True while TTS playback is active."""
        return self._speaking_count > 0

    @property
    def suppressed_until(self) -> float:
        """Monotonic timestamp until which self-echo suppression remains active."""
        return self._suppressed_until

    @property
    def gated(self) -> bool:
        """True while STT should be treated as gated by active or recent TTS."""
        return self.speaking or _guard_now() < self._suppressed_until

    @property
    def loop_counter(self) -> int:
        """Current watchdog counter for repeated self-echo candidates."""
        return self._loop_counter

    @property
    def recent_tts_fingerprints(self) -> tuple[str, ...]:
        """Recent normalized TTS fingerprints, newest last."""
        self._expire(_guard_now())
        return tuple(text for text, _ts in self._recent_tts_fingerprints)

    def on_tts_start(self, text: str) -> None:
        """Enter speaking mode before playback begins."""
        self._speaking_count += 1
        normalized = _normalize_voice_text(text)
        if normalized:
            self._remember_fingerprint(normalized, _guard_now())

    def on_tts_end(self, text: str, *, played: bool) -> None:
        """Exit speaking mode after playback, optionally arming the suppression window."""
        if self._speaking_count > 0:
            self._speaking_count -= 1
        now = _guard_now()
        normalized = _normalize_voice_text(text)
        if played and normalized:
            self._remember_fingerprint(normalized, now)
            self._suppressed_until = max(
                self._suppressed_until, now + self._suppression_window_secs
            )
        elif not self.speaking:
            self._suppressed_until = min(self._suppressed_until, now)

    def should_gate_partial(self, text: str) -> bool:
        """Return True when a partial transcript should be hidden while TTS is gated."""
        decision = self.check_transcript(text, count_for_watchdog=False)
        return decision.blocked

    def check_transcript(self, text: str, *, count_for_watchdog: bool = True) -> VoiceGuardDecision:
        """Decide whether a committed transcript should be suppressed."""
        normalized = _normalize_voice_text(text)
        if not normalized:
            self._reset_loop()
            return VoiceGuardDecision(blocked=False)

        now = _guard_now()
        self._expire(now)
        matches_recent = self._matches_recent_fingerprint(normalized)

        if self.speaking:
            should_restart = (
                self._register_loop_echo(normalized, now)
                if count_for_watchdog and matches_recent
                else False
            )
            return VoiceGuardDecision(
                blocked=True, reason="tts_active", should_restart=should_restart
            )

        if now < self._suppressed_until and matches_recent:
            should_restart = (
                self._register_loop_echo(normalized, now) if count_for_watchdog else False
            )
            return VoiceGuardDecision(
                blocked=True, reason="tts_suppression", should_restart=should_restart
            )

        self._reset_loop()
        return VoiceGuardDecision(blocked=False)

    def _expire(self, now: float) -> None:
        while self._recent_tts_fingerprints:
            _text, ts = self._recent_tts_fingerprints[0]
            if now - ts <= self._fingerprint_ttl_secs:
                break
            self._recent_tts_fingerprints.popleft()
        if now - self._loop_last_time > self._loop_window_secs:
            self._reset_loop()

    def _remember_fingerprint(self, normalized: str, now: float) -> None:
        self._recent_tts_fingerprints.append((normalized, now))
        self._expire(now)

    def _matches_recent_fingerprint(self, normalized: str) -> bool:
        for fingerprint, _ts in reversed(self._recent_tts_fingerprints):
            if normalized == fingerprint:
                return True
            if len(normalized) >= 8 and (normalized in fingerprint or fingerprint in normalized):
                return True
            if min(len(normalized), len(fingerprint)) < 4:
                continue
            ratio = SequenceMatcher(None, normalized, fingerprint).ratio()
            if ratio >= _SIMILARITY_THRESHOLD:
                return True
        return False

    def _register_loop_echo(self, normalized: str, now: float) -> bool:
        if (
            normalized == self._loop_fingerprint
            and now - self._loop_last_time <= self._loop_window_secs
        ):
            self._loop_counter += 1
        else:
            self._loop_fingerprint = normalized
            self._loop_counter = 1
        self._loop_last_time = now
        return self._loop_counter >= self._loop_trigger_count

    def _reset_loop(self) -> None:
        self._loop_fingerprint = ""
        self._loop_counter = 0
        self._loop_last_time = 0.0


_SHARED_VOICE_GUARD: VoiceLoopGuard | None = None


def get_shared_voice_guard() -> VoiceLoopGuard:
    """Return the process-wide voice guard shared by TTS and realtime STT."""
    global _SHARED_VOICE_GUARD
    if _SHARED_VOICE_GUARD is None:
        _SHARED_VOICE_GUARD = VoiceLoopGuard()
    return _SHARED_VOICE_GUARD
