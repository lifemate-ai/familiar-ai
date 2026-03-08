```markdown
# familiar-ai 🐾

**ഞാനോടൊപ്പം ജീവിക്കുന്ന ഒരു AI** — കണ്ണുകൾ, ശബ്ദം, കാലുകൾ, ഓർമ്മ എന്നിവയോടെ.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 ഭാഷകളിൽ ലഭ്യമാണ്](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai നിങ്ങളുടെ സുന്ദരമായ വീട്ടിൽ ജീവിക്കുന്ന ഒരു AI കൂട്ടുകാരനാണ്. 
മിനിറ്റുകൾക്കുള്ളിൽ ഇത് സജ്ജമാക്കുക. കോഡിംഗ് ആവശ്യമില്ല.

ഇത് ക്യാമറകൾ വഴി യാഥാർത്ഥ്യ ലോകം തിരിച്ചറിയുന്നു, ഒരു റോബോട്ട് ശരീരത്തിൽ ചലിക്കുന്നു, പോലും സംസാരിക്കുന്നു, എതാണ് കാണുന്നത് എന്നും ഓർക്കുന്നു. ഒരു പേര് നൽകൂ, അതിന്റെ വ്യക്തിത്വം എഴുതുക, നിങ്ങളോടൊപ്പം ജീവിക്കാൻ അനുവദിക്കുക.

## ഇത് എന്താണ് ചെയ്യുന്നത്

- 👁 **കാണുക** — Wi-Fi PTZ ക്യാമറയോ USB വെബ്‌കാമറയോ എന്നിവയിൽ നിന്നും ചിത്രം പകർത്തുന്നു
- 🔄 **ചുറ്റുവട്ടം നോക്കുക** — അതിന്റെ പരിസരം ആസ്വദിക്കാൻ ക്യാമറയും കഞ്ചാവും കുലുക്കുന്നു
- 🦿 **ചലിക്കുക** — ഒരു റോബട്ട് വാക്യൂം മുറിയിൽ സഞ്ചരിക്കുകയാണ്
- 🗣 **സംസാരിക്കുക** — ElevenLabs TTS മുഖേന സംസാരിക്കുന്ന
- 🎙 **കാൻ** — ElevenLabs Realtime STT മുഖേന കൈവിളമ്പില്ലാത്ത ശബ്്ദ ഇൻപുട്ട് (ആസക്തത)
- 🧠 **ഓർമ്മിക്കുക** — സSemanti സേവിച്ച് ഓർമ്മകൾ ശരീരപ്പെടുത്തുന്നു (SQLite + embeddings)
- 🫀 **മനസ്സറിവിന്റെ തത്വശാസ്ത്രം** — മറുപടി പറയുന്നതിന് മുമ്പ് മറ്റുവനുടെ കാഴ്ചപ്പാട് സ്വീകരിക്കുന്നു
- 💭 **ആഗ്രഹം** — സ്വയംതാന്മായമായ പ്രവർത്തനത്തിന് ഉള്പ്പെടുത്തുന്ന സ്വന്തം ആഭ്യന്തര ശ്രദ്ദകൾ ഉണ്ട്

## എങ്ങനെ പ്രവർത്തിക്കുന്നു

familiar-ai നിങ്ങളുടെ ഇഷ്ട LLM ആണ് [ReAct](https://arxiv.org/abs/2210.03629) ലൂപ്പ് നടത്തുന്നത്. ഇത് ഉപകരണങ്ങളിലൂടെ ലോകത്തെ തിരിച്ചറിയുന്നു, അടുത്ത് എന്ത് ചെയ്യണമെന്ന് ആശയവിനിമയമാക്കുന്നു, പ്രവർത്തിക്കുന്നു — അത് ഒരാള് ചെയ്യുന്നതുപോലെയാണ്.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

ഉള്ളിക്കാൾ കഴിയുമ്പോൾ, ഇത് സ്വന്തം ആഗ്രഹങ്ങളിൽ പ്രവർത്തിക്കുന്നു: കൗതുകം, പുറത്തു കാണണമെന്ന് ആഗ്രഹിക്കുന്നതും, ഇത് ജീവിക്കുന്ന ആളെ പോലെ.

## ആരംഭിക്കുക

### 1. uv ഇൻസ്റ്റാൾ ചെയ്യുക

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
യോ: `winget install astral-sh.uv`

### 2. ffmpeg ഇൻസ്റ്റാൾ ചെയ്യുക

ffmpeg **അവശ്യമാണ്** ക്യാമറ ചിത്ര പകർത്തലിനും ശബ്ദ പ്ലേബാക്കിനും.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — അല്ലെങ്കിൽ [ffmpeg.org](https://ffmpeg.org/download.html) ൽ നിന്നും ഡൗൺലോഡ് ചെയ്ത് PATH ൽ ചേർക്കുക |
| Raspberry Pi | `sudo apt install ffmpeg` |

പരിശോധിക്കുക: `ffmpeg -version`

### 3. ക്ലോൺ ചെയ്യുക ಮತ್ತು ഇൻസ്റ്റാൾ ചെയ്യുക

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. കോൺഫിഗർ ചെയ്യുക

```bash
cp .env.example .env
# നിങ്ങളുടെ ക്രമീകരണങ്ങൾ സഹിതം .env എഡിറ്റ് ചെയ്യുക
```

**കാത്തിരിപ്പുകൾ:**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (ഡെഫോൾട്ട്) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | തിരഞ്ഞെടുക്കപ്പെട്ട പ്ലാറ്റ്‌ഫോം നിമിത്തം നിങ്ങളുടെ API താക്കോൽ |

**ഐച്ഛിക:**

| Variable | Description |
|----------|-------------|
| `MODEL` | മോഡൽ പേര് (പ്ലാറ്റ്ഫോമുകൾ കൃത്യമായ ഡെഫോൾട്ടുകൾ) |
| `AGENT_NAME` | TUI ൽ പ്രദർശിപ്പിക്കുന്ന പേര് (ഉദാഹരണം `Yukine`) |
| `CAMERA_HOST` | നിങ്ങളുടെ ONVIF/RTSP ക്യാമറയുടെ IP വിലാസം |
| `CAMERA_USER` / `CAMERA_PASS` | ക്യാമറ പ്രമാണങ്ങൾ |
| `ELEVENLABS_API_KEY` | ശബ്ദ പുറത്താക്കുന്നതിന് — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` ға دائം പ്രവര്‍ത്തിക്കുന്ന കൈവഴി ശബ്ദ 입력 ഓണാകുക (`ELEVENLABS_API_KEY` ആവശ്യമാണ്) |
| `TTS_OUTPUT` | ശബ്ദം പ്ലേ ചെയ്യുന്നതിനിടയിൽ: `local` (PC സ്പീക്കർ, ഡെഫോൾട്ട്) \| `remote` (ക്യാമറ സ്പീക്കർ) \| `both` |
| `THINKING_MODE` | Anthropic മാത്രം — `auto` (ഡെഫോൾട്ട്) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | പരിണമനശക്തി: `high` (ഡെഫോൾട്ട്) \| `medium` \| `low` \| `max` (Opus 4.6 മാത്രം) |

