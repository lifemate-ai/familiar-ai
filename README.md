# familiar-ai 🐾

**An AI that lives alongside you** — with eyes, voice, legs, and memory.

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
- 🧠 **Remember** — stores observations with semantic search (SQLite + embeddings)
- 💭 **Desire** — has its own internal drives that trigger autonomous behavior

## How it works

familiar-ai runs a [ReAct](https://arxiv.org/abs/2210.03629) loop powered by Claude (Anthropic). It perceives the world through tools, thinks about what to do next, and acts — just like a person would.

```
user input
  → think → act (camera / move / speak) → observe → think → ...
```

When idle, it acts on its own desires: curiosity, wanting to look outside, missing the person it lives with.

## Getting started

### Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- Anthropic API key
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
# Fill in your API keys and camera settings
```

### Create your familiar

```bash
cp persona-template/en.md ME.md
# Edit ME.md — give it a name and personality
```

### Run

```bash
uv run familiar
```

## Persona (ME.md)

Your familiar's personality lives in `ME.md`. This file is gitignored — it's yours alone.

See [`persona-template/en.md`](./persona-template/en.md) for an example, or [`persona-template/ja.md`](./persona-template/ja.md) for a Japanese version.

## Hardware

familiar-ai was built with off-the-shelf hardware:

| Part | What it does | Example |
|------|-------------|---------|
| Wi-Fi PTZ camera | Eyes + neck | Tapo C220 (~$30) |
| Robot vacuum | Legs | Any Tuya-compatible model |
| PC / Raspberry Pi | Brain | Anything that runs Python |

## License

[MIT](./LICENSE)
