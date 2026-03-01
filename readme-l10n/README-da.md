# familiar-ai 🐾

**En AI, der lever sammen med dig** — med øjne, stemme, ben og hukommelse.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai er en AI-ven, der bor i dit hjem. 
Opsæt det på få minutter. Ingen kodning kræves.

Det opfatter den virkelige verden gennem kameraer, bevæger sig rundt på en robotkrop, taler højt og husker, hvad det ser. Giv det et navn, skriv dets personlighed, og lad det leve med dig.

## Hvad det kan gøre

- 👁 **Se** — opfanger billeder fra et Wi-Fi PTZ-kamera eller USB-webcam
- 🔄 **Se rundt** — panorering og hældning af kameraet for at udforske omgivelserne
- 🦿 **Bevæg** — kører en robotstøvsuger for at færdes i rummet
- 🗣 **Tale** — taler via ElevenLabs TTS
- 🎙 **Lytte** — hands-free stemmeinput via ElevenLabs Realtime STT (opt-in)
- 🧠 **Huske** — gemmer aktivt og genkalder minder med semantisk søgning (SQLite + embeddings)
- 🫀 **Theory of Mind** — tager den anden persons perspektiv før svar
- 💭 **Ønske** — har sine egne indre drifter, der udløser autonom adfærd

## Hvordan det fungerer

