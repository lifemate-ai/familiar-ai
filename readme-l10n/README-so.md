# familiar-ai 🐾

**Haddii AI oo la nool yahay agaa** — leh indho, cod, lugo, iyo xusuus.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Lagu helay 74 luqadood](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai waa AI saaxiib ah oo ku nool gurigaaga.
Dejiso daqiiqado gudahood. Koodh u baahan maahan.

Waxay aragtaa adduunka dhabta ah iyadoo loo marayo kamaradaha, waxay ku dhaqaaqdaa jidhka robotka, waxay hadashaa, waxayna xasuusataa waxa ay aragto. Siiso magac, qor shakhsiyaddeeda, oo u ogolow inay kula noolaato.

## Waxay sameyn karta

- 👁 **Arag** — qabta sawirro ka socota kamarad Wi-Fi PTZ ama webcam USB
- 🔄 **Eeg agagaarka** — wuxuu rogaa oo wuxuu leexin kaamarka si uu u baadho agagaarkeeda
- 🦿 **Dhaqaaq** — wuxuu kaxeeyaa vacuum robot si uu u dhex socdo qolka
- 🗣 **Hadlo** — wuxuu hadlaa iyada oo loo marayo ElevenLabs TTS
- 🎙 **Dhageyso** — habka codka oo gacmo la'aan ah iyada oo loo marayo ElevenLabs Realtime STT (ikhtiyaari)
- 🧠 **Xusuus** — si firfircoon ayuu u kaydiyaa oo u soo celinayaa xusuus leh raadinta macnaha (SQLite + embeds)
- 🫀 **Fikradda Maskaxda** — waxay qaadanaysaa aragtida dadka kale ka hor inta aysan jawaabin
- 💭 **Rabitaan** — waxay leedahay xoogag gudaha ah oo kicisa dabeecadaha madaxbannaan

## Sida ay u shaqeyso

familiar-ai waxay socotaa [ReAct](https://arxiv.org/abs/2210.03629) wareeg oo ay ku xiran tahay dookhaaga LLM. Waxay aragtaa adduunka iyadoo adeegsaneysa qalab, waxayna ka fikiraysaa waxa ay sameynayso xiga, kadibna waxay dhaqaaqdaa — sida qof kale.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Marka ay raaxo leedahay, waxay ka jawaabtaa rabitaankeeda: welwel, rabitaannada in la eego banaanka, waxayna ka maqantaa qofka ay la nool tahay.

## Sida loo bilaabo

### 1. Ku rakib uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Ama: `winget install astral-sh.uv`

### 2. Ku rakib ffmpeg

ffmpeg waa **lagama maarmaan** si loo qabto sawirrada kamarada iyo dib u ciyaarista codka.

| OS | Amar |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ama soo degso [ffmpeg.org](https://ffmpeg.org/download.html) oo ku dar PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Hubi: `ffmpeg -version`

### 3. Clone oo rakib

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Deji

```bash
cp .env.example .env
# Tafatir .env adigoo adeegsanaya dejimahaaga
```

**U baahan yare:**

| Variable | Sharaxaad |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Furahaaga API ee madasha la doortay |

**Ikhtiyaari:**

| Variable | Sharaxaad |
|----------|-------------|
| `MODEL` | Magaca moodalka (tiro macquul ah oo ah midka xiliga madasha) |
| `AGENT_NAME` | Magaca la muujiyo ee muuqaalka TUI (tusaale: `Yukine`) |
| `CAMERA_HOST` | Cinwaanka IP ee kamarada ONVIF/RTSP-gaaga |
| `CAMERA_USER` / `CAMERA_PASS` | Aqoonsiga kamarada |
| `ELEVENLABS_API_KEY` | Si loogu soo saaro codka — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` si loo dhaqaajiyo codka oo had iyo jeer gacmo la'aan ah (waxaa looga baahan yahay `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Halka lagu ciyaarayo codka: `local` (maqalka PC, default) \| `remote` (maqalka kamarada) \| `both` |
| `THINKING_MODE` | Kaliya Anthropic — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Dedaal fikirka oo la hagaajiyo: `high` (default) \| `medium` \| `low` \| `max` (Kaliya Opus 4.6) |

### 5. Samee familiar-kaaga

```bash
cp persona-template/en.md ME.md
# Tafatir ME.md — siiso magac iyo shakhsiyad
```

### 6. Socodsii

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI qoraal ah (la talinay)
./run.sh --no-tui    # REPL caadi ah
```

**Windows:**
```bat
run.bat              # TUI qoraal ah (la talinay)
run.bat --no-tui     # REPL caadi ah
```

---

## Doorashada LLM

> **La tali: Kimi K2.5** — waxqabadka ugu wanaagsan ee la tijaabiyey ilaa iyo hadda. Wuxuu waeelaa macnaha, weydiiya su'aalo raac ah, wuxuuna si madaxbannaan ugu dhaqaaqaa siyaabo aan moodallo kale sameynin. Qiimihiisu waa mid la mid ah Claude Haiku.

| Platform | `PLATFORM=` | Moodal default | Halka laga helo furaha |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (amar) | — |

**Kimi K2.5 `.env` tusaale:**
```env
PLATFORM=kimi
API_KEY=sk-...   # laga soo qaaday platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` tusaale:**
```env
PLATFORM=glm
API_KEY=...   # laga soo qaaday api.z.ai
MODEL=glm-4.6v   # muuqaal leh; glm-4.7 / glm-5 = qoraal kaliya
AGENT_NAME=Yukine
```

**Google Gemini `.env` tusaale:**
```env
PLATFORM=gemini
API_KEY=AIza...   # laga soo qaaday aistudio.google.com
MODEL=gemini-2.5-flash  # ama gemini-2.5-pro si loo helo awood sare
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` tusaale:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # laga soo qaaday openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # ikhtiyaar: tilmaam moodal
AGENT_NAME=Yukine
```

> **Fiiro gaar ah:** Si looga joojiyo moodallo gudaha/NVIDIA ah, si fudud ha u dejin `BASE_URL` meel qodob ah sida `http://localhost:11434/v1`. Isticmaal adeegyo daruur ah halkii.

**CLI tool `.env` tusaale:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — ma jiraan {}, prompt wuxuu ku socda stdin
```

---

## MCP Servers

familiar-ai waxay ku xidhmi kartaa kasta [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Tani waxay kuu ogolaaneysaa inaad geliso xusuus dibedda, helitaanka faylka nidaamka, raadin webka, ama qalab kale oo kasta.

Dejiso server-yada ee `~/.familiar-ai.json` (qaab isku mid ah sida Claude Code):

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

Laba nooc oo gaadiid ah ayaa la taageeray:
- **`stdio`**: bilaabi subprocess maxalli ah (`command` + `args`)
- **`sse`**: ku xir HTTP+SSE server (`url`)

Beddel meesha faylka la keydiyo adiga oo adeegsanaya `MCP_CONFIG=/path/to/config.json`.

---

## Qalabka

familiar-ai waxay la shaqeyn kartaa qalab kasta oo aad haysato — ama waxba.

| Qayb | Waxa ay sameyneyso | Tusaale | U baahan? |
|------|-------------|---------|-----------|
| Kamarada Wi-Fi PTZ | Indhaha + qoorta | Tapo C220 (~$30) | **La talinay** |
| Webcam USB | Indho (deggan) | Kamarad kasta oo UVC ah | **La talinay** |
| Vacuum robot | Lugaha | Moodal kasta oo la jaanqaadaya Tuya | Maya |
| PC / Raspberry Pi | Maskaxda | Wax kasta oo Python ku shaqeeya | **Haa** |

> **Kamarad waa la talinayaa.** Iyadoo mid la'aan ah, familiar-ai wali waxay hadli kartaa — laakiin ma arki karto adduunka, taas oo ah sababta asaasiga ah.

### Dejinta yar (wax qalab ah maahan)

Kaliya ma rabtaa inaad tijaabiso? Waxaad kaliya u baahan tahay furaha API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Socodsii `./run.sh` (macOS/Linux/WSL2) ama `run.bat` (Windows) oo bilaaw wada hadalka. Qalab ku dar sidii aad u socoto.

### Kamarada Wi-Fi PTZ (Tapo C220)

1. App-ka Tapo: **Settings → Advanced → Camera Account** — samee akoon maxalli ah (ma aha akoon TP-Link)
2. Hel IP-ga kamaradaada liiska qalabka ee router-kaaga
3. dejin `.`env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Cod (ElevenLabs)

1. Hel furaha API ee [elevenlabs.io](https://elevenlabs.io/)
2. Dejiso `.`env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # ikhtiyaar, waxay isticmaashaa codka default haddii la seego
   ```

Waxaa jira laba goobo ciyaar ah, oo lagu xakameynayo `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # maqalka PC (default)
TTS_OUTPUT=remote   # maqalka kamarada oo kaliya
TTS_OUTPUT=both     # maqalka kamarada + maqalka PC isla mar
```

#### A) Maqalka kamarada (iyadoo loo marayo go2rtc)

Dejiso `TTS_OUTPUT=remote` (ama `both`). Waxay u baahan tahay [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Soo degso binary kaaga bogga [release-yada](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Meel dhig oo magac u baddal:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x waa lagama maarmaan

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Samee `go2rtc.yaml` isla galkaas:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Isticmaal aqoonsiga kamarada maxalliga ah (ma aha akoonka TP-Link cloud).

4. familiar-ai waxay si otomaatig ah u bilaabaysaa go2rtc markii la bilaabayo. Haddii kamaradaadu taageerto cod wadaag ah (backchannel), codka wuxuu ka ciyaaraysaa maqalka kamarada.

#### B) Maqalka PC-ga maxalliga ah

Tusaale ahaan (`TTS_OUTPUT=local`). Waxay isku dayaysaa ciyaartoyda si ay u dooratid: **paplay** → **mpv** → **ffplay**. Sidoo kale loo isticmaali doonaa sida ka dib marka `TTS_OUTPUT=remote` oo go2rtc aan la heli karin.

| OS | Rakib |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ama `paplay` iyada oo loo marayo `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — deji `PULSE_SERVER=unix:/mnt/wslg/PulseServer` ee `.`env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — download oo ku dar PATH, **ama** `winget install ffmpeg` |

> Haddii ciyaartoy cod aan la heli karin, hadalka wali waa la sameeyaa — kaliya ma ciyaari doono.

### Codka galinta (Realtime STT)

Dejiso `REALTIME_STT=true` ee `.`env` si loogu soo dhajiyo codka, had iyo jeer gacmo la'aan:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # isla furaha sida TTS
```

familiar-ai waxay qaybisaa codka makarafoonka ilaa ElevenLabs Scribe v2 oo auto-ku dejiya qoralka markaad joojiso hadalka. Ma jirto badhan la riixo oo loo baahan yahay. Waxay si wada jir ah ula noolaan kartaa habka riix-ta-hadal (Ctrl+T).

---

## TUI

familiar-ai waxay ka kooban tahay UI terminal oo la dhisay iyadoo la adeegsanayo [Textual](https://textual.textualize.io/):

- Taariikhda wada hadalka ee la rogi karo oo leh qoraal toos ah oo baxaya
- Dhammaystirka tabka ee `/quit`, `/clear`
- Joojiya wakiilka bartamaha xilliga fikirka adiga oo qorin intay ka fikirayso
- **Diiwaanka wada hadalka** oo si otomaatig ah loogu kaydiyo `~/.cache/familiar-ai/chat.log`

Si aad ugu raacdo diiwaanka terminal kale (useful for copy-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Shakhsiyadda familiar-kaaga waxay ku taallaa `ME.md`. Faylkan waa gitignored — adiga kaliya ayaa haysta.

Eeg [`persona-template/en.md`](./persona-template/en.md) tusaale ahaan, ama [`persona-template/ja.md`](./persona-template/ja.md) nooca Japanese.

---

## FAQ

**Su'aal: Ma shaqaynaysaa iyadoo aan GPU la isticmaalin?**
Haa. Moodalka embedding (multilingual-e5-small) si fiican ayuu ugu shaqeeyaa CPU. GPU wuxuu ka dhigayaa mid degdeg ah laakiin lagama maarmaan maaha.

**Su'aal: Ma isticmaali karaa kamarad ka duwan Tapo?**
Kamarad kasta oo taageerta ONVIF + RTSP waa inay shaqeysaa. Tapo C220 waa inta aan tijaabinnay.

**Su'aal: Ma xogtaydu meelo kale ayaa la dirayaa?**
Sawirrada iyo qoraallada waxaa loo diraa API-ga LLM-gaaga ee la doortay si loo farsameeyo. Xusuusta waxaa lagu kaydiyaa maxalliga ah ee `~/.familiar_ai/`.

**Su'aal: Maxaa yeelay wakiilka wuxuu qoraa `（...）` halkii uu ka hadli lahaa?**
Hubi in `ELEVENLABS_API_KEY` la dejiyay. Haddii aan la dejin, codka ayaa la wyროგ მადებაʻotaამაშ======кжы--[jك  th ղb salt hagati]]. Munaasaba@endsection]",
