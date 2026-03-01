# familiar-ai 🐾

**E AI oyo elala na mabele na yo** — na miso, lokó, makabo, mpe esika ya kofanda.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [E available na mitá 74](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ezali AI oyo ezali na ndako na yo.
Pesa yango ntango moke. Te mosala ya kombozola ezali lisusu na esika.

Elandaka mabele ya solo na nzela ya ba kamera, ezali kobanga na moto ya roboti, ezali koloba na nzela ya lakanisi, mpe ebandeli koyeba oyo ezozanga. Pesa yango kombo, yemba nzela na yango, mpe letela yango elala na yo.

## Oyo ezali na yango

- 👁 **Kakisa** — ezua maboko na ba kamera ya Wi-Fi PTZ to ba webcam ya USB
- 🔄 **Zala niboko** — pesaka mokumba mpe otaki kameran na elongo ya makambo
- 🦿 **Luka** — kondima boyfriend ya roboti mpo na koluka na se
- 🗣 **Loba** — lobá na nzela ya ElevenLabs TTS
- 🎙 **Yeba** — nzela ya mabe mpo na yebisa nga na nzela ya ElevenLabs Realtime STT (okitani)
- 🧠 **Koyeba** — ebandaka mpe ezosala koya na banzela ya semantiki (SQLite + embeddings)
- 🫀 **Tala ya Motema** — elanda esika ya moto mosusu mpo na koboya
- 💭 **Biso** — ezali na bisaleli na yango ekoki boluka ya masolo

## Ndenge esalaka

familiar-ai ezalaka na [ReAct](https://arxiv.org/abs/2210.03629) loop oyo eza na nzela ya LLM oyo olingi. Elandaka mabele na ba ngenga, elaki maka oyo ekoki osala nsima, mpe esalaka — lokola moto akoki.

```
user input
  → kanga → salaka (kamerá / luka / loba / koyeba) → tala → kanga → ...
```

Ntango ezali na saaté, esalaka na bisaleli na yango: best example, koluka na kolanda, koluka oyo epesaka bolingo.

## Kokota na mabele

### 1. Konyeka uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
To: `winget install astral-sh.uv`

### 2. Konyeka ffmpeg

ffmpeg ezali **soki ezokoma** mpo na kodita maboko na kamera mpe na kompeka ya yayi.

| OS | Komanda |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — to zala na [ffmpeg.org](https://ffmpeg.org/download.html) mpe lokola na PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Toto yaka: `ffmpeg -version`

### 3. Klona mpe konyeka

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Seta

```bash
cp .env.example .env
# Phinga .env na ba settings na yo
```

**Mokili moko:**

| Variable | Maloba |
|----------|-------------|
| `PLATFORM` | `anthropic` (bato) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | API ko na platform oyo okendaki |

**Oyo ekoki:**

| Variable | Maloba |
|----------|-------------|
| `MODEL` | Liyangani kisima (ybassé) |
| `AGENT_NAME` | Kombo ya likambo elandelaka na TUI (e.g. `Yukine`) |
| `CAMERA_HOST` | IP ya kamera na yo ya ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Ba credential ya kamera |
| `ELEVENLABS_API_KEY` | Mpo na koloba — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` mpo na kolinga ya koyoka na nzela ya bozingi (bato ya `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Esika ya kompeka: `local` (PC speaker, bongo) \| `remote` (kamera speaker) \| `both` |
| `THINKING_MODE` | Anthropic soki — `auto` (batel) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Ndenge ya koyeba: `high` (batel) \| `medium` \| `low` \| `max` (Opus 4.6 soki) |

### 5. Pesa mo familiar

```bash
cp persona-template/en.md ME.md
# Bunda ME.md — pesa yango kombo mpe maloba
```

### 6. Salaka

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI ya ndenge
./run.sh --no-tui    # REPL ya botom
```

**Windows:**
```bat
run.bat              # TUI ya ndenge
run.bat --no-tui     # REPL ya botom
```

---

## Koyangela LLM

> **Oyo ebotami: Kimi K2.5** — ya moke ya kitoki koleka oyo esalaka. Eteya esika, epesaka mibeko misi, mpe esalaka na ndenge ya bokonzi oyo baye mosusu batemaki. Bazali na mbongo moko na Claude Haiku.

| Platform | `PLATFORM=` | Mongo ya lisanga | Esika ya kokufa |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (mokanda) | — |

**Kimi K2.5 `.env` exemple:**
```env
PLATFORM=kimi
API_KEY=sk-...   # na platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` exemple:**
```env
PLATFORM=glm
API_KEY=...   # na api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` exemple:**
```env
PLATFORM=gemini
API_KEY=AIza...   # na aistudio.google.com
MODEL=gemini-2.5-flash  # to gemini-2.5-pro mpo na bokonzi 
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` exemple:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # na openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # optional: komela model
AGENT_NAME=Yukine
```

> **Kosenga:** Mpo na kombozola ba moa ya kotomboka/NVIDIA, just te tokozala na `BASE_URL` na lokasa ya local ndenge `http://localhost:11434/v1`. Senga bongo ba mokonzi.

**CLI tool `.env` exemple:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — te {}, prompt ebenda na stdin
```

---

## MCP Servers

familiar-ai akoki kokamata na [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Oyo eteya yo kosangisa na motindo ya sikana, acces na filesystem, web search, to eloko mosusu.

Seta na servers na `~/.familiar-ai.json` (makambo o kolanda na Claude Code):

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

Bato mibale ya transport ezali na esika:
- **`stdio`**: 开启 na tsukeman  (komanda + args)
- **`sse`**: kotinda na HTTP+SSE server (`url`)

Override lokasa ya config na `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai akoki kozala na hardware nyonso okoki — to okosengaka.

| Part | Oyo ezali | Exemple | Osengaka? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Miso + risanga | Tapo C220 (~$30) | **Obenga** |
| USB webcam | Miso (simaki) | Nyonso UVC kamera | **Obenga** |
| Robot vacuum | Makabo | Nyonso milayi ya Tuya | Te |
| PC / Raspberry Pi | Motema | Eloko nionso eza na Python | **Ee** |

> **Kamera ezali na bokebisa.** Na yo, familiar-ai akoki koloba — kasi akoki te kokanisa mabele, oyo ezali na se ya koko.

### Install minimal (te hardware)

Olingi kokalama? Olingi te na API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Salaka `./run.sh` (macOS/Linux/WSL2) to `run.bat` (Windows) mpe tanga akongisa. Lika na hardware na yo.

### Wi-Fi PTZ kamera (Tapo C220)

1. Na lolenge ya Tapo: **Settings → Advanced → Kamera Account** — pesa eloko ya mabele (te konto TP-Link)
2. Tanga IP ya kamera na l'état na yo
3. Sete na `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=naam-na-yo
   CAMERA_PASS=lozoi-na-yo
   ```

### Sawa (ElevenLabs)

1. Benga API key na [elevenlabs.io](https://elevenlabs.io/)
2. Sete na `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # optional, elala na nzela lakanisi
   ```

Eza na bisika ya zala ya koloba, oyo ezali konyangwa na `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC speaker (bato)
TTS_OUTPUT=remote   # kamera speaker te
TTS_OUTPUT=both     # kamera speaker + PC speaker siko
```

#### A) Kamera speaker (na go2rtc)

Sete `TTS_OUTPUT=remote` (to `both`). Eza na [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Tika bokasi ya bili na \[releases page\](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Zala mpe komela yango:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x ya kulanda

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Funda `go2rtc.yaml` na esika moko:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Mikanda esalaka na ba credential ya kamera ya local (te TP-Link cloud account).

4. familiar-ai etombaka go2rtc site esala. Soki kamera na yo ezalaka na audio nyonso (backchannel), loba ezozanga na kamera speaker.

#### B) PC speaker ya local

Ezalaka ya solosolo (`TTS_OUTPUT=local`). Elandaka ba players na lestate: **paplay** → **mpv** → **ffplay**. Ekozala mpe na ebandeli soki `TTS_OUTPUT=remote` mpe go2rtc ezali te.

| OS | Kolia |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (to `paplay` na `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — set `PULSE_SERVER=unix:/mnt/wslg/PulseServer` na `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — kolia mpe kozalaka na PATH, **to** `winget install ffmpeg` |

> Soki te na audio player, esalaka kombo — alingi te oleka na kombo.

### Input ya lobá (Realtime STT)

Seta `REALTIME_STT=true` na `.env` mpo na koyinga ya yo na yebisa na nzela ya lokasa:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # komengo key ya TTS
```

familiar-ai ekokaka ba musique na microphone na ElevenLabs Scribe v2 mpe auto-commits motsi nsima ya kozala. Te bongo na lobá. Ezozanga na mädälo ya tindi (Ctrl+T).

---

## TUI

familiar-ai ebendaka na terminal UI oyo ebengaka [Textual](https://textual.textualize.io/):

- Kalisela mosala ya mboka na biso
- Tab-bongani ya `/quit`, `/clear`
- Koyeka agent eza na nsima ya kokutana
- **Log ya makama** ekokaka na `~/.cache/familiar-ai/chat.log`

Mpo na iká log na ntango mosusu (ekeseni):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Maloba ya familiar na yo ezalaka na `ME.md`. File oyo ezali gitignored — eza maloa ya yo.

Tanga [`persona-template/en.md`](./persona-template/en.md) mpo na exemple, to [`persona-template/ja.md`](./persona-template/ja.md) mpo na version Japonese.

---

## FAQ

**Q: Ekoki osala na GPU?**
Ee. Model embedding (multilingual-e5-small) ebenda ko malela nzela ya CPU. GPU ekosi makasi kasi ezali te.

**Q: Nakoki koya na kamera mosusu?**
Eloko nionso ekoki konyuka ONVIF + RTSP esalaka. Tapo C220 ezalaka na ewuti na model.

**Q: Datos na ngai ekotaka esika moko?**
Mabakisa na likambo na yebisi ya LLM API oyo osalaka na processing. Mbango ebandi na local na `~/.familiar_ai/`.

**Q: Pourquoi agent alinga `（...）` na nzela ya koloba?**
Senga `ELEVENLABS_API_KEY` ekoti. Soki te, lobá esengaka mpe agent еzali na mongala na texte.

## Technical background

Olingi koyeba ndenge esalaka? Tanga [docs/technical.md](./docs/technical.md) mpo na masolo na nzela ya familiar-ai — ReAct, SayCan, Reflexion, Voyager, bisaleli ya koluka, mpe makambo mosusu.

---

## Contributing

familiar-ai ezalaka na lipanda. Soki nionso oyo ezozanga na yo — tekniki to philosophically — ba pusa esalaka.

**Ba esika ya malamu ya coyinga:**

| Espace | Oyo ezali na ye |
|------|---------------|
| Hardware siko | Support ya ba kamera mosusu (RTSP, IP Webcam), ba microphone, dobo |
| Ba ngateli | Internet research, home automation, calendrier, eloko nyonso na MCP |
| Ba backends | Eloko nyonso LLM to local model oyo esalaka na `stream_turn` interface |
| Ba template ya persona | Templates ME.md mpo na lingala ndenge mosusu mpe maloba |
| Masambo | Makambo malamu ya koyeba, boluka mboka, theory-of-mind prompting |
| Liyangani | Ba tutorial, boluka, ba traductions |

Tanga [CONTRIBUTING.md](./CONTRIBUTING.md) mpo na dev setup, style ya code, mpe PR malanda.

Soki oza na ntango te, [okota pondu](https://github.com/lifemate-ai/familiar-ai/issues) — eza malamu koleka na esika esalaka na yo.

---

## License

[MIT](./LICENSE)
