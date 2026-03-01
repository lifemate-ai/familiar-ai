# familiar-ai 🐾

**An AI that lives alongside you** — with eyes, voice, legs, and memory.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Available in 74 languages](./SUPPORTED_LANGUAGES.md)

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
- 🎙 **Listen** — hands-free voice input via ElevenLabs Realtime STT (opt-in)
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

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Or: `winget install astral-sh.uv`

### 2. Install ffmpeg

ffmpeg is **required** for camera image capture and audio playback.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — or download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verify: `ffmpeg -version`

### 3. Clone and install

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configure

```bash
cp .env.example .env
# Edit .env with your settings
```

**Minimum required:**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Your API key for the chosen platform |

**Optional:**

| Variable | Description |
|----------|-------------|
| `MODEL` | Model name (sensible defaults per platform) |
| `AGENT_NAME` | Display name shown in the TUI (e.g. `Yukine`) |
| `CAMERA_HOST` | IP address of your ONVIF/RTSP camera |
| `CAMERA_USER` / `CAMERA_PASS` | Camera credentials |
| `ELEVENLABS_API_KEY` | For voice output — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` to enable always-on hands-free voice input (requires `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Where to play audio: `local` (PC speaker, default) \| `remote` (camera speaker) \| `both` |
| `THINKING_MODE` | Anthropic only — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptive thinking effort: `high` (default) \| `medium` \| `low` \| `max` (Opus 4.6 only) |

### 5. Create your familiar

```bash
cp persona-template/en.md ME.md
# Edit ME.md — give it a name and personality
```

### 6. Run

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textual TUI (recommended)
./run.sh --no-tui    # Plain REPL
```

**Windows:**
```bat
run.bat              # Textual TUI (recommended)
run.bat --no-tui     # Plain REPL
```

---

## Choosing an LLM

> **Recommended: Kimi K2.5** — best agentic performance tested so far. Notices context, asks follow-up questions, and acts autonomously in ways other models don't. Priced similarly to Claude Haiku.

| Platform | `PLATFORM=` | Default model | Where to get key |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (the command) | — |

**Kimi K2.5 `.env` example:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` example:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` example:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # or gemini-2.5-pro for higher capability
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` example:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # optional: specify model
AGENT_NAME=Yukine
```

> **Note:** To disable local/NVIDIA models, simply don't set `BASE_URL` to a local endpoint like `http://localhost:11434/v1`. Use cloud providers instead.

**CLI tool `.env` example:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — no {}, prompt goes via stdin
```

---

## MCP Servers

familiar-ai can connect to any [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. This lets you plug in external memory, filesystem access, web search, or any other tool.

Configure servers in `~/.familiar-ai.json` (same format as Claude Code):

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user"]
    },
    "memory": {
      "type": "sse",
      "url": "http://localhost:3000/sse"
    }
  }
}
```

Two transport types are supported:
- **`stdio`**: launch a local subprocess (`command` + `args`)
- **`sse`**: connect to an HTTP+SSE server (`url`)

Override the config file location with `MCP_CONFIG=/path/to/config.json`.

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

Run `./run.sh` (macOS/Linux/WSL2) or `run.bat` (Windows) and start chatting. Add hardware as you go.

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

There are two playback destinations, controlled by `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC speaker (default)
TTS_OUTPUT=remote   # camera speaker only
TTS_OUTPUT=both     # camera speaker + PC speaker simultaneously
```

#### A) Camera speaker (via go2rtc)

Set `TTS_OUTPUT=remote` (or `both`). Requires [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Download the binary from the [releases page](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Place and rename it:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x required

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Create `go2rtc.yaml` in the same directory:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Use the local camera account credentials (not your TP-Link cloud account).

4. familiar-ai starts go2rtc automatically at launch. If your camera supports two-way audio (backchannel), voice plays from the camera speaker.

#### B) Local PC speaker

The default (`TTS_OUTPUT=local`). Tries players in order: **paplay** → **mpv** → **ffplay**. Also used as a fallback when `TTS_OUTPUT=remote` and go2rtc is unavailable.

| OS | Install |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (or `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — set `PULSE_SERVER=unix:/mnt/wslg/PulseServer` in `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — download and add to PATH, **or** `winget install ffmpeg` |

> If no audio player is available, speech is still generated — it just won't play.

### Voice input (Realtime STT)

Set `REALTIME_STT=true` in `.env` for always-on, hands-free voice input:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # same key as TTS
```

familiar-ai streams microphone audio to ElevenLabs Scribe v2 and auto-commits transcripts when you pause speaking. No button press required. Coexists with the push-to-talk mode (Ctrl+T).

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

---

## Contributing

familiar-ai is an open experiment. If any of this resonates with you — technically or philosophically — contributions are very welcome.

**Good places to start:**

| Area | What's needed |
|------|---------------|
| New hardware | Support for more cameras (RTSP, IP Webcam), microphones, actuators |
| New tools | Web search, home automation, calendar, anything via MCP |
| New backends | Any LLM or local model that fits the `stream_turn` interface |
| Persona templates | ME.md templates for different languages and personalities |
| Research | Better desire models, memory retrieval, theory-of-mind prompting |
| Documentation | Tutorials, walkthroughs, translations |

See [CONTRIBUTING.md](./CONTRIBUTING.md) for dev setup, code style, and PR guidelines.

If you're unsure where to start, [open an issue](https://github.com/lifemate-ai/familiar-ai/issues) — happy to point you in the right direction.

---

## License

[MIT](./LICENSE)