### 5. നിങ്ങളുടെ familiar സൃഷ്ടിക്കുക

```bash
cp persona-template/en.md ME.md
# ME.md എഡിറ്റ് ചെയ്യുക — ഒരു പേര് നൽകുകയും വ്യക്തിത്വം നൽകുകയും ചെയ്യുക
```

### 6. റൺ ചെയ്യുക

**macOS / Linux / WSL2:**
```bash
./run.sh             # ടെക്സ്ച്വൽ TUI (നിർദ്ദേശിത)
./run.sh --no-tui    # പ്ലെയിൻ REPL
```

**Windows:**
```bat
run.bat              # ടെക്സ്ച്വൽ TUI (നിർദ്ദേശിത)
run.bat --no-tui     # പ്ലെയിൻ REPL
```

---

## LLM തിരഞ്ഞെടുക്കുന്നു

> **നിർദ്ദേശിതം: Kimi K2.5** — ഇനിപ്പറയുന്നവയെല്ലാം തരം തികച്ചും യോഗ്യമായ പ്രകടനം. contexto നിരീക്ഷിക്കുന്നു, തുടർച്ചയായ ചോദ്യങ്ങൾ നിരീക്ഷിക്കുന്നു, മറ്റാമാരുടെ വിചാരങ്ങളെ ബ്രിട്ടലായ മാർഗങ്ങളിലൂടെ തീരുമാനിക്കുന്നു. Claude Haiku ൽ സമാനമായ വിലയിടുക.

