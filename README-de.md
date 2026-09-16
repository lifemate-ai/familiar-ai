# familiar-ai 

<img width="25%" height="25%" alt="familiar-ai-icon" src="https://github.com/user-attachments/assets/944b2023-9ca0-4b30-8240-de766e4439ed" />

**Eine KI, die neben dir lebt** — mit Augen, Stimme, Beinen und Gedächtnis.

[![Lint](https://github.com/lifemate-ai/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/lifemate-ai/familiar-ai/actions/workflows/lint.yml)
[![Test](https://github.com/lifemate-ai/familiar-ai/actions/workflows/test.yml/badge.svg)](https://github.com/lifemate-ai/familiar-ai/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [In 74 Sprachen verfügbar](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ist ein KI-Begleiter, der in deinem Zuhause lebt.
Richte es in Minuten ein. Keine Programmierkenntnisse erforderlich.

Es nimmt die reale Welt durch Kameras wahr, bewegt sich auf einem Roboterkörper, spricht laut und merkt sich, was es sieht. Gib ihm einen Namen, schreib seine Persönlichkeit auf, und lass es mit dir leben.

## Was es kann

- 👁 **Sehen** — erfasst Bilder von einer Wi-Fi-PTZ-Kamera oder USB-Webcam
- 🔄 **Umschauen** — schwenkt und neigt die Kamera, um die Umgebung zu erkunden
- 🦿 **Sich bewegen** — steuert einen Roboterstaubsauger durch den Raum
- 🗣 **Sprechen** — spricht über ElevenLabs TTS
- 🎙 **Zuhören** — freihändige Spracheingabe über ElevenLabs Realtime STT (optional)
- 🧠 **Erinnern** — speichert und ruft aktiv Erinnerungen mit semantischer Suche ab (SQLite + Embeddings)
- 🫀 **Perspektivenwechsel** — nimmt die Perspektive der anderen Person ein, bevor sie antwortet
- 💭 **Wünsche** — hat eigene innere Triebe, die eigenständiges Verhalten auslösen
- 🌐 **Global Workspace** — Wahrnehmung, Gedächtnis, Wünsche und Vorhersagen konkurrieren um Aufmerksamkeit; nur das Salienzeste gewinnt
- 🔮 **Vorhersage** — verfolgt, was es erwartet zu sehen; Überraschung senkt die Aufmerksamkeitsschwelle
- 🔍 **Attention Schema** — führt ein Selbstmodell dessen, worauf es fokussiert, und warum
- 💤 **Default Mode** — der Verstand schweift ab, wenn untätig, und Erinnerungen und Assoziationen tauchen spontan auf
- 🔬 **Metakognition** — beobachtet seine eigenen Denkschritte bei jedem Durchlauf

## Wie es funktioniert

familiar-ai führt eine [ReAct](https://arxiv.org/abs/2210.03629)-Schleife durch, angetrieben von deinem gewählten LLM. Es nimmt die Welt durch Tools wahr, denkt über die nächsten Schritte nach und handelt — genau wie eine Person.

```
Benutzereingabe
  → denken → handeln (Kamera / bewegen / sprechen / erinnern) → beobachten → denken → ...
```

Wenn untätig, handelt es nach seinen eigenen Wünschen: Neugier, hinausschauen wollen, die Person vermissen, mit der es lebt.

### Global Workspace Architecture

Im Innern implementiert familiar-ai eine von [Global Workspace Theory](https://arxiv.org/abs/2410.11407) inspirierte Architektur. Statt alles in den LLM-Prompt zu werfen, konkurrieren spezialisierte Prozessoren bei jedem Durchlauf um einen zentralen Workspace — und nur der Gewinner bekommt volle Repräsentation:

```
Spezialisierte Prozessoren (laufen parallel bei jedem Durchlauf)
  ├─ Wünsche              — was es jetzt möchte
  ├─ Szene               — was es wahrnimmt (Vorhersagefehler: Überraschung → erhöhtes Bewusstsein)
  ├─ Gedächtnis          — was es sich merkt
  ├─ Perspektivenwechsel — was die andere Person vielleicht denkt
  ├─ Selbsterzählung     — Kontinuität der Identität
  ├─ Erkundung           — Neugier auf unbesuchte Richtungen
  ├─ Attention Schema    — Selbstmodell des eigenen Fokus
  ├─ Vorhersage          — erwarteter vs. tatsächlicher Weltzustand
  └─ Default Mode        — Gedankenwandern, wenn nichts anderes zündet
          │
          ▼  konkurrieren (Zündungsschwelle)
   ┌─────────────┐
   │  Workspace  │  Gewinner → LLM-Prompt (Engpass)
   │ Broadcast   │  Andere → periphere Zusammenfassung (je 1 Zeile)
   └─────────────┘
          │
          └──▶ Meta-Monitor zeichnet jeden Schritt auf („worauf habe ich geachtet?")
```

Dies erzeugt **selektive Aufmerksamkeit** — nicht alles erreicht das LLM bei jedem Durchlauf, nur was am wichtigsten ist.

## Erste Schritte

### 1. Installiere uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Oder: `winget install astral-sh.uv`

### 2. Installiere ffmpeg

ffmpeg ist **erforderlich** für die Erfassung von Kamerabildern und die Wiedergabe von Kamera-Lautsprecher über go2rtc.
Die Wiedergabe von lokaler PC-Audio kann auch auf integrierten Betriebssystem-Playern (`afplay` unter macOS) oder dem reinen Python-Fallback basieren.

| OS | Befehl |
|----|--------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — oder von [ffmpeg.org](https://ffmpeg.org/download.html) herunterladen und zu PATH hinzufügen |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifizierung: `ffmpeg -version`

### 3. Klone und installiere

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfiguriere

```bash
cp .env.example .env
# Bearbeite .env mit deinen Einstellungen
```

Wenn du den Desktop-Flow bevorzugst, kann `./run-gui.sh` (oder `run-gui.bat`) beim ersten Start, wenn `API_KEY` noch fehlt, den Setup-Dialog für dich öffnen.

**Minimum erforderlich:**

| Variable | Beschreibung |
|----------|------------|
| `PLATFORM` | `anthropic` (Standard) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Dein API-Schlüssel für die gewählte Plattform |

**Optional:**

| Variable | Beschreibung |
|----------|------------|
| `MODEL` | Modellname (sinnvolle Standardwerte pro Plattform) |
| `AGENT_NAME` | Anzeigename in der TUI (z. B. `Yukine`) |
| `CAMERA_HOST` | IP-Adresse deiner ONVIF/RTSP-Kamera |
| `CAMERA_USERNAME` / `CAMERA_PASSWORD` | Kamera-Anmeldedaten |
| `CAMERA_PTZ_HOST` / `CAMERA_PTZ_USERNAME` / `CAMERA_PTZ_PASSWORD` / `CAMERA_PTZ_PORT` | Optionale PTZ-Overrides, wenn der Steuerendpunkt vom RTSP-Stream-Endpunkt abweicht |
| `ELEVENLABS_API_KEY` | Für Sprachausgabe — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, um immer aktive freihändige Spracheingabe zu aktivieren (erfordert `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Wo Audio wiedergegeben wird: `local` (PC-Lautsprecher, Standard) \| `remote` (Kamera-Lautsprecher) \| `both` |
| `THINKING_MODE` | Nur Anthropic — `auto` (Standard) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptiver Denkaufwand: `high` (Standard) \| `medium` \| `low` \| `max` (nur Opus 4.6) |

### 5. Erstelle dein Familiar

```bash
cp persona-template/en.md ME.md
# Bearbeite ME.md — gib ihm einen Namen und eine Persönlichkeit
```

### 6. Starte

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textual TUI (rückwärts-kompatibel Standard)
./run-gui.sh         # Desktop-GUI-Launcher
./run.sh --gui       # Desktop-GUI (wie run-gui.sh)
./run.sh --no-tui    # Einfache REPL
```

**Windows:**
```bat
run.bat              # Textual TUI (rückwärts-kompatibel Standard)
run-gui.bat          # Desktop-GUI-Launcher
run.bat --gui        # Desktop-GUI (wie run-gui.bat)
run.bat --no-tui     # Einfache REPL
```

---

## LLM wählen

> **Empfohlen: Kimi K2.5** — beste Agentic-Leistung bisher getestet. Bemerkt Kontext, stellt Folgefragen und handelt eigenständig auf Weise, die andere Modelle nicht tun. Ähnlich wie Claude Haiku preislich.

| Plattform | `PLATFORM=` | Standardmodell | API-Schlüssel erhalten |
|-----------|-----------|----------------|----------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| **Ollama (lokal, natives API)** | `ollama` | `gemma4:12b-it-qat` | [ollama.com](https://ollama.com) |
| OpenAI-kompatibel (vllm, LM Studio…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (Multi-Provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI-Tool** (claude -p, ollama…) | `cli` | (der Befehl) | — |

**Kimi K2.5 `.env` Beispiel:**
```env
PLATFORM=kimi
API_KEY=sk-...   # von platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` Beispiel:**
```env
PLATFORM=glm
API_KEY=...   # von api.z.ai
MODEL=glm-4.6v   # visionsfähig; glm-4.7 / glm-5 = nur Text
AGENT_NAME=Yukine
```

**Google Gemini `.env` Beispiel:**
```env
PLATFORM=gemini
API_KEY=AIza...   # von aistudio.google.com
MODEL=gemini-2.5-flash  # oder gemini-2.5-pro für höhere Fähigkeit
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` Beispiel:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # von openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # optional: Modell angeben
AGENT_NAME=Yukine
```

> **Hinweis:** Um lokale/NVIDIA-Modelle zu deaktivieren, setze einfach `BASE_URL` nicht auf einen lokalen Endpunkt wie `http://localhost:11434/v1`. Verwende stattdessen Cloud-Provider.

**Ollama (lokal ~10B) `.env` Beispiel:**
```env
PLATFORM=ollama
MODEL=gemma4:12b-it-qat          # bestes lokal getestetes ~10B; qwen3.5:9b funktioniert auch
BASE_URL=http://localhost:11434  # Standard
UTILITY_PLATFORM=ollama          # Emotion/Summary-Seitenaufrufe bleiben auch lokal
AGENT_NAME=Yukine
# PROMPT_PROFILE=compact  (automatisch für lokale Modelle) — kurzer, beispielgestützter Prompt
# SOCIAL_REFLEX=on        (automatisch für compact)     — keine Kamera bei sozialen Durchläufen, Auto-Sprechen
# THINKING_MODE=disabled  (automatisch = aus für lokal; "extended" aktiviert Ollama think)
# OLLAMA_NUM_CTX=16384
```
Kleine lokale Modelle
