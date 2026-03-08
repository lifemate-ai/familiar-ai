```markdown
# familiar-ai 🐾

**Mākslīgais intelekts, kas dzīvo kopā ar jums** — ar acīm, balsi, kājām un atmiņu.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Pieejams 74 valodās](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ir AI pavadonis, kas dzīvo jūsu mājās.
Iestatiet to dažu minūšu laikā. Nav nepieciešama kodēšana.

Tas uztver reālo pasauli caur kamerām, pārvietojas uz robota ķermeņa, runā skaļi un atceras to, ko redz. Iedodiet tam vārdu, rakstiet tā personību un ļaujiet tam dzīvot kopā ar jums.

## Ko tas var darīt

- 👁 **Redzēt** — uzņem attēlus no Wi-Fi PTZ kameras vai USB webkameras
- 🔄 **Aplūkot apkārt** — griež un maina kameras leņķi, lai izpētītu apkārtni
- 🦿 **Pārvietoties** — vada robota sūknēšanas ierīci, lai pārvietotos pa istabu
- 🗣 **Runāt** — runā caur ElevenLabs TTS
- 🎙 **Klausīties** — bezrokas balss ievade caur ElevenLabs Realtime STT (piekrišana)
- 🧠 **Atcerēties** — aktīvi uzglabā un atsauc atmiņas ar semantisko meklēšanu (SQLite + iemaldījumi)
- 🫀 **Prāta teorija** — ņem otra cilvēka perspektīvu pirms atbildēšanas
- 💭 **Vēlme** — piemīt iekšējās vēlmes, kas izraisa autonomu uzvedību

## Kā tas darbojas

familiar-ai darbojas ar [ReAct](https://arxiv.org/abs/2210.03629) ciklu, ko aktivizē jūsu izvēlētais LLM. Tas uztver pasauli caur rīkiem, domā par to, ko darīt tālāk, un rīkojas — tieši tā, kā to darītu cilvēks.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kad tas ir neaktīvs, tas rīkojas saskaņā ar savām vēlmēm: ziņķarība, vēlme paskatīties ārā, izsist savai personai, ar kuru tas dzīvo.

## Sākt darbu

### 1. Instalējiet uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Vai: `winget install astral-sh.uv`

### 2. Instalējiet ffmpeg

ffmpeg ir **nepieciešams** kameru attēlu uzņemšanai un audio atskaņošanai.

| OS | Komanda |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — vai lejupielādējiet no [ffmpeg.org](https://ffmpeg.org/download.html) un pievienojiet PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Pārbaudiet: `ffmpeg -version`

### 3. Klonējiet un instalējiet

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurācija

```bash
cp .env.example .env
# Rediģējiet .env ar saviem iestatījumiem
```

**Minimālie prasības:**

| Mainīgais | Apraksts |
|-----------|----------|
| `PLATFORM` | `anthropic` (noklusējums) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Jūsu API atslēga izvēlētajai platformai |

**Piemēram:**

| Mainīgais | Apraksts |
|-----------|----------|
| `MODEL` | Modeļa nosaukums (jēgpilni noklusējumi katrai platformai) |
| `AGENT_NAME` | Redzamais vārds, kas parādās TUI (piemēram, `Yukine`) |
| `CAMERA_HOST` | Jūsu ONVIF/RTSP kameras IP adrese |
| `CAMERA_USER` / `CAMERA_PASS` | Kameras kredenciāli |
| `ELEVENLABS_API_KEY` | Balss izejai — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, lai aktivizētu vienmēr ieslēgtu bezrokas balss ievadi (prasa `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kur atskaņot audio: `local` (PC skaļrunis, noklusējums) \| `remote` (kameras skaļrunis) \| `both` |
| `THINKING_MODE` | Tikai Anthropic — `auto` (noklusējums) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptīvais domāšanas piepūles līmenis: `high` (noklusējums) \| `medium` \| `low` \| `max` (tikai Opus 4.6) |

### 5. Izveidojiet savu familiar

```bash
cp persona-template/en.md ME.md
# Rediģējiet ME.md — dodiet tam vārdu un personību
```

### 6. Palaižam

**macOS / Linux / WSL2:**
```bash
./run.sh             # Teksts TUI (ieteicams)
./run.sh --no-tui    # Parasts REPL
```

**Windows:**
```bat
run.bat              # Teksts TUI (ieteicams)
run.bat --no-tui     # Parasts REPL
```

---

## Izvēloties LLM

> **Ieteicams: Kimi K2.5** — labākā agentiskā veiktspēja līdz šim pārbaudīta. Pamanām kontekstu, uzdod turpmākus jautājumus un rīkojas autonomi tādās manierēs, kādas citi modeļi to nedara. Cenas ziņā līdzīgs Claude Haiku.

