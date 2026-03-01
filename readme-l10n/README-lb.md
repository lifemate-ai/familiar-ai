[→ English README](../README.md)

# familiar-ai 🐾

**Eng AI déi an der Nopesch vum Iech lieft** — mat Aen, Stëmm, Benen, an Erënnerung.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ass e AI Begleeder deen an Ärem Haus liewt.
Setzt et an an e puer Minutten. Keen Code néideg.

Et erkennt d'echte Welt duerch Kameren, beweegt sech op engem Roboterkierper, schwätzt, an erënnert wat et gesäit. Gebt et e Numm, schreiwt seng Perséinlechkeet, an loosst et mat Iech liewen.

## Wat et kann

- 👁 **Séih** — fänkt Biller vun enger Wi-Fi PTZ Kamera oder USB Webcam
- 🔄 **Kuckt ronderëm** — panen a tilten d'Kamera fir seng Ëmgebung ze exploréieren
- 🦿 **Bewegt** — féiert e Roboter-Stäuber am Raum
- 🗣 **Schwätzt** — schwätzt duerch ElevenLabs TTS
- 🎙 **Listener** — hands-free Stëmmeneingang duerch ElevenLabs Realtime STT (opt-in)
- 🧠 **Erënneren** — aktiv erhalend an erënnerend Erënnerungen mat semantescher Sich (SQLite + embeddings)
- 🫀 **Theory of Mind** — hëlt d'Perspektiv vum aneren éier et reagéiert
- 💭 **Wënsch** — huet seng eege intern Drécker déi autonom Verhalen ausléisen

## Wéi et funktionnéiert

