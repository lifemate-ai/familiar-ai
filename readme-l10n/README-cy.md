```markdown
# familiar-ai 🐾

**AI sy'n byw gyda thi** — gyda llygaid, llais, coesau, a chof.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Ar gael mewn 74 iaith](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai yw cymar AI sy'n byw yn dy gartref.
Gosodwch hi mewn munudau. Dim codio'n angenrheidiol.

Mae'n deall y byd real trwy gamariau, yn symud o amgylch ar gorff robot, yn siarad yn uchel, a'n cofio'r hyn a welodd. Rhowch enw iddi, ysgrifennwch ei phersonoliaeth, a gadewch iddi fyw gyda thi.

## Beth all hi ei wneud

- 👁 **Gwelwch** — yn dal lluniau o gamera PTZ Wi-Fi neu gamera USB
- 🔄 **Edrych o gwmpas** — yn panner a symud y camera i archwilio ei chyffiniau
- 🦿 **Symud** — yn gyrrwr pwmpen robot i deithio drwy'r ystafell
- 🗣 **Siarad** — yn siarad trwy ElevenLabs TTS
- 🎙 **Gwrando** — mewnbwn llais di-hadau trwy ElevenLabs Realtime STT (dewisol)
- 🧠 **Cofio** — yn actif yn storio a chofio atgofion gyda chwiliad semanteg (SQLite + ymgyffro)
- 🫀 **Theori o Feddwl** — yn cymryd perpectif yr unigolyn arall cyn ymateb
- 💭 **Dymuniad** — mae ganddi ei gyffro mewnol ei hun sy'n achosi ymddygiad hunanllywodraethol

## Sut mae'n gweithio

mae familiar-ai yn rhedeg [ReAct](https://arxiv.org/abs/2210.03629) cylch sydd wedi'i bweru gan dy ddewis o LLM. Mae'n deall y byd trwy offer, yn meddwl am beth i'w wneud nesaf, a phan gynnau — yn union fel y byddai person.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Pan yn ddi-gymryd, mae'n gweithredu ar ei dymuniadau ei hun: chwilfrydedd, eisiau edrych tu allan, colli'r person y mae'n byw gyda.

## Dechrau

### 1. Gosod uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Neu: `winget install astral-sh.uv`

### 2. Gosod ffmpeg

mae ffmpeg yn **angenrheidiol** ar gyfer dal lluniau camera a chwarae sain.

| OS | Gorchymyn |
|----|----------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — neu llwytho o [ffmpeg.org](https://ffmpeg.org/download.html) a'i ychwanegu i PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Cadarnhewch: `ffmpeg -version`

### 3. Clone a gosod

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Cyfluniwch

```bash
cp .env.example .env
# Gwnewch addasiadau `.env` gyda'ch gosodiadau
```

**Mae'r isafswm yn angenrheidiol:**

| Amod | Disgrifiad |
|------|------------|
| `PLATFORM` | `anthropic` (diffyg) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Eich allwedd API ar gyfer y llwyfan a ddewiswyd |

**Dewisol:**

| Amod | Disgrifiad |
|------|------------|
| `MODEL` | Enw'r model (diffyg sensibl ar bob llwyfan) |
| `AGENT_NAME` | Enw arddangos a ddangosir yn y TUI (e.e. `Yukine`) |
| `CAMERA_HOST` | Cyfeiriad IP eich camera ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Cyfrinachau camera |
| `ELEVENLABS_API_KEY` | Ar gyfer allbwn llais — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` i alluogi mewnbwn llais di-hadau bob amser (mae angen `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Ble i chwarae sain: `local` (speakar PC, diffyg) \| `remote` (speakar camera) \| `both` |
| `THINKING_MODE` | Dim ond Anthropic — `auto` (diffyg) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Ymdrech feddwl addasol: `high` (diffyg) \| `medium` \| `low` \| `max` (dim ond Opus 4.6) |

### 5. Creu dy familiar

```bash
cp persona-template/en.md ME.md
# Golygu ME.md — rhoi enw a phersonoliaeth iddi
```

### 6. Rhedeg

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI testunol (argymhell)
./run.sh --no-tui    # REPL plân
```

**Windows:**
```bat
run.bat              # TUI testunol (argymhell)
run.bat --no-tui     # REPL plân
```

---

## Dewis LLM

> **Argymhell: Kimi K2.5** — y perfformiad agentic gorau a brofwyd hyd yma. Mae'n sylwi ar gyd-destun, yn gofyn cwestiynau dilynol, a gweithredu'n hunangynheladwy mewn ffyrdd nad yw modelau eraill yn ei wneud. Wedi ei brisio yn debyg i Claude Haiku.

| Llwyfan | `PLATFORM=` | Model diffyg | Ble i gael allwedd |
|---------|-------------|--------------|--------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Cymhwysfeydd OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Offer CLI** (claude -p, ollama…) | `cli` | (y gorchymyn) | — |

**Enghraifft `.env` ar gyfer Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # o platform.moonshot.ai
AGENT_NAME=Yukine
```

**Enghraifft `.env` ar gyfer Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # o api.z.ai
MODEL=glm-4.6v   # wedi'i alluogi gan weledigaeth; glm-4.7 / glm-5 = testun yn unig
AGENT_NAME=Yukine
```

**Enghraifft `.env` ar gyfer Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # o aistudio.google.com
MODEL=gemini-2.5-flash  # neu gemini-2.5-pro ar gyfer gallu uwch
AGENT_NAME=Yukine
```

**Enghraifft `.env` ar gyfer OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # o openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # dewisol: nodi model
AGENT_NAME=Yukine
```

> **Nodyn:** I ddiffodd modelau lleol/NVIDIA, dim ond peidiwch â gosod `BASE_URL` i benbwynt lleol fel `http://localhost:11434/v1`. Defnyddiwch ddarparwyr cwmwl yn ei le.

**Enghraifft CLI tool `.env`:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = arg prompt
# MODEL=ollama run gemma3:27b  # Ollama — dim {}, mae'r prompt yn mynd trwy stdin
```

---

## Gweinyddion MCP

gall familiar-ai gysylltu ag unrhyw [gweinydd MCP (Model Context Protocol)](https://modelcontextprotocol.io). Mae hyn yn gadael i ti ymgorffori cof allanol, mynediad i system ffeiliau, chwiliad gwe, neu unrhyw offer arall.

Cyfluniwch weinyddion yn `~/.familiar-ai.json` (yr un fformat â Claude Code):

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

Mae dwy fath cludiant yn cael eu cefnogi:
- **`stdio`**: lansio self-proses lleol (`gorchymyn` + `args`)
- **`sse`**: cysylltu â gweinydd HTTP+SSE (`url`)

Gallar ddirwyn y lleoliad ffeil gyhoeddiad gyda `MCP_CONFIG=/path/to/config.json`.

---

## Caledwaith

mae familiar-ai yn gweithio gyda pha bynnag offer sydd gennyf — neu dim o gwbl.

| Rhan | Beth mae'n ei wneud | Enghraifft | Angen? |
|------|---------------------|------------|---------|
| Camera PTZ Wi-Fi | Llygaid + gwddf | Tapo C220 (~$30) | **Argymhell** |
| Camera USB | Llygaid (ffisegol) | Unrhyw gamera UVC | **Argymhell** |
| Pwmpen robot | Coesau | Unrhyw fodel sy'n gydnaws â Tuya | Na |
| PC / Raspberry Pi | Ymennydd | Unrhyw beth sy'n rhedeg Python | **Ie** |

> **Mae camera yn annerchadwy.** Heb un, gall familiar-ai dal siarad — ond ni all wel neu gyffwrdd â'r byd, sy'n rhyw fath o'r holl bwynt.

### Gosodiad lleiaf (dim caledwedd)

Mo'n gallu dadlau? Dim ond mae arnoch angen allwedd API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Rhedwch `./run.sh` (macOS/Linux/WSL2) neu `run.bat` (Windows) a dechrau sgwrsio. Ychwanegwch offer wrth fynd.

### Camera PTZ Wi-Fi (Tapo C220)

1. Mewn ap Tapo: **Dewisiadau → Uwch → Cyfrif Camera** — creu cyfrif lleol (nid cyfrif TP-Link)
2. Dod o hyd i gyfeiriad IP y camera yn rhestr dy feintiau
3. Gosod yn `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=dy-gyfrif-leol
   CAMERA_PASS=dy- gyfrinach-leol
   ```

### Llais (ElevenLabs)

1. Cael allwedd API ar [elevenlabs.io](https://elevenlabs.io/)
2. Gosod yn `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # dewisol, yn defnyddio llais diffyg os bydd yn cael ei ddileu
   ```

Mae dwy leoliad chwarae, a reolir gan `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # speakar PC (diffyg)
TTS_OUTPUT=remote   # speakar camera yn unig
TTS_OUTPUT=both     # speakar camera + speakar PC ar yr un pryd
```

#### A) Speakar camera (trwy go2rtc)

Gosodwch `TTS_OUTPUT=remote` (neu `both`). Mae angen [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Llwythwch y binary o'r [tudalen rhyddhau](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Lleolwch a newid ei enw:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x angenrheidiol

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Creu `go2rtc.yaml` yn yr un cyfeiriad:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://DY_CAM_USER:DY_CAM_PASS@DY_CAM_IP/stream1
   ```
   Defnyddiwch gyrolion cyfrif camera lleol (nid eich cyfrif cwmwl TP-Link).

4. mae familiar-ai yn dechrau go2rtc yn awtomatig ar lansio. Os yw dy gamera yn cefnogi sain dwy ffordd (cynffon), mae llais yn chwarae o'r siaradwr camera.

#### B) Speakar PC lleol

Y diffyg (`TTS_OUTPUT=local`). Ceisiwch chwaraewyr yn nhrefn: **paplay** → **mpv** → **ffplay**. Caiff ei defnyddio hefyd fel gollyngwr pan mai `TTS_OUTPUT=remote` ac nad yw go2rtc ar gael.

| OS | Gosod |
|----|-------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (neu `paplay` trwy `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — gosod `PULSE_SERVER=unix:/mnt/wslg/PulseServer` yn `.env` |
| Windows | [mpv.io/gosod](https://mpv.io/installation/) — llwythwch a'i ychwanegu i PATH, **neu** `winget install ffmpeg` |

> Os nad oes chwaraewr sain ar gael, mae llais yn dal i gael ei gynhyrchu — ni fydd yn chwarae, fodd bynnag.

### Mewnbwn llais (Realtime STT)

Gosodwch `REALTIME_STT=true` yn `.env` ar gyfer mewnbwn llais di-hadau bob amser:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # yr un allwedd â TTS
```

mae familiar-ai yn llifio sain meicroffon i ElevenLabs Scribe v2 a'u cyhoeddi'n auto-pan fyddwch yn rhoi yr ystyr o siarad. Dim angen pwysau botwm. Ymgorfforiad gyda'r modd i bwyso i siarad (Ctrl+T).

---

## TUI

mae familiar-ai yn cynnwys UI dyfrnod a adeiladwyd gyda [Textual](https://textual.textualize.io/):

- Hanes sgwrsiau sy'n sgrolio gyda thestun byw
- Cwblhau tab ar gyfer `/quit`, `/clear`
- Interrupt y agent yn ystod tro trwy deipio tra bo'n meddwl
- **Log sgwrs** wedi'i autosaflu i `~/.cache/familiar-ai/chat.log`

I ddilyn y log yn terminal arall (defnyddiol ar gyfer copïo-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Mae personoliaeth dy familiar yn byw yn `ME.md`. Mae'r ffeil hon yn gitignored — dim ond i ti sy'n berchen arni.

Gweler [`persona-template/en.md`](./persona-template/en.md) am engraf, neu [`persona-template/ja.md`](./persona-template/ja.md) am fersiwn Siapaneaidd.

---

## CWESTIYNAU CYFFREDIN

**C: A yw'n gweithio heb GPU?**
Ydy. Mae'r model ymgyffro (multilingual-e5-small) yn rhedeg yn iawn ar CPU. Mae GPU'n gwneud iddo fod yn gyflymach ond ddim yn ofynnol.

**C: A allaf ddefnyddio camera arall heblaw am Tapo?**
Ym mhob camera sy'n cefnogi ONVIF + RTSP dylai weithio. Tapo C220 yw'r camera a brofwyd.

**C: A yw fy data yn cael ei hanfon i unrhyw le?**
Mae delweddau a thestun yn cael eu hanfon i dy LLM API a ddewiswyd ar gyfer prosesu. Mae atgofion yn cael eu storio'n lleol yn `~/.familiar_ai/`.

**C: Pam mae'r agent yn ysgrifennu `（...）` yn lle siarad?**
Gwnewch yn siŵr bod `ELEVENLABS_API_KEY` wedi'i gosod. Hebddo, mae llais wedi'i ddiffodd a'r agent yn dychwelyd at destun.

## Cefndir technegol

Oeddet ti'n chwilfrydedd am sut mae'n gweithio? Gweler [docs/technical.md](./docs/technical.md) am y ymchwil a'r penderfyniadau dylunio yn y tu ôl i familiar-ai — ReAct, SayCan, Reflexion, Voyager, y system dymuniad, a mwy.

---

## Cyfrannu

mae familiar-ai yn arbrofi agored. Os yw unrhyw un o hyn yn taro â thi — yn dechnegol neu'n feddylgar — mae cyfraniadau'n cael eu croesawu'n fawr.

**Lleoedd da i ddechrau:**

| Ardal | Beth sydd ei angen |
|-------|-------------------|
| Caledwedd newydd | Cefnogaeth ar gyfer mwy o gamarau (RTSP, Camera IP), meicroffonau, gweithredu |
| Offer newydd | Chwilio gwe, awtomatiaeth cartref, calendr, unrhyw beth trwy MCP |
| Cefnweithiau newydd | Unrhyw LLM neu fodel lleol sy'n ffitio'r rhyngwyneb `stream_turn` |
| Templedi persona | Templedi ME.md ar gyfer ieithoedd a phersonoliaethau gwahanol |
| Ymchwil | Modelau dymuniad gwell, adfer cof, cyfarwyddyd theori o feddwl |
| Dogfennaeth | Tiwtorialau, cerdded drwy, cyfieithiadau |

Gweler [CONTRIBUTING.md](./CONTRIBUTING.md) am osod dev, arddull cod, a chanllawiau PR.

Os nad oes unrhyw gyswllt ar ba le i ddechrau, [agoriwch broblem](https://github.com/lifemate-ai/familiar-ai/issues) — yn hapus i dy gyfeirio i'r cyfeiriad cywir.

---

## Trwydded

[MIT](./LICENSE)
```
