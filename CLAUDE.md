# familiar-ai — Developer Guide for Claude Code

## Project overview

familiar-ai is an AI companion agent that perceives the real world through cameras, moves on a robot vacuum, speaks via TTS, and remembers what it sees. It runs a ReAct loop powered by the Anthropic API.

## Repository structure

```
src/familiar_agent/
├── agent.py       # ReAct loop (main agent logic)
├── config.py      # Environment-based configuration
├── desires.py     # Desire system (autonomous behavior)
├── main.py        # CLI REPL entry point
└── tools/
    ├── camera.py  # ONVIF PTZ camera + RTSP capture
    ├── memory.py  # SQLite + multilingual-e5-small embeddings
    ├── mobility.py # Tuya robot vacuum control
    └── tts.py     # ElevenLabs TTS
```

## Key architectural decisions

- **Camera and legs are separate physical devices.** The camera is fixed (e.g., on a shelf or outdoor unit). Moving the robot vacuum does NOT change what the camera sees. The system prompt must always make this clear to the agent.
- **Memory uses SQLite + numpy embeddings** (not ChromaDB) for fast startup and lightweight deployment.
- **Embeddings use CPU-only torch** by default. Do not switch to GPU builds without good reason — most users won't have a GPU.
- **ME.md is gitignored.** It contains the user's personal persona. Never commit it.

## Commit messages

**Always in English.** Follow Conventional Commits:

```
feat: add USB microphone support
fix: handle ONVIF reconnect on timeout
docs: update camera setup instructions
chore: bump anthropic to 0.42.0
```

## Code style

- Python 3.10+
- Formatted with `ruff` (line length: 100)
- Async-first (`asyncio`)
- Run before committing:

```bash
uv run ruff check .
uv run ruff format .
```

## Adding a new tool

1. Implement in `src/familiar_agent/tools/<name>.py`
2. Add `get_tool_definitions()` and `call()` methods
3. Register in `agent.py` → `_init_tools()`, `_all_tool_defs`, `_execute_tool()`
4. Add the tool name to the system prompt description

## Environment variables

All configuration is via environment variables (see `.env.example`). Never hardcode API keys or IP addresses.
