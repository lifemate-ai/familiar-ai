# familiar-ai 🐾

**An AI that lives alongside you** — with eyes, voice, legs, and memory.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

- [日本語](./README-ja.md)
- [中文](./README-zh.md)
- [繁體中文](./README-zh-TW.md)
- [Français](./README-fr.md)
- [Deutsch](./README-de.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

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

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and install

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your settings
```

**Minimum required:**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` |
| `API_KEY` | Your API key for the chosen platform |

**Optional:**

| Variable | Description |
|----------|-------------|
| `MODEL` | Model name (sensible defaults per platform) |
| `AGENT_NAME` | Display name shown in the TUI (e.g. `Yukine`) |
| `CAMERA_HOST` | IP address of your ONVIF/RTSP camera |
| `CAMERA_USER` / `CAMERA_PASS` | Camera credentials |
| `ELEVENLABS_API_KEY` | For voice output — [elevenlabs.io](https://elevenlabs.io/) |

### 4. Create your familiar

```bash
cp persona-template/en.md ME.md
# Edit ME.md — give it a name and personality
```

### 5. Run

```bash
./run.sh             # Textual TUI (recommended)
./run.sh --no-tui    # Plain REPL
```

---

## Choosing an LLM

> **Recommended: Kimi K2.5** — best agentic performance tested so far. Notices context, asks follow-up questions, and acts autonomously in ways other models don't. Priced similarly to Claude Haiku.

| Platform | `PLATFORM=` | Default model | Where to get key |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |

**Kimi K2.5 `.env` example:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

---

## Hardware

familiar-ai works with whatever hardware you have — or none at all.

| Part | What it does | Example | Required? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Eyes + neck | Tapo C220 (~$30) | **Recommended** |
| USB webcam | Eyes (fixed) | Any UVC camera | **Recommended** |
| Robot vacuum | Legs | Any Tuya-compatible model | No |
| PC / Raspberry Pi | Brain | Anything that runs Python | **Yes** |

> **A camera is strongly recommended.** Without one, familiar-ai can still talk — but it can't see the world, which is kind of the whole point.

### Minimal setup (no hardware)

Just want to try it? You only need an API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Run `./run.sh` and start chatting. Add hardware as you go.

### Wi-Fi PTZ camera (Tapo C220)

1. In the Tapo app: **Settings → Advanced → Camera Account** — create a local account (not TP-Link account)
2. Find the camera's IP in your router's device list
3. Set in `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Voice (ElevenLabs)

1. Get an API key at [elevenlabs.io](https://elevenlabs.io/)
2. Set in `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # optional, uses default voice if omitted
   ```
3. Voice plays through the camera's built-in speaker via go2rtc (auto-downloaded on first run)

**Local audio playback** (used as fallback, or when no camera speaker is configured) requires **mpv** or **ffplay**. mpv is recommended:

| OS | Install |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — download and add to PATH, **or** install ffmpeg: `winget install ffmpeg` |

> Without mpv or ffplay, familiar-ai can still generate speech — it just won't play it locally. Voice via camera speaker (go2rtc) is unaffected.

---

## TUI

familiar-ai includes a terminal UI built with [Textual](https://textual.textualize.io/):

- Scrollable conversation history with live streaming text
- Tab-completion for `/quit`, `/clear`
- Interrupt the agent mid-turn by typing while it's thinking
- **Conversation log** auto-saved to `~/.cache/familiar-ai/chat.log`

To follow the log in another terminal (useful for copy-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Your familiar's personality lives in `ME.md`. This file is gitignored — it's yours alone.

See [`persona-template/en.md`](./persona-template/en.md) for an example, or [`persona-template/ja.md`](./persona-template/ja.md) for a Japanese version.

---

## FAQ

**Q: Does it work without a GPU?**
Yes. The embedding model (multilingual-e5-small) runs fine on CPU. A GPU makes it faster but isn't required.

**Q: Can I use a camera other than Tapo?**
Any camera that supports ONVIF + RTSP should work. Tapo C220 is what we tested with.

**Q: Is my data sent anywhere?**
Images and text are sent to your chosen LLM API for processing. Memories are stored locally in `~/.familiar_ai/`.

**Q: Why does the agent write `（...）` instead of speaking?**
Make sure `ELEVENLABS_API_KEY` is set. Without it, voice is disabled and the agent falls back to text.

## Technical background

Curious about how it works? See [docs/technical.md](./docs/technical.md) for the research and design decisions behind familiar-ai — ReAct, SayCan, Reflexion, Voyager, the desire system, and more.

## License

[MIT](./LICENSE)
