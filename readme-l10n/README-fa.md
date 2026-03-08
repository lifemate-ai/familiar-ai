```markdown
# familiar-ai 🐾

**یک هوش مصنوعی که در کنار شما زندگی می‌کند** — با چشم‌ها، صدا، پاها و حافظه.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [در 74 زبان قابل دسترسی است](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai یک همراه هوش مصنوعی است که در خانه شما زندگی می‌کند.
در عرض چند دقیقه آن را راه‌اندازی کنید. نیازی به کدنویسی نیست.

این هوش مصنوعی دنیای واقعی را از طریق دوربین‌ها درک می‌کند، بر روی بدنه ربات حرکت می‌کند، سخن می‌گوید و آنچه را که می‌بیند به خاطر می‌سپارد. به آن یک نام بدهید، شخصیت آن را بنویسید و بگذارید با شما زندگی کند.

## چه کارهایی می‌تواند انجام دهد

- 👁 **ببیند** — تصاویر را از یک دوربین PTZ Wi-Fi یا وب‌کم USB ثبت می‌کند
- 🔄 **به اطراف نگاه کند** — دوربین را به چرخش و کج کردن برای کاوش محیط اطراف هدایت می‌کند
- 🦿 **حرکت کند** — یک جاروبرقی ربات را برای گردش در اتاق هدایت می‌کند
- 🗣 **صحبت کند** — از طریق ElevenLabs TTS صحبت می‌کند
- 🎙 **گوش دهد** — ورودی صوتی بدون دست از طریق ElevenLabs Realtime STT (اختیاری)
- 🧠 **به یاد بسپارد** — به طور فعال خاطرات را با جستجوی معنایی ذخیره و بازیابی می‌کند (SQLite + embeddings)
- 🫀 **نظریه ذهن** — به دیدگاه شخص دیگر قبل از پاسخ دادن توجه می‌کند
- 💭 **تمایل** — دارای انگیزه‌های داخلی خود است که رفتار خودمختار را تحریک می‌کند

## چگونه کار می‌کند

familiar-ai یک حلقه [ReAct](https://arxiv.org/abs/2210.03629) راه‌اندازی می‌کند که به انتخاب شما از LLM قدرت می‌دهد. آن به جهان از طریق ابزارها درک می‌کند، به این فکر می‌کند که بعداً چه کار کند و اقدام می‌کند — دقیقاً مانند یک شخص.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

وقتی بی‌تحرک است، بر اساس تمایلات خود عمل می‌کند: کنجکاوی، خواستن برای نگاه کردن به بیرون، دلتنگی برای شخصی که با او زندگی می‌کند.

## شروع کار

### 1. نصب uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
یا: `winget install astral-sh.uv`

### 2. نصب ffmpeg

ffmpeg برای ثبت تصاویر دوربین و پخش صدا **نیاز است**.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — یا از [ffmpeg.org](https://ffmpeg.org/download.html) دانلود کنید و به PATH اضافه کنید |
| Raspberry Pi | `sudo apt install ffmpeg` |

تأیید: `ffmpeg -version`

### 3. کلون و نصب

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. پیکربندی

```bash
cp .env.example .env
# .env را با تنظیمات خود ویرایش کنید
```

**حداقل نیاز:**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (پیش‌فرض) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | کلید API شما برای پلتفرم انتخابی |

**اختیاری:**

| Variable | Description |
|----------|-------------|
| `MODEL` | نام مدل (گزینه‌های معقول برای هر پلتفرم) |
| `AGENT_NAME` | نام نمایشی که در TUI نشان داده می‌شود (مثلاً `Yukine`) |
| `CAMERA_HOST` | آدرس IP دوربین ONVIF/RTSP شما |
| `CAMERA_USER` / `CAMERA_PASS` | اعتبارنامه‌های دوربین |
| `ELEVENLABS_API_KEY` | برای خروجی صوتی — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` برای فعال‌سازی ورودی صوتی بدون دست همیشه‌فعال (نیاز به `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | جایی که صدا پخش می‌شود: `local` (بلندگو PC، پیش‌فرض) \| `remote` (بلندگوی دوربین) \| `both` |
| `THINKING_MODE` | فقط Anthropic — `auto` (پیش‌فرض) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | تلاش تفکر تطبیقی: `high` (پیش‌فرض) \| `medium` \| `low` \| `max` (فقط Opus 4.6) |

### 5. ایجاد آشنای خود

```bash
cp persona-template/en.md ME.md
# ME.md را ویرایش کنید — به آن یک نام و شخصیت دهید
```

### 6. اجرا

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI متنی (پیشنهادی)
./run.sh --no-tui    # REPL ساده
```

**Windows:**
```bat
run.bat              # TUI متنی (پیشنهادی)
run.bat --no-tui     # REPL ساده
```

---

## انتخاب یک LLM

> **پیشنهاد شده: Kimi K2.5** — بهترین عملکرد ایجنتی که تا کنون آزمایش شده است. توجه به زمینه، پرسش‌های پیگیری می‌پرسد و به طور خودمختار عمل می‌کند به روش‌هایی که مدل‌های دیگر نمی‌کنند. قیمت مشابه با Claude Haiku.

| Platform | `PLATFORM=` | Default model | Where to get key |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (the command) | — |

**مثال `.env` Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # از platform.moonshot.ai
AGENT_NAME=Yukine
```

**مثال `.env` Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # از api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = فقط متن
AGENT_NAME=Yukine
```

**مثال `.env` Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # از aistudio.google.com
MODEL=gemini-2.5-flash  # یا gemini-2.5-pro برای قابلیت‌های بالاتر
AGENT_NAME=Yukine
```

**مثال `.env` OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # از openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # اختیاری: مشخص کردن مدل
AGENT_NAME=Yukine
```

> **توجه:** برای غیر فعال کردن مدل‌های محلی/NVIDIA، به سادگی `BASE_URL` را به یک نقطه محلی مانند `http://localhost:11434/v1` تنظیم نکنید. به جایش از ارائه‌دهندگان ابری استفاده کنید.

**مثال `.env` ابزار CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = پارامتر پیش روی
# MODEL=ollama run gemma3:27b  # Ollama — بدون {}, پارامتر از طریق stdin ارسال می‌شود
```

---

## سرورهای MCP

familiar-ai می‌تواند به هر سرور [MCP (Model Context Protocol)](https://modelcontextprotocol.io) متصل شود. این امکان را به شما می‌دهد که حافظه خارجی، دسترسی به فایل سیستم، جستجوی وب یا هر ابزار دیگری را متصل کنید.

سرورها را در `~/.familiar-ai.json` پیکربندی کنید (همان فرمت مانند Claude Code):

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

دو نوع حمل و نقل پشتیبانی می‌شود:
- **`stdio`**: راه‌اندازی یک subprocess محلی (`command` + `args`)
- **`sse`**: اتصال به یک سرور HTTP+SSE (`url`)

مکان فایل پیکربندی را می‌توانید با `MCP_CONFIG=/path/to/config.json` نادیده بگیرید.

---

## سخت‌افزار

familiar-ai با هر سخت‌افزاری که دارید کار می‌کند — یا حتی بدون آن.

| Part | What it does | Example | Required? |
|------|-------------|---------|-----------|
| دوربین PTZ Wi-Fi | چشم‌ها + گردن | Tapo C220 (~$30, Eufy C220) | **پیشنهادی** |
| وب‌کم USB | چشم‌ها (ثابت) | هر دوربین UVC | **پیشنهادی** |
| جاروبرقی رباتی | پاها | هر مدل سازگار با Tuya | خیر |
| PC / Raspberry Pi | مغز | هر چیزی که پایتون را اجرا کند | **بله** |

> **یک دوربین به شدت توصیه می‌شود.** بدون آن، familiar-ai هنوز می‌تواند صحبت کند — اما نمی‌تواند دنیای بیرون را ببیند، که در واقع هدف اصلی است.

### تنظیمات حداقلی (بدون سخت‌افزار)

فقط می‌خواهید آن را امتحان کنید؟ شما فقط به یک کلید API نیاز دارید:

```env
PLATFORM=kimi
API_KEY=sk-...
```

اجرای `./run.sh` (macOS/Linux/WSL2) یا `run.bat` (Windows) و شروع به چت کنید. سخت‌افزار را به مرور اضافه کنید.

### دوربین PTZ Wi-Fi (Tapo C220)

1. در برنامه Tapo: **تنظیمات → پیشرفته → حساب دوربین** — یک حساب محلی بسازید (اما حساب TP-Link نباشید)
2. IP دوربین را در لیست دستگاه‌های روتر خود پیدا کنید
3. در `.env` تنظیم کنید:
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


### صدا (ElevenLabs)

1. یک کلید API در [elevenlabs.io](https://elevenlabs.io/) دریافت کنید
2. در `.env` تنظیم کنید:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # اختیاری، از صدای پیش‌فرض استفاده می‌کند اگر حذف شود
   ```

دو مقصد پخش وجود دارد که توسط `TTS_OUTPUT` کنترل می‌شود:

```env
TTS_OUTPUT=local    # بلندگوی PC (پیش‌فرض)
TTS_OUTPUT=remote   # فقط بلندگوی دوربین
TTS_OUTPUT=both     # بلندگوی دوربین + بلندگوی PC به صورت همزمان
```

#### A) بلندگوی دوربین (از طریق go2rtc)

`TTS_OUTPUT=remote` (یا `both`) را تنظیم کنید. به [go2rtc](https://github.com/AlexxIT/go2rtc/releases) نیاز دارید:

1. باینری را از [صفحه انتشار](https://github.com/AlexxIT/go2rtc/releases) دانلود کنید:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. آن را در محل قرار دهید و نام‌گذاری کنید:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x مورد نیاز است

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. در همان دایرکتوری `go2rtc.yaml` را بسازید:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   از اعتبارنامه‌های حساب دوربین محلی استفاده کنید (نه حساب ابری TP-Link شما).

4. familiar-ai به طور خودکار go2rtc را در زمان راه‌اندازی آغاز می‌کند. اگر دوربین شما صدای دوطرفه را پشتیبانی کند (بازخورد)، صدا از بلندگوی دوربین پخش می‌شود.

#### B) بلندگوی محلی PC

پیش‌فرض (`TTS_OUTPUT=local`). سعی می‌کند پلیرها را به ترتیب امتحان کند: **paplay** → **mpv** → **ffplay**. همچنین به عنوان یک پشتیبان زمانی که `TTS_OUTPUT=remote` و go2rtc در دسترس نیست استفاده می‌شود.

| OS | Install |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (یا `paplay` از طریق `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — در `.env` `PULSE_SERVER=unix:/mnt/wslg/PulseServer` را تنظیم کنید |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — دانلود کرده و به PATH اضافه کنید، **یا** `winget install ffmpeg` |

> اگر هیچ پلیر صوتی در دسترس نباشد، گفتار هنوز تولید می‌شود — فقط پخش نخواهد شد.

### ورودی صوتی (Realtime STT)

در `.env` `REALTIME_STT=true` را برای ورودی صوتی همیشه‌فعال و بدون دست تنظیم کنید:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # همان کلید به عنوان TTS
```

familiar-ai صدای میکروفن را به ElevenLabs Scribe v2 استریم می‌کند و هنگامی که شما صحبت را متوقف می‌کنید، به طور خودکار متن‌ها را ذخیره می‌کند. هیچ فشاری بر روی دکمه مورد نیاز نیست. با حالت فشار برای صحبت (Ctrl+T) همخوانی دارد.

---

## TUI

familiar-ai شامل یک رابط کاربری ترمینالی است که با [Textual](https://textual.textualize.io/) ساخته شده است:

- تاریخچه مکالمات قابل پیمایش با متن زنده استریم شده
- تکمیل تب برای `/quit`, `/clear`
- وقفه در تفکر ایجنت در میانه‌ی نوبت با تایپ در حالی که در حال فکر کردن است
- **گزارش مکالمه** به طور خودکار در `~/.cache/familiar-ai/chat.log` ذخیره می‌شود

برای پیگیری گزارش در ترمینال دیگر (برای کپی-پیست مفید):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## شخصیت (ME.md)

شخصیت آشنای شما در `ME.md` زندگی می‌کند. این فایل gitignored است — فقط شما آن را دارید.

برای یک مثال، [`persona-template/en.md`](./persona-template/en.md) یا برای نسخه ژاپنی [`persona-template/ja.md`](./persona-template/ja.md) را ببینید.

---

## سوالات متداول

**س: آیا بدون GPU کار می‌کند؟**
بله. مدل embedding (multilingual-e5-small) به خوبی بر روی CPU اجرا می‌شود. یک GPU کار را سریع‌تر می‌کند اما لازم نیست.

**س: آیا می‌توانم از دوربین دیگری غیر از Tapo استفاده کنم؟**
هر دوربینی که از Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**س: آیا داده‌های من به جایی ارسال می‌شود؟**
تصاویر و متن‌ها به API LLM انتخابی شما برای پردازش ارسال می‌شوند. خاطرات به صورت محلی در `~/.familiar_ai/` ذخیره می‌شوند.

**س: چرا ایجنت به جای صحبت کردن `（...）` می‌نویسد؟**
اطمینان حاصل کنید که `ELEVENLABS_API_KEY` تنظیم شده است. بدون آن، صدای خروجی غیرفعال است و ایجنت به متن باز می‌گردد.

## پس‌زمینه فنی

کنجکاوید که چگونه کار می‌کند؟ برای تحقیقات و تصمیمات طراحی پشت familiar-ai به [docs/technical.md](./docs/technical.md) مراجعه کنید — ReAct، SayCan، Reflexion، Voyager، سیستم تمایل و بیشتر.

---

## مشارکت

familiar-ai یک آزمایش باز است. اگر هیچ‌کدام از این موارد با شما هماهنگ است — از نظر فنی یا فلسفی — مشارکت‌ها بسیار خوش‌آمد است.

**محل‌های خوب برای شروع:**

| Area | What's needed |
|------|---------------|
| سخت‌افزار جدید | پشتیبانی از دوربین‌های بیشتر (RTSP، وب‌کم IP)، میکروفن‌ها، محرک‌ها |
| ابزارهای جدید | جستجوی وب، اتوماسیون خانگی، تقویم، هر چیزی از طریق MCP |
| Backendهای جدید | هر LLM یا مدل محلی که متناسب با رابط `stream_turn` باشد |
| الگوهای شخصیت | الگوهای ME.md برای زبان‌ها و شخصیت‌های مختلف |
| تحقیق | مدل‌های تمایل بهتر، بازیابی حافظه، تحریک نظریه ذهن |
| مستندات | آموزش‌ها، راهنماها، ترجمه‌ها |

به [CONTRIBUTING.md](./CONTRIBUTING.md) برای تنظیمات توسعه، سبک کد و دستورالعمل‌های PR مراجعه کنید.

اگر مطمئن نیستید از کجا شروع کنید، [یک مسئله باز کنید](https://github.com/lifemate-ai/familiar-ai/issues) — خوشحال می‌شوم که شما را به سمت درست راهنمایی کنم.

---

## مجوز

[MIT](./LICENSE)
```
