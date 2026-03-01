# familiar-ai 🐾

**Un'IA che vive accanto a te** — con occhi, voce, gambe e memoria.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Disponibile in 74 lingue](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai è un compagno IA che vive a casa tua. Configuralo in pochi minuti. Non è richiesta programmazione.

Percepisce il mondo reale attraverso telecamere, si muove su un corpo robotico, parla ad alta voce e ricorda ciò che vede. Dagli un nome, scrivi la sua personalità e lascialo vivere con te.

## Cosa può fare

- 👁 **Vedere** — cattura immagini da una telecamera PTZ Wi-Fi o da una webcam USB
- 🔄 **Guardarsi intorno** — panoramica e inclinazione della telecamera per esplorare i dintorni
- 🦿 **Muoversi** — guida un aspirapolvere robotico per vagare nella stanza
- 🗣 **Parlare** — parla tramite ElevenLabs TTS
- 🎙 **Ascoltare** — input vocale a mani libere tramite ElevenLabs Realtime STT (opzionale)
- 🧠 **Ricordare** — memorizza e richiama attivamente ricordi con ricerca semantica (SQLite + embedding)
- 🫀 **Teoria della Mente** — prende la prospettiva dell'altra persona prima di rispondere
- 💭 **Desiderio** — ha le proprie spinte interne che innescano comportamenti autonomi

## Come funziona

