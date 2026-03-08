```markdown
# familiar-ai 🐾

**An AI that lives alongside you** — with eyes, voice, legs, and memory.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Available in 74 languages](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai হৈছে এটা AI সঙ্গী যিয়ে আপোনাৰ ঘৰতে থাকে। 
এইটো স্থাপন কৰিবলৈ মিনেটৰ ভিতৰতে। কোডিংৰ আৱশ্যকতা নাই।

এইয়া কেমেৰা আৰু মুভমেণ্টৰ পৰা আৰ্থিক সঞ্জাল সম্পন্ন কৰে, এক ৰ’বট শৰীৰত ঘূৰি ফুৰে, উচাং কৈ কথা কয়, আৰু কি চাৰা মনেৰে ৰাখে। ইয়াক এখন নাম দিয়ক, ইয়াৰ ব্যক্তিত্ব লিখক, আৰু ইয়াক আপোনাৰ সৈতে বসবাস কৰিবলৈ দিয়ক।

## What it can do

- 👁 **See** — Wi-Fi PTZ কেমেৰাৰ পৰা ছবিসমূহ গ্ৰহণ কৰে বা USB ৱেবকেম
- 🔄 **Look around** — কেমেৰাটো পেন আৰু টিল্ট কৰি চাৰিওফালৰ অনুসন্ধান কৰে
- 🦿 **Move** — ৰ’বট ভেকিউমটোৰে কোঠাটো বিচৰণ কৰে
- 🗣 **Speak** — ElevenLabs TTSৰ জৰিয়তে কথা কয়
- 🎙 **Listen** — ElevenLabs Realtime STTৰ জৰিয়তে হাত-ফ্ৰী ভয়চ ইনপুট (অপ্ট-ইন)
- 🧠 **Remember** — সক্ৰিয়ভাৱে স্মৃতি সঞ্চয় আৰু স্মৰণ কৰে ছেমাণ্টিক চাৰ্চ (SQLite + embeddings)
- 🫀 **Theory of Mind** — সঁহাৰি দিবৰ আগতে আনজনৰ দৃষ্টিভংগী গ্ৰহণ কৰে
- 💭 **Desire** — অন্তৰ অন্তৰ বেঢ়ি অহা বাহ্যিক আৱেগ থাকে যিয়ে স্বায়ত্তশাসিত আচৰণৰ কাৰণ হয়

## How it works

familiar-ai এটা [ReAct](https://arxiv.org/abs/2210.03629) লুপ চলায় যি আপোনাৰপৰা LLMৰ দ্বাৰা চালিত। ই সঁচা জগতটোক টুলৰ জৰিয়তে উপলব্ধি কৰে, কি কৰিব সেই বিষয়ে ভাবিবলৈৰ বাবে চিন্তা কৰে, আৰু কাম কৰে — ঠিক যেন ব্যক্তি কৰিলে।

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

নিৰব থাকিলে, ই নিজৰ ইচ্ছাৰ ওপৰত কাৰ্য কৰে: কৌতুহল, বাহিৰলৈ চাবলৈ ইচ্ছা, তাত থকা ব্যক্তিৰ অভাৱ।

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
অথবা: `winget install astral-sh.uv`

### 2. Install ffmpeg

ffmpeg হৈছে **আবশ্যক** কেমেৰা চিত্ৰ গ্ৰহণ আৰু অডিঅ’ প্লেবাকৰ বাবে।

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — অথবা [ffmpeg.org](https://ffmpeg.org/download.html) ত ডাউনলোড কৰক আৰু PATHত যোগ কৰক |
| Raspberry Pi | `sudo apt install ffmpeg` |

সत्यাপিত কৰক: `ffmpeg -version`

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
| `PLATFORM` | `anthropic` (ডিফল্ট) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | আপোনাৰ নিৰ্বাচিত প্লেটফৰ্মৰ বাবে API কী |

**Optional:**

| Variable | Description |
|----------|-------------|
| `MODEL` | মডেল নাম (প্ৰতিটো প্লেটফৰ্মৰ বাবে বোধগম্য ডিফল্ট) |
| `AGENT_NAME` | TUIত দেখুওৱা নাম (যেনে `Yukine`) |
| `CAMERA_HOST` | আপোনাৰ ONVIF/RTSP কেমেৰাৰ IP ঠিকনা |
| `CAMERA_USER` / `CAMERA_PASS` | কেমেৰা প্ৰমাণপত্ৰ |
| `ELEVENLABS_API_KEY` | কণ্ঠ্য আউটপুটৰ বাবে — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` হাত-ফ্ৰী ভয়চ ইনপুট সদায় সক্ষম কৰিবলৈ (আৱশ্যক `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | অডিঅ’ প্লে কৰাৰ স্থান: `local` (PC স্পীকাৰ, ডিফল্ট) \| `remote` (কেমেৰা স্পীকাৰ) \| `both` |
| `THINKING_MODE` | মাথো অন্তৰ-প্ৰধান — `auto` (ডিফল্ট) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | অভিযোজনাধীন চিন্তাৰ দৰাৰ: `high` (ডিফল্ট) \| `medium` \| `low` \| `max` (Opus 4.6 মাথো) |

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

> **Recommended: Kimi K2.5** — এতিয়ালৈ পৰ্যন্ত পৰীক্ষিত সৰ্বশ্ৰেষ্ঠ এজেন্টিক কাৰ্যক্ষমতা। পৰিপ্রেক্ষিত লক্ষ্য কৰে, অনুসৰণ কৰাৰ প্ৰশ্ন সোধে, আৰু অন্যান্য মডেলৰ দৰে স্বায়ত্তশাসিতভাবে কাৰ্য কৰে। Claude Haikuৰ লগত দাম সমান।

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

> **Note:** স্থানীয়/NVIDIA মডেল বন্ধ কৰিবলৈ, কেৱল `BASE_URL` এ স্থানীয় সমাপ্তি যেনে `http://localhost:11434/v1` ত স্থাপন নকৰা। একাধিক মেঘ প্ৰদানকাৰীৰ ব্যৱহাৰ কৰক।

**CLI tool `.env` example:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — no {}, prompt goes via stdin
```

---

## MCP Servers

familiar-ai যে কোনো [MCP (Model Context Protocol)](https://modelcontextprotocol.io) ছাৰ্ভাৰ সৈতে সংযোগিত হ’ব পাৰে। এইটো বাহ্যিক স্মৃতি, ফাইলছystem প্ৰৱেশ, ৱেব চাৰ্চ, বা আন যিকোনো টুল যুক্ত কৰিবলৈ অনুমতি দিয়ে।

ছাৰ্ভাৰসমূহ `~/.familiar-ai.json` ত কনফিগাৰ কৰক (Claude Codeৰ দৰে):

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

দুটা পৰিবহণ ধৰণ সমৰ্থিত হয়:
- **`stdio`**: স্থানীয় উপ-শ্ৰেণী আৰম্ভ কৰা (`command` + `args`)
- **`sse`**: HTTP+SSE ছাৰ্ভাৰত সংযোগ কৰা (`url`)

`MCP_CONFIG=/path/to/config.json` দিয়ে কনফিগাৰ ফাইলৰ স্থান সলনি কৰক।

---

## Hardware

familiar-ai কিছুমান হাৰ্ডওয়্যাৰ সহ কাম কৰিব পাৰে — নাইবা একো নোৱাৰে।

| Part | What it does | Example | Required? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Eyes + neck | Tapo C220 (~$30, Eufy C220) | **Recommended** |
| USB webcam | Eyes (fixed) | Any UVC camera | **Recommended** |
| Robot vacuum | Legs | Any Tuya-compatible model | No |
| PC / Raspberry Pi | Brain | Anything that runs Python | **Yes** |

> **এটা কেমেৰা দৃঢ়ভাৱে এইটো চাৰা।** একো নাথাকিলে, familiar-ai কথাবাৰ্তা কৰিব পাৰে — কিন্তু ই জগত চাবলৈ অক্ষম, যিটো সঁচাকৈয়ে সম্পূৰ্ণ মূলক।

### Minimal setup (no hardware)

মাত্ৰ চেষ্টা কৰিবলৈ বিচাৰে? আপোনাৰ এটা API কীৰ প্রয়োজন:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) বা `run.bat` (Windows) চলাও আৰু কথাৰ আৰম্ভণা কৰা। আপুনি হাৰ্ডৱেৰ যোগ কৰিব পাৰিব।

### Wi-Fi PTZ camera (Tapo C220)

1. Tapo এপত: **Settings → Advanced → Camera Account** — এটা স্থানীয় একাউণ্ট সৃষ্টি কৰক (TP-Link একাউণ্ট নহয়)
2. আপোনাৰ ৰাউটাৰৰ ডিভাইচ তালিকাত কেমেৰাৰ IP বিচাৰি পোৱা
3. `.env` ত সেট কৰক:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Wi-Fi Camera (Eufy C220)

[Eufy C220 on Amazon Japan](https://www.amazon.co.jp/dp/B0CQQQ5NZ1/)

> **Tested and confirmed working.** Follow these steps carefully — a few settings differ from Tapo.

1. In the Eufy Security app: go to the camera → **Settings → NAS(RTSP)** and enable it
2. Set **Authentication** to **Basic** (Digest authentication does NOT work)
3. Set a streaming username and password
4. Note the RTSP URL shown in the app (format: `rtsp://username:password@ip/live0`)
5. Set in `.env` — use the **full RTSP URL** as `CAMERA_HOST`:
   ```env
   CAMERA_HOST=rtsp://your-username:your-password@192.168.1.xxx/live0
   CAMERA_USERNAME=
   CAMERA_PASSWORD=
   ```
   Leave `CAMERA_USERNAME` and `CAMERA_PASSWORD` empty — credentials are already in the URL.

> **Note:** Eufy C220 allows only **one simultaneous RTSP connection**. Stop other apps connected to the camera before starting familiar-ai.


### Voice (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) ত এটা API কীৰ গ্ৰহণ কৰক
2. `.env` ত সেট কৰক:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # optional, uses default voice if omitted
   ```

দুখন প্লেবেক গন্তব্য আছে, `TTS_OUTPUT` দ্বাৰা নিয়ন্ত্ৰিত:

```env
TTS_OUTPUT=local    # PC speaker (default)
TTS_OUTPUT=remote   # camera speaker only
TTS_OUTPUT=both     # camera speaker + PC speaker simultaneously
```

#### A) Camera speaker (via go2rtc)

`TTS_OUTPUT=remote` (অথবা `both`) সেট কৰক। [go2rtc](https://github.com/AlexxIT/go2rtc/releases)ৰ আৱশ্যক:

1. [releases পৃষ্ঠাৰ পৰা](https://github.com/AlexxIT/go2rtc/releases) বাইন্যাৰী ডাউনলোড কৰক:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. স্থানান্তৰ আৰু নাম সলনি কৰক:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x আৱশ্যক

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. একে ডিৰেক্টৰী মুকলি `go2rtc.yaml` সৃষ্টি কৰক:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   স্থানীয় কেমেযাৰ একাউণ্ট প্ৰমাণপত্ৰ ব্যৱহাৰ কৰক (আপোনাৰ TP-Link মেঘ একাউণ্ট নহয়)।

4. familiar-ai আৰম্ভণিত go2rtc স্বয়ংক্ৰিয়ভাবে আৰম্ভ কৰে। যদি আপোনাৰ কেমেৰা দু-দিশৰ অডিঅ’ (পিছফালৰ চেনেল) সমৰ্থন কৰে, তেন্তে কণ্ঠ্য কেমেৰাৰ স্পীকাৰৰ পৰা বাজে।

#### B) Local PC speaker

ডিফল্ট (`TTS_OUTPUT=local`)। নিম্নলিখিত খেলুৱৈবোৰ চেষ্টা কৰে: **paplay** → **mpv** → **ffplay**। `TTS_OUTPUT=remote` আৰু go2rtc উপলব্ধ নহ’লে fallback হিচাপে ব্যবহাৰ কৰা হয়।

| OS | Install |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (বা `paplay` মাধ্যমে `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` ত `PULSE_SERVER=unix:/mnt/wslg/PulseServer` নিৰ্ধাৰণ কৰে |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — ডাউনলোড কৰক আৰু PATHত যোগ কৰক, **অথবা** `winget install ffmpeg` |

> যদি কোনো অডিও প্লেয়াৰ উপলব্ধ নহয়, তেন্তে বক্তৃতা এখন যি সৃষ্টি কৰা হৈছে — ই কেবল বাজিব নৱ।

### Voice input (Realtime STT)

`REALTIME_STT=true` `.env` ত ৰাখক হাত-ফ্ৰী ভয়চ ইনপুটৰ বাবে সদায় সক্ষম কৰিবলৈ:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # same key as TTS
```

familiar-ai মাইক্ৰোফোন অডিঅ’টো ElevenLabs Scribe v2লৈ ষ্ট্ৰীম কৰে আৰু আপুনি কথা বন্ধ কৰিবলৈ যেতিয়া স্বচালিতভাবে পাঠ্য কৰি দিছে। কোনো বুটামৰ চাপৰ প্ৰয়োজন নাই। ইটো চাপ-ৰ-তুমি মোডৰ সৈতে (Ctrl+T) একেলগে থাকিব।

---

## TUI

familiar-ai ৰ অন্তৰ্গত হৈছে [Textual](https://textual.textualize.io/)ৰ সৈতে নির্মিত এটা টাৰ্মিনেল UI:

- চলাই থকা কথোপকথন ইতিহাস সজীৱ ষ্ট্ৰীমিং টেক্সট
- `/quit`, `/clear`ৰ বাবে টাব-সম্পূৰ্ণতা
- আদায় কৰিছে তেখেত চিন্তা কৰি থকা কালসীমাৰ মাজত_agent আগতে ৰোকা দিয়া |
- **Conversation log** স্বয়ংক্ৰিয়ভাৱে `~/.cache/familiar-ai/chat.log` ত সংৰক্ষণ কৰা

লগটো আন এটা টাৰ্মিনেলত অনুসৰণ কৰিবলৈ (কপি-পেষ্টৰ বাবে উপকাৰী):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

আপোনাৰ familiarৰ ব্যক্তিত্ব `ME.md` ত আছে। এই ফাইলটো gitignored — এইটো কেৱল আপোনাৰ।

[`persona-template/en.md`](./persona-template/en.md) এটাৰ উদাহৰণৰ বাবে চাওক, অথবা [`persona-template/ja.md`](./persona-template/ja.md) জাপানী সংস্কৰণৰ বাবে।

---

## FAQ

**Q: কি GPU নোহোৱা অৱস্থাত ই কাজনা লাগে?**
হয়। এম্বেডিং মডেল (multilingual-e5-small) CPU ত ভালকৈ চলে। GPU ইটো ডাঙৰ কৰে কিন্তু আৱশ্যক নহয়।

**Q: কি মই Tapo বৰ একটি কেমেৰা ব‍্যৱহাৰ কৰিব পাৰিম?**
যিকোনো কেমেৰা যিয়ে ONVIF + RTSP সমৰ্থিত সেইটো কাম কৰিব। Tapo C220 হৈছে যাক আমি পৰীক্ষা কৰিছিল।

**Q: মোৰ তথ্য ক'লৈ ৱে কৰা হয়?**
ছবিসমূহ আৰু পাঠ্য আপোনাৰ নিৰ্বাচিত LLM APIলৈ প্ৰসেসিংৰ বাবে পাঠ কৰা হয়। স্মৃতিসমূহ স্থানীয়ভাৱে `~/.familiar_ai/`ত সংৰক্ষণ কৰা হয়।

**Q: এজেন্টে `（...）` লেখে কেনেকৈ?**
`ELEVENLABS_API_KEY` নিৰ্ধাৰিত হোৱা নিশ্চিত কৰক। ইয়াৰ অভাৱত, কণ্ঠ নিষিদ্ধ হয় আৰু এজেন্টে পাঠ্যত পাছে।

## Technical background

কৈছে কিদৰে এইটো কাজ কৰি থাকে? familiar-aiৰ পিছৰ গৱেষণা আৰু ডিজাইন সিদ্ধান্তৰ বাবে [docs/technical.md](./docs/technical.md) চাওক — ReAct, SayCan, Reflexion, Voyager, ইচ্ছাৰ ব্যৱস্থা, আৰু অধিক। 

---

## Contributing

familiar-ai হৈছে এটা মুক্ত পৰীক্ষা। যদি ইয়াৰ কোনোটা আপোনাৰ লগত দৰকাৰবাদে — প্ৰযুক্তিগত বা দাৰ্শনিক — অংশগ্ৰহণৰ বাবে বাচিগৰাকী।

**শুভ স্থানসমূহ আৰম্ভণীৰ বাবে:**

| Area | What's needed |
|------|---------------|
| New hardware | অধিক কেমেৰা (RTSP, IP Webcam), মাইক্ৰোফোন, আন্দোলনকাৰীক সমৰ্থন |
| New tools | ৱেব চাৰ্চ, গৃহ স্বায়ত্ত, কেলেণ্ডাৰ, MCPৰ জৰিয়তে যিকোনো |
| New backends | যিকোনো LLM বা স্থানীয় মডেল যিয়ে `stream_turn` ইন্টাৰফেছৰ সৈতে আৱদ্ধ |
| Persona templates | বেলেগ ভাষা আৰু ব্যক্তিত্বৰ বাবে ME.md টেমপ্লেট |
| Research | উন্নত ইচ্ছাৰ মডেল, স্মৃতি পুন:প্ৰাপ্তি, চিন্তা-ৰ তত্ত্ব |
| Documentation | টিউটোৰিয়েল, ৱাকথ্ৰে, অনুবাদ |

[CONTRIBUTING.md](./CONTRIBUTING.md) চাওক বাচিগৰাকীৰ সৈতে, কোড শৈলী, আৰু PR নির্দেশনাসমূহৰ পৰা।

যদি আপোনাৰ ক'ৰ পৰা আৰম্ভ কৰিব পৰা নাই, [এক ব্যৱস্থা খোলক](https://github.com/lifemate-ai/familiar-ai/issues) — আপোনাৰ দিশৰ বাবে খুশি।

---

## License

[MIT](./LICENSE)

[→ English README](../README.md)
```
