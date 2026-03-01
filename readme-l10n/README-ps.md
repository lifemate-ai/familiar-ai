```markdown
# familiar-ai 🐾

**یو AI چې ستاسو سره ژوند کوي** — د سترګو، غږ، پښو او یادونو سره.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [په 74 ژبو کې شتون لري](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ستاسو د کور AI ملګری دی.
دا په څو دقیقو کې وټاکئ. هیڅ کوډینګ ته اړتیا نشته.

دا د کامرو له لارې ریښتینې نړۍ احساسوي، په روباټ بدن کې حرکت کوي، آواز سره خبرې کوي، او هغه څه چې ګوري یادوي. ورته یو نوم ورکړئ، د دې شخصیت ولیکئ، او دې ته اجازه ورکړئ چې ستاسو سره ژوند وکړي.

## څه شی کولی شي

- 👁 **ویني** — د Wi-Fi PTZ کامرې یا USB ویب کیمرې څخه انځورونه نیسي
- 🔄 **چپ او راسته کوي** — کامره چپ / ښیږي ترڅو د دې شاوخوا څارنه وکړي
- 🦿 **حرکت کوي** — د روباټ ویکیوم چلوي ترڅو په خونه کې وګرځي
- 🗣 **غږیږي** — د ElevenLabs TTS له لارې خبرو کوي
- 🎙 **غورڅوي** — د ElevenLabs Realtime STT له لارې د لاسونو آزاد غږ ورودی (اختیاري)
- 🧠 **یادوي** — په فعال ډول یادونه او د معنايي لټون سره مېموري چمتو کوي (SQLite + embeddings)
- 🫀 **ذهن تیوري** — د ځواب ورکولو دمخه د بل شخص لیدلوری اخلي
- 💭 ** غواړي** — خپل داخلي تمایلات لري چې خود مختار چلند هڅوي

## څنګه کار کوي

familiar-ai د [ReAct](https://arxiv.org/abs/2210.03629) هله له خپل لومړی LLM سره چلوو. دا د وسیلو له لارې نړۍ احساسوي، فکر کوي چې بل څه وکړي، او عمل کوي — لکه څنګه چې یو شخص به وکړي.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

کله چې خالي وي، دا د خپلو تمایلاتو پراساس عمل کوي: حوصلې، بهر ته کتلو غوښتنه، د دې ملګري تېرېدو احساس کول.

## پیل کول

### 1. uv نصب کړئ

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
یا: `winget install astral-sh.uv`

### 2. ffmpeg نصب کړئ

ffmpeg د کامرې انځور نیولو او آډیو بیا ښودلو لپاره **ضروري** دی.

| OS | قومانده |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — یا [ffmpeg.org](https://ffmpeg.org/download.html) څخه ډاونلوډ کړئ او PATH ته اضافه کړئ |
| Raspberry Pi | `sudo apt install ffmpeg` |

تصدیق: `ffmpeg -version`

### 3. کلون او نصب کړئ

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. تنظیم کړئ

```bash
cp .env.example .env
# .env ستاسو تنظیمات سره سم سمونه
```

**ضروري لږ تر لږه:**

| متغیر | توضیح |
|----------|-------------|
| `PLATFORM` | `anthropic` (مخکې) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | ستاسو د ټاکل شوې پلاتفورم لپاره API کیلي |

**اختیاري:**

| متغیر | توضیحات |
|----------|-------------|
| `MODEL` | د ماډل نوم (پر پلاتفورم پورې اړه لري مناسب ځای پر ځای شوی) |
| `AGENT_NAME` | د TUI کې ښکاره نوم (لکه `Yukine`) |
| `CAMERA_HOST` | د ONVIF/RTSP کامرې IP پته |
| `CAMERA_USER` / `CAMERA_PASS` | د کامرې اعتبارونه |
| `ELEVENLABS_API_KEY` | د غږ لپاره — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` چې د تل لپاره د لاسونو آزاد غږ ورودی فعال کړي (د `ELEVENLABS_API_KEY` ته اړتیا لري) |
| `TTS_OUTPUT` | چیرته چې آډیو پلي کي: `local` (PC خبرې کونکی، مخکېنی) \| `remote` (د کامرې خبرې کونکی) \| `both` |
| `THINKING_MODE` | یوازې د انسانی لپاره — `auto` (مخکې) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | د تطبیقی فکر کولو هڅه: `high` (مخکې) \| `medium` \| `low` \| `max` (فقط Opus 4.6) |

