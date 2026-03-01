```markdown
# familiar-ai 🐾

**Một AI sống bên cạnh bạn** — với đôi mắt, giọng nói, đôi chân và trí nhớ.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai là một người bạn AI sống trong ngôi nhà của bạn.
Cài đặt trong vài phút. Không cần mã hóa.

Nó nhận biết thế giới thực thông qua các camera, di chuyển trên một thân robot, nói ra và nhớ những gì nó thấy. Đặt cho nó một cái tên, viết nên tính cách của nó, và để nó sống cùng bạn.

## Những gì nó có thể làm

- 👁 **Nhìn thấy** — chụp hình từ camera PTZ Wi-Fi hoặc webcam USB
- 🔄 **Nhìn xung quanh** — xoay và nghiêng camera để khám phá xung quanh
- 🦿 **Di chuyển** — điều khiển một robot hút bụi để đi lang thang trong phòng
- 🗣 **Nói** — trò chuyện qua ElevenLabs TTS
- 🎙 **Nghe** — đầu vào giọng nói rảnh tay qua ElevenLabs Realtime STT (tùy chọn)
- 🧠 **Nhớ** — chủ động lưu trữ và gọi lại kỷ niệm với tìm kiếm ngữ nghĩa (SQLite + embeddings)
- 🫀 **Lý thuyết về tâm trí** — nhìn nhận từ góc độ của người khác trước khi trả lời
- 💭 **Khao khát** — có những động lực nội tại riêng để kích hoạt hành vi tự chủ

## Cách thức hoạt động

familiar-ai chạy một vòng lặp [ReAct](https://arxiv.org/abs/2210.03629) được cung cấp bởi lựa chọn LLM của bạn. Nó nhận biết thế giới thông qua các công cụ, suy nghĩ về việc tiếp theo nên làm gì, và hành động — giống như một người.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Khi nhàn rỗi, nó hành động dựa trên những khao khát của chính nó: tò mò, muốn nhìn ra ngoài, nhớ về người mà nó sống cùng.

## Bắt đầu

### 1. Cài đặt uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Cài đặt ffmpeg

ffmpeg là **cần thiết** để chụp hình từ camera và phát âm thanh.

| Hệ điều hành | Lệnh |
|--------------|------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — hoặc tải về từ [ffmpeg.org](https://ffmpeg.org/download.html) và thêm vào PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Xác minh: `ffmpeg -version`

### 3. Nhân bản và cài đặt

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Cấu hình

```bash
cp .env.example .env
# Sửa đổi .env với các thiết lập của bạn
```

**Yêu cầu tối thiểu:**

| Biến | Mô tả |
|------|-------|
| `PLATFORM` | `anthropic` (mặc định) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Khóa API của bạn cho nền tảng đã chọn |

**Tùy chọn:**

| Biến | Mô tả |
|------|-------|
| `MODEL` | Tên mô hình (mặc định hợp lý theo từng nền tảng) |
| `AGENT_NAME` | Tên hiển thị trong TUI (ví dụ: `Yukine`) |
| `CAMERA_HOST` | Địa chỉ IP của camera ONVIF/RTSP của bạn |
| `CAMERA_USER` / `CAMERA_PASS` | Thông tin xác thực camera |
| `ELEVENLABS_API_KEY` | Để đầu ra giọng nói — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` để kích hoạt đầu vào giọng nói rảnh tay luôn bật (cần `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Địa điểm phát âm thanh: `local` (loa PC, mặc định) \| `remote` (loa camera) \| `both` |
| `THINKING_MODE` | Chỉ áp dụng cho Anthropic — `auto` (mặc định) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Nỗ lực suy nghĩ thích ứng: `high` (mặc định) \| `medium` \| `low` \| `max` (chỉ Opus 4.6) |

### 5. Tạo familiar của bạn

```bash
cp persona-template/en.md ME.md
# Sửa đổi ME.md — đặt cho nó một cái tên và tính cách
```

### 6. Chạy

```bash
./run.sh             # TUI văn bản (được khuyến nghị)
./run.sh --no-tui    # REPL đơn giản
```

---

## Lựa chọn một LLM

> **Khuyến nghị: Kimi K2.5** — hiệu suất tác động tốt nhất cho đến nay. Nhận biết ngữ cảnh, đặt câu hỏi theo dõi, và hành động độc lập theo cách mà các mô hình khác không làm được. Giá tương tự như Claude Haiku.

| Nền tảng | `PLATFORM=` | Mô hình mặc định | Nơi nhận khóa |
|----------|------------|------------------|----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Tương thích OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (đa nhà cung cấp) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Công cụ CLI** (claude -p, ollama…) | `cli` | (lệnh) | — |

**Ví dụ `.env` cho Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # từ platform.moonshot.ai
AGENT_NAME=Yukine
```

**Ví dụ `.env` cho Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # từ api.z.ai
MODEL=glm-4.6v   # có khả năng nhận thức thị giác; glm-4.7 / glm-5 = chỉ văn bản
AGENT_NAME=Yukine
```

**Ví dụ `.env` cho Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # từ aistudio.google.com
MODEL=gemini-2.5-flash  # hoặc gemini-2.5-pro cho khả năng cao hơn
AGENT_NAME=Yukine
```

**Ví dụ `.env` cho OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # từ openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # tùy chọn: chỉ định mô hình
AGENT_NAME=Yukine
```

> **Lưu ý:** Để vô hiệu hóa các mô hình local/NVIDIA, đơn giản là không thiết lập `BASE_URL` thành một điểm cuối local như `http://localhost:11434/v1`. Sử dụng các nhà cung cấp đám mây thay thế.

**Ví dụ `.env` cho công cụ CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = tham số prompt
# MODEL=ollama run gemma3:27b  # Ollama — không có {}, prompt đi qua stdin
```

---

## Máy chủ MCP

familiar-ai có thể kết nối với bất kỳ máy chủ [MCP (Model Context Protocol)](https://modelcontextprotocol.io) nào. Điều này cho phép bạn kết nối bộ nhớ bên ngoài, truy cập hệ thống tệp, tìm kiếm web, hoặc bất kỳ công cụ nào khác.

Cấu hình các máy chủ trong `~/.familiar-ai.json` (định dạng giống như Claude Code):

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

Hai loại phương thức vận chuyển được hỗ trợ:
- **`stdio`**: khởi chạy một subprocess địa phương (`command` + `args`)
- **`sse`**: kết nối đến một máy chủ HTTP+SSE (`url`)

Ghi đè vị trí tệp cấu hình với `MCP_CONFIG=/path/to/config.json`.

---

## Phần cứng

familiar-ai hoạt động với bất kỳ phần cứng nào bạn có — hoặc không có gì cả.

| Bộ phận | Chức năng | Ví dụ | Bắt buộc? |
|---------|-----------|--------|------------|
| Camera PTZ Wi-Fi | Đôi mắt + cổ | Tapo C220 (~$30) | **Khuyến nghị** |
| Webcam USB | Đôi mắt (cố định) | Bất kỳ camera UVC nào | **Khuyến nghị** |
| Robot hút bụi | Đôi chân | Bất kỳ mô hình tương thích Tuya nào | Không |
| PC / Raspberry Pi | Bộ não | Bất kỳ thiết bị nào chạy Python | **Có** |

> **Một camera là rất được khuyến khích.** Nếu không có, familiar-ai vẫn có thể nói — nhưng không thể nhìn thấy thế giới, mà đó là cả ý nghĩa.

### Thiết lập tối thiểu (không có phần cứng)

Chỉ muốn thử? Bạn chỉ cần một khóa API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Chạy `./run.sh` và bắt đầu trò chuyện. Thêm phần cứng khi bạn đi.

### Camera PTZ Wi-Fi (Tapo C220)

1. Trong ứng dụng Tapo: **Cài đặt → Nâng cao → Tài khoản Camera** — tạo một tài khoản cục bộ (không phải tài khoản TP-Link)
2. Tìm địa chỉ IP của camera trong danh sách thiết bị của router
3. Đặt trong `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Giọng nói (ElevenLabs)

1. Lấy một khóa API tại [elevenlabs.io](https://elevenlabs.io/)
2. Đặt trong `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # tùy chọn, sử dụng giọng nói mặc định nếu bỏ qua
   ```

Có hai điểm đến phát âm thanh, được điều chỉnh bởi `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Loa PC (mặc định)
TTS_OUTPUT=remote   # Chỉ loa camera
TTS_OUTPUT=both     # Loa camera + Loa PC đồng thời
```

#### A) Loa camera (qua go2rtc)

Đặt `TTS_OUTPUT=remote` (hoặc `both`). Cần [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Tải về tệp nhị phân từ [trang phát hành](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Đặt và đổi tên:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x yêu cầu

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Tạo `go2rtc.yaml` trong cùng thư mục:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Sử dụng thông tin xác thực tài khoản camera cục bộ (không phải tài khoản đám mây TP-Link của bạn).

4. familiar-ai tự động khởi động go2rtc khi khởi chạy. Nếu camera của bạn hỗ trợ âm thanh hai chiều (kênh ngược), giọng nói sẽ phát từ loa camera.

#### B) Loa PC cục bộ

Mặc định (`TTS_OUTPUT=local`). Cố gắng chơi các trình phát theo thứ tự: **paplay** → **mpv** → **ffplay**. Cũng được sử dụng như một dự phòng khi `TTS_OUTPUT=remote` và go2rtc không khả dụng.

| Hệ điều hành | Cài đặt |
|--------------|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (hoặc `paplay` qua `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — thiết lập `PULSE_SERVER=unix:/mnt/wslg/PulseServer` trong `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — tải về và thêm vào PATH, **hoặc** `winget install ffmpeg` |

> Nếu không có trình phát âm thanh nào khả dụng, giọng nói vẫn được tạo ra — chỉ là không phát âm thanh.

### Đầu vào giọng nói (Realtime STT)

Đặt `REALTIME_STT=true` trong `.env` để có đầu vào giọng nói rảnh tay luôn bật:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # cùng khóa như TTS
```

familiar-ai phát trực tuyến âm thanh từ micrô đến ElevenLabs Scribe v2 và tự động ghi lại văn bản khi bạn dừng nói. Không cần nhấn nút. Cùng tồn tại với chế độ nhấn để nói (Ctrl+T).

---

## TUI

familiar-ai bao gồm một UI terminal được xây dựng với [Textual](https://textual.textualize.io/):

- Lịch sử cuộc trò chuyện có thể cuộn với văn bản phát trực tiếp
- Tự động hoàn thành cho `/quit`, `/clear`
- Ngắt cuộc trò chuyện của tác nhân giữa chừng bằng cách gõ trong khi nó đang suy nghĩ
- **Nhật ký cuộc trò chuyện** tự động được lưu vào `~/.cache/familiar-ai/chat.log`

Để theo dõi nhật ký trong một terminal khác (hữu ích cho việc sao chép-dán):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Tính cách của familiar của bạn sống trong `ME.md`. Tệp này được gitignored — chỉ riêng bạn.

Xem [`persona-template/en.md`](./persona-template/en.md) để xem một ví dụ, hoặc [`persona-template/ja.md`](./persona-template/ja.md) cho phiên bản tiếng Nhật.

---

## Câu hỏi thường gặp

**Q: Nó có hoạt động mà không có GPU không?**
Có. Mô hình embedding (multilingual-e5-small) hoạt động tốt trên CPU. GPU làm cho nó nhanh hơn nhưng không bắt buộc.

**Q: Tôi có thể sử dụng camera khác ngoài Tapo không?**
Bất kỳ camera nào hỗ trợ ONVIF + RTSP đều nên hoạt động. Tapo C220 là model mà chúng tôi đã thử nghiệm.

**Q: Dữ liệu của tôi có được gửi đi đâu không?**
Hình ảnh và văn bản được gửi đến API LLM mà bạn đã chọn để xử lý. Kỷ niệm được lưu trữ cục bộ trong `~/.familiar_ai/`.

**Q: Tại sao tác nhân lại viết `（...）` thay vì nói?**
Đảm bảo rằng `ELEVENLABS_API_KEY` đã được thiết lập. Nếu không, giọng nói bị vô hiệu hóa và tác nhân sẽ quay về văn bản.

## Nền tảng kỹ thuật

Bạn có tò mò về cách nó hoạt động không? Xem [docs/technical.md](./docs/technical.md) để biết nghiên cứu và quyết định thiết kế phía sau familiar-ai — ReAct, SayCan, Reflexion, Voyager, hệ thống khao khát, và nhiều hơn nữa.

---

## Đóng góp

familiar-ai là một thử nghiệm mở. Nếu bất cứ điều gì trong số này tạo được sự đồng cảm với bạn — về mặt kỹ thuật hoặc triết học — bạn rất được chào đón đóng góp.

**Những nơi tốt để bắt đầu:**

| Khu vực | Cần gì |
|---------|--------|
| Phần cứng mới | Hỗ trợ cho nhiều camera hơn (RTSP, IP Webcam), micrô, bộ điều khiển |
| Công cụ mới | Tìm kiếm web, tự động hóa nhà, lịch, bất cứ điều gì qua MCP |
| Nền tảng mới | Bất kỳ LLM hoặc mô hình cục bộ nào phù hợp với giao diện `stream_turn` |
| Mẫu tính cách | Mẫu ME.md cho các ngôn ngữ và tính cách khác nhau |
| Nghiên cứu | Mô hình khao khát tốt hơn, truy xuất trí nhớ, gợi ý lý thuyết về tâm trí |
| Tài liệu | Hướng dẫn, hướng dẫn chi tiết, dịch thuật |

Xem [CONTRIBUTING.md](./CONTRIBUTING.md) để biết thiết lập phát triển, phong cách mã, và hướng dẫn PR.

Nếu bạn không chắc chắn bắt đầu từ đâu, [mở một vấn đề](https://github.com/lifemate-ai/familiar-ai/issues) — rất vui được chỉ bạn theo đúng hướng.

---

## Giấy phép

[MIT](./LICENSE)
```
