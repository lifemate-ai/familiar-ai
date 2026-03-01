# familiar-ai 🐾

**'n KI wat langs jou leef** — met oë, stem, bene, en geheue.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Beskikbaar in 74 tale](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai is 'n KI metgesel wat in jou huis leef. Stel dit binne minute op. Geen koderings ervaring nodig nie.

Dit waarneem die werklike wêreld deur kamera's, beweeg rond op 'n robot liggaam, praat hardop, en onthou wat dit sien. Gee dit 'n naam, skryf sy persoonlikheid, en laat dit saam met jou leef.

## Wat dit kan doen

- 👁 **Sien** — neem beelde op van 'n Wi-Fi PTZ kamera of USB webcam
- 🔄 **Kyk rondom** — pan en kantel die kamera om die omgewing te verken
- 🦿 **Beweeg** — dryf 'n robot stofsuiweraar om die kamer te verken
- 🗣 **Praat** — praat via ElevenLabs TTS
- 🎙 **Luister** — hands-free steminvoer via ElevenLabs Realtime STT (opt-in)
- 🧠 **Onthou** — stoor aktief en roep herinneringe op met semantiese soektog (SQLite + embeddings)
- 🫀 **Teorie van die Gees** — neem die ander persoon se perspektief in voordat daar geantwoord word
- 💭 **Verlangen** — het sy eie interne dryfvere wat outonome gedrag onttrigger

## Hoe dit werk

familiar-ai hardloop 'n [ReAct](https://arxiv.org/abs/2210.03629) lus wat aangedryf word deur jou keuze van LLM. Dit waarneem die wêreld deur gereedskap, dink oor wat om volgende te doen, en tree op — net soos 'n mens sou.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Wanneer dit inactief is, tree dit op volgens sy eie verlangens: nuuskierigheid, wil om buite te kyk, en mis die persoon met wie dit leef.

## Begin

### 1. Installeer uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Of: `winget install astral-sh.uv`

### 2. Installeer ffmpeg

ffmpeg is **vereis** vir kamera beeldopname en klankweergave.