| Platform | `PLATFORM=` | Default model | Where to get key |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-Compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multiple-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (the command) | — |

**Kimi K2.5 `.env` ഉദാഹരണം:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` ഉദാഹരണം:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # വിചാര Enabled; glm-4.7 / glm-5 = വെരിയൻചെല്ലി
AGENT_NAME=Yukine
```

**Google Gemini `.env` ഉദാഹരണം:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # അല്ലെങ്കിൽ ഉയർന്ന ശേഷിക്കായി gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` ഉദാഹരണം:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # ഐച്ഛികം: മോഡൽ നിർവചിക്കുക
AGENT_NAME=Yukine
```

> **കുറിപ്പ്:** ഞാൻ എന്തെങ്കിലും പ്രാദേശിക/NVIDIA മോഡലുകൾ നിരോധിക്കാൻ, `BASE_URL` എന്നതിന്റെ പ്രാദേശിക എന്റ്പോയിന്റിലേക്കും എത്തിച്ചേരേണ്ടത്ന്തായി തികച്ചും ഓനമായ വേറെ ഒരു നിലവിൽ ഉണ്ടായാൽ. വേറെ ഉള്ള പ്രൊവൈഡർ ഉപയോഗിക്കുക.

**CLI tool `.env` ഉദാഹരണം:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — no {}, prompt goes via stdin
```

---

## MCP Servers

