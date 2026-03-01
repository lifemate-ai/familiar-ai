# familiar-ai 🐾

**Usa ka AI nga nagpuyo uban kanimo** — uban ang mga mata, tingog, mga tiil, ug memorya.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Available in 74 languages](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai usa ka AI nga kauban nga nagpuyo sa imong balay. I-set up kini sa mga minuto. Wala’y kinahanglan nga coding.

Nakaplagan niini ang tinuod nga kalibutan pinaagi sa mga kamera, nagalihok sa usa ka robot nga lawas, nagtug-an sa tingog, ug nahinumduman ang iyang nakita. Tagai kini og ngalan, isulat ang iyang personalidad, ug pasagdi kini nga magpuyo uban kanimo.

## Unsa ang mahimo niini

- 👁 **Makakita** — nagkuha og mga hulagway gikan sa Wi-Fi PTZ camera o USB webcam
- 🔄 **Tan-awa ang palibot** — naglingkod ug nag-tilt sa kamera aron masusi ang palibot
- 🦿 **Makalihok** — nag drive sa usa ka robot vacuum aron maglakaw sa silid
- 🗣 **Makapanggawas og tingog** — nagtug-an pinaagi sa ElevenLabs TTS
- 🎙 **Makapaminaw** — hands-free nga tingog nga input pinaagi sa ElevenLabs Realtime STT (opt-in)
- 🧠 **Makahunahuna** — aktibo nga nagtipig ug nagbalik sa mga panumduman gamit ang semantic search (SQLite + embeddings)
- 🫀 **Teorya sa Hunahuna** — nagkuha sa panan-aw sa laing tawo sa dili pa motubag
- 💭 **Tinguha** — adunay kaugalingong internal drives nga nagpalihok sa autonomous nga pamatasan

## Unsaon kini pagtrabaho

familiar-ai nagpadagan og usa ka [ReAct](https://arxiv.org/abs/2210.03629) loop nga powered sa imong gipili nga LLM. Nakaplagan niini ang kalibutan pinaagi sa mga himan, naghunahuna kung unsay buhaton ug naglihok — sama sa pagbuhat sa usa ka tawo.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kung idle, naglihok kini base sa iyang kaugalingong mga tinguha: kuryusidad, gusto nga tan-awon ang gawas, pagpangakig sa tawo nga ginalagaran niya.

## Unsaon Pagsugod

### 1. I-install ang uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
O: `winget install astral-sh.uv`

### 2. I-install ang ffmpeg

ang ffmpeg **gikinahanglan** para sa pagkuha sa hulagway sa kamera ug pag-playback sa audio.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — o pag-download gikan sa [ffmpeg.org](https://ffmpeg.org/download.html) ug i-add sa PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Susiha: `ffmpeg -version`

### 3. I-clone ug i-install

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. I-configure

```bash
cp .env.example .env
# I-edit ang .env gamit ang imong mga setting
```

**Minimum nga gikinahanglan:**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Imong API key para sa napiling platform |

**Opsyonal:**

| Variable | Description |
|----------|-------------|
| `MODEL` | Ngalan sa modelo (sensible defaults per platform) |
| `AGENT_NAME` | Nagpakita nga ngalan nga gipakita sa TUI (e.g. `Yukine`) |
| `CAMERA_HOST` | IP address sa imong ONVIF/RTSP nga kamera |
| `CAMERA_USER` / `CAMERA_PASS` | Credentials sa kamera |
| `ELEVENLABS_API_KEY` | Para sa output sa tingog — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` aron i-enable ang always-on hands-free voice input (nagkinahanglan og `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Asa ipagawas ang audio: `local` (PC speaker, default) \| `remote` (kamera speaker) \| `both` |
| `THINKING_MODE` | Anthropic lamang — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptive thinking effort: `high` (default) \| `medium` \| `low` \| `max` (Opus 4.6 lamang) |

### 5. Paghimo sa imong familiar

```bash
cp persona-template/en.md ME.md
# I-edit ang ME.md — tagai kini og ngalan ug personalidad
```

### 6. Padagana

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

## Pagpili og LLM

> **Girekomenda: Kimi K2.5** — pinakamahusay nga agentic nga performance nga nasulayan hangtod karon. Nakamatikod sa konteksto, nagtanong og sunod nga mga pangutana, ug naglihok nga autonomous sa mga paagi nga wala sa ubang modelo. Sa presyo nga susama sa Claude Haiku.

| Platform | `PLATFORM=` | Default model | Asa makakuha og key |
|----------|------------|---------------|---------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (ang command) | — |

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
MODEL=gemini-2.5-flash  # o gemini-2.5-pro para sa mas taas nga kapasidad
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` nga ehemplo:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # gikan sa openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opsyonal: specify ang modelo
AGENT_NAME=Yukine
```

> **Nota:** Aron i-disable ang local/NVIDIA nga mga modelo, ayaw lang i-set ang `BASE_URL` sa usa ka local nga endpoint sama sa `http://localhost:11434/v1`. Gamita ang cloud providers imbis.

**CLI tool `.env` nga ehemplo:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — walay {}, ang prompt moagi pinaagi sa stdin
```

---

## MCP Servers

familiar-ai makakonekta sa bisan unsang [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Kini nagtugot kanimo sa pag-plug in sa external memory, filesystem access, web search, o bisan unsang laing himan.

I-configure ang mga server sa `~/.familiar-ai.json` (parehas nga format sama sa Claude Code):

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

Duha ka transport types ang gisuportahan:
- **`stdio`**: maglunsad sa usa ka local nga subprocess (`command` + `args`)
- **`sse`**: magkonekta sa usa ka HTTP+SSE nga server (`url`)

I-override ang config file location gamit ang `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai nagtrabaho sa bisan unsang hardware nga imong naa — o walay bisan unsa.

| Part | Unsa ang gibuhat | Ehemplo | Gikinahanglan? |
|------|------------------|---------|----------------|
| Wi-Fi PTZ camera | Mga mata + liog | Tapo C220 (~$30) | **Girekomenda** |
| USB webcam | Mga mata (fixed) | Bisan unsang UVC camera | **Girekomenda** |
| Robot vacuum | Mga tiil | Bisan unsang modelo nga compatible sa Tuya | Dili |
| PC / Raspberry Pi | Utok | Bisan unsang nagdagan og Python | **Oo** |

> **Girekomenda jud ang usa ka kamera.** Kung wala, ang familiar-ai makapagsulti gihapon — apan dili kini makakita sa kalibutan, nga mao ang kinatibuk-ang tuyo.

### Minimal nga setup (walay hardware)

Gusto lang ba nimo sulayan kini? Kailangan ra nimo og API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Padagana ang `./run.sh` (macOS/Linux/WSL2) o `run.bat` (Windows) ug sugdi ang pakig-chat. Idugang ang hardware samtang nagpadayon ka.

### Wi-Fi PTZ camera (Tapo C220)

1. Sa Tapo app: **Settings → Advanced → Camera Account** — paghimo og lokal nga account (dili TP-Link account)
2. Pangitaa ang IP sa kamera sa lista sa mga device sa imong router
3. Set sa `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Tingog (ElevenLabs)

1. Kuhaa ang API key sa [elevenlabs.io](https://elevenlabs.io/)
2. Set sa `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opsyonal, naggamit og default voice kung mahibulong
   ```

Adunay duha ka playback destinations, nga kontrolado sa `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC speaker (default)
TTS_OUTPUT=remote   # camera speaker only
TTS_OUTPUT=both     # camera speaker + PC speaker sabay-sabay
```

#### A) Camera speaker (pinaagi sa go2rtc)

Set ang `TTS_OUTPUT=remote` (o `both`). Nanginahanglan og [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. I-download ang binary gikan sa [releases page](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Ibutang ug i-rebrand kini:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x nga gikinahanglan

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Paghimo og `go2rtc.yaml` sa parehong directory:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gamita ang local camera account credentials (dili imong TP-Link cloud account).

4. Ang familiar-ai magsugod sa go2rtc sa awtomatik nga pagsugod. Kung ang imong kamera nagsuporta sa two-way audio (backchannel), ang tingog magplay gikan sa kamera speaker.

#### B) Local PC speaker

Ang default (`TTS_OUTPUT=local`). Nag-attempt og players sa order: **paplay** → **mpv** → **ffplay**. Gigamit usab kini isip fallback kung `TTS_OUTPUT=remote` ug ang go2rtc wala.

| OS | I-install |
|----|-----------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (o `paplay` pinaagi sa `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — set `PULSE_SERVER=unix:/mnt/wslg/PulseServer` sa `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — i-download ug i-add sa PATH, **o** `winget install ffmpeg` |

> Kung wala’y audio player nga magamit, ang tingog gihapon buhion — dili lang kini magplay.

### Voice input (Realtime STT)

Set ang `REALTIME_STT=true` sa `.env` para sa always-on, hands-free voice input:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # parehong key sama sa TTS
```

Ang familiar-ai mag-stream sa microphone audio ngadto sa ElevenLabs Scribe v2 ug awtomatikong mag-commit sa transcripts kung mopaubos ka sa paghisgot. Wala’y button press nga gikinahanglan. Nag-coexist kini sa push-to-talk mode (Ctrl+T).

---

## TUI

familiar-ai naglakip sa usa ka terminal UI nga gitukod gamit ang [Textual](https://textual.textualize.io/):

- Scrollable nga kasaysayan sa pakig-chat uban ang live streaming nga teksto
- Tab-completion para sa `/quit`, `/clear`
- Ma-interrupt ang agent sa tunga-tunga sa turn pinaagi sa pag-type samtang kini naghunahuna
- **Conversation log** nga awtomatikong nasalbar sa `~/.cache/familiar-ai/chat.log`

Aron sundon ang log sa lain nga terminal (mapuslanon para sa copy-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Ang personalidad sa imong familiar nagpuyo sa `ME.md`. Kini nga file gitagana sa git — kini imo ra gyod.

Tan-awa ang [`persona-template/en.md`](./persona-template/en.md) alang sa usa ka ehemplo, o [`persona-template/ja.md`](./persona-template/ja.md) alang sa Japanese nga bersyon.

---

## FAQ

**Q: Moobra ba kini nga walay GPU?**
Oo. Ang embedding model (multilingual-e5-small) maayo ra nga nagdagan sa CPU. Ang GPU nagpasayon niini apan dili gikinahanglan.

**Q: Makagamit ba ko ug kamera nga lahi sa Tapo?**
Bisan unsang kamera nga nagsuporta sa ONVIF + RTSP ang mahimong magamit. Ang Tapo C220 mao ang among gisuwayan.

**Q: Ang akong datos gisugo ba sa bisan asa?**
Ang mga hulagway ug teksto gisugdan sa imong gipiling LLM API para sa pagproseso. Ang mga panumduman gitipig lokal sa `~/.familiar_ai/`.

**Q: Ngano nga ang agent nagsulat og `（...）` imbes nga nagtug-an?**
Siguroha nga ang `ELEVENLABS_API_KEY` nakaset. Kung wala, ang tingog disabled ug ang agent mobalik sa teksto.

## Teknikal nga background

Curious ka ba kung unsaon kini nagtrabaho? Tan-awa ang [docs/technical.md](./docs/technical.md) alang sa research ug disenyo nga mga desisyon nga nagatuyok sa familiar-ai — ReAct, SayCan, Reflexion, Voyager, ang desire system, ug daghan pa.

---

## Pag-ambit

familiar-ai usa ka open experiment. Kung bisan unsa niini nagakaigo kanimo — teknikal o pilosopiya — ang mga kontribusyon malipayong dawaton.

**Maayo nga mga lugar aron magsugod:**

| Area | Unsa ang gikinahanglan |
|------|-----------------------|
| Bag-o nga hardware | Suportahan ang daghang mga kamera (RTSP, IP Webcam), mga mikropono, actuator |
| Bag-o nga himan | Web search, home automation, kalendaryo, bisan unsa pinaagi sa MCP |
| Bag-o nga backends | Bisan unsang LLM o local model nga mohaom sa `stream_turn` interface |
| Persona templates | ME.md templates para sa nagkadaiyang mga pinulongan ug personalidad |
| Research | Mas maayong mga modelo sa tinguha, retrieval sa memorya, theory-of-mind prompting |
| Dokumentasyon | Tutorials, walkthroughs, translations |

Tan-awa ang [CONTRIBUTING.md](./CONTRIBUTING.md) para sa dev setup, code style, ug PR guidelines.

Kung dili ka sigurado asa magsugod, [abrihi ang usa ka isyu](https://github.com/lifemate-ai/familiar-ai/issues) — malipayong magtudlo kanimo sa husto nga direksyon.

---

## Lisensya

[MIT](./LICENSE)