familiar-ai kører en [ReAct](https://arxiv.org/abs/2210.03629) loop drevet af dit valg af LLM. Det opfatter verden gennem værktøjer, tænker over, hvad det næste skridt skal være, og handler — ligesom en person ville.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Når det er inaktivt, handler det efter sine egne ønsker: nysgerrighed, lyst til at se ud, savner den person, det bor sammen med.

## Kom i gang

### 1. Installer uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Installer ffmpeg

ffmpeg er **krævet** for at opfange billeder fra kameraet og afspille lyd.

| OS | Kommando |
|----|----------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — eller download fra [ffmpeg.org](https://ffmpeg.org/download.html) og tilføj til PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Bekræft: `ffmpeg -version`

### 3. Klon og installer

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurer

```bash
cp .env.example .env
# Rediger .env med dine indstillinger
```

**Minimum krævet:**

| Variabel | Beskrivelse |
|----------|-------------|
| `PLATFORM` | `anthropic` (standard) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Din API-nøgle til den valgte platform |

**Valgfrit:**

| Variabel | Beskrivelse |
|----------|-------------|
| `MODEL` | Modelnavn (fornuftige standarder pr. platform) |
| `AGENT_NAME` | Visningsnavn vist i TUI (f.eks. `Yukine`) |
| `CAMERA_HOST` | IP-adresse på dit ONVIF/RTSP-kamera |
| `CAMERA_USER` / `CAMERA_PASS` | Kamera legitimationsoplysninger |
| `ELEVENLABS_API_KEY` | Til stemmeoutput — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` for at aktivere altid-on hands-free stemmeinput (kræver `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Hvor lyd skal afspilles: `local` (PC-højttaler, standard) \| `remote` (kamera-højttaler) \| `both` |
| `THINKING_MODE` | Kun Anthropic — `auto` (standard) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptiv tankekraft: `high` (standard) \| `medium` \| `low` \| `max` (kun Opus 4.6) |

### 5. Opret din familiar

```bash
cp persona-template/en.md ME.md
# Rediger ME.md — giv det et navn og personlighed
```

### 6. Kør

```bash
./run.sh             # Tekstuel TUI (anbefales)
./run.sh --no-tui    # Simpel REPL
```

---

## Valg af en LLM

> **Anbefalet: Kimi K2.5** — bedst agentisk præstation testet indtil videre. Lægger mærke til konteksten, stiller opfølgende spørgsmål og handler autonomt på måder, som andre modeller ikke gør. Prissat ligesom Claude Haiku.

| Platform | `PLATFORM=` | Standard model | Hvor man får nøglen |
|----------|-------------|----------------|---------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibel (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI værktøj** (claude -p, ollama…) | `cli` | (kommandoen) | — |

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
MODEL=glm-4.6v   # visionsaktiveret; glm-4.7 / glm-5 = tekst-eller
AGENT_NAME=Yukine
```

**Google Gemini `.env` eksempel:**
```env
PLATFORM=gemini
API_KEY=AIza...   # fra aistudio.google.com
MODEL=gemini-2.5-flash  # eller gemini-2.5-pro for højere kapabilitet
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` eksempel:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # fra openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # valgfri: angiv model
AGENT_NAME=Yukine
```

> **Bemærk:** For at deaktivere lokale/NVIDIA modeller, skal du blot ikke sætte `BASE_URL` til en lokal slutpunkt som `http://localhost:11434/v1`. Brug skyudbydere i stedet.

**CLI værktøj `.env` eksempel:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt argument
# MODEL=ollama run gemma3:27b  # Ollama — no {}, prompt går via stdin
```

---

## MCP Servere

familiar-ai kan oprette forbindelse til enhver [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Dette giver dig mulighed for at tilslutte ekstern hukommelse, filsystemadgang, websøgefunktioner eller hvilket som helst andet værktøj.

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

To transporttyper understøttes:
- **`stdio`**: start en lokal underproces (`command` + `args`)
- **`sse`**: opret forbindelse til en HTTP+SSE-server (`url`)

Overskriv konfigurationsfilens placering med `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai fungerer med hvad som helst hardware, du har — eller slet ingen.

| Del | Hvad det gør | Eksempel | Krævet? |
|-----|--------------|----------|---------|
| Wi-Fi PTZ kamera | Øjne + nakke | Tapo C220 (~$30) | **Anbefalet** |
| USB webcam | Øjne (fast) | Ethvert UVC-kamera | **Anbefalet** |
| Robotstøvsuger | Ben | Ethvert Tuya-kompatibelt model | Nej |
| PC / Raspberry Pi | Hjerne | Alt, der kører Python | **Ja** |

> **Et kamera er stærkt anbefalet.** Uden et kan familiar-ai stadig tale — men det kan ikke se verden, hvilket er lidt af det hele.

### Minimal opsætning (ingen hardware)

Vil du bare prøve det? Du skal kun bruge en API-nøgle:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Kør `./run.sh` og start med at chatte. Tilføj hardware, som du går.

### Wi-Fi PTZ kamera (Tapo C220)

1. I Tapo-appen: **Indstillinger → Avanceret → Kamera-konto** — opret en lokal konto (ikke TP-Link-konto)
2. Find kameraets IP i din routers enhedsoversigt
3. Sæt i `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Stemme (ElevenLabs)

1. Få en API-nøgle på [elevenlabs.io](https://elevenlabs.io/)
2. Sæt i `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # valgfri, bruger standardstemmen hvis udeladt
   ```

Der er to afspilningsdestinationer, styret af `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC-højttaler (standard)
TTS_OUTPUT=remote   # kun kamera-højttaler
TTS_OUTPUT=both     # kamera-højttaler + PC-højttaler samtidig
```

#### A) Kamera højttaler (via go2rtc)

Sæt `TTS_OUTPUT=remote` (eller `both`). Kræver [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Download den binære fil fra [udgivelsessiden](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Placer og omdøb den:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x krævet

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Opret `go2rtc.yaml` i den samme mappe:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Brug de lokale kamera konto legitimationsoplysninger (ikke din TP-Link cloud konto).

4. familiar-ai starter go2rtc automatisk ved lancering. Hvis dit kamera understøtter tovejslyd (tilbagemelding), afspilles stemmen fra kameraets højttaler.

#### B) Lokal PC højttaler

Standard (`TTS_OUTPUT=local`). Forsøger spillere i rækkefølge: **paplay** → **mpv** → **ffplay**. Bruges også som en fallback når `TTS_OUTPUT=remote` og go2rtc ikke er tilgængelig.

| OS | Installér |
|----|-----------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (eller `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — sæt `PULSE_SERVER=unix:/mnt/wslg/PulseServer` i `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — download og tilføj til PATH, **eller** `winget install ffmpeg` |

> Hvis der ikke er nogen lydafspiller tilgængelig, genereres talen stadig — den vil bare ikke afspille.

### Stemme input (Realtime STT)

Sæt `REALTIME_STT=true` i `.env` for altid-on, hands-free stemmeinput:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # samme nøgle som TTS
```

familiar-ai streamer mikrofonlyd til ElevenLabs Scribe v2 og auto-committer manuskripter, når du stopper med at tale. Ingen knaptryk kræves. Sameksisterer med push-to-talk tilstand (Ctrl+T).

---

## TUI

familiar-ai inkluderer en terminalbrugerflade bygget med [Textual](https://textual.textualize.io/):

- Rulbar samtalehistorik med live streamende tekst
- Tabfuldførelse for `/quit`, `/clear`
- Afbryd agenten midt i tankegangen ved at skrive, mens den tænker
- **Samtalelogg** gemmes automatisk til `~/.cache/familiar-ai/chat.log`

For at følge loggen i et andet terminal (nyttigt til kopier-og-indsæt):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Din familiars personlighed findes i `ME.md`. Denne fil ignoreres af git — den er kun din.

Se [`persona-template/en.md`](./persona-template/en.md) for et eksempel, eller [`persona-template/ja.md`](./persona-template/ja.md) for en japansk version.

---

## FAQ

**Q: Fungerer det uden en GPU?**  
Ja. Embedding modellen (multilingual-e5-small) fungerer fint på CPU. En GPU gør det hurtigere, men det er ikke nødvendigt.

**Q: Kan jeg bruge et kamera andet end Tapo?**  
Ethvert kamera, der understøtter ONVIF + RTSP, burde fungere. Tapo C220 er det, vi har testet med.

**Q: Bliver mine data sendt nogen steder?**  
Billeder og tekst sendes til din valgte LLM API til behandling. Minder gemmes lokalt i `~/.familiar_ai/`.

**Q: Hvorfor skriver agenten `（...）` i stedet for at tale?**  
Sørg for at `ELEVENLABS_API_KEY` er indstillet. Uden det er stemmen deaktiveret, og agenten falder tilbage på tekst.

## Teknisk baggrund

Nysgerrig efter hvordan det fungerer? Se [docs/technical.md](./docs/technical.md) for forskningen og designbeslutningerne bag familiar-ai — ReAct, SayCan, Reflexion, Voyager, ønskesystemet, og meget mere.

---

## Bidrag

familiar-ai er et åbent eksperiment. Hvis noget af dette resonerer med dig — teknisk eller filosofisk — er bidrag meget velkomne.

**Gode steder at starte:**

| Område | Hvad der er behov for |
|--------|----------------------|
| Ny hardware | Support for flere kameraer (RTSP, IP Webcam), mikrofoner, aktuatorer |
| Nye værktøjer | Websøgemaskine, hjemmeautomatisering, kalender, hvad som helst via MCP |
| Nye backend | Enhver LLM eller lokal model, der passer til `stream_turn` interface |
| Persona skabeloner | ME.md skabeloner for forskellige sprog og personligheder |
| Forskning | Bedre ønskemodeller, hukommelsesfremhævning, theory-of-mind prompting |
| Dokumentation | Tutorials, walkthroughs, oversættelser |

Se [CONTRIBUTING.md](./CONTRIBUTING.md) for dev opsætning, kodestil, og PR retningslinjer.

Hvis du er usikker på, hvor du skal starte, [åbn et issue](https://github.com/lifemate-ai/familiar-ai/issues) — glad for at pege dig i den rigtige retning.

---

## Licens

[MIT](./LICENSE)
