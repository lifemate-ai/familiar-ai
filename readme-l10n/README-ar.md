# familiar-ai 🐾

**ذكاء اصطناعي يعيش بجانبك** — لديه عيون، صوت، أرجل، وذاكرة.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [متاح بـ 74 لغة](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai هو رفيق ذكي اصطناعي يعيش في منزلك.
قم بإعداده في دقائق. لا يتطلب كتابة كود.

يستشعر العالم الحقيقي من خلال الكاميرات، ويتحرك على جسم روبوت، ويتحدث بصوت عالٍ، ويتذكر ما يراه. أعطه اسمًا، اكتب شخصيته، واتركه يعيش معك.

## ماذا يمكنه أن يفعل

- 👁 **يرى** — يلتقط الصور من كاميرا PTZ متصلة بالواي فاي أو Webcam USB
- 🔄 **يتجول** — يوجه الكاميرا لاستكشاف محيطه
- 🦿 **يتحرك** — يقود مكنسة روبوتية للتجول في الغرفة
- 🗣 **يتحدث** — يستخدم ElevenLabs TTS للحديث
- 🎙 **يستمع** — إدخال صوتي بدون استخدام اليدين عبر ElevenLabs Realtime STT (اختياري)
- 🧠 **يتذكر** — يخزن ويسترجع الذكريات بنشاط باستخدام البحث الدلالي (SQLite + تضمينات)
- 🫀 **نظرية العقل** — يتبنى منظور الشخص الآخر قبل الرد
- 💭 **الرغبة** — لديه دوافع داخلية خاصة به تُحفز السلوكيات المستقلة

## كيف يعمل

familiar-ai يقوم بتشغيل حلقة [ReAct](https://arxiv.org/abs/2210.03629) مدعومة باختيارك من LLM. يستشعر العالم من خلال الأدوات، يفكر فيما يجب عليه فعله بعد ذلك، ويتصرف — تمامًا كما يفعل الإنسان.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

عندما يكون في حالة خمول، يتصرف وفقًا لرغباته: الفضول، الرغبة في النظر إلى الخارج، والشعور بالوحدة بعد افتقاده للشخص الذي يعيش معه.

## البدء

### 1. تثبيت uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
أو: `winget install astral-sh.uv`

### 2. تثبيت ffmpeg

ffmpeg **مطلوب** لالتقاط صور الكاميرا وتشغيل الصوت.

| النظام | الأمر |
|--------|-------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — أو يمكنك تنزيله من [ffmpeg.org](https://ffmpeg.org/download.html) وإضافته إلى PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

تحقق: `ffmpeg -version`

### 3. استنساخ وتثبيت

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. تكوين

```bash
cp .env.example .env
# حرر .env مع إعداداتك
```

**المتطلبات الدنيا:**

| المتغير | الوصف |
|---------|-------|
| `PLATFORM` | `anthropic` (الافتراضي) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | مفتاح API الخاص بك للمنصة المختارة |

**اختياري:**

| المتغير | الوصف |
|---------|-------|
| `MODEL` | اسم النموذج (الإعدادات الافتراضية المعقولة حسب المنصة) |
| `AGENT_NAME` | اسم العرض المظهر في TUI (على سبيل المثال `Yukine`) |
| `CAMERA_HOST` | عنوان IP لكاميرتك ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | بيانات اعتماد الكاميرا |
| `ELEVENLABS_API_KEY` | للإخراج الصوتي — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` لتفعيل إدخال الصوت من دون استخدام اليدين (يتطلب `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | حيث يتم تشغيل الصوت: `local` (مكبر الصوت الخاص بالكمبيوتر، الافتراضي) \| `remote` (مكبر الصوت الخاص بالكاميرا) \| `both` |
| `THINKING_MODE` | خاص بـ Anthropic فقط — `auto` (الافتراضي) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | جهد التفكير التكييفي: `high` (الافتراضي) \| `medium` \| `low` \| `max` (فقط Opus 4.6) |

### 5. أنشئ رفيقك

```bash
cp persona-template/en.md ME.md
# حرر ME.md — أعطه اسمًا وشخصية
```

### 6. تشغيل

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI النصية (موصى بها)
./run.sh --no-tui    # REPL بسيط
```

**Windows:**
```bat
run.bat              # TUI النصية (موصى بها)
run.bat --no-tui     # REPL بسيط
```

---

## اختيار LLM

> **موصى به: Kimi K2.5** — أفضل أداء وكيل تم اختباره حتى الآن. يلاحظ السياق، يطرح أسئلة متابعة، ويتصرف بشكل مستقل بطرق لا تفعلها النماذج الأخرى. مسعّر على نحو مشابه لـ Claude Haiku.

| المنصة | `PLATFORM=` | النموذج الافتراضي | أين تحصل على المفتاح |
|--------|------------|------------------|---------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| متوافق مع OpenAI (Ollama، vllm...) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (مقدم متعدد) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **أداة سطر الأوامر** (claude -p، ollama…) | `cli` | (الأمر) | — |

**مثال `.env` لـ Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # من platform.moonshot.ai
AGENT_NAME=Yukine
```

**مثال `.env` لـ Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # من api.z.ai
MODEL=glm-4.6v   # مدعوم للرؤية؛ glm-4.7 / glm-5 = نص فقط
AGENT_NAME=Yukine
```

**مثال `.env` لـ Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # من aistudio.google.com
MODEL=gemini-2.5-flash  # أو gemini-2.5-pro لقدرات أعلى
AGENT_NAME=Yukine
```

**مثال `.env` لـ OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # من openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # اختياري: حدد النموذج
AGENT_NAME=Yukine
```

> **ملاحظة:** لتعطيل النماذج المحلية/NVIDIA، ما عليك سوى عدم ضبط `BASE_URL` على نقطة نهاية محلية مثل `http://localhost:11434/v1`. استخدم مقدمي الخدمات السحابية بدلاً من ذلك.

**مثال `.env` لأداة سطر الأوامر:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = معطى prompt
# MODEL=ollama run gemma3:27b  # Ollama — بدون {}، يتم توجيه المعطى عبر stdin
```

---

## خوادم MCP

 يمكن لـ familiar-ai الاتصال بأي خادم [MCP (نموذج بروتوكول السياق)](https://modelcontextprotocol.io). هذا يسمح لك بتوصيل الذاكرة الخارجية، والوصول إلى نظام الملفات، والبحث على الويب، أو أي أداة أخرى.

(configuration الخوادم في `~/.familiar-ai.json` (نفس تنسيق كلود كود):

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

يدعم نوعان من النقل:
- **`stdio`**: إطلاق عملية فرعية محلية (`command` + `args`)
- **`sse`**: الاتصال بخادم HTTP+SSE (`url`)

يمكنك تجاوز موقع ملف التكوين باستخدام `MCP_CONFIG=/path/to/config.json`.

---

## الأجهزة

يعمل familiar-ai مع أي أجهزة لديك — أو بدون أي منها.

| الجزء | ماذا يفعل | مثال | مطلوب؟ |
|------|----------|-------|--------|
| كاميرا PTZ متصلة بالواي فاي | عيون + عنق | Tapo C220 (~$30, Eufy C220) | **موصى بها** |
| Webcam USB | عيون (ثابتة) | أي كاميرا UVC | **موصى بها** |
| مكنسة روبوتية | أرجل | أي طراز متوافق مع Tuya | لا |
| الكمبيوتر / Raspberry Pi | دماغ | أي شيء يعمل بـ Python | **نعم** |

> **الكاميرا موصى بها بشدة.** بدون واحدة، يمكن لـ familiar-ai التحدث — لكنه لا يستطيع رؤية العالم، وهو نوع من الشيء الأساسي.

### الإعداد البسيط (بدون أجهزة)

تريد فقط تجربته؟ تحتاج فقط إلى مفتاح API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

شغل `./run.sh` (macOS/Linux/WSL2) أو `run.bat` (Windows) وابدأ المحادثة. أضف الأجهزة أثناء القيام بذلك.

### كاميرا PTZ متصلة بالواي فاي (Tapo C220)

1. في تطبيق Tapo: **الإعدادات → متقدمة → حساب الكاميرا** — أنشئ حسابًا محليًا (ليس حساب TP-Link)
2. ابحث عن IP الكاميرا في قائمة الأجهزة في جهاز التوجيه الخاص بك
3. قم بتعيينه في `.env`:
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


### الصوت (ElevenLabs)

1. احصل على مفتاح API من [elevenlabs.io](https://elevenlabs.io/)
2. قم بتعيينه في `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # اختياري، يستخدم الصوت الافتراضي إذا تم تجاهله
   ```

توجد وجهتان لتشغيل الصوت، يتم التحكم فيهما بواسطة `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # مكبر الصوت الخاص بالكمبيوتر (افتراضي)
TTS_OUTPUT=remote   # مكبر الصوت الخاص بالكاميرا فقط
TTS_OUTPUT=both     # مكبر الصوت الخاص بالكاميرا + مكبر الصوت الخاص بالكمبيوتر في نفس الوقت
```

#### A) مكبر الصوت الخاص بالكاميرا (عبر go2rtc)

قم بتعيين `TTS_OUTPUT=remote` (أو `both`). يتطلب [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. قم بتنزيل الثنائي من [صفحة الإصدارات](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. ضعها وأعد تسميتها:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x مطلوب

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. أنشئ `go2rtc.yaml` في نفس الدليل:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   استخدم بيانات اعتماد الحساب المحلي للكاميرا (وليس حساب TP-Link السحابي الخاص بك).

4. يبدأ familiar-ai go2rtc تلقائيًا عند الإطلاق. إذا كانت الكاميرا تدعم الصوت ثنائي الاتجاه (قناة عكسية)، فإن الصوت سيصدر من مكبر الصوت الخاص بالكاميرا.

#### B) مكبر الصوت الخاص بالكمبيوتر المحلي

الإعداد الافتراضي (`TTS_OUTPUT=local`). يحاول اللاعبون بالترتيب: **paplay** → **mpv** → **ffplay**. يستخدم أيضًا كنسخة احتياطية عندما يكون `TTS_OUTPUT=remote` و go2rtc غير متاح.

| النظام | التثبيت |
|--------|----------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (أو `paplay` عبر `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — قم بتعيين `PULSE_SERVER=unix:/mnt/wslg/PulseServer` في `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — قم بالتنزيل وأضفه إلى PATH، **أو** `winget install ffmpeg` |

> إذا لم يكن هناك مشغل صوت متاح، يتم توليد الصوت ولكن لن يتم تشغيله.

### إدخال الصوت (Realtime STT)

قم بتعيين `REALTIME_STT=true` في `.env` لإدخال الصوت دائمًا وبدون استخدام اليدين:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # نفس المفتاح مثل TTS
```

يتم بث صوت الميكروفون إلى ElevenLabs Scribe v2 وتسجيل النصوص تلقائيًا عندما تتوقف عن الكلام. لا حاجة للضغط على زر. يتواجد بالتوازي مع وضع الدفع للتحدث (Ctrl+T).

---

## TUI

يتضمن familiar-ai واجهة_terminal مبنية باستخدام [Textual](https://textual.textualize.io/):

- تاريخ محادثة قابل للتمرير مع نص متدفق مباشر
- إكمال تلقائي لـ `/quit`, `/clear`
- قطع الوكيل أثناء التفكير بكتابة أثناء تفكيره
- **سجل المحادثة** محفوظ تلقائيًا في `~/.cache/familiar-ai/chat.log`

للاطلاع على السجل في نافذة طرفية أخرى (مفيد للنسخ واللصق):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## الشخصية (ME.md)

تعيش شخصية رفيقك في `ME.md`. هذا الملف يتجاهله git — إنه لك وحدك.

انظر إلى [`persona-template/en.md`](./persona-template/en.md) كمثال، أو [`persona-template/ja.md`](./persona-template/ja.md) لنسخة يابانية.

---

## الأسئلة الشائعة

**س: هل يعمل بدون GPU؟**
نعم. نموذج التضمين (multilingual-e5-small) يعمل بشكل جيد على وحدة المعالجة المركزية. تُسرّع GPU من الأداء لكنها ليست مطلوبة.

**س: هل يمكنني استخدام كاميرا غير Tapo؟**
يجب أن تعمل أي كاميرا تدعم Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**س: هل تُرسل بياناتي إلى أي مكان؟**
تُرسل الصور والنصوص إلى واجهة برمجة تطبيقات LLM التي اخترتها للمعالجة. تُخزن الذكريات محليًا في `~/.familiar_ai/`.

**س: لماذا يكتب الوكيل `（...）` بدلاً من التحدث؟**
تأكد من تعيين `ELEVENLABS_API_KEY`. بدونها، يتم تعطيل الصوت ويتحول الوكيل للاستخدام النصي.

## الخلفية التقنية

هل أنت فضولي حول كيفية عمله؟ انظر [docs/technical.md](./docs/technical.md) للبحث والقرارات التصميمية وراء familiar-ai — ReAct، SayCan، Reflexion، Voyager، نظام الرغبات، والمزيد.

---

## المساهمة

familiar-ai هو تجربة مفتوحة. إذا كان أي من هذا يت resonates معك — تقنيًا أو فلسفيًا — فالمساهمات مرحب بها بشدة.

**أماكن جيدة للبدء:**

| المنطقة | ما هو مطلوب |
|---------|--------------|
| أجهزة جديدة | دعم لمزيد من الكاميرات (RTSP، Webcam IP)، ميكروفونات، محركات |
| أدوات جديدة | بحث عبر الإنترنت، أتمتة المنزل، التقويم، أي شيء عبر MCP |
| الباكيندات الجديدة | أي LLM أو نموذج محلي يناسب واجهة `stream_turn` |
| قوالب الشخصية | قوالب ME.md للغات وشخصيات مختلفة |
| البحث | نماذج رغبة أفضل، استرجاع الذكريات، تحفيز نظرية العقل |
| الوثائق | دروس، عمليات استكشاف، ترجمات |

انظر [CONTRIBUTING.md](./CONTRIBUTING.md) لإعداد التطوير، نمط الشيفرة، وإرشادات PR.

إذا كنت غير متأكد من أين تبدأ، [افتح مشكلة](https://github.com/lifemate-ai/familiar-ai/issues) — سعيد جدًا بتوجيهك في الاتجاه الصحيح.

---

## الترخيص

[MIT](./LICENSE)
