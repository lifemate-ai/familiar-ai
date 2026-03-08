```markdown
# familiar-ai 🐾

**একটি AI যা আপনার সাথে বসবাস করে** — চোখ, স্বর, পা এবং স্মৃতি সহ।

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Available in 74 languages](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai হলো একটি AI সঙ্গী যা আপনার বাড়িতে বসবাস করে।
এটি মিনিটের মধ্যে সেট আপ করুন। কোড লেখার প্রয়োজন নেই।

এটি ক্যামেরার মাধ্যমে বাস্তব বিশ্বের উপলব্ধি করে, রোবট শরীরে চারিদিকে চলে, উচ্চকণ্ঠে কথা বলে এবং যা দেখে তা মনে রাখে। এটি একটি নাম দিন, এর ব্যক্তিত্ব লিখুন, এবং এটি আপনার সাথে বসবাস করতে দিন।

## এটি কী কী করতে পারে

- 👁 **দেখুন** — Wi-Fi PTZ ক্যামেরা বা USB ওয়েবক্যাম থেকে ছবি ধারণ করে
- 🔄 **চারপাশে তাকান** — চারপাশের পরিবেশ অন্বেষণের জন্য ক্যামেরা প্যান এবং টিল্ট করে
- 🦿 **চলুন** — একটি রোবট ভ্যাকুয়াম চালিত করে ঘরে ঘুরে বেড়ায়
- 🗣 **কথা বলুন** — ElevenLabs TTS এর মাধ্যমে কথা বলে
- 🎙 **শুনুন** — ElevenLabs Realtime STT এর মাধ্যমে হাতমুক্ত ভয়েস ইনপুট (অপট-ইন)
- 🧠 **মনে রাখুন** — কার্যকরীভাবে স্মৃতি সংরক্ষণ এবং পুনরুদ্ধার করে সেমান্তিক অনুসন্ধানের মাধ্যমে (SQLite + এম্বেডিংস)
- 🫀 **মনোরীতি** — প্রতিউত্তরের আগে অন্য ব্যক্তির দৃষ্টিভঙ্গি গ্রহণ করে
- 💭 **ইচ্ছা** — স্বায়ত্তশাসিত আচরণে উদ্দীপক নিজের অভ্যন্তরীণ চালনা থাকে

## এটি কীভাবে কাজ করে

familiar-ai একটি [ReAct](https://arxiv.org/abs/2210.03629) লুপ চালায় যা আপনার পছন্দের LLM দ্বারা চালিত। এটি টুলের মাধ্যমে বিশ্বকে উপলব্ধি করে, পরবর্তী কাজ সম্পর্কে চিন্তা করে, এবং কাজ করে — যেমন একজন মানুষ করবে।

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

অকার্যকর থাকার সময়, এটি নিজের ইচ্ছার উপর কাজ করে: কৌতূহল, বাইরের দিকে তাকাতে চাওয়া, নিজেদের সাথে বসবাসকারী ব্যক্তির স্মৃতি।

## শুরু করা যাক

### 1. uv ইনস্টল করুন

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
অথবা: `winget install astral-sh.uv`

### 2. ffmpeg ইনস্টল করুন

ffmpeg হল **অবশ্যই প্রয়োজনীয়** ক্যামেরার ছবি ধারণ এবং অডিও প্লেব্যাকের জন্য।

| OS | কমান্ড |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — অথবা [ffmpeg.org](https://ffmpeg.org/download.html) থেকে ডাউনলোড করুন এবং PATH এ যোগ করুন |
| Raspberry Pi | `sudo apt install ffmpeg` |

যাচাই করুন: `ffmpeg -version`

### 3. ক্লোন এবং ইনস্টল করুন

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. কনফিগার করুন

```bash
cp .env.example .env
# আপনার সেটিংস সহ .env সম্পাদনা করুন
```

**ন্যূনতম প্রয়োজন:**

| ভেরিয়েবল | বর্ণনা |
|----------|-------------|
| `PLATFORM` | `anthropic` (ডিফল্ট) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | নির্বাচিত প্ল্যাটফর্মের জন্য আপনার API কী |

**ঐচ্ছিক:**

| ভেরিয়েবল | বর্ণনা |
|----------|-------------|
| `MODEL` | মডেল নাম (প্রত্যেক প্ল্যাটফর্মের জন্য গ্রহণযোগ্য ডিফল্ট) |
| `AGENT_NAME` | TUI তে প্রদর্শিত নাম (যেমন `Yukine`) |
| `CAMERA_HOST` | আপনার ONVIF/RTSP ক্যামেরার IP ঠিকানা |
| `CAMERA_USER` / `CAMERA_PASS` | ক্যামেরার পরিচয়পত্র |
| `ELEVENLABS_API_KEY` | ভয়েস আউটপুটের জন্য — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | সব সময়ের জন্য হাতমুক্ত ভয়েস ইনপুট সক্ষম করতে `true` (প্রয়োজন `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | অডিও প্লেব্যাকের স্থান: `local` (PC স্পিকার, ডিফল্ট) \| `remote` (ক্যামেরার স্পিকার) \| `both` |
| `THINKING_MODE` | Anthropic শুধুমাত্র — `auto` (ডিফল্ট) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | অভিযোজিত চিন্তাভাবনার প্রচেষ্টা: `high` (ডিফল্ট) \| `medium` \| `low` \| `max` (Opus 4.6 শুধুমাত্র) |

