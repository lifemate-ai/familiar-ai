# familiar-ai 🐾

**En AI som lever sammen med deg** — med øyne, stemme, bein og hukommelse.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai er en AI-kompanjong som bor i hjemmet ditt.
Sett det opp på minutter. Ingen koding kreves.

Den oppfatter den virkelige verden gjennom kameraer, beveger seg på en robotkropp, snakker høyt og husker hva den ser. Gi den et navn, skriv dens personlighet, og la den bo med deg.

## Hva den kan gjøre

- 👁 **Se** — tar bilder fra et Wi-Fi PTZ-kamera eller USB-webkamera
- 🔄 **Se seg rundt** — panorere og tilte kameraet for å utforske omgivelsene
- 🦿 **Bevege seg** — kjøre en robotstøvsuger for å utforske rommet
- 🗣 **Snakke** — snakker via ElevenLabs TTS
- 🎙 **Lytte** — håndfri stemmeinput via ElevenLabs Realtime STT (opt-in)
- 🧠 **Huske** — aktivt lagrer og henter minner med semantisk søk (SQLite + embeddings)
- 🫀 **Teori om sinn** — tar den andre personens perspektiv før den svarer
- 💭 **Ønske** — har sine egne indre drifter som utløser autonom atferd

## Slik fungerer det

