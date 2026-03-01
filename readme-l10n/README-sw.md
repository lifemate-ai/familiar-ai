# familiar-ai 🐾

**AI ambayo inaishi pamoja nawe** — yenye macho, sauti, miguu, na kumbukumbu.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ni mwenza wa AI anayekaa nyumbani kwako.
Ianzishe ndani ya dakika chache. Hakuna coding inahitajika.

Inatambua ulimwengu halisi kupitia kamera, inahamia kwenye mwili wa roboti, inazungumza kwa sauti, na inakumbuka kile inachokiona. Mpatie jina, andika tabia yake, na iachie kuishi pamoja nawe.

## Vitu inavyoweza kufanya

- 👁 **Kuona** — inachukua picha kutoka kwa kamera ya PTZ ya Wi-Fi au webcam ya USB
- 🔄 **Kuangalia kuzunguka** — inapanua na kugeuza kamera ili kuchunguza mazingira yake
- 🦿 **Kuhama** — inaendesha kivakuja cha roboti kuzunguka chumba
- 🗣 **Kuzungumza** — inazungumza kupitia ElevenLabs TTS
- 🎙 **Kusikiliza** — pembejeo ya sauti bila mikono kupitia ElevenLabs Realtime STT (opt-in)
- 🧠 **Kumbuka** — inapohifadhi na kukumbuka kumbukumbu kwa utafutaji wa maana (SQLite + embeddings)
- 🫀 **Nadharia ya Akili** — inachukua mtazamo wa mtu mwingine kabla ya kujibu
- 💭 **Tamani** — ina matarajio yake ya ndani ambayo huleta tabia huru

## Inavyofanya kazi

