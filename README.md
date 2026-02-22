# familiar-ai 🐾

**An AI that lives alongside you** — with eyes, voice, legs, and memory.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

[日本語版はこちら → README-ja.md](./README-ja.md)

---

familiar-ai is an AI companion that lives in your home.
Set it up in minutes. No coding required.

It perceives the real world through cameras, moves around on a robot body, speaks aloud, and remembers what it sees. Give it a name, write its personality, and let it live with you.

## What it can do

- 👁 **See** — captures images from a Wi-Fi PTZ camera or USB webcam
- 🔄 **Look around** — pans and tilts the camera to explore its surroundings
- 🦿 **Move** — drives a robot vacuum to roam the room
- 🗣 **Speak** — talks via ElevenLabs TTS
- 🧠 **Remember** — actively stores and recalls memories with semantic search (SQLite + embeddings)
- 🫀 **Theory of Mind** — takes the other person's perspective before responding
- 💭 **Desire** — has its own internal drives that trigger autonomous behavior

## How it works

familiar-ai runs a [ReAct](https://arxiv.org/abs/2210.03629) loop powered by your choice of LLM. It perceives the world through tools, thinks about what to do next, and acts — just like a person would.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

When idle, it acts on its own desires: curiosity, wanting to look outside, missing the person it lives with.

## Getting started

### Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- An API key (Anthropic, Google Gemini, or OpenAI)
- A camera (Wi-Fi PTZ or USB webcam)

### Install

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### Configure

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` |
| `API_KEY` | Your API key for the chosen platform |
| `MODEL` | Model name (optional — sensible defaults per platform) |
| `AGENT_NAME` | Display name shown in the TUI (e.g. `Yukine`) |
| `CAMERA_HOST` | IP address of your ONVIF/RTSP camera (optional) |
| `ELEVENLABS_API_KEY` | For voice output (optional) — [elevenlabs.io](https://elevenlabs.io/) |

For OpenAI-compatible local models (Ollama etc.), also set `BASE_URL`.

See [`.env.example`](./.env.example) for all options.

### Create your familiar

```bash
cp persona-template/en.md ME.md
# Edit ME.md — give it a name and personality
```

### Run

```bash
uv run familiar          # Textual TUI (default)
uv run familiar --no-tui # Plain REPL
```

## TUI

familiar-ai includes a terminal UI built with [Textual](https://textual.textualize.io/):

- Scrollable conversation history with live streaming text
- Tab-completion for `/quit`, `/clear`
- Interrupt the agent mid-turn by typing while it's thinking
- Conversation log auto-saved to `~/.cache/familiar-ai/chat.log` for easy copy-paste

## Persona (ME.md)

Your familiar's personality lives in `ME.md`. This file is gitignored — it's yours alone.

See [`persona-template/en.md`](./persona-template/en.md) for an example, or [`persona-template/ja.md`](./persona-template/ja.md) for a Japanese version.

## Supported LLM platforms

| Platform | `PLATFORM=` | Default model |
|----------|------------|---------------|
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` |
| Google Gemini | `gemini` | `gemini-2.5-flash` |
| OpenAI | `openai` | `gpt-4o-mini` |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — |
| Moonshot Kimi K2.5 | `kimi` | `kimi-k2.5` |

## Hardware

familiar-ai works with whatever hardware you have — or none at all.

| Part | What it does | Example | Required? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Eyes + neck | Tapo C220 (~$30) | **Recommended** |
| USB webcam | Eyes (fixed) | Any UVC camera | **Recommended** |
| Robot vacuum | Legs | Any Tuya-compatible model | No |
| PC / Raspberry Pi | Brain | Anything that runs Python | **Yes** |

> **A camera is strongly recommended.** Without one, familiar-ai can still talk — but it can't see the world, which is kind of the whole point.

Start with a PC, an API key, and a cheap webcam. Add more hardware as you go.

## FAQ

**Q: Does it work without a GPU?**
Yes. The embedding model (multilingual-e5-small) runs fine on CPU. A GPU will make it faster, but it's not required.

**Q: Can I use a camera other than Tapo?**
Any camera that supports ONVIF + RTSP should work. Tapo C220 is what we tested with.

**Q: Is my data sent anywhere?**
Images and observations are sent to your chosen LLM API for processing. Memories are stored locally in `~/.familiar_ai/`.

## License

[MIT](./LICENSE)
