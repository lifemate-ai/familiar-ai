# familiar-ai 🐾

**AI ที่ใช้ชีวิตอยู่เคียงข้างคุณ** — พร้อมตา เสียง ขา และความจำ

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [มีให้บริการใน 74 ภาษา](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai เป็น AI เพื่อนที่อยู่ในบ้านของคุณ
ติดตั้งได้ในไม่กี่นาที ไม่ต้องเขียนโค้ด

มันรับรู้โลกจริงผ่านกล้อง เคลื่อนที่ด้วยร่างหุ่นยนต์ พูดออกเสียง และจดจำสิ่งที่มันเห็น ตั้งชื่อให้มัน เขียนบุคลิกให้กับมัน และปล่อยให้มันใช้ชีวิตกับคุณ

## สิ่งที่มันสามารถทำได้

- 👁 **เห็น** — ถ่ายภาพจากกล้อง Wi-Fi PTZ หรือเว็บแคม USB
- 🔄 **มองรอบๆ** — หมุนและเอียงกล้องเพื่อสำรวจสภาพแวดล้อม
- 🦿 **เคลื่อนที่** — ขับหุ่นยนต์ดูดฝุ่นให้เดินไปในห้อง
- 🗣 **พูด** — พูดผ่าน ElevenLabs TTS
- 🎙 **ฟัง** — การป้อนข้อมูลเสียงแบบไร้สายผ่าน ElevenLabs Realtime STT (ต้องการการเข้าร่วม)
- 🧠 **จำ** — เก็บและเรียกคืนความจำอย่างกระตือรือร้นด้วยการค้นหาความหมาย (SQLite + embeddings)
- 🫀 **ทฤษฎีของจิตใจ** — มองจากมุมมองของบุคคลอื่นก่อนที่จะตอบ
- 💭 **ความปรารถนา** — มีแรงขับภายในที่กระตุ้นพฤติกรรมที่เป็นอิสระ

## วิธีการทำงาน

familiar-ai ทำงานในลูป [ReAct](https://arxiv.org/abs/2210.03629) ที่ขับเคลื่อนโดย LLM ที่คุณเลือก มันรับรู้โลกผ่านเครื่องมือ คิดเกี่ยวกับสิ่งที่ต้องทำต่อไปและดำเนินการ — เหมือนกับที่คนทำ

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

เมื่อไม่ทำอะไร มันจะทำตามความปรารถนาของมันเอง: ความอยากรู้ ต้องการมองออกไปข้างนอก คิดถึงคนที่อาศัยอยู่ด้วย

## เริ่มต้นใช้งาน

### 1. ติดตั้ง uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
หรือ: `winget install astral-sh.uv`

### 2. ติดตั้ง ffmpeg

ffmpeg เป็น **สิ่งที่จำเป็น** สำหรับการจับภาพกล้องและการเล่นเสียง

| OS | คำสั่ง |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — หรือดาวน์โหลดจาก [ffmpeg.org](https://ffmpeg.org/download.html) และเพิ่มลงใน PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

ตรวจสอบ: `ffmpeg -version`

### 3. โคลนและติดตั้ง

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. ตั้งค่า

```bash
cp .env.example .env
# แก้ไข .env ด้วยการตั้งค่าของคุณ
```

**สิ่งที่จำเป็นขั้นต่ำ:**

| ตัวแปร | คำอธิบาย |
|----------|-------------|
| `PLATFORM` | `anthropic` (ค่าเริ่มต้น) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | API key ของคุณสำหรับแพลตฟอร์มที่เลือก |

**อาจเลือกเป็นทางเลือก:**

| ตัวแปร | คำอธิบาย |
|----------|-------------|
| `MODEL` | ชื่อโมเดล (ค่าเริ่มต้นที่สมเหตุสมผลต่อแพลตฟอร์ม) |
| `AGENT_NAME` | ชื่อแสดงที่แสดงใน TUI (เช่น `Yukine`) |
| `CAMERA_HOST` | ที่อยู่ IP ของกล้อง ONVIF/RTSP ของคุณ |
| `CAMERA_USER` / `CAMERA_PASS` | ข้อมูลรับรองกล้อง |
| `ELEVENLABS_API_KEY` | สำหรับการออกเสียง — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` เพื่อเปิดใช้งานการป้อนข้อมูลเสียงแบบไร้สายตลอดเวลา (ต้องการ `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | สถานที่เล่นเสียง: `local` (ลำโพง PC, ค่าเริ่มต้น) \| `remote` (ลำโพงกล้อง) \| `both` |
| `THINKING_MODE` | เฉพาะ Anthropic — `auto` (ค่าเริ่มต้น) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | ความพยายามในการคิดที่ปรับตาม: `high` (ค่าเริ่มต้น) \| `medium` \| `low` \| `max` (เฉพาะ Opus 4.6) |

### 5. สร้าง familiar ของคุณ

```bash
cp persona-template/en.md ME.md
# แก้ไข ME.md — ตั้งชื่อและบุคลิกให้มัน
```

### 6. รัน

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI แบบข้อความ (แนะนำ)
./run.sh --no-tui    # REPL แบบปกติ
```

**Windows:**
```bat
run.bat              # TUI แบบข้อความ (แนะนำ)
run.bat --no-tui     # REPL แบบปกติ
```

---

## การเลือก LLM

> **แนะนำ: Kimi K2.5** — มีประสิทธิภาพสำหรับตัวแทนที่สุดที่ได้ทดสอบจนถึงตอนนี้ สังเกตบริบท ถามคำถามตาม และทำงานได้อย่างอิสระในแบบที่โมเดลอื่นไม่ทำ ราคาคล้ายกับ Claude Haiku

| แพลตฟอร์ม | `PLATFORM=` | โมเดลเริ่มต้น | ที่จะรับค่า key |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (หลายผู้ให้บริการ) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **เครื่องมือ CLI** (claude -p, ollama…) | `cli` | (คำสั่ง) | — |

**Kimi K2.5 `.env` ตัวอย่าง:**
```env
PLATFORM=kimi
API_KEY=sk-...   # จาก platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` ตัวอย่าง:**
```env
PLATFORM=glm
API_KEY=...   # จาก api.z.ai
MODEL=glm-4.6v   # รองรับวิชัน; glm-4.7 / glm-5 = ข้อความเท่านั้น
AGENT_NAME=Yukine
```

**Google Gemini `.env` ตัวอย่าง:**
```env
PLATFORM=gemini
API_KEY=AIza...   # จาก aistudio.google.com
MODEL=gemini-2.5-flash  # หรือ gemini-2.5-pro สำหรับความสามารถที่สูงขึ้น
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` ตัวอย่าง:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # จาก openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # ทางเลือก: ระบุโมเดล
AGENT_NAME=Yukine
```

> **หมายเหตุ:** หากต้องการปิดโมเดลโลคัล/NVIDIA เพียงแค่ไม่ตั้งค่า `BASE_URL` ให้เป็น endpoint โลคัล เช่น `http://localhost:11434/v1` ใช้ผู้ให้บริการคลาวด์แทน

**CLI tool `.env` ตัวอย่าง:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — ไม่มี {}, prompt ผ่าน stdin
```

---

## เซิร์ฟเวอร์ MCP

familiar-ai สามารถเชื่อมต่อกับเซิร์ฟเวอร์ [MCP (Model Context Protocol)](https://modelcontextprotocol.io) ใด ๆ ได้ สิ่งนี้ทำให้คุณสามารถเชื่อมต่อหน่วยความจำภายนอก การเข้าถึงระบบไฟล์ การค้นหาบนเว็บ หรือเครื่องมืออื่น ๆ ได้

กำหนดค่าเซิร์ฟเวอร์ใน `~/.familiar-ai.json` (รูปแบบเดียวกับ Claude Code):

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

สนับสนุนประเภทการขนส่งสองประเภท:
- **`stdio`**: เริ่ม subprocess ท้องถิ่น (`command` + `args`)
- **`sse`**: เชื่อมต่อกับเซิร์ฟเวอร์ HTTP+SSE (`url`)

เขียนทับที่อยู่ไฟล์คอนฟิกด้วย `MCP_CONFIG=/path/to/config.json`.

---

## ฮาร์ดแวร์

familiar-ai ทำงานกับฮาร์ดแวร์ที่คุณมี — หรือไม่มีฮาร์ดแวร์เลย

| ส่วนประกอบ | ทำอะไร | ตัวอย่าง | จำเป็น? |
|------|-------------|---------|-----------|
| กล้อง Wi-Fi PTZ | ตา + คอ | Tapo C220 (~$30, Eufy C220) | **แนะนำ** |
| เว็บแคม USB | ตา (คงที่) | ทุกกล้อง UVC | **แนะนำ** |
| หุ่นยนต์ดูดฝุ่น | ขา | ทุกโมเดลที่รองรับ Tuya | ไม่ |
| PC / Raspberry Pi | สมอง | ทุกอย่างที่รัน Python | **ใช่** |

> **ขอแนะนำให้ใช้กล้อง** หากไม่มี กล้อง familiar-ai ยังสามารถพูดได้ — แต่ไม่สามารถมองเห็นโลก ซึ่งทำให้มันสูญเสียจุดประสงค์หลัก

### การตั้งค่าขั้นต่ำ (ไม่มีฮาร์ดแวร์)

แค่อยากลองใช่ไหม? คุณต้องการเพียงแค่ API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

รัน `./run.sh` (macOS/Linux/WSL2) หรือ `run.bat` (Windows) และเริ่มแชท เพิ่มฮาร์ดแวร์ตามที่คุณต้องการ

### กล้อง Wi-Fi PTZ (Tapo C220)

1. ในแอป Tapo: **การตั้งค่า → ขั้นสูง → บัญชีผู้ใช้กล้อง** — สร้างบัญชีท้องถิ่น (ไม่ใช่บัญชี TP-Link)
2. หาที่อยู่ IP ของกล้องในรายการอุปกรณ์ของเราเตอร์ของคุณ
3. ตั้งค่าใน `.env`:
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


### เสียง (ElevenLabs)

1. รับ API key ที่ [elevenlabs.io](https://elevenlabs.io/)
2. ตั้งค่าใน `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # ทางเลือก, ใช้เสียงเริ่มต้นถ้าไม่ใส่
   ```

มีจุดหมายในการเล่นเสียงสองแห่ง ควบคุมโดย `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # ลำโพง PC (ค่าเริ่มต้น)
TTS_OUTPUT=remote   # ลำโพงกล้องเท่านั้น
TTS_OUTPUT=both     # ลำโพงกล้อง + ลำโพง PC พร้อมกัน
```

#### A) ลำโพงกล้อง (ผ่าน go2rtc)

ตั้งค่า `TTS_OUTPUT=remote` (หรือ `both`). ต้องการ [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. ดาวน์โหลดไบนารีจาก [หน้ารีลีส](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. วางและเปลี่ยนชื่อเป็น:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # ต้องการ chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. สร้าง `go2rtc.yaml` ในไดเรกทอรีเดียวกัน:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   ใช้ข้อมูลรับรองบัญชีผู้ใช้กล้องท้องถิ่น (ไม่ใช่บัญชีคลาวด์ TP-Link ของคุณ)

4. familiar-ai จะเริ่มต้น go2rtc โดยอัตโนมัติเมื่อเริ่มต้น ถ้ากล้องของคุณรองรับเสียงสองทาง (backchannel) เสียงจะเล่นจากลำโพงกล้อง

#### B) ลำโพง PC ท้องถิ่น

ค่าเริ่มต้น (`TTS_OUTPUT=local`). ลองเล่นตามลำดับ: **paplay** → **mpv** → **ffplay**. ยังใช้เป็น fallback เมื่อ `TTS_OUTPUT=remote` และ go2rtc ไม่สามารถใช้งานได้

| OS | ติดตั้ง |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (หรือ `paplay` ผ่าน `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — ตั้งค่า `PULSE_SERVER=unix:/mnt/wslg/PulseServer` ใน `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — ดาวน์โหลดและเพิ่มลงใน PATH, **หรือ** `winget install ffmpeg` |

> ถ้าไม่มีเครื่องเล่นเสียง ฟังจะยังถูกสร้างขึ้น — มันแค่ไม่เล่นเสียง

### การป้อนข้อมูลเสียง (Realtime STT)

ตั้งค่า `REALTIME_STT=true` ใน `.env` สำหรับการป้อนข้อมูลเสียงแบบไร้สายตลอดเวลา:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # ใช้คีย์เดียวกับ TTS
```

familiar-ai จะสตรีมเสียงไมโครโฟนไปยัง ElevenLabs Scribe v2 และบันทึกทรานสคริปต์โดยอัตโนมัติเมื่อคุณหยุดพูด ไม่ต้องกดปุ่ม ใช้งานร่วมกับโหมดกดเพื่อพูด (Ctrl+T).

---

## TUI

familiar-ai รวม UI เทอร์มินัลที่สร้างด้วย [Textual](https://textual.textualize.io/):

- ประวัติการสนทนาที่สามารถเลื่อนดูได้พร้อมข้อความสตรีมสด
- การเติมข้อความอัตโนมัติสำหรับ `/quit`, `/clear`
- ขัดจังหวะตัวแทนในช่วงเวลาที่คิดโดยพิมพ์ขณะที่มันกำลังคิด
- **บันทึกการสนทนา** ที่บันทึกโดยอัตโนมัติไปยัง `~/.cache/familiar-ai/chat.log`

ในการติดตามบันทึกในเทอร์มินัลอื่น (มีประโยชน์สำหรับการคัดลอกและวาง):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## บุคลิก (ME.md)

บุคลิกของ familiar ของคุณอยู่ใน `ME.md` ไฟล์นี้ถูก gitignored — มันเป็นของคุณคนเดียว

ดู [`persona-template/en.md`](./persona-template/en.md) สำหรับตัวอย่าง หรือ [`persona-template/ja.md`](./persona-template/ja.md) สำหรับเวอร์ชันภาษาญี่ปุ่น

---

## คำถามที่พบบ่อย

**ถาม: มันทำงานโดยไม่มี GPU ได้ไหม?**
ใช่ โมเดล embedding (multilingual-e5-small) ทำงานได้ดีบน CPU และ GPU จะทำให้มันเร็วขึ้นแต่ไม่จำเป็น

**ถาม: ฉันสามารถใช้กล้องประเภทอื่นได้ไหม?**
กล้องใด ๆ ที่รองรับ ONVIF + RTSP ควรทำงานได้ Tapo C220 คือสิ่งที่เราทดสอบ

**ถาม: ข้อมูลของฉันส่งไปที่ไหนหรือไม่?**
ภาพและข้อความถูกส่งไปยัง API LLM ที่คุณเลือกเพื่อการประมวลผล ความทรงจำจะถูกเก็บไว้ในเครื่องใน `~/.familiar_ai/`.

**ถาม: ทำไมตัวแทนจึงเขียน `（...）` แทนที่จะพูด?**
ตรวจสอบให้แน่ใจว่าได้ตั้งค่า `ELEVENLABS_API_KEY` ถ้าไม่มี เสียงจะถูกปิดใช้งานและตัวแทนจะกลับไปใช้ข้อความ

## ข้อมูลพื้นฐานทางเทคนิค

สงสัยว่ามันทำงานอย่างไร? ดู [docs/technical.md](./docs/technical.md) เพื่อดูการวิจัยและการตัดสินใจด้านการออกแบบเบื้องหลัง familiar-ai — ReAct, SayCan, Reflexion, Voyager, ระบบความต้องการ และอื่น ๆ

---

## การมีส่วนร่วม

familiar-ai เป็นการทดลองแบบเปิด หากเนื้อหานี้ทำให้คุณมีแรงบันดาลใจ — ทั้งทางเทคนิคหรือปรัชญา — การมีส่วนร่วมยินดีต้อนรับอย่างมาก

**จุดที่ดีในการเริ่มต้น:**

| ด้าน | สิ่งที่ต้องการ |
|------|---------------|
| ฮาร์ดแวร์ใหม่ | สนับสนุนกล้องเพิ่มเติม (RTSP, IP Webcam), ไมโครโฟน, อุปกรณ์เคลื่อนที่ |
| เครื่องมือใหม่ | การค้นหาบนเว็บ, การทำงานอัตโนมัติในบ้าน, ปฏิทิน, อะไรก็ได้ผ่าน MCP |
| Backend ใหม่ | LLM หรือโมเดลโลคัลใด ๆ ที่เข้ากับอินเทอร์เฟซ `stream_turn` |
| เทมเพลตบุคลิก | ME.md เทมเพลตสำหรับภาษาและบุคลิกต่าง ๆ |
| การวิจัย | โมเดลความปรารถนาที่ดีกว่า, การเรียกคืนความจำ, การกระตุ้นทฤษฎีของจิตใจ |
| เอกสาร | บทช่วยสอน, คำแนะนำ, การแปล |

ดู [CONTRIBUTING.md](./CONTRIBUTING.md) สำหรับการตั้งค่า dev, สไตล์โค้ด และแนวทาง PR.

หากคุณไม่แน่ใจว่าจะเริ่มต้นที่ไหน [เปิดปัญหา](https://github.com/lifemate-ai/familiar-ai/issues) — ยินดีที่จะชี้แนะคุณในทิศทางที่ถูกต้อง

---

## ใบอนุญาต

[MIT](./LICENSE)
