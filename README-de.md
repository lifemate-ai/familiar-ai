# familiar-ai 🐾

**Eine KI, die neben dir lebt** — mit Augen, Stimme, Beinen und Gedächtnis.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

[English README](./README.md)

---

[![Demo-Video](https://img.youtube.com/vi/PQvQ6M6-Uys/0.jpg)](https://youtube.com/shorts/PQvQ6M6-Uys)

familiar-ai ist ein KI-Begleiter, der in deinem Zuhause lebt.
Richte es in wenigen Minuten ein. Keine Programmierkenntnisse erforderlich.

Es nimmt die reale Welt durch Kameras wahr, bewegt sich auf einem Roboter, spricht laut und erinnert sich an das, was es sieht. Gib ihm einen Namen, schreibe seine Persönlichkeit auf und lass es bei dir leben.

## Was es kann

- 👁 **Sehen** — erfasst Bilder von einer Wi-Fi-PTZ-Kamera oder USB-Webcam
- 🔄 **Umschauen** — schwenkt und neigt die Kamera, um die Umgebung zu erkunden
- 🦿 **Bewegen** — steuert einen Roboterstaubsauger durchs Zimmer
- 🗣 **Sprechen** — spricht via ElevenLabs TTS
- 🧠 **Erinnern** — speichert und ruft aktiv Erinnerungen mit semantischer Suche ab (SQLite + Embeddings)
- 🫀 **Theory of Mind** — berücksichtigt die Perspektive des anderen, bevor es antwortet
- 💭 **Wünsche** — hat eigene innere Antriebe, die autonomes Verhalten auslösen

## Wie es funktioniert

familiar-ai führt eine [ReAct](https://arxiv.org/abs/2210.03629)-Schleife aus, angetrieben durch dein gewähltes LLM. Es nimmt die Welt durch Tools wahr, überlegt sich, was es tun soll, und handelt — wie ein Mensch.

```
Benutzereingabe
  → überlegen → handeln (Kamera / bewegen / sprechen / erinnern) → beobachten → überlegen → ...
```

Im Leerlauf handelt es nach seinen eigenen Wünschen: Neugier, den Wunsch nach draußen zu schauen, das Vermissen der Person, mit der es lebt.

## Erste Schritte

### 1. Installiere uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Installiere ffmpeg

ffmpeg ist **erforderlich** für die Kamerabilderfassung und Audiowiedergabe.

| OS | Befehl |
|----|--------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — oder von [ffmpeg.org](https://ffmpeg.org/download.html) herunterladen und zu PATH hinzufügen |
| Raspberry Pi | `sudo apt install ffmpeg` |

Überprüfen: `ffmpeg -version`

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

**Erforderlich:**

| Variable | Beschreibung |
|----------|-------------|
| `PLATFORM` | `anthropic` (Standard) \| `gemini` \| `openai` \| `kimi` |
| `API_KEY` | Dein API-Schlüssel für die gewählte Plattform |

**Optional:**

| Variable | Beschreibung |
|----------|-------------|
| `MODEL` | Modellname (sinnvolle Standard pro Plattform) |
| `AGENT_NAME` | Anzeigename in der TUI (z. B. `Yukine`) |
| `CAMERA_HOST` | IP-Adresse deiner ONVIF/RTSP-Kamera |
| `CAMERA_USER` / `CAMERA_PASS` | Anmeldedaten der Kamera |
| `ELEVENLABS_API_KEY` | Für Sprachausgabe — [elevenlabs.io](https://elevenlabs.io/) |
| `TTS_OUTPUT` | Audioziel: `local` (PC-Lautsprecher, Standard) \| `remote` (Kameralautsprecher) \| `both` (beides gleichzeitig) |

### 5. Erstelle deinen Familiar

```bash
cp persona-template/en.md ME.md
# Bearbeite ME.md — gib ihm einen Namen und eine Persönlichkeit
```

### 6. Starten

```bash
./run.sh             # Textuelle TUI (empfohlen)
./run.sh --no-tui    # Einfache REPL
```

---

## Ein LLM wählen

> **Empfohlen: Kimi K2.5** — beste Agent-Performance, die bisher getestet wurde. Bemerkt Kontext, stellt Nachfragen und handelt auf Weise autonom, wie andere Modelle nicht. Preis ähnlich wie Claude Haiku.

| Plattform | `PLATFORM=` | Standardmodell | Wo man den Schlüssel bekommt |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibel (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (Mehrfachanbieter) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI-Tool** (llm, ollama…) | `cli` | (der Befehl) | — |

**Kimi K2.5 `.env` Beispiel:**
```env
PLATFORM=kimi
API_KEY=sk-...   # von platform.moonshot.ai
AGENT_NAME=Yukine
```

**Google Gemini `.env` Beispiel:**
```env
PLATFORM=gemini
API_KEY=AIza...   # von aistudio.google.com
MODEL=gemini-2.5-flash  # oder gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` Beispiel:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # von openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # optional
AGENT_NAME=Yukine
```

> **Hinweis:** Um lokale/NVIDIA-Modelle zu deaktivieren, setzen Sie `BASE_URL` nicht auf einen lokalen Endpunkt wie `http://localhost:11434/v1`. Verwenden Sie stattdessen Cloud-Anbieter.

**CLI-Tool `.env` Beispiel:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = Prompt-Argument
# MODEL=ollama run gemma3:27b  # Ollama — ohne {}, Prompt via stdin
```

---

## MCP-Server

familiar-ai kann sich mit jedem [MCP (Model Context Protocol)](https://modelcontextprotocol.io) Server verbinden und so externe Speicher, Dateizugriff, Websuche und weitere Tools einbinden.

Konfigurieren Sie Server in `~/.familiar-ai.json` (gleiches Format wie Claude Code):

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

Zwei Transporttypen werden unterstützt:
- **`stdio`**: startet einen lokalen Unterprozess (`command` + `args`)
- **`sse`**: verbindet sich mit einem HTTP+SSE-Server (`url`)

Überschreiben Sie den Pfad der Konfigurationsdatei mit `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai funktioniert mit jeder Hardware, die du hast — oder mit gar keiner.

| Teil | Funktion | Beispiel | Erforderlich? |
|------|----------|---------|-----------|
| Wi-Fi-PTZ-Kamera | Augen + Nacken | Tapo C220 (~$30) | **Empfohlen** |
| USB-Webcam | Augen (fest) | Jede UVC-Kamera | **Empfohlen** |
| Roboterstaubsauger | Beine | Jedes Tuya-kompatibles Modell | Nein |
| PC / Raspberry Pi | Gehirn | Alles, das Python ausführt | **Ja** |

> **Eine Kamera wird dringend empfohlen.** Ohne sie kann familiar-ai zwar sprechen — aber es kann die Welt nicht sehen, was ja der ganze Sinn der Sache ist.

### Minimales Setup (keine Hardware)

Du möchtest es nur ausprobieren? Du brauchst nur einen API-Schlüssel:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Starte `./run.sh` und fang an zu chatten. Füge Hardware später hinzu.

### Wi-Fi-PTZ-Kamera (Tapo C220)

1. In der Tapo-App: **Einstellungen → Erweitert → Kamerakonto** — erstelle ein lokales Konto (nicht TP-Link-Konto)
2. Finde die IP-Adresse der Kamera in der Geräteliste deines Routers
3. Stelle in `.env` ein:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=dein-lokaler-benutzer
   CAMERA_PASS=dein-lokales-passwort
   ```

### Stimme (ElevenLabs)

1. Hole dir einen API-Schlüssel auf [elevenlabs.io](https://elevenlabs.io/)
2. Stelle in `.env` ein:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # optional, verwendet Standardstimme wenn weggelassen
   ```
Das Audioziel wird mit `TTS_OUTPUT` gesteuert:

```env
TTS_OUTPUT=local    # PC-Lautsprecher (Standard)
TTS_OUTPUT=remote   # Nur Kameralautsprecher
TTS_OUTPUT=both     # Kameralautsprecher + PC-Lautsprecher gleichzeitig
```

#### A) Kameralautsprecher (via go2rtc)

Setze `TTS_OUTPUT=remote` (oder `both`). [go2rtc](https://github.com/AlexxIT/go2rtc/releases) muss manuell eingerichtet werden:

1. Lade das Binary von der [Releases-Seite](https://github.com/AlexxIT/go2rtc/releases) herunter:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Ablegen und umbenennen:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x erforderlich

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. `go2rtc.yaml` im selben Verzeichnis erstellen:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```

4. familiar-ai startet go2rtc automatisch beim Start. Wenn die Kamera bidirektionales Audio (Backchannel) unterstützt, kommt die Stimme aus dem Kameralautsprecher.

#### B) Lokaler PC-Lautsprecher

Standard (`TTS_OUTPUT=local`). Verwendet **mpv** oder **ffplay**. Wird auch als Fallback genutzt, wenn `TTS_OUTPUT=remote` und go2rtc nicht verfügbar ist.

| OS | Installation |
|----|-------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — herunterladen und zu PATH hinzufügen, **oder** `winget install ffmpeg` |

> Ohne go2rtc und lokalen Player funktioniert die Sprachgenerierung (ElevenLabs API) weiterhin — die Wiedergabe wird lediglich übersprungen.

---

## TUI

familiar-ai enthält eine Terminal-Benutzeroberfläche, gebaut mit [Textual](https://textual.textualize.io/):

- Scrollbarer Gesprächsverlauf mit Live-Streaming-Text
- Tab-Vervollständigung für `/quit`, `/clear`
- Unterbreche den Agent während des Denkens, indem du tippst
- **Gesprächsprotokoll** wird automatisch in `~/.cache/familiar-ai/chat.log` gespeichert

Um das Protokoll in einem anderen Terminal zu verfolgen (nützlich zum Kopieren):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persönlichkeit (ME.md)

Die Persönlichkeit deines Familiars lebt in `ME.md`. Diese Datei ist gitignoriert — sie gehört dir allein.

Siehe [`persona-template/en.md`](./persona-template/en.md) für ein Beispiel oder [`persona-template/ja.md`](./persona-template/ja.md) für eine japanische Version.

---

## Häufig gestellte Fragen

**F: Funktioniert es ohne GPU?**
Ja. Das Embedding-Modell (multilingual-e5-small) läuft problemlos auf der CPU. Eine GPU macht es schneller, ist aber nicht erforderlich.

**F: Kann ich eine andere Kamera als Tapo verwenden?**
Jede Kamera, die ONVIF + RTSP unterstützt, sollte funktionieren. Tapo C220 ist das, womit wir getestet haben.

**F: Werden meine Daten irgendwo hingekannt?**
Bilder und Text werden an deine gewählte LLM-API zum Verarbeiten gesendet. Erinnerungen werden lokal in `~/.familiar_ai/` gespeichert.

**F: Warum schreibt der Agent `（...）` statt zu sprechen?**
Stelle sicher, dass `ELEVENLABS_API_KEY` gesetzt ist. Ohne ihn ist Sprache deaktiviert und der Agent fällt auf Text zurück.

## Lizenz

[MIT](./LICENSE)
