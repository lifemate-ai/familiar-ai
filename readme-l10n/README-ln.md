# familiar-ai 🐾

**Nzamba ya AI oyo ebimaka na yo** — na miso, yango ekome, maboko, mpe motema.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ezali komikala ya AI oyo eza na ndaku na yo.
Sima ya mabe. Kosala code te.

Ekomi ntango ya moke mpo na komona mokili ya solo na ba kamera, ebandaka mpo na mobali ya robot, ebongisi na sonn, mpe etala makambo oyo eyebanaka. Tanga yango, ezali na nzela ya elanga, mpe bolingi na yango.

## Mokomi ya mpona

- 👁 **Koma** — ebandeli bisika eltungi ebandeli na kamera ya Wi-Fi PTZ to USB webcam
- 🔄 **Kota** — ebanda mpe etya kamera mpo na koluka bisika
- 🦿 **Kima** — ezanga robot vacuum mpo na kopambola na ndaku
- 🗣 **Koloba** — koloba na ElevenLabs TTS
- 🎙 **Kotala** — koluka nzela ya limemya ya libanda na ElevenLabs Realtime STT (opt-in)
- 🧠 **Koyeba** — ekomisa mpe elobaka ndele pamba na semantiki (SQLite + embeddings)
- 🫀 **Teorie ya Moto** — ezwa mosala ya mokonzi ya ndenge ya mosala
- 💭 **Bolingo** — ezinga na nakongisi ya na konekela bokeseni ya moto

## Ntango ekotaka