familiar-ai inayo mzunguko wa [ReAct](https://arxiv.org/abs/2210.03629) unaoendeshwa na chaguo lako la LLM. Inatambua ulimwengu kupitia zana, inafikiri nini kifanyike, na inatekeleza - kama vile mtu anavyofanya.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Wakati haina chochote, inatekeleza tamaa zake: udadisi, kutaka kuangalia nje, kutokuwepo na mtu anayekaa naye.

## Jinsi ya kuanza

### 1. Sakinisha uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Sakinisha ffmpeg

ffmpeg ni **lazima** kwa ajili ya kuchukuwa picha za kamera na kupiga sauti.

| OS | Amri |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — au pakua kutoka [ffmpeg.org](https://ffmpeg.org/download.html) na ongeza kwenye PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Thibitisha: `ffmpeg -version`

### 3. Clone na usakinishe

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

**Lazima iwe:**

| Kigezo | Maelezo |
|----------|-------------|
| `PLATFORM` | `anthropic` (chaguo la kawaida) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Funguo yako ya API kwa jukwaa ulilochagua |

**Hiari:**

| Kigezo | Maelezo |
|----------|-------------|
| `MODEL` | Jina la modeli (maelezo mazuri ya chaguo kwa kila jukwaa) |
| `AGENT_NAME` | Jina la kuonyesha linaloonyeshwa kwenye TUI (mfano: `Yukine`) |
| `CAMERA_HOST` | Anwani ya IP ya kamera yako ya ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Sifa za kamera |
| `ELEVENLABS_API_KEY` | Kwa matokeo ya sauti — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` ili kuwezesha pembejeo ya sauti bila mikono (inahitaji `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Mahali pa kupiga sauti: `local` (spika ya PC, chaguo la kawaida) \| `remote` (spika ya kamera) \| `both` |
| `THINKING_MODE` | Anthropic pekee — `auto` (chaguo la kawaida) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Jaribio la kufikiria linalobadilika: `high` (chaguo la kawaida) \| `medium` \| `low` \| `max` (Opus 4.6 pekee) |

### 5. Unda mwenza wako

```bash
cp persona-template/en.md ME.md
# Hariri ME.md — mpatie jina na tabia
```

### 6. Endesha

```bash
./run.sh             # TUI ya maandiko (inayopendekezwa)
./run.sh --no-tui    # REPL ya kawaida
```

---

## Kuchagua LLM

> **Inapendekezwa: Kimi K2.5** — utendaji bora wa agensi uliojaribiwa hadi sasa. Inatambua muktadha, inafanya maswali ya ziada, na inatekeleza kwa kujitegemea kwa njia ambazo modeli nyingine hazifanyi. Bei sawa na Claude Haiku.

| Jukwaa | `PLATFORM=` | Mfano wa chaguo | Wapi kupata funguo |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kampatibili (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (mtoa-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (amri) | — |

**Mfano wa `.env` wa Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # kutoka platform.moonshot.ai
AGENT_NAME=Yukine
```

**Mfano wa `.env` wa Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # kutoka api.z.ai
MODEL=glm-4.6v   # imewezesha kuona; glm-4.7 / glm-5 = maandiko pekee
AGENT_NAME=Yukine
```

**Mfano wa `.env` wa Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # kutoka aistudio.google.com
MODEL=gemini-2.5-flash  # au gemini-2.5-pro kwa uwezo zaidi
AGENT_NAME=Yukine
```

**Mfano wa `.env` wa OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # kutoka openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # hiari: andika mfano
AGENT_NAME=Yukine
```

> **Kumbuka:** Kuondoa modeli za ndani/NVIDIA, usiweke `BASE_URL` kwenye mwisho wa ndani kama `http://localhost:11434/v1`. Tumia watoa huduma wa wingu badala yake.

**Mfano wa CLI tool `.env`:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = kiashiria cha kutaka
# MODEL=ollama run gemma3:27b  # Ollama — hakuna {}, kiashiria kinatolewa kupitia stdin
```

---

## Servers za MCP

familiar-ai inaweza kuunganishwa na chochote [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Hii inakuwezesha kuingiza kumbukumbu za nje, ufikiaji wa mfumo wa faili, utafutaji wa wavuti, au zana nyingine yoyote.

Sanidi seva katika `~/.familiar-ai.json` (aina sawa na Claude Code):

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
- **`stdio`**: anza mchakato wa ndani (`command` + `args`)
- **`sse`**: ungana na seva ya HTTP+SSE (`url`)

Badilisha mahali pa faili la config kwa `MCP_CONFIG=/path/to/config.json`.

---

## Vifaa

familiar-ai inafanya kazi na vifaa vyovyote ulivyonavyo — au hakuna hata kimoja.

| Sehemu | Kazi yake | Mfano | Lazima? |
|------|-------------|---------|-----------|
| Kamera ya Wi-Fi PTZ | Macho + shingo | Tapo C220 (~$30) | **Inapendekezwa** |
| Webcam ya USB | Macho (imefungwa) | Kamera yoyote ya UVC | **Inapendekezwa** |
| Kivakuja cha roboti | Miguu | Mfano wowote unaoendana na Tuya | Hapana |
| PC / Raspberry Pi | Ubongo | Kitu chochote kinachofanya kazi na Python | **Ndio** |

> **Kamera inapendekezwa kwa nguvu.** Bila hiyo, familiar-ai inaweza bado kuzungumza — lakini haiwezi kuona ulimwengu, ambayo ndiyo maana yake kuu.

### Mipangilio ya chini (hakuna vifaa)

Unataka kujaribu tu? Unahitaji funguo ya API pekee:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Endesha `./run.sh` na anza kubishana. Ongeza vifaa kadri unavyoendelea.

### Kamera ya Wi-Fi PTZ (Tapo C220)

1. Katika programu ya Tapo: **Mipangilio → Kisasa → Akaunti ya Kamera** — unda akaunti ya ndani (sio akaunti ya TP-Link)
2. Pata IP ya kamera katika orodha ya vifaa vya router yako
3. Sanidi katika `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=mtumiaji-wako-wa-menomasi
   CAMERA_PASS=fewasha-yako-ya-menomasi
   ```

### Sauti (ElevenLabs)

1. Pata funguo ya API huko [elevenlabs.io](https://elevenlabs.io/)
2. Sanidi katika `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # hiari, inatumia sauti ya kawaida ikiwa haijafanikiwa
   ```

Kuna mahali pa kupiga sauti mawili, yanayodhibitiwa na `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # spika ya PC (chaguo la kawaida)
TTS_OUTPUT=remote   # spika ya kamera pekee
TTS_OUTPUT=both     # spika ya kamera + spika ya PC kwa wakati mmoja
```

#### A) Spika ya kamera (kupitia go2rtc)

Set `TTS_OUTPUT=remote` (au `both`). Inahitaji [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Pakua binary kutoka kwenye [kurasa za toleo](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Weka na uibadilishe jina:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # ruhusa ya chmod +x inahitajika

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Unda `go2rtc.yaml` katika saraka hiyo hiyo:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Tumia sifa za akaunti za ndani za kamera (sio akaunti yako ya wingu ya TP-Link).

4. familiar-ai inaanzisha go2rtc moja kwa moja, wakati wa uzinduzi. Ikiwa kamera yako ina sauti za pande mbili (backchannel), sauti itachezeshwa kutoka kwa spika ya kamera.

#### B) Spika ya PC ya ndani

Chaguo la kawaida (`TTS_OUTPUT=local`). Inajaribu wachezaji kwa mpangilio: **paplay** → **mpv** → **ffplay**. Pia hutumika kama akiba wakati `TTS_OUTPUT=remote` na go2rtc haiwezekani.

| OS | Sakinisha |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (au `paplay` kupitia `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — weka `PULSE_SERVER=unix:/mnt/wslg/PulseServer` katika `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — pakua na ongeza kwenye PATH, **au** `winget install ffmpeg` |

> Ikiwa hakuna mchezaji wa sauti anapatikana, hotuba bado inaundwa — haitachezwa tu.

### Pembejeo ya sauti (Realtime STT)

Weka `REALTIME_STT=true` katika `.env` kwa pembejeo ya sauti bila mikono daima:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # funguo sawa kama TTS
```

familiar-ai inastream sauti ya kipaza sauti kwa ElevenLabs Scribe v2 na kujiandikisha moja kwa moja maandiko unapoacha kuzungumza. Hakuna kitufe kinachohitajika. Inakutana na hali ya kusukuma kwa kuzungumza (Ctrl+T).

---

## TUI

familiar-ai inajumuisha UI ya terminal iliyoandaliwa na [Textual](https://textual.textualize.io/):

- Historia ya mazungumzo inayoweza kupita na maandiko yanayoendelea
- Kamusi ya tabo kwa `/quit`, `/clear`
- Kimsingi yachafua agenti katikati ya zamu kwa kuandika wakati inafikiri
- **Rekodi ya mazungumzo** huokolewa moja kwa moja kwenye `~/.cache/familiar-ai/chat.log`

Ili kufuatilia rekodi katika terminal nyingine (inasaidia kwa kunakili-na-kupasta):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Tabia ya mwenza wako inapatikana katika `ME.md`. Faili hii inaigizwa na git — ni yako pekee.

Tazama [`persona-template/en.md`](./persona-template/en.md) kwa mfano, au [`persona-template/ja.md`](./persona-template/ja.md) kwa toleo la Kijapani.

---

## Maswali Yanayoulizwa Mara kwa Mara

**Q: Je, inafanya kazi bila GPU?**
Ndio. Mfano wa embedding (multilingual-e5-small) unafanya kazi vizuri kwenye CPU. GPU inafanya kuwa ya haraka lakini haihitajiki.

**Q: Naweza kutumia kamera nyingine isipokuwa Tapo?**
Kamera yoyote inayounganisha ONVIF + RTSP inapaswa kufanya kazi. Tapo C220 ndiyo tuliyojaribu nayo.

**Q: Je, data zangu zinaenda wapi?**
Picha na maandiko huendelezwa kwenye API yako iliyochaguliwa ya LLM kwa usindikaji. Kumbukumbu zinahifadhiwa ndani katika `~/.familiar_ai/`.

**Q: Kwa nini agenti anaandika `（...）` badala ya kuzungumza?**
Hakikisha `ELEVENLABS_API_KEY` imewekwa. Bila hiyo, sauti inakuwa imezimwa na agenti inarudi kwenye maandiko.

## Muktadha wa Kihandisi

Unataka kujua jinsi inavyofanya kazi? Tazama [docs/technical.md](./docs/technical.md) kwa utafiti na maamuzi ya kubuni nyuma ya familiar-ai — ReAct, SayCan, Reflexion, Voyager, mfumo wa tamaa, na mengineyo.

---

## Kuchangia

familiar-ai ni jaribio wazi. Ikiwa yoyote kati ya haya inakuhusisha - kiufundi au kifalsafa - michango inakaribishwa sana.

**Maeneo mazuri ya kuanzia:**

| Eneo | Kinachohitajika |
|------|---------------|
| Vifaa vipya | Msaada kwa kamera zaidi (RTSP, IP Webcam), microphones, actuators |
| Zana mpya | Utafutaji wa wavuti, uhamasishaji wa nyumbani, kalenda, chochote kupitia MCP |
| Backends mpya | LLM yoyote au mfano wa ndani unaofaa kwa kiolesura cha `stream_turn` |
| Mifano ya tabia | Mifano ya ME.md kwa lugha na tabia tofauti |
| Utafiti | Mifano bora ya tamaa, utafutaji wa kumbukumbu, kuamsha nadharia ya akili |
| Hati | Miongozo, maelekezo, tafsiri |

Tazama [CONTRIBUTING.md](./CONTRIBUTING.md) kwa usakinishaji wa dev, mtindo wa msimbo, na miongozo ya PR.

Ikiwa hujui wapi kuanzia, [fungua tatizo](https://github.com/lifemate-ai/familiar-ai/issues) — furahi kuelekeza mahali sahihi.

---

## Leseni

[MIT](./LICENSE)
