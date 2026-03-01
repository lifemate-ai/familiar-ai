# familiar-ai 🐾

**En AI som lever vid din sida** — med ögon, röst, ben och minne.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai är en AI-kompanjon som bor i ditt hem. Ställ in den på några minuter. Ingen kodning krävs.

Den uppfattar den verkliga världen genom kameror, rör sig på en robotkropp, talar högt och minns vad den ser. Ge den ett namn, skriv dess personlighet och låt den leva med dig.

## Vad den kan göra

- 👁 **Se** — fångar bilder från en Wi-Fi PTZ-kamera eller USB-webbkamera
- 🔄 **Titta omkring** — panorera och luta kameran för att utforska omgivningen
- 🦿 **Röra sig** — kör en robotdammsugare för att röra sig omkring i rummet
- 🗣 **Tala** — pratar via ElevenLabs TTS
- 🎙 **Lyssna** — handsfree röstinmatning via ElevenLabs Realtime STT (opt-in)
- 🧠 **Minna** — lagrar och återkallar aktivt minnen med semantisk sökning (SQLite + inbäddningar)
- 🫀 **Theory of Mind** — tar den andres perspektiv innan den svarar
- 💭 **Önskan** — har sina egna interna drivkrafter som utlöser autonomt beteende

## Hur det fungerar

