# familiar-ai 🐾

**Usa ka AI nga nagpuyo uban kanimo** — nga adunay mata, tingog, mga tiil, ug hinumduman.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai usa ka AI nga kauban nga nagpuyo sa imong balay.
I-set up lang kini sa sulod sa pipila ka minuto. Wala nagkinahanglan og coding.

Kini nagtan-aw sa tinuod nga kalibutan pinaagi sa mga camera, nagalihok sa usa ka robot nga lawas, nagasulti nga nataran, ug nagahinumdom sa iyang nakit-an. Hatagi kini og ngalan, isulat ang personalidad niini, ug pasagdi kini nga mabuhi uban kanimo.

## Unsay mahimo niini

- 👁 **Tan-aw** — nagsagap og mga hulagway gikan sa usa ka Wi-Fi PTZ kamera o USB webcam
- 🔄 **Tan-aw palibot** — nagpaandar ug nagtilt sa kamera aron mag-imbestiya sa palibot
- 🦿 **Lihok** — nagmaneho sa usa ka robot vacuum aron maglibot sa kwarto
- 🗣 **Sulti** — nagasulti pinaagi sa ElevenLabs TTS
- 🎙 **Paminaw** — hands-free nga voice input pinaagi sa ElevenLabs Realtime STT (opt-in)
- 🧠 **Hinumdom** — aktibong nag-save ug nagkuha ug mga hinumduman gamit ang semantic search (SQLite + embeddings)
- 🫀 **Theory of Mind** — nagkuha sa panan-aw sa laing tawo sa dili pa motubag
- 💭 **Desire** — adunay kaugalingon nga internal drives nga nagpasikad sa autonomous nga pamatasan

## Giunsa kini nagtrabaho

