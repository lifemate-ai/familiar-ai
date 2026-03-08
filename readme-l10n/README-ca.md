# familiar-ai 🐾

**Una IA que viu al teu costat** — amb ulls, veu, cames i memòria.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Disponible en 74 idiomes](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai és un company AI que viu a casa teva. Configura-ho en minuts. No es requereix programació.

Perceba el món real a través de càmeres, es mou en un cos de robot, parla en veu alta i recorda el que veu. Dona-li un nom, escriu la seva personalitat i deixa'l viure amb tu.

## Què pot fer

- 👁 **Veure** — captura imatges d'una càmera PTZ Wi-Fi o webcam USB
- 🔄 **Mirar al voltant** — gira i inclina la càmera per explorar els voltants
- 🦿 **Moure's** — condueix un robot aspirador per recórrer l'habitació
- 🗣 **Parlar** — parla a través d'ElevenLabs TTS
- 🎙 **Escoltar** — entrada de veu sense mans a través d'ElevenLabs Realtime STT (opcional)
- 🧠 **Recordar** — emmagatzema i recorda activament records amb cerca semàntica (SQLite + embeddings)
- 🫀 **Teoria de la ment** — pren la perspectiva de l'altra persona abans de respondre
- 💭 **Desig** — té els seus propis impulsos interns que desencadenen un comportament autònom

## Com funciona

familiar-ai executa un bucle [ReAct](https://arxiv.org/abs/2210.03629) alimentat per la teva elecció de LLM. Perceba el món a través d'eines, pensa en què fer a continuació i actua — exactament com ho faria una persona.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Quan està inactiva, actua segons els seus propis desitjos: curiositat, voler mirar a fora, trobat la persona amb qui viu.

## Començament

### 1. Instal·la uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
O: `winget install astral-sh.uv`

### 2. Instal·la ffmpeg

ffmpeg és **requerit** per a la captura d'imatges de càmera i la reproducció d'àudio.

| OS | Comandament |
|----|-------------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — o descarrega des de [ffmpeg.org](https://ffmpeg.org/download.html) i afegeix-ho al PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifica: `ffmpeg -version`

### 3. Clona i instal·la

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configura

```bash
cp .env.example .env
# Edita .env amb la teva configuració
```

**Mínim requerit:**

| Variable | Descripció |
|----------|-------------|
| `PLATFORM` | `anthropic` (per defecte) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | La teva clau API per a la plataforma escollida |

**Opcional:**

| Variable | Descripció |
|----------|-------------|
| `MODEL` | Nom del model (valors per defecte raonables per plataforma) |
| `AGENT_NAME` | Nom de visualització que apareix a la TUI (per exemple, `Yukine`) |
| `CAMERA_HOST` | Adreça IP de la teva càmera ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Credencials de la càmera |
| `ELEVENLABS_API_KEY` | Per a la sortida de veu — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` per habilitar l'entrada de veu sense mans permanent (requereix `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | On reproduir àudio: `local` (altaveu de PC, per defecte) \| `remote` (altaveu de càmera) \| `both` |
| `THINKING_MODE` | Només Anthropic — `auto` (per defecte) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Esforç de pensament adaptatiu: `high` (per defecte) \| `medium` \| `low` \| `max` (només Opus 4.6) |

### 5. Crea el teu familiar

```bash
cp persona-template/en.md ME.md
# Edita ME.md — dóna-li un nom i personalitat
```

### 6. Executa

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI textual (recomanat)
./run.sh --no-tui    # REPL simple
```

**Windows:**
```bat
run.bat              # TUI textual (recomanat)
run.bat --no-tui     # REPL simple
```

---

## Escollint un LLM

> **Recomanat: Kimi K2.5** — millor rendiment agentic provat fins ara. Nota el context, fa preguntes de seguiment i actua autònomament de maneres que altres models no fan. Preu similar a Claude Haiku.

| Plataforma | `PLATFORM=` | Model per defecte | On obtenir la clau |
|------------|-------------|-------------------|--------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatibles (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-proveïdor) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Eina CLI** (claude -p, ollama…) | `cli` | (el comandament) | — |

**Exemple de `.env` de Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # de platform.moonshot.ai
AGENT_NAME=Yukine
```

**Exemple de `.env` de Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # de api.z.ai
MODEL=glm-4.6v   # habilitat per visió; glm-4.7 / glm-5 = només text
AGENT_NAME=Yukine
```

**Exemple de `.env` de Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # de aistudio.google.com
MODEL=gemini-2.5-flash  # o gemini-2.5-pro per a major capacitat
AGENT_NAME=Yukine
```

**Exemple de `.env` de OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # de openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcional: especifica model
AGENT_NAME=Yukine
```

> **Nota:** Per deshabilitar models locals/NVIDIA, simplement no establisqueu `BASE_URL` a un punt final local com `http://localhost:11434/v1`. Utilitzeu en canvi proveïdors al núvol.

**Exemple de `.env` d'eina CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argument del prompt
# MODEL=ollama run gemma3:27b  # Ollama — sense {}, el prompt passa via stdin
```

---

## Servidors MCP

familiar-ai pot connectar-se a qualsevol servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Això et permet connectar memòria externa, accés al sistema de fitxers, cerca per web, o qualsevol altra eina.

Configura els servidors a `~/.familiar-ai.json` (mateix format que Claude Code):

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

Dos tipus de transport són compatibles:
- **`stdio`**: llança un subprocess local (`command` + `args`)
- **`sse`**: connecta a un servidor HTTP+SSE (`url`)

Substitueix la ubicació del fitxer de configuració amb `MCP_CONFIG=/path/to/config.json`.

---

## Maquinari

familiar-ai funciona amb qualsevol maquinari que tinguis — o cap en absolut.

| Parts | Què fa | Exemple | Requerit? |
|-------|--------|---------|-----------|
| Càmera PTZ Wi-Fi | Ulls + coll | Tapo C220 (~$30, Eufy C220) | **Recomanat** |
| Webcam USB | Ulls (fixa) | Qualsevol càmera UVC | **Recomanat** |
| Robot aspirador | Cames | Qualsevol model compatible amb Tuya | No |
| PC / Raspberry Pi | Cervell | Qualsevol cosa que executi Python | **Sí** |

> **Es recomana fortament una càmera.** Sense ella, familiar-ai pot parlar — però no pot veure el món, que és una mica el tema.

### Configuració mínima (sense maquinari)

Només vols provar-ho? Només necessites una clau API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Executa `./run.sh` (macOS/Linux/WSL2) o `run.bat` (Windows) i comença a xerrar. Afegeix maquinari a mesura que avancis.

### Càmera PTZ Wi-Fi (Tapo C220)

1. A l'app Tapo: **Configuració → Avançat → Compte de càmera** — crea un compte local (no el compte de TP-Link)
2. Troba la IP de la càmera a la llista de dispositius del teu router
3. Estableix a `.env`:
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


### Veu (ElevenLabs)

1. Obteniu una clau API a [elevenlabs.io](https://elevenlabs.io/)
2. Estableix a `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcional, utilitza la veu per defecte si es omet
   ```

Hi ha dues destinacions de reproducció, controlades per `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Altaveu de PC (per defecte)
TTS_OUTPUT=remote   # només altaveu de càmera
TTS_OUTPUT=both     # altaveu de càmera + altaveu de PC simultàniament
```

#### A) Altaveu de càmera (via go2rtc)

Estableix `TTS_OUTPUT=remote` (o `both`). Requereix [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Descarrega el binari de la [pàgina de versions](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Col·loca i canvia el nom:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x requereix

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Crea `go2rtc.yaml` a la mateixa carpeta:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Utilitza les credencials del compte de càmera local (no el teu compte al núvol de TP-Link).

4. familiar-ai inicia go2rtc automàticament en llançar-se. Si la teva càmera suporta àudio bidireccional (canal de tornada), la veu es reproduirà des de l'altaveu de la càmera.

#### B) Altaveu local del PC

El valor per defecte (`TTS_OUTPUT=local`). Prova reproductors en ordre: **paplay** → **mpv** → **ffplay**. També s'utilitza com a fallback quan `TTS_OUTPUT=remote` i go2rtc no està disponible.

| OS | Instal·la |
|----|-----------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (o `paplay` a través de `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — estableix `PULSE_SERVER=unix:/mnt/wslg/PulseServer` a `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — descarrega i afegeix al PATH, **o** `winget install ffmpeg` |

> Si no hi ha cap reproductor d'àudio disponible, el discurs encara es genera — simplement no es reproduirà.

### Entrada de veu (Realtime STT)

Estableix `REALTIME_STT=true` a `.env` per a entrada de veu permanent, sense mans:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # la mateixa clau que TTS
```

familiar-ai transmet àudio del micròfon a ElevenLabs Scribe v2 i auto-compromet transcripcions quan pauses de parlar. No es requereix prémer cap botó. Coexisteix amb el mode de parla a demanda (Ctrl+T).

---

## TUI

familiar-ai inclou una interfície d'usuari de terminal construïda amb [Textual](https://textual.textualize.io/):

- Historial de conversa desplaçable amb text d'streaming en viu
- Compleció de pestanyes per a `/quit`, `/clear`
- Interromp l'agent a mitja ronda escrivint mentre pensa
- **Registre de conversa** auto-desat a `~/.cache/familiar-ai/chat.log`

Per seguir el registre en un altre terminal (útil per copiar i enganxar):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

La personalitat del teu familiar viu a `ME.md`. Aquest fitxer és gitignored — és només teu.

Veure [`persona-template/en.md`](./persona-template/en.md) per a un exemple, o [`persona-template/ja.md`](./persona-template/ja.md) per a una versió en japonès.

---

## FAQ

**Q: Funciona sense una GPU?**
Sí. El model d'embeddings (multilingual-e5-small) funciona bé en CPU. Una GPU el fa més ràpid però no és requerit.

**Q: Puc utilitzar una càmera diferent de Tapo?**
Qualsevol càmera que suporti Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: S'enviament les meves dades enlloc?**
Imatges i text s'envien a la teva API LLM escollida per processar. Els records s'emmagatzemen localment a `~/.familiar_ai/`.

**Q: Per què l'agent escriu `（...）` en lloc de parlar?**
Assegura't que `ELEVENLABS_API_KEY` està establert. Sense ella, la veu està deshabilitada i l'agent torna al text.

## Antecedents tècnics

Curiós sobre com funciona? Veure [docs/technical.md](./docs/technical.md) per a la investigació i les decisions de disseny darrere familiar-ai — ReAct, SayCan, Reflexion, Voyager, el sistema de desig, i més.

---

## Contribuint

familiar-ai és un experiment obert. Si alguna d'aquestes coses ressona amb tu — tècnicament o filosòficament — les contribucions són molt benvingudes.

**Bons llocs per començar:**

| Àrea | Què és necessari |
|------|------------------|
| Nou maquinari | Suport per a més càmeres (RTSP, IP Webcam), micròfons, actuadors |
| Noves eines | Cerca web, automatització de la llar, calendari, qualsevol cosa a través de MCP |
| Nous backends | Qualsevol LLM o model local que s'ajusti a la interfície `stream_turn` |
| Plantilles de persona | Plantilles de ME.md per a diferents idiomes i personalitats |
| Investigació | Millors models de desig, recuperació de memòria, indicis de teoria de la ment |
| Documentació | Tutorials, guies, traduccions |

Veure [CONTRIBUTING.md](./CONTRIBUTING.md) per a la configuració de desenvolupament, estil de codi, i directrius de PR.

Si no estàs segur per on començar, [obre un problema](https://github.com/lifemate-ai/familiar-ai/issues) — encantat de dirigir-te en la direcció correcta.

---

## Llicència

[MIT](./LICENSE)

[→ English README](../README.md)