familiar-ai kör en [ReAct](https://arxiv.org/abs/2210.03629) loop drivs av ditt val av LLM. Den uppfattar världen genom verktyg, tänker på vad den ska göra nästa gång och agerar — precis som en person skulle.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

När den är inaktiv agerar den på sina egna önskningar: nyfikenhet, vilja att titta ut, sakna den person den lever med.

## Komma igång

### 1. Installera uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Installera ffmpeg

ffmpeg är **krävs** för kamerabildtagning och ljuduppspelning.

| OS | Kommando |
|----|---------|
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

**Minst krav:**

| Variabel | Beskrivning |
|----------|-------------|
| `PLATFORM` | `anthropic` (standard) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Din API-nyckel för den valda plattformen |

**Valfri:**

| Variabel | Beskrivning |
|----------|-------------|
| `MODEL` | Modellnamn (förnuftiga standardinställningar per plattform) |
| `AGENT_NAME` | Visningsnamn som visas i TUI (t.ex. `Yukine`) |
| `CAMERA_HOST` | IP-adress till din ONVIF/RTSP-kamera |
| `CAMERA_USER` / `CAMERA_PASS` | Kamerautgifter |
| `ELEVENLABS_API_KEY` | För röstutdata — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` för att aktivera alltid-aktiv handsfree röstinmatning (kräver `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Var att spela ljud: `local` (PC-högtalare, standard) \| `remote` (kamerahögtalare) \| `both` |
| `THINKING_MODE` | Anthropic endast — `auto` (standard) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptiv tankemöda: `high` (standard) \| `medium` \| `low` \| `max` (Endast Opus 4.6) |

### 5. Skapa din familiar

```bash
cp persona-template/en.md ME.md
# Redigera ME.md — ge det ett namn och en personlighet
```

### 6. Kör

```bash
./run.sh             # Textuell TUI (rekommenderad)
./run.sh --no-tui    # Plain REPL
```

---

## Välja en LLM

> **Rekommenderad: Kimi K2.5** — bästa agentiska prestanda som testats hittills. Noterar kontext, ställer följdfrågor och agerar autonomt på sätt som andra modeller inte gör. Prissatt liknande Claude Haiku.

| Plattform | `PLATFORM=` | Standardmodell | Var att få nyckel |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibel (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-leverantör) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI-verktyg** (claude -p, ollama…) | `cli` | (kommandot) | — |

**Kimi K2.5 `.env` exempel:**
```env
PLATFORM=kimi
API_KEY=sk-...   # från platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` exempel:**
```env
PLATFORM=glm
API_KEY=...   # från api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` exempel:**
```env
PLATFORM=gemini
API_KEY=AIza...   # från aistudio.google.com
MODEL=gemini-2.5-flash  # eller gemini-2.5-pro för högre kapacitet
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` exempel:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # från openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # valfritt: specificera modell
AGENT_NAME=Yukine
```

> **Observera:** För att inaktivera lokala/NVIDIA-modeller, sätt bara inte `BASE_URL` till en lokal endpoint som `http://localhost:11434/v1`. Använd molnleverantörer istället.

**CLI-verktyg `.env` exempel:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — ingen {}, prompt går via stdin
```

---

## MCP-servrar

familiar-ai kan ansluta till valfri [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Detta låter dig koppla in extern minne, filsystemåtkomst, webbsökning eller något annat verktyg.

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
- **`sse`**: ansluta till en HTTP+SSE-server (`url`)

Överskriv konfigurationsfilens plats med `MCP_CONFIG=/path/to/config.json`.

---

## Hårdvara

familiar-ai fungerar med den hårdvara du har — eller ingen alls.

| Del | Vad den gör | Exempel | Nödvändig? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ-kamera | Ögon + nacke | Tapo C220 (~$30) | **Rekommenderad** |
| USB-webbkamera | Ögon (fast) | Valfri UVC-kamera | **Rekommenderad** |
| Robotdammsugare | Ben | Valfri Tuya-kompatibel modell | Nej |
| PC / Raspberry Pi | Hjärna | Vad som helst som kör Python | **Ja** |

> **En kamera rekommenderas starkt.** Utan en kan familiar-ai fortfarande prata — men den kan inte se världen, vilket är lite av hela poängen.

### Minimal uppsättning (ingen hårdvara)

Vill du bara prova? Du behöver bara en API-nyckel:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Kör `./run.sh` och börja chatta. Lägg till hårdvara efter hand.

### Wi-Fi PTZ-kamera (Tapo C220)

1. I Tapo-appen: **Inställningar → Avancerat → Kamera-konto** — skapa ett lokalt konto (inte TP-Link-konto)
2. Hitta kamerans IP i din routers enhetslista
3. Sätt i `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Röst (ElevenLabs)

1. Få en API-nyckel på [elevenlabs.io](https://elevenlabs.io/)
2. Sätt i `.env`:
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

Sätt `TTS_OUTPUT=remote` (eller `both`). Kräver [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Ladda ner binären från [releaser-sidan](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Placera och döp om den:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x krävs

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Skapa `go2rtc.yaml` i samma mapp:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Använd de lokala kamerakontouppgifterna (inte ditt TP-Link-molnkonto).

4. familiar-ai startar go2rtc automatiskt vid start. Om din kamera stödjer tvåvägs ljud (backchannel), spelas rösten från kamerans högtalare.

#### B) Lokal PC-högtalare

Standard (`TTS_OUTPUT=local`). Försöker spelare i ordning: **paplay** → **mpv** → **ffplay**. Används också som en fallback när `TTS_OUTPUT=remote` och go2rtc inte är tillgänglig.

| OS | Installera |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (eller `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — sätt `PULSE_SERVER=unix:/mnt/wslg/PulseServer` i `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — ladda ner och lägg till i PATH, **eller** `winget install ffmpeg` |

> Om ingen ljudspelare är tillgänglig, genereras fortfarande tal — det kommer bara inte att spelas.

### Röstinmatning (Realtime STT)

Sätt `REALTIME_STT=true` i `.env` för alltid-aktiv, handsfree röstinmatning:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # samma nyckel som TTS
```

familiar-ai strömmar mikrofonljud till ElevenLabs Scribe v2 och auto-sparar transkriptioner när du pausar talet. Ingen knapptryckning krävs. Samexisterar med tryck-till-prata-läget (Ctrl+T).

---

## TUI

familiar-ai inkluderar ett terminalgränssnitt byggt med [Textual](https://textual.textualize.io/):

- Bläddringsbar konversationhistoria med live-streamande text
- Tab-komplettering för `/quit`, `/clear`
- Avbryta agenten mitt i ett turnerande genom att skriva medan den tänker
- **Konversationslogg** auto-sparad till `~/.cache/familiar-ai/chat.log`

För att följa loggen i en annan terminal (användbar för kopiera-klistra):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Din familiars personlighet lever i `ME.md`. Denna fil ignoreras av git — den är endast din.

Se [`persona-template/en.md`](./persona-template/en.md) för ett exempel, eller [`persona-template/ja.md`](./persona-template/ja.md) för en japansk version.

---

## FAQ

**Q: Fungerar det utan GPU?**
Ja. Embedingsmodellen (multilingual-e5-small) fungerar fint på CPU. En GPU gör det snabbare men är inte nödvändig.

**Q: Kan jag använda en kamera som inte är Tapo?**
Vilken kamera som helst som stöder ONVIF + RTSP bör fungera. Tapo C220 är vad vi testade med.

**Q: Skickas mina data någonstans?**
Bilder och text skickas till din valda LLM API för behandling. Minnen lagras lokalt i `~/.familiar_ai/`.

**Q: Varför skriver agenten `（...）` istället för att tala?**
Se till att `ELEVENLABS_API_KEY` är inställd. Utan den inaktiveras röst och agenten faller tillbaka på text.

## Teknisk bakgrund

Nyfiken på hur det fungerar? Se [docs/technical.md](./docs/technical.md) för forskningen och designbesluten bakom familiar-ai — ReAct, SayCan, Reflexion, Voyager, önskesystemet, och mer.

---

## Bidra

familiar-ai är ett öppet experiment. Om något av detta resonerar med dig — tekniskt eller filosofiskt — är bidrag mycket välkomna.

**Bra ställen att börja på:**

| Område | Vad som behövs |
|------|---------------|
| Ny hårdvara | Stöd för fler kameror (RTSP, IP Webcam), mikrofoner, aktuatorer |
| Nya verktyg | Webbsökning, hemautomatisering, kalender, vad som helst via MCP |
| Nya backend | Vilken LLM eller lokal modell som passar `stream_turn` gränssnittet |
| Personaförmallar | ME.md-mallar för olika språk och personligheter |
| Forskning | Bättre önskemodeller, minnesåtervinning, theory-of-mind prompting |
| Dokumentation | Tutorials, genomgångar, översättningar |

Se [CONTRIBUTING.md](./CONTRIBUTING.md) för dev-uppsättning, kodstil och PR-riktlinjer.

Om du är osäker på var du ska börja, [öppna en issue](https://github.com/lifemate-ai/familiar-ai/issues) — gärna hjälpa dig i rätt riktning.

---

## Licens

[MIT](./LICENSE)
