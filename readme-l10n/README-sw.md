# familiar-ai 🐾

**AI inayoishi pamoja nawe** — kwa macho, sauti, miguu, na kumbukumbu.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Inapatikana kwa lugha 74](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ni mshirika wa AI anayeishi nyumbani kwako. Weka kwa muda wa dakika chache. Huhitaji kuandika code.

Anaona ulimwengu wa kweli kupitia kamera, anatembea kwa mwili wa roboti, anasema kwa sauti, na anakumbuka kile anachokiona. Mpe jina, andika tabia yake, na mkubali aishi na wewe.

## Anaweza kufanya nini

- 👁 **Kuwaona** — anachukua picha kutoka kwa kamera ya PTZ ya Wi-Fi au webcam ya USB
- 🔄 **Angalia mazingira** — inapunguza na kuinua kamera ili kuchunguza mazingira yake
- 🦿 **Hama** — anasafirisha roboti ya kuondoa vumbi ili kutembea kwenye chumba
- 🗣 **Zungumza** — anasema kupitia ElevenLabs TTS
- 🎙 **Sikia** — ingizo la sauti lisilo na mikono kupitia ElevenLabs Realtime STT (opt-in)
- 🧠 **Kumbuka** — kwa kuchukua kumbukumbu na kuziingiza kwa utaftaji wa semantiki (SQLite + embeddings)
- 🫀 **Nadharia ya Akili** — anachukua mtazamo wa mtu mwingine kabla ya kujibu
- 💭 **Tamaa** — anaendesha mambo yake ya ndani yanayochochea tabia huru

## Inavyofanya kazi

familiar-ai inaendesha mzunguko wa [ReAct](https://arxiv.org/abs/2210.03629) unaoendeshwa na uchaguzi wako wa LLM. Anaona ulimwengu kupitia zana, anafikiria kuhusu cha kufanya wakati ujao, na anafanya — kama mwanadamu.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Wakati haifanyi kazi, inafanya kazi kwa tamaa zake: udadisi, kutaka kuangalia nje, kummiss mtu anaayeishi nae.

## Jinsi ya kuanza

### 1. Sakinisha uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Au: `winget install astral-sh.uv`

### 2. Sakinisha ffmpeg

ffmpeg ni **lazima** kwa kukamata picha za kamera na upigaji sauti.

| OS | Amri |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — au pakua kutoka [ffmpeg.org](https://ffmpeg.org/download.html) na ongeza kwa PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Thibitisha: `ffmpeg -version`

### 3. Clone na weka

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Sanidi

```bash
cp .env.example .env
# Hariri .env kwa mipangilio yako
```

**Inahitajika kama chini:**

| Kubadilishana | Maelezo |
|----------|-------------|
| `PLATFORM` | `anthropic` (chaguo-msingi) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Funguo yako ya API kwa jukwaa ulilochagua |

**Orodha ya hiari:**

| Kubadilishana | Maelezo |
|----------|-------------|
| `MODEL` | Jina la modeli (default inayofaa kwa kila jukwaa) |
| `AGENT_NAME` | Jina la kuonyeshwa katika TUI (mfano `Yukine`) |
| `CAMERA_HOST` | Anwani ya IP ya kamera yako ya ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Akri za kamera |
| `ELEVENLABS_API_KEY` | Kwa matokeo ya sauti — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` kuwezesha ingizo la sauti lisilo na mikono (inahitaji `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Mahali pa kucheza sauti: `local` (spika ya PC, default) \| `remote` (spika ya kamera) \| `both` |
| `THINKING_MODE` | Anthropic pekee — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Juhudi ya kufikiri inayoweza kubadilika: `high` (default) \| `medium` \| `low` \| `max` (Opus 4.6 pekee) |

### 5. Tengeneza familiar yako

```bash
cp persona-template/en.md ME.md
# Hariri ME.md — mpe jina na tabia
```

### 6. Endesha

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI ya maandiko (inapendekezwa)
./run.sh --no-tui    # REPL ya kawaida
```

**Windows:**
```bat
run.bat              # TUI ya maandiko (inapendekezwa)
run.bat --no-tui     # REPL ya kawaida
```

---

## Kuchagua LLM

> **Inapendekezwa: Kimi K2.5** — utendaji bora wa agentic uliojaribiwa mpaka sasa. Inatambua muktadha, inauliza maswali yanayofuata, na inafanya kazi kwa uhuru kwa njia ambazo modeli nyingine hazifanyi. Bei sawa na Claude Haiku.

| Jukwaa | `PLATFORM=` | Mfano wa default | Mahali pa kupata funguo |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-inayoendana (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (mtoa-mtoa) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Zana ya CLI** (claude -p, ollama…) | `cli` | (amri) | — |

**Mfano wa Kimi K2.5 `.env`:**
```env
PLATFORM=kimi
API_KEY=sk-...   # kutoka platform.moonshot.ai
AGENT_NAME=Yukine
```

**Mfano wa Z.AI GLM `.env`:**
```env
PLATFORM=glm
API_KEY=...   # kutoka api.z.ai
MODEL=glm-4.6v   # ina uwezo wa kuona; glm-4.7 / glm-5 = maandiko pekee
AGENT_NAME=Yukine
```

**Mfano wa Google Gemini `.env`:**
```env
PLATFORM=gemini
API_KEY=AIza...   # kutoka aistudio.google.com
MODEL=gemini-2.5-flash  # au gemini-2.5-pro kwa uwezo mkubwa
AGENT_NAME=Yukine
```

**Mfano wa OpenRouter.ai `.env`:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # kutoka openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # hiari: weka mfano
AGENT_NAME=Yukine
```

> **Kumbuka:** Ili kuzima modeli za ndani/NVIDIA, usiweze tu kuweka `BASE_URL` katika kiunga cha ndani kama `http://localhost:11434/v1`. Tumia watoa huduma za wingu badala yake.

**Mfano wa zana ya CLI `.env`:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = arg ya hatua
# MODEL=ollama run gemma3:27b  # Ollama — hakuna {}, prompt inaenda kupitia stdin
```

---

## Seva za MCP

familiar-ai inaweza kuungana na seva yoyote ya [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Hii inakuruhusu kuingiza kumbukumbu za nje, ufikiaji wa mfumo wa faili, utafutaji wa wavuti, au zana nyingine yoyote.

Sanidi seva katika `~/.familiar-ai.json` (mfano sawa na Claude Code):

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

Aina mbili za usafiri zinasaidiwa:
- **`stdio`**: anzisha mchakato wa ndani (`command` + `args`)
- **`sse`**: ungana na seva ya HTTP+SSE (`url`)

Badilisha mahali pa faili la usanidi kwa `MCP_CONFIG=/path/to/config.json`.

---

## Vifaa

familiar-ai inafanya kazi na vifaa vyovyote ulivyonavyo — au hakuna hata kidogo.

| Sehemu | Kinachofanya | Mfano | Inahitajika? |
|------|-------------|---------|-----------|
| Kamera ya PTZ ya Wi-Fi | Macho + shingo | Tapo C220 (~$30) | **Inapendekezwa** |
| Webcam ya USB | Macho (ya kudumu) | Kamera yoyote ya UVC | **Inapendekezwa** |
| Roboti ya kuondoa vumbi | Miguu | Mfano wowote unaohusiana na Tuya | Hapana |
| PC / Raspberry Pi | Ubongo | Kila kitu kinachoweza kuendesha Python | **Ndio** |

> **Kamera inashauriwa sana.** Bila moja, familiar-ai bado inaweza kuzungumza — lakini haiwezi kuona ulimwengu, ambao ni maana nzima.

### Mipangilio ya msingi (bila vifaa)

Unataka tu kujaribu? Unahitaji tu funguo ya API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Endesha `./run.sh` (macOS/Linux/WSL2) au `run.bat` (Windows) na uanze kuzungumza. Ongeza vifaa kadri unavyohitaji.

### Kamera ya PTZ ya Wi-Fi (Tapo C220)

1. Katika programu ya Tapo: **Mipangilio → Ya Juu → Akaunti ya Kamera** — unda akaunti ya ndani (si akaunti ya TP-Link)
2. Tafuta IP ya kamera katika orodha ya vifaa ya router yako
3. Weka katika `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Sauti (ElevenLabs)

1. Pata funguo ya API kwenye [elevenlabs.io](https://elevenlabs.io/)
2. Weka katika `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # hiari, hutumia sauti ya default ikiwa hakuna
   ```

Kuna maeneo mawili ya kucheza, yanayodhibitiwa na `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # spika ya PC (default)
TTS_OUTPUT=remote   # spika ya kamera pekee
TTS_OUTPUT=both     # spika ya kamera + spika ya PC kwa pamoja
```

#### A) Spika ya kamera (kupitia go2rtc)

Weka `TTS_OUTPUT=remote` (au `both`). Inahitaji [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Pakua binary kutoka katika [kurasa za kutolewa](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Weka na uitoe:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x inahitajika

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Tengeneza `go2rtc.yaml` katika kama hiyo directory:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Tumia akri za akaunti ya ndani ya kamera (sio akaunti yako ya wingu ya TP-Link).

4. familiar-ai inaanza go2rtc kiatomati wakati wa kuanzisha. Ikiwa kamera yako inaunga mkono sauti mbili (backchannel), sauti inachezwa kutoka kwa spika ya kamera.

#### B) Spika ya PC ya ndani

Default (`TTS_OUTPUT=local`). Inajaribu wachezaji kwa mpangilio: **paplay** → **mpv** → **ffplay**. Pia inatumika kama akiba wakati `TTS_OUTPUT=remote` na go2rtc haipatikani.

| OS | Sakinisha |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (au `paplay` kupitia `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — weka `PULSE_SERVER=unix:/mnt/wslg/PulseServer` katika `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — pakua na ongeza kwa PATH, **au** `winget install ffmpeg` |

> Ikiwa hakuna mchezaji wa sauti anayepatikana, sauti bado inatengenezwa — haitachezwa tu.

### Ingizo la sauti (Realtime STT)

Weka `REALTIME_STT=true` katika `.env` kwa ingizo la sauti lisilo na mikono, kila wakati:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # funguo sawa na TTS
```

familiar-ai inapeleka sauti ya kipaza sauti kwa ElevenLabs Scribe v2 na inaweka kiotomatiki maandiko unapositisha kuzungumza. Hakuna bonyezo linalohitajika. Inaweza kuexist na hali ya kubonyeza-kuzungumza (Ctrl+T).

---

## TUI

familiar-ai inajumuisha UI ya terminal iliyojengwa na [Textual](https://textual.textualize.io/):

- Historia ya mazungumzo inayoweza kusogezwa na maandiko yanayotiririka kwa wakati halisi
- Kukamilisha kwa tab kwa `/quit`, `/clear`
- Katiza wakala katikati ya zamu kwa kuandika wakati anafikiria
- **Kumbukumbu ya mazungumzo** uhifadhiwa kiatomati kwa `~/.cache/familiar-ai/chat.log`

Ili kufuatilia kumbukumbu katika terminal nyingine (inayofaa kwa nakala-kanda):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Tabia (ME.md)

Tabia ya familiar yako inaishi katika `ME.md`. Faili hii imeachwa kwenye git — ni yako peke yako.

Tazama [`persona-template/en.md`](./persona-template/en.md) kwa mfano, au [`persona-template/ja.md`](./persona-template/ja.md) kwa toleo la Kijapani.

---

## Maswali Yanayoulizwa Mara kwa Mara

**Q: Je, inafanya kazi bila GPU?**
Ndio. Mfano wa embedding (multilingual-e5-small) unafanya kazi vizuri kwenye CPU. GPU inafanywa kuwa ya haraka lakini si lazima.

**Q: Naweza kutumia kamera nyingine badala ya Tapo?**
Kamera yoyote inayounga mkono ONVIF + RTSP inapaswa kufanya kazi. Tapo C220 ndiyo tumetumia kwa majaribio.

**Q: Je, data yangu inatumwa kokote?**
Picha na maandiko yanatumwa kwa API ya LLM uliyouchagua kwa usindikaji. Kumbukumbu zinawekwa katika eneo hili kwa ndani kwenye `~/.familiar_ai/`.

**Q: Kwa nini wakala anaandika `（...）` badala ya kuzungumza?**
Hakikisha `ELEVENLABS_API_KEY` imewekwa. Bila hiyo, sauti inazuiliwa na wakala anarejelea maandiko.

## Muktadha wa kiufundi

Unataka kujua inavyofanya kazi? Tazama [docs/technical.md](./docs/technical.md) kwa utafiti na maamuzi ya muundo nyuma ya familiar-ai — ReAct, SayCan, Reflexion, Voyager, mfumo wa tamaa, na mengineyo.

---

## Mchango

familiar-ai ni jaribio wazi. Ikiwa yoyote ya haya inakuvutia — kiufundi au kifalsafa — michango inakaribishwa sana.

**Mijadala mizuri ya kuanzia:**

| Eneo | Kinachohitajika |
|------|---------------|
| Vifaa vipya | Msaada kwa kamera zaidi (RTSP, IP Webcam), microphones, actuators |
| Zana mpya | Utafutaji wa wavuti, otomatisishaji wa nyumbani, kalenda, chochote kupitia MCP |
| Sehemu zilizopangwa | LLM yoyote au mfano wa ndani unaofaa kwa kiolesura cha `stream_turn` |
| Sanamu za tabia | ME.md mifano kwa lugha tofauti na tabia |
| Utafiti | Mifano bora ya tamaa, uokoaji wa kumbukumbu, kuhimiza nadharia ya akili |
| Nyaraka | Makaratasi, mwongozo, tafsiri |

Tazama [CONTRIBUTING.md](./CONTRIBUTING.md) kwa usanidi wa maendeleo, mtindo wa kanuni, na miongozo ya PR.

Ikiwa hujui wapi kuanzia, [fungua suala](https://github.com/lifemate-ai/familiar-ai/issues) — niko radhi kukuelekeza katika njia sahihi.

---

## Leseni

[MIT](./LICENSE)
