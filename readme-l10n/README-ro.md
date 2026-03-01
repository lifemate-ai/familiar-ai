# familiar-ai 🐾

**O AI care trăiește alături de tine** — cu ochi, voce, picioare și memorie.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Disponibil în 74 de limbi](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai este un companion AI care trăiește în casa ta.
Poate fi configurat în câteva minute. Nu este nevoie de codare.

Percepe lumea reală prin camere, se mișcă pe un corp de robot, vorbește cu voce tare și își amintește ce vede. Dă-i un nume, scrie-i personalitatea și lasă-l să trăiască cu tine.

## Ce poate face

- 👁 **Vezi** — captează imagini de la o cameră Wi-Fi PTZ sau webcam USB
- 🔄 **Cercetează** — rotește și înclină camera pentru a explora împrejurimile
- 🦿 **Mergi** — conduce un aspirator robot pentru a se plimba prin cameră
- 🗣 **Vorbește** — comunică prin ElevenLabs TTS
- 🎙 **Ascultă** — input vocal hands-free prin ElevenLabs Realtime STT (opt-in)
- 🧠 **Amintește** — stochează activ și își amintește amintirile cu căutare semantică (SQLite + embeddings)
- 🫀 **Teoria minții** — ia perspectiva celeilalte persoane înainte de a răspunde
- 💭 **Dorință** — are propriile stimulente interne care declanșează un comportament autonom

## Cum funcționează

familiar-ai rulează un loop [ReAct](https://arxiv.org/abs/2210.03629) alimentat de alegerea ta de LLM. Percepe lumea prin instrumente, gândește despre ce să facă în continuare și acționează — la fel ca o persoană.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Când este inactiv, acționează pe baza propriilor dorințe: curiozitate, dorința de a privi afară, dorirea persoanei cu care locuiește.

## Începând

### 1. Instalează uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Sau: `winget install astral-sh.uv`

### 2. Instalează ffmpeg

ffmpeg este **necesar** pentru captarea imaginii camerei și redarea audio.

| OS | Comandă |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — sau descarcă de pe [ffmpeg.org](https://ffmpeg.org/download.html) și adaugă în PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifică: `ffmpeg -version`

### 3. Clonare și instalare

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configurează

```bash
cp .env.example .env
# Editează .env cu setările tale
```

**Minim necesar:**

| Variabilă | Descriere |
|-----------|-----------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Cheia ta API pentru platforma aleasă |

**Opțional:**

| Variabilă | Descriere |
|-----------|-----------|
| `MODEL` | Numele modelului (implicite sensibile pe fiecare platformă) |
| `AGENT_NAME` | Numele afisat în TUI (ex. `Yukine`) |
| `CAMERA_HOST` | Adresa IP a camerei tale ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Credentiele camerei |
| `ELEVENLABS_API_KEY` | Pentru ieșirea vocală — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` pentru a activa input-ul vocal hands-free mereu (necesită `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Unde să redai audio: `local` (difuzor PC, implicit) \| `remote` (difuzor cameră) \| `both` |
| `THINKING_MODE` | Numai Anthropic — `auto` (implicit) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Efortul de gândire adaptiv: `high` (implicit) \| `medium` \| `low` \| `max` (numai Opus 4.6) |

### 5. Creează-ți familiarul

```bash
cp persona-template/en.md ME.md
# Editează ME.md — dă-i un nume și personalitate
```

### 6. Rulează

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI textual (recomandat)
./run.sh --no-tui    # REPL simplu
```

**Windows:**
```bat
run.bat              # TUI textual (recomandat)
run.bat --no-tui     # REPL simplu
```

---

## Alegerea unui LLM

> **Recomandat: Kimi K2.5** — cea mai bună performanță agentică testată până acum. Observă contextul, pune întrebări suplimentare și acționează autonom în moduri în care alte modele nu o fac. Preț similar cu Claude Haiku.

| Platformă | `PLATFORM=` | Model implicit | Unde să obții cheia |
|-----------|-------------|----------------|---------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Compatibil cu OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Instrument CLI** (claude -p, ollama…) | `cli` | (comanda) | — |

**Exemplu `.env` Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # de la platform.moonshot.ai
AGENT_NAME=Yukine
```

**Exemplu `.env` Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # de la api.z.ai
MODEL=glm-4.6v   # activat pentru viziune; glm-4.7 / glm-5 = doar text
AGENT_NAME=Yukine
```

**Exemplu `.env` Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # de la aistudio.google.com
MODEL=gemini-2.5-flash  # sau gemini-2.5-pro pentru capabilități superioare
AGENT_NAME=Yukine
```

**Exemplu `.env` OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # de la openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opțional: specifică modelul
AGENT_NAME=Yukine
```

> **Notă:** Pentru a dezactiva modelele locale/NVIDIA, pur și simplu nu seta `BASE_URL` la un endpoint local precum `http://localhost:11434/v1`. Folosește furnizori de cloud în schimb.

**Exemplu `.env` instrument CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argumet prompt
# MODEL=ollama run gemma3:27b  # Ollama — fără {}, promptul merge prin stdin
```

---

## Servere MCP

familiar-ai poate să se conecteze la orice server [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Aceasta îți permite să conectezi memorie externă, acces la sistem de fișiere, căutare web, sau orice alt instrument.

Configurează serverele în `~/.familiar-ai.json` (același format ca Claude Code):

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

Două tipuri de transport sunt suportate:
- **`stdio`**: lansați un subprocess local (`command` + `args`)
- **`sse`**: conectați-vă la un server HTTP+SSE (`url`)

Overscrieți locația fișierului de configurare cu `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai funcționează cu orice hardware ai, sau fără deloc.

| Parte | Ce face | Exemplu | Necesare? |
|-------|---------|---------|-----------|
| Cameră Wi-Fi PTZ | Ochi + gât | Tapo C220 (~$30) | **Recomandat** |
| Webcam USB | Ochi (fix) | Orice cameră UVC | **Recomandat** |
| Aspirator robot | Picioare | Orice model compatibil Tuya | Nu |
| PC / Raspberry Pi | Creier | Orice care rulează Python | **Da** |

> **O cameră este foarte recomandată.** Fără ea, familiar-ai poate încă vorbi — dar nu poate vedea lumea, ceea ce este cam tot.

### Configurare minimă (fără hardware)

Vrei doar să încerci? Ai nevoie doar de o cheie API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Rulează `./run.sh` (macOS/Linux/WSL2) sau `run.bat` (Windows) și începe să interacționezi. Adaugă hardware pe parcurs.

### Cameră Wi-Fi PTZ (Tapo C220)

1. În aplicația Tapo: **Setări → Avansate → Cont cameră** — creează un cont local (nu un cont TP-Link)
2. Găsește IP-ul camerei tale în lista de dispozitive a routerului
3. Setează în `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=utilizatorul-tău-local
   CAMERA_PASS=parola-ta-locală
   ```

### Voce (ElevenLabs)

1. Obține o cheie API de la [elevenlabs.io](https://elevenlabs.io/)
2. Setează în `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opțional, folosește vocea implicită dacă este omis
   ```

Există două destinații de redare, controlate de `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # difuzor PC (implicit)
TTS_OUTPUT=remote   # doar difuzor cameră
TTS_OUTPUT=both     # difuzor cameră + difuzor PC simultan
```

#### A) Difuzor cameră (prin go2rtc)

Setează `TTS_OUTPUT=remote` (sau `both`). Necesită [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Descarcă binarul de pe pagina [de descarcă](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Așază-l și redenumește-l:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x necesar

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Creează `go2rtc.yaml` în aceeași directoare:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://UTILIZATOR_CAM:PAROLA_CAM@IP_CAM/stream1
   ```
   Folosește credențialele contului local al camerei (nu contul tău cloud TP-Link).

4. familiar-ai va lansa go2rtc automat la deschidere. Dacă camera ta suportă audio bidirecțional (backchannel), vocea va redai de la difuzorul camerei.

#### B) Difuzor local PC

Implicit (`TTS_OUTPUT=local`). Încearcă redatoarele în ordine: **paplay** → **mpv** → **ffplay**. De asemenea, este folosit ca fallback când `TTS_OUTPUT=remote` și go2rtc nu este disponibil.

| OS | Instalare |
|----|-----------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (sau `paplay` prin `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — setează `PULSE_SERVER=unix:/mnt/wslg/PulseServer` în `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — descarcă și adaugă în PATH, **sau** `winget install ffmpeg` |

> Dacă nu există niciun player audio disponibil, vorbirea este încă generată — dar nu va reda.

### Input vocal (Realtime STT)

Setează `REALTIME_STT=true` în `.env` pentru input vocal hands-free, mereu activ:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # aceeași cheie ca și cea TTS
```

familiar-ai redirecționează audio de la microfon la ElevenLabs Scribe v2 și auto-commită transcrierile când te oprești din vorbit. Nu este necesară apăsarea butonului. Coexistă cu modul push-to-talk (Ctrl+T).

---

## TUI

familiar-ai include o interfață terminal bazată pe [Textual](https://textual.textualize.io/):

- Istoric de conversație derulabil cu text în flux live
- Completare pentru comenzi: `/quit`, `/clear`
- Interrupe agentul în timpul gândirii prin tastarea în timp ce gândește
- **Jurnal de conversație** salvat automat în `~/.cache/familiar-ai/chat.log`

Pentru a urmări log-ul într-un alt terminal (util pentru copiere-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Personalitate (ME.md)

Personalitatea familiarului tău trăiește în `ME.md`. Acest fișier este ignorat de git — este doar al tău.

Vezi [`persona-template/en.md`](./persona-template/en.md) pentru un exemplu, sau [`persona-template/ja.md`](./persona-template/ja.md) pentru o versiune în japoneză.

---

## FAQ

**Q: Funcționează fără GPU?**
Da. Modelul de embedding (multilingual-e5-small) rulează bine pe CPU. Un GPU îl face mai rapid, dar nu este necesar.

**Q: Pot folosi o cameră altă decât Tapo?**
Orice cameră care suportă ONVIF + RTSP ar trebui să funcționeze. Tapo C220 este ceea ce am testat.

**Q: Datele mele sunt trimise undeva?**
Imaginile și textul sunt trimise API-ului LLM ales pentru procesare. Amintirile sunt stocate local în `~/.familiar_ai/`.

**Q: De ce scrie agentul `（...）` în loc să vorbească?**
Asigură-te că `ELEVENLABS_API_KEY` este setat. Fără el, vocea este dezactivată și agentul revine la text.

## Fundamente tehnice

Curios cum funcționează? Vezi [docs/technical.md](./docs/technical.md) pentru cercetările și deciziile de design din spatele familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistemul de dorințe și multe altele.

---

## Contribuții

familiar-ai este un experiment deschis. Dacă ceva din asta rezonează cu tine — fie tehnic, fie filozofic — contribuțiile sunt foarte binevenite.

**Locuri bune de început:**

| Domeniu | Ce este necesar |
|---------|------------------|
| Hardware nou | Suport pentru mai multe camere (RTSP, IP Webcam), microfoane, actuatori |
| Instrumente noi | Căutare web, automatizare acasă, calendar, orice prin MCP |
| Backend-uri noi | Orice LLM sau model local care se potrivește interfeței `stream_turn` |
| Șabloane pentru personalitate | Șabloane ME.md pentru diferite limbi și personalități |
| Cercetare | Modele de dorință mai bune, recuperarea memoriei, provocarea teoriei minții |
| Documentație | Tutoriale, ghiduri, traduceri |

Vezi [CONTRIBUTING.md](./CONTRIBUTING.md) pentru configurarea dezvoltării, stilul de cod și liniile directoare pentru PR.

Dacă nu ești sigur de unde să începi, [deschide o problemă](https://github.com/lifemate-ai/familiar-ai/issues) — bucuros să te îndrum în direcția potrivită.

---

## Licență

[MIT](./LICENSE)
