```markdown
# familiar-ai 🐾

**మీతో పాటు నివసించే AI** — కళ్ళు, స్వరం, కాలు, మరియు జ్ఞానం ఉన్నది.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 భాషల్లో అందుబాటులో ఉంది](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai మీ ఇంటిలో నివసించే AI టోకర.

ని కొద్ది నిమిషాల్లో సెట్ చేయండి. కోడింగ్ అవసరం లేదు.

ఎమిటి చూసేందుకు కామార్ల ద్వారా యధార్ధ ప్రపంచాన్ని గ్రహిస్తది, ఒక రోబోట్ శరీరంపై చలించద, మెట్లతో మాట్లాడుతుంది మరియు ఇది చూడగలదిన్ని గుర్తు చేస్తది. దీనికి ఒక పేరు ఇవ్వండి, దీని వ్యక్తిత్వాన్ని రాయండి, మరియు దీన్ని మీతో నివసించనికి అనుమతించండి.

## ఇది ఏమి చేయగలదు

- 👁 **చూడండి** — Wi-Fi PTZ కమెరా లేదా USB వెబ్‌కెమ్కి చిత్రాలను పరిగణిస్తుంది
- 🔄 **చుట్టూ చూడండి** — దాని పరిసరాలను అన్వేషించడానికి కమెరాను పాన్ మరియు టిల్ట్ చేస్తది
- 🦿 **ప్రయాణం చేయండి** — బాల్కెలి కక్ష్యతో గది చపలించడానికి రోబోట్ వ్యాక్యూమ్‌ను చలిస్తది
- 🗣 **మాట్లు చెప్పండి** — ElevenLabs TTS ద్వారా మాట్లాడుతుంది
- 🎙 **విని** — ElevenLabs రియల్‌టైమ్ STT ద్వారా వరకు చేయబడింది (opt-in)
- 🧠 **గుర్తు పెట్టుకోండి** — స معنాపూరిత శోధనతో జ్ఞాపకాలను సక్రియంగా నిల్వ మరియు గుర్తు చేస్తది (SQLite + అంథిమాలు)
- 🫀 **మనసు సిద్ధాంతం** — ప్రత్యర్థి వైపు తళుక్కు తీసుకుని ప్రతిస్పందించడానికి:
- 💭 **ఇష్టము** — ఆత్మీయ స్వభావానికి అనువాదంగా స్వతంత్ర ప్రవర్తనను ప్రేరేపిస్తుంది

## ఇది ఎలా పనిచేస్తది

familiar-ai మీ ఎంపిక చేసిన LLM ద్వారా శక్తివంతమైన [ReAct](https://arxiv.org/abs/2210.03629) లూప్‌ను నడుపుతుంది. ఇది ప్రయోగాలకు సాధనాలతో ప్రపంచాన్ని గ్రహిస్తుంది, తదుపరి ఏమి చేయాలో ఆలోచిస్తుంది, మరియు చర్యను చేప్తది — ఒక వ్యక్తి చేసే విధంగా.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

సేపు ఆపితే, ఇది తన స్వంత ఇష్టాలు: అవాంఛితంగా ఉంది, బాహ్యాన్ని చూడాలనుకుంటోంది, అది నివసిస్తున్న వ్యక్తిని కోల్పోతుంది.

## ప్రారంభించడం

### 1. ఉవ్ ని ఇన్స్టాల్ చేయండి

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
లేదా: `winget install astral-sh.uv`

### 2. ffmpeg ని ఇన్స్టాల్ చేయండి

ffmpeg **అవసరం** కెమరా చిత్రాలను పట్టుకునేందుకు మరియు ఆడియోను ప్లేబ్యాక్ చేయడానికి.

| OS | కమాండ్ |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — లేదా [ffmpeg.org](https://ffmpeg.org/download.html) నుంచి డౌన్లోడ్ చేసి PATHకి చేరవేయండి |
| Raspberry Pi | `sudo apt install ffmpeg` |

సत्यాపనం: `ffmpeg -version`

### 3. క్లోన్ మరియు ఇన్స్టాల్ చేయండి

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. కాన్ఫిగర్ చేయండి

```bash
cp .env.example .env
# మీ సెట్టింగ్లతో .env ని సవరించండి
```

**అవసరమైన కనిష్టం:**

| వేరియబుల్ | వివరణ |
|----------|-------------|
| `PLATFORM` | `anthropic` (డిఫాల్ట్) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | ఎంపిక చేసిన ప్లాట్‌ఫార్మ్ కోసం మీ API కీ |

**ఐచ్ఛిక:**

| వేరియబుల్ | వివరణ |
|----------|-------------|
| `MODEL` | నమూనా పేరు (ప్రతి ప్లాట్‌ఫార్మ్‌కి సున్నితమైన డిఫాల్ట్‌లు) |
| `AGENT_NAME` | TUIలో చూపించే ప్రదర్శన పేరు (ఉదా: `Yukine`) |
| `CAMERA_HOST` | మీ ONVIF/RTSP కమెరా యొక్క IP చిరునామా |
| `CAMERA_USER` / `CAMERA_PASS` | కమెరా క్రెడెన్షియల్స్ |
| `ELEVENLABS_API_KEY` | స్వరం ఉత్పత్తికి — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | ఎప్పుడూ-చాలీ చేతి-రహిత స్వరం ఇన్పుట్లను నిర్దేశించడానికి `true` (అనుమతి కోసం `ELEVENLABS_API_KEY` అవసరం) |
| `TTS_OUTPUT` | ఆడియో ప్లేయ్ చేయడానికి ఎక్కడ: `local` (PC స్పీకర్, డిఫాల్ట్) \| `remote` (కమెరా స్పీకర్) \| `both` |
| `THINKING_MODE` | Anthropic మాత్రమే — `auto` (డిఫాల్ట్) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | సాఫ్ట్ కనిష్ట ఆలోచన శక్తి: `high` (డిఫాల్ట్) \| `medium` \| `low` \| `max` (Opus 4.6 మాత్రమే) |

### 5. మీ ఫామిలియన్ ని తయారుచేయండి

```bash
cp persona-template/en.md ME.md
# ME.md ని సవరించండి — దీనికి ఒక పేరు మరియు వ్యక్తిత్వాన్ని ఇవ్వండి
```

### 6. నడిసంచు

**macOS / Linux / WSL2:**
```bash
./run.sh             # పాఠ్య TUI (ఛాయించినది)
./run.sh --no-tui    # సాధారణ REPL
```

**Windows:**
```bat
run.bat              # పాఠ్య TUI (ఛాయించినది)
run.bat --no-tui     # సాధారణ REPL
```

---

## LLMను ఎంచుకోవడం

> **ఛాయించినది: Kimi K2.5** — ఇప్పటివరకు బాగా పరీక్షించబడిన అధిక కౌశల సమర్ధత. పరిష్కారాన్ని గుర్తించి, కొనసాగింపు ప్రశ్నలు అడిగి, స్వతంత్రంగా ప్రవర్తిస్తుంది.

| ప్లాట్‌ఫారం | `PLATFORM=` | డిఫాల్ట్ నమూనా | కీను ఎక్కడ పొందాలి |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-అनుకూలం (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (బహుళ-దాత) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI టూల్** (claude -p, ollama…) | `cli` | (కమాండ్) | — |

**Kimi K2.5 `.env` ఉదాహరణ:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` ఉదాహరణ:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # దృక్పథము సంబందిత; glm-4.7 / glm-5 = కొరకు మాత్రమే
AGENT_NAME=Yukine
```

**Google Gemini `.env` ఉదాహరణ:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # లేదా అధిక సామర్ధ్యం కోసం gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` ఉదాహరణ:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # ఐచ్ఛిక: నమూనా తప్పనిసరిగా
AGENT_NAME=Yukine
```

> **గమనిక:** స్థానిక/NVIDIA నమూనాలను అబద్ధం చేయడానికి, మీరు కేవలం `BASE_URL` ని స్థానిక ఎండ్పాయింట్‌గా అమర్చకూడదు — కాంతి ఛార్తీ కంటే వాడుకరి కోసం క్లౌడ్ సేవలను వాడండి.

**CLI టూల్ `.env` ఉదాహరణ:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = ప్రాంప్ట్ ఆర్గ్
# MODEL=ollama run gemma3:27b  # Ollama — ఏ {}, ప్రాంప్ట్ stdin ద్వారా వెళ్ళదు
```