familiar-ai esegue un loop [ReAct](https://arxiv.org/abs/2210.03629) alimentato dalla tua scelta di LLM. Percepisce il mondo attraverso strumenti, pensa a cosa fare dopo e agisce — proprio come farebbe una persona.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Quando è inattivo, agisce secondo i propri desideri: curiosità, voglia di guardare fuori, mancanza della persona con cui vive.

## Iniziare

### 1. Installa uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Oppure: `winget install astral-sh.uv`

### 2. Installa ffmpeg

ffmpeg è **richiesto** per la cattura di immagini dalla telecamera e la riproduzione audio.

| OS | Comando |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — oppure scarica da [ffmpeg.org](https://ffmpeg.org/download.html) e aggiungi al PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifica: `ffmpeg -version`

### 3. Clona e installa

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configura

```bash
cp .env.example .env
# Modifica .env con le tue impostazioni
```

**Minimo richiesto:**

| Variabile | Descrizione |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | La tua chiave API per la piattaforma scelta |

**Opzionale:**

| Variabile | Descrizione |
|----------|-------------|
| `MODEL` | Nome del modello (valori per impostazione predefinita ragionevoli per piattaforma) |
| `AGENT_NAME` | Nome visualizzato nel TUI (es. `Yukine`) |
| `CAMERA_HOST` | Indirizzo IP della tua telecamera ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Credenziali della telecamera |
| `ELEVENLABS_API_KEY` | Per output vocale — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` per abilitare l'input vocale a mani libere sempre attivo (richiede `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Dove riprodurre l'audio: `local` (altoparlante PC, predefinito) \| `remote` (altoparlante della telecamera) \| `both` |
| `THINKING_MODE` | Solo Anthropic — `auto` (predefinito) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Sforzo di pensiero adattivo: `high` (predefinito) \| `medium` \| `low` \| `max` (solo Opus 4.6) |

### 5. Crea il tuo familiare

```bash
cp persona-template/en.md ME.md
# Modifica ME.md — dagli un nome e una personalità
```

### 6. Esegui

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI testuale (raccomandato)
./run.sh --no-tui    # REPL semplice
```

**Windows:**
```bat
run.bat              # TUI testuale (raccomandato)
run.bat --no-tui     # REPL semplice
```

---

## Scegliere un LLM

> **Raccomandato: Kimi K2.5** — il miglior rendimento agentico testato finora. Nota il contesto, fa domande di follow-up e agisce autonomamente in modi che altri modelli non fanno. Prezzo simile a Claude Haiku.

| Piattaforma | `PLATFORM=` | Modello predefinito | Dove ottenere la chiave |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatibile (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Strumento CLI** (claude -p, ollama…) | `cli` | (il comando) | — |

**Esempio `.env` per Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # da platform.moonshot.ai
AGENT_NAME=Yukine
```

**Esempio `.env` per Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # da api.z.ai
MODEL=glm-4.6v   # abilitato alla visione; glm-4.7 / glm-5 = solo testo
AGENT_NAME=Yukine
```

**Esempio `.env` per Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # da aistudio.google.com
MODEL=gemini-2.5-flash  # o gemini-2.5-pro per maggiori capacità
AGENT_NAME=Yukine
```

**Esempio `.env` per OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # da openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opzionale: specifica il modello
AGENT_NAME=Yukine
```

> **Nota:** Per disabilitare i modelli locali/NVIDIA, non impostare `BASE_URL` su un endpoint locale come `http://localhost:11434/v1`. Usa piuttosto fornitori di cloud.

**Esempio `.env` per strumento CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argomento del prompt
# MODEL=ollama run gemma3:27b  # Ollama — senza {}, il prompt viene passato tramite stdin
```

---

## Server MCP

familiar-ai può connettersi a qualsiasi server [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Questo ti consente di collegare memoria esterna, accesso a filesystem, ricerca web o qualsiasi altro strumento.

Configura i server in `~/.familiar-ai.json` (stesso formato di Claude Code):

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

Due tipi di trasporto sono supportati:
- **`stdio`**: avvia un processo locale (`command` + `args`)
- **`sse`**: connettiti a un server HTTP+SSE (`url`)

Sovrascrivi la posizione del file di configurazione con `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai funziona con qualsiasi hardware tu abbia — o anche senza alcun hardware.

| Parte | Cosa fa | Esempio | Necessario? |
|------|-------------|---------|-----------|
| Telecamera PTZ Wi-Fi | Occhi + collo | Tapo C220 (~$30) | **Raccomandato** |
| Webcam USB | Occhi (fissi) | Qualsiasi telecamera UVC | **Raccomandato** |
| Aspirapolvere robotico | Gambe | Qualsiasi modello compatibile Tuya | No |
| PC / Raspberry Pi | Cervello | Qualsiasi dispositivo che esegue Python | **Sì** |

> **È fortemente raccomandata una telecamera.** Senza di essa, familiar-ai può comunque parlare — ma non può vedere il mondo, che è un po' il senso di tutto.

### Configurazione minima (senza hardware)

Vuoi solo provarlo? Ti serve solo una chiave API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Esegui `./run.sh` (macOS/Linux/WSL2) o `run.bat` (Windows) e inizia a chattare. Aggiungi hardware man mano che procedi.

### Telecamera PTZ Wi-Fi (Tapo C220)

1. Nell'app Tapo: **Impostazioni → Avanzate → Account Telecamera** — crea un account locale (non l'account TP-Link)
2. Trova l'IP della telecamera nella lista dei dispositivi del tuo router
3. Imposta in `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=tuo-utente-locale
   CAMERA_PASS=tuo-password-locale
   ```

### Voce (ElevenLabs)

1. Ottieni una chiave API su [elevenlabs.io](https://elevenlabs.io/)
2. Imposta in `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opzionale, utilizza la voce predefinita se omesso
   ```

Ci sono due destinazioni di riproduzione, controllate da `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Altoparlante PC (predefinito)
TTS_OUTPUT=remote   # Solo altoparlante della telecamera
TTS_OUTPUT=both     # Altoparlante della telecamera + altoparlante PC contemporaneamente
```

#### A) Altoparlante della telecamera (via go2rtc)

Imposta `TTS_OUTPUT=remote` (o `both`). Richiede [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Scarica il binary dalla [pagina delle release](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Posizionalo e rinominalo:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x richiesto

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Crea `go2rtc.yaml` nella stessa directory:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Usa le credenziali dell'account locale della telecamera (non il tuo account cloud TP-Link).

4. familiar-ai avvia automaticamente go2rtc all'avvio. Se la tua telecamera supporta l'audio bidirezionale (canale di ritorno), la voce viene riprodotta dall'altoparlante della telecamera.

#### B) Altoparlante locale del PC

Il predefinito (`TTS_OUTPUT=local`). Prova i lettori in ordine: **paplay** → **mpv** → **ffplay**. Utilizzato anche come fallback quando `TTS_OUTPUT=remote` e go2rtc non è disponibile.

| OS | Installazione |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (o `paplay` tramite `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — imposta `PULSE_SERVER=unix:/mnt/wslg/PulseServer` in `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — scarica e aggiungi al PATH, **oppure** `winget install ffmpeg` |

> Se nessun lettore audio è disponibile, la voce viene comunque generata — ma non verrà riprodotta.

### Input vocale (Realtime STT)

Imposta `REALTIME_STT=true` in `.env` per l'input vocale a mani libere sempre attivo:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # stessa chiave di TTS
```

familiar-ai streaming l'audio del microfono a ElevenLabs Scribe v2 e auto-commit trascrizioni quando smetti di parlare. Non è richiesto alcun tasto da premere. Coesiste con la modalità push-to-talk (Ctrl+T).

---

## TUI

familiar-ai include un'interfaccia terminale costruita con [Textual](https://textual.textualize.io/):

- Cronologia delle conversazioni scrollabile con testo in streaming dal vivo
- Completamento automatico per `/quit`, `/clear`
- Interrompi l'agente a metà turno digitando mentre sta pensando
- **Registro conversazioni** auto-salvato in `~/.cache/familiar-ai/chat.log`

Per seguire il log in un'altra terminale (utile per copia-incolla):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

La personalità del tuo familiare vive in `ME.md`. Questo file è ignorato da git — è solo tuo.

Vedi [`persona-template/en.md`](./persona-template/en.md) per un esempio, o [`persona-template/ja.md`](./persona-template/ja.md) per una versione giapponese.

---

## FAQ

**D: Funziona senza GPU?**
Sì. Il modello di embedding (multilingual-e5-small) funziona bene su CPU. Una GPU lo rende più veloce ma non è necessaria.

**D: Posso usare una telecamera diversa da Tapo?**
Qualsiasi telecamera che supporta ONVIF + RTSP dovrebbe funzionare. La Tapo C220 è quella che abbiamo testato.

**D: I miei dati vengono inviati da qualche parte?**
Le immagini e il testo vengono inviati all'API LLM scelta per l'elaborazione. I ricordi sono memorizzati localmente in `~/.familiar_ai/`.

**D: Perché l'agente scrive `（...）` invece di parlare?**
Assicurati che `ELEVENLABS_API_KEY` sia impostata. Senza, la voce è disabilitata e l'agente torna al testo.

## Background tecnico

Curioso di sapere come funziona? Vedi [docs/technical.md](./docs/technical.md) per la ricerca e le decisioni progettuali dietro familiar-ai — ReAct, SayCan, Reflexion, Voyager, il sistema dei desideri e altro ancora.

---

## Contribuire

familiar-ai è un esperimento aperto. Se qualcosa di tutto ciò risuona con te — tecnicamente o filosoficamente — i contributi sono molto benvenuti.

**Buoni punti di partenza:**

| Area | Cosa serve |
|------|---------------|
| Nuovo hardware | Supporto per più telecamere (RTSP, IP Webcam), microfoni, attuatori |
| Nuovi strumenti | Ricerca web, automazione domestica, calendario, qualsiasi cosa tramite MCP |
| Nuovi backend | Qualsiasi LLM o modello locale che si adatti all'interfaccia `stream_turn` |
| Template persona | Template ME.md per diverse lingue e personalità |
| Ricerca | Modelli di desiderio migliori, recupero di memoria, prompting di teoria della mente |
| Documentazione | Tutorial, walkthrough, traduzioni |

Vedi [CONTRIBUTING.md](./CONTRIBUTING.md) per la configurazione dello sviluppo, lo stile del codice e le linee guida per le PR.

Se non sei sicuro da dove iniziare, [apri un problema](https://github.com/lifemate-ai/familiar-ai/issues) — saremo felici di indicarti la giusta direzione.

---

## Licenza

[MIT](./LICENSE)
