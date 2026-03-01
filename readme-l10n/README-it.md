```markdown
# familiar-ai 🐾

**Un'IA che vive accanto a te** — con occhi, voce, gambe e memoria.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai è un compagno IA che vive a casa tua.
Configuralo in pochi minuti. Non è richiesta programmazione.

Percepisce il mondo reale attraverso telecamere, si muove su un corpo robotico, parla ad alta voce e ricorda ciò che vede. Dagli un nome, scrivi la sua personalità e lascialo vivere con te.

## Cosa può fare

- 👁 **Vedere** — cattura immagini da una telecamera PTZ Wi-Fi o da una webcam USB
- 🔄 **Guardarsi intorno** — ruota e inclina la telecamera per esplorare l'ambiente
- 🦿 **Muoversi** — aziona un robot aspirapolvere per girare nella stanza
- 🗣 **Parlare** — comunica tramite ElevenLabs TTS
- 🎙 **Ascoltare** — input vocale senza mani tramite ElevenLabs Realtime STT (su richiesta)
- 🧠 **Ricordare** — memorizza e richiama attivamente ricordi con ricerca semantica (SQLite + embeddings)
- 🫀 **Teoria della mente** — considera la prospettiva dell'altra persona prima di rispondere
- 💭 **Desiderio** — ha i propri impulsi interni che innescano comportamenti autonomi

## Come funziona

familiar-ai esegue un ciclo [ReAct](https://arxiv.org/abs/2210.03629) alimentato dalla tua scelta di LLM. Percepisce il mondo attraverso strumenti, pensa a cosa fare dopo e agisce — proprio come farebbe una persona.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Quando è inattivo, agisce secondo i propri desideri: curiosità, voglia di guardare fuori, nostalgia della persona con cui vive.

## Iniziare

### 1. Installa uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Installa ffmpeg

ffmpeg è **richiesto** per la cattura delle immagini della telecamera e la riproduzione audio.

| OS | Comando |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — o scarica da [ffmpeg.org](https://ffmpeg.org/download.html) e aggiungi a PATH |
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
| `PLATFORM` | `anthropic` (predefinito) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | La tua chiave API per la piattaforma scelta |

**Opzionale:**

| Variabile | Descrizione |
|----------|-------------|
| `MODEL` | Nome del modello (predefiniti sensati per piattaforma) |
| `AGENT_NAME` | Nome visualizzato nell'interfaccia TUI (es. `Yukine`) |
| `CAMERA_HOST` | Indirizzo IP della tua telecamera ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Credenziali della telecamera |
| `ELEVENLABS_API_KEY` | Per l'output vocale — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` per abilitare l'input vocale sempre attivo senza mani (richiede `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Dove riprodurre l'audio: `local` (cassa PC, predefinito) \| `remote` (cassa telecamera) \| `both` |
| `THINKING_MODE` | Solo per Anthropic — `auto` (predefinito) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Sforzo di pensiero adattivo: `high` (predefinito) \| `medium` \| `low` \| `max` (solo Opus 4.6) |

### 5. Crea il tuo familiare

```bash
cp persona-template/en.md ME.md
# Modifica ME.md — dagli un nome e una personalità
```

### 6. Esegui

```bash
./run.sh             # TUI testuale (consigliato)
./run.sh --no-tui    # REPL semplice
```

---

## Scelta di un LLM

> **Consigliato: Kimi K2.5** — migliore prestazione agentica testata finora. Nota il contesto, pone domande di follow-up e agisce autonomamente in modi che altri modelli non fanno. Prezzo simile a Claude Haiku.

