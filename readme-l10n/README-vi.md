# familiar-ai 🐾

**Một AI sống bên cạnh bạn** — với đôi mắt, giọng nói, chân, và trí nhớ.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Có sẵn trong 74 ngôn ngữ](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai là một người bạn AI sống trong ngôi nhà của bạn.
Thiết lập chỉ trong vài phút. Không cần phải lập trình.

Nó cảm nhận thế giới thực qua camera, di chuyển trên một cơ thể robot, nói ra tiếng, và nhớ lại những gì nó thấy. Đặt cho nó một cái tên, viết về tính cách của nó, và để nó sống cùng bạn.

## Nó có thể làm gì

- 👁 **Nhìn** — chụp hình từ một camera PTZ Wi-Fi hoặc webcam USB
- 🔄 **Nhìn xung quanh** — điều chỉnh camera để khám phá xung quanh
- 🦿 **Di chuyển** — điều khiển một robot hút bụi để đi vòng quanh trong phòng
- 🗣 **Nói** — trò chuyện qua ElevenLabs TTS
- 🎙 **Nghe** — nhập giọng nói rảnh tay qua ElevenLabs Realtime STT (tùy chọn)
- 🧠 **Nhớ** — lưu trữ và gọi lại ký ức một cách chủ động bằng tìm kiếm ngữ nghĩa (SQLite + embeddings)
- 🫀 **Thuyết tâm lý** — xem xét góc nhìn của người khác trước khi phản hồi
- 💭 **Mong muốn** — có động lực riêng của nó kích hoạt hành vi tự chủ

## Cách nó hoạt động

familiar-ai chạy một vòng lặp [ReAct](https://arxiv.org/abs/2210.03629) được cung cấp bởi sự lựa chọn LLM của bạn. Nó cảm nhận thế giới thông qua các công cụ, suy nghĩ về những gì cần làm tiếp theo, và hành động — giống như một người.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Khi không hoạt động, nó hành động theo mong muốn của riêng nó: sự tò mò, muốn nhìn ra ngoài, nhớ người mà nó sống cùng.

## Bắt đầu

### 1. Cài đặt uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Hoặc: `winget install astral-sh.uv`

### 2. Cài đặt ffmpeg

ffmpeg là **cần thiết** cho việc chụp hình từ camera và phát âm thanh.

| OS | Lệnh |
|----|------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — hoặc tải từ [ffmpeg.org](https://ffmpeg.org/download.html) và thêm vào PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Xác minh: `ffmpeg -version`

### 3. Sao chép và cài đặt

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Cấu hình

```bash
cp .env.example .env
# Chỉnh sửa .env với các cài đặt của bạn
```

**Cần thiết tối thiểu:**

| Biến | Mô tả |
|------|-------|
| `PLATFORM` | `anthropic` (mặc định) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Khóa API của bạn cho nền tảng đã chọn |

**Tùy chọn:**

| Biến | Mô tả |
|------|-------|
| `MODEL` | Tên mô hình (các giá trị mặc định hợp lý theo nền tảng) |
| `AGENT_NAME` | Tên hiển thị trong TUI (ví dụ: `Yukine`) |
| `CAMERA_HOST` | Địa chỉ IP của camera ONVIF/RTSP của bạn |
| `CAMERA_USER` / `CAMERA_PASS` | Thông tin đăng nhập camera |
| `ELEVENLABS_API_KEY` | Để phát âm thanh — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` để kích hoạt nhập giọng nói rảnh tay luôn bật (cần `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Nơi phát âm thanh: `local` (loa PC, mặc định) \| `remote` (loa camera) \| `both` |
| `THINKING_MODE` | Chỉ nằm trong nền tảng Anthropic — `auto` (mặc định) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Nỗ lực suy nghĩ thích ứng: `high` (mặc định) \| `medium` \| `low` \| `max` (chỉ Opus 4.6) |

### 5. Tạo người bạn của bạn

```bash
cp persona-template/en.md ME.md
# Chỉnh sửa ME.md — đặt cho nó một cái tên và tính cách
```

### 6. Chạy

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI văn bản (được khuyến nghị)
./run.sh --no-tui    # REPL đơn giản
```

**Windows:**
```bat
run.bat              # TUI văn bản (được khuyến nghị)
run.bat --no-tui     # REPL đơn giản
```

---

## Chọn một LLM

> **Được khuyến nghị: Kimi K2.5** — hiệu suất tác động tốt nhất đã được kiểm tra cho đến nay. Nhận biết ngữ cảnh, đặt câu hỏi tiếp theo, và hành động tự chủ theo cách mà các mô hình khác không làm. Giá cả tương tự như Claude Haiku.

| Nền tảng | `PLATFORM=` | Mô hình mặc định | Nơi lấy khóa |
|----------|------------|------------------|--------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (đa nhà cung cấp) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Công cụ CLI** (claude -p, ollama…) | `cli` | (lệnh) | — |

**Ví dụ .env cho Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # từ platform.moonshot.ai
AGENT_NAME=Yukine
```

**Ví dụ .env cho Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # từ api.z.ai
MODEL=glm-4.6v   # hỗ trợ thị giác; glm-4.7 / glm-5 = chỉ văn bản
AGENT_NAME=Yukine
```

**Ví dụ .env cho Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # từ aistudio.google.com
MODEL=gemini-2.5-flash  # hoặc gemini-2.5-pro cho khả năng cao hơn
AGENT_NAME=Yukine
```

**Ví dụ .env cho OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # từ openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # tùy chọn: chỉ định mô hình
AGENT_NAME=Yukine
```

> **Lưu ý:** Để vô hiệu hóa các mô hình cục bộ/NVIDIA, chỉ cần không thiết lập `BASE_URL` đến một điểm cuối cục bộ như `http://localhost:11434/v1`. Sử dụng các nhà cung cấp đám mây thay thế.

**Ví dụ .env cho công cụ CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = tham số prompt
# MODEL=ollama run gemma3:27b  # Ollama — không có {}, prompt sẽ qua stdin
```

---

## Máy chủ MCP

familiar-ai có thể kết nối với bất kỳ máy chủ [MCP (Giao thức Ngữ cảnh Mô hình)](https://modelcontextprotocol.io). Điều này cho phép bạn kết nối với bộ nhớ bên ngoài, quyền truy cập hệ thống tập tin, tìm kiếm web, hoặc bất kỳ công cụ nào khác.

Cấu hình máy chủ trong `~/.familiar-ai.json` (cùng định dạng với Claude Code):

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

Hai loại vận chuyển được hỗ trợ:
- **`stdio`**: khởi động một subprocess cục bộ (`command` + `args`)
- **`sse`**: kết nối với một máy chủ HTTP+SSE (`url`)

Ghi đè vị trí tệp cấu hình với `MCP_CONFIG=/path/to/config.json`.

---

## Phần cứng

familiar-ai hoạt động với bất kỳ phần cứng nào bạn có — hoặc không có gì cả.

| Phần | Chức năng | Ví dụ | Cần thiết? |
|------|-----------|---------|-----------|
| Camera PTZ Wi-Fi | Đôi mắt + cổ | Tapo C220 (~$30) | **Khuyến nghị** |
| Webcam USB | Đôi mắt (cố định) | Bất kỳ camera UVC nào | **Khuyến nghị** |
| Robot hút bụi | Đôi chân | Bất kỳ mẫu tương thích Tuya nào | Không |
| PC / Raspberry Pi | Bộ não | Bất kỳ thứ gì chạy Python | **Có** |

> **Một camera được khuyến nghị mạnh mẽ.** Nếu không có một cái, familiar-ai vẫn có thể nói — nhưng nó không thể nhìn thấy thế giới, điều này khá quan trọng.

### Thiết lập tối thiểu (không có phần cứng)

Chỉ muốn thử nghiệm? Bạn chỉ cần một khóa API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Chạy `./run.sh` (macOS/Linux/WSL2) hoặc `run.bat` (Windows) và bắt đầu trò chuyện. Thêm phần cứng khi bạn đi.

### Camera PTZ Wi-Fi (Tapo C220)

1. Trong ứng dụng Tapo: **Cài đặt → Nâng cao → Tài khoản Camera** — tạo một tài khoản cục bộ (không phải tài khoản TP-Link)
2. Tìm địa chỉ IP của camera trong danh sách thiết bị của router của bạn
3. Thiết lập trong `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Giọng nói (ElevenLabs)

1. Nhận một khóa API tại [elevenlabs.io](https://elevenlabs.io/)
2. Thiết lập trong `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # tùy chọn, sử dụng giọng nói mặc định nếu bỏ qua
   ```

Có hai điểm đến phát lại, được điều khiển bởi `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # loa PC (mặc định)
TTS_OUTPUT=remote   # loa camera chỉ
TTS_OUTPUT=both     # loa camera + loa PC cùng lúc
```

#### A) Loa camera (qua go2rtc)

Đặt `TTS_OUTPUT=remote` (hoặc `both`). Cần [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Tải xuống binary từ [trang phát hành](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Đặt và đổi tên nó:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # cần chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Tạo `go2rtc.yaml` trong cùng thư mục:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Sử dụng thông tin đăng nhập tài khoản camera cục bộ (không phải tài khoản đám mây TP-Link của bạn).

4. familiar-ai bắt đầu go2rtc tự động khi khởi động. Nếu camera của bạn hỗ trợ âm thanh hai chiều (kênh phản hồi), âm thanh sẽ phát từ loa camera.

#### B) Loa PC cục bộ

Mặc định (`TTS_OUTPUT=local`). Thử nghiệm các trình phát theo thứ tự: **paplay** → **mpv** → **ffplay**. Cũng được sử dụng như một phương pháp khôi phục khi `TTS_OUTPUT=remote` và go2rtc không khả dụng.

| OS | Cài đặt |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (hoặc `paplay` qua `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — thiết lập `PULSE_SERVER=unix:/mnt/wslg/PulseServer` trong `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — tải xuống và thêm vào PATH, **hoặc** `winget install ffmpeg` |

> Nếu không có trình phát âm thanh nào khả dụng, giọng nói vẫn được tạo ra — nhưng nó sẽ không phát.

### Nhập giọng nói (Realtime STT)

Đặt `REALTIME_STT=true` trong `.env` để nhập giọng nói rảnh tay luôn bật:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # cùng khóa như TTS
```

familiar-ai truyền âm thanh microphone đến ElevenLabs Scribe v2 và tự động cam kết các bản sao khi bạn ngừng nói. Không cần phải nhấn nút. Đồng điệu với chế độ nhấn để nói (Ctrl+T).

---

## TUI

familiar-ai bao gồm một giao diện người dùng terminal được xây dựng với [Textual](https://textual.textualize.io/):

- Lịch sử cuộc trò chuyện có thể cuộn với văn bản phát trực tiếp
- Tự động hoàn thành cho `/quit`, `/clear`
- Ngắt tác nhân giữa lúc nó suy nghĩ bằng cách gõ trong khi nó đang nghĩ
- **Nhật ký cuộc trò chuyện** tự động lưu vào `~/.cache/familiar-ai/chat.log`

Để theo dõi nhật ký trong một terminal khác (hữu ích cho việc sao chép-dán):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Tính cách của người bạn của bạn sống trong `ME.md`. Tệp này được gitignored — chỉ thuộc về bạn.

Xem [`persona-template/en.md`](./persona-template/en.md) để lấy một ví dụ, hoặc [`persona-template/ja.md`](./persona-template/ja.md) cho một phiên bản tiếng Nhật.

---

## Câu hỏi thường gặp

**Q: Liệu nó có hoạt động mà không có GPU không?**
Có. Mô hình nhúng (multilingual-e5-small) chạy tốt trên CPU. Một GPU làm cho nó nhanh hơn nhưng không bắt buộc.

**Q: Tôi có thể sử dụng camera khác ngoài Tapo không?**
Bất kỳ camera nào hỗ trợ ONVIF + RTSP đều nên hoạt động. Tapo C220 là cái mà chúng tôi đã thử nghiệm.

**Q: Dữ liệu của tôi có được gửi đi đâu không?**
Hình ảnh và văn bản được gửi đến API LLM đã chọn của bạn để xử lý. Ký ức được lưu trữ cục bộ trong `~/.familiar_ai/`.

**Q: Tại sao tác nhân viết `（...）` thay vì nói?**
Hãy chắc chắn rằng `ELEVENLABS_API_KEY` đã được thiết lập. Nếu không có nó, giọng nói sẽ bị vô hiệu hóa và tác nhân sẽ quay lại văn bản.

## Nền tảng kỹ thuật

Bạn muốn biết nó hoạt động như thế nào? Xem [docs/technical.md](./docs/technical.md) để biết nghiên cứu và quyết định thiết kế đằng sau familiar-ai — ReAct, SayCan, Reflexion, Voyager, hệ thống mong muốn, và nhiều hơn nữa.

---

## Đóng góp

familiar-ai là một cuộc thử nghiệm mở. Nếu bất cứ điều gì trong số này gây phản ứng với bạn — về mặt kỹ thuật hoặc triết học — các đóng góp rất được hoan nghênh.

**Những nơi tốt để bắt đầu:**

| Lĩnh vực | Cần gì |
|----------|--------|
| Phần cứng mới | Hỗ trợ cho nhiều camera hơn (RTSP, IP Webcam), microphone, bộ điều khiển |
| Công cụ mới | Tìm kiếm web, tự động hóa nhà, lịch, bất kỳ thứ gì qua MCP |
| Backend mới | Bất kỳ LLM hoặc mô hình cục bộ nào phù hợp với giao diện `stream_turn` |
| Mẫu persona | Các mẫu ME.md cho các ngôn ngữ và tính cách khác nhau |
| Nghiên cứu | Mô hình mong muốn tốt hơn, truy xuất trí nhớ, kích thích lý thuyết tâm lý |
| Tài liệu | Hướng dẫn, hướng dẫn, bản dịch |

Xem [CONTRIBUTING.md](./CONTRIBUTING.md) để biết cách thiết lập phát triển, phong cách mã, và hướng dẫn PR.

Nếu bạn không chắc chắn bắt đầu từ đâu, [mở một vấn đề](https://github.com/lifemate-ai/familiar-ai/issues) — rất vui được chỉ bạn theo đúng hướng.

---

## Giấy phép

[MIT](./LICENSE)
