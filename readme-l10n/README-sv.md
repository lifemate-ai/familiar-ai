[→ English README](../README.md)

# familiar-ai 🐾

**En AI som lever vid din sida** — med ögon, röst, ben och minne.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Tillgänglig på 74 språk](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai är en AI-kompanjon som lever i ditt hem. Sätt upp det på några minuter. Ingen kodning krävs.

Det uppfattar den verkliga världen genom kameror, rör sig runt på en robotkropp, pratar högt och minns vad det ser. Ge den ett namn, skriv dess personlighet och låt den leva med dig.

## Vad den kan göra

- 👁 **Se** — fångar bilder från en Wi-Fi PTZ-kamera eller USB-webbkamera
- 🔄 **Titta runt** — panorering och lutning av kameran för att utforska omgivningen
- 🦿 **Röra sig** — kör en robotdammsugare för att utforska rummet
- 🗣 **Tala** — pratar via ElevenLabs TTS
- 🎙 **Lyssna** — handsfree röstinmatning via ElevenLabs Realtime STT (opt-in)
- 🧠 **Minna** — lagrar aktivt och hämtar minnen med semantisk sökning (SQLite + inbäddningar)
- 🫀 **Theory of Mind** — tar den andra personens perspektiv innan den svarar
- 💭 **Önskan** — har sina egna interna drifter som utlöser autonomt beteende

## Hur det fungerar

familiar-ai kör en [ReAct](https://arxiv.org/abs/2210.03629) loop som drivs av ditt val av LLM. Den uppfattar världen genom verktyg, tänker på vad den ska göra härnäst och agerar — precis som en människa skulle.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

När den är inaktiv agerar den utifrån sina egna önskningar: nyfikenhet, vilja att titta ut, sakna personen den lever med.

## Komma igång

### 1. Installera uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Eller: `winget install astral-sh.uv`

### 2. Installera ffmpeg

ffmpeg är **nödvändigt** för kamerabildupptagning och ljuduppspelning.

| OS | Kommando |
|----|----------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — eller ladda ner från [ffmpeg.org](https://ffmpeg.org/download.html) och lägg till i PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifiera: `ffmpeg -version`

### 3. Klona och installera

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurera

```bash
cp .env.example .env
# Redigera .env med dina inställningar
```

**Minimikrav:**

| Variabel | Beskrivning |
|----------|-------------|
| `PLATFORM` | `anthropic` (standard) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Din API-nyckel för den valda plattformen |

**Valfritt:**

| Variabel | Beskrivning |
|----------|-------------|
| `MODEL` | Modellnamn (förnuftiga standarder per plattform) |
| `AGENT_NAME` | Visningsnamn som visas i TUI (t.ex. `Yukine`) |
| `CAMERA_HOST` | IP-adressen till din ONVIF/RTSP-kamera |
| `CAMERA_USER` / `CAMERA_PASS` | Kamerainloggningar |
| `ELEVENLABS_API_KEY` | För röstutmatning — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` för att aktivera alltid-på handsfree röstinmatning (kräver `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Var ljudet ska spelas: `local` (PC-högtalare, standard) \| `remote` (kamerahögtalare) \| `both` |
| `THINKING_MODE` | Endast Anthropic — `auto` (standard) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptiv tänkandeinsats: `high` (standard) \| `medium` \| `low` \| `max` (Endast Opus 4.6) |

### 5. Skapa din familiar

```bash
cp persona-template/en.md ME.md
# Redigera ME.md — ge den ett namn och personlighet
```

### 6. Kör

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textuell TUI (rekommenderas)
./run.sh --no-tui    # Plain REPL
```

**Windows:**
```bat
run.bat              # Textuell TUI (rekommenderas)
run.bat --no-tui     # Plain REPL
```

---

## Välja en LLM

> **Rekommenderad: Kimi K2.5** — bäst agentisk prestanda som testats hittills. Märker sammanhang, ställer följdfrågor och agerar autonomt på sätt som andra modeller inte gör. Prissatt liknande Claude Haiku.

| Plattform | `PLATFORM=` | Standardmodell | Var att få nyckel |
|-----------|-------------|-----------------|-------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibel (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-leverantör) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI-verktyg** (claude -p, ollama…) | `cli` | (kommandot) | — |

**Exempel på Kimi K2.5 `.env`:**
```env
PLATFORM=kimi
API_KEY=sk-...   # från platform.moonshot.ai
AGENT_NAME=Yukine
```

**Exempel på Z.AI GLM `.env`:**
```env
PLATFORM=glm
API_KEY=...   # från api.z.ai
MODEL=glm-4.6v   # visionsaktiverad; glm-4.7 / glm-5 = text-endast
AGENT_NAME=Yukine
```

**Exempel på Google Gemini `.env`:**
```env
PLATFORM=gemini
API_KEY=AIza...   # från aistudio.google.com
MODEL=gemini-2.5-flash  # eller gemini-2.5-pro för högre kapabilitet
AGENT_NAME=Yukine
```

**Exempel på OpenRouter.ai `.env`:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # från openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # valfritt: specificera modell
AGENT_NAME=Yukine
```

> **Obs:** För att stänga av lokala/NVIDIA-modeller, sätt helt enkelt inte `BASE_URL` till en lokal slutpunkt som `http://localhost:11434/v1`. Använd molnleverantörer istället.

**Exempel på CLI-verktyg `.env`:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt-argument
# MODEL=ollama run gemma3:27b  # Ollama — ingen {}, prompt går via stdin
```

---

## MCP-servrar

familiar-ai kan ansluta till valfri [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Detta låter dig ansluta extern minne, filsystemåtkomst, webbsökning, eller något annat verktyg.

Konfigurera servrar i `~/.familiar-ai.json` (samma format som Claude Code):

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

Två transporttyper stöds:
- **`stdio`**: starta en lokal subprocess (`command` + `args`)
- **`sse`**: anslut till en HTTP+SSE-server (`url`)

Överskriv konfigurationsfilens plats med `MCP_CONFIG=/path/to/config.json`.

---

## Hårdvara

familiar-ai fungerar med vilken hårdvara du än har — eller ingen alls.

| Del | Vad den gör | Exempel | Krävdes? |
|-----|-------------|---------|----------|
| Wi-Fi PTZ-kamera | Ögon + nacke | Tapo C220 (~$30) | **Rekommenderas** |
| USB-webbkamera | Ögon (fast) | Valfri UVC-kamera | **Rekommenderas** |
| Robotdammsugare | Ben | Valfri modell kompatibel med Tuya | Nej |
| PC / Raspberry Pi | Hjärna | Vad som helst som kör Python | **Ja** |

> **En kamera rekommenderas starkt.** Utan en kan familiar-ai fortfarande prata — men den kan inte se världen, vilket är ganska mycket poängen.

### Minimal installation (ingen hårdvara)

Vill du bara prova det? Du behöver bara en API-nyckel:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Kör `./run.sh` (macOS/Linux/WSL2) eller `run.bat` (Windows) och börja chatta. Lägg till hårdvara efterhand.

### Wi-Fi PTZ-kamera (Tapo C220)

1. I Tapo-appen: **Inställningar → Avancerat → Kamerakonto** — skapa ett lokalt konto (inte TP-Link-konto)
2. Hitta kamerans IP i din routers enhetslista
3. Ställ in i `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Röst (ElevenLabs)

1. Skaffa en API-nyckel på [elevenlabs.io](https://elevenlabs.io/)
2. Ställ in i `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # valfritt, använder standardröst om utelämnat
   ```

Det finns två uppspelningsdestinationer, kontrollerade av `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC-högtalare (standard)
TTS_OUTPUT=remote   # endast kamerahögtalare
TTS_OUTPUT=both     # kamerahögtalare + PC-högtalare samtidigt
```

#### A) Kamerahögtalare (via go2rtc)

Ställ in `TTS_OUTPUT=remote` (eller `both`). Kräver [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Ladda ner binären från [utgivningssidan](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Placera och döp om den:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x behövs

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Skapa `go2rtc.yaml` i samma katalog:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Använd de lokala kamerakontoinloggningarna (inte ditt TP-Link-molnkonto).

4. familiar-ai startar go2rtc automatiskt vid lansering. Om din kamera stöder tvåvägs ljud (backchannel), spelas rösten från kamerahögtalaren.

#### B) Lokal PC-högtalare

Standard (`TTS_OUTPUT=local`). Försöker spelare i ordning: **paplay** → **mpv** → **ffplay**. Används också som fallback när `TTS_OUTPUT=remote` och go2rtc inte är tillgängligt.

| OS | Installera |
|----|------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (eller `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — ställ in `PULSE_SERVER=unix:/mnt/wslg/PulseServer` i `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — ladda ner och lägg till i PATH, **eller** `winget install ffmpeg` |

> Om ingen ljudspelare är tillgänglig, genereras talet fortfarande — det spelas bara inte.

### Röstinmatning (Realtime STT)

Ställ in `REALTIME_STT=true` i `.env` för alltid-på, handsfree röstinmatning:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # samma nyckel som TTS
```

familiar-ai strömmar mikrofonljud till ElevenLabs Scribe v2 och auto-commitar transkriptioner när du pausar för att prata. Ingen knapptryckning krävs. Samverkar med tryck-för-att-prata-läget (Ctrl+T).

---

## TUI

familiar-ai inkluderar en terminal UI byggd med [Textual](https://textual.textualize.io/):

- Scrollbar konversationshistorik med direkt textströmning
- Tab-komplettering för `/quit`, `/clear`
- Avbryt agenten mitt under turen genom att skriva medan den tänker
- **Konversationslogg** auto-sparad till `~/.cache/familiar-ai/chat.log`

För att följa loggen i en annan terminal (användbart för kopiera-klistra):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Din familiars personlighet lever i `ME.md`. Denna fil är gitignored — den är endast din.

Se [`persona-template/en.md`](./persona-template/en.md) för ett exempel, eller [`persona-template/ja.md`](./persona-template/ja.md) för en japansk version.

---

## FAQ

**Q: Fungerar det utan en GPU?**
Ja. Inbäddningsmodellen (multilingual-e5-small) fungerar bra på CPU. En GPU gör det snabbare men är inte nödvändig.

**Q: Kan jag använda en kamera som inte är Tapo?**
Vilken kamera som stödjer ONVIF + RTSP bör fungera. Tapo C220 är vad vi testade med.

**Q: Skickas mina data någonstans?**
Bilder och text skickas till din valda LLM-API för bearbetning. Minnen lagras lokalt i `~/.familiar_ai/`.

**Q: Varför skriver agenten `（...）` istället för att tala?**
Se till att `ELEVENLABS_API_KEY` är inställt. Utan det är rösten inaktiverad och agenten faller tillbaka till text.

## Teknisk bakgrund

Nyfiken på hur det fungerar? Se [docs/technical.md](./docs/technical.md) för forskningen och designbesluten bakom familiar-ai — ReAct, SayCan, Reflexion, Voyager, önskesystemet och mer.

---

## Bidra

familiar-ai är ett öppet experiment. Om något av detta resonerar med dig — tekniskt eller filosofiskt — är bidrag mycket välkomna.

**Bra ställen att börja:**

| Område | Vad som behövs |
|--------|----------------|
| Ny hårdvara | Stöd för fler kameror (RTSP, IP Webcam), mikrofoner, aktuatorer |
| Nya verktyg | Webbsökning, hemautomation, kalender, vad som helst via MCP |
| Nya backend | Valfri LLM eller lokal modell som passar `stream_turn`-gränssnittet |
| Persona-mallar | ME.md-mallar för olika språk och personligheter |
| Forskning | Bättre önskemodeller, minneshämtning, teori-om-sinne-frågor |
| Dokumentation | Handledning, genomgångar, översättningar |

Se [CONTRIBUTING.md](./CONTRIBUTING.md) för utvecklingsinställningar, kodstil och PR-riktlinjer.

Om du är osäker på var du ska börja, [öppna ett problem](https://github.com/lifemate-ai/familiar-ai/issues) — jag hjälper gärna till med riktningen.

---

## Licens

[MIT](./LICENSE)
