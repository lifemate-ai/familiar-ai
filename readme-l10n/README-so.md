# familiar-ai 🐾

**AI oo kula nool** — leh indho, cod, lugo, iyo xasuus.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai waa laacib AI ah oo ku nool gurigaaga.
Waa la dejin karaa daqiiqado gudahood. Koodh looma baahna.

Waxay dareentaa adduunka dhabta ah adiga oo kaashanaya kamaradaha, waxay dhaqdhaqaaqdaa jidh robot, waxay si cad u hadashaa, waxayna xasuusataa waxa ay aragto. Siinamee magac, qor shakhsiyadda, ka dibna u oggolow inay kula noolaato.

## Waxyaabaha ay qaban karto

- 👁 **Arag** — qabta sawirada ka socota kamarad Wi-Fi PTZ ama webcam USB
- 🔄 **Eeg agagaarka** — xagjirka kamaradda si ay u sahmiso agagaarkeeda
- 🦿 **Dhaqaaq** — ku wado vacuum robot si uu ugu furo qolka
- 🗣 **Hadlaa** — ku hadlaa iyada oo loo marayo ElevenLabs TTS
- 🎙 **Dhagaysi** — codka aan gacanta lagu isticmaalin iyada oo loo marayo ElevenLabs Realtime STT (ikhtiyaar)
- 🧠 **Xasuus** — si firfircoon u kaydiyo oo dib u xasuusato xasuusta adiga oo adeegsanaya raadinta semantiga (SQLite + embeddings)
- 🫀 **Fikradda Maskaxda** — waxay qaadataa aragtida qofka kale ka hor inta aysan ka jawaabin
- 💭 **Rabitaan** — waxay leedahay dalabkeeda gudaha oo kicisa dabeecadda madax-bannaan

## Sida ay u shaqeyso

