```markdown
# familiar-ai 🐾

**ایک AI جو آپ کے ساتھ ساتھ رہتا ہے** — آنکھوں، آواز، پیروں، اور یادداشت کے ساتھ۔

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 زبانوں میں دستیاب](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ایک AI ساتھی ہے جو آپ کے گھر میں رہتا ہے۔
اسے چند منٹوں میں سیٹ کریں۔ کوئی کوڈنگ کی ضرورت نہیں۔

یہ حقیقی دنیا کو کیمرے کے ذریعے محسوس کرتا ہے، ایک روبوٹ جسم پر حرکت کرتا ہے، بلند آواز میں بولتا ہے، اور جو کچھ وہ دیکھتا ہے اسے یاد رکھتا ہے۔ اسے ایک نام دیں، اس کی شخصیت لکھیں، اور اسے اپنے ساتھ رہنے دیں۔

## یہ کیا کر سکتا ہے

- 👁 **دیکھیں** — Wi-Fi PTZ کیمرے یا USB ویب کیم سے تصاویر captures کرتا ہے
- 🔄 **دیکھیں گرد و نوش** — اپنے ارد گرد کی جانچ کے لیے کیمرے کو پین اور جھکاتا ہے
- 🦿 **حرکت کریں** — ایک روبوٹ ویکیوم کو کمرے میں گھومنے کے لیے چلاتا ہے
- 🗣 **بولیں** — ElevenLabs TTS کے ذریعے بات کرتا ہے
- 🎙 **سنیں** — ElevenLabs Realtime STT کے ذریعے ہاتھوں سے آزاد صوتی ان پٹ (opt-in)
- 🧠 **یاد رکھیں** — فعال طور پر یاداشت کو ذخیرہ کرتا ہے اور سمینٹک سرچ کے ذریعے یاد کرتا ہے (SQLite + embeddings)
- 🫀 **تھیوری آف مائنڈ** — جواب دینے سے پہلے دوسرے شخص کے نقطہ نظر کو لیتا ہے
- 💭 **خواہش** — اس کا اپنا اندرونی مقام ہے جو خود مختار سلوک کو متحرک کرتا ہے

## یہ کیسے کام کرتا ہے

familiar-ai ایک [ReAct](https://arxiv.org/abs/2210.03629) لوپ چلاتا ہے جو آپ کے منتخب کردہ LLM سے چلتا ہے۔ یہ دنیا کو ٹولز کے ذریعے محسوس کرتا ہے، یہ سوچتا ہے کہ کیا کرنا ہے، اور عمل کرتا ہے — بالکل جیسے ایک شخص کرے گا۔

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

جب یہ غیر فعال ہوتا ہے، یہ اپنی خواہشات پر عمل کرتا ہے: تجسس، باہر دیکھنے کی خواہش، اپنے ساتھ رہنے والے شخص کی کمی محسوس کرنا۔

## شروع کرنے کے لیے

### 1. uv انسٹال کریں

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
یا: `winget install astral-sh.uv`

### 2. ffmpeg انسٹال کریں

ffmpeg **ضروری** ہے کیمرے کی تصویر کیپچر اور آڈیو پلے بیک کے لئے۔

| OS | کمانڈ |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — یا [ffmpeg.org](https://ffmpeg.org/download.html) سے ڈاؤن لوڈ کریں اور PATH میں شامل کریں |
| Raspberry Pi | `sudo apt install ffmpeg` |

تصدیق کریں: `ffmpeg -version`

### 3. کلون اور انسٹال کریں

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. تشکیل دیں

```bash
cp .env.example .env
# اپنی ترتیبات کے ساتھ .env میں ترمیم کریں
```

**کم سے کم ضروری:**

| متغیر | تفصیل |
|----------|-------------|
| `PLATFORM` | `anthropic` (ڈیفالٹ) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | منتخب کردہ پلیٹ فارم کے لئے آپ کا API کلید |

**اختیاری:**

| متغیر | تفصیل |
|----------|-------------|
| `MODEL` | ماڈل کا نام (پلیٹ فارم کے لحاظ سے معقول ڈیفالٹس) |
| `AGENT_NAME` | TUI میں دکھائے جانے والا نام (جیسے `Yukine`) |
| `CAMERA_HOST` | آپ کے ONVIF/RTSP کیمرے کا IP پتہ |
| `CAMERA_USER` / `CAMERA_PASS` | کیمرے کی اسناد |
| `ELEVENLABS_API_KEY` | صوتی آؤٹ پٹ کے لئے — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | ہمیشہ آن ہونے کے لئے `true` جو کہ ہاتھوں سے آزاد صوتی ان پٹ کو فعال کرتا ہے (requires `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | آڈیو جہاں چلانا ہے: `local` (پی سی اسپیکر، ڈیفالٹ) \| `remote` (کیمرے کا اسپیکر) \| `both` |
| `THINKING_MODE` | صرف Anthropic — `auto` (ڈیفالٹ) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | موافقت پذیر سوچنے کی کوشش: `high` (ڈیفالٹ) \| `medium` \| `low` \| `max` (صرف Opus 4.6) |

