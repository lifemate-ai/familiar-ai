```markdown
# familiar-ai 🐾

**En AI som lever sammen med deg** — med øyne, stemme, bein og minne.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Tilgjengelig på 74 språk](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai er en AI-kompanjong som bor i hjemmet ditt. Sett det opp på minutter. Ingen koding nødvendig.

Det oppfatter den virkelige verden gjennom kameraer, beveger seg rundt på en robotkropp, snakker høyt og husker det den ser. Gi det et navn, skriv dens personlighet, og la det bo med deg.

## Hva den kan gjøre

- 👁 **Se** — tar bilder fra et Wi-Fi PTZ-kamera eller USB-webkamera
- 🔄 **Se rundt** — panorering og neigen av kameraet for å utforske omgivelsene
- 🦿 **Bevege seg** — kjører en robotstøvsuger for å vandre rundt i rommet
- 🗣 **Snakke** — snakker via ElevenLabs TTS
- 🎙 **Lytte** — hands-free talebehandling via ElevenLabs Realtime STT (opt-in)
- 🧠 **Huske** — lagrer aktivt og husker minner med semantisk søk (SQLite + innbøttinger)
- 🫀 **Teori om sinn** — tar den andre personens perspektiv før den svarer
- 💭 **Ønske** — har sine egne interne drivkrefter som utløser autonom atferd

## Hvordan det fungerer

familiar-ai kjører en [ReAct](https://arxiv.org/abs/2210.03629) løkke drevet av ditt valg av LLM. Den oppfatter verden gjennom verktøy, tenker på hva den skal gjøre neste, og handler — akkurat som et menneske ville gjort.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Når den er inaktiv, handler den på sine egne ønsker: nysgjerrighet, ønsker å se ut, savner personen den bor med.

## Komme i gang

### 1. Installer uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Eller: `winget install astral-sh.uv`

### 2. Installer ffmpeg

ffmpeg er **nødvendig** for kamera bildedekning og lydavspilling.

| OS | Kommando |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — eller last ned fra [ffmpeg.org](https://ffmpeg.org/download.html) og legg til PATH |
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

**Minimum påkrevd:**

| Variabel | Beskrivelse |
|----------|-------------|
| `PLATFORM` | `anthropic` (standard) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Din API-nøkkel for den valgte plattformen |

**Valgfritt:**

| Variabel | Beskrivelse |
|----------|-------------|
| `MODEL` | Modellnavn (fornuftige standarder per plattform) |
| `AGENT_NAME` | Vist navn i TUI (f.eks. `Yukine`) |
| `CAMERA_HOST` | IP-adresse til ditt ONVIF/RTSP-kamera |
| `CAMERA_USER` / `CAMERA_PASS` | Kamera-legitimasjon |
| `ELEVENLABS_API_KEY` | For stemmeutgang — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` for å aktivere alltid-på hands-free taledekning (krever `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Hvor lyden skal spilles: `local` (PC-høyttaler, standard) \| `remote` (kamera-høyttaler) \| `both` |
| `THINKING_MODE` | Kun Anthropic — `auto` (standard) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptiv tenkeinnsats: `high` (standard) \| `medium` \| `low` \| `max` (Kun Opus 4.6) |

### 5. Lag din familiar

```bash
cp persona-template/en.md ME.md
# Rediger ME.md — gi det et navn og personlighet
```

### 6. Kjør

**macOS / Linux / WSL2:**
```bash
./run.sh             # Tekstlig TUI (anbefalt)
./run.sh --no-tui    # Plain REPL
```

**Windows:**
```bat
run.bat              # Tekstlig TUI (anbefalt)
run.bat --no-tui     # Plain REPL
```

---

## Velge en LLM

> **Anbefalt: Kimi K2.5** — beste agentiske ytelse som er testet så langt. Legger merke til konteksten, stiller oppfølgingsspørsmål og handler autonomt på måter andre modeller ikke gjør. Priset likt som Claude Haiku.

| Plattform | `PLATFORM=` | Standardmodell | Hvor få nøkkel |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibel (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI-verktøy** (claude -p, ollama…) | `cli` | (kommandolinjen) | — |

**Kimi K2.5 `.env` eksempel:**
```env
PLATFORM=kimi
API_KEY=sk-...   # fra plattform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` eksempel:**
```env
PLATFORM=glm
API_KEY=...   # fra api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = tekstkun
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

> **Merk:** For å deaktivere lokale/NVIDIA-modeller, sett bare ikke `BASE_URL` til en lokal endepunkt som `http://localhost:11434/v1`. Bruk skyløsninger i stedet.

**CLI-verktøy `.env` eksempel:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt-argument
# MODEL=ollama run gemma3:27b  # Ollama — ingen {}, prompt går via stdin
```

---

## MCP-servere

familiar-ai kan koble seg til hvilken som helst [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Dette lar deg koble til ekstern minne, filsystemtilgang, nettsøk eller noe annet verktøy.

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
- **`stdio`**: starte en lokal undertask (`command` + `args`)
- **`sse`**: koble til en HTTP+SSE server (`url`)

Overskriv konfigurasjonsfilens plassering med `MCP_CONFIG=/path/to/config.json`.

---

## Maskinvare

familiar-ai fungerer med hvilken som helst maskinvare du har — eller ingen i det hele tatt.

| Del | Hva den gjør | Eksempel | Nødvendig? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ-kamera | Øyne + nakke | Tapo C220 (~$30) | **Anbefalt** |
| USB-webkamera | Øyne (fast) | Enhvilken UVC-kamera | **Anbefalt** |
| Robotstøvsuger | Bein | Enhvilken Tuya-kompatibel modell | Nei |
| PC / Raspberry Pi | Hjerne | Alt som kjører Python | **Ja** |

> **Et kamera anbefales sterkt.** Uten et kan familiar-ai fortsatt snakke — men den kan ikke se verden, som er liksom hele poenget.

### Minimal oppsett (ingen maskinvare)

Bare vil prøve det? Du trenger bare en API-nøkkel:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Kjør `./run.sh` (macOS/Linux/WSL2) eller `run.bat` (Windows) og start chatting. Legg til maskinvare mens du går.

### Wi-Fi PTZ-kamera (Tapo C220)

1. I Tapo-appen: **Innstillinger → Avansert → Kamera-konto** — opprett en lokal konto (ikke TP-Link-konto)
2. Finn kameraets IP i ruteren din enhetsliste
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

Det er to avspillingsmålsteder, kontrollert av `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC-høyttaler (standard)
TTS_OUTPUT=remote   # kun kamera-høyttaler
TTS_OUTPUT=both     # kamera-høyttaler + PC-høyttaler samtidig
```

#### A) Kamera-høyttaler (via go2rtc)

Sett `TTS_OUTPUT=remote` (eller `both`). Krever [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Last ned den kjørbare filen fra [utgivelsessiden](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Plasser og gi nytt navn:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x nødvendig

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Lag `go2rtc.yaml` i samme katalog:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Bruk de lokale kamera-kontoinformasjonene (ikke din TP-Link sky-konto).

4. familiar-ai starter go2rtc automatisk ved oppstart. Hvis kameraet ditt støtter toveis lyd (tilbakekanal), spilles stemmen fra kamera-høyttaleren.

#### B) Lokal PC-høyttaler

Den standard (`TTS_OUTPUT=local`). Prøver spillere i rekkefølge: **paplay** → **mpv** → **ffplay**. Også brukt som en fallback når `TTS_OUTPUT=remote` og go2rtc ikke er tilgjengelig.

| OS | Installer |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (eller `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — sett `PULSE_SERVER=unix:/mnt/wslg/PulseServer` i `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — last ned og legg til PATH, **eller** `winget install ffmpeg` |

> Hvis ingen lydspiller er tilgjengelig, genereres tale fortsatt — den vil bare ikke spille.

### Stemmeinnputt (Realtime STT)

Sett `REALTIME_STT=true` i `.env` for alltid-på, hands-free stemmeinput:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # samme nøkkel som TTS
```

familiar-ai strømmer mikrofonlyd til ElevenLabs Scribe v2 og auto-registrerer transkripsjoner når du pauser talingen. Ingen knapptrykk nødvendig. Sameksisterer med push-to-talk-modus (Ctrl+T).

---

## TUI

familiar-ai inkluderer en terminal UI bygget med [Textual](https://textual.textualize.io/):

- Rullbar samtalehistorikk med live streaming tekst
- Tab-fullføring for `/quit`, `/clear`
- Avbryt agenten midt i turen ved å skrive mens den tenker
- **Samtaleloggen** lagres automatisk til `~/.cache/familiar-ai/chat.log`

For å følge loggen i en annen terminal (nyttig for kopi-og-lim):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Personligheten til din familiar ligger i `ME.md`. Denne filen er gitignored — den er kun din.

Se [`persona-template/en.md`](./persona-template/en.md) for et eksempel, eller [`persona-template/ja.md`](./persona-template/ja.md) for en japansk versjon.

---

## FAQ

**Q: Fungerer det uten GPU?**
Ja. Inbøttingsmodellen (multilingual-e5-small) kjører fint på CPU. En GPU gjør det raskere, men er ikke nødvendig.

**Q: Kan jeg bruke et kamera annet enn Tapo?**
Alle kameraer som støtter ONVIF + RTSP bør fungere. Tapo C220 er det vi testet med.

**Q: Blir dataene mine sendt noe sted?**
Bilder og tekst sendes til din valgte LLM API for behandling. Minner lagres lokalt i `~/.familiar_ai/`.

**Q: Hvorfor skriver agenten `（...）` i stedet for å snakke?**
Sørg for at `ELEVENLABS_API_KEY` er satt. Uten den er stemmen deaktivert og agenten faller tilbake til tekst.

## Teknisk bakgrunn

Nysgjerrig på hvordan det fungerer? Se [docs/technical.md](./docs/technical.md) for forskningen og designbeslutningene bak familiar-ai — ReAct, SayCan, Reflexion, Voyager, ønskesystemet, og mer.

---

## Bidra

familiar-ai er et åpent eksperiment. Hvis noen av dette resonnerer med deg — teknisk eller filosofisk — er bidrag veldig velkomne.

**Gode steder å starte:**

| Område | Hva som trengs |
|------|---------------|
| Ny maskinvare | Støtte for flere kameraer (RTSP, IP Webcam), mikrofoner, aktuatorer |
| Nye verktøy | Nett-søk, hjemmeautomatisering, kalender, hva som helst via MCP |
| Nye backends | Enhvilken LLM eller lokal modell som passer til `stream_turn` grensesnittet |
| Persona-maler | ME.md maler for forskjellige språk og personligheter |
| Forskning | Bedre ønsker modeller, minne henting, teori-om-sinn prompting |
| Dokumentasjon | Veiledninger, gjennomganger, oversettelser |

Se [CONTRIBUTING.md](./CONTRIBUTING.md) for utviklingsoppsett, kode-stil og PR-retningslinjer.

Hvis du er usikker på hvor du skal starte, [åpne en sak](https://github.com/lifemate-ai/familiar-ai/issues) — glad for å peke deg i riktig retning.

---

## Lisens

[MIT](./LICENSE)
```