familiar-ai waxay maamushaa [ReAct](https://arxiv.org/abs/2210.03629) wareeg ku shaqeeya doorashadaada LLM. Waxay dareentaa adduunka iyadoo adeegsanaysa alaabta, waxay ka fikirtaa waxa xiga oo ay dhaqaaqdaa — sidii qof kale.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Marka aan waxba samayn, waxay ku dhaqaaqdaa rabitaankeeda: xiiso, doonista inay eegto bannaanka, iyo ilmada qofka ay la nool tahay.

## Sida loo bilaabo

### 1. Ku rakib uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Ku rakib ffmpeg

ffmpeg ayaa **lagama maarmaan** u ah qabashada sawirada kamaradda iyo ciyaaridda codka.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ama ka soo deji [ffmpeg.org](https://ffmpeg.org/download.html) oo ku dar PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Hubi: `ffmpeg -version`

### 3. Clone oo rakib

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Habee

```bash
cp .env.example .env
# Edit .env with your settings
```

**Ugu yaraan waxay u baahan tahay:**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Keygaaga API ee madal la doortay |

**Ikhtiyaari:**

| Variable | Description |
|----------|-------------|
| `MODEL` | Magaca moodeelka (xulashooyin habboon oo ku xiran madal) |
| `AGENT_NAME` | Magaca muujinta oo muuqda TUI (tusaale `Yukine`) |
| `CAMERA_HOST` | Cinwaanka IP-ga kamaraddaada ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Aqoonsiga kamaradda |
| `ELEVENLABS_API_KEY` | Codka codka — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` si loo awoodsiiyo hadal-gacmeed had iyo jeer (waxaa loo baahan yahay `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Meesha lagu ciyaariyo codka: `local` (kuhadalka PC, default) \| `remote` (kuhadalka kamaradda) \| `both` |
| `THINKING_MODE` | Kaliya Anthropic — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Dhiirigelinta fikirka firfircoon: `high` (default) \| `medium` \| `low` \| `max` (Kaliya Opus 4.6) |

### 5. Abuur laacibkaaga

```bash
cp persona-template/en.md ME.md
# Edit ME.md — siin magac iyo shakhsiyadda
```

### 6. Orod

```bash
./run.sh             # TUI qoraal (la talinay)
./run.sh --no-tui    # REPL caadi ah
```

---

## Doorashada LLM

> **La talinayo: Kimi K2.5** — waxqabadka ugu fiican oo la tijaabiyey ilaa hadda. Waxay ogaataa macnaha, weydii su'aalo dheeraad ah, oo waxay si madax-bannaan uga dhaqaaqdaa siyaabo kale oo moodeellada aan sameynin. Qiime la mid ah Claude Haiku.

| Platform | `PLATFORM=` | Moodeelka default | Halka laga helayo furaha |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kaan ah (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (bixiye-multi) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (amarka) | — |

**Tusaale `.env` ah Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # ka socota platform.moonshot.ai
AGENT_NAME=Yukine
```

**Tusaale `.env` ah Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # ka socota api.z.ai
MODEL=glm-4.6v   # muuqaal leh; glm-4.7 / glm-5 = qoraal keliya
AGENT_NAME=Yukine
```

**Tusaale `.env` ah Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # ka socota aistudio.google.com
MODEL=gemini-2.5-flash  # ama gemini-2.5-pro oo leh awood dheeri ah
AGENT_NAME=Yukine
```

**Tusaale `.env` ah OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # ka socota openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # ikhtiyaar: qeex moodeel
AGENT_NAME=Yukine
```

> **Fiiro gaar ah:** Si aad u joojiso moodeellada maxalli/NVIDIA, si fudud ha u dejin `BASE_URL` iyo cinwaanka maxalliga ah sida `http://localhost:11434/v1`. Isticmaal bixiyeyaasha daruuraha halkii.

**Tusaale `.env` ah CLI tool:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = arg-ka dalabka
# MODEL=ollama run gemma3:27b  # Ollama — ma jiro {}, dalabku wuxuu u socdaa stdin
```

---

## Servers MCP

familiar-ai waxay ku xiran kartaa xoriyad kasta [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Tani waxay kuu oggolaanaysaa inaad ku xirto xasuus dibadda, gelin faylal, baaritaanka shabakadda, ama qalab kale.

Dejinta servers gudaha `~/.familiar-ai.json` (qaab la mid ah Claude Code):

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

Laba nooc oo gaadiid ah ayaa la taageeraa:
- **`stdio`**: kici subprocess maxalli ah (`command` + `args`)
- **`sse`**: ku xirnaada server HTTP+SSE (`url`)

Waxaad ka beddeli kartaa goobta faylka qaabeynta `MCP_CONFIG=/path/to/config.json`.

---

## Qalabka

familiar-ai waxay la shaqayn kartaa qalab kasta oo aad haysato — ama waxba.

| Qeyb | Waxa ay qabato | Tusaale | Lagama maarmaan? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Indho + qanjir | Tapo C220 (~$30) | **La talinaya** |
| USB webcam | Indho (xiran) | Kamarad UVC oo kasta | **La talinaya** |
| Robot vacuum | Lug | Nooc kasta oo ku habboon Tuya | Maya |
| PC / Raspberry Pi | Maskax | Wax kasta oo Python ku ordi kara | **Haa** |

> **Kamarad ayaa si xoog leh loogu talinayaa.** Iyadoo aan midna, familiar-ai si fiican ayey hadli kartaa — laakiin ma arki karto adduunka, taasoo ah waxa muhiimka ah.

### Dejin ugu yar (birlaaw)

Ma dooneysaa inaad tijaabiso? Kaliya waxaad u baahan tahay API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Orod `./run.sh` oo bilow sheekada. Ku dar qalab sida aad u socoto.

### Wi-Fi PTZ camera (Tapo C220)

1. Wax ka beddel Tapo app: **Settings → Advanced → Camera Account** — samee akoon maxalli ah (maahan akoon TP-Link)
2. Hel cinwaanka IP ee kamaradda liiska qalabkaaga routerka
3. Ku deje `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Cod (ElevenLabs)

1. Hel API key [elevenlabs.io](https://elevenlabs.io/)
2. Ku deje `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # ikhtiyaar, waxay isticmaashaa codka default haddii aan la sheegin
   ```

Waxaa jira laba meelood oo ciyaarid, oo lagu maamulo `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # kuhadalka PC (default)
TTS_OUTPUT=remote   # kuhadalka kamaradda oo kaliya
TTS_OUTPUT=both     # kuhadalka kamaradda + kuhadalka PC isku mar
```

#### A) Kamaradda codka (iyadoo loo marayo go2rtc)

Deji `TTS_OUTPUT=remote` (ama `both`). Waxay u baahan tahay [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Soo deji binary-ga bogga [releases](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Meel dhig oo magac beddel:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x ayaa loo baahan yahay

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Abuur `go2rtc.yaml` isla galkaas:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Isticmaal aqoonsiga akoonada kamaradda maxalliga ah (maahan akoonka daruuriga ee TP-Link).

4. familiar-ai waxay go2rtc si otomaatig ah u bilaabaysaa markii la furo. Haddii kamaraddaadu taageerto cod-laba geesood ah (backchannel), codka wuu ka ciyaari doonaa kuhadalka kamaradda.

#### B) Ku hadlaha PC maxalli ah

Default-ka (`TTS_OUTPUT=local`). Waxay isku dayeysaa ciyaartoyda kala horreeya: **paplay** → **mpv** → **ffplay**. Sidoo kale waxaa loo isticmaalaa sida ka-beddelka marka `TTS_OUTPUT=remote` iyo go2rtc uusan diyaar ahayn.

| OS | Rakib |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ama `paplay` iyadoo loo marayo `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — deji `PULSE_SERVER=unix:/mnt/wslg/PulseServer` gudaha `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — soo deji oo ku dar PATH, **ama** `winget install ffmpeg` |

> Haddii ciyaartoy codka ah aan la heli karin, hadalka wali waa la abuuri doonaa — waxa kaliya ee ma dhici doonaan inay ciyaaraan.

### Input cod (Realtime STT)

Deji `REALTIME_STT=true` gudaha `.env` si aad had iyo jeer ugu haboonaato codka aan gacanta lagu isticmaalin:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # isla furaha Labaad TTS
```

familiar-ai waxay qulqulaynaysaa codka mikrofoonka si ElevenLabs Scribe v2 oo si otomaatig ah u kaydisa qoraal-xusuusaha marka aad joojiso hadalka. Uma baahnid inaad riixdo badhanka. Waxay la co-exist kartaa habka riix-in-qar oo (Ctrl+T).

---

## TUI

familiar-ai waxaa ku jira UI terminiyaal ah oo la dhisay [Textual](https://textual.textualize.io/):

- Taariikh sheeko oo la daabacan karo leh qoraal toos ah
- Tab-gudbiye loogu talagalay `/quit`, `/clear`
- Joojinta wakhtiga agent-ka adiga oo qoraya inta ay ka fikirayso
- **Taariikhda sheekada** si otomaatig ah ayaa loogu keydiyey `~/.cache/familiar-ai/chat.log`

Si aad ula socoto taariikhda terminal kale (waxay waxtar leedahay marka la caddeeyo):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Shakhsiyadda (ME.md)

Shakhsiyadda laacibkaaga waxay ku jirtaa `ME.md`. Faylkaan waxaa laga ilaaliya git — adiga kaliya.

Eeg [`persona-template/en.md`](./persona-template/en.md) tusaale ahaan, ama [`persona-template/ja.md`](./persona-template/ja.md) nooca Japan.

---

## Su'aalaha Inta Badan La Isweydiiyo

**Q: Ma shaqeyn kartaa iyada oo aan GPU laga helin?**
Haa. Moodeelka embedding (multilingual-e5-small) waxay si fiican ugu shaqeysaa CPU. GPU waxa uu ka dhigayaa inuu si dhaqso ah u shaqeeyo laakiin lagama maarmaan maaha.

**Q: Ma isticmaali karaa kamarad ka duwan Tapo?**
Kamarad kasta oo taageerta ONVIF + RTSP waa inay shaqeysaa. Tapo C220 ayaa ah mid aan tijaabinay.

**Q: Ma xogtayda la diraa meel kale?**
Sawirada iyo qoraallada waa la diraa si ay u shaqeeyaan API-gaaga LLM. Xasuusku waa lagu kaydiyaa maxalli ah `~/.familiar_ai/`.

**Q: Maxaa yeelay agent-ka wuxuu qoraa `（...）` halkii uu ka hadli lahaa?**
Hubi in `ELEVENLABS_API_KEY` la dejiyo. Haddii aan la dejin, codka waa la baabi'inayaa oo agent-ka wuxuu ku dhawaaji doonaa qoraal.

## Asalka Farsamada

Xiiso badan ma leedahay sida ay u shaqeyso? Eeg [docs/technical.md](./docs/technical.md) si aad u aragto cilmi-baarista iyo go'aannada naqshadeynta ee ku saabsan familiar-ai — ReAct, SayCan, Reflexion, Voyager, nidaamka rabitaanka, iyo in ka badan.

---

## Ka Qaybqaadashada

familiar-ai waa tijaabo furan. Haddii mid ka mid ah tan ay la xiriirto adiga — farsamo ahaan ama falsafad ahaan — qeybqaadashada waa si weyn loo soo dhoweyaa.

**Meelo wanaagsan oo laga bilaabi karo:**

| Area | Wax lagama maarmaan ah |
|------|---------------|
| Qalab cusub | Taageero kamarado badan (RTSP, IP Webcam), mikrofoonada, hawlgallada |
| Qalab cusub | Baaritaanka shabakadda, otomaatiga guriga, jadwalka, wax kasta oo MCP ku dhex jira |
| Dhex-dhexaadiye cusub | Wax kasta oo LLM ah ama moodeel maxalli ah oo ku habboon `stream_turn` interface |
| Template Shakhsiyadda | Template-yada ME.md ee luqado iyo shakhsiyado kala duwan |
| Cilmi-baaris | Moodeelada rabitaanka wanaagsan, soo kabashada xasuusta, dhiirrigelinta fikradda-maskaxda |
| Dukumentiga | Tababaro, guddiga, tarjumo |

Eeg [CONTRIBUTING.md](./CONTRIBUTING.md) si aad u hesho deeqda horumarinta, qaabka koodhka, iyo tilmaamaha PR.

Haddii aadan hubin halka aad ku bilaabi karto, [furo arrin](https://github.com/lifemate-ai/familiar-ai/issues) — waxaan ku faraxsanahay inaan ku tilmaamo jidka saxda ah.

---

## Ruqsad

[MIT](./LICENSE)
