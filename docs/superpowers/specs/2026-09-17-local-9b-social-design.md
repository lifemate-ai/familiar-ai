# Local 9B social behaviour — design

Goal: make familiar-ai behave with recognisable sociality (turn toward bids, read
implicature, validate before advising, stay in persona register, don't interrogate,
don't reach for the camera on social utterances) when the conversation model is a
~9B Japanese-capable model served by Ollama (qwen3.5:9b, qwen3.8-9b-distill).

## Baseline findings (2026-09-17, qwen3.5:9b, thinking off, native tools)

- The 4.2k-token S-expression SYSTEM_PROMPT does not fit Ollama's default 4096 ctx
  and, even when it fits, produces no measurable improvement over persona-only.
- Prompt-mode `<tool_call>` JSON collides with Ollama's built-in qwen tool parser
  (HTTP 500 "EOF"). Native function calling is required.
- Via `/v1`, qwen3.5 always thinks unless `reasoning_effort: "none"` is sent;
  `num_ctx` cannot be set. The native `/api/chat` endpoint controls both.
- Behavioural failures: camera reflex on social turns, text instead of say(),
  literal reading of implicature, register drift (敬体/俺/女性語 mixed), rambling
  multi-question replies, fabricated visual detail, comparisons without memory.

## Components

1. `backend.py: OllamaBackend` (PLATFORM=ollama) — native `/api/chat`, streaming,
   native tools, images, `think` from THINKING_MODE, `options.num_ctx` from
   OLLAMA_NUM_CTX (default 16384). `complete()` also thinking-off.
   `OpenAICompatibleBackend` gains `reasoning_effort` passthrough and drops
   `reasoning` deltas. Utility/scene factories accept `ollama`.
2. `prompt_profiles.py` — `PROMPT_PROFILE=full|compact`. `compact` (auto for
   ollama/local) is a ~600-token natural-language prompt with concrete Japanese
   examples instead of abstract theory. Body block still generated from hardware.
3. `social_reflex.py` — deterministic pre-step classifier of the user utterance
   → `SocialTurn(kind, tools_allowed, max_sentences, camera_ok)`. On social kinds
   the tool set handed to the model excludes see/look/walk. Post-step guards:
   strip hallucinated `<tool_code>`/`<tool_call>` text, route say-less text to
   say() (auto_say on for compact profile), collapse multi-question rambles via
   a one-shot correction nudge.
4. `benchmarks/social_eval.py` — Japanese social scenarios with deterministic
   checks (say used / no camera on social turn / ≤2 sentences / ≤1 question /
   no unmemoried comparison / persona register) plus optional LLM judge.
   Runs against any PLATFORM; primary targets qwen3.5:9b and
   tobestyledintro/qwen3.8-9b-distill.

## Non-goals

- Changing behaviour for Anthropic/Gemini frontier backends (profile `full` stays default there).
- Fine-tuning.

## Results (benchmarks/social_eval.py, 12 scenarios, 106 checks)

| model | full/off (baseline) | compact/off | full/on | compact/on |
|---|---|---|---|---|
| qwen3.5:9b | 63% | 76% | 75% | 85% → 94% after share_joy / early-stop / say-unwrap fixes |
| tobestyledintro/qwen3.8-9b-distill | 60% (never calls say) | — | — | see below |

Remaining qualitative gaps seen in transcripts: occasional Chinese/English reply drift
(now caught by the language guard with one redo), fabricated comparisons on
"昨日と比べて" (no memory), and rambling on deflection turns.