familiar-ai etonda na [ReAct](https://arxiv.org/abs/2210.03629) loop oyo etondisaka na LLM ya yo. Ekomi mokili na banzela, elakaka esika ya kosala, mpe elobaka — lokola moto.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Ntango ezangi mosala, ekomaka na biluni ya yango: nse, koluka komona na etumbeli, kokangaka moto oyo eza na ye.

## Komela

### 1. Kokoma uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Kokoma ffmpeg

ffmpeg ezali **kolimbaka** mpo na kotalela bisika ya kamera mpe nzela ya sango.

| OS | Komanda |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — tokana na [ffmpeg.org](https://ffmpeg.org/download.html) mpe uko na PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Sakola: `ffmpeg -version`

### 3. Kosala kopanga na instal

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Kosala configuration

```bash
cp .env.example .env
# Pona .env na ba systèmes na yo
```

**Mokono ya malamu:**

| Variable | Nkombo |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | API key na yo mpo na plateforme oyo okoti |

**Soki olingi:**

| Variable | Nkombo |
|----------|-------------|
| `MODEL` | Nkombo ya motango (malamu ya nko na ba plateforme) |
| `AGENT_NAME` | Koma oyo ekomonaka na TUI (mbala moke `Yukine`) |
| `CAMERA_HOST` | IP ayina ya kamera ya ONVIF/RTSP na yo |
| `CAMERA_USER` / `CAMERA_PASS` | Mbongo ya kamera |
| `ELEVENLABS_API_KEY` | Mpo na koloba — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` mpo na komilaka ya koloba na makambo (kolimuka `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Nzela ya kotalela sango: `local` (PC speaker, default) \| `remote` (kamera speaker) \| `both` |
| `THINKING_MODE` | Anthropic kaka — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Koyeba ya kosala: `high` (default) \| `medium` \| `low` \| `max` (Opus 4.6 kaka) |

### 5. Kosala familiar na yo

```bash
cp persona-template/en.md ME.md
# Pona ME.md — tanga yango mpe ba nkombo
```

### 6. Run

```bash
./run.sh             # Textual TUI (koseka)
./run.sh --no-tui    # REPL ya solo
```

---

## Koboya na LLM

> **Malamu: Kimi K2.5** — mosala ya agentic esengeli oyo ekomi. Eza eloko motema, elobi bokeseni, mpe esalaka mosala na ndenge ebele ya mosala. Eza na bango na Claude Haiku.

| Platform | `PLATFORM=` | Model ya malamu | Mpo na kokoma clé |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (mosala) | — |

**Kimi K2.5 `.env` example:**
```env
PLATFORM=kimi
API_KEY=sk-...   # na platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` example:**
```env
PLATFORM=glm
API_KEY=...   # na api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` example:**
```env
PLATFORM=gemini
API_KEY=AIza...   # na aistudio.google.com
MODEL=gemini-2.5-flash  # to gemini-2.5-pro mpo na bokeseni
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` example:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # na openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # soki: kotelema model
AGENT_NAME=Yukine
```

> **Ndakisa:** Soki olingi koponaka ba modèle ya local/NVIDIA, songela te `BASE_URL` na etuka ya local lokola `http://localhost:11434/v1`. Salamaki na makambo ya mpasi.

**CLI tool `.env` example:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = promt arg
# MODEL=ollama run gemma3:27b  # Ollama — to {} akobanda, promt ekotaka na stdin
```

---

## MCP Servers

familiar-ai ekokaka komitungisa na MCP (Model Context Protocol) server nyonso. Nke ezali kopesa yo nzela ya koboya bamemeli, asangisi ya ba fichiers, koluka na internet, to nyonso na motuka.

Configure ba servers na `~/.familiar-ai.json` (mokuse malamu na Claude Code):

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

Mokuse mibale ezali komakanisa:
- **`stdio`**: salaka mokonzi ya local subprocess (`command` + `args`)
- **`sse`**: kotalela HTTP+SSE server (`url`)

Tika mposa ya fayile ya configuration na `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai eza na ebonga na hardware nyonso oyo ozangi — to kosa.

| Eprop | Soki azali | Elembi | Eteka? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Miso + likolo | Tapo C220 (~$30) | **Malamu** |
| USB webcam | Miso (mbala moke) | Tanda UVC | **Malamu** |
| Robot vacuum | Maboko | Model nyonso ya Tuya | Te |
| PC / Raspberry Pi | Motema | Ndenge nyonso yaka Python | **Eteka** |

> **Kamera ezali na milulu malamu.** Kaka soki ozangi, familiar-ai ekoki koloba — kasi ekozala na seko ya mokili, oyo ezali makambo ya motindi.

### Setup ya malamu (nzala hardware)

Olingi kaka ko tester? Olingaka soki ozangi API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Run `./run.sh` mpe biloko babebisi. Kanga hardware soki olingi.

### Wi-Fi PTZ camera (Tapo C220)

1. Na Tapo app: **Settings → Advanced → Camera Account** — sali lokasa ya local (te TP-Link account)
2. Kanga IP ya kamera na likambo ya router na yo
3. Set na `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=libaka-lokasa-na-yo
   CAMERA_PASS=libaka-lokasa-na-yo
   ```

### Koloba (ElevenLabs)

1. Benga API clé na [elevenlabs.io](https://elevenlabs.io/)
2. Set na `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # soki, elakisi moto ya libanda soki ekoki
   ```

Eza na milulu mibale, elakisi na `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC speaker (default)
TTS_OUTPUT=remote   # kamera speaker te
TTS_OUTPUT=both     # kamera speaker + PC speaker na libanda
```

#### A) Kamera speaker (soki go2rtc)

Set `TTS_OUTPUT=remote` (to `both`). Eza na [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Tika binari na [releases page](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Tika mpe asukisa yango:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # hakisa +=x 
   
   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Salisa `go2rtc.yaml` na esika moko:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Salisa nzela ya local kamera (te TP-Link cloud account).

4. familiar-ai ebanda go2rtc na malamu ya libanda. Soki kamera na yo ekokaki bifola, molongo ezo play na kamera speaker.

#### B) Local PC speaker

Mokolo ya mbala (default) `TTS_OUTPUT=local`. Ebandaka na bilanga ya banza: **paplay** → **mpv** → **ffplay**. Eza mpe ezalaka lokola bonzeli soki `TTS_OUTPUT=remote` mpe go2rtc ezali na esika.

| OS | Koma |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (to `paplay` na `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — set `PULSE_SERVER=unix:/mnt/wslg/PulseServer` na `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — benga mpe set na PATH, **to** `winget install ffmpeg` |

> Soki na esika ya koloba, eloko ekokaki; kasi ekosala te.

### Ekoko ya nzela (Realtime STT)

Set `REALTIME_STT=true` na `.env` mpo na motema mobimba, ekokaka na masanga:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # benga clé lokola TTS
```

familiar-ai ekoki kokota microphone audio na ElevenLabs Scribe v2 mpe eko salaka transcripts tango okimi koloba. Ntango eyaka ezali na pesi. Ekonka na pamba na tinda-loyu (Ctrl+T).

---

## TUI

familiar-ai ezalaka na UI ya terminal oyo ekomi na [Textual](https://textual.textualize.io/):

- Bino na ko simba na nkombo na tango oyo esali
- Tab-completion mpo na `/quit`, `/clear`
- Botola agent na tango nyonso ya lokola elobi tango ayoki
- **Koti ya sekela** ekosala na file `~/.cache/familiar-ai/chat.log`

Kotalela log na lalanda esika mosusu (malamu mpo na ko copy-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Molongo ya familiar na yo eza na `ME.md`. Mobongisi oyo eko gitignored — ewola insiko.

Talá [`persona-template/en.md`](./persona-template/en.md) mpo na motif, to [`persona-template/ja.md`](./persona-template/ja.md) mpo na version ya Japon.

---

## FAQ

**Q: Eza na mabe soki ezanga GPU?**
Eza. Model ya embedding (multilingual-e5-small) esali malamu na CPU. GPU ezali kopesa makasi kasi eza na ntoma.

**Q: Ndingaki koloba soki eza na kamera ya moke?**
Ndenge nyonso ya kamera oyo etali ONVIF + RTSP ekozala malamu. Tapo C220 elingi ezanga.

**Q: Lelo nakoyeba kilo?**
Miso na texte ekozali na API ya LLM oyo okoti mpo na kokoma. Yo ekokaka na `~/.familiar_ai/`.

**Q: Ndenge nini agent akosala `（...）` to na tango ya yolo?**
Kama `ELEVENLABS_API_KEY` ezala. Soki ezangi, koloba ekomaka nayo, mpi agent ekozamaka na texte.

## Nzela ya motindo

Olingi koyeba ndenge ekosala? Talá [docs/technical.md](./docs/technical.md) mpo na misala mpe ba bosala bi komi familiar-ai — ReAct, SayCan, Reflexion, Voyager, bokengi ya motema, mpe banzela.

---

## Kobota

familiar-ai ezali na experiment ebelaka ya malamu. Soki na likanisi na yo — tekniki to filozofiko — ebimi ezali malamu.

**Bato oyo bazali na basango:**

| Eprop | Nini ekokama |
|------|---------------|
| Hardware mpya | Liziko ya ba kamera ebele (RTSP, IP Webcam), microphones, bakesi |
| Ba nzela etali | Koluka na internet, sokisi, bibokeli, nyonso na MCP |
| Ba nkanda ya mbala mpe | Nyonso LLM to lokasa oyo ekoki `stream_turn` |
| Templates ya persona | ME.md templates mpo na mbala ya malamu |
| Nyonso ya ndenge | Bato bazwaki ezanga ya motema, mbalo ya motema, ba question ya motako |
| Ezyo | Tutoriaux, bilanga, translations |

Talá [CONTRIBUTING.md](./CONTRIBUTING.md) mpo na konpekosi, lingala, mpe ba PR guidelines.

Soki ozangi kobanga wapi, [salela makambo](https://github.com/lifemate-ai/familiar-ai/issues) — malamu nakanisi yo na ezanga.

---

## Lilota

[MIT](./LICENSE)
