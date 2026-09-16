# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

familiar-ai is an embodied AI companion: it sees through an ONVIF/RTSP camera, moves on a
Tuya robot vacuum, speaks via ElevenLabs TTS, listens via STT, and remembers in SQLite.
A ReAct loop (`agent.py`) drives a pluggable LLM backend; a set of cognitive modules
(workspace, self state, concerns, prediction, desires) feed context into every turn.
`AGENTS.md` is the short contributor guide; `docs/architecture.md` maps modules to the
"Neighbor Intelligence Stack" layers and is the best entry point for the cognitive side.

## Commands

```bash
uv sync                                   # install (dev, gui, camera, voice groups are default)
./run.sh            # or run.bat           # start (Textual TUI); ./run.sh --no-tui for plain REPL
uv run familiar --gui                     # PySide6 GUI

uvx ruff@0.15.3 check . && uvx ruff@0.15.3 format .   # pinned version: newer ruff flags pre-existing code
uv run --group dev mypy src/familiar_agent
uv run pytest -q                          # ~870 tests, ~15 s; pytest-asyncio for async tests
uv run pytest tests/test_ollama_backend.py -q          # single file
uv run pytest -k "social_reflex and camera" -q         # single test by keyword
uvx pre-commit install                    # ruff + ruff-format + mypy hooks

scripts/new_migration.sh add_thing        # → migration/YYYY-MM-DD-NNN_add_thing.py with upgrade(conn)
uv run python benchmarks/social_eval.py --profile compact --reflex on   # local-model social eval
uv run python benchmarks/run.py           # S-expr vs NL prompt comparison (needs API key)
uv run python benchmarks/neighbor_eval.py # intervention-policy replay eval, no LLM
```

Two tests are environment-dependent and fail on a stock macOS without ffmpeg / a Qt display
(`test_tts_no_ffmpeg.py::test_tts_payload_requests_pcm_format`,
`test_gui_async_stability.py::test_gui_idle_desire_logs_localized_murmur`).
Older TUI tests use `asyncio.get_event_loop()`; new async tests must use
`@pytest.mark.asyncio`, not `asyncio.run()`, or they break those tests when run in one session.

## Architecture: how a turn flows

1. `main.py` builds `AgentConfig` (all env-driven, `config.py`) and an `EmbodiedAgent`.
2. `EmbodiedAgent.run()` (agent.py) recalls memories, assembles the system prompt, then loops
   `backend.stream_turn()` → execute tool calls → append results, until `end_turn`.
3. **System prompt = (stable, variable) tuple** (`_system_prompt`). Stable = ME.md persona +
   rule set; variable = interoception, relationship, continuity, memories, plan, workspace
   broadcast. Anthropic caches the stable half; other backends join them with `---`.
4. **Post-response pipeline runs in the background** (`_run_post_response_pipeline`): emotion
   label, summary, self-model, scene, concerns, self-state, next-turn TAPE plan and workspace
   context are computed after the reply and cached for the next turn. Keep new work off the
   reply's critical path.
5. Tools live in `tools/` and each expose `get_tool_definitions()` + `call()`. To add one:
   implement it, register in `agent.py` (`_init_tools`, `_all_tool_defs`, `_execute_tool`,
   `_TOOL_TIMEOUTS`), and mention it in the prompt. MCP servers from `~/.familiar-ai.json`
   are merged in by `mcp_client.py`.

### Prompt profiles and small models (`prompt_profiles.py`, `social_reflex.py`)

- `full` = the S-expression `SYSTEM_PROMPT` in agent.py (frontier models).
- `compact` = short English, example-driven prompt for ~9B local models; auto-selected for
  `PLATFORM=ollama|cli` and local OpenAI-compatible URLs (`PROMPT_PROFILE` overrides).
- With the compact profile, **social reflex** is on: `classify_turn()` labels the utterance
  (venting, greeting, deflection, indirect request, disclosure, implicature, share_joy,
  visual request…). On social kinds the agent withholds `see/look/walk` from the model, ends
  the turn as soon as `say()` was called, strips hallucinated `<tool_code>`/stage directions,
  unwraps literal `say("…")` prose, and speaks say-less text. These are code guards, not
  prompt rules — 9B models do not follow abstract constraints.
- Measure any prompt/reflex change with `benchmarks/social_eval.py` before and after.
  Baseline 2026-09-17, qwen3.5:9b: full/off 63% → compact/on ≈85%.

### Backends (`backend.py`, `ollama_backend.py`)

`create_backend()` picks by `PLATFORM`: anthropic, gemini, openai (+`BASE_URL`), ollama,
kimi, glm, cli. Separate utility/scene backends (`UTILITY_PLATFORM`, `SCENE_PLATFORM`) handle
cheap side-calls and fall back to the main backend. Backends share an informal interface:
`make_user_message`, `make_assistant_message`, `make_tool_results`, `stream_turn`, `complete`.

Ollama specifics learned the hard way:
- Use `PLATFORM=ollama` (native `/api/chat`), not `/v1`. Default local model: `gemma4:12b-it-qat`. Via `/v1` you cannot set `num_ctx`
  (default 4096 → HTTP 500 "EOF" on long prompts) and qwen3.x always thinks unless
  `reasoning_effort=none` is sent. Prompt-mode `<tool_call>` JSON collides with Ollama's
  built-in qwen tool parser → use native tools.
- `THINKING_MODE=auto` means *no* thinking for local models (latency); `extended` turns it on.
- `OllamaBackend` retries once on Ollama's "XML syntax error" tool-parse glitch.

### Memory and persistence

- `tools/memory.py`: SQLite + `multilingual-e5-small` (CPU torch by default — don't switch to
  GPU builds). Schema changes go through `migration/` scripts applied at startup
  (`sqlite_migrations.py`, tracked in `schema_migrations`).
- `relationship.py`, `desires.py`, `intervention_policy.py`, `self_narrative.py` persist small
  JSON files under `~/.familiar_ai/`.
- `ME.md` (persona) is gitignored; `persona-template/*.md` are the starters. Set
  `FAMILIAR_EMBEDDING_PREWARM=0` in tests (conftest does).

## Conventions

- Always branch (`feat/...`, `fix/...`); never commit to `main`. Conventional Commits in
  English. Update `CHANGELOG.md` under `[Unreleased]` when behaviour changes.
- Python 3.10+, async-first, ruff line length 100, type hints on public functions.
- Camera and legs are separate devices: `walk()` never changes the camera view. Keep that
  true in any prompt or body description.
- Never hardcode API keys, hosts, or IPs; everything is in `.env` (see `.env.example`).
- UI strings go through `_i18n._t()` and `locales/*.json` (generated for ~70 languages);
  `README_ja.md` / `readme-l10n/` are generated by `scripts/translate_readme.py`.
- `dev/` holds Claude Code skills for this repo (`familiar-add-tool`, `familiar-check-env`,
  `familiar-debug-loop`).
