# familiar-ai 🐾

**En AI, der lever sammen med dig** — med øjne, stemme, ben og hukommelse.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Tilgængelig på 74 sprog](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai er en AI-ven, der lever i dit hjem. 
Sæt det op på få minutter. Ingen kodning krævet.

Det opfatter den virkelige verden gennem kameraer, bevæger sig rundt på en robotkrop, taler højt og husker, hvad det ser. Giv det et navn, skriv dens personlighed, og lad det bo sammen med dig.

## Hvad det kan gøre

- 👁 **Se** — fanger billeder fra et Wi-Fi PTZ-kamera eller USB-webcam
- 🔄 **Se rundt** — panorerer og tilter kameraet for at udforske omgivelserne
- 🦿 **Bevæge sig** — kører en robotstøvsuger for at færdes i rummet
- 🗣 **Tale** — taler via ElevenLabs TTS
- 🎙 **Lytte** — håndfri stemmeinddata via ElevenLabs Realtime STT (opt-in)
- 🧠 **Huske** — gemmer og husker aktivt minder med semantisk søgning (SQLite + embeddings)
- 🫀 **Teori om sind** — tager den andens perspektiv, før den svarer
- 💭 **Ønske** — har sine egne indre drifter, der udløser autonom adfærd

## Hvordan det fungerer

familiar-ai kører en [ReAct](https://arxiv.org/abs/2210.03629) løkke drevet af dit valg af LLM. Den opfatter verden gennem værktøjer, tænker over, hvad der skal gøres næste gang, og handler — ligesom en person ville.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Når den er inaktiv, handler den på sine egne ønsker: nysgerrighed, ønsker at se udenfor, savner personen, den lever sammen med.

## Kom godt i gang

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

ffmpeg er **påkrævet** for kamera billedefangst og lydafspilning.

| OS | Kommando |
|----|---------|
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

### 4. Konfigurere

```bash
cp .env.example .env
# Rediger .env med dine indstillinger
```

**Minimum påkrævet:**

| Variabel | Beskrivelse |
|----------|-------------|
| `PLATFORM` | `anthropic` (standard) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Din API-nøgle for den valgte platform |

**Valgfrit:**

| Variabel | Beskrivelse |
|----------|-------------|
| `MODEL` | Modelnavn (fornuftige standardindstillinger pr. platform) |
| `AGENT_NAME` | Visningsnavn vist i TUI (f.eks. `Yukine`) |
| `CAMERA_HOST` | IP-adresse for dit ONVIF/RTSP kamera |
| `CAMERA_USER` / `CAMERA_PASS` | Kameraoplysninger |
| `ELEVENLABS_API_KEY` | For stemmeoutput — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` for at aktivere altid-tændt håndfri stemmeinddata (kræver `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Hvor lyd skal afspilles: `local` (PC-højttaler, standard) \| `remote` (kamera-højttaler) \| `both` |
| `THINKING_MODE` | Kun Anthropic — `auto` (standard) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptiv tænkeindsats: `high` (standard) \| `medium` \| `low` \| `max` (kun Opus 4.6) |

### 5. Opret din familiar

```bash
cp persona-template/en.md ME.md
# Rediger ME.md — giv det et navn og personlighed
```

### 6. Kør

**macOS / Linux / WSL2:**
```bash
./run.sh             # Tekstuel TUI (anbefales)
./run.sh --no-tui    # Simpel REPL
```

**Windows:**
```bat
run.bat              # Tekstuel TUI (anbefales)
run.bat --no-tui     # Simpel REPL
```

---

## Vælge en LLM

> **Anbefalet: Kimi K2.5** — bedst agentisk præstation testet hidtil. Lægger mærke til konteksten, stiller opfølgende spørgsmål, og handler autonomt på måder, som andre modeller ikke gør. Prissat tilsvarende Claude Haiku.

| Platform | `PLATFORM=` | Standardmodel | Hvor man kan få nøgle |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibel (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI-værktøj** (claude -p, ollama…) | `cli` | (kommandoen) | — |

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
MODEL=glm-4.6v   # vision-aktiveret; glm-4.7 / glm-5 = tekstkun
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
MODEL=mistralai/mistral-7b-instruct  # valgfrit: specificer model
AGENT_NAME=Yukine
```

> **Bemærk:** For at deaktivere lokale/NVIDIA-modeller skal du simpelt set ikke indstille `BASE_URL` til en lokal slutpunkt som `http://localhost:11434/v1`. Brug i stedet cloud-udbydere.

**CLI-værktøj `.env` eksempel:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt-argument
# MODEL=ollama run gemma3:27b  # Ollama — ingen {}, prompt går via stdin
```

---

## MCP Servere

familiar-ai kan forbinde til enhver [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Dette lader dig tilslutte ekstern hukommelse, filsystemadgang, websøgnings, eller ethvert andet værktøj.

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
- **`stdio`**: lancerer en lokal underproces (`command` + `args`)
- **`sse`**: forbinder til en HTTP+SSE server (`url`)

Overskriv konfigurationsfilens placering med `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai fungerer med hvilket som helst hardware, du har — eller slet ingen.

| Del | Hvad den gør | Eksempel | Required? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kamera | Øjne + nakke | Tapo C220 (~$30, Eufy C220) | **Anbefales** |
| USB webcam | Øjne (fast) | Ethvert UVC kamera | **Anbefales** |
| Robotstøvsuger | Ben | Enhver Tuya-kompatibel model | Nej |
| PC / Raspberry Pi | Hjerne | Alt, der kører Python | **Ja** |

> **Et kamera anbefales stærkt.** Uden et, kan familiar-ai stadig tale — men den kan ikke se verden, hvilket er lidt af hele pointen.

### Minimal opsætning (ingen hardware)

Vil du bare prøve det? Du har kun brug for en API-nøgle:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Kør `./run.sh` (macOS/Linux/WSL2) eller `run.bat` (Windows) og begynd at chatte. Tilføj hardware, som du går.

### Wi-Fi PTZ kamera (Tapo C220)

1. I Tapo-appen: **Indstillinger → Avanceret → Kamera Konto** — opret en lokal konto (ikke TP-Link konto)
2. Find kameraets IP i din routers enhedsliste
3. Indstil i `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Wi-Fi Camera (Eufy C220)

[Eufy C220 on Amazon Japan](https://www.amazon.co.jp/dp/B0CQQQ5NZ1/)

> **Tested and confirmed working.** Follow these steps carefully — a few settings differ from Tapo.

1. In the Eufy Security app: go to the camera → **Settings → NAS(RTSP)** and enable it
2. Set **Authentication** to **Basic** (Digest authentication does NOT work)
3. Set a streaming username and password
4. Note the RTSP URL shown in the app (format: `rtsp://username:password@ip/live0`)
5. Set in `.env` — use the **full RTSP URL** as `CAMERA_HOST`:
   ```env
   CAMERA_HOST=rtsp://your-username:your-password@192.168.1.xxx/live0
   CAMERA_USERNAME=
   CAMERA_PASSWORD=
   ```
   Leave `CAMERA_USERNAME` and `CAMERA_PASSWORD` empty — credentials are already in the URL.

> **Note:** Eufy C220 allows only **one simultaneous RTSP connection**. Stop other apps connected to the camera before starting familiar-ai.


### Stemme (ElevenLabs)

1. Få en API-nøgle på [elevenlabs.io](https://elevenlabs.io/)
2. Indstil i `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # valgfrit, bruger standardstemmen hvis udeladt
   ```

Der er to afspilningsdestinationer, styret af `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC-højttaler (standard)
TTS_OUTPUT=remote   # kamera-højttaler kun
TTS_OUTPUT=both     # kamera-højttaler + PC-højttaler samtidigt
```

#### A) Kamera højttaler (via go2rtc)

Indstil `TTS_OUTPUT=remote` (eller `both`). Kræver [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Download binæren fra [udgivelsessiden](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Placer og omdøb den:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x påkrævet

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Opret `go2rtc.yaml` i samme mappe:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Brug de lokale kameraoplysninger (ikke din TP-Link cloud-konto).

4. familiar-ai starter go2rtc automatisk ved opstart. Hvis dit kamera understøtter tovejs lyd (backchannel), spiller stemmen fra kameraets højttaler.

#### B) Lokal PC-højttaler

Den standard (`TTS_OUTPUT=local`). Forsøger spillere i rækkefølge: **paplay** → **mpv** → **ffplay**. Også brugt som en fallback når `TTS_OUTPUT=remote` og go2rtc ikke er tilgængelig.

| OS | Installer |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (eller `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — indstil `PULSE_SERVER=unix:/mnt/wslg/PulseServer` i `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — download og tilføj til PATH, **eller** `winget install ffmpeg` |

> Hvis ingen lydafspiller er tilgængelig, genereres stadig tale — den vil bare ikke afspille.

### Stemmeinddata (Realtime STT)

Indstil `REALTIME_STT=true` i `.env` for altid-tændt, håndfri stemmeinddata:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # samme nøgle som TTS
```

familiar-ai streamer mikrofonlyd til ElevenLabs Scribe v2 og auto-kommitter transkripter, når du holder pause med at tale. Ingen knaptryk kræves. Sameksisterer med tryk-for-at-tale tilstand (Ctrl+T).

---

## TUI

familiar-ai inkluderer en terminal UI bygget med [Textual](https://textual.textualize.io/):

- Scrollerbar samtalehistorik med live streaming tekst
- Tabfuldførelse for `/quit`, `/clear`
- Afbryd agenten midt i en tur ved at skrive, mens den tænker
- **Samtalelog** auto-gemmes til `~/.cache/familiar-ai/chat.log`

For at følge loggen i en anden terminal (nyttigt til kopi-indsæt):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Din familiars personlighed lever i `ME.md`. Denne fil er gitignored — det er kun din.

Se [`persona-template/en.md`](./persona-template/en.md) for et eksempel, eller [`persona-template/ja.md`](./persona-template/ja.md) for en japansk version.

---

## FAQ

**Q: Fungerer det uden en GPU?**
Ja. Embedding-modellen (multilingual-e5-small) kører fint på CPU. En GPU gør det hurtigere, men den er ikke påkrævet.

**Q: Kan jeg bruge et kamera, der ikke er Tapo?**
Ethvert kamera, der understøtter Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: Bliver mine data sendt nogen steder?**
Billeder og tekst sendes til din valgte LLM API til behandling. Minder gemmes lokalt i `~/.familiar_ai/`.

**Q: Hvorfor skriver agenten `（...）` i stedet for at tale?**
Sørg for, at `ELEVENLABS_API_KEY` er indstillet. Uden det, er stemmen deaktiveret, og agenten falder tilbage til tekst.

## Teknisk baggrund

Nysgerrig på hvordan det fungerer? Se [docs/technical.md](./docs/technical.md) for forskningen og designbeslutningerne bag familiar-ai — ReAct, SayCan, Reflexion, Voyager, desire-systemet og mere.

---

## Bidrag

familiar-ai er et åbent eksperiment. Hvis noget af dette resonerer med dig — teknisk eller filosofisk — bidrag er meget velkomne.

**Gode steder at starte:**

| Område | Hvad der er nødvendigt |
|------|---------------|
| Nyt hardware | Support til flere kameraer (RTSP, IP Webcam), mikrofoner, aktuatorer |
| Nye værktøjer | Websøgnings, hjemmeautomatisering, kalender, alt via MCP |
| Nye backends | Enhver LLM eller lokal model, der passer til `stream_turn` interface |
| Persona skabeloner | ME.md skabeloner for forskellige sprog og personligheder |
| Forskning | Bedre ønsker modeller, hukommelsesudtræk, theory-of-mind prompting |
| Dokumentation | Tutorials, walkthroughs, oversættelser |

Se [CONTRIBUTING.md](./CONTRIBUTING.md) for udviklingsopsætning, kodestil og PR-retningslinjer.

Hvis du er usikker på, hvor du skal starte, [åbn et issue](https://github.com/lifemate-ai/familiar-ai/issues) — glad for at pege dig i den rigtige retning.

---

## Licens

[MIT](./LICENSE)

[→ English README](../README.md)
