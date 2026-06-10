"""Deferred-topic detection — "後で話す" must not be lost.

A deterministic detector for the companion deferring a conversation topic
("その話はあとで", "また今度説明する"). Detected deferrals are recorded as
unfinished business so the surface/resolve machinery the agent already has
keeps the topic alive until the conversation returns to it.

Patterns require a communication verb after あとで/後で so that doing
something later ("あとでお風呂入る") is not mistaken for deferring a topic.
"""

from __future__ import annotations

import re

_DEFERRAL_PATTERNS = [
    r"(?:あとで|後で)(?:ゆっくり)?(?:話|説明|教え|言う|聞かせ|相談)",
    r"また今度",
    r"その(?:話|件)は(?:また|あとで|後で)",
    r"後日(?:話|説明|相談|連絡|改めて)",
    r"\btell you later\b",
    r"\btalk (?:about (?:it|this) )?(?:later|another time)\b",
    r"\banother time\b",
]

_COMPILED = [re.compile(p) for p in _DEFERRAL_PATTERNS]

# Prompt-block prefix used when recording; also used for dedup matching.
DEFERRAL_PREFIX = "deferred topic: "


def detect_deferral(user_input: str) -> str | None:
    """Return a bounded snippet when the input defers a topic, else None."""
    text = user_input.strip()
    if not text:
        return None
    lower = text.lower()
    if any(p.search(lower) for p in _COMPILED):
        return text[:120]
    return None
