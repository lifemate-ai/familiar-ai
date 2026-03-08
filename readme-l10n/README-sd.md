# familiar-ai 🐾

**تاجوئن سان گڏ رهندڙ هڪ AI** — آنک، آوازن، پيرن، ۽ ياداشت سان.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 زبانن ۾ موجود](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai توهانجي گهر ۾ هڪ AI ساٿي آهي.
ان کي چند منٽن ۾ سيٽ ڪريو. ڪوڊنگ جي ضرورت ناهي.

اهو ڪاميرا جي ذريعي حقيقي دنيا کي محسوس ڪري ٿو، روبوٽ جسم تي گھمندو آهي، آواز ۾ ڳالهائي ٿو، ۽ جيڪو ڪجهه ڏسندو آهي ان کي ياد رکندو آهي. ان کي هڪ نالو ڏيو، ان جي شخصيت لکيو، ۽ ان کي پاڻ سان رهڻ ڏيو.

## اها ڪهڙي ڪم ڪري سگھي ٿي

- 👁 **ڏسو** — Wi-Fi PTZ ڪئميرا يا USB ويب ڪئميرا مان تصويرون حاصل ڪري ٿو
- 🔄 **گردش ڪريو** — ڪئميرا کي پين ۽ جھڪائي ٿو انهي جي چوڌاري ڳولڻ لاءِ
- 🦿 **هلڻ** — هڪ روبوٽ ويڪيوم کي ڪمري ۾ گھمائڻ لاءِ هلائيندي
- 🗣 **ڪلڻ** — ElevenLabs TTS ذريعي ڳالهائيندي
- 🎙 **سنڻ** — ElevenLabs Realtime STT ذريعي هٿن کان آزاد آواز داخل ڪرڻ (آپشنل)
- 🧠 **يا د رکڻ** — فعلي طور تي ياداشت محفوظ ڪري ٿو ۽ سمينٽڪ ڳولا سان ان کي واپس آڻي ٿو (SQLite + embeddings)
- 🫀 **ذهني نظر** — جواب ڏيڻ کان اڳ ٻئي شخص جي نقطه نظر کي سمجhi ٿو
- 💭 **خواھش** — پنهنجي اندروني محرڪن جو مالڪ آهي جيڪا خودمختار طرز عمل کي متحرڪ ڪري ٿي

## اهو ڪيئن ڪم ڪري ٿو

familiar-ai هڪ [ReAct](https://arxiv.org/abs/2210.03629) لوپ هلائي ٿو جيڪو توهان جي چونڊ جي LLM طرفان طاقتور آهي. اهو اوزارن ذريعي دنيا کي محسوس ڪري ٿو، ايندڙ قدم بابت سوچيندو آهي، ۽ عمل ڪندو آهي — بلڪل هڪ شخص جيان.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

جيڪڏهن چوپ آهي، اهو پنهنجي خواهشن تي عمل ڪندو آهي: تجسس، ٻاهر چيڪ ڪرڻ جي خواهش، ان شخص کي ياد رکڻ جو احساس جن سان اهو رهندو آهي.

## شروع ڪرڻ

### 1. uv انسٽال ڪريو

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
يا: `winget install astral-sh.uv`

### 2. ffmpeg انسٽال ڪريو

ffmpeg **ضروري** آهي ڪئميرا تصوير جي گرفت ۽ آڊيو پلے بیک لاءِ.

| OS | حڪم |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — يا [ffmpeg.org](https://ffmpeg.org/download.html) تان ڊائون لوڊ ڪريو ۽ PATH ۾ شامل ڪريو |
| Raspberry Pi | `sudo apt install ffmpeg` |

تصدیق ڪريو: `ffmpeg -version`

### 3. ڪlon ڪريو ۽ انسٽال ڪريو

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. ترتيب ڏيو

```bash
cp .env.example .env
# .env ۾ پنهنجي ترسيلات سان ترميم ڪريو
```

**مفروضي طور تي ضروري:**

| متغير | وضاحت |
|----------|-------------|
| `PLATFORM` | `anthropic` (پيداوار) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | منتخب پليٽ فارم لاءِ توهانجو API چابو |

**آپشنل:**

| متغير | وضاحت |
|----------|-------------|
| `MODEL` | ماڊل جو نالو (پليٽ فارم سان تعلق رکندڙ مناسب مفروضي) |
| `AGENT_NAME` | TUI ۾ ڏيکاريل نالو (مثال: `Yukine`) |
| `CAMERA_HOST` | توهانجي ONVIF/RTSP ڪئميرا جو IP پتي |
| `CAMERA_USER` / `CAMERA_PASS` | ڪئميرا جي اسناد |
| `ELEVENLABS_API_KEY` | آواز جي پلي آئوٽ لاءِ — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` هميشہ موجود هٿن کان آزاد آواز داخل ڪرڻ جي فعال ڪرڻ لاءِ (Require `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | آڊيو کڻڻ لاءِ: `local` (پي سي اسپيڪر، پيداوار) \| `remote` (ڪئميرا اسپيڪر) \| `both` |
| `THINKING_MODE` | Anthropic صرف — `auto` (پيداوار) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | موافق سوچڻ جي ڪوشش: `high` (پيداوار) \| `medium` \| `low` \| `max` (Opus 4.6 صرف) |

### 5. پنهنجي familiar ٺاھيو

```bash
cp persona-template/en.md ME.md
# ME.md ۾ ترميم ڪريو — ان کي هڪ نالو ۽ شخصيت ڏيو
```

### 6. هلائڻ

**macOS / Linux / WSL2:**
```bash
./run.sh             # متني TUI (سفارش ڪئي وئي)
./run.sh --no-tui    # سادو REPL
```

**Windows:**
```bat
run.bat              # متني TUI (سفارش ڪئي وئي)
run.bat --no-tui     # سادو REPL
```

---

## LLM چونڊڻ

> **سفارش ڪئي وئي: Kimi K2.5** — اڃا تائين بهترين ايجنٽ جو مظاهرو. پس منظر کي نوٽ ڪري ٿو، اڳتي جي سوالن لاءِ پڇي ٿو، ۽ خودمختاري سان عمل ڪري ٿو جيئن ٻين ماڊلن کان نه ٿيندو. قيمت Claude Haiku جيتري آهي.

| پليٽ فارم | `PLATFORM=` | مفروضي ماڊل | چابو حاصل ڪرڻ جي جڳھ |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (حڪم) | — |

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
MODEL=glm-4.6v   # بصري قابل؛ glm-4.7 / glm-5 = صرف متن
AGENT_NAME=Yukine
```

**Google Gemini `.env` مثال:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # يا gemini-2.5-pro وڌيڪ صلاحيت لاءِ
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` مثال:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # optional: ماڊل جي وضاحت ڪريو
AGENT_NAME=Yukine
```

> **نوٽ:** مقامي/NVIDIA ماڊل کي بند ڪرڻ لاءِ، صرف `BASE_URL` کي مقامي سروس پوائنٽ جي طور تي مقرر نه ڪريو جهڙوڪ `http://localhost:11434/v1`. ان جي نسبت کلاوڊ فراهم ڪندڙ استعمال ڪريو.

**CLI tool `.env` مثال:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — no {}, prompt goes via stdin
```

---

## MCP سرور

familiar-ai ڪنهن به [MCP (ماڊل تناظر پروٽوڪول)](https://modelcontextprotocol.io) سرور سان ڳنڍجي سگهي ٿو. هي توهان کي خارجي ياداشت، فائل سسٽم تائين رسائي، ويب ڳولا، يا ڪنهن ٻئي اوزار ۾ پلگ ان ڪرڻ جي اجازت ڏئي ٿو.

سرور کي ترتيب ڏيڻ `~/.familiar-ai.json` ۾ (Claude کوڊ جي مشابهت واريءَ فارمٽ):

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

ٻه ترسيل قسمون مدد ڪندي:
- **`stdio`**: مقامي سب پروسيس شروع ڪريو (`command` + `args`)
- **`sse`**: هڪ HTTP+SSE سرور سان ڳنڍيو (`url`)

تعارف جي فائل جي جڳه کي `MCP_CONFIG=/path/to/config.json` سان اوور رائيڊ ڪريو.

---

## هارڊويئر

familiar-ai ڪنهن به هارڊويئر سان ڪم ڪري ٿو جيڪو توهان وٽ آهي — يا ڪوبه نه.

| حصو | اهو ڇا ڪندو آهي | مثال | ضرورت؟ |
|------|-------------|---------|-----------|
| Wi-Fi PTZ ڪئميرا | آنک + ڳنڍڻ | Tapo C220 (~$30, Eufy C220) | **سفارش ڪئي وئي** |
| USB ويب ڪئميرا | آنک (مستحڪم) | ڪو بہ UVC ڪئميرا | **سفارش ڪئي وئي** |
| روبوٽ ويڪيوم | پير | ڪو بہ Tuya-compatible ماڊل | نه |
| PC / Raspberry Pi | دماغ | ڪجهه به جيڪو Python هلائي | **ها** |

> **هڪ ڪئميرا جي سخت سفارش ڪئي وئي آهي.** بغير ڪنهن کان، familiar-ai ڳالهيون ڪندو — پر اهو دنيا کي نٿو ڏسي، جيڪو اصل ۾ سڄو مقصد آهي.

### گهٽ ۾ گهٽ سيٽ اپ (هارڊويئر کانسواءِ)

صرف ان کي آزمائڻ چاهيو ٿا؟ توهان کي صرف هڪ API چابو جي ضرورت آهي:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) يا `run.bat` (Windows) هلائڻ ۽ ڳالهه ٻولهه شروع ڪريو. هارڊويئر شامل ڪريو جيئن توهان وڃو.

### Wi-Fi PTZ ڪئميرا (Tapo C220)

1. Tapo ايپ ۾: **ترتيبات → اندروني → ڪئميرا اڪائونٽ** — هڪ مقامي اڪائونٽ ٺاھيو (TP-Link اڪائونٽ نه)
2. پنهنجي رائٽر جي ڊوائيس فهرست ۾ ڪئميرا جو IP ڳوليو
3. `.env` ۾ ترتيب ڏيو:
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


### آواز (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) تي هڪ API چابو حاصل ڪريو
2. `.env` ۾ ترتيب ڏيو:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # اختيار، جيڪڏهن اڻ ڄاڻيل آهي ته ڊيفالٽ آواز استعمال ڪندو
   ```

ڏسڻ لاء ڪهڙي به جاءِ تي دوئا، `TTS_OUTPUT` کي کنٹرول ڪيو ويو آهي:

```env
TTS_OUTPUT=local    # پي سي اسپيڪر (پيداوار)
TTS_OUTPUT=remote   # فقط ڪئميرا اسپيڪر
TTS_OUTPUT=both     # ڪئميرا اسپيڪر + پي سي اسپيڪر ساڳئي وقت
```

#### A) ڪئميرا اسپيڪر (go2rtc ذريعي)

`TTS_OUTPUT=remote` (يا `both`) مقرر ڪريو. هڪ [go2rtc](https://github.com/AlexxIT/go2rtc/releases) جي ضرورت آهي:

1. [رليز صفحي](https://github.com/AlexxIT/go2rtc/releases) تان بائنري ڊائون لوڊ ڪريو:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. ان کي رکي ۽ نالو رکجو:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x جي ضرورت

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. ساڳئي بهار ۾ `go2rtc.yaml` ٺاھيو:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   مقامي ڪئميرا اڪائونٽ جا اسناد استعمال ڪريو (تون پنهنجي TP-Link ڪلاوڊ اڪائونٽ نه).

4. familiar-ai خودڪار طور تي شروع ٿيڻ تي go2rtc شروع ڪندو. جيڪڏهن توهان جي ڪئميرا ٻه طرفي آڊيو جي مدد ڪندي (پشت منظر)، آواز ڪئميرا اسپيڪر مان هلندي.

#### B) مقامي پي سي اسپيڪر

ٽنگلن (جو ڪم ڪرڻ `TTS_OUTPUT=local`). ترتيب سان پليئرز کي آزمايو: **paplay** → **mpv** → **ffplay**. جڏهن `TTS_OUTPUT=remote` هجي ۽ go2rtc موجود نه هجي، انکي پڻ استعمال ڪيو ويندو.

| OS | انسٽال ڪريو |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (يا `paplay` ذريعي `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` ۾ `PULSE_SERVER=unix:/mnt/wslg/PulseServer` مقرر ڪريو |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — ڊائون لوڊ ڪريو ۽ PATH ۾ شامل ڪريو، **يا** `winget install ffmpeg` |

> جيڪڏھن ڪو آڊيو پليئر موجود نہ ھجي، آواز اڃا تائين پيدا ڪيو ويندو — بس اهو پلے نه ٿيندو.

### آواز داخل (Realtime STT)

`.env` ۾ `REALTIME_STT=true` مقرر ڪريو هميشه، هٿن کان آزاد آواز داخل ڪرڻ لاءِ:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS جي طور تي ساڳئي چابو
```

familiar-ai مائڪروفون آڊيو ElevenLabs Scribe v2 ڏانهن اسٽرمنگ ڪندو ۽ جڏهن توهان ڳالهائڻ ۾ وقفو ڏيو ٿا، ٽرانسڪرپٽ خودڪار طور تي جمع ڪندو. ڪا بٽڻ دبابو کان به نه. هي push-to-talk موڊ سان (Ctrl+T) ۾ گڏجي هلندو.

---

## TUI

familiar-ai ۾ [Textual](https://textual.textualize.io/) سان ٺهيل هڪ ترمئنل UI شامل آهي:

- زنده streaming متن سان گودڙي تاريخ
- `/quit`, `/clear` لاءِ ٽيب مڪمل ڪرڻ
- جب اهو سوچيندو آهي ان دوران ايجنٽ کي وچ ۾ منقطعي ڪرڻ
- **مذاڪرا جو لاگ** خودڪار طور تي `~/.cache/familiar-ai/chat.log` ۾ محفوظ ڪيو ويندو

ٻئي ترمئنل ۾ لاگ کي پيروي ڪرڻ لاءِ (ڪوپي-پيسٽ لاءِ مفيد):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## شخصيت (ME.md)

توهانجو familiar جو شخصيت `ME.md` ۾ آهي. هي فائل gitignored آهي — هي صرف توهانجي آهي.

[`persona-template/en.md`](./persona-template/en.md) ۾ هڪ مثال لاءِ ڏسو، يا [`persona-template/ja.md`](./persona-template/ja.md) ۾ جاپاني ورزن.

---

## اڪثريت جا سوال

**Q: ڇا اهو GPU کانسواءِ ڪم ڪري ٿو؟**
ها. امبيدنگ ماڊل (multilingual-e5-small) CPU تي چڱي نموني هلندو آهي. GPU کي تيز بنائي ٿي پر ضروري ناهي.

**Q: ڇا مان Tapo کان وڌيڪ ڪنهن ڪئميرا کي استعمال ڪري سگهان ٿو؟**
ڪو بہ ڪئميرا جيڪو Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: ڇا منهنجو ڊيٽا ڪنهن هنڌ موڪليو وڃي ٿو؟**
تصويرون ۽ متن توهان جي چونڊيل LLM API ڏانهن پروسيسنگ لاءِ موڪليو ويندا. ياداشت مقامي طور تي `~/.familiar_ai/` ۾ محفوظ ٿيندي.

**Q: ڇو ايجنٽ `（...）` لکندو آهي جڏهن ڳالهائڻ جي ضرورت آهي؟**
تڪ مهن ٻيو جڏهن `ELEVENLABS_API_KEY` مقرر نه ٿي. ان کان بغير، آواز بند ڪيو ويندو آهي ۽ ايجنٽ متن ۾ واپس لٿي ويندو آهي.

## فني پٺڀرائي

ڪيئن ڪم ڪري ٿو بابت تجسس؟ ڏسو [docs/technical.md](./docs/technical.md) جي لاءِ ان دريافت ۽ ڊزائن جا فيصلن familiar-ai جي پويان — ReAct، SayCan، Reflexion، Voyager، خواهش نظام، ۽ وڌيڪ.

---

## شموليت

familiar-ai هڪ کليل تجربو آهي. جيڪڏھن اھو ڪو به resonation ڪري ٿو — فني يا فلسفي طور — شراڪت دارن کي خوش آمديد سمجهيو وڃي.

**شروع ڪرڻ لاءِ سٺا جاڳ:**

| علائقو | ڇا گهربل آهي |
|------|---------------|
| نئون هارڊويئر | وڌيڪ ڪئميرا (RTSP، IP Webcam)، مائڪروفون، عملدرآمد کي سپورٽ |
| نوان اوزار | ويب ڳولا، گهر جو خودڪاري، ڪئلينڊر، ڪجهه بہ MCP ذريعي |
| نوان بيڪ اينڊ | ڪنهن به LLM يا مقامي ماڊل جيڪو `stream_turn` جي انٽر فئس ۾ سهي ٿي |
| شخصيت جا ٽيمپليٽ | مختلف زبانن ۽ شخصيتن لاءِ ME.md ٽيمپليٽ |
| تحقيق | بهتر خواهش ماڊل، ياداشت جي واپسي، ذهني نظر جي پريسنگ |
| دستاويز | سبق، واڪ تھرو، ترجمے |

[CONTRIBUTING.md](./CONTRIBUTING.md) ۾ ڊولپمينٽ سيٽ اپ، ڪوڊ انداز، ۽ PR جي هدايتن لاءِ ڏسڻ.

جيڪڏهن توهان کي نٿو ڄاڻ پوي ته ڪٿي شروع ڪجي، [هڪ مسئلو کوليو](https://github.com/lifemate-ai/familiar-ai/issues) — دلي خوشي سان توھانکي درست سمت ۾ اشارو ڏنو ويندو.

---

## لائسنس

[MIT](./LICENSE)