familiar-ai kjører en [ReAct](https://arxiv.org/abs/2210.03629) løkke drevet av ditt valg av LLM. Den oppfatter verden gjennom verktøy, tenker på hva den skal gjøre neste, og handler — akkurat som en person ville gjort.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Når den er inaktiv, handler den på sine egne ønsker: nysgjerrighet, lyst til å se utenfor, savne personen den bor med.

## Komme i gang

### 1. Installer uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Installer ffmpeg

ffmpeg er **nødvendig** for kamerabildeopptak og avspilling av lyd.

| OS | Kommando |
|----|----------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — eller last ned fra [ffmpeg.org](https://ffmpeg.org/download.html) og legg det til PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Bekreft: `ffmpeg -version`

### 3. Klon og installer

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurer

```bash
cp .env.example .env
# Rediger .env med innstillingene dine
```

**Minimum krav:**

| Variable | Beskrivelse |
|----------|-------------|
| `PLATFORM` | `anthropic` (standard) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Din API-nøkkel for den valgte plattformen |

**Valgfritt:**

| Variable | Beskrivelse |
|----------|-------------|
| `MODEL` | Modellenavn (fornuftige standardverdier per plattform) |
| `AGENT_NAME` | Vist navn i TUI (f.eks. `Yukine`) |
| `CAMERA_HOST` | IP-adresse til ditt ONVIF/RTSP-kamera |
| `CAMERA_USER` / `CAMERA_PASS` | Kamera legitim informasjon |
| `ELEVENLABS_API_KEY` | For stemmeutgang — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` for å aktivere alltid-på håndfri stemmeinput (krever `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Hvor lyd skal spilles av: `local` (PC-høyttaler, standard) \| `remote` (kamera-høyttaler) \| `both` |
| `THINKING_MODE` | Kun Anthropic — `auto` (standard) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptiv tenkning innsats: `high` (standard) \| `medium` \| `low` \| `max` (kun Opus 4.6) |

### 5. Lag din familiar

```bash
cp persona-template/en.md ME.md
# Rediger ME.md — gi den et navn og personlighet
```

### 6. Kjør

```bash
./run.sh             # Tekstlig TUI (anbefalt)
./run.sh --no-tui    # Ren REPL
```

---

## Velge en LLM

> **Anbefalt: Kimi K2.5** — best agentisk ytelse testet så langt. Legger merke til kontekst, stiller oppfølgingsspørsmål, og handler autonomt på måter andre modeller ikke gjør. Priset omtrent som Claude Haiku.

| Plattform | `PLATFORM=` | Standardmodell | Hvor å få nøkkel |
|-----------|-------------|----------------|------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibel (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-leverandør) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI-verktøy** (claude -p, ollama…) | `cli` | (kommandoen) | — |

**Kimi K2.5 `.env` eksempel:**
```env
PLATFORM=kimi
API_KEY=sk-...   # fra platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` eksempel:**
```env
PLATFORM=glm
API_KEY=...   # fra api.z.ai
MODEL=glm-4.6v   # visjonsaktivert; glm-4.7 / glm-5 = kutt-uten tekst
AGENT_NAME=Yukine
```

**Google Gemini `.env` eksempel:**
```env
PLATFORM=gemini
API_KEY=AIza...   # fra aistudio.google.com
MODEL=gemini-2.5-flash  # eller gemini-2.5-pro for høyere kapasitet
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` eksempel:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # fra openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # valgfritt: spesifiser modell
AGENT_NAME=Yukine
```

> **Merk:** For å deaktivere lokale/NVIDIA-modeller, sett rett og slett ikke `BASE_URL` til en lokal endepunkt som `http://localhost:11434/v1`. Bruk sky-leverandører i stedet.

**CLI-verktøy `.env` eksempel:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — ingen {}, prompt går via stdin
```

---

## MCP-servere

familiar-ai kan koble til enhver [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Dette lar deg koble inn ekstern hukommelse, filsystemtilgang, web-søk, eller ethvert annet verktøy.

Konfigurer servere i `~/.familiar-ai.json` (samme format som Claude Code):

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

To transporttyper støttes:
- **`stdio`**: start en lokal subprocess (`command` + `args`)
- **`sse`**: koble til en HTTP+SSE-server (`url`)

Overskriv konfigurasjonsfilplasseringen med `MCP_CONFIG=/path/to/config.json`.

---

## Maskinvare

familiar-ai fungerer med hva som helst maskinvare du har — eller ingen i det hele tatt.

| Del | Hva det gjør | Eksempel | Nødvendig? |
|-----|--------------|----------|------------|
| Wi-Fi PTZ-kamera | Øyne + nakke | Tapo C220 (~$30) | **Anbefalt** |
| USB-webkamera | Øyne (fast) | Ethvert UVC-kamera | **Anbefalt** |
| Robotstøvsuger | Ben | Ethvert Tuya-kompatibelt modell | Nei |
| PC / Raspberry Pi | Hjerne | Hva som helst som kjører Python | **Ja** |

> **Et kamera anbefales sterkt.** Uten et, kan familiar-ai fortsatt snakke — men kan ikke se verden, som er hele poenget.

### Minimal oppsett (ingen maskinvare)

Bare vil prøve det? Du trenger bare en API-nøkkel:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Kjør `./run.sh` og start å chatte. Legg til maskinvare etter hvert.

### Wi-Fi PTZ-kamera (Tapo C220)

1. I Tapo-appen: **Innstillinger → Avansert → Kamera-konto** — opprett en lokal konto (ikke TP-Link-konto)
2. Finn kameraets IP i ruteren enhetsliste
3. Sett i `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Stemme (ElevenLabs)

1. Få en API-nøkkel på [elevenlabs.io](https://elevenlabs.io/)
2. Sett i `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # valgfritt, bruker standard stemme hvis utelatt
   ```

Det er to avspillingsdestinasjoner, kontrollert av `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC-høyttaler (standard)
TTS_OUTPUT=remote   # kun kamera-høyttaler
TTS_OUTPUT=both     # kamera-høyttaler + PC-høyttaler samtidig
```

#### A) Kamera-høyttaler (via go2rtc)

Sett `TTS_OUTPUT=remote` (eller `begge`). Krever [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Last ned den binære filen fra [utgivelsessiden](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Plassér og omdøp den:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x nødvendig

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Opprett `go2rtc.yaml` i samme katalog:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Bruk de lokale kamera-kontokredentialene (ikke din TP-Link sky-konto).

4. familiar-ai starter go2rtc automatisk ved oppstart. Hvis kameraet ditt støtter toveiskommunikasjon (tilbakemelding), spilles stemmen fra kamera-høyttaleren.

#### B) Lokal PC-høyttaler

Standard (`TTS_OUTPUT=local`). Prøver spillere i rekkefølge: **paplay** → **mpv** → **ffplay**. Også brukt som en fallback når `TTS_OUTPUT=remote` og go2rtc ikke er tilgjengelig.

| OS | Installer |
|----|-----------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (eller `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — sett `PULSE_SERVER=unix:/mnt/wslg/PulseServer` i `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — last ned og legg til PATH, **eller** `winget install ffmpeg` |

> Hvis ingen lyddriver er tilgjengelig, genereres fortsatt talen — den vil bare ikke spilles av.

### Stemmeinput (Realtime STT)

Sett `REALTIME_STT=true` i `.env` for alltid-på, håndfri stemmeinput:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # samme nøkkel som TTS
```

familiar-ai strømmer mikrofonlyd til ElevenLabs Scribe v2 og auto-forplikter transkripter når du pauser talen. Ingen knappetrykk nødvendig. Samcoexisterer med trykk-for-å-snakke-modus (Ctrl+T).

---

## TUI

familiar-ai inkluderer en terminal UI bygget med [Textual](https://textual.textualize.io/):

- Rullbar samtalehistorikk med live streaming tekst
- Tab-fullføring for `/quit`, `/clear`
- Avbryt agenten midt under omgangen ved å skrive mens den tenker
- **Samtalelog** auto-lagret til `~/.cache/familiar-ai/chat.log`

For å følge loggen i en annen terminal (nyttig for kopiering-og-lim):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Din familiars personlighet ligger i `ME.md`. Denne filen er gitignored — den er kun din.

Se [`persona-template/en.md`](./persona-template/en.md) for et eksempel, eller [`persona-template/ja.md`](./persona-template/ja.md) for en japansk versjon.

---

## FAQ

**Q: Fungerer det uten GPU?**
Ja. Embedding-modellen (multilingual-e5-small) kjører fint på CPU. En GPU gjør det raskere men er ikke nødvendig.

**Q: Kan jeg bruke et annet kamera enn Tapo?**
Ethvert kamera som støtter ONVIF + RTSP bør fungere. Tapo C220 er det vi testet med.

**Q: Blir dataene mine sendt noe sted?**
Bilder og tekst sendes til din valgte LLM API for behandling. Minner lagres lokalt i `~/.familiar_ai/`.

**Q: Hvorfor skriver agenten `（...）` i stedet for å snakke?**
Sørg for at `ELEVENLABS_API_KEY` er satt. Uten den, er stemmen deaktivert og agenten faller tilbake til tekst.

## Teknisk bakgrunn

Nysgjerrig på hvordan det fungerer? Se [docs/technical.md](./docs/technical.md) for forskningen og designavgjørelsene bak familiar-ai — ReAct, SayCan, Reflexion, Voyager, ønskesystemet, og mer.

---

## Bidra

familiar-ai er et åpent eksperiment. Hvis noen av dette resonnerer med deg — teknisk eller filosofisk — er bidrag hjertelig velkomne.

**Gode steder å starte:**

| Område | Hva som trengs |
|--------|----------------|
| Ny maskinvare | Støtte for flere kameraer (RTSP, IP-webkamera), mikrofoner, aktuatører |
| Nye verktøy | Web-søk, hjemmeautomatisering, kalender, alt via MCP |
| Nye bakender | Enhver LLM eller lokal modell som passer den `stream_turn` grensesnitt |
| Persona-maler | ME.md-maler for forskjellige språk og personligheter |
| Forskning | Bedre ønskemodeller, minnehenting, teori-om-sinn prompting |
| Dokumentasjon | Tutorials, walkthroughs, oversettelser |

Se [CONTRIBUTING.md](./CONTRIBUTING.md) for utviklingsoppsett, kode-stil, og PR-retningslinjer.

Hvis du er usikker på hvor du skal starte, [åpne et problem](https://github.com/lifemate-ai/familiar-ai/issues) — glad for å peke deg i riktig retning.

---

## Lisens

[MIT](./LICENSE)
