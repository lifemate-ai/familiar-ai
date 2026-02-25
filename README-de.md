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

### 2. Klone und installiere

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 3. Konfiguriere

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

### 4. Erstelle deinen Familiar

```bash
cp persona-template/en.md ME.md
# Bearbeite ME.md — gib ihm einen Namen und eine Persönlichkeit
```

### 5. Starten

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

**Kimi K2.5 `.env` Beispiel:**
```env
PLATFORM=kimi
API_KEY=sk-...   # von platform.moonshot.ai
AGENT_NAME=Yukine
```

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
3. Die Stimme wird über den integrierten Kameralautsprecher via go2rtc abgespielt (beim ersten Start automatisch heruntergeladen)

**Lokale Audiowiedergabe** (Fallback oder ohne Kameralautsprecher) erfordert **mpv** oder **ffplay**. mpv wird empfohlen:

| OS | Installation |
|----|-------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — herunterladen und zu PATH hinzufügen, **oder** ffmpeg installieren: `winget install ffmpeg` |

> Ohne mpv oder ffplay kann familiar-ai Sprache generieren, aber nicht lokal abspielen. Kameralautsprecher (go2rtc) ist davon nicht betroffen.

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