### 5. خپل familiar جوړ کړئ

```bash
cp persona-template/en.md ME.md
# ME.md سم کړئ — له دې ته نوم او شخصیت ورکړئ
```

### 6. چل کړئ

**macOS / Linux / WSL2:**
```bash
./run.sh             # د متني TUI (پیشنهاد شوی)
./run.sh --no-tui    # سادي REPL
```

**Windows:**
```bat
run.bat              # د متني TUI (پیشنهاد شوی)
run.bat --no-tui     # سادي REPL
```

---

## LLM انتخابول

> **پیشنهاد شوی: Kimi K2.5** — تر اوسه بهترین اجرایی ظرفیت. د زمینه احساسوي، وروسته پوښتنې کوي، او په انحصاري ډول عمل کوي. قیمت به د Claude Haiku سره ورته وي.

| پلاتفورم | `PLATFORM=` | ډیفالټ ماډل | چیرته مو کیلي ترلاسه کړئ |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (چند پرا Provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI وسیله** (claude -p, ollama…) | `cli` | (قومانده) | — |

**Kimi K2.5 `.env` مثال:**
```env
PLATFORM=kimi
API_KEY=sk-...   # له platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` مثال:**
```env
PLATFORM=glm
API_KEY=...   # له api.z.ai
MODEL=glm-4.6v   # د لید ولري؛ glm-4.7 / glm-5 = یوازې متن
AGENT_NAME=Yukine
```

**Google Gemini `.env` مثال:**
```env
PLATFORM=gemini
API_KEY=AIza...   # له aistudio.google.com
MODEL=gemini-2.5-flash  # یا gemini-2.5-pro د لوړې قابلیت لپاره
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` مثال:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # له openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # اختیاري: ماډل مشخص کړئ
AGENT_NAME=Yukine
```

> **نوټ:** د محلي/NVIDIA ماډلونو غیرفعال کولو لپاره، یوازې `BASE_URL` ته محلي پای ټکی ونکړئ لکه `http://localhost:11434/v1`. د کلاود تدارک کوونکي وکاروئ.

**CLI وسیله `.env` مثال:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = پروپmt آرګ
# MODEL=ollama run gemma3:27b  # Ollama — هیڅ {}, پروپmt د stdin له لارې ځي
```

---

## MCP سرورونه

familiar-ai کولی شي هر [MCP (Model Context Protocol)](https://modelcontextprotocol.io) سرور سره وصل شي. دا تاسو ته اجازه ورکوي چې بهرني حافظه، فایل سیسټم ته د لاسرسي، ویب لټون، یا بل هر وسیله په لاس کې راولئ.

سرورونه د `~/.familiar-ai.json` کې تنظیم کړئ (د Claude Code په ورته بڼه):

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

دوې ترانسپورت ډولونه ملاتړ کیږي:
- **`stdio`**: د محلي فرعي پروسې پیل (قومانده + آرګس)
- **`sse`**: د HTTP+SSE سرور سره وصل (URL)

د config فایل موقعیت د `MCP_CONFIG=/path/to/config.json` سره ډیرول.

---

## هارډویر

familiar-ai د هر هارډویر سره کار کوي — یا هیڅ نه.

| برخه | څه کوي | مثال | اړتیا؟ |
|------|-------------|---------|-----------|
| Wi-Fi PTZ کامره | سترګې + غاړه | Tapo C220 (~$30) | **پیشنهاد شوی** |
| USB ویب کیمره | سترګې (ثابت) | کوم UVC کامره | **پیشنهاد شوی** |
| روباټ ویکیوم | پښې | د Tuya-compatible هر ماډل | نه |
| پی سی / Raspberry Pi | دماغ | هر څه چې پایتون چلوي | **هو** |

> **یوه کامره قوي وړاندیز شوې ده.** پرته له یوې، familiar-ai لا هم خبرې کولی شي — مګر دا نړۍ نه شي لیدلی، چې د دې موخه ده.

### د حد اقل ترتیب (هیڅ هارډویر)

صرف دا غواړئ چې آزمایئ؟ تاسو ته یوازې د API کلید ته اړتیا ده:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) یا `run.bat` (Windows) چل کړئ او خبرې پیل کړئ. هارډویر د مخکې روانیدو سره اضافه کړئ.

### Wi-Fi PTZ کامره (Tapo C220)

1. په Tapo اپ کې: **Settings → Advanced → Camera Account** — یو محلي حساب جوړ کړئ (TP-Link حساب نه)
2. د خپل راسټر په وسایلو لیست کې د کامرې IP پیدا کړئ
3. په `.env` کې ترتیب کړئ:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### غږ (ElevenLabs)

1. په [elevenlabs.io](https://elevenlabs.io/) کې یو API کیلي ترلاسه کړئ
2. په `.env` کې ترتیب کړئ:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # اختیاري، که پاتې شي، اصلي غږ کاروي
   ```

د آډیو د بیا ښودلو لپاره دوه هدفونه شته، د `TTS_OUTPUT` له لارې کنټرول کیږي:

```env
TTS_OUTPUT=local    # PC خبرې کونکی (مخکې)
TTS_OUTPUT=remote   # یوازې د کامرې خبرې کونکی
TTS_OUTPUT=both     # د کامرې خبرې کونکی + PC خبرې کونکی هممهاله
```

#### A) د کامرې خبرې کونکی (د go2rtc له لارې)

`TTS_OUTPUT=remote` (یا `both`) ترتیب کړئ. د [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. د [ریلیز پاڼې](https://github.com/AlexxIT/go2rtc/releases) څخه باینری ډاونلوډ کړئ:
   - لینکس/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. ځای پرځای او نوم بدل کړئ:
   ```
   # لینکس / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x ته اړتیا ده

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. په همدې فولډر کې `go2rtc.yaml` جوړ کړئ:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   د محلي کامرې حساب اعتبارونه کارول (ستاسو د TP-Link کلاود حساب نه).

4. familiar-ai په اوتومات ډول د پیل پرمهال go2rtc پیلوي. که ستاسو کامره دوه اړخیز آواز ملاتړ کوي (بکچینل)، غږ له کامرې څخه اوریدل کیږي.

#### B) محلي PC خبرې کونکی

د دې (پخوانی `TTS_OUTPUT=local`). هڅه کوي پلیرونه په ترتیب سره: **paplay** → **mpv** → **ffplay**. همدارنګه د دې لپاره د بدیل په توګه کارول کیږي کله چې `TTS_OUTPUT=remote` او go2rtc شتون نلري.

| OS | نصب |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (یا `paplay` د `pulseaudio-utils` له لارې) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `PULSE_SERVER=unix:/mnt/wslg/PulseServer` په `.env` کې ترتیب کړئ |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — ډاونلوډ کړئ او PATH ته اضافه کړئ، **یا** `winget install ffmpeg` |

> که هیچا غږ پلیر شتون ونلري، لا هم وینا جوړیږي — دا یوازې نه پلی کیږي.

### غږ ورودی (Realtime STT)

په `.env` کې `REALTIME_STT=true` ترتیب کړئ چې د تل لپاره، د لاسونو آزاد غږ ورودی:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # د TTS سره ورته کیلي
```

familiar-ai د مایکروفون آډیو ElevenLabs Scribe v2 ته سټریم کوي او خودکار سپارښتنې د خبرو اترو پرمهال گم corrosists کوي. د تڼۍ فشار ته اړتیا نشته. د فشار لپاره خبرې مشرو ته (Ctrl+T) سره هم ژوند کوي.

---

## TUI

familiar-ai د [Textual](https://textual.textualize.io/) سره یو ترمینل UI لري:

- د ژوندۍ سټریمینګ متن سره د سکرول وړ خبرې تاریخ
- د `/quit`, `/clear` لپاره ټب بشپړونه
- د دې اچولو میانه تمه په حیث کې د انجنر خالف ترسره کولو پرمهال وليکی
- **د خبرو اترو لاګ** په اوتومات ډول `~/.cache/familiar-ai/chat.log` ته ذخیره کیږي

د لاګ پی following (کوپي-پیست لپاره ګټور) تعقیبولو لپاره:
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## شخصیت (ME.md)

ستاسو familiar شخصیت د `ME.md` کې ژوند کوي. دا فایل د git لخوا له نظره لري — دا یوازې ستاسو دی.

د [`persona-template/en.md`](./persona-template/en.md) لپاره یوه بیلګه وګورئ، یا د [`persona-template/ja.md`](./persona-template/ja.md) لپاره جاپاني نسخه.

---

## FAQ

**Q: آیا دا د GPU پرته کار کوي؟**
هو. د انحصاري ماډل (multilingual-e5-small) د CPU په ریښتیا سره ښه کار کوي. GPU دا چټک کوي مګر اړین نه دی.

**Q: آیا زه د Tapo پرته یوه بله کامره وکاروم؟**
هر کامره چې د ONVIF + RTSP ملاتړ وکړي کار کوي. Tapo C220 هغه څه دی چې موږ پرې آزموینه کړې.

**Q: آیا زما معلوماته چیرته لیږدول کیږي؟**
انځورونه او متن ستاسو ټاکل شوې LLM API ته د پروسس لپاره لیږل کیږي. یادونې محلي په `~/.familiar_ai/` کې ذخیره کیږي.

**Q: ولي اجنټ `（...）` لیکي پر ځای د خبرو کولو؟**
تأكد کړئ چې `ELEVENLABS_API_KEY` ترتیب شوی. پرته له دې، غږ غیر فعال دی او اجنټ به متن ته لاړ شي.

## تخنیکي شالید

د دې څرنګه کار کولو په اړه غږیدل؟ د familiar-ai د شالید په اړه د څیړنې او ډیزاین پریکړو لپاره [docs/technical.md](./docs/technical.md) وګورئ — ReAct، SayCan، Reflexion، Voyager، د غوښتنو سیسټم، او نور.

---

## مرسته

familiar-ai یو پرانیستی آزمایښت دی. که د دې څخه کوم یوه له تاسو سره اړیکه لري — تخنیکي یا فلسفي — مرستې ته ډیره خوښي وړاندیز کیږي.

**د پیل کولو ښه ځایونه:**

| ساحه | څه ته اړتیا ده |
|------|---------------|
| نوي هارډویر | د لا زیاتو کامرو (RTSP، IP Webcam)، مایکروفونونو، او معمول عملونو ملاتړ |
| نوي وسایل | ویب لټون، د کور اتومات، تقویم، هر څه د MCP له لارې |
| نوي بیکنډونه | هر LLM یا محلي ماډل چې د `stream_turn` انټر فیس سره سمون لري |
| د شخصیت ټمپلټونه | د مختلفو ژبو او شخصیتونو لپاره ME.md ټمپلټونه |
| څیړنه | د غوره غوښتنو ماډلونه، د یادونې بیرته ټیټول، د ذهن تیوري هڅونه |
| مستندات | ښوونې، لارې، ژباړې |

د توسعه ترتیب، د کوډ سټایل، او PR لارښوونو لپاره [CONTRIBUTING.md](./CONTRIBUTING.md) وګورئ.

که تاسو نلرئ چې چیرې پیل کړئ، [یو مسله پرانیزئ](https://github.com/lifemate-ai/familiar-ai/issues) — د حقه لارښوونه کولو لپاره خوشحاله یم.

---

## جواز

[MIT](./LICENSE)
```