### 5. اپنا familiar بنائیں

```bash
cp persona-template/en.md ME.md
# ME.md میں ترمیم کریں — اسے ایک نام اور شخصیت دیں
```

### 6. چلائیں

**macOS / Linux / WSL2:**
```bash
./run.sh             # متنی TUI (تجویز کردہ)
./run.sh --no-tui    # سادہ REPL
```

**Windows:**
```bat
run.bat              # متنی TUI (تجویز کردہ)
run.bat --no-tui     # سادہ REPL
```

---

## LLM منتخب کرنا

> **تجویز کردہ: Kimi K2.5** — اب تک کی بہترین ایجنٹک کارکردگی کا ٹیسٹ کیا گیا۔ تناظر معلوم کرتا ہے، پیروی کرنے کے سوالات پوچھتا ہے، اور ایسے انداز میں خودمختار طور پر عمل کرتا ہے جو دیگر ماڈلز نہیں کرتے۔ قیمت کلود ہائیکو کے قریب ہے۔

| پلیٹ فارم | `PLATFORM=` | ڈیفالٹ ماڈل | کلید کہاں ملے گی |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI ٹول** (claude -p, ollama…) | `cli` | (کمانڈ) | — |

**Kimi K2.5 `.env` مثال:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` مثال:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` مثال:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # یا gemini-2.5-pro اعلیٰ صلاحیت کے لئے
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` مثال:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # optional: ماڈل متعین کریں
AGENT_NAME=Yukine
```

> **نوٹ:** مقامی/NVIDIA ماڈلز کو غیر فعال کرنے کے لئے، بس `BASE_URL` کو مقامی اینڈپوائنٹ جیسے `http://localhost:11434/v1` پر سیٹ نہ کریں۔ بلکہ کلاؤڈ فراہم کرنے والوں کا انتخاب کریں۔

**CLI ٹول `.env` مثال:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — کوئی {}, prompt stdin کے ذریعے جاتا ہے
```

---

## MCP سرورز

familiar-ai کسی بھی [MCP (Model Context Protocol)](https://modelcontextprotocol.io) سرور سے جڑ سکتا ہے۔ یہ آپ کو خارجی یادداشت، فائل سسٹم تک رسائی، ویب تلاش، یا کوئی بھی ٹول پلگ ان کرنے دیتا ہے۔

سرورز کو `~/.familiar-ai.json` میں ترتیب دیں (Claude Code کی طرح ہی شکل):

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

دو ٹرانسپورٹ کی اقسام کی حمایت کی جاتی ہیں:
- **`stdio`**: ایک مقامی سب پروسیس شروع کریں (`command` + `args`)
- **`sse`**: ایک HTTP+SSE سرور سے جڑیں (`url`)

کنفیگ فائل کی جگہ کو `MCP_CONFIG=/path/to/config.json` کے ساتھ اوور رائڈ کریں۔

---

## ہارڈ ویئر

familiar-ai کسی بھی ہارڈ ویئر کے ساتھ کام کرتا ہے — یا بالکل بھی نہیں۔

| حصہ | یہ کیا کرتا ہے | مثال | ضروری؟ |
|------|-------------|---------|-----------|
| Wi-Fi PTZ کیمرہ | آنکھیں + گردن | Tapo C220 (~$30) | **تجویز کردہ** |
| USB ویب کیم | آنکھیں (مستقل) | کوئی بھی UVC کیمرہ | **تجویز کردہ** |
| روبوٹ ویکیوم | پیر | کوئی بھی Tuya-compatible ماڈل | نہیں |
| پی سی / Raspberry Pi | دماغ | کچھ بھی جو Python کو چلائے | **جی ہاں** |

> **کیمرے کی سختی سے سفارش کی جاتی ہے۔** اس کے بغیر، familiar-ai اب بھی بول سکتا ہے — لیکن یہ دنیا کو نہیں دیکھ سکتا، جو کہ پوری بات کا نکتہ ہے۔

### کم سے کم سیٹ اپ (کوئی ہارڈ ویئر نہیں)

کیا آپ صرف آزمانا چاہتے ہیں؟ آپ کو صرف ایک API کلید کی ضرورت ہے:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) یا `run.bat` (Windows) کو چلائیں اور گفتگو شروع کریں۔ جیسے ہی آپ چلتے ہیں ہارڈ ویئر شامل کریں۔

### Wi-Fi PTZ کیمرہ (Tapo C220)

1. Tapo ایپ میں: **Settings → Advanced → Camera Account** — ایک مقامی اکاؤنٹ بنائیں (TP-Link اکاؤنٹ نہیں)
2. اپنے روٹر کے ڈیوائس کی فہرست میں کیمرے کا IP تلاش کریں
3. `.env` میں سیٹ کریں:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### آواز (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) پر ایک API کلید حاصل کریں
2. `.env` میں سیٹ کریں:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # optional, استعمال نہ ہونے پر ڈیفالٹ آواز کا استعمال کرتا ہے
   ```

