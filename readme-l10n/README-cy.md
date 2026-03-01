# familiar-ai 🐾

**AI sy'n byw ochr yn ochr â chi** — gyda llygaid, llais, traed, a chof.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai yw cyfaill AI sy'n byw yn eich cartref.
Gosodwch ef mewn munudau. Dim codio sydd ei angen.

Mae'n canfod y byd go iawn drwy gamera, yn symud o gwmpas ar gorff robot, yn siarad yn uchel, ac yn cofio'r hyn y mae'n ei weld. Rhowch enw iddo, ysgrifennwch ei bersonoliaeth, a gadewch iddo fyw gyda chi.

## Beth mae'n gallu ei wneud

- 👁 **Gwelwch** — yn dal delweddau o gamera PTZ Wi-Fi neu webcam USB
- 🔄 **Edrych o gwmpas** — yn pannu a chodi'r camera i archwilio ei amgylchedd
- 🦿 **Symud** — yn gyrru glanhau robot i deithio o gwmpas ystafell
- 🗣 **Siarad** — yn siarad drwy ElevenLabs TTS
- 🎙 **Gwrando** — mewnbwn llais di-law drwy ElevenLabs Realtime STT (opt-in)
- 🧠 **Cofio** — yn storio a chofio cofannau yn weithredol gyda chwiliad semantig (SQLite + embeddings)
- 🫀 **Theori o Feddwl** — yn cymryd persbectif y person arall cyn ymateb
- 💭 **Dymuniad** — mae ganddo ei dymuniadau mewnol ei hun sy'n achosi ymddygiad hunanllywodraethol

## Sut mae'n gweithio