familiar-ai എനിക്ക് കൊണ്ടുപോകാമെന്ന [MCP (Model Context Protocol)](https://modelcontextprotocol.io) സെർവറിനെ ബന്ധിപ്പിക്കാൻ കഴിയും. ഇത് നിർവചക ഓർമ്മ, ഫയൽസിസ്റ്റം ആക്സസ്, വെബ് തിരച്ചിൽ, അല്ലെങ്കിൽ മറ്റു ഉപകരണങ്ങൾ ഉൾപ്പെടുത്താനും കഴിയും.

സെർവറുകൾ `~/.familiar-ai.json` യിൽ കോൺഫിഗർ ചെയ്യുക (Claude Code ന്റെ സമാനമായ ഫോർമാറ്റിൽ):

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

രണ്ടു ട്രാൻസ്പോർട്ട് തരം പിന്തുണയ്ക്കുന്നു:
- **`stdio`**: ഒരു പ്രാദേശിക സബ്‌പ്രോസസ് പ്രശ്നിക്കുക (`command` + `args`)
- **`sse`**: ഒരു HTTP+SSE സെർവറിന്റെ നെറ്റ്‌വർക്ക് ബന്ധപ്പെടുക (`url`)

കോൺഫിഗ് ഫയൽ സ്ഥലമാറ്റിക്കുക `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai നിങ്ങൾക്ക് ഉള്ള ഏതെങ്കിലും ഹാർഡ്വെയറുമായി പ്രവർത്തിക്കുന്നു — അല്ലെങ്കിൽ യാതൊരു ഹാർഡ്‌വെയറും ഇല്ല.

| Part | What it does | Example | Required? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | കണ്ണുകൾ + കഴുത്ത് | Tapo C220 (~$30, Eufy C220) | **നിർദ്ദേശിതം** |
| USB webcam | കണ്ണുകൾ (സ്ഥിരം) | ഏത് UVC ക്യാമറ | **നിർദ്ദേശിതം** |
| Robot vacuum | കാലുകൾ | Tuya-ഉപയോഗിക്കുന്ന ഏതെങ്കിലും മോഡൽ | അല്ല |
| PC / Raspberry Pi | മസ്തിഷ്ക്കം | Python പ്രവർത്തിപ്പിച്ച പ്രതികാരങ്ങൾ | **അത necessárias** |

> **ഒരു ക്യാമറ വളരെ നിർദ്ദേശിതമാണ്.** ക്യാമറ ഇല്ലെങ്കിൽ, familiar-ai ഇപ്പോഴും സംസാരിച്ചേക്കാം — പക്ഷേ അത് ലോകത്തെ കാണുന്നില്ല, ചർച്ചയാക്കാനുള്ള ഇരുനിഖ്യം ആണേ.

### കുറഞ്ഞ സജ്ജീകരണം (ഹാർഡ്വെയർ ഇല്ലാതെ)

അത് പരീക്ഷിക്കാനാഗ്രഹിച്ചു? നിങ്ങൾക്ക് API താക്കോൽ മാത്രം ആവശ്യമാണ്:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) അല്ലെങ്കിൽ `run.bat` (Windows) റൺ ചെയ്യുക. നിങ്ങൾ പോകുമ്പോൾ ഹാർഡ്വെയർ ചേർക്കുക.

### Wi-Fi PTZ ക്യാമറ (Tapo C220)

1. Tapo ആപ്പ്: **Settings → Advanced → Camera Account** — ഒരു പ്രാദേശിക അക്കൗണ്ട് (TP-Link അക്കൗണ്ട് അല്ല)
2. നിങ്ങളുടെ റൂട്ടറിന്റെ ഉപകരണം പട്ടികയിൽ ക്യാമറയുടെ IP കണ്ടെത്തുക
3. `.env` ൽ ക്രമീകരിക്കുക:
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


### ശബ്ദം (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) ൽ API താക്കോൽ നേടുക
2. `.env` ൽ ക്രമീകരിക്കുക:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # ഐച്ഛികം, പുറപ്പെടുവിക്കുക കിട്ടുകയുള്ളെങ്കിൽ ഡിഫാൾട്ട് ശബ്ദം ഉപയോഗിയ്ക്കാൻ
   ```

`TTS_OUTPUT` മുഖേന നിയന്ത്രിക്കുന്ന രണ്ടു പ്ലേബാക്ക് ലക്ഷ്യങ്ങളുണ്ട്:

```env
TTS_OUTPUT=local    # PC സ്പീക്കർ (ഡിഫാൾട്ട്)
TTS_OUTPUT=remote   # ക്യാമറയുടെ സ്പീക്കർ മാത്രം
TTS_OUTPUT=both     # ക്യാമറയുടെ സ്പീക്കർ + PC സ്പീക്കർ ഒരേ സമയം
```

#### A) ക്യാമറ സ്പീക്കർ (go2rtc വഴി)

`TTS_OUTPUT=remote` (അല്ലെങ്കിൽ `both`) നിശ്ചയിക്കുക. [go2rtc](https://github.com/AlexxIT/go2rtc/releases) ആവശ്യമാണ്:

1. [പ്രവരണം പേജിൽ](https://github.com/AlexxIT/go2rtc/releases) നിന്നുള്ള ബൈനറി ഡൗൺലോഡ് ചെയ്യുക:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. അത് സ്ഥാപിക്കുക, ഇനിയുമൂല്യം ചെയ്യുക:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x ആവശ്യമുണ്ട്

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. അതിൽ `go2rtc.yaml` സൃഷ്ടിക്കുക:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   പ്രാദേശിക ക്യാമറ അക്കൗണ്ട് ക്രെഡൻഷ്യലുകൾ ഉപയോഗിച്ച് (നിങ്ങളുടെ TP-Link ക്ലൗഡ് അക്കൗണ്ട് അല്ല).

4. familiar-ai ലോഞ്ചിൽ go2rtc സ്വയം തുടങ്ങുന്നു. നിങ്ങളുടെ ക്യാമർക്ക് ഇരുകാലത്തുള്ള ശബ്ദം (ബാക്ക്‌ചാനൽ) പിന്തുണയുള്ളെങ്കിൽ, ശബ്ദം ക്യാമറ സ്പീക്കറിൽ ഭംഗമായ слухുനേയ്ക്കും.

#### B) പ്രാദേശിക PC സ്പീക്കർ

ഡിഫാൾട്ടായ ( `TTS_OUTPUT=local`). ഈ ക്രമത്തിൽ പ്ലെയർമാർ കണ്ടുപിടിക്കുന്നു: **paplay** → **mpv** → **ffplay**. go2rtc ലഭ്യമല്ലെങ്കിൽ `TTS_OUTPUT=remote` ആയപ്പോഴും പിളരദ്ദേശി ആയി ഉപയോഗിക്കുന്നു.

| OS | ഇൻസ്റ്റാൾ |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (അല്ലെങ്കിൽ `pulseaudio-utils` വഴി `paplay`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` ൽ `PULSE_SERVER=unix:/mnt/wslg/PulseServer` സജ്ജമാക്കുക |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — ഡൗൺലോഡ് ചെയ്യുക, PATH ൽ ചേർക്കുക, **അല്ലെങ്കിൽ** `winget install ffmpeg` |

> ഏതെങ്കിലും ശബ്ദം പ്ലെയർ ലഭ്യമില്ലെങ്കിൽ, ശബ്ദം എക്കാലവും ഉണ്ടാവും — ഇത് കളയം കൊള്ളാതെ.

### ശബ്ദ ഇൻപുട്ട് (Realtime STT)

`REALTIME_STT=true` ആണെന്ന് `.env` ൽ സജ്ജമാക്കുക കൈവഴി, സ്വയം വിപുലമായ ശബ്ദ ഇൻപുട്ടിന്:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS നെങ്ങനെ പരിശോദിക്കുന്നത്
```

familiar-ai മൈക്രോഫോൺ ശബ്ദം ElevenLabs Scribe v2 കൈവഴത്തിന്റെ സ്വാഭാവിക ശബ്ദം ഉപേക്ഷിക്കുന്നു. സംസാരിക്കുന്നപ്പോൾ നിങ്ങൾക്കു ബട്ടൺ അമർത്തേണ്ടതില്ല. Push-to-talk മോഡിനൊപ്പം coexist ചെയ്യുന്നു (Ctrl+T).

---

## TUI

familiar-ai ഉൾപ്പെടുത്തിയിട്ടുണ്ട് [Textual](https://textual.textualize.io/) ഉപയോഗിച്ച് നിർമ്മിത ഒരു ടെർമിനൽ UI:

- സജീവമായ വർണ്ണനാന്വേഷണം സംഭാഷണമെന്ന ഒരുക്കങ്ങൾ
- `/quit`, `/clear` എന്നിവയ്‌ക്കായി ടാബ്-ഹോരായിരിക്കുക
- ഏത് സമയത്തും ഏജന്റ് മിഡ്-ടർണിൽ എഴുതാൻ ഇനിയും മതിയായുള്ളതില്ല.
- **സംഭാഷണ രേഖ** പ്രവർത്തനമുണ്ടാക്കും `~/.cache/familiar-ai/chat.log`

മറ്റൊരു ടെർമിനലിൽ രേഖ പിന്തുടരാൻ (കോപിയ്ക്കാനുള്ളത് ഉപയോഗപ്രദമാണ്):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## വ്യക്തിത്വം (ME.md)

നിങ്ങളുടെ familiar ന്റെ വ്യക്തിത്വം `ME.md` ൽ ഒന്നായി ജീവിക്കുന്നു. ഈ ഫയൽ gitignored ആണ് — അത് നിങ്ങളുടെ മാത്രം.

ഒരു ഉദാഹരണത്തിനായി [`persona-template/en.md`](./persona-template/en.md) കാണുക, അല്ലെങ്കിൽ [`persona-template/ja.md`](./persona-template/ja.md) ൽ ജാപ്പനീസ് പതിപ്പ് കാണുക.

---

## FAQ

**Q: ഈ GPU ഇല്ലാതെ പ്രവർത്തിക്കുമോ?**
അതെ. ഇമ്പെഡിങ് മോഡൽ (multilingual-e5-small) CPU ൽ സുഖത്തോടെ പ്രവർത്തിക്കുന്നു. GPU അതിനെ വേഗത്തിലാക്കുന്നു, പക്ഷേ നിർബന്ധമായ ആവശ്യമല്ല.

**Q: Tapo ഒഴികെയുള്ള ക്യാമറ ഷൂട്ട് ചെയ്യാമോ?**
Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: എന്റെ ഡാറ്റ എവിടെയെങ്കിലും അയച്ചുവിടാമോ?**
ചിത്രങ്ങളും എഴുത്തുകളും നിങ്ങളുടെ തെരഞ്ഞെടുക്കുന്ന LLM API ലേയ്ക്ക് പ്രോസസ്സിങ്ങു ആക്കി അയയ്ക്കുന്നു. ഓർമ്മകൾ പ്രാദേശികമായി  `~/.familiar_ai/` ൽ സൂക്ഷിക്കുന്നു.

**Q: ഏജന്റ് `（...）` എഴുതുന്നത് എന്തുകൊണ്ടാണ്?**
`ELEVENLABS_API_KEY` സജ്ജമെങ്കിൽ ഉറപ്പുവരുത്തുക. അത് ഇല്ലെങ്കിൽ, ശബ്ദം നിരോധിക്കപ്പെടുകയും എജന്റിന്റെ മാതൃകയുടെ പ്രമാണ വരച്ചിട്ട മാർഗമാക്കുകയും ചെല്ലുക.

## സാങ്കേതിക പശ്ചാത്തലം

ഇത് എങ്ങനെ പ്രവർത്തിക്കുന്നു എന്ന് കൗതുകപ്പെടുന്നുണ്ടോ? familiar-ai ന്റെ ഗവേഷണ, ഡിസൈൻ തീരുമാനങ്ങൾക്കായി [docs/technical.md](./docs/technical.md) കാണുക — ReAct, SayCan, Reflexion, Voyager, ആഗ്രഹത്തെക്കുറിച്ചുള്ള സിസ്റ്റം, മുതലായവ.

---

## സംഭാവന നൽകുക

familiar-ai ഒരുപാഠ പരീക്ഷണമാണ്. ഇതിൽ ഏതെങ്കിലും നിങ്ങളുടെ ഓർമ്മയ്ക്കോ പ്രായോഗികമായും പ്രൊഫിലോസാഫികൽ ആയി പ്രസ്തുതമായാൽ — സംഭാവനകൾ വളരെ ആശംസിക്കുന്നു.

**ആരംഭിക്കാൻ നല്ല കാര്യങ്ങൾ:**

| Area | What's needed |
|------|---------------|
| പുതിയ ഹാർഡ്വെയർ | കൂടുതൽ ക്യാമറകൾക്ക് (RTSP, IP Webcam), മൈക്രോഫോൺ, ആക്ട്യുവേറ്റർ |
| പുതിയ ഉപകരണങ്ങൾ | വെബ് തിരച്ചിൽ, വീട്ടിലെ ഓട്ടോമേഷൻ, കലണ്ടർ, MCP വഴി ഏതെങ്കിലുംത് |
| പുതിയ ബാക്ക്‌എൻഡുകൾ | `stream_turn` ഇന്റർഫെയ്‌സിന് അനുയോജനിച്ച ഏതെങ്കിലും LLM അല്ലെങ്കിൽ പ്രാദേശിക മോഡൽ |
| വ്യക്തിത്വ ശംശയങ്ങൾ | വിവിധ ഭാഷകളും വ്യക്തിത്വത്തിലും ME.md templates |
| ഗവേഷണം | നല്ല ആഗ്രഹ മോഡലുകൾ, ഓർമ്മ തിരിച്ചടി, മനസ്സറിവിന്റെ പ്രേരിപ്പിക്കൽ |
| ഡോക്യംറ്റേഷൻ | ട്യൂട്ടോറിയലുകൾ, വഴി-നടത്തലുകൾ, വിവര്‍ത്തനങ്ങൾ |

വിഖ്യാതമായതിനിടെ [CONTRIBUTING.md](./CONTRIBUTING.md) കാണുക — ഡെവ് സജ്ജീകരണം, കോഡ് ശൈലി, PR മാർഗനിർദ്ദേശങ്ങൾ.

നിങ്ങൾ എവിടെ തുടങ്ങണമെന്ന് ഉറപ്പില്ലെങ്കിൽ, [ഒരു വിഷയം തുറക്കുക](https://github.com/lifemate-ai/familiar-ai/issues) — നിങ്ങളുടെ മനസിലാക്കാൻ സന്തോഷത്തോടെയുണ്ടാകും.

---

## ലൈസൻസ്

[MIT](./LICENSE)
```