familiar-ai leeft e [ReAct](https://arxiv.org/abs/2210.03629) Loop, déi powered by Ärer Wahl vum LLM ass. Et erkennt d'Welt duerch Werkzeeg, denkt iwwer wat et als Nächstes maachen soll, an handelt – just wéi eng Persoun et géif.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Wann et inaktiv ass, agéiert et op seng eegen Wënsch: Neugier, wëllt erauszekucken, vermëisst d'Persoun mat där et liewt.

## Ugefaangen

### 1. Installéiert uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Installéiert ffmpeg

ffmpeg ass **verlinkt** fir d'Bildcapturing vun der Kamera an d'Audioduerstellung.

| OS | Kommando |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — oder lued et vun [ffmpeg.org](https://ffmpeg.org/download.html) an der PATH bäi |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifiziert: `ffmpeg -version`

### 3. Klonéieren an installéieren

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfiguréieren

```bash
cp .env.example .env
# Editéiert .env mat Äre Setzunge
```

**Minimum néideg:**

| Variabel | Beschreiwung |
|----------|-------------|
| `PLATFORM` | `anthropic` (standard) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Ären API Schlüssel fir d'gewielt Plattform |

**Optiounnal:**

| Variabel | Beschreiwung |
|----------|-------------|
| `MODEL` | Modellnumm (sënnvoll Standarden pro Plattform) |
| `AGENT_NAME` | Weisen Numm deen am TUI ugewise gëtt (z.B. `Yukine`) |
| `CAMERA_HOST` | IP Adress vun Ärer ONVIF/RTSP Kamera |
| `CAMERA_USER` / `CAMERA_PASS` | Kamera Identifikatioun |
| `ELEVENLABS_API_KEY` | Fir Stëmmenausgabe — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` fir ëmmer aktiv hands-free Stëmmeneingang zu aktivéieren (avangéiert `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Doheem fir Audios ze spillen: `local` (PC Lautsprecher, standard) \| `remote` (Kamerastoe) \| `both` |
| `THINKING_MODE` | Nëmmen fir Anthropic — `auto` (standard) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptiv Denkëmfeld: `high` (standard) \| `medium` \| `low` \| `max` (Opus 4.6 nëmmen) |

### 5. Schaf Ären Familiar

```bash
cp persona-template/en.md ME.md
# Editéiert ME.md — gitt et e Numm an Perséinlechkeet
```

### 6. Lauf

```bash
./run.sh             # Textual TUI (empfohlen)
./run.sh --no-tui    # Plang REPL
```

---

## Wielt eng LLM

> **Empfohlen: Kimi K2.5** — déi bescht agentesch Leeschtung vum Test bis elo. Bemierkt Kontext, freet no-nächsten Froen, an agéiert autonom opweisend aner Modeller et net maachen. Präislech ähnlech wéi Claude Haiku.

| Plattform | `PLATFORM=` | Standardmodell | Wou fir de Schlüssel ze kréien |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibel (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI Tool** (claude -p, ollama…) | `cli` | (de Kommando) | — |

**Kimi K2.5 `.env` Beispill:**
```env
PLATFORM=kimi
API_KEY=sk-...   # vun platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` Beispill:**
```env
PLATFORM=glm
API_KEY=...   # vun api.z.ai
MODEL=glm-4.6v   # visuelles aktivéiert; glm-4.7 / glm-5 = text-ounly
AGENT_NAME=Yukine
```

**Google Gemini `.env` Beispill:**
```env
PLATFORM=gemini
API_KEY=AIza...   # vun aistudio.google.com
MODEL=gemini-2.5-flash  # oder gemini-2.5-pro fir méi Fäegkeet
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` Beispill:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # vun openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # optiounal: spezifizéieren Modell
AGENT_NAME=Yukine
```

> **Bemierkung:** Fir lokal/NVIDIA Modeller ze deaktivéieren, setzt einfach net `BASE_URL` op eng lokal Endpoint wéi `http://localhost:11434/v1`. Benotzt cloud Provider amplaz.

**CLI Tool `.env` Beispill:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — keng {}, prompt geet duerch stdin
```

---

## MCP Server

familiar-ai kann mat all [MCP (Model Context Protocol)](https://modelcontextprotocol.io) Server verbannen. Dëst erlaabt Iech extern Erënnerungen, Dateisystemzougank, Websich, oder all aner Werkzeug ze verbannen.

Konfiguréiert Serveren an `~/.familiar-ai.json` (selwecht Format wéi Claude Code):

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

Zwei Transporttypen sinn ënnerstëtzt:
- **`stdio`**: start e lokale Subprozess (`command` + `args`)
- **`sse`**: verbannen mat engem HTTP+SSE Server (`url`)

Iwwerschreiwen d'Config-Datei Plaz mat `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai funktionéiert mat all Hardware déi Dir hutt — oder keng.

| Deel | Wat et mécht | Beispill | Néideg? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ Kamera | Aen + Hals | Tapo C220 (~$30) | **Empfohl** |
| USB Webcam | Aen (fësch) | All UVC Kamera | **Empfohl** |
| Roboter-Stäuber | Benen | All Tuya-kompatibel Modell | Nee |
| PC / Raspberry Pi | Geescht | Anything dat Python leeft | **Jo** |

> **Eng Kamera ass staark recommandéiert.** Ouni eng, kann familiar-ai nach ëmmer schwätzen — awer et kann d'Welt net gesin, wat e gewësse Punkt ass.

### Minimal Setup (keine Hardware)

Mocht Dir just wëllen et probéieren? Dir braucht nëmmen e API Schlüssel:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Féiert `./run.sh` aus an startet ze schwätzen. Füügt Hardware während der Zäit bäi.

### Wi-Fi PTZ Kamera (Tapo C220)

1. Am Tapo App: **Settings → Advanced → Camera Account** — erstellt en local Konto (net TP-Link Konto)
2. Fannt d'Kamera IP an der Lëscht vun Är Router
3. Setzt an `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Stëmm (ElevenLabs)

1. Kritt en API Schlüssel op [elevenlabs.io](https://elevenlabs.io/)
2. Setzt an `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # optiounal, benotzt Standardstëmm wann ausgeschloss
   ```

Et ginn zwou Spillplacken, kontrolléiert duerch `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC Lautsprecher (standard)
TTS_OUTPUT=remote   # Kamerastoe nëmmen
TTS_OUTPUT=both     # Kamerastoe + PC Lautsprecher zur selwechter Zäit
```

#### A) Kamera Lautsprecher (via go2rtc)

Setzt `TTS_OUTPUT=remote` (oder `both`). Benotzt [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Lued d'binary vum [releases Seite](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Plazéiert a renomméiert et:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x néideg

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Erstellt `go2rtc.yaml` am selwechte Verzeichnis:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Benotzt d'local Kamera Konto Identifikatioun (net Äre TP-Link Cloud Konto).

4. familiar-ai starten go2rtc automatesch bei Launch. Wann Är Kamera zweetwech Audio (Retour-Link) ënnerstëtzt, spillt d'Audio vum Kamera Lautsprecher.

#### B) Lokalen PC Lautsprecher

De Standard (`TTS_OUTPUT=local`). Versuchersspillere geet an der Rei: **paplay** → **mpv** → **ffplay**. Och benotzt als Backup wann `TTS_OUTPUT=remote` an go2rtc net verfügbar ass.

| OS | Installéiert |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (oder `paplay` iwwer `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — setzt `PULSE_SERVER=unix:/mnt/wslg/PulseServer` an `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — lued et erof an der PATH bäi, **oder** `winget install ffmpeg` |

> Wann keng Audio Spillere verfügbar sinn, gëtt d'Sprooch nach ëmmer generéiert — et wäert just net spillen.

### Stëmmeneingang (Realtime STT)

Setzt `REALTIME_STT=true` an `.env` fir ëmmer aktiv, hands-free Stëmmeneingang:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # selwechte Schlüssel wéi TTS
```

familiar-ai streamt Mikrofon Audio u ElevenLabs Scribe v2 an auto-commits Transkripten wann Dir stopt ze schwätzen. Keen Knäppchen ass noutwenneg. Koexistéiert mat der Pfeif-Talk Mod (Ctrl+T).

---

## TUI

familiar-ai enthält eng Terminal UI gebaut mat [Textual](https://textual.textualize.io/):

- Scrollable Gespréichsgeschicht mat live Streamtext
- Tab-completion fir `/quit`, `/clear`
- Stéiert den Agent während der Turn andeems Dir schreift während et denkt
- **Gespréichslog** automatesch gespäichert an `~/.cache/familiar-ai/chat.log`

Fir de Log an engem aneren Terminal ze verfollegen (nuttzbar fir Kopie-Paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persoun (ME.md)

Är familiar's Perséinlechkeet liewt an `ME.md`. Dës Datei ass gitignored — et ass nëmme fir Iech.

Säit [`persona-template/en.md`](./persona-template/en.md) fir e Beispill, oder [`persona-template/ja.md`](./persona-template/ja.md) fir eng japanesch Versioun.

---

## FAQ

**Q: Funktionéiert et ouni GPU?**
Jo. D'Schema Modell (multilingual-e5-small) leeft gutt op der CPU. Eng GPU mécht et méi séier, ass awer net néideg.

**Q: Kann ech eng Kamera benotzen déi net Tapo ass?**
Jeder Kamera déi ONVIF + RTSP ënnerstëtzt soll funktionéieren. Tapo C220 ass déi, déi mir getest hunn.

**Q: Gëtt meng Donnéeën iergendwou geschéckt?**
Biller a Text ginn un Äre gewielte LLM API fir d'Verarbeitung geschéckt. Erënnerungen sinn lokal an `~/.familiar_ai/` gespäichert.

**Q: Firwat schreift den Agent `（...）` amplaz ze schwätzen?**
Sëcheren, datt `ELEVENLABS_API_KEY` setzt. Ouni et ass d'Sprooch deaktivéiert an den Agent fällt zréck op Text.

## Technesch Hannergrond

Interesséiert wéi et funktionnéiert? Kuckt [docs/technical.md](./docs/technical.md) fir d'Fuerschung an Desigentscheedungen hannert familiar-ai — ReAct, SayCan, Reflexion, Voyager, d'Wënschsystem, an méi.

---

## Contributing

familiar-ai ass e kloere Experiment. Wann eng vun dëser Informatioun Iech beréiert — technesch oder philosophesch — sinn d'Kontributiounen häerzlech wëllkomm.

**Gutt Plazen fir unzefänken:**

| Beräich | Wat gebraucht gëtt |
|------|---------------|
| Nei Hardware | Ënnerstëtzung fir méi Kameras (RTSP, IP Webcam), Mikrofonen, Aktuatoren |
| Nei Tools | Websich, Hausautomatiséierung, Kalenner, alles iwwer MCP |
| Nei Backends | All LLM oder lokal Modell dat mat der `stream_turn` Interface passt |
| Persoun Template | ME.md Templates fir verschiddener Sproochen an Perséinlechkeeten |
| Fuerschung | Besser Wënschmodeller, Erënnerungsretrieval, Theorie-vun-Mënsch Invitatioun |
| Dokumentatioun | Tutorials, Walkthroughs, Iwwersetzungen |

Kuckt [CONTRIBUTING.md](./CONTRIBUTING.md) fir dev Setup, Code Stil, an PR Richtlinnen.

Wann Dir net sécher sidd wou Dir unzefänken, [e probleme opmaachen](https://github.com/lifemate-ai/familiar-ai/issues) — gär bereet fir Iech an déi richteg Richtung ze weisen.

---

## Lizenz

[MIT](./LICENSE)