familiar-ai nagdagan sa usa ka [ReAct](https://arxiv.org/abs/2210.03629) loop nga gikuha sa imong gipili nga LLM. Nakit-an niini ang kalibutan pinaagi sa mga galamiton, naghunahuna unsay sunod nga buhaton, ug naglihok — sama sa pagbuhat sa usa ka tawo.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Sa dihang idle, naglihok kini base sa kaugalingon nga mga tinguha: pagkurog, gusto nga tan-awon ang gawas, ug pagkahigut sa tawo nga iyang ginalingan.

## Pag-sugod

### 1. I-install ang uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. I-install ang ffmpeg

ang ffmpeg **gikinahanglan** alang sa pagkuha og mga hulagway gikan sa camera ug pag-playback sa audio.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — o i-download gikan sa [ffmpeg.org](https://ffmpeg.org/download.html) ug idugang sa PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Susiha: `ffmpeg -version`

### 3. Clone ug i-install

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. I-configure

```bash
cp .env.example .env
# Edit .env gamit ang imong mga setting
```

**Minimum nga gikinahanglan:**

| Variable | Deskripsyon |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Imong API key alang sa napiling platform |

**Opsyonal:**

| Variable | Deskripsyon |
|----------|-------------|
| `MODEL` | Ngalan sa modelo (sensible defaults per platform) |
| `AGENT_NAME` | Display name nga gipakita sa TUI (e.g. `Yukine`) |
| `CAMERA_HOST` | IP address sa imong ONVIF/RTSP nga camera |
| `CAMERA_USER` / `CAMERA_PASS` | Mga kredensyal sa camera |
| `ELEVENLABS_API_KEY` | Alang sa voice output — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` aron i-enable ang always-on hands-free voice input (nagkinahanglan og `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Asa magplay sa audio: `local` (PC speaker, default) \| `remote` (camera speaker) \| `both` |
| `THINKING_MODE` | Anthropic lang — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptive thinking effort: `high` (default) \| `medium` \| `low` \| `max` (Opus 4.6 lang) |

### 5. Paghimo sa imong familiar

```bash
cp persona-template/en.md ME.md
# Edit ME.md — hatagi kini og ngalan ug personalidad
```

### 6. Dagana

```bash
./run.sh             # Textual TUI (girekomenda)
./run.sh --no-tui    # Plain REPL
```

---

## Pagpili og LLM

> **Girekomenda: Kimi K2.5** — labing maayo nga agentic performance nga nasulayan sa pagkakaron. Nakabantay sa konteksto, nagpangutana og mga follow-up questions, ug naglihok autonomously sa mga paagi nga dili gibuot sa uban nga mga modelo. Presyo parehas sa Claude Haiku.

| Platform | `PLATFORM=` | Default model | Asa makakuha og key |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (the command) | — |

**Kimi K2.5 `.env` nga ehemplo:**
```env
PLATFORM=kimi
API_KEY=sk-...   # gikan sa platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` nga ehemplo:**
```env
PLATFORM=glm
API_KEY=...   # gikan sa api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` nga ehemplo:**
```env
PLATFORM=gemini
API_KEY=AIza...   # gikan sa aistudio.google.com
MODEL=gemini-2.5-flash  # o gemini-2.5-pro alang sa mas taas nga kakayahan
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` nga ehemplo:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # gikan sa openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opsyonal: pagtutok sa modelo
AGENT_NAME=Yukine
```

> **Nota:** Aron i-disable ang local/NVIDIA nga mga modelo, dili lang ipasetting `BASE_URL` sa lokal nga endpoint sama sa `http://localhost:11434/v1`. Gamita ang mga cloud providers imbis.

**CLI tool `.env` nga ehemplo:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — walay {}, prompt moagi pinaagi sa stdin
```

---

## MCP Servers

familiar-ai maka-connect sa bisan unsang [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Kini nagtugot kanimo sa pag-plug sa external memory, filesystem access, web search, o bisan unsang alat.

I-configure ang mga server sa `~/.familiar-ai.json` (sama nga format sa Claude Code):

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

Duha ka tipo sa transport ang suportado:
- **`stdio`**: naglunsad sa lokal nga subprocess (`command` + `args`)
- **`sse`**: nagkonektar sa usa ka HTTP+SSE server (`url`)

I-override ang config file location gamit ang `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai nagtrabaho sa bisan unsang hardware nga imong adunay — o wala gani.

| Part | Unsay ginabuhat | Ehemplo | Gikinahanglan? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Mata + liog | Tapo C220 (~$30) | **Girekomenda** |
| USB webcam | Mata (fixed) | Bisan unsang UVC nga camera | **Girekomenda** |
| Robot vacuum | Mga tiil | Bisan unsang modelo nga compatible sa Tuya | Wala |
| PC / Raspberry Pi | Utok | Bisan unsang nagdagan og Python | **Oo** |

> **Kinahanglan gyud ang kamera.** Kung wala, familiar-ai makasulti gihapon — apan dili kini makakita sa kalibutan, nga mao ang tibuok punto.

### Minimal nga setup (walay hardware)

Gusto lang nimo sulayan kini? Kailangan lang nimo og API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Dagan `./run.sh` ug sugdi ang pakighimamat. Idugang ang hardware samtang nagpadayon.

### Wi-Fi PTZ camera (Tapo C220)

1. Sa Tapo app: **Settings → Advanced → Camera Account** — paghimo og lokal nga account (dili TP-Link nga account)
2. Pangitaa ang IP sa camera sa listahan sa mga device sa imong router
3. I-set sa `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Voice (ElevenLabs)

1. Kuhaa ang usa ka API key sa [elevenlabs.io](https://elevenlabs.io/)
2. I-set sa `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opsyonal, naggamit og default voice kung wala
   ```

Adunay duha ka mga audio playback destinations, nga gikinahanglan sa `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC speaker (default)
TTS_OUTPUT=remote   # camera speaker lang
TTS_OUTPUT=both     # camera speaker + PC speaker sabay
```

#### A) Speaker sa camera (pinaagi sa go2rtc)

I-set ang `TTS_OUTPUT=remote` (o `both`). Nagkinahanglan og [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. I-download ang binary gikan sa [releases page](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Ibutang ug i-rerename kini:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # kinahanglan ang chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Paghimo og `go2rtc.yaml` sa sama nga direktoryo:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gamita ang mga kredensyal sa lokal nga account sa camera (dili imong TP-Link cloud nga account).

4. Ang familiar-ai nagsugod sa go2rtc awtomatik sa paglansad. Kung ang imong camera nagsuporta sa two-way audio (backchannel), ang tingog magplay gikan sa speaker sa camera.

#### B) Local PC speaker

Ang default (`TTS_OUTPUT=local`). Nagtan-aw sa players sa pagkasunod-sunod: **paplay** → **mpv** → **ffplay**. Gigamit usab ingon nga fallback kung ang `TTS_OUTPUT=remote` ug ang go2rtc wala.

| OS | Install |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (o `paplay` pinaagi sa `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — i-set ang `PULSE_SERVER=unix:/mnt/wslg/PulseServer` sa `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — i-download ug idugang sa PATH, **o** `winget install ffmpeg` |

> Kung walay audio player nga magamit, ang tingog gihapon buhaton — pero dili kini magplay.

### Voice input (Realtime STT)

I-set ang `REALTIME_STT=true` sa `.env` alang sa always-on, hands-free voice input:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # sama nga key sa TTS
```

Ang familiar-ai nag-stream sa audio sa mikropono ngadto sa ElevenLabs Scribe v2 ug auto-commits sa mga transcript sa dihang mohunong ka sa pagsulti. Wala’y button press nga gikinahanglan. Coexists kini sa push-to-talk mode (Ctrl+T).

---

## TUI

familiar-ai naglakip sa usa ka terminal UI nga gihimo gamit ang [Textual](https://textual.textualize.io/):

- Scrollable conversation history nga adunay live streaming text
- Tab-completion para sa `/quit`, `/clear`
- Ang pagputol sa ahente sa tunga-tunga sa hunahuna pinaagi sa pagsulat samtang kini naghunahuna
- **Conversation log** awtomatik nga nasalbar sa `~/.cache/familiar-ai/chat.log`

Aron mosunod sa log sa lain nga terminal (mapuslanon alang sa copy-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Ang personalidad sa imong familiar nagapuyo sa `ME.md`. Kini nga file gitignore sa git — kini lang ang sa imoha.

Tan-awa ang [`persona-template/en.md`](./persona-template/en.md) alang sa usa ka ehemplo, o [`persona-template/ja.md`](./persona-template/ja.md) alang sa bersyon sa Hapon.

---

## FAQ

**Q: Nagtrabaho ba kini nga walay GPU?**
Oo. Ang embedding model (multilingual-e5-small) nagdagan sa CPU. Ang usa ka GPU mohimo kini nga mas paspas apan dili kini gikinahanglan.

**Q: Mahimo ba akong gamiton ang laing camera gawas sa Tapo?**
Bisan unsang camera nga nagsuporta sa ONVIF + RTSP ang angay magtrabaho. Ang Tapo C220 mao ang among gisulayan.

**Q: Ang akong datos gipadala ba sa bisan asa?**
Ang mga larawan ug teksto ipadala sa imong napiling LLM API para sa pagproseso. Ang mga hinumduman gitipig sa lokal sa `~/.familiar_ai/`.

**Q: Ngano nga ang ahente nagsulat og `（...）` imbes nga mosulti?**
Siguroha nga nakaset ang `ELEVENLABS_API_KEY`. Kung wala kini, ang tingog ma-disable ug ang ahente magbalik sa teksto.

## Technical background

Nangutana bahin sa kung giunsa kini nagtrabaho? Tan-awa ang [docs/technical.md](./docs/technical.md) alang sa mga panukiduki ug mga desisyon sa disenyo sa likod sa familiar-ai — ReAct, SayCan, Reflexion, Voyager, ang desire system, ug uban pa.

---

## Paghatag og kontribusyon

Ang familiar-ai usa ka bukas nga eksperimento. Kung bisan unsang bahin niini nakapukaw sa imo — teknikal o pilosopikal — ang mga kontribusyon malipayong dawaton.

**Maayo nga mga dapit nga sugdan:**

| Area | Unsay gikinahanglan |
|------|---------------|
| Bag-ong hardware | Suporta alang sa dugang nga mga camera (RTSP, IP Webcam), mga mikropono, actuators |
| Bag-ong mga galamiton | Web search, home automation, kalendaryo, bisan unsa pinaagi sa MCP |
| Bag-ong mga backend | Bisan unsang LLM o lokal nga modelo nga angay sa `stream_turn` interface |
| Persona templates | ME.md templates alang sa lain-laing mga sinultian ug personalidad |
| Panukiduki | Mas maayong mga modelo sa desire, retrieval sa memorya, theory-of-mind prompting |
| Dokumentasyon | Tutorials, walkthroughs, mga hubad |

Tan-awa ang [CONTRIBUTING.md](./CONTRIBUTING.md) alang sa dev setup, code style, ug PR guidelines.

Kung ikaw nagduha-duha kung asa magsugod, [ablihi ang usa ka isyu](https://github.com/lifemate-ai/familiar-ai/issues) — malipayong ipapunta ka sa husto nga dalan.

---

## Lisensya

[MIT](./LICENSE)
