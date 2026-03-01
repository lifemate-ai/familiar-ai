# familiar-ai 🐾

**Una IA que viu al teu costat** — amb ulls, veu, cames i memòria.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai és un company d'IA que viu a casa teva.
Configura-ho en minuts. No es requereix codificació.

Percebs el món real a través de càmeres, es mou en un cos de robot, parla en veu alta i recorda el que veu. Dona-li un nom, escriu la seva personalitat i deixa'l viure amb tu.

## What it can do

- 👁 **Veure** — captura imatges d'una càmera Wi-Fi PTZ o webcam USB
- 🔄 **Mira al voltant** — pan i inclina la càmera per explorar els voltants
- 🦿 **Moure's** — mou un aspirador robot per recórrer l'habitació
- 🗣 **Parlar** — parla a través de ElevenLabs TTS
- 🎙 **Escoltar** — entrada de veu sense mans a través de ElevenLabs Realtime STT (opt-in)
- 🧠 **Recordar** — emmagatzema i recorda activament les memòries amb cerca semàntica (SQLite + embeddings)
- 🫀 **Teoria de la ment** — adopta la perspectiva de l'altra persona abans de respondre
- 💭 **Desig** — té els seus propis impulsos interns que desencadenen un comportament autònom

## How it works

familiar-ai executa un [ReAct](https://arxiv.org/abs/2210.03629) loop alimentat per la teva elecció de LLM. Perceps el món a través d'eines, pensa en què fer a continuació i actua — igual que ho faria una persona.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Quan està inactiu, actua segons els seus propis desitjos: curiositat, ganes de mirar cap a fora, enyorant la persona amb qui viu.

## Getting started

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install ffmpeg

ffmpeg és **requerit** per a la captura d'imatges de càmeres i la reproducció d'àudio.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — o descarrega-ho des de [ffmpeg.org](https://ffmpeg.org/download.html) i afegeix-ho a PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifica: `ffmpeg -version`

### 3. Clone and install

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configure

```bash
cp .env.example .env
# Edit .env with your settings
```

**Minimum required:**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (per defecte) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | La teva clau API per a la plataforma escollida |

**Optional:**

| Variable | Description |
|----------|-------------|
| `MODEL` | Nom del model (predeterminats raonables per plataforma) |
| `AGENT_NAME` | Nom que es mostra a la TUI (per exemple, `Yukine`) |
| `CAMERA_HOST` | Adreça IP de la teva càmera ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Credencials de la càmera |
| `ELEVENLABS_API_KEY` | Per a la sortida de veu — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` per habilitar l'entrada de veu sense mans sempre activa (requereix `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | On reproduir l'àudio: `local` (altaveu del PC, per defecte) \| `remote` (altaveu de la càmera) \| `both` |
| `THINKING_MODE` | Només Anthropic — `auto` (per defecte) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Esforç de pensament adaptatiu: `high` (per defecte) \| `medium` \| `low` \| `max` (només Opus 4.6) |

### 5. Create your familiar

```bash
cp persona-template/en.md ME.md
# Edit ME.md — give it a name and personality
```

### 6. Run

```bash
./run.sh             # Textual TUI (recomanat)
./run.sh --no-tui    # Plain REPL
```

---

## Choosing an LLM

> **Recomanat: Kimi K2.5** — millor rendiment agentic provat fins ara. Nota el context, fa preguntes de seguiment i actua de manera autònoma d'una manera que altres models no ho fan. Preu similar a Claude Haiku.

| Platform | `PLATFORM=` | Default model | Where to get key |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (the command) | — |

**Kimi K2.5 `.env` example:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` example:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` example:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # o gemini-2.5-pro per a major capacitat
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` example:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcional: especificar model
AGENT_NAME=Yukine
```

> **Nota:** Per desactivar models locals/NVIDIA, simplement no estableixis `BASE_URL` a un endpoint local com `http://localhost:11434/v1`. Utilitza proveïdors de núvol en el seu lloc.

**CLI tool `.env` example:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — no {}, prompt va per stdin
```

---

## MCP Servers

familiar-ai pot connectar-se a qualsevol servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Això et permet connectar memòria externa, accés a sistema de fitxers, cerca web, o qualsevol altra eina.

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

Dos tipus de transport són suportats:
- **`stdio`**: llança un subprocess local (`command` + `args`)
- **`sse`**: connecta a un servidor HTTP+SSE (`url`)

Substitueix la ubicació del fitxer de configuració amb `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai funciona amb qualsevol maquinari que tinguis — o sense cap.

| Part | What it does | Example | Required? |
|------|-------------|---------|-----------|
| Càmera Wi-Fi PTZ | Ulls + coll | Tapo C220 (~$30) | **Recomanat** |
| Webcam USB | Ulls (fix) | Qualsevol càmera UVC | **Recomanat** |
| Aspirador robot | Cames | Qualsevol model compatible amb Tuya | No |
| PC / Raspberry Pi | Cervell | Qualsevol cosa que executi Python | **Sí** |

> **Es recomana fortament una càmera.** Sense una, familiar-ai pot seguir parlant — però no pot veure el món, que és una mica el sentit de tot això.

### Minimal setup (no hardware)

Només vols provar-ho? Només necessites una clau API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Executa `./run.sh` i comença a xerrar. Afegeix maquinari a mesura que avançis.

### Càmera Wi-Fi PTZ (Tapo C220)

1. A l'aplicació Tapo: **Configuració → Avançat → Compte de càmera** — crea un compte local (no compte de TP-Link)
2. Troba l'IP de la càmera a la llista de dispositius del teu router
3. Estableix a `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Veu (ElevenLabs)

1. Obteniu una clau API a [elevenlabs.io](https://elevenlabs.io/)
2. Estableix a `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcional, utilitza la veu per defecte si es deixa de costat
   ```

Hi ha dues destinacions de reproducció, controlades per `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Altaveu del PC (per defecte)
TTS_OUTPUT=remote   # Altaveu de la càmera només
TTS_OUTPUT=both     # Altaveu de la càmera + altaveu del PC simultàniament
```

#### A) Altaveu de càmera (via go2rtc)

Estableix `TTS_OUTPUT=remote` (o `both`). Requereix [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Descarrega el binari de la [pàgina de llançaments](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Col·loca'l i canvia-li el nom:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x requerit

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Crea `go2rtc.yaml` al mateix directori:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Utilitza les credencials del compte local de la càmera (no el teu compte del núvol TP-Link).

4. familiar-ai inicia go2rtc automàticament al llançament. Si la teva càmera suporta àudio bidireccional (canal de retorn), el so es reproduirà a l'altaveu de la càmera.

#### B) Altaveu local del PC

El predeterminat (`TTS_OUTPUT=local`). Prova reproductors en ordre: **paplay** → **mpv** → **ffplay**. També s'utilitza com a fallback quan `TTS_OUTPUT=remote` i go2rtc no està disponible.

| OS | Install |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (o `paplay` a través de `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — estableix `PULSE_SERVER=unix:/mnt/wslg/PulseServer` a `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — descarrega i afegeix a PATH, **o** `winget install ffmpeg` |

> Si no hi ha cap reproductor d'àudio disponible, el discurs segueix generant-se — simplement no es reproduirà.

### Entrada de veu (Realtime STT)

Estableix `REALTIME_STT=true` a `.env` per a l'entrada de veu sense mans sempre activa:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # mateixa clau que TTS
```

familiar-ai transmet àudio del micròfon a ElevenLabs Scribe v2 i auto-commita transcripcions quan pauses de parlar. No es requereix cap premuda de botó. Coexisteix amb el mode de pressiona-per-parlar (Ctrl+T).

---

## TUI

familiar-ai inclou una interfície d'usuari de terminal construïda amb [Textual](https://textual.textualize.io/):

- Historial de conversa desplaçable amb text en temps real
- Compleció de fitxers per a `/quit`, `/clear`
- Interromp l'agent a mitjan torn escrivint mentre está pensant
- **Registre de conversa** auto-desat a `~/.cache/familiar-ai/chat.log`

Per seguir el registre en un altre terminal (útil per copiar-enganxar):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

La personalitat del teu familiar viu a `ME.md`. Aquest fitxer és gitignored — és només teu.

Veure [`persona-template/en.md`](./persona-template/en.md) per a un exemple, o [`persona-template/ja.md`](./persona-template/ja.md) per a una versió japonesa.

---

## FAQ

**Q: Funciona sense GPU?**
Sí. El model d'embeddings (multilingual-e5-small) funciona bé al CPU. Una GPU el fa més ràpid però no és necessària.

**Q: Puc utilitzar una càmera diferent de Tapo?**
Qualsevol càmera que suporti ONVIF + RTSP hauria de funcionar. Tapo C220 és amb la qual ho hem provat.

**Q: Es transmeten les meves dades enlloc?**
Les imatges i el text es transmeten a l'API LLM escollida per a processament. Les memòries es desaten localment a `~/.familiar_ai/`.

**Q: Per què l'agent escriu `（...）` en comptes de parlar?**
Assegura't que `ELEVENLABS_API_KEY` està establert. Sense ell, la veu es desactiva i l'agent torna al text.

## Technical background

Curiós sobre com funciona? Veure [docs/technical.md](./docs/technical.md) per a la investigació i les decisions de disseny darrere de familiar-ai — ReAct, SayCan, Reflexion, Voyager, el sistema de desigs, i més.

---

## Contributing

familiar-ai és un experiment obert. Si alguna cosa d'això et ressona — tècnicament o filosòficament — les contribucions són molt benvingudes.

**Bons llocs per començar:**

| Area | What's needed |
|------|---------------|
| Nou maquinari | Suport per a més càmeres (RTSP, IP Webcam), micròfons, actuadors |
| Noves eines | Cerca web, automatització de la llar, calendari, qualsevol cosa a través de MCP |
| Novos backends | Qualsevol LLM o model local que s'adapti a la interfície `stream_turn` |
| Plantilles de persona | Plantilles ME.md per a diferents idiomes i personalitats |
| Investigació | Millors models de desig, recuperació de memòria, suggeriment de teoria de la ment |
| Documentació | Tutorials, guies, traduccions |

Veure [CONTRIBUTING.md](./CONTRIBUTING.md) per a configurar el desenvolupament, estil de codi i directrius de PR.

Si no estàs segur per on començar, [obre un problema](https://github.com/lifemate-ai/familiar-ai/issues) — encantat de guiar-te en la direcció correcta.

---

## License

[MIT](./LICENSE)