| OS | Opdrag |
|----|-------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — of aflaai van [ffmpeg.org](https://ffmpeg.org/download.html) en voeg by PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifieer: `ffmpeg -version`

### 3. Klone en installeer

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigureer

```bash
cp .env.example .env
# Wysig .env met jou instellings
```

**Minimum vereis:**

| Veranderlike | Beskrywing |
|--------------|-------------|
| `PLATFORM` | `anthropic` (standaard) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Jou API-sleutel vir die gekose platform |

**Opsioneel:**

| Veranderlike | Beskrywing |
|--------------|-------------|
| `MODEL` | Modelnaam (verstanding standaard per platform) |
| `AGENT_NAME` | Weergegewe naam in die TUI (bv. `Yukine`) |
| `CAMERA_HOST` | IP-adres van jou ONVIF/RTSP kamera |
| `CAMERA_USER` / `CAMERA_PASS` | Kamera geloofsbriewe |
| `ELEVENLABS_API_KEY` | Vir stemuitset — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` om altyd-aan hands-free steminvoer te aktiviseer (vereis `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Waar om klank te speel: `local` (PC luidspreker, standaard) \| `remote` (kamera luidspreker) \| `both` |
| `THINKING_MODE` | Anthropic slegs — `auto` (standaard) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Aanpasbare denkeffort: `high` (standaard) \| `medium` \| `low` \| `max` (Opus 4.6 slegs) |

### 5. Skep jou bekendheid

```bash
cp persona-template/en.md ME.md
# Wysig ME.md — gee dit 'n naam en persoonlikheid
```

### 6. Hardloop

**macOS / Linux / WSL2:**
```bash
./run.sh             # Tekstuele TUI (aanbeveel)
./run.sh --no-tui    # Eenvoudige REPL
```

**Windows:**
```bat
run.bat              # Tekstuele TUI (aanbeveel)
run.bat --no-tui     # Eenvoudige REPL
```

---

## Keuse van 'n LLM

> **Aanbeveel: Kimi K2.5** — beste agentiese prestasie tot dusver getoets. Merke konteks, vra opvolgevrae, en tree outonoom op op maniere wat ander modelle nie doen nie. Prijs soortgelyk aan Claude Haiku.

| Platform | `PLATFORM=` | Standaard model | Waar om sleutel te kry |
|----------|------------|-----------------|-----------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-verse (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (die opdrag) | — |

**Kimi K2.5 `.env` voorbeeld:**
```env
PLATFORM=kimi
API_KEY=sk-...   # van platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` voorbeeld:**
```env
PLATFORM=glm
API_KEY=...   # van api.z.ai
MODEL=glm-4.6v   # visie-geskikte; glm-4.7 / glm-5 = slegs teks
AGENT_NAME=Yukine
```

**Google Gemini `.env` voorbeeld:**
```env
PLATFORM=gemini
API_KEY=AIza...   # van aistudio.google.com
MODEL=gemini-2.5-flash  # of gemini-2.5-pro vir hoër kapasiteit
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` voorbeeld:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # van openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opsioneel: spesifiseer model
AGENT_NAME=Yukine
```

> **Nota:** Om plaaslike/NVIDIA modelle te deaktiveer, stel eenvoudig nie `BASE_URL` in op 'n plaaslike eindpunt soos `http://localhost:11434/v1`. Gebruik in plaas daarvan wolk verskaffers.

**CLI tool `.env` voorbeeld:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — geen {}, prompt gaan via stdin
```

---

## MCP Bedieners

familiar-ai kan aan enige [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server koppel. Dit laat jou toe om eksterne geheue, filesystem toegang, websoektog of enige ander gereedskap aan te sluit.

Konfigureer bedieners in `~/.familiar-ai.json` (dieselfde formaat as Claude Code):

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

Twee vervoertipes word ondersteun:
- **`stdio`**: begin 'n plaaslike subprocess (`command` + `args`)
- **`sse`**: koppel aan 'n HTTP+SSE server (`url`)

Oorheers die konfigurasie lêer ligging met `MCP_CONFIG=/path/to/config.json`.

---

## Hardeware

familiar-ai werk met enige hardeware wat jy het — of glad nie.

| Deel | Wat dit doen | Voorbeeld | Vereis? |
|------|-------------|-----------|---------|
| Wi-Fi PTZ kamera | Oë + nek | Tapo C220 (~$30) | **Aanbeveel** |
| USB webcam | Oë (vas) | Enige UVC kamera | **Aanbeveel** |
| Robot stofsuiweraar | Bene | Enige Tuya-kompatible model | Nee |
| PC / Raspberry Pi | Brein | Enige iets wat Python draai | **Ja** |

> **'n Kamera word sterk aanbeveel.** Sonder een, kan familiar-ai steeds praat — maar dit kan nie die wêreld sien nie, wat eintlik die hele punt is.

### Minimale opstelling (geen hardeware)

Wil net dit probeer? Jy het net 'n API-sleutel nodig:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Hardloop `./run.sh` (macOS/Linux/WSL2) of `run.bat` (Windows) en begin gesels. Voeg hardeware by soos jy gaan.

### Wi-Fi PTZ kamera (Tapo C220)

1. In die Tapo app: **Instellings → Gevorderde → Kamera Rekening** — skep 'n plaaslike rekening (nie TP-Link rekening nie)
2. Vind die kamera se IP in jou router se toestel lys
3. Stel in `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=jou-lokale-gebruiker
   CAMERA_PASS=jou-lokale-wagwoord
   ```

### Stem (ElevenLabs)

1. Kry 'n API-sleutel by [elevenlabs.io](https://elevenlabs.io/)
2. Stel in `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opsioneel, gebruik die standaard stem as weggelaat
   ```

Daar is twee weergawedoelwitte, beheer deur `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC luidspreker (standaard)
TTS_OUTPUT=remote   # kamera luidspreker net
TTS_OUTPUT=both     # kamera luidspreker + PC luidspreker gelyktydig
```

#### A) Kamera luidspreker (via go2rtc)

Stel `TTS_OUTPUT=remote` (of `both`). Vereis [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Laai die binêre lêer af vanaf die [vrygawes page](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Plaas en hernoem dit:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x benodig

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Skep `go2rtc.yaml` in dieselfde gids:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://JOU_CAM_GEbruiker:JOU_CAM_WAGWOORD@JOU_CAM_IP/stream1
   ```
   Gebruik die plaaslike kamera rekening geloofsbriewe (nie jou TP-Link wolk rekening nie).

4. familiar-ai begin go2rtc outomaties by lanseering. As jou kamera twee-rigting klank ondersteun (terugkanaal), speel die stem vanaf die kamera luidspreker.

#### B) Plaaslike PC luidspreker

Die standaard (`TTS_OUTPUT=local`). Probeer spelers in volgorde: **paplay** → **mpv** → **ffplay**. Ook gebruik as 'n terugval wanneer `TTS_OUTPUT=remote` en go2rtc nie beskikbaar is nie.

| OS | Installeer |
|----|-------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (of `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — stel `PULSE_SERVER=unix:/mnt/wslg/PulseServer` in `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — laai af en voeg by PATH, **of** `winget install ffmpeg` |

> As daar geen klankspeler beskikbaar is nie, word spraak steeds gegenereer — dit speel net nie.

### Stem invoer (Realtime STT)

Stel `REALTIME_STT=true` in `.env` vir altyd-aan, hands-free steminvoer:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # dieselfde sleutel as TTS
```

familiar-ai stroom mikrofoon geluid na ElevenLabs Scribe v2 en outomaties registreer transkripsies wanneer jy ophou praat. Geen knoppie druk nodig nie. Koexistensie met die druk-om-te-praat modus (Ctrl+T).

---

## TUI

familiar-ai sluit 'n terminal UI in wat gebou is met [Textual](https://textual.textualize.io/):

- Scrolbare gesprek geskiedenis met lewendige stroom teks
- Tab-voltooiing vir `/quit`, `/clear`
- Onderbreek die agent terwyl dit dink deur te tik terwyl dit aan die dink is
- **Gesprek log** outomaties gestoor in `~/.cache/familiar-ai/chat.log`

Om die log in 'n ander terminal te volg (nuttig vir kopie-plak):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Jou bekendheid se persoonlikheid leef in `ME.md`. Hierdie lêer is gitignored — dit is slegs joune.

Sien [`persona-template/en.md`](./persona-template/en.md) vir 'n voorbeeld, of [`persona-template/ja.md`](./persona-template/ja.md) vir 'n Japanse weergawe.

---

## VRAAG

**V: Werk dit sonder 'n GPU?**
Ja. Die embedding model (multilingual-e5-small) werk goed op CPU. 'n GPU maak dit vinniger, maar is nie vereis nie.

**V: Kan ek 'n kamera ander as Tapo gebruik?**
Enige kamera wat ONVIF + RTSP ondersteun, moet werk. Tapo C220 is wat ons getoets het.

**V: Word my data enige plek gestuur?**
Beelde en teks word gestuur na jou gekose LLM API vir verwerking. Herinneringe word plaaslik gestoor in `~/.familiar_ai/`.

**V: Waarom skryf die agent `（...）` in plaas van om te praat?**
Maak seker dat `ELEVENLABS_API_KEY` ingesteld is. Sonder dit, is die stem deaktiveer en val die agent terug na teks.

## Tegniese agtergrond

Nuuskierig oor hoe dit werk? Sien [docs/technical.md](./docs/technical.md) vir die navorsing en ontwerpbeslissings agter familiar-ai — ReAct, SayCan, Reflexion, Voyager, die verlangstelsel, en meer.

---

## Bydrae

familiar-ai is 'n oop eksperimente. As enige van hierdie met jou resoneer — tegnies of filosofies — is bydraes baie welkom.

**Goeie plekke om te begin:**

| Area | Wat is nodig |
|------|---------------|
| Nuwe hardeware | Ondersteuning vir meer kameras (RTSP, IP Webcam), mikrofone, actuators |
| Nuwe gereedskap | Web soektog, huis outomatisering, kalender, enigiets via MCP |
| Nuwe agterpette | Enige LLM of plaaslike model wat pas by die `stream_turn` interface |
| Persona templates | ME.md templates vir verskillende tale en persoonlikhede |
| Navorsing | Beter verlang modelle, geheue herwinning, teorie-van-die-gees prompting |
| Dokumentasie | Tutorials, stapsgewyse, vertalings |

Sien [CONTRIBUTING.md](./CONTRIBUTING.md) vir dev opstelling, kode styl, en PR riglyne.

As jy onseker is oor waar om te begin, [open 'n probleem](https://github.com/lifemate-ai/familiar-ai/issues) — gelukkig om jou in die regte rigting te wys.

---

## Lisensie

[MIT](./LICENSE)
