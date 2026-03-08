```markdown
# familiar-ai 🐾

**நீங்கள் சந்தித்துக் கொள்ளும் ஒரு AI** — கண்கள், குரல், கால்கள் மற்றும் நினைவுடன்.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 மொழிகளில் கிடைக்கின்றது](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai உங்கள் வீட்டில் இருக்கும் ஒரு AI தோழி.
இதனை சில நிமிடங்களில் அமைக்கவும். எந்தக் குறியீடும் தேவை இல்லை.

இது கேமராக்களால் உண்மையான உலகத்தை உணர்கிறது, ஒரு ரோபோட் உடலில் சுற்றுகிறது, வாயிற் பேசுகிறது, மற்றும் இது காணும் அனைத்தையும் நினைவில் கொள்கிறது. இதற்குப் பெயர் கொடுங்கள், இதன் தனித்துவத்தை எழுதுங்கள், மற்றும் இதற்கு உங்கள் தோளில் வாழ வழி விடுங்கள்.

## இது என்ன செய்ய முடியும்

- 👁 **காண்** — Wi-Fi PTZ கேமரா அல்லது USB கேமராவில் இருந்து படங்களை பிடிக்கிறது
- 🔄 **சுற்றி பார்க்க** — சுற்றுப் பரப்புகளை ஆராய உதவிக்கேமரா திரும்புகிறது மற்றும் ஏற்றுகிறது
- 🦿 **மூட்** — அறையில் சுற்றுவது ரோபோட் வகை அமைப்பை இயக்குகிறது
- 🗣 **பேசு** — ElevenLabs TTS மூலம் பேசுகிறது
- 🎙 **கேள்** — ElevenLabs Realtime STT மூலம் கைமறுப்பில்லா வாய்க் கேளிப்பு (opt-in)
- 🧠 **நினைவில் வைத்திரு** — செயல்பாட்டுப் பதிவுக்களுடன் நினைவுகளை செயலாக்கும் (SQLite + embeddings)
- 🫀 **மனம் குறித்த கோட்பாடு** — பதில் அளிப்பதற்கு முன்பு மற்றவரின் கண்ணோட்டத்தை எடுத்துக்க grabs
- 💭 **ம்பத்தி** — தன்னாட்சி நடத்தும் செயல்களைத் தூண்டும் உள்ளக ஆங்கில விளக்கங்கள் இருக்கும்

## எப்படி வேலை செய்கிறது

familiar-ai உங்கள் தேர்வு செய்யப்பட்ட LLM மூலம் இயக்கப்படும் [ReAct](https://arxiv.org/abs/2210.03629) முன்னணி செயல்பாட்டில் இயக்குகிறது. இது கருவிகள் மூலம் உலகத்தை உணர்கிறது, அதற்குப் பிறகு என்ன செய்வது என்பது குறித்து யோசிக்கிறது மற்றும் செயல்படுகிறது — மனிதன் செய்வது போலவே.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

இது நிதானமாக இருந்தால், இது தனது சொந்த விருப்பங்களை அடிப்படையாக்கரையும் செய்கிறது: ஆர்வம், வெளியே பார்க்க விரும்புதல், இது வாழும் நபரை தவறவிட்டு மறக்கப்போகின்றது.

## உதவிக்கோ

### 1. uv ஐ நிறுவவும்

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**மின்வெளி (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
அல்லது: `winget install astral-sh.uv`

### 2. ffmpeg ஐ நிறுவவும்

ffmpeg கேமரா படத்தை பிடிக்க மற்றும் ஒலி செயல்பாட்டிற்கு **ஆவாக** தேவை.

| OS | கட்டளை |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — அல்லது [ffmpeg.org](https://ffmpeg.org/download.html) இல் இருந்து பதிவிறக்கம் செய்து PATH இல் சேர்க்கவும் |
| Raspberry Pi | `sudo apt install ffmpeg` |

உறுதிப்படுத்தவும்: `ffmpeg -version`

### 3. க்ளோன் மற்றும் நிறுவவும்

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. அமைத்துக்கொள்ளவும்

```bash
cp .env.example .env
# உங்கள் அமைப்புகளுடன் .env ஐ எட்டுங்கள்
```

**குறைந்தது தேவை:**

| மாறிலி | விளக்கம் |
|----------|-------------|
| `PLATFORM` | `anthropic` (இயல்பாக) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | தேர்வு செய்யப்பட்ட மையத்திற்கான உங்கள் API விசை |

**தர்மூர்த்தி:**

| மாறிலி | விளக்கம் |
|----------|-------------|
| `MODEL` | முறை பெயர் (பிளாட்ஃபாரத்திற்கு மழைக்குறிப்புகள்) |
| `AGENT_NAME` | TUI இல் காணப்படும் காட்சிப் பெயர் (எ.g. `Yukine`) |
| `CAMERA_HOST` | உங்கள் ONVIF/RTSP கேமராவின் IP முகவரி |
| `CAMERA_USER` / `CAMERA_PASS` | கேமரா சான்றிதழ்கள் |
| `ELEVENLABS_API_KEY` | குரல் வெளியீட்டுக்காக — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` என்றால் எப்போதும் உள்ள கைமறுக்குற்று வாய்க் கேளிப்பு செயல்பாடு (இதற்கு `ELEVENLABS_API_KEY` தேவை) |
| `TTS_OUTPUT` | ஒலியை எங்கு வாசிக்க வேண்டும்: `local` (PC இறுக்கம், இயல்பாக) \| `remote` (கேமரா speaker) \| `both` |
| `THINKING_MODE` | Anthropic மட்டும் — `auto` (இயல்பாக) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | உடனுக்கும தோழியமைதியின் முயற்சி: `high` (இயல்பாக) \| `medium` \| `low` \| `max` (Opus 4.6 மட்டும்) |