---

## MCP సర్వర్లు

familiar-ai ఎలాంటి [MCP (Model Context Protocol)](https://modelcontextprotocol.io) సర్వర్‌ను కనెక్ట్ చేయగలదు. ఇది మీరు బాహ్య జ్ఞానం, ఫైలు వ్యవస్థ యాక్సెస్, వెబ్ శోధన, లేదా ఏ ఇతర సాధనాలను ప్లగ్ చేయడం అనుమతిస్తుంది.

సర్వర్లను `~/.familiar-ai.json` లో కాన్ఫిగర్ చేయండి (Claude కోడ్ వంటినే రీతిలో):

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

రెండు నౌకాశ్రయ రకాల ఉన్నాయి:
- **`stdio`**: ఒక స్థానిక ఉప ప్రక్రియను ప్రారంభించండి (`command` + `args`)
- **`sse`**: ఒక HTTP+SSE సర్వర్‌కు కనెక్ట్ కావచ్చు (`url`)

కన్ఫిగరేషన్ ఫైలు యొక్క స్థానాన్ని `MCP_CONFIG=/path/to/config.json` తో మరింత చెయ్యండి.

---

## హార్డ్వేర్

familiar-ai మీ వద్ద ఉన్న ఏ హార్డ్వేర్‌తో పని చేస్తది — లేదంటే ఎలాంటి కాకుండా.

| భాగం | ఇది ఏమి చేస్తది | ఉదాహరణ | అవసరం? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ కమెరా | కళ్ళు + మెడ | Tapo C220 (~$30, Eufy C220) | **ఛాయించినది** |
| USB వెబ్‌కెమా | కళ్ళు (స్థిరంగా) | ఏ UVC కమెరా | **ఛాయించినది** |
| రోబోట్ వ్యాక్యూమ్ | కాల్లు | ఏ Tuya-సంబంధిత నమూనా | కాదు |
| PC / Raspberry Pi | మెదడు | పిథాన్ నడిచే ఏ స్టాఫ్ | **అవసరం** |

> **ఒక కమెరా గట్టిగా సిఫార్సు చేయబడింది.** ఒకటు లేకపోతే, familiar-ai ఇప్పటికీ మాట్లాడవచ్చు — కానీ అది ప్రపంచాన్ని చూడలేదు, ఇది మొత్తం అంశం.

### కనిష్ట సెటప్ (హార్డ్వేర్ వుండకపోతే)

తీసుకోడానికి మాత్రమే కావాలా? మీకు ఒక API కీ అవసరం మాత్రమే:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) లేదా `run.bat` (Windows) ని నడిపించండి మరియు చాటింగ్ ప్రారంభించండి. హార్డ్వేర్‌ను మీ వెతుక్కుంటే చేర్చించండి.

