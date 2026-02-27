# Contributing to familiar-ai

familiar-ai is an open experiment in giving AI a physical presence — eyes, voice, legs, memory, and something like desires. If that sounds interesting to you, welcome.

## What we're exploring

- **Embodied cognition** — does grounding an LLM in real-world perception change how it behaves?
- **Autonomous behavior** — internal drive systems that make the agent act without being asked
- **Persistent identity** — memory and self-model that survive across sessions
- **Accessible hardware** — anything that works, starting at $30

No background in robotics or ML required. If you can write Python and you find this interesting, you can contribute.

## What the project needs

| Area | Concrete ideas |
|------|----------------|
| **Hardware support** | More cameras (generic RTSP, IP Webcam app), microphones, smart home devices |
| **Tools** | Web search, calendar, home automation, anything via MCP server |
| **LLM backends** | New providers, better streaming, vision model support |
| **Persona templates** | ME.md starters for more languages and personality types |
| **Memory / cognition** | Better retrieval, episodic memory, curiosity-driven exploration |
| **Tests** | More coverage, integration tests, hardware mocks |
| **Docs & tutorials** | Setup walkthroughs, video guides, translations |

If you have an idea that doesn't fit the list, open an issue and let's talk.

## Development setup

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync

# Set up pre-commit hooks (runs ruff automatically before every commit)
uvx pre-commit install
```

## Before submitting a PR

```bash
uv run ruff check .        # lint
uv run ruff format .       # format
uv run pytest -v           # tests
```

All three must pass cleanly.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/) in **English**:

```
feat: add support for USB microphone input
fix: prevent camera reconnect loop on timeout
docs: clarify hardware requirements in README
chore: bump anthropic to 0.42.0
```

## Pull requests

- Keep PRs focused — one thing per PR
- Add tests for new behavior
- Update `CHANGELOG.md` under `[Unreleased]`

## Code style

- Python 3.10+, formatted with `ruff`
- Line length: 100
- Async-first (`asyncio`)

## Questions?

[Open an issue](https://github.com/lifemate-ai/familiar-ai/issues) — we're happy to help.
