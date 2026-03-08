# familiar-ai 🐾

**Een AI die naast je leeft** — met ogen, stem, benen en geheugen.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Beschikbaar in 74 talen](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai is een AI-compagnon die in je huis leeft. Zet het in enkele minuten op. Geen codering vereist.

Het percepeert de echte wereld via camera's, beweegt rond op een robotlichaam, spreekt luidop en onthoudt wat het ziet. Geef het een naam, schrijf zijn persoonlijkheid en laat het bij je wonen.

## Wat het kan doen

- 👁 **Zien** — maakt afbeeldingen van een Wi-Fi PTZ-camera of USB-webcam
- 🔄 **Om zich heen kijken** — pan en kantel de camera om zijn omgeving te verkennen
- 🦿 **Bewegen** — laat een robotstofzuiger door de kamer rijden
- 🗣 **Spreken** — praat via ElevenLabs TTS
- 🎙 **Luisteren** — handsfree spraakinput via ElevenLabs Realtime STT (opt-in)
- 🧠 **Onthouden** — slaat actief herinneringen op en haalt ze op met semantische zoekopdrachten (SQLite + embeddings)
- 🫀 **Theory of Mind** — neemt het perspectief van de ander in voordat het reageert
- 💭 **Verlangen** — heeft zijn eigen interne drijfveren die autonoom gedrag activeren

## Hoe het werkt

familiar-ai draait een [ReAct](https://arxiv.org/abs/2210.03629) lus aangedreven door jouw keuze van LLM. Het perceiveert de wereld via tools, denkt na over wat te doen, en handelt — net zoals een persoon zou doen.

```
user input
  → denken → handelen (camera / bewegen / spreken / onthouden) → observeren → denken → ...
```

Wanneer het inactief is, handelt het op zijn eigen verlangens: nieuwsgierigheid, verlangen om naar buiten te kijken, het missen van de persoon met wie het samenwoont.

## Aan de slag

### 1. Installeer uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Of: `winget install astral-sh.uv`

### 2. Installeer ffmpeg

ffmpeg is **vereist** voor het vastleggen van camera-afbeeldingen en audioweergave.

| OS | Opdracht |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — of download van [ffmpeg.org](https://ffmpeg.org/download.html) en voeg toe aan PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifieer: `ffmpeg -version`

### 3. Clone en installeer

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configureer

```bash
cp .env.example .env
# Bewerk .env met jouw instellingen
```

**Minimum vereist:**

| Variabele | Beschrijving |
|----------|-------------|
| `PLATFORM` | `anthropic` (standaard) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Jouw API-sleutel voor het gekozen platform |

**Optioneel:**

| Variabele | Beschrijving |
|----------|-------------|
| `MODEL` | Modelnaam (redelijke standaardwaarden per platform) |
| `AGENT_NAME` | Weergavenaam in de TUI (bijv. `Yukine`) |
| `CAMERA_HOST` | IP-adres van jouw ONVIF/RTSP-camera |
| `CAMERA_USER` / `CAMERA_PASS` | Camera-inloggegevens |
| `ELEVENLABS_API_KEY` | Voor spraakaudio — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` om altijd ingeschakelde handsfree spraakinput te activeren (vereist `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Waar audio afgespeeld moet worden: `local` (PC-luidspreker, standaard) \| `remote` (camera-luidspreker) \| `both` |
| `THINKING_MODE` | Alleen Anthropic — `auto` (standaard) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptieve denk inspanning: `high` (standaard) \| `medium` \| `low` \| `max` (alleen Opus 4.6) |

### 5. Maak je vertrouwde AI

```bash
cp persona-template/en.md ME.md
# Bewerk ME.md — geef het een naam en persoonlijkheid
```

### 6. Voer uit

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textuele TUI (aanbevolen)
./run.sh --no-tui    # Eenvoudige REPL
```

**Windows:**
```bat
run.bat              # Textuele TUI (aanbevolen)
run.bat --no-tui     # Eenvoudige REPL
```

---

## Een LLM kiezen

> **Aanbevolen: Kimi K2.5** — beste agentische prestaties tot nu toe getest. Merkt context op, stelt vervolgvragen en handelt autonoom op manieren die andere modellen niet doen. Prijs vergelijkbaar met Claude Haiku.

| Platform | `PLATFORM=` | Standaardmodel | Waar de sleutel te krijgen |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatibel (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI-tool** (claude -p, ollama…) | `cli` | (de opdracht) | — |

**Kimi K2.5 `.env` voorbeeld:**
```env
PLATFORM=kimi
API_KEY=sk-...   # van platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` voorbeeld:**
```env
PLATFORM=glm
API_KEY=...   # van api.z.ai
MODEL=glm-4.6v   # visie-ingeschakeld; glm-4.7 / glm-5 = alleen tekst
AGENT_NAME=Yukine
```

**Google Gemini `.env` voorbeeld:**
```env
PLATFORM=gemini
API_KEY=AIza...   # van aistudio.google.com
MODEL=gemini-2.5-flash  # of gemini-2.5-pro voor hogere mogelijkheden
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` voorbeeld:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # van openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # optioneel: specificeer model
AGENT_NAME=Yukine
```

> **Opmerking:** Om lokale/NVIDIA-modellen uit te schakelen, stel `BASE_URL` eenvoudig niet in op een lokaal eindpunt zoals `http://localhost:11434/v1`. Gebruik in plaats daarvan cloudproviders.

**CLI-tool `.env` voorbeeld:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — geen {}, prompt gaat via stdin
```

---

## MCP-servers

familiar-ai kan verbinding maken met elke [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Dit stelt je in staat om externe opslag, bestandsysteemtoegang, webzoekopdrachten, of een andere tool aan te sluiten.

Configureer servers in `~/.familiar-ai.json` (zelfde formaat als Claude Code):

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

Twee transporttypes worden ondersteund:
- **`stdio`**: start een lokaal subprocess (`command` + `args`)
- **`sse`**: verbind met een HTTP+SSE-server (`url`)

Overschrijf de configuratie-bestandslocatie met `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai werkt met welke hardware je ook hebt — of zelfs zonder hardware.

| Onderdeel | Wat het doet | Voorbeeld | Vereist? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Ogen + nek | Tapo C220 (~$30, Eufy C220) | **Aanbevolen** |
| USB webcam | Ogen (vast) | Elke UVC-camera | **Aanbevolen** |
| Robotstofzuiger | Benen | Elk Tuya-compatibel model | Nee |
| PC / Raspberry Pi | Brein | Alles wat Python draait | **Ja** |

> **Een camera is sterk aanbevolen.** Zonder een kan familiar-ai nog steeds praten — maar het kan de wereld niet zien, wat toch de hele bedoeling is.

### Minimale setup (geen hardware)

Wil je het gewoon proberen? Je hebt alleen een API-sleutel nodig:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Voer `./run.sh` (macOS/Linux/WSL2) of `run.bat` (Windows) uit en begin met chatten. Voeg hardware toe terwijl je gaat.

### Wi-Fi PTZ camera (Tapo C220)

1. In de Tapo-app: **Instellingen → Geavanceerd → Camera-account** — maak een lokaal account aan (niet een TP-Link-account)
2. Vind het IP-adres van de camera in de apparatenlijst van je router
3. Stel in `.env` in:
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


### Stem (ElevenLabs)

1. Krijg een API-sleutel op [elevenlabs.io](https://elevenlabs.io/)
2. Stel in `.env` in:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # optioneel, gebruikt standaardstem als weggelaten
   ```

Er zijn twee afspeelbestemmingen, te bedienen door `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC-luidspreker (standaard)
TTS_OUTPUT=remote   # alleen camera-luidspreker
TTS_OUTPUT=both     # camera-luidspreker + PC-luidspreker gelijktijdig
```

#### A) Camera-luidspreker (via go2rtc)

Stel `TTS_OUTPUT=remote` (of `both`) in. Vereist [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Download de binaire van de [releases-pagina](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Plaats en hernoem het:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x vereist

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Maak `go2rtc.yaml` in dezelfde map:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gebruik de lokale camera-accountgegevens (niet je TP-Link-cloudaccount).

4. familiar-ai start go2rtc automatisch bij het opstarten. Als je camera tweeweg audio ondersteunt (terugkanaal), speelt de stem af via de camera-luidspreker.

#### B) Lokale PC-luidspreker

De standaard (`TTS_OUTPUT=local`). Probeert spelers in volgorde: **paplay** → **mpv** → **ffplay**. Ook gebruikt als fallback wanneer `TTS_OUTPUT=remote` en go2rtc niet beschikbaar is.

| OS | Installatie |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (of `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — stel `PULSE_SERVER=unix:/mnt/wslg/PulseServer` in `.env` in |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — download en voeg toe aan PATH, **of** `winget install ffmpeg` |

> Als er geen audio speler beschikbaar is, wordt de spraak nog steeds gegenereerd — het speelt alleen niet af.

### Spraakinput (Realtime STT)

Stel `REALTIME_STT=true` in `.env` voor altijd ingeschakelde, handsfree spraakinput:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # dezelfde sleutel als TTS
```

familiar-ai streamt microfoongeluid naar ElevenLabs Scribe v2 en auto-committeert transcripties wanneer je stopt met spreken. Geen knopdruk vereist. Coëxisteert met de druk-om-te-praten modus (Ctrl+T).

---

## TUI

familiar-ai bevat een terminal UI gebouwd met [Textual](https://textual.textualize.io/):

- Scrollbare gespreksgeschiedenis met live streaming tekst
- Tab-completion voor `/quit`, `/clear`
- Onderbreek de agent halverwege door te typen terwijl het aan het denken is
- **Gesprekslog** automatisch opgeslagen in `~/.cache/familiar-ai/chat.log`

Om de log in een andere terminal te volgen (handig voor copy-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persoonlijkheid (ME.md)

De persoonlijkheid van je vertrouwde AI staat in `ME.md`. Dit bestand is gitignored — het is alleen van jou.

Zie [`persona-template/en.md`](./persona-template/en.md) voor een voorbeeld, of [`persona-template/ja.md`](./persona-template/ja.md) voor een Japanse versie.

---

## Veelgestelde vragen

**V: Werkt het zonder GPU?**
Ja. Het embedding-model (multilingual-e5-small) draait prima op CPU. Een GPU maakt het sneller maar is niet required.

**V: Kan ik een andere camera dan Tapo gebruiken?**
Elke camera die Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**V: Worden mijn gegevens ergens naartoe gestuurd?**
Afbeeldingen en tekst worden naar je gekozen LLM API gestuurd voor verwerking. Herinneringen worden lokaal opgeslagen in `~/.familiar_ai/`.

**V: Waarom schrijft de agent `（...）` in plaats van te spreken?**
Zorg ervoor dat `ELEVENLABS_API_KEY` is ingesteld. Zonder dit is de spraak uitgeschakeld en valt de agent terug op tekst.

## Technische achtergrond

Ben je nieuwsgierig naar hoe het werkt? Zie [docs/technical.md](./docs/technical.md) voor het onderzoek en de ontwerpbeslissingen achter familiar-ai — ReAct, SayCan, Reflexion, Voyager, het verlangen-systeem, en meer.

---

## Bijdragen

familiar-ai is een open experiment. Als een van dit resoneert met jou — technisch of filosofisch — zijn bijdragen zeer welkom.

**Goede plekken om te beginnen:**

| Gebied | Wat is nodig |
|------|---------------|
| Nieuwe hardware | Ondersteuning voor meer camera's (RTSP, IP Webcam), microfoons, actuatoren |
| Nieuwe tools | Webzoekopdrachten, huisautomatisering, kalender, alles via MCP |
| Nieuwe backends | Elke LLM of lokaal model dat past bij de `stream_turn` interface |
| Persoonlijkheidtemplates | ME.md-sjablonen voor verschillende talen en persoonlijkheden |
| Onderzoek | Betere verlangen-modellen, geheugentoegang, theory-of-mind prompting |
| Documentatie | Tutorials, walkthroughs, vertalingen |

Zie [CONTRIBUTING.md](./CONTRIBUTING.md) voor ontwikkelopstelling, code-stijl en PR-richtlijnen.

Als je niet zeker weet waar te beginnen, [open een issue](https://github.com/lifemate-ai/familiar-ai/issues) — we helpen je graag op weg.

---

## Licentie

[MIT](./LICENSE)