| Piattaforma | `PLATFORM=` | Modello predefinito | Dove ottenere la chiave |
|-------------|------------|---------------------|------------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatibile (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Strumento CLI** (claude -p, ollama…) | `cli` | (il comando) | — |

**Esempio `.env` di Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # da platform.moonshot.ai
AGENT_NAME=Yukine
```

**Esempio `.env` di Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # da api.z.ai
MODEL=glm-4.6v   # con visione abilitata; glm-4.7 / glm-5 = solo testo
AGENT_NAME=Yukine
```

**Esempio `.env` di Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # da aistudio.google.com
MODEL=gemini-2.5-flash  # o gemini-2.5-pro per maggiore capacità
AGENT_NAME=Yukine
```

**Esempio `.env` di OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # da openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opzionale: specifica il modello
AGENT_NAME=Yukine
```

> **Nota:** Per disabilitare modelli locali/NVIDIA, basta non impostare `BASE_URL` su un endpoint locale come `http://localhost:11434/v1`. Utilizza invece i provider cloud.

**Esempio `.env` di strumento CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argomento prompt
# MODEL=ollama run gemma3:27b  # Ollama — no {}, il prompt passa tramite stdin
```

---

## Server MCP

familiar-ai può collegarsi a qualsiasi server [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Questo ti consente di collegare memoria esterna, accesso al filesystem, ricerca sul web o qualsiasi altro strumento.

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
- **`stdio`**: avvia un sotto-processo locale (`command` + `args`)
- **`sse`**: collegati a un server HTTP+SSE (`url`)

Sovrascrivi la posizione del file di configurazione con `MCP_CONFIG=/percorso/del/config.json`.

---

## Hardware

familiar-ai funziona con qualunque hardware tu abbia — o anche senza.

| Parte | Cosa fa | Esempio | Necessario? |
|-------|---------|---------|-------------|
| Telecamera PTZ Wi-Fi | Occhi + collo | Tapo C220 (~$30) | **Consigliato** |
| Webcam USB | Occhi (fissi) | Qualsiasi camera UVC | **Consigliato** |
| Robot aspirapolvere | Gambe | Qualsiasi modello compatibile con Tuya | No |
| PC / Raspberry Pi | Cervello | Qualsiasi cosa che esegue Python | **Sì** |

> **È fortemente consigliata una telecamera.** Senza di essa, familiar-ai può comunque parlare — ma non può vedere il mondo, che è un po' il punto principale.

### Configurazione minima (senza hardware)

Vuoi solo provarlo? Hai bisogno solo di una chiave API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Esegui `./run.sh` e inizia a chattare. Aggiungi hardware man mano che procedi.

### Telecamera PTZ Wi-Fi (Tapo C220)

1. Nell'app Tapo: **Impostazioni → Avanzate → Account Telecamera** — crea un account locale (non un account TP-Link)
2. Trova l'IP della telecamera nell'elenco dei dispositivi del tuo router
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
TTS_OUTPUT=local    # Cassa PC (predefinita)
TTS_OUTPUT=remote   # solo cassa telecamera
TTS_OUTPUT=both     # cassa telecamera + cassa PC contemporaneamente
```

#### A) Cassa della telecamera (via go2rtc)

Imposta `TTS_OUTPUT=remote` (o `both`). Richiede [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Scarica il binario dalla [pagina delle versioni](https://github.com/AlexxIT/go2rtc/releases):
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

4. familiar-ai avvia automaticamente go2rtc all'avvio. Se la tua telecamera supporta l'audio bidirezionale (backchannel), la voce verrà riprodotta dalla cassa della telecamera.

#### B) Cassa locale del PC

Il predefinito (`TTS_OUTPUT=local`). Prova i lettori in ordine: **paplay** → **mpv** → **ffplay**. Utilizzato anche come fallback quando `TTS_OUTPUT=remote` e go2rtc non è disponibile.

| OS | Installazione |
|----|---------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (o `paplay` tramite `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — imposta `PULSE_SERVER=unix:/mnt/wslg/PulseServer` in `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — scarica e aggiungi a PATH, **oppure** `winget install ffmpeg` |

> Se non è disponibile alcun lettore audio, il discorso viene comunque generato — ma non verrà riprodotto.

### Input vocale (Realtime STT)

Imposta `REALTIME_STT=true` in `.env` per l'input vocale sempre attivo e senza mani:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # stessa chiave di TTS
```

familiar-ai invia in streaming l'audio del microfono a ElevenLabs Scribe v2 e registra automaticamente i trascritti quando smetti di parlare. Non è necessaria alcuna pressione di pulsante. Coesiste con la modalità push-to-talk (Ctrl+T).

---

## TUI

familiar-ai include una UI da terminale costruita con [Textual](https://textual.textualize.io/):

- Cronologia delle conversazioni scrollabile con testo in streaming live
- Completamento della scheda per `/quit`, `/clear`
- Interrompi l'agente a metà turno digitando mentre sta pensando
- **Registro delle conversazioni** auto-salvato in `~/.cache/familiar-ai/chat.log`

Per seguire il log in un altro terminale (utile per copiare e incollare):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

La personalità del tuo familiare vive in `ME.md`. Questo file è gitignored — è solo tuo.

Guarda [`persona-template/en.md`](./persona-template/en.md) per un esempio, o [`persona-template/ja.md`](./persona-template/ja.md) per una versione giapponese.

---

## FAQ

**D: Funziona senza una GPU?**
Sì. Il modello di embedding (multilingual-e5-small) funziona bene su CPU. Una GPU lo rende più veloce ma non è necessaria.

**D: Posso usare una telecamera diversa da Tapo?**
Qualsiasi telecamera che supporta ONVIF + RTSP dovrebbe funzionare. Tapo C220 è quella che abbiamo testato.

**D: I miei dati vengono inviati da qualche parte?**
Le immagini e i testi vengono inviati all'API LLM scelta per l'elaborazione. I ricordi sono memorizzati localmente in `~/.familiar_ai/`.

**D: Perché l'agente scrive `（...）` invece di parlare?**
Assicurati che `ELEVENLABS_API_KEY` sia impostata. Senza di essa, la voce è disabilitata e l'agente ricade sul testo.

## Sfondo tecnico

Curioso su come funziona? Consulta [docs/technical.md](./docs/technical.md) per le ricerche e le decisioni progettuali dietro familiar-ai — ReAct, SayCan, Reflexion, Voyager, il sistema dei desideri e altro.

---

## Contribuire

familiar-ai è un esperimento aperto. Se qualcosa di tutto ciò risuona in te — tecnicamente o filosoficamente — le contribuzioni sono molto benvenute.

**Buoni posti per iniziare:**

| Area | Cosa serve |
|------|------------|
| Nuovo hardware | Supporto per più telecamere (RTSP, Webcam IP), microfoni, attuatori |
| Nuovi strumenti | Ricerca web, automazione domestica, calendario, qualsiasi cosa tramite MCP |
| Nuovi backend | Qualsiasi LLM o modello locale che soddisfi l'interfaccia `stream_turn` |
| Modelli di persona | Modelli ME.md per diverse lingue e personalità |
| Ricerca | Migliori modelli di desiderio, recupero di memoria, prompting teoria-della-mente |
| Documentazione | Tutorial, walkthrough, traduzioni |

Guarda [CONTRIBUTING.md](./CONTRIBUTING.md) per la configurazione dello sviluppo, lo stile del codice e le linee guida per le PR.

Se non sei sicuro da dove iniziare, [apri un problema](https://github.com/lifemate-ai/familiar-ai/issues) — felice di indicarti la giusta direzione.

---

## Licenza

[MIT](./LICENSE)
```
