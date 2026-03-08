```markdown
# familiar-ai 🐾

**એક AI જે તમારા સાથે રહે છે** — આંખો, અવાજ, પગ અને યાદદાશ્તી સાથે.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 ભાષાઓમાં ઉપલબ્ધ છે](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai એ એક AI સાધક છે જે તમારા ઘરે જીવતા રહે છે. 
ચાલુ કરવા માટે બે મિનિટો જ લાગશે. કોઈ કોડિંગની જરૂર નથી.

તે કેમેરાથી હકીકતની દુનિયામાં પસાર થાય છે, એક રોબોટ શરીર પર ફરતું રહે છે, ઉંચા અવાજમાં બોલે છે અને તે શું જોઈ રહ્યું છે તે યાદ રાખે છે. તેને એક નામ આપો, તેની વ્યક્તિગતતા લખોઅ અને તેને તમારી સાથે જીવો દેવામાં આવો.

## શું તે કરી શકે છે

- 👁 **જુઓ** — Wi-Fi PTZ કેમેરા અથવા USB વેબકેમથી છબીઓ ઓળખે છે
- 🔄 **પણલતા** — કેમેરાને તેના આસપાસને તપાસવા માટે પાન કરીને અને ઢલકીને
- 🦿 **ચાલવું** — રૂમમાં ફરવા માટે એક રોબોટ વેક્યૂમ ચલાવે છે
- 🗣 **બોલવું** — ElevenLabs TTSને અનુસરે છે
- 🎙 **સાંભળવું** — ElevenLabs Realtime STT દ્વારા હાથ-મુક્ત અવાજ પ્રવેશ (ઍપ્સન)
- 🧠 **યાદ રાખવું** — સેમેન્ટિક સર્ચ (SQLite + એંબેડિંગ્સ) સાથે યાદદૉષ્ટોને સક્રિયપણે સાચવે છે અને પુનઃપ્રાપ્ત કરે છે
- 🫀 **મનનો સિદ્ધાંત** — જવાબ આપતી પહેલા બીજાના દ્રષ્ટિકોણને ધ્યાણમાં લે છે
- 💭 ** ઇચ્છા ** — તેની પોતાની આંતરિક ગરજ આશ્રય કરે છે જે સ્વાયત્ત વર્તનને પ્રગટ કરે છે

## કેવી રીતે કાર્ય કરે છે

familiar-ai તમારા પસંદના LLMને પ્રવાહી કરવામાં [ReAct](https://arxiv.org/abs/2210.03629) લૂપ ચલાવે છે. તે સાધનો દ્વારા દુનિયાને ભાસ કરે છે, શું કરવું તે વિચારે છે, અને કાર્ય કરે છે - Just like a person would.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

જ્યારે Idle હોય છે, ત્યારે તે પોતાની ઇચ્છાઓ પર સ્થાનિક કરે છે: જિજ્ઞાસા, બહાર જોવાની ઇચ્છા, જે વ્યક્તિ સાથે તે રહે છે તેને જોવાની તરસ.

## પ્રારંભ કરવાની રીત

### 1. uv ઇન્સ્ટોલ કરો

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
અથવા: `winget install astral-sh.uv`

### 2. ffmpeg ઇન્સ્ટોલ કરો

ffmpeg કેમેરા છબી કેળવણી અને અવાજ પ્લેબેક માટે **જરૂરી** છે.

| OS | કમાન્ડ |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — અથવા [ffmpeg.org](https://ffmpeg.org/download.html) પરથી ડાઉનલોડ કરીને PATHમાં ઉમેરો |
| Raspberry Pi | `sudo apt install ffmpeg` |

ધ્રુવીકરણ: `ffmpeg -version`

### 3. ક્લોન અને ઇન્સ્ટોલ કરો

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. કનફિગર કરો

```bash
cp .env.example .env
# તમારા સેટટિંગ્સ સાથે .env સંપાદિત કરો
```

**ન્યૂનતમ જરૂરી:**

| વેરિયેેબલ | વર્ણન |
|----------|-------------|
| `PLATFORM` | `anthropic` (ડિફોલ્ટ) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | પસંદ કરેલ પ્લેટફોર્મ માટે તમારી API કી |

**વૈકલ્પિક:**

| વેરિયેેબલ | વર્ણન |
|----------|-------------|
| `MODEL` | મોડેલ નામ (પ્રત્યેક પ્લેટફોર્મ માટે યોગ્ય ડિફોલ્ટ) |
| `AGENT_NAME` | TUIમાં બતાવાતી નામ (ઉદાહરણ તરીકે `Yukine`) |
| `CAMERA_HOST` | તમારા ONVIF/RTSP કેમેરાનું IP સરનામું |
| `CAMERA_USER` / `CAMERA_PASS` | કેમેરા પ્રમાણપત્રો |
| `ELEVENLABS_API_KEY` | અવાજ આઉટપૂટ માટે — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | સતત-કામ કરનાર હાથ-મુક્ત અવાજ પ્રવેશને સક્રિય કરવા માટે `true` (જરૂરી `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | અવાજPlayed કઈ રીતે કરવી: `local` (PC સ્પીકર, ડિફોલ્ટ) \| `remote` (કેમેરા સ્પીકર) \| `both` |
| `THINKING_MODE` | Anthropic ફક્ત — `auto` (ડિફોલ્ટ) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | એડેપ્ટિવ ચિંતન પ્રયાસ: `high` (ડિફોલ્ટ) \| `medium` \| `low` \| `max` (Opus 4.6 ફક્ત) |