| Platforma | `PLATFORM=` | Noklusējuma modelis | Kur iegūt atslēgu |
|-----------|------------|---------------------|-------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI saderīgs (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (vairāku nodrošinātāju) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI rīks** (claude -p, ollama…) | `cli` | (komanda) | — |

**Kimi K2.5 `.env` piemērs:**
```env
PLATFORM=kimi
API_KEY=sk-...   # no platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` piemērs:**
```env
PLATFORM=glm
API_KEY=...   # no api.z.ai
MODEL=glm-4.6v   # redzes iespēja; glm-4.7 / glm-5 = tikai tekstam
AGENT_NAME=Yukine
```

**Google Gemini `.env` piemērs:**
```env
PLATFORM=gemini
API_KEY=AIza...   # no aistudio.google.com
MODEL=gemini-2.5-flash  # vai gemini-2.5-pro ar augstāku jaudu
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` piemērs:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # no openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcional: norādiet modeli
AGENT_NAME=Yukine
```

> **Piezīme:** Lai atslēgtu vietējās/NVIDIA modeļus, vienkārši nenorādiet `BASE_URL` uz vietējo gala punktu, piemēram, `http://localhost:11434/v1`. Izmantojiet mākoņu sniedzējus.

**CLI rīka `.env` piemērs:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = uzvedne
# MODEL=ollama run gemma3:27b  # Ollama — nav {}, uzvedne iet caur stdin
```

---

## MCP serveri

familiar-ai var pieslēgties jebkuram [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serverim. Tas ļauj pievienot ārēju atmiņu, piekļuvi failu sistēmai, tīmekļa meklēšanu vai jebkuru citu rīku.

Konfigurējiet serverus `~/.familiar-ai.json` (tas pats formāts kā Claude Code):

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

Divi transporta veidi ir atbalstīti:
- **`stdio`**: palaidiet lokālu apakšprocesu (`command` + `args`)
- **`sse`**: pieslēgties HTTP+SSE serverim (`url`)

Pārdefinējiet konfigurācijas faila atrašanās vietu ar `MCP_CONFIG=/path/to/config.json`.

---

## Aparatūra

familiar-ai darbojas ar jebkuru aparatūru, kas jums ir — vai arī nevienu.

| Daļa | Ko tā dara | Piemērs | Nepieciešama? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kamera | Acis + kakls | Tapo C220 (~$30, Eufy C220) | **Ieteicams** |
| USB webkamera | Acis (fiksētas) | Jebkura UVC kamera | **Ieteicams** |
| Robota sūknēšanas ierīce | Kājās | Jebkurš Tuya saderīgs modelis | Nē |
| PC / Raspberry Pi | Smadzenes | Jebkas, kas var darbināt Python | **Jā** |

> **Kamera ir stingri ieteicama.** Bez tās, familiar-ai var runāt — bet tas nevar redzēt pasauli, kas ir tāds kā viss jēga.

### Minimāla iestatīšana (nav aparatūras)

Vienkārši vēlaties izmēģināt? Jums nepieciešama tikai API atslēga:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Palaižiet `./run.sh` (macOS/Linux/WSL2) vai `run.bat` (Windows) un sāciet sarunu. Pievienojiet aparatūru laikā.

### Wi-Fi PTZ kamera (Tapo C220)

1. Tapo lietotnē: **Iestatījumi → Paplašinātie iestatījumi → Kameras konts** — izveidojiet vietējo kontu (nevis TP-Link kontu)
2. Atrodiet kameras IP savā maršrutētāja ierīču sarakstā
3. Iestatiet `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=jūsu-vietējais-lietotājs
   CAMERA_PASS=jūsu-vietējā-parole
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


### Balss (ElevenLabs)

1. Iegūstiet API atslēgu vietnē [elevenlabs.io](https://elevenlabs.io/)
2. Iestatiet `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcional, izmanto noklusējuma balsi, ja atstājāt izlaistu
   ```

Ir divas atskaņošanas vietas, ko kontrolē `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC skaļrunis (noklusējums)
TTS_OUTPUT=remote   # tikai kamerā
TTS_OUTPUT=both     # kamerā + PC skaļrunis vienlaikus
```

#### A) Kameras skaļrunis (caur go2rtc)

Iestatiet `TTS_OUTPUT=remote` (vai `both`). Prasa [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Lejupielādējiet bināro failu no [izlaidumu lapas](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Novietojiet un pārdēvējiet to:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # nepieciešama chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Veidojiet `go2rtc.yaml` tajā pašā direktorijā:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Izmantojiet vietējā konta kredenciālus (nevis TP-Link mākoņa kontu).

4. familiar-ai automātiski sāk go2rtc palaišanas laikā. Ja jūsu kamera atbalsta divvirzienu audio (atpakaļkanāls), balss tiek atskaņota no kameras skaļruņa.

#### B) Vietējais PC skaļrunis

Noklusējums (`TTS_OUTPUT=local`). Mēģina atskaņotājprogrammas secībā: **paplay** → **mpv** → **ffplay**. Arī tiek izmantots kā rezervju variants, kad `TTS_OUTPUT=remote` un go2rtc nav pieejams.

| OS | Instalējiet |
|----|-------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (vai `paplay` caur `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — iestatiet `PULSE_SERVER=unix:/mnt/wslg/PulseServer` `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — lejupielādējiet un pievienojiet PATH, **vai** `winget install ffmpeg` |

> Ja nav pieejams nevienis audio atskaņotājs, runa joprojām tiek ģenerēta — tā vienkārši netiks atskaņota.

### Balss ievade (Realtime STT)

Iestatiet `REALTIME_STT=true` `.env`, lai aktivizētu vienmēr ieslēgtu, bezrokas balss ievadi:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # tā pati atslēga kā TTS
```

familiar-ai straumē mikrofonu audio uz ElevenLabs Scribe v2 un auto-iedod transkriptus, kad pārtraucat runāt. Nav nepieciešama pogas nospiešana. Labi sadzīvo ar nospied-pat-nogalināšanas režīmu (Ctrl+T).

---

## TUI

familiar-ai ietver terminālā UI, kas būvēts ar [Textual](https://textual.textualize.io/):

- Ritina sarunu vēsturi ar tiešraides tekstu
- Tab-completion `/quit`, `/clear`
- Pārtrauciet aģentu pa vidu, rakstot, kamēr tas domā
- **Sarunu žurnāls** automātiski saglabāts `~/.cache/familiar-ai/chat.log`

Lai sekotu žurnālam citā terminālī (noderīgi kopēšanai-ielīmēšanai):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Jūsu familiar personība dzīvo `ME.md`. Šis fails ir gitignored — tas ir tikai jūsu.

Skatiet [`persona-template/en.md`](./persona-template/en.md) kā piemēru, vai [`persona-template/ja.md`](./persona-template/ja.md) japāņu versijai.

---

## Biežāk uzdotie jautājumi

**Q: Vai tas strādā bez GPU?**
Jā. Iemaldījumu modelis (multilingual-e5-small) darbojas labi uz CPU. GPU padara to ātrāku, bet nav obligāts.

**Q: Vai es varu izmantot citu kameru, nevis Tapo?**
Jebkura kamera, kas atbalsta Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: Vai mana dati tiek nosūtīti kur?**
Attēli un teksti tiek nosūtīti uz jūsu izvēlēto LLM API apstrādei. Atmiņas tiek uzglabātas lokāli `~/.familiar_ai/`.

**Q: Kāpēc aģents raksta `（...）` nevis runā?**
Pārliecinieties, ka ir iestatīta `ELEVENLABS_API_KEY`. Bez tā balss ir atslēgta, un aģents atgriežas pie teksta.

## Tehniskais fons

Interesē, kā tas darbojas? Skatiet [docs/technical.md](./docs/technical.md) pētījumus un dizaina lēmumus, kas stāv aiz familiar-ai — ReAct, SayCan, Reflexion, Voyager, vēlmes sistēma un vēl daudz vairāk.

---

## Iesaistīšanās

familiar-ai ir atvērts eksperiments. Ja kāda no šīm tēmām rezonē ar jums — tehniski vai filozofiski — ieguldījumi ir ļoti laipni gaidīti.

**Labas vietas, kur sākt:**

| Joma | Kas ir nepieciešams |
|------|---------------------|
| Jauna aparatūra | Atbalsts vairākām kamerām (RTSP, IP webkamera), mikrofoniem, aktuatatoriem |
| Jauni rīki | Tīmekļa meklēšana, mājas automatizācija, kalendārs, jebkas caur MCP |
| Jauni aizmugures | Jebkurš LLM vai vietējais modelis, kas atbilst `stream_turn` interfeisam |
| Persona veidnes | ME.md veidnes dažādām valodām un personībām |
| Pētniecība | Labāki vēlmes modeļi, atmiņas atgūšana, prāta teorijas pamudināšana |
| Dokumentācija | Apmācības, gidi, tulkojumi |

Skatiet [CONTRIBUTING.md](./CONTRIBUTING.md) par izstrādātāja iestatīšanu, koda stilu un PR vadlīnijām.

Ja neesat droši, kur sākt, [atveriet problēmu](https://github.com/lifemate-ai/familiar-ai/issues) — prieks norādīt pareizajā virzienā.

---

## Licenze

[MIT](./LICENSE)
```