### Wi-Fi PTZ కమెరా (Tapo C220)

1. Tapo యాప్‌లో: **సెట్టింగ్స్ → అడ్వాన్స్డ్ → కెమెరా ఖాతా** — ఒక స్థానిక ఖాతా సృష్టించండి (TP-Link ఖాతా కాదు)
2. మీ రౌటర్ యొక్క పరికరాల జాబితాలో కమెరా యొక్క IPని కనుగొనండి
3. `.env`లో సెట్ చేయండి:
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


### స్వరం (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) లో ఒక API కీ పొందండి
2. `.env`లో సెట్ చేయండి:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # ఐచ్ఛిక, ఉదహరించిన స్వరం ఉపయోగిస్తుంది
   ```

ఇక్కడ రెండు ప్లేబ్యాక్ గమ్యాలు ఉన్నాయి, `TTS_OUTPUT` ద్వారా నియంత్రించబడ్డది:

```env
TTS_OUTPUT=local    # PC స్పీకర్ (డిఫాల్ట్)
TTS_OUTPUT=remote   # కమెరా స్పీకర్ మాత్రమే
TTS_OUTPUT=both     # కమెరా స్పీకర్ + PC స్పీకర్ ఒకేసారి
```

#### A) కమెరా స్పీకర్ (go2rtc ద్వారా)

`TTS_OUTPUT=remote` (లేదా `both`) ను సెట్ చేయండి. [go2rtc](https://github.com/AlexxIT/go2rtc/releases) అవసరం:

1. [releases page](https://github.com/AlexxIT/go2rtc/releases) నుంచి బైనరీని డౌన్లోడ్ చేయండి:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. దీనిని ఉంచి పేరు మార్చండి:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x అవసరం

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. అదే డైరెక్టరీలో `go2rtc.yaml` సృష్టించండి:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   స్థానిక కమెరా ఖాతా క్రెడెన్షియల్స్ ఉపయోగించండి (మీ TP-Link క్లౌడ్ ఖాతా కాదు).

4. familiar-ai ప్రారంభంలో ఆత్మగతంగా go2rtc‌ను ప్రారంభిస్తుంది. మీ కమెరా రెండు-విధాల ఆడియో (పునఃచలన)కి మద్దతిస్తే, స్వరం కమెరా స్పీకర్ నుండి ప్లే అవుతుంది.

#### B) స్థానిక PC స్పీకర్

డిఫాల్ట్ (`TTS_OUTPUT=local`). క్రమంలో ప్లేయర్లు అందుబాటులో ఉన్నది: **paplay** → **mpv** → **ffplay**. `TTS_OUTPUT=remote` మరియు go2rtc అందుబాటులో లేకపోతే కీగా కూడా ఉపయోగించబడింది.

| OS | ఇన్స్టాల్ |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (లేక `pulseaudio-utils` ద్వారా `paplay`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` లో `PULSE_SERVER=unix:/mnt/wslg/PulseServer` సెట్ చేయండి |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — డౌన్లోడ్ చేసి PATHకి చేరవేయండి, **లేదా** `winget install ffmpeg` |