### 5. আপনার পরিচিতি তৈরি করুন

```bash
cp persona-template/en.md ME.md
# ME.md সম্পাদনা করুন — এটি একটি নাম এবং ব্যক্তিত্ব দিন
```

### 6. চালান

**macOS / Linux / WSL2:**
```bash
./run.sh             # টেক্সচুয়াল TUI (প্রস্তাবিত)
./run.sh --no-tui    # পLAIN REPL
```

**Windows:**
```bat
run.bat              # টেক্সচুয়াল TUI (প্রস্তাবিত)
run.bat --no-tui     # পLAIN REPL
```

---

## একটি LLM নির্বাচন

> **প্রস্তাবিত: Kimi K2.5** — এখন পর্যন্ত পরীক্ষা করা সেরা এজেন্টিক কার্যকারিতা। প্রেক্ষাপট লক্ষ্য করে, অনুসরণকারী প্রশ্ন জিজ্ঞেস করে, এবং অন্যান্য মডেলের তুলনায় স্বায়ত্তশাসিত ভাবে কাজ করে। Claude Haiku এর মতো একই দামে।

| প্ল্যাটফর্ম | `PLATFORM=` | ডিফল্ট মডেল | কী কোথা থেকে পাবেন |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-কম্প্যাটিবল (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (মাল্টি-প্রোভাইডার) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI টুল** (claude -p, ollama…) | `cli` | (কমান্ড) | — |

**Kimi K2.5 `.env` উদাহরণ:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` উদাহরণ:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # ভিশন সক্ষম; glm-4.7 / glm-5 = পাঠ্য-শুধু
AGENT_NAME=Yukine
```

**Google Gemini `.env` উদাহরণ:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # অথবা উচ্চ ক্ষমতার জন্য gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` উদাহরণ:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # ঐচ্ছিক: মডেল নির্ধারণ করুন
AGENT_NAME=Yukine
```

> **দ্রষ্টব্য:** স্থানীয়/NVIDIA মডেলগুলি নিষ্ক্রিয় করতে, শুধু `BASE_URL` কে একটি স্থানীয় এন্ডপয়েন্টের মতো `http://localhost:11434/v1` এ সেট করবেন না। বরং ক্লাউড প্রদানকারীরা ব্যবহার করুন।

**CLI টুল `.env` উদাহরণ:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = প্রম্পট আর্গ
# MODEL=ollama run gemma3:27b  # Ollama — কোন {}, প্রম্পট stdin এর মাধ্যমে যাবে
```

---

## MCP সার্ভার

familiar-ai যে কোনও [MCP (মডেল কনটেক্সট প্রোটোকল)](https://modelcontextprotocol.io) সার্ভারের সাথে সংযুক্ত হতে পারে। এটি আপনাকে বাইরের মেমরি, ফাইল সিস্টেম অ্যাক্সেস, ওয়েব অনুসন্ধান, বা অন্য কোনও সরঞ্জাম সংযোগ করতে দেয়।

`~/.familiar-ai.json` এ সার্ভার কনফিগার করুন (Claude কোডের মতো একই ফরম্যাট):

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

দুটি ট্রান্সপোর্ট প্রকার সমর্থিত:
- **`stdio`**: একটি স্থানীয় সাবপ্রক্রিয়া চালু করুন (`command` + `args`)
- **`sse`**: একটি HTTP+SSE সার্ভারে সংযোগ করুন (`url`)

কনফিগারেশন ফাইলের অবস্থান `MCP_CONFIG=/path/to/config.json` দ্বারা ওভাররাইড করুন।

---

## হার্ডওয়্যার

familiar-ai আপনার কাছে যে কোনও হার্ডওয়্যার নিয়ে কাজ করে — অথবা একটিও নয়।

| অংশ | এটি কী করে | উদাহরণ | প্রয়োজনীয়? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ ক্যামেরা | চোখ + গলা | Tapo C220 (~$30, Eufy C220) | **প্রস্তাবিত** |
| USB ওয়েবক্যাম | চোখ (স্থির) | যে কোনও UVC ক্যামেরা | **প্রস্তাবিত** |
| রোবট ভ্যাকুয়াম | পা | যে কোনও Tuya-সঙ্গত মডেল | না |
| PC / Raspberry Pi | মস্তিষ্ক | কিছু যা পাইথন চালায় | **হ্যাঁ** |

> **একটি ক্যামেরার প্রচুর প্রয়োজনীয়তা।** এটি ছাড়া, familiar-ai এখনও কথা বলতে পারে — কিন্তু এটি বিশ্ব দেখতে পারছে না, যা মোটামুটি পুরো পয়েন্ট।

### ন্যূনতম সেটআপ (কোনও হার্ডওয়্যার নেই)

এটি চেষ্টা করতে চান? আপনাকে কেবল একটি API কী প্রয়োজন:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) বা `run.bat` (Windows) চালান এবং চ্যাট শুরু করুন। প্রক্রিয়ায় হার্ডওয়্যার যুক্ত করুন।

### Wi-Fi PTZ ক্যামেরা (Tapo C220)

1. Tapo অ্যাপে: **সেটিংস → উন্নত → ক্যামেরা অ্যাকাউন্ট** — একটি স্থানীয় অ্যাকাউন্ট তৈরি করুন (TP-Link অ্যাকাউন্ট নয়)
2. আপনার রাউটারে ডিভাইস তালিকায় ক্যামেরার IP খুঁজুন
3. `.env` এ সেট করুন:
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


### ভয়েস (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) এ একটি API কী পান
2. `.env` এ সেট করুন:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # ঐচ্ছিক, বাদ দিলে ডিফল্ট ভয়েস ব্যবহার করে
   ```

দুইটি প্লেব্যাক গন্তব্য রয়েছে, যা `TTS_OUTPUT` দ্বারা নিয়ন্ত্রিত:

```env
TTS_OUTPUT=local    # PC স্পিকার (ডিফল্ট)
TTS_OUTPUT=remote   # শুধুমাত্র ক্যামেরার স্পিকার
TTS_OUTPUT=both     # ক্যামেরার স্পিকার + PC স্পিকার একযোগে
```

#### A) ক্যামেরার স্পিকার (go2rtc এর মাধ্যমে)

`TTS_OUTPUT=remote` (বা `both`) সেট করুন। প্রয়োজন [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. [রিলিজ পৃষ্ঠা](https://github.com/AlexxIT/go2rtc/releases) থেকে বাইনারিটি ডাউনলোড করুন:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. এটি স্থাপন এবং পুনঃনামকরণ করুন:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x প্রয়োজন

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. একই ফোল্ডারে `go2rtc.yaml` তৈরি করুন:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   স্থানীয় ক্যামেরার অ্যাকাউন্ট পরিচয়পত্রগুলি ব্যবহার করুন (আপনার TP-Link ক্লাউড অ্যাকাউন্ট নয়)।

4. familiar-ai স্বয়ংক্রিয়ভাবে চালু হলে go2rtc শুরু করে। যদি আপনার ক্যামেরা দুই-দিকের অডিও সমর্থন করে (ব্যাকচ্যানেল), তবে ভয়েস ক্যামেরার স্পিকার থেকে বাজবে।

#### B) স্থানীয় PC স্পিকার

ডিফল্ট (`TTS_OUTPUT=local`)। এটি ক্রম অনুসারে প্লেয়ারগুলিকে চেষ্টা করে: **paplay** → **mpv** → **ffplay**। এছাড়াও `TTS_OUTPUT=remote` এ যখন go2rtc উপলব্ধ নয় তখন এটি ব্যাকআপ হিসেবে ব্যবহৃত হয়।

| OS | ইনস্টল |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (অথবা `paplay` এর মাধ্যমে `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` এ `PULSE_SERVER=unix:/mnt/wslg/PulseServer` সেট করুন |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — ডাউনলোড করুন এবং PATH এ যোগ করুন, **অথবা** `winget install ffmpeg` |

> যদি কোন অডিও প্লেয়ার উপলব্ধ না থাকে, তবে বক্তৃতা এখনও তৈরি হয় — এটি শুধুমাত্র বাজবে না।

### ভয়েস ইনপুট (Realtime STT)

সব সময়ের জন্য হাতমুক্ত ভয়েস ইনপুটের জন্য `.env` এ `REALTIME_STT=true` সেট করুন:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS এর জন্য একই কী
```

familiar-ai মাইক্রোফোনের অডিও ElevenLabs Scribe v2 এ প্রবাহিত করে এবং আপনি কথা বলার সময় বন্ধ হয়ে গেলে স্বয়ংক্রিয়ভাবে ট্রান্সক্রিপ্ট জমা করে। বোতাম টিপে চাপা প্রয়োজন নেই। এটি পুশ-টু-টক মোডের সাথে সহাবস্থান করে (Ctrl+T)।

---

## TUI

familiar-ai একটি টার্মিনাল UI অন্তর্ভুক্ত করে যা [Textual](https://textual.textualize.io/) দিয়ে তৈরি:

--live স্ট্রিমিং টেক্সট সহ স্ক্রলযোগ্য কথোপকথনের ইতিহাস
- `/quit`, `/clear` এর জন্য ট্যাব-সম্পূর্ণতা
- এজেন্টের চিন্তা করার সময় টাইপ করে তাকে মাঝখানে বাধা দেওয়া
- **কথোপকথনের লগ** স্বয়ংক্রিয়ভাবে `~/.cache/familiar-ai/chat.log` এ সংরক্ষিত

অন্য টার্মিনালে লগ অনুসরণ করতে (কপি-পেস্টের জন্য উপকারী):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

আপনার পরিচিতির ব্যক্তিত্ব `ME.md` এ বিদ্যমান। এই ফাইলটি gitignored — এটি আপনার একার।

একটি উদাহরণের জন্য দেখুন [`persona-template/en.md`](./persona-template/en.md), অথবা জাপানি সংস্করণের জন্য [`persona-template/ja.md`](./persona-template/ja.md)।

---

## FAQ

**Q: এটি কি GPU ছাড়া কাজ করে?**
হ্যাঁ। এম্বেডিং মডেল (multilingual-e5-small) CPU তে ভালভাবে চলে। একটি GPU এটি দ্রুত করে কিন্তু তা অপরিহার্য নয়।

**Q: আমি কি Tapo ছাড়া অন্য কোন ক্যামেরা ব্যবহার করতে পারি?**
যে কোনও ক্যামেরা যা ONVIF + RTSP সমর্থন করে তা কাজ করা উচিত। Tapo C220-এ আমরা পরীক্ষার জন্য ব্যবহৃত করেছি।

**Q: আমার ডেটা কি কোথাও পাঠানো হয়?**
ছবি এবং পাঠ্য আপনার নির্বাচিত LLM API তে প্রক্রিয়াকরণের জন্য পাঠানো হয়। স্মৃতিগুলি স্থানীয়ভাবে `~/.familiar_ai/` এ সংরক্ষিত হয়।

**Q: এজেন্ট `（...）` লেখে কেন কথা বলেনা?**
নিশ্চিত করুন যে `ELEVENLABS_API_KEY` সেট আছে। এটি ছাড়া, ভয়েস নিষ্ক্রিয় হয় এবং এজেন্টটি পাঠ্যতে ফিরে যায়।

## প্রযুক্তিগত পটভূমি

এটি কীভাবে কাজ করে তা জানার আগ্রহী? familiar-ai এর পিছনে গবেষণা এবং ডিজাইন সিদ্ধান্তগুলি দেখুন [docs/technical.md](./docs/technical.md) — ReAct, SayCan, Reflexion, Voyager, স্বার্থের ব্যবস্থা, এবং আরও অনেক কিছু।

---

## অবদান

familiar-ai একটি উন্মুক্তExperiment। যদি এর মধ্যে কিছু আপনার জন্য প্রাসঙ্গিক হয় — প্রযুক্তিগত বা দার্শনিকভাবে — অবদান খুবই স্বাগত।

**শুরু করার জন্য ভাল জায়গা:**

| এলাকা | কী প্রয়োজন |
|------|---------------|
| নতুন হার্ডওয়্যার | আরও ক্যামেরার (RTSP, IP Webcam), মাইক্রোফোন, একচেটিয়া সমর্থন |
| নতুন সরঞ্জাম | ওয়েব অনুসন্ধান, বাড়ির অটোমেশন, ক্যালেন্ডার, MCP এর মাধ্যমে কিছু |
| নতুন ব্যাকএন্ড | যে কোনও LLM বা স্থানীয় মডেল যা `stream_turn` ইন্টারফেসে ফিট করে |
| পরিচয় টেমপ্লেট | বিভিন্ন ভাষা এবং ব্যক্তিত্বের জন্য ME.md টেমপ্লেট |
| গবেষণা | আরও ভাল ইচ্ছার মডেল, স্মৃতি পুনরুদ্ধার, মনোরীতি প্রম্পটিং |
| ডকুমেন্টেশন | টিউটোরিয়াল, গাইড, অনুবাদ |

ডেভেলপমেন্ট সেটআপ, কোড শৈলী এবং PR নির্দেশিকার জন্য [CONTRIBUTING.md](./CONTRIBUTING.md) দেখুন।

যদি আপনি নিশ্চিত না হন কোথায় শুরু করবেন, তবে [একটি সমস্যা খুলুন](https://github.com/lifemate-ai/familiar-ai/issues) — আপনাকে সঠিক পথের দিকে নির্দেশ দিতে পেরে খুশি হব।

---

## লাইসেন্স

[MIT](./LICENSE)
```