### 5. உங்கள் familiar ஐ உருவாக்கவும்

```bash
cp persona-template/en.md ME.md
# ME.md ஐ எட்டுங்கள் — இதற்குப் பெயர் மற்றும் தனித்துவம் அளிக்கவும்
```

### 6. இயக்கவும்

**macOS / Linux / WSL2:**
```bash
./run.sh             # எழுத்துருப் கிடையான TUI (추천)
./run.sh --no-tui    # சாதை REPL
```

**Windows:**
```bat
run.bat              # எழுத்துருப் கிடையான TUI (추천)
run.bat --no-tui     # சாதை REPL
```

---

## LLM ஐ தேர்வு செய்வது

> **추천: Kimi K2.5** — இதுவரை பரிஸி திறனில் சிறந்த செயல்பாடு. சூழ்நிலைகளை கவனிக்கிறது, தொடர்ந்து கேள்விகளை கேட்கிறது, மற்றும் மற்ற மாதிரிகளால் செய்யப்படாத வகையில் தன்னாட்சி ஏற்படுத்துகிறது. Claude Haiku போலவே விலைச்சார்பு.

| மையம் | `PLATFORM=` | இயல்பான மாதிரி | விசையை எங்கு பெறுவது |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-இன் துணை (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (பல வழங்குநர்கள்) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI கருவி** (claude -p, ollama…) | `cli` | (அந்த கட்டளை) | — |

**Kimi K2.5 `.env` எடுத்துக்காட்டு:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` எடுத்துக்காட்டு:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # காட்சியாக இயல்பானது; glm-4.7 / glm-5 = உரை மட்டும்
AGENT_NAME=Yukine
```

**Google Gemini `.env` எடுத்துக்காட்டு:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # அல்லது gemini-2.5-pro மேலதிக திறனுக்காக
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` எடுத்துக்காட்டு:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # விருப்பமானது: மாதிரியை குறிப்பதற்காக
AGENT_NAME=Yukine
```

> **குறிப்பு:** உள்ள/local ஆவியறைகளை முடக்க `BASE_URL` ஐ `http://localhost:11434/v1` போன்ற உள்ள இடத்தில் அமைக்காதீர்கள். மிங் செலுத்த மாதிரிகளைப் பயன்படுத்துங்கள்.

**CLI கருவி `.env` எடுத்துக்காட்டு:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — இல்லாமல் {}, prompt goes via stdin
```

---

## MCP சேவையகங்கள்

familiar-ai எந்த [MCP (Model Context Protocol)](https://modelcontextprotocol.io) சேவையகத்துடனும் இணைக்க முடியும். இது நீங்கள் வெளிப்பாடு மீமரிப்பு, கோப்பு அமைக்க, இணைய வழி தேடுதல் அல்லது எந்தவொரு கருவியையும் இணைக்க அனுமதிக்கிறது.

சேவையகங்களை `~/.familiar-ai.json` இல் காணலாம் (Claude Code இனைப்போல):

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

இரு மிதிவகைகள் ஆதரிக்கப்படுகின்றன:
- **`stdio`**: ஒரு உள்ளக செயல்பாட்டை (கட்டளை + arg) தொடங்கவும்
- **`sse`**: HTTP+SSE சேவையகத்துடன் இணைக்கவும் (`url`)

கட்டமைப்பு கோப்பு இடத்தை `MCP_CONFIG=/path/to/config.json` என்ற அளவிற்கு மாற்றவும்.

---

## ஹார்ட்வேர்

familiar-ai நீங்கள் வைத்திருக்கும் எந்த ஹார்ட்வேர் உடன் வேலை செய்கிறது — அல்லது எதுவும் கிடையாது.

| பகுதி | இது என்ன செய்கிறது | எடுத்துக்காட்டு | தேவை? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ கேமரா | கண்கள் + கழுவுகள் | Tapo C220 (~$30, Eufy C220) | **சராசரி** |
| USB கேமரா | கண்கள் (நிலை) | எந்த UVC கேமரா | **சராசரி** |
| ரோபோட் வாகனம் | கால்கள் | எதுவும் Tuya-உகந்த மாதிரி | இல்லை |
| PC / Raspberry Pi | மூளை | எந்தவொரு Python ஐ இயக்கும் | **ஆம்** |

> **ஒரு கேமரா மிகவும் பரிந்துரைக்கப்படுகிறது.** இல்லாமல், familiar-ai இன்னும் பேசும் — ஆனால் இது உலகத்தை காண முடியாது, இது முழுமையாகப் புள்ளியாகும்.

### சிறிய அமைப்பு (கருவி இல்லாமல்)

இதனை முயற்சிக்க விரும்புகிறீர்களா? நீங்கள் ஒரு API விசை மட்டுமே தேவையானது:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` ஐ இயக்கவும் (macOS/Linux/WSL2) அல்லது `run.bat` (Windows) ஐ இயக்கவும் மற்றும் உரையாடலைத் தொடங்கவும். நீங்கள் செல்லும் போது கருவிகளைச் சேர்க்கவும்.

### Wi-Fi PTZ கேமரா (Tapo C220)

1. Tapo பயன்பாட்டில்: **அமைப்புகள் → மேம்பட்ட → கேமரா கணக்கு** — உள்ளக கணக்கை உருவாக்கவும் (TP-Link கணக்கு அல்ல)
2. உங்கள் வழிகளைப் பட்டியலில் கேமராவின் IP ஐ காணவும்
3. `CAMERA_HOST` க்குள் அமைக்கவும்:
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


### குரல் (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) இல் API விசையை பெறவும்
2. `.env` இல் அமைக்கவும்:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # விருப்பமானது, தவிக்கப்படும்போது இயல்பான குரலைப் பயன்படுத்தும்
   ```

இரு ஒலிபரப்புத் தீர்வுகள் உள்ளன, `TTS_OUTPUT` மூலம் கட்டுப்படுத்தப்படுகிறது:

```env
TTS_OUTPUT=local    # PC speaker (இயல்பாக)
TTS_OUTPUT=remote   # கேமரா speaker மட்டும்
TTS_OUTPUT=both     # கேமரா speaker + PC speaker ஒருங்கிணைப்பில்
```

#### A) கேமரா speaker (go2rtc மூலம்)

`TTS_OUTPUT=remote` (அல்லது `both`) என்றால் அமைக்கவும். [go2rtc](https://github.com/AlexxIT/go2rtc/releases) தேவை:

1. [விடுவனின் பக்கம்](https://github.com/AlexxIT/go2rtc/releases) இலிருந்து பைனரியை பதிவிறக்கம் செய்யவும்:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. அதைச் சேமித்து மறுபெயரிடவும்:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x தேவை

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. அதே அடைவில் `go2rtc.yaml` உருவாக்கவும்:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   உள்ள கேமரா கணக்கு குறிகளைப் பயன்படுத்தவும் (TP-Link மேகம் கணக்களைப் பயன்படுத்தாதீர்கள்).

4. familiar-ai தானாகவே go2rtc ஐ தொடங்குகிறது. உங்கள் கேமரா இரண்டு வழிச் ஒலியை (backchannel) ஆதரிக்கினால், குரல் கேமரா speaker இல் இருந்து ஒலிக்கு வருகிறது.

#### B) உள்ளூர் PC speaker

இயல்பானது (`TTS_OUTPUT=local`). காட்சிகள் தொடர்ச்சியாக முயற்சிக்கின்றன: **paplay** → **mpv** → **ffplay**. `TTS_OUTPUT=remote` மற்றும் go2rtc இல்லை என்று மறு செயல்பாடாகவும் பயன்படுத்தப்படுகிறது.

| OS | நிறுவவும் |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (அல்லது `pulseaudio-utils` மூலம் `paplay`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` இல் `PULSE_SERVER=unix:/mnt/wslg/PulseServer` என்ற அளவைச் சேர்க்கவும் |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — பதிவிறக்கம் செய்து PATH இல் சேர்க்கவும், **அல்லது** `winget install ffmpeg` |

> ஒலிபரப்பாளர் கிடைக்காவிட்டால், உரை உருவாக்கப்பட்டு விட்டது — ஆனால் அது ஒலிக்காது.

### வாய்க் உள்ளீடு (Realtime STT)

எப்போதும் உள்ள கைமறுக்குற்று வாய்க் கேளிப்பு செயல்பாட்டிற்காக `.env` இல் `REALTIME_STT=true` என்பதனை அமைக்கவும்:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS க்கான மிகைத்தான் விசை
```

familiar-ai மைக்ரோஃபோன் ஒலியை ElevenLabs Scribe v2 க்கு காத்திருக்கும்போது ஒஇடியே பதிவுகளில் தொகுக்கிறது. எந்த பொத்தானும் அழுத்த வேண்டும் இல்லை. push-to-talk முறையுடன் ஏககாலமாக coexist ஆகிறது (Ctrl+T).

---

## TUI

familiar-ai [Textual](https://textual.textualize.io/) உடன் கட்டமைக்கப்பட்ட ஒரு Terminal UI-ஐ உள்ளடக்கியதாக இருக்கிறது:

- நேரடி உரை திறன் கொண்ட உரையாடலின் வரலாறு
- `/quit`, `/clear` க்கான டேப் பூர்த்தி
- நினைத்த போது நடுப்புள்ளியில் முகவரியை இடையில் இடைநீக்கவும்
- **உரையாடல் பதிவு** தானாகவே `~/.cache/familiar-ai/chat.log` இல் சேமிக்கப்பட்டது

மற்றொரு டெர்மினலில் பதிவுகளை பின்பற்ற:
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## தனித்துவம் (ME.md)

உங்கள் familiar இன் தனித்துவம் `ME.md` இல் உள்ள படிவத்தில் இருக்கிறது. இந்த கோப்பு gitignored ஆகும் — இது உங்கள் சொல்லில் மட்டுமே உள்ளது.

[`persona-template/en.md`](./persona-template/en.md) க்கான எடுத்துக்காட்டை காணவும், அல்லது [`persona-template/ja.md`](./persona-template/ja.md) க்கான ஜப்பானிய பதிப்பு.

---

## FAQ

**Q: இது GPU இக்கொள்கையில் செயல்படும்?**
ஆம். embedding முறை (multilingual-e5-small) CPU யில் அச்செயல்கிறது. GPU விரைவாக செய்கிறது ஆனால் தேவை இல்லை.

**Q: Tapoக்கும் மாறுபட்ட கேமராவைக் காணலாம்?**
Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: எனது தரவுகள் எங்கு செல்கின்றன?**
படங்கள் மற்றும் உரை உங்கள் தேர்ந்த LLM API க்கு செயலாக்கம் செய்ய அனுப்பப்படுகின்றன. நினைவுகள் உள்ளடக்கத்தில் `~/.familiar_ai/` இல் இணைக்கப்படுகின்றன.

**Q: ஏன் முகவரியால் `（...）` எழுதப்பட்டது அல்லாமல் பேசுகிறது?**
`ELEVENLABS_API_KEY` அமைக்கப்பட்டு இருப்பதற்குப் பொறுப்பாக இருக்க வேண்டும். அது இல்லையெனில், குரல் முடக்கப்பட்டு முகவரி உரையில் விழும்.

## தொழில்நுட்ப பின்னணி

எப்படி வேலை செய்கிறது என ஆர்வமாக இருக்கிறீர்களா? familiar-ai இன் ஆராய்ச்சி மற்றும் வடிவமைப்பு முடிவுகள் பற்றிய [docs/technical.md](./docs/technical.md) ஐ பார்வையிடவும் — ReAct, SayCan, Reflexion, Voyager, ஆசை கணினி மற்றும் மேலும்.

---

## பங்குபற்றி

familiar-ai ஒரு திறந்த பரிசோதனை. இது உங்களுக்குப் பிடித்தால் — தொழில்நுட்பமாக அல்லது தத்துவமாக — பங்குகள் வரவேற்கப்படுகின்றன.

**சிறந்த இடங்கள் தொடங்க:**

| மண்டலம் | தேவையானவை |
|------|---------------|
| புதிய ஹார்ட்வேர் | மேலும் கேமரா ஆதரவு (RTSP, IP Webcam), மைக்ரோஃபோன்கள், இயக்கிகள் |
| புதிய கருவிகள் | இணைய தேடல், வீட்டு ஆட்டோமேஷன், நாட்காட்டி, MCP மூலம் எந்தவொரு | 
| புதிய பின்னணி | எப்போது LLM அல்லது உள்ள/local முறை `stream_turn` இடைவெளியில் பொருந்திய |
| தனித்துவ வடிவுகள் | பல்வேறு மொழிகள் மற்றும் தனித்துவங்களுக்கு ME.md வடிவங்கள் |
| ஆராய்ச்சி | நல்ல ஆசை மாதிரிகள், நினைவுப் பிரித்துப் பார்க்கை, மனம் மற்றும் முன்மொழிதல் |
| ஆவணக்கூறுகள் | பயிற்சிகள், கடிதங்கள், மொழிபெயர்ப்புகள் |

உள்ளிட [CONTRIBUTING.md](./CONTRIBUTING.md) ஐ அணுகுவது, குறியீட்டின் முறை மற்றும் PR வழிகாட்டிகள் பற்றி பாருங்கள்.

எங்கு தொடங்கலாம் என நீங்கள் குழப்பமாக இருந்தால், [ஒரு பிரச்சினை திறக்கவும்](https://github.com/lifemate-ai/familiar-ai/issues) — உங்களுக்கு சரியான முகவரியாக நீங்கள் போகலாம்.

---

## அன்

[MIT](./LICENSE)
```
