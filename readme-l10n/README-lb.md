# familiar-ai 🐾

**Eng AI déi neben dir lieft** — mat Aen, Stëmm, Been, a Gedächtnis.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Available in 74 languages](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ass en AI Begleiter deen an dengem Heem lieft. 
Setz et an nëmmen e puer Minutten. Kee Code néideg.

Et erkennt d'ächt Welt duerch Kameras, bewegt sech op engem Roboterkierper, schwätzt, an erënnert sech un wat et gesäit. Gëff et e Numm, schreiw seng Perséinlechkeet, an loosst et mat dir liewen.

## Wat et kann

- 👁 **Sehen** — fänkt Biller vun enger Wi-Fi PTZ Kamera oder USB Webcam
- 🔄 **Rondrëm kucken** — panoraméiert an tilts d'Kamera fir seng Ëmfeld ze entdecken
- 🦿 **Bewegen** — féiert e Roboter-Stëbsauger ronderëm d'Zëmmer
- 🗣 **Sprechen** — schwätzt iwwer ElevenLabs TTS
- 🎙 **Héieren** — freihänschen Spriechinput iwwer ElevenLabs Realtime STT (op opt-in)
- 🧠 **Erënneren** — aktiv armazenéiert a rëckruff Gedächtnisser mat semantescher Sich (SQLite + Embeddings)
- 🫀 **Theory of Mind** — ass d'Perspektiv vun der anerer Persoun virun der Äntwert
- 💭 **Wënsch** — huet seng eegen intern Dréit déi autonom Verhalen ausléisen

## Wéi et funktionnéiert

familiar-ai betreibt eng [ReAct](https://arxiv.org/abs/2210.03629) Schleife déi vun der gewielter LLM ugedriwwe gëtt. Et erkennt d'Welt duerch Tools, denkt iwwer wat ze maachen, a handelt — just wéi eng Persoun.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Wann et roueg ass, handelt et baséiert op sengen eegenen Wënsch: Sënn fir Entdeckungen, wëll d'Welt vun der Dier ze gesin, vermësst d'Persoun déi mat et liewt.

## Ugefaangen

### 1. Installéiert uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Oder: `winget install astral-sh.uv`

### 2. Installéiert ffmpeg

ffmpeg ass **virdru** fir d'Fangung vun Kamera-Biller an Audio-Wiedergabe.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — oder eroflueden vun [ffmpeg.org](https://ffmpeg.org/download.html) an zur PATH derbäi setzen |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifizéieren: `ffmpeg -version`

### 3. Klonen an Installéieren

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfiguréieren

```bash
cp .env.example .env
# Edit .env mat deinen Astellungen
```

**Minimum néideg:**

| Variable | Beschreiwung |
|----------|--------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Déi API Schlüssel fir d'gewielte Plattform |

**Optional:**

| Variable | Beschreiwung |
|----------|--------------|
| `MODEL` | Modell Numm (sënnvoll Standards pro Plattform) |
| `AGENT_NAME` | E Display Numm am TUI (z.B. `Yukine`) |
| `CAMERA_HOST` | IP Adress vun der ONVIF/RTSP Kamera |
| `CAMERA_USER` / `CAMERA_PASS` | Kamera Credentials |
| `ELEVENLABS_API_KEY` | Fir d'Audio Ausgab — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` fir ëmmer-op Hände fräi Stëmm Input ze aktivéieren (requiert `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Wou d'Audio spillen: `local` (PC Lautsprecher, standard) \| `remote` (Kamera Lautsprecher) \| `both` |
| `THINKING_MODE` | Antropic nëmmen — `auto` (standard) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptiv Gedankenaufwand: `high` (standard) \| `medium` \| `low` \| `max` (Opus 4.6 nëmmen) |

### 5. Kéiert Är Familiar

```bash
cp persona-template/en.md ME.md
# Edit ME.md — gitt et e Numm an Perséinlechkeet
```

### 6. Lafen

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textual TUI (recommandéiert)
./run.sh --no-tui    # Plain REPL
```

**Windows:**
```bat
run.bat              # Textual TUI (recommandéiert)
run.bat --no-tui     # Plain REPL
```

---

## Wielen eng LLM

> **Recommandéiert: Kimi K2.5** — déi bescht agentesch Leeschtung bis elo getest. Erkannt Kontext, freet no, a handelt autonom op Manéieren déi aner Modeller net maachen. Präis huet e ähnleche Präis wéi Claude Haiku.

| Plattform | `PLATFORM=` | Standard Modell | Wou den Key kréien |
|----------|------------|----------------|-------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibel (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI Tool** (claude -p, ollama…) | `cli` | (de Befehl) | — |

**Kimi K2.5 `.env` Beispiel:**
```env
PLATFORM=kimi
API_KEY=sk-...   # vun platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` Beispiel:**
```env
PLATFORM=glm
API_KEY=...   # vun api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` Beispiel:**
```env
PLATFORM=gemini
API_KEY=AIza...   # vun aistudio.google.com
MODEL=gemini-2.5-flash  # oder gemini-2.5-pro fir méi Fäegkeet
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` Beispiel:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # vun openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # optional: spezifizéieren Modell
AGENT_NAME=Yukine
```

> **Bemierkung:** Fir lokal/NVIDIA Modeller ze deaktivéieren, setzt einfach net `BASE_URL` op eng lokal Adress wéi `http://localhost:11434/v1`. Benotz léiwer Cloud-Provider.

**CLI Tool `.env` Beispiel:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — keen {}, prompt geet iwwer stdin
```

---

## MCP Server

familiar-ai kann sich mat all [MCP (Model Context Protocol)](https://modelcontextprotocol.io) Server verbannen. Dëst erlaabt dir extern Gedächtnis, Dateisystem Accès, Web Sich, oder all aner Tools anzestellen.

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

Zwee Transporttypen sinn ënnerstëtzt:
- **`stdio`**: Start eng lokal Subprozess (`command` + `args`)
- **`sse`**: Verbënnt mat engem HTTP+SSE Server (`url`)

D'Config Datei Plaz mat `MCP_CONFIG=/path/to/config.json` änneren.

---

## Hardware

familiar-ai funktionnéiert mat all Hardware déi Dir hutt — oder och keng.

| Deel | Wat et mécht | Beispill | Néideg? |
|------|--------------|----------|---------|
| Wi-Fi PTZ Kamera | Aen + Hals | Tapo C220 (~$30, Eufy C220) | **Recommandéiert** |
| USB Webcam | Aen (fest) | All UVC Kamera | **Recommandéiert** |
| Roboter-Stëbsauger | Been | All Tuya-kompatibel Modell | Nee |
| PC / Raspberry Pi | Gehier | Alles wat Python ënnerstëtzt | **Jo** |

> **Eng Kamera ass staark recommandéiert.** Ouni eng, kann familiar-ai nach ëmmer schwätzen — mä et kann d'Welt net gesin, firwat et tatsächlech enges do ass.

### Minimal Setup (keine Hardware)

Wëlls de just probéieren? Du braucht nëmmen eng API Schlüssel:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Fänken `./run.sh` (macOS/Linux/WSL2) oder `run.bat` (Windows) un an ufänken ze schwätzen. Add Hardware wa's de gees.

### Wi-Fi PTZ Kamera (Tapo C220)

1. An der Tapo App: **Settings → Advanced → Camera Account** — eng lokal Kont erstell (net TP-Link Kont)
2. Fann d'IP vun der Kamera an der Gerätelëscht vu sengem Router
3. Setz an `.env`:
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


### Stëmm (ElevenLabs)

1. Kréie eng API Schlüssel op [elevenlabs.io](https://elevenlabs.io/)
2. Setz an `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # optional, benotzt Standardstëmm wann et ausgelass ass
   ```

Et ginn zwou Playback Destinatiounen, kontrolléiert duerch `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC Lautsprecher (standard)
TTS_OUTPUT=remote   # Kamera Lautsprecher vun der Läsch
TTS_OUTPUT=both     # Kamera Lautsprecher + PC Lautsprecher gläichzäiteg
```

#### A) Kamera-Lautsprecher (via go2rtc)

Setz `TTS_OUTPUT=remote` (oder `both`). Requiert [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Lued d'binary vun der [Releases Seite](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Plazéieren a umbenannt:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x néideg

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Kreéiert `go2rtc.yaml` an der selwechter Dosséier:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Benotzt d'lokale Kamera Kont Credentials (net är TP-Link Cloud Kont).

4. familiar-ai startet go2rtc automatesch beim Start. Wann d'Kamera zwee-Wee Audio (Backchannel) ënnerstëtzt, spillt d'Audio vum Kamera Lautsprecher.

#### B) Lokalen PC Lautsprecher

Den Standard (`TTS_OUTPUT=local`). Probéiert Spiller an der Rei no: **paplay** → **mpv** → **ffplay**. Och als Fallback wann `TTS_OUTPUT=remote` an go2rtc net verfügbar ass.

| OS | Installéieren |
|----|---------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (oder `paplay` iwwer `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — setzt `PULSE_SERVER=unix:/mnt/wslg/PulseServer` an `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — eroflueden an zur PATH derbäi setzen, **oder** `winget install ffmpeg` |

> Wann keen Audio Spiller verfügbar ass, gëtt d'Sprooch nach ëmmer generéiert — et spilliicht se just net.

### Stëmm Input (Realtime STT)

Setz `REALTIME_STT=true` an `.env` fir ëmmer-op, Hände fräi Stëmm Input:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # déiselwecht Key wéi TTS
```

familiar-ai streamt Mikrofon Audio zu ElevenLabs Scribe v2 an auto-committed Transkriptiounen wanns de stopt ze schwätzen. Keen Knäppchen drécke gebraucht. Koexistéiert mat der Push-to-Talk Modus (Ctrl+T).

---

## TUI

familiar-ai enthält eng Terminal UI gebaut mat [Textual](https://textual.textualize.io/):

- Scrollable Gespréchsverlauf mat live Streaming Text
- Tab-Completing fir `/quit`, `/clear`
- Unterbriech den Agent Mëd-Turn andeems de schreift wann et denkt
- **Gesprächslog** automatesch gespäichert an `~/.cache/familiar-ai/chat.log`

Fir de Log an engem anere Terminal ze verfollegen (nëtzlech fir Kopiéiere-Paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

D'Perséinlechkeet vun dengem Familiar lieft an `ME.md`. Dëse File ass gitignored — et ass nëmme fir dech.

Kuck [`persona-template/en.md`](./persona-template/en.md) fir e Beispill, oder [`persona-template/ja.md`](./persona-template/ja.md) fir eng japanesch Versioun.

---

## FAQ

**Q: Funktionéiert et ouni GPU?**
Jo. D'Embedding Modell (multilingual-e5-small) fonctionnéiert gutt um CPU. E GPU mécht et méi séier, ass awer net néideg.

**Q: Kann ech eng Kamera benotzen déi net Tapo ass?**
Jede Kamera déi Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: Gëtt meng Daten irgendsou geschéckt?**
Biller an Text ginn un deng gewielt LLM API fir Verarbetung geschéckt. Gedächtnisser ginn lokal an `~/.familiar_ai/` armazenéiert.

**Q: Firwat schreift den Agent `（...）` amplaz ze schwätzen?**
Anerstécht sécher datt `ELEVENLABS_API_KEY` gesetzt ass. Ouni dat ass d'Audio deaktivéiert a den Agent geet zréck op Text.

## Technesch Hannergrond

Interesséiert fir wéi et funktionnéiert? Kuck [docs/technical.md](./docs/technical.md) fir d'Recherche a Design-Entscheedungen déi hannert familiar-ai steet — ReAct, SayCan, Reflexion, Voyager, d'Wënschsystem, an méi.

---

## Contributing

familiar-ai ass e offenen Experiment. Wann eppes dovun mat dir ressonéiert — technesch oder philosophesch — sinn d'Contributiounen ganz wëllkomm.

**Gudde Plazen fir unzefänken:**

| Beräich | Wat néideg ass |
|------|----------------|
| New Hardware | Ënnerstëtzung fir méi Kameraen (RTSP, IP Webcam), Mikrofone, Aktuatoren |
| New Tools | Web Sich, Heem Automatioun, Kalenner, alles iwwer MCP |
| New Backends | All LLM oder lokal Modell dat der `stream_turn` Interface passt |
| Persona Templates | ME.md Templates fir verschidde Sproochen a Perséinlechkeeten |
| Recherche | Besser Wënsch Modeller, Gedächtnisretrieval, Theory-of-Mind Prompting |
| Dokumentatioun | Tutorials, Walkthroughs, Iwwersetzungen |

Kuck [CONTRIBUTING.md](./CONTRIBUTING.md) fir Dev Setup, Code Style, a PR Richtlinnen.

Wanns de net sécher bis, wou unzefänken, [maach eng Problematik op](https://github.com/lifemate-ai/familiar-ai/issues) — ech sinn zougestëmmen fir dech an déi richteg Richtung ze weisen.

---

## Lizenz

[MIT](./LICENSE)
