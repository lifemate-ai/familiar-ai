"""Pragmatic read — one bounded utility call that reads what is *meant*.

Small local models answer the literal words ("あいつは器用やからな" → "そうやな、
器用やな"). With a thinking channel they read the implicature, but unbounded
thinking costs 60 s a turn. This module buys the same inference for ~2–3 s: a
separate, thinking-off call that runs the Gricean procedure once and returns
three short lines the main turn can lean on.

    implicature: <what the words imply about their state or want>
    act: <one label from SPEECH_ACT_VOCABULARY>
    move: <the right kind of reply, one clause>

Deterministic layers stay authoritative: ``act`` is only a *hint* (ADR 0004
zones), and the read is advisory prompt text, never a gate.
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Any

from .social_policy import SPEECH_ACT_VOCABULARY

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_S = 6.0
MAX_TOKENS = 120

_PROMPT = """\
You are reading one utterance from the person you live with. Do not reply to them.
Run this quickly:
1. LITERAL — what the words say.
2. MAXIM — is a Gricean maxim flouted (quantity: trails off / says too little;
   quality: says what they cannot mean, e.g. "it's fine" when it is not;
   relation: a non-sequitur, e.g. praising someone else's talent when their own
   result is the topic; manner: vague or indirect)? A flout is deliberate: it IS
   the message.
3. IMPLICATURE — what it implies about their state or want.
4. ACT — one label from: {vocabulary}.
5. MOVE — the right kind of reply (receive the feeling / grant the indirect
   request / one-line greeting / share the joy / remember it / look where they
   point). Never advice unless asked.

Answer in exactly three lines, in the person's language for the free text:
implicature: ...
act: <label>
move: ...

Utterance: {utterance}"""

_LINE_RE = re.compile(r"^\s*(implicature|act|move)\s*[:：]\s*(.+?)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class PragmaticRead:
    implicature: str
    act: str | None
    move: str

    def prompt_lines(self) -> list[str]:
        lines = []
        if self.implicature:
            lines.append(f"- implicature: {self.implicature}")
        if self.move:
            lines.append(f"- move: {self.move}")
        return lines


def parse_pragmatic_read(raw: str) -> PragmaticRead | None:
    fields: dict[str, str] = {}
    for line in (raw or "").splitlines():
        m = _LINE_RE.match(line.replace("*", ""))
        if m:
            fields[m.group(1).lower()] = m.group(2).strip().strip('"').strip("'")
    if not fields.get("implicature") and not fields.get("move"):
        return None
    act = (fields.get("act") or "").lower().strip()
    return PragmaticRead(
        implicature=fields.get("implicature", "")[:160],
        act=act if act in SPEECH_ACT_VOCABULARY else None,
        move=fields.get("move", "")[:120],
    )


async def pragmatic_read(
    backend: Any,
    utterance: str,
    *,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> PragmaticRead | None:
    """One bounded call; None on timeout, failure, or unparseable output."""
    text = (utterance or "").strip()
    if not text:
        return None
    prompt = _PROMPT.format(
        vocabulary=", ".join(sorted(SPEECH_ACT_VOCABULARY)), utterance=text[:300]
    )
    try:
        raw = await asyncio.wait_for(
            backend.complete(prompt, max_tokens=MAX_TOKENS), timeout=timeout_s
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("Pragmatic read failed: %s", exc)
        return None
    read = parse_pragmatic_read(raw)
    if read is None:
        logger.debug("Pragmatic read unparseable: %s", (raw or "")[:120])
    return read