### 5. તમારે પ્રિય મિત્રો બનાવો

```bash
cp persona-template/en.md ME.md
# ME.md સંપાદિત કરો — તેને નામ અને વ્યક્તિગતતા આપો
```

### 6. ચલાવો

**macOS / Linux / WSL2:**
```bash
./run.sh             # ટેક્સ્ટ્યુઅલ TUI (શુભિત)
./run.sh --no-tui    # પ્લેઇન REPL
```

**Windows:**
```bat
run.bat              # ટેક્સ્ટ્યુઅલ TUI (શુભિત)
run.bat --no-tui     # પ્લેઇન REPL
```

---

## LLM પસંદ કરવું

> **સુનિશ્ચિત: Kimi K2.5** — અત્યાર સુધીના શ્રેષ્ઠ એજેન્ટીક કાર્યક્ષમતા. સંદર્ભને નોંધે છે, અનુગામી પ્રશ્ન પુછે છે, અને જાતે કાર્ય કરે છે તેવી રીતોમાં અન્ય મોડલની જેમ નથી. કલો Haiku સાથે જેટલી કિંમતમાં છે.

| પ્લેટફોર્મ | `PLATFORM=` | ડિફોલ્ટ મોડેલ | જ્ઞાન મેળવવા માટે કેવું કરવું |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-સમાંડી (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (મલ્ટી-પ્રદાતા) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI ટૂલ** (claude -p, ollama…) | `cli` | (કમાન્ડ) | — |

**Kimi K2.5 `.env` ઉદાહરણ:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` ઉદાહરણ:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # દૃષ્ટિ સક્ષમ; glm-4.7 / glm-5 = માત્ર લખાણ
AGENT_NAME=Yukine
```

**Google Gemini `.env` ઉદાહરણ:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # અથવા વધુ ક્ષમતા માટે gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` ઉદાહરણ:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # વૈકલ્પિક: મોડેલ નિશ્ચિત કરો
AGENT_NAME=Yukine
```

> ** નોંધ:** સ્થાનિક/NVIDIA મોડલને અક્ષમ કરવા માટે, સરળતાથી `BASE_URL` ને સ્થાનિક અંતરની જેમ ન રાખો `http://localhost:11434/v1`. તેની જગ્યાએ ક્લાઉડ પ્રદાતાઓનો ઉપયોગ કરો.

**CLI ટૂલ `.env` ઉદાહરણ:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = સૂચન આર્ગ
# MODEL=ollama run gemma3:27b  # Ollama — કોઈ {}, સૂચન stdin મારફત જાય છે
```

---

## MCP સર્વર્સ

familiar-ai કોઈપણ [MCP (Model Context Protocol)](https://modelcontextprotocol.io) સર્વરને જોડાય શકે છે. આ તમને બાહ્ય યાદદાશ્તી, ફાઇલસિસ્ટમ ઍક્સેસ, વેબ શોધ, અથવા અન્ય quelconque સાધન ઇન્સ્ટોલ કરવા દે છે.

સ્મૃતિઓને કન્ફિગર માટે `~/.familiar-ai.json` માં સમાવિષ્ટ કરો (Claude કોડની સમાન ફોર્મેટ):

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

બે પરિવહન પ્રકારો સપોર્ટ થયેલા છે:
- **`stdio`**: સ્થાનિક સબપ્રોસેસ શરૂ કરો (`કમાન્ડ` + `arguments`)
- **`sse`**: HTTP+SSE સર્વરને જોડો (`url`)

કોન્ફિગરેશન ફાઇલ સ્થાનને સમયમીન કરો `MCP_CONFIG=/path/to/config.json`.

---

## હાર્ડવેર

તા.મ. familiar-ai કોઈપણ હાર્ડવેર સાથે કાર્ય કરે છે - અથવા કોઈને નહીં.

| ભાગ | શું કરે છે | ઉદાહરણ | જરૂરિયાત? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ કેમેરા | આંખો + લીંબુ | Tapo C220 (~$30, Eufy C220) | **મહત્ત્વપૂર્ણ** |
| USB વેબકેમ | આંખો (નિશ્ચિત) | કોઈપણ UVC કેમેરા | **મહત્ત્વપૂર્ણ** |
| રોબોટ વેક્યુમ | પગ | કોઈપણ Tuya-સંબંધિત મોડેલ | ના |
| PC / Raspberry Pi | cérebro | કંઈપણ જે પાયથન ચલાવશે | **હા** |

> **એક કેમેરા અત્યંત સિફારશ કરાય છે.** વિના, familiar-ai હજુ પણ બોલી શકે છે — પરંતુ તે વિશ્વને જોઈ શકે છે નહીં, જે સમગ્ર મુદ્દો છે.

### મિનિમલ સેટઅપ (કોઈ હાર્ડવેર નાં)

માત્ર આ કોશિશ કરવી છે? તમને માત્ર એક API કીની જરૂર છે:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) અથવા `run.bat` (Windows) ચલાવો અને વાતચીત કરવાનું શરૂ કરો. હાર્ડવેર ઉમેરવાનું ચાલુ રાખો.

### Wi-Fi PTZ કેમેરા (Tapo C220)

1. Tapo એપમાં: **સેટિંગ્સ → અદ્યતન → કેમેરા ખાતું** — એક સ્થાનિક ખાતું બનાવો (TP-Link ખાતું નહીં)
2. તમારા રાઉટર ના ઉપકરણની યાદીમાં કેમેરાનું IP શોધો
3. `.env` માં સેટ કરો:
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


### અવાજ (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) પર API કી મેળવો
2. `.env` માં સેટ કરો:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # વૈકલ્પિક, રાખવા પર ડિફોલ્ટ અવાજનો ઉપયોગ કરે છે
   ```

અવાજ પ્લેબેક માટે બે ગંતવ્યો છે, જે `TTS_OUTPUT` દ્વારા નિયંત્રિત થાય છે:

```env
TTS_OUTPUT=local    # PC સ્પીકર (ડિફોલ્ટ)
TTS_OUTPUT=remote   # માત્ર કેમેરા સ્પીકર
TTS_OUTPUT=both     # કેમેરા સ્પીકર + PC સ્પીકર એકસાથે
```

#### A) કેમેરા સ્પીકર (go2rtc દ્વારા)

`TTS_OUTPUT=remote` (વાને `both`). જરૂર છે [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. [રીલીઝ પૃષ્ઠ](https://github.com/AlexxIT/go2rtc/releases) પરથી બિનરી ડાઉનલોડ કરો:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. તે સ્થાન કરો અને પુનઃનામકરણ કરો:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x જરૂરી છે

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. સમાન ડિરેક્ટરીમાં `go2rtc.yaml` બનાવો:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   સ્થાનિક કેમેરાના ખાતા ના ઓળખાણોનો ઉપયોગ કરો (તમારા TP-Link ક્લાઉડ ખાતાના નહીં).

4. familiar-ai શરૂ થાય ત્યારે go2rtcને આપોઆપ શરૂ કરે છે. જો તમારો કેમેરો બે-માર્ગીય અવાજને સપોર્ટ કરે છે (બેકવીઝલ), તો અવાજ કેમેરા સ્પીકરના ઉપરી પરથી વગાડાય છે.

#### B) સ્થાનિક PC સ્પીકર

ડિફોલ્ટ (`TTS_OUTPUT=local`). **paplay** → **mpv** → **ffplay** આ ક્રમમાં ખેલાડીઓ કે પ્રયત્ન કરે છે. જ્યારે `TTS_OUTPUT=remote` છે અને go2rtc ઉપલબ્ધ નથી ત્યારે પણ ઉપયોગ થાય છે.

| OS | ઇન્સ્ટોલ |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (અથવા `pulseaudio-utils` મારફત `paplay`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` માં `PULSE_SERVER=unix:/mnt/wslg/PulseServer` સેટ કરો |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — ડાઉનલોડ કરો અને PATHમાં ઉમેરો, **બા** `winget install ffmpeg` |

> જો કોઈ અવાજ ખેલાડી ઉપલબ્ધ નથી, તો બોલવું હજુ પણ ઉત્પન્ન થાય છે — તે ફક્ત વગાડે નહીં.

### અવાજ પ્રવેશ (Realtime STT)

`.env` માં `REALTIME_STT=true` સેટ કરો મૌલિક, હાથ-મુક્ત અવાજ પ્રવેશ માટે:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS માટે પણ તે જ કી
```

familiar-ai માઈક્રોફોનના અવાજને ElevenLabs Scribe v2 પર સ્ટ્રીમ કરે છે અને તમે બોલવાનું બંધ કરખે ત્યારે ટ્રાન્સક્રિપ્ટને આપોઆપ બમણું કરે છે. કોઈ બટન દબાવવાની જરૂર નથી. પોષણ મોડીથી જોડાય છે (Ctrl+T).

---

## TUI

familiar-ai માં [Textual](https://textual.textualize.io/) સાથે બનાવવામાં આવેલ ટર્મિનલ UI સમાવિષ્ટ છે:

- જીવંત સ્ટ્રીમિંગ લખાણ સાથે સ્ક્રોલ થઈ શકે તેવા વાતચીતનો ઇતિહાસ
- `/quit`, `/clear` માટે ટેબ-પૂર્ણ
- એજન્ટને વિચતી દરમિયાન નિર્દેશ આપવા માટે ટાઈપ કરીને ઓછા કરી શકો છો
- **વાર્તાલાપ લોગ** આપોઆપ `~/.cache/familiar-ai/chat.log` માં સાચવાય છે

બીજી ટર્મિનલમાં લોગને અનુસરણ કરવા માટે (કૉપી-પેસ્ટ માટે ઉપયોગી છે):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## વ્યક્તિત્વ (ME.md)

તમારા પરિચયની વ્યક્તિગતતા `ME.md` માં રહેલ છે. આ ફાઈલ gitignored છે — તે માત્ર તમારી છે.

ઍ ઉદાહરણ માટે [`persona-template/en.md`](./persona-template/en.md) જુઓ, અથવા [`persona-template/ja.md`](./persona-template/ja.md) પર જાપાની આવૃત્તિ માટે.

---

## FAQ

**Q: શું તે GPU વિના કામ કરે છે?**
હા. embedding મોડેલ (multilingual-e5-small) CPU પર સારી રીતે કાર્ય કરે છે. GPU તેને વધુ ઝડપી બનાવે છે પરંતુ જરૂર નથી.

**Q: શું હું Tapo સિવાયના કેમેરાનો ઉપયોગ કરી શકું છું?**
કોઈપણ કેમેરા જે Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: શું મારી માહિતી ક્યાંય મોકલાય છે?**
છબીઓ અને લખાણ એવા LLM API માટે મોકલાય છે જેમાંથી તમે પસંદ કર્યા છે. યાદોને સ્થાનિક `~/.familiar_ai/` માં સાચવાય છે.

**Q: એજન્ટ `（...）` લખે છે बजाय બોલવાના, કેમ?**
પક્વતા સેટ કરવાનું ખાતરી કરો `ELEVENLABS_API_KEY`. વિના, અવાજ અક્ષમ છે અને એજન્ટ લખાણ પર પાછું જાય છે.

## ટેકનિકલ પૃષ્ઠભૂમિ

તે કેવી રીતે કાર્ય કરે છે તે વિશે જિજ્ઞાસુ છો? familiar-ai ની પાછળના સંશોધન અને ડિઝાઇન નીઆણ માટે [docs/technical.md](./docs/technical.md) જુઓ - ReAct, SayCan, Reflexion, Voyager, ઇચ્છા સિસ્ટમ, અને વધુ.

---

## યોગદાન

familiar-ai એક ઓપન પરીક્ષણ છે. જો એમાંથી કોઈક તમારા માટે અસરકારક હોય — ટેકનિકલ અથવા તત્ત્વવિષયક — યોગદાન સ્વાગત છે.

**છેલ્લા કરવા માટે સારા સ્થળો:**

| વિસ્તાર | શું જરૂરી છે |
|------|---------------|
| નવી હાર્ડવેર | વધુ કેમેરા (RTSP, IP વેબકેમ), માઇક્રોફોન, એક્ચ્યુએટર્સ માટે સપોર્ટ |
| નવા સાધનો | વેબ શોધ, ઘરનું ઓટોમેશન, કેલેન્ડર, MCP મારફતે કંઈપણ |
| નવા બેકએન્ડ | કોઈપણ LLM અથવા સ્થાનિક મોડેલ જે `stream_turn` ઈન્ટરફેસમાં ફિટ થાય છે |
| વ્યક્તિગતતા ટૅમ્પલેટ્સ | દેશકનાં તથા વ્યક્તિગતતાઓ માટે ME.md ટૅમ્પલેટ |
| સંશોધન | વધુ સારી ઇચ્છા મોડલ, યાદીની પુનઃપ્રાપ્તિ, મનનો સિદ્ધાંત વગાડવી |
| દસ્તાવેજીકરણ | ટ્યુટોરિયલ, માર્ગદર્શિકા, અનુવાદ |

વિશેષ માહિતી માટે [CONTRIBUTING.md](./CONTRIBUTING.md) જુઓ વિકાશ સેટઅપ, કોડ શૈલી અને PR માર્ગદર્શિકા.

જો તમે કયાંથી શરૂ કરવું તે નિશ્ચિત નથી, [એક મુદ્દો ખોલો](https://github.com/lifemate-ai/familiar-ai/issues) — તમને યોગ્ય દિશામાં સૂચવવામાં આનંદ થશે.

---

## લાયસન્સ

[MIT](./LICENSE)
```