> ఆడియో ప్లేయర్ అందుబాటులో లేకపోతే, మాటలు ఇప్పటికీ రూపొందించబడతాయి — కానీ అవి ప్లే అవుతాయి.

### స్వరం ఇన్పుట్ (రియల్‌టైమ్ STT)

స్వతంత్రంగా, చేతి-రహిత స్వరం ఇన్పుట్ కొరకు ఎప్పుడూ-ఊపిరితిత్తి, `.env` లో `REALTIME_STT=true` గా సెట్ చేయండి:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS కి అదే కీ
```

familiar-ai మైక్రోఫోన్ ఆడియోను ElevenLabs Scribe v2కు స్ట్రీమ్ చేస్తుంది మరియు మీరు మాట్లాడటం ఆపినప్పుడు ఆర్టికల్స్ ఆటో-కమిట్ చేస్తుంది. బటన్ నొక్కడం అవసరం లేదు. పుష్-టు-టాక్ మోడ్ (Ctrl+T) తో సహోద్యోగం చేయగలదు.

---

## TUI

familiar-ai [Textual](https://textual.textualize.io/) తో ఏర్పాటుచేసిన టెర్మినల్ UI ను కలిగిస్తుంది:

- ప్రసంగ తెలుగు చరిత్ర ఆక్కేసి వినారు
- `/quit`, `/clear` కు టాబ్-పూర్తి
- ఇది ఆలోచిస్తున్నప్పుడు మధ్యలో ఏ విధమైన చలనాన్ని విరమించండి
- **సమావేశ లాగ్** ఆటోసేవ్ చేయబడింది `~/.cache/familiar-ai/chat.log`

లాగ్‌ను మరో టెర్మినల్‌లో అనుసరించడానికి (కాపీ-పేస్ట్ కొరకు):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## వ్యక్తిత్వం (ME.md)

మీ ఫామిలియన్ యొక్క వ్యక్తిత్వం `ME.md` లో ఉంటుంది. ఈ ఫైల్ gitignored ఉంటుంది — ఇది మీదే తెలుస్తుంది.

ఉదాహరణ కొరకు [`persona-template/en.md`](./persona-template/en.md) చూడండి, లేదా జపనీస్ వెర్షన్ కొరకు [`persona-template/ja.md`](./persona-template/ja.md) చూడండి.

---

## FAQ

**Q: ఇది GPU లేకుండా పని చేస్తుందా?**
అవును. ఎంబెరిడింగ్ నమూనా (multilingual-e5-small) CPU పై బాగా నడుస్తుంది. GPU వేగంగా చేస్తుంది కానీ అవసరం లేదు.

**Q: Tapo కు అదనంగా ఏ కమెరాను ఉపయోగించగలనా?**
Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: నా డేటా ఎక్కడా పంపబడుతుందా?**
చిత్రాలు మరియు టెక్ట్స్ మీ ఎంపిక చేసిన LLM APIకి ప్రాసెసింగ్ కోసం పంపబడుతాయి. జ్ఞాపకాలు స్థానికంగా `~/.familiar_ai/`లో నిల్వ చేయబడతాయి.

**Q: ఏ అధిక элемент చెప్పవచ్చు, `（...）` అని ఎందుకు ఫిర్యాదు చేస్తుంది?**
`ELEVENLABS_API_KEY` సెట్ అవుతుంది అని నిర్ధారించండి. లేకపోతే, స్వరం అక్షరాలు మరియు ఏఐ టెక్స్ట్‌కి తిరిగి వస్తుంది.

## సాంకేతిక నేపథ్యం

ఎలా పనిచేస్తుందో కనిపెడ్దాం? familiar-ai వెనుక పరిశోధనమును మరియు రూపకల్పన నిర్ణయాలను [docs/technical.md](./docs/technical.md) లో చూడండి — ReAct, SayCan, Reflexion, Voyager, ఇష్టత వ్యవస్థ, మరియు మరింత.

---

## సహాయం చేయడం

familiar-ai ఒక ఓపెన్ ప్రయోగం. దీన్నులో మీకు ఏదైనది నచ్చినా — సాంకేతికంగానా లేదా తాత్వికంగానా — సహకారాలు చాలా స్వాగతం.

**ప్రారంభించడానికి మంచి ప్రదేశాలు:**

| రేణువు | ఏమౌ తయారుచేయబడింది |
|------|---------------|
| కొత్త హార్డ్వేర్ | మరింత కమెరాతో (RTSP, IP Webcam), మైక్రోఫోన్లు, యాక్యుయ్టర్ల కొరకు మద్దతు |
| కొత్త సాధనలు | వెబ్ శోధన, హోమ్ ఆటోమేషన్, క్యాలెండర్, మీసా MCP ద్వారా ఏదైనా |
| కొత్త బ్యాకెండ్‌లు | ఏ LLM లేదా స్థానిక నమూనా `stream_turn` ఇంటర్ఫేస్‌కు సరిపోయినవి |
| వ్యక్తిత్వ నమూనాలు | విభిన్న భాషలకు మరియు వ్యక్తిత్వాలకు ME.md టెంప్లేట్ |
| పరిశోధన | మెరుగైన ఇష్ట మార్గాలు, జ్ఞాపకాలు తిరిగి పొందడం, మానసిక వాస్తవానికి ప్రేరణ |
| డాక్యుమెంటేషన్ | ట్యుటోరియల్స్, వాక్తికాలు, అనువాదాలు |

[CONTRIBUTING.md](./CONTRIBUTING.md) చూడండి డెవ్ సెటప్, కోడ్ శైలి, మరియు PR మార్గదర్శకాలను ఆలోచించండి.

మీరు ప్రారంభించడానికి ఎక్కడ అనుమానం ఉంటే, [ఒక సమస్యను తెరవండి](https://github.com/lifemate-ai/familiar-ai/issues) — మిమ్మల్ని సరే దిశలో సూచించడానికీ సంతోషంగా ఉంటాను.

---

## లైసెన్స్

[MIT](./LICENSE)
```