mae familiar-ai yn rhedeg cylch [ReAct](https://arxiv.org/abs/2210.03629) a gefnogir gan eich dewis o LLM. Mae'n canfod y byd trwy offer, yn meddwl am yr hyn i'w wneud nesaf, ac yn gweithredu — yn union fel byddai rhywun.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Pan fydd yn ddi-waith, mae'n gweithredu ar ei dymuniadau ei hun: curiaeth, eisiau edrych ymhellach, colli'r person y mae'n byw gyda.

## Dechrau

### 1. Gosodwch uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Gosodwch ffmpeg

mae ffmpeg yn **angenrheidiol** ar gyfer dal delweddau rhag camera a chplay eang.

| OS | Gorchymyn |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — neu lawrlwythwch oddi ar [ffmpeg.org](https://ffmpeg.org/download.html) a'i ychwanegu i'r PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Dilyswch: `ffmpeg -version`

### 3. Clone a gosodwch

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Ffurfweddu

```bash
cp .env.example .env
# Gwybodaeth amgylchedd .env gyda'ch gosodiadau
```

**Anghenion isaf:**

| Mwyndod | Disgrifiad |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Eich allwedd API ar gyfer y llwyfan dewiswyd |

**Dewisol:**

| Mwyndod | Disgrifiad |
|----------|-------------|
| `MODEL` | Enw model (dewis sensitif yn ôl y llwyfan) |
| `AGENT_NAME` | Enw arddangos a ddangosir yn y TUI (e.e. `Yukine`) |
| `CAMERA_HOST` | Cyfeiriad IP eich camera ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Cydnabyddion y camera |
| `ELEVENLABS_API_KEY` | Ar gyfer allbwn llais — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` i alluogi mewnbwn llais di-law bob amser (mae angen `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Ble i chwarae sain: `local` (speakers PC, yn ddiofid) \| `remote` (speaker camera) \| `both` |
| `THINKING_MODE` | Dim ond Anthropic — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Ymdrech feddwl addasol: `high` (default) \| `medium` \| `low` \| `max` (dim ond Opus 4.6) |

### 5. Creu eich cyfaill

```bash
cp persona-template/en.md ME.md
# Golygu ME.md — rhowch enw a phersonoliaeth iddo
```

### 6. Rhedeg

```bash
./run.sh             # TUI ysgrifenedig (argymhellir)
./run.sh --no-tui    # REPL syml
```

---

## Dewis LLM

> **Argymhellir: Kimi K2.5** — perfformiad agentig gorau a brofwyd hyd yma. Mae'n sylwi ar gyd-destun, yn gofyn cwestiynau dilynol, ac yn gweithredu yn hunanllywodraethol mewn ffyrdd nad yw modelau eraill yn gwneud. Pris tebyg i Claude Haiku.

| Platfform | `PLATFORM=` | Model default | Ble i gael allwedd |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (y gorchymyn) | — |

**Esampl `.env` Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # o platform.moonshot.ai
AGENT_NAME=Yukine
```

**Esampl `.env` Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # o api.z.ai
MODEL=glm-4.6v   # cynnwrch-gweladwy; glm-4.7 / glm-5 = testun yn unig
AGENT_NAME=Yukine
```

**Esampl `.env` Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # o aistudio.google.com
MODEL=gemini-2.5-flash  # neu gemini-2.5-pro am mwy o allu
AGENT_NAME=Yukine
```

**Esampl `.env` OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # o openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # dewisol: nodwch model
AGENT_NAME=Yukine
```

> **Nodyn:** I analluogi modelau lleol/NVIDIA, peidiwch ag osod `BASE_URL` i ddiweddyn lleol fel `http://localhost:11434/v1`. Defnyddiwch ddarparwyr cwmwl yn hytrach na hynny.

**Esampl `.env` offer CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = arg prompt
# MODEL=ollama run gemma3:27b  # Ollama — dim {}, bydd y prompt yn mynd drwy stdin
```

---

## Gweinyddion MCP

mae familiar-ai yn gallu cysylltu â phob gweinydd [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Mae hyn yn eich galluogi i glymu at gof external, mynediad i system ffeil, chwilio trwy we, neu unrhyw offer arall.

Ffurfweddwch weinyddion yn `~/.familiar-ai.json` (yr un fformat â Claude Code):

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

Mae dau ddimensiwn cludiant yn cael eu cefnogi:
- **`stdio`**: lansio proses lleol (`command` + `args`)
- **`sse`**: cysylltu â gweinydd HTTP+SSE (`url`)

Gwaith drwg i drosi lleoliad y ffeil gynfigwr gyda `MCP_CONFIG=/path/to/config.json`.

---

## Caledwaith

mae familiar-ai yn gweithio gyda phob caledwedd sydd gennych — neu ddim o gwbl.

| Rhan | Beth mae'n ei wneud | Enghraifft | Angenrheidiol? |
|------|-------------|---------|-----------|
| Camera PTZ Wi-Fi | Llygaid + gwddf | Tapo C220 (~$30) | **Argymhellir** |
| Webcam USB | Llygaid (fixed) | Unrhywbeth UVC | **Argymhellir** |
| Glanhau robot | Traed | Unrhywbeth sy'n cyd-fynd â Tuya | Dim |
| PC / Raspberry Pi | Ymennydd | Dim ond rhaid i unrhyw beth redeg Python | **Ie** |

> **Argymhellir camera.** Heb un, gall familiar-ai siarad — ond ni all weld y byd, sy'n cwblhan y pwynt.

### Gosodiad sylfaenol (dim caledwaith)

Dim ond eisiau ei brofi? Dim ond angen allwedd API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Rhedwch `./run.sh` a dechreuwch siarad. Ychwanegwch caledwaith wrth fynd.

### Camera PTZ Wi-Fi (Tapo C220)

1. Yn y cais Tapo: **Gosodiadau → Uwch → Cyfrif Camera** — creu cyfrif lleol (nid cyfrif TP-Link)
2. Dychmygwch IP y camera yn rhestr dyfeisiau eich rwystr
3. Gosodwch yn `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Llais (ElevenLabs)

1. Cael allwedd API ar [elevenlabs.io](https://elevenlabs.io/)
2. Gosodwch yn `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # dewisol, yn defnyddio llais default os heb ei nodi
   ```

Mae dwy gyrchfan chwarae, a reolir gan `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # speaker PC (default)
TTS_OUTPUT=remote   # speaker camera yn unig
TTS_OUTPUT=both     # speaker camera + speaker PC yn unig
```

#### A) Speaker camera (trwy go2rtc)

Gosodwch `TTS_OUTPUT=remote` (neu `both`). Mae angen [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Lawrlwythwch y binary oddi wrth y [drosglwyddiadau](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Rhowch a newid ei enw:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x sydd ei angen

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Creu `go2rtc.yaml` yn yr un cyfeiriad:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Defnyddiwch gofrestriadau ar gyfer cyfrif lleol y camera (nid yw'r cyfrif cwmwl TP-Link).

4. Mae familiar-ai yn dechrau go2rtc yn awtomatig pan fydd yn cychwyn. Os yw eich camera yn cefnogi sain ddwy ffordd (cynhelwr nwy), bydd llais yn chwarae o siaradwr y camera.

#### B) Speaker PC lleol

Y default (`TTS_OUTPUT=local`). Ceisia chwarae ym mhrawfdyf yn y drefn honno: **paplay** → **mpv** → **ffplay**. Defnyddir hefyd fel dychwelyd pan fydd `TTS_OUTPUT=remote` ac nid yw go2rtc ar gael.

| OS | Gosodwch |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (neu `paplay` trwy `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — gosodwch `PULSE_SERVER=unix:/mnt/wslg/PulseServer` yn `.env` |
| Windows | [mpv.io/gosodiad](https://mpv.io/installation/) — lawrlwythwch a'i ychwanegu i'r PATH, **neu** `winget install ffmpeg` |

> Os nad oes chwaraewr sain ar gael, cynhelir lleferydd o hyd — ni fydd yn chwarae.

### Mewnbwn llais (Realtime STT)

Gosodwch `REALTIME_STT=true` yn `.env` ar gyfer mewnbwn llais di-law bob amser:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # yr un allwedd â TTS
```

mae familiar-ai yn llifo sain y meicroffon i ElevenLabs Scribe v2 ac yn awtomatig yn cofrestru trawsgrifiadau pan fyddwch yn aros yn siarad. Nid oes angen gwasgu botwm. Mae'n cyd-fyw gyda'r dull pwyswch-i-siarad (Ctrl+T).

---

## TUI

mae familiar-ai yn cynnwys UI terminal wedi'i adeiladu gyda [Textual](https://textual.textualize.io/):

- Hanes sgwrsadwy gyda thestun streameg yn fyw
- Cwblhau tab ar gyfer `/quit`, `/clear`
- Preifate'r agent yn ystod troi trwy deipio tra mae'n meddwl
- **Cofnod sgwrs** yn awtomatig yn cael ei achub i `~/.cache/familiar-ai/chat.log`

I ddilyn y cofnod mewn terminal arall (defnyddiol ar gyfer copïo-gludo):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Mae personoliaeth eich cyfaill yn byw yn `ME.md`. Mae'r ffeil hon wedi'i gwrthod gan git — eich un chi yw hi yn unig.

Gwyliwch [`persona-template/en.md`](./persona-template/en.md) am esiampl, neu [`persona-template/ja.md`](./persona-template/ja.md) am fersiwn Siapan.

---

## Cwestiynau Cyffredin

**C: A yw'n gweithio heb GPU?**
Ie. Mae'r model embeddiad (multilingual-e5-small) yn rhedeg yn dda ar CPU. Mae GPU yn ei wneud yn gyflymach ond nid yw'n angenrheidiol.

**C: A allaf ddefnyddio camera heblaw am Tapo?**
Dylai unrhyw gamera sy'n cefnogi ONVIF + RTSP weithio. Tapo C220 yw'r un a brofwyd.

**C: A yw fy data wedi'i anfon unrhyw ble?**
Mae delweddau a testunau yn cael eu hanfon i'ch API LLM dewisedig am brosesu. Mae cofannau yn cael eu storio'n lleol yn `~/.familiar_ai/`.

**C: Pam mae'r agent yn ysgrifennu `（...）` yn lle siarad?**
Gwnewch yn siŵr fod `ELEVENLABS_API_KEY` wedi'i osod. Hebddo, mae lleferydd wedi'i analluogi ac mae'r agent yn chwilio yn ôl at destun.

## Cefndir Technegol

Diddorol am sut mae'n gweithio? Gwyliwch [docs/technical.md](./docs/technical.md) am y ymchwil a'r penderfyniadau dylunio ynghylch familiar-ai — ReAct, SayCan, Reflexion, Voyager, y system dymuniad, a mwy.

---

## Cyfrannu

mae familiar-ai yn arbrofion agored. Os yw unrhyw un o hyn yn cyd-fynd â chi — yn dechnegol neu yn feddyliol — mae croeso i gyfraniadau.

**Lleoedd da i ddechrau:**

| Ardal | Beth sydd ei angen |
|------|---------------|
| Caledwedd newydd | Cefnogaeth ar gyfer mwy o gamera (RTSP, IP Webcam), meicroffonau, gweithredwyr |
| Offer newydd | Chwilio gwe, awtomeiddio cartref, calendr, unrhyw beth trwy MCP |
| Dychweliad newydd | Unrhyw LLM neu fodel lleol sy'n ffitio'r rhyngwyneb `stream_turn` |
| Templedi persona | Templedi ME.md ar gyfer ieithoedd a phersonoliaethau gwahanol |
| Ymchwil | Gwell modelau dymuniad, adfer cof, cyfarwyddo ar theori o feddwl |
| Dogfennaeth | Tiwtorialau, cerbydau, cyfieithiadau |

Gwyliwch [CONTRIBUTING.md](./CONTRIBUTING.md) am sefydlu datblygiad, arddull cod, a chanllawiau PR.

Os ydych yn ansicr ble i ddechrau, [agorwch fater](https://github.com/lifemate-ai/familiar-ai/issues) — hapus i'ch cyfeirio yn y cyfeiriad cywir.

---

## Trwydded

[MIT](./LICENSE)
