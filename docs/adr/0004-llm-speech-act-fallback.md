# ADR 0004: LLM fallback for speech-act classification

## Status

Proposed

## Context

`SocialPolicyEngine._base_decision` classifies the companion's utterance into
one of ~17 speech acts using ordered regex pattern lists. A four-round,
reproduction-required audit (2026-06) found and fixed **51 wrong-register
misfires** — including inverted registers such as celebrating a tumor
diagnosis (腫瘍ができた → delight), comforting joy slang (最高すぎて死んだ →
grief), apologizing when thanked (この前の返事ありがとうな → repair), and
treating the most common workplace greeting as an exhaustion complaint
(お疲れ様です → fatigue). All 51 are pinned by regression tests in
`tests/test_social_policy.py`.

The audit did **not** run dry. The rounds converged on failure classes that
regular expressions cannot close:

1. **Unbounded lexicons** — ailment formations (虫歯/ものもらい/できもの…)
   can be netted by a locative frame (体部位+に…できた) but never enumerated.
2. **Reported speech** — やめろって言われた is a disclosure, やめろ is a
   boundary; the same surface token inverts meaning by quotation.
3. **Transitivity / direction** — 傷ついた (I was hurt) vs 友達を傷つけた
   (I hurt someone) vs 主人公が傷つくシーン (fiction).
4. **Concession and scope** — 疲れたけど最高の一日やった！ is joy;
   最高の誕生日になるはずやったのに is lament. Regex sees both tokens in both.
5. **Sarcasm** — 最高かよ is regex-detectable; "yay, another outage" is not.

Each class was patched for its reproduced instances, but the tail is
structural: these distinctions require parsing, not matching.

## Decision (proposed)

Keep the regex layer as the deterministic fast path, and add an **LLM
fallback** via the existing utility backend for exactly two situations:

1. **Fallthrough** — when no pattern matches and the turn lands in the
   `attuned`/`bid_for_connection` fallback *and* the utterance is substantive
   (length above a threshold, not a desire turn), ask the utility backend to
   pick the speech act from the fixed 17-act vocabulary (single completion,
   ~50 output tokens, strict JSON, 2s timeout, fallback to `attuned` on any
   failure).
2. **Conflict** — when two or more of {delight, venting/grief, repair,
   boundary} pattern groups match the same utterance (the mixed-sentiment /
   inversion-risk zone), let the LLM arbitrate instead of branch order.

The deterministic layer remains authoritative for everything else, so
existing tests and latency characteristics are unchanged for the common case.
The 51-case regression suite doubles as the evaluation set for the fallback
prompt.

Costs: one extra utility call on a minority of turns (estimated <15%; the
auto-ToM cooldown pattern from `embodied_hook._should_auto_tom` can rate-limit
identically). Risks: nondeterminism in the arbitration zone — mitigated by
keeping the regex verdict when the LLM call fails or returns an act outside
the vocabulary.

## Alternatives considered

- **Keep auditing regexes** — rounds produced 16 → 12 → 12 → 10 findings;
  the marginal round cost is constant while severity declines. Reasonable as
  maintenance, insufficient as a fix for classes 1–5.
- **Replace the classifier with the LLM entirely** — loses determinism,
  testability, and the zero-latency common path; the appraisal/policy layers
  were deliberately designed deterministic (see project development rules).
- **A small local classifier model** — attractive long-term, but adds a
  deployment dependency the utility backend already covers.

## Consequences

- `SocialPolicyEngine.decide()` would gain an optional async variant or a
  pre-computed `llm_act_hint` input (computed in `prepare_turn` alongside
  auto-ToM) so the engine itself stays synchronous and testable.
- The fallback prompt and act vocabulary become versioned artifacts pinned by
  the existing regression suite.