دو پلے بیک مقامات ہیں، جو `TTS_OUTPUT` کے ذریعے کنٹرول ہوتے ہیں:

```env
TTS_OUTPUT=local    # پی سی اسپیکر (ڈیفالٹ)
TTS_OUTPUT=remote   # صرف کیمرے کا اسپیکر
TTS_OUTPUT=both     # کیمرے کا اسپیکر + پی سی اسپیکر بیک وقت
```

#### A) کیمرے کا اسپیکر (go2rtc کے ذریعے)

`TTS_OUTPUT=remote` (یا `both`) سیٹ کریں۔ [go2rtc](https://github.com/AlexxIT/go2rtc/releases) کی ضرورت ہے:

1. [رہائیوں کے صفحے](https://github.com/AlexxIT/go2rtc/releases) سے بائنری کو ڈاؤن لوڈ کریں:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. اسے جگہ دیں اور دوبارہ نام دیں:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x درکار ہے

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. اسی ڈائریکٹری میں `go2rtc.yaml` بنائیں:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   مقامی کیمرے کے اکاؤنٹ کی اسناد کا استعمال کریں (آپ کا TP-Link کلاؤڈ اکاؤنٹ نہیں)۔

4. familiar-ai خود بخود شروع ہونے پر go2rtc شروع کرتا ہے۔ اگر آپ کا کیمرہ دو طرفہ آڈیو (بیک چینل) کی حمایت کرتا ہے، تو آواز کیمرے کے اسپیکر سے چلے گی۔

#### B) مقامی پی سی اسپیکر

ڈیفالٹ (`TTS_OUTPUT=local`)۔ **paplay** → **mpv** → **ffplay** کے آرڈر میں پلیئرز کو آزمانے کی کوشش کرتا ہے۔ جب `TTS_OUTPUT=remote` اور go2rtc دستیاب نہ ہو تو بھی اس کا استعمال بیک اپ کے طور پر کیا جاتا ہے۔

| OS | انسٹال کریں |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (یا `paplay` کے ذریعے `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` میں `PULSE_SERVER=unix:/mnt/wslg/PulseServer` سیٹ کریں |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — ڈاؤن لوڈ کریں اور PATH میں شامل کریں، **یا** `winget install ffmpeg` |

> اگر کوئی آڈیو پلیئر دستیاب نہیں ہے، تو تقریر اب بھی تیار کی جاتی ہے — یہ صرف نہیں پلے ہوگی۔

### آواز کی ان پٹ (Realtime STT)

ہمیشہ آن، ہاتھوں سے آزاد صوتی ان پٹ کے لئے `.env` میں `REALTIME_STT=true` سیٹ کریں:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS کے ساتھ ایک ہی کلید
```

familiar-ai مائیکروفون کی آڈیو کو ElevenLabs Scribe v2 کے لئے اسٹریمنگ کرتا ہے اور جب آپ بولنا روکتے ہیں تو خود بخود ٹرانسکرپٹ جمع کرتا ہے۔ کسی بٹن کی دبانے کی ضرورت نہیں۔ یہ دستی طور پر بات کرنے کے موڈ کے ساتھ (Ctrl+T) میں ساتھ دیتا ہے۔

---

## TUI

familiar-ai میں [Textual](https://textual.textualize.io/) کے ساتھ بنایا گیا ایک ٹرمینل UI شامل ہے:

- جاندار اسٹریمنگ ٹیکسٹ کے ساتھ قابل سکرول گفتگو کی تاریخ
- `/quit`, `/clear` کے لئے ٹیب-پیشن
- جب ایجنٹ اپنی باری میں سوچ رہا ہو تو ٹائپ کرنے کے ذریعے اسے مداخلت کریں
- **گفتگو کی لاگ** خود بخود `~/.cache/familiar-ai/chat.log` میں محفوظ ہو جاتی ہے

لاگ کو دوسرے ٹرمینل میں فالو کرنے کے لئے (کاپی پیسٹ کے لئے مفید):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## شخصیت (ME.md)

آپ کے familiar کی شخصیت `ME.md` میں ہے۔ یہ فائل gitignored ہے — یہ صرف آپ کی ہے۔

مثال کے لئے [`persona-template/en.md`](./persona-template/en.md) دیکھیں، یا جاپانی ورژن کے لئے [`persona-template/ja.md`](./persona-template/ja.md) دیکھیں۔

---

## اکثر پوچھے جانے والے سوالات

**س: کیا یہ بغیر GPU کے کام کرتا ہے؟**
جی ہاں۔ ایمبیڈنگ ماڈل (multilingual-e5-small) CPU پر ٹھیک چلتا ہے۔ ایک GPU اسے تیز کرتا ہے لیکن یہ ضروری نہیں ہے۔

**س: کیا میں Tapo کے علاوہ کسی اور کیمرے کا استعمال کر سکتا ہوں؟**
کوئی بھی کیمرہ جو ONVIF + RTSP کی حمایت کرتا ہے وہ کام کرے گا۔ Tapo C220 ہمارا ٹیسٹ کردہ ماڈل ہے۔

**س: کیا میرا ڈیٹا کہیں بھی بھیجا جاتا ہے؟**
تصاویر اور متن آپ کے منتخب کردہ LLM API پر پروسیسنگ کے لئے بھیجے جاتے ہیں۔ یادیں مقامی طور پر `~/.familiar_ai/` میں محفوظ کی جاتی ہیں۔

**س: ایجنٹ `（...）` کیوں لکھتا ہے بجائے اس کے کہ وہ بولے؟**
یقینی بنائیں کہ `ELEVENLABS_API_KEY` سیٹ ہے۔ بغیر اس کے، آواز بند ہو جاتی ہے اور ایجنٹ متن پر واپس آتا ہے۔

## تکنیکی پس منظر

جاننا چاہتے ہیں کہ یہ کیسے کام کرتا ہے؟ دیکھیں [docs/technical.md](./docs/technical.md) familiar-ai کے پیچھے تحقیق اور ڈیزائن کے فیصلوں کے لئے — ReAct، SayCan، Reflexion، Voyager، خواہش کا نظام، اور مزید۔

---

## شراکت داری

familiar-ai ایک کھلا تجربہ ہے۔ اگر ان میں سے کوئی بھی آپ کے لئے موزوں ہے — تکنیکی یا فلسفی طور پر — شراکتیں خوش آمدید ہیں۔

**شروع کرنے کے لئے اچھے مقامات:**

| علاقہ | کیا درکار ہے |
|------|---------------|
| نئی ہارڈ ویئر | مزید کیمروں (RTSP، آئی پی ویب کیم)، مائیکروفونز، ایکچویٹرز کی حمایت |
| نئے ٹولز | ویب تلاش، گھریلو خودکار، کیلنڈر، کوئی بھی MCP کے ذریعے |
| نئے بیک اینڈ | کوئی بھی LLM یا مقامی ماڈل جو `stream_turn` انٹرفیس میں فٹ بیٹھتا ہو |
| شخصیت کے ٹیمپلیٹس | مختلف زبانوں اور شخصیات کے لئے ME.md ٹیمپلیٹس |
| تحقیق | بہتر خواہش کے ماڈلز، یاد داشت کی بازیابی، تھیوری آف مائنڈ کی پرامپٹنگ |
| دستاویزات | سبق، واک تھرو، ترجمے |

[CONTRIBUTING.md](./CONTRIBUTING.md) میں ترقی کی ترتیب، کوڈ اسٹائل، اور PR ہدایات کے لئے دیکھیں۔

اگر آپ کو نہیں معلوم کہ کہاں سے شروع کرنا ہے، تو [ایک مسئلہ کھولیں](https://github.com/lifemate-ai/familiar-ai/issues) — ہم خوشی سے آپ کو صحیح راستے پر گامزن کریں گے۔

---

## لائسنس

[MIT](./LICENSE)
```
