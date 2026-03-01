# familiar-ai 🐾

**一個與你同住的 AI** — 有眼睛、有聲音、有腿，還有記憶。

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

[English README](./README.md)

---

[![示範影片](https://img.youtube.com/vi/GUFpd4E7Zeo/0.jpg)](https://youtube.com/shorts/GUFpd4E7Zeo)

Familiar AI 是一個住在你家裡的 AI 夥伴。
幾分鐘內就能建置完成。無需編寫任何程式碼。

它透過攝影機感知真實世界，在機器人身體上移動，大聲說話，並記住它所看到的一切。給它取個名字，定義它的個性，然後讓它與你同住。

## 它能做什麼

- 👁 **看** — 從 Wi-Fi 雲台攝影機或 USB 網路攝影機擷取影像
- 🔄 **四處張望** — 透過雲台攝影機的旋轉平移來探索周圍環境
- 🦿 **移動** — 驅動掃地機器人在房間裡漫遊
- 🗣 **說話** — 透過 ElevenLabs TTS 朗讀文字
- 🎙 **聆聽** — 透過 ElevenLabs 即時 STT 實現免提語音輸入（選用）
- 🧠 **記住** — 主動儲存和回憶記憶，支援語義搜尋（SQLite + 向量嵌入）
- 🫀 **心智理論** — 在回應前換位思考
- 💭 **慾望** — 有自己的內在驅動，會觸發自主行為

## 運作原理

Familiar AI 執行一個由你選擇的大型語言模型驅動的 [ReAct](https://arxiv.org/abs/2210.03629) 迴圈。它透過工具感知世界，思考接下來要做什麼，然後行動 — 就像一個人一樣。

```
使用者輸入
  → 思考 → 行動（攝影機 / 移動 / 說話 / 記憶） → 觀察 → 思考 → ...
```

閒置時，它會根據自己的慾望行動：好奇心、想看看窗外、想念與它同住的人。

## 快速開始

### 1. 安裝 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安裝 ffmpeg

ffmpeg是**必要**的，用於相機圖像擷取和音訊播放。

| OS | 指令 |
|----|------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — 或從 [ffmpeg.org](https://ffmpeg.org/download.html) 下載並加入 PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

驗證：`ffmpeg -version`

### 3. 複製並安裝

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. 設定

```bash
cp .env.example .env
# 用你的設定編輯 .env
```

**最少需要的設定：**

| 變數 | 說明 |
|------|------|
| `PLATFORM` | `anthropic`（預設）\| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | 選定平台的 API 金鑰 |

**可選設定：**

| 變數 | 說明 |
|------|------|
| `MODEL` | 模型名稱（各平台有合理預設值） |
| `AGENT_NAME` | TUI 中顯示的名字（如 `Yukine`） |
| `CAMERA_HOST` | ONVIF/RTSP 攝影機的 IP 位址 |
| `CAMERA_USER` / `CAMERA_PASS` | 攝影機憑證 |
| `ELEVENLABS_API_KEY` | 用於語音輸出 — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` 啟用免提即時語音輸入（需要 `ELEVENLABS_API_KEY`） |
| `TTS_OUTPUT` | 音訊輸出位置：`local`（PC 喇叭，預設）\| `remote`（攝影機喇叭）\| `both`（兩者同時） |
| `THINKING_MODE` | 僅 Anthropic — `auto`（預設）\| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptive thinking 深度：`high`（預設）\| `medium` \| `low` \| `max`（僅 Opus 4.6） |

### 5. 建立你的夥伴

```bash
cp persona-template/en.md ME.md
# 編輯 ME.md — 給它取名字，定義個性
```

### 6. 執行

```bash
./run.sh             # 文字 UI（推薦）
./run.sh --no-tui    # 純命令列互動
```

---

## 選擇大型語言模型

> **推薦：Kimi K2.5** — 目前測試效果最好的 Agent 模型。它能注意到上下文、提出追問、以及用其他模型做不到的方式自主行動。價格與 Claude Haiku 相近。

| 平台 | `PLATFORM=` | 預設模型 | 取得金鑰 |
|------|-----------|---------|--------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI 相容（Ollama、vllm 等） | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai（多供應商） | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI 工具**（claude -p、ollama 等） | `cli` | （指令） | — |

**Kimi K2.5 `.env` 範例：**
```env
PLATFORM=kimi
API_KEY=sk-...   # 來自 platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` 範例：**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` 範例：**
```env
PLATFORM=gemini
API_KEY=AIza...   # 來自 aistudio.google.com
MODEL=gemini-2.5-flash  # 或 gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` 範例：**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # 來自 openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # 可選
AGENT_NAME=Yukine
```

> **注意：** 要停用本地/NVIDIA 模型，請勿將 `BASE_URL` 設定為本地端點如 `http://localhost:11434/v1`。請使用雲端服務提供商。

**CLI 工具 `.env` 範例：**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI（https://llm.datasette.io）— {} = 提示詞參數
# MODEL=ollama run gemma3:27b  # Ollama — 無 {}，提示詞透過 stdin 傳入
```

---

## MCP 伺服器

familiar-ai 可以連接任何 [MCP（模型情境協定）](https://modelcontextprotocol.io) 伺服器，從而接入外部記憶、檔案系統存取、網路搜尋等各種工具。

在 `~/.familiar-ai.json` 中設定伺服器（與 Claude Code 格式相同）：

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

支援兩種傳輸類型：
- **`stdio`**：啟動本地子程序（`command` + `args`）
- **`sse`**：連接 HTTP+SSE 伺服器（`url`）

透過 `MCP_CONFIG=/path/to/config.json` 可覆蓋設定檔路徑。

---

## 硬體

Familiar AI 可以用任何你擁有的硬體執行 — 或者根本不需要。

| 元件 | 功能 | 範例 | 必需？ |
|-----|------|------|-------|
| Wi-Fi 雲台攝影機 | 眼睛 + 脖子 | Tapo C220（約 $30） | **推薦** |
| USB 網路攝影機 | 眼睛（固定） | 任何 UVC 攝影機 | **推薦** |
| 掃地機器人 | 腿 | 任何相容 Tuya 的型號 | 否 |
| PC / 樹莓派 | 大腦 | 任何能執行 Python 的裝置 | **是** |

> **強烈推薦配備攝影機。** 沒有攝影機的話，Familiar AI 仍然可以說話 — 但它看不到世界，這有點違背了設計初衷。

### 最小化設定（無硬體）

只想試試？你只需要一個 API 金鑰：

```env
PLATFORM=kimi
API_KEY=sk-...
```

執行 `./run.sh` 開始聊天。之後可以逐步新增硬體。

### Wi-Fi 雲台攝影機（Tapo C220）

1. 在 Tapo 應用程式中：**設定 → 進階 → 攝影機帳號** — 建立本機帳號（不是 TP-Link 帳號）
2. 在路由器的裝置清單中找到攝影機的 IP
3. 在 `.env` 中設定：
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### 語音（ElevenLabs）

1. 在 [elevenlabs.io](https://elevenlabs.io/) 取得 API 金鑰
2. 在 `.env` 中設定：
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # 可選，省略則使用預設聲音
   ```
音訊播放位置由 `TTS_OUTPUT` 控制：

```env
TTS_OUTPUT=local    # PC 喇叭（預設）
TTS_OUTPUT=remote   # 僅攝影機喇叭
TTS_OUTPUT=both     # 攝影機喇叭 + PC 喇叭同時播放
```

#### A) 攝影機喇叭（透過 go2rtc）

設定 `TTS_OUTPUT=remote`（或 `both`）時使用。需手動安裝 [go2rtc](https://github.com/AlexxIT/go2rtc/releases)：

1. 從[發布頁面](https://github.com/AlexxIT/go2rtc/releases)下載二進位檔：
   - Linux/macOS：`go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows：`go2rtc_win64.exe`**

2. 放置並重新命名到以下路徑：
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # 需要 chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. 在同一目錄下建立 `go2rtc.yaml`：
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```

4. familiar-ai 啟動時會自動啟動 go2rtc。若攝影機支援雙向音訊，聲音將從攝影機喇叭輸出。

#### B) 本機 PC 喇叭

預設方式（`TTS_OUTPUT=local`）。依序嘗試 **paplay** → **mpv** → **ffplay**。當 `TTS_OUTPUT=remote` 且 go2rtc 無法使用時也作為備用方案。

| 作業系統 | 安裝方式 |
|---------|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv`（或透過 `pulseaudio-utils` 使用 paplay）|
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — 在 `.env` 中設定 `PULSE_SERVER=unix:/mnt/wslg/PulseServer` |
| Windows | 從 [mpv.io/installation](https://mpv.io/installation/) 下載並加入 PATH，**或** `winget install ffmpeg` |

> 即使沒有 go2rtc 或本機播放器，語音生成本身（ElevenLabs API 呼叫）仍可正常運作，只是不會播放。

### 語音輸入（即時 STT）

在 `.env` 中設定 `REALTIME_STT=true` 可啟用免提即時語音輸入：

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # 與 TTS 相同的金鑰
```

說話暫停後，ElevenLabs Scribe v2 會自動轉錄。無需按鍵操作。可與按鍵通話（Ctrl+T）同時使用。

---

## TUI

Familiar AI 包含一個使用 [Textual](https://textual.textualize.io/) 建置的終端機 UI：

- 可捲動的對話歷史，支援即時串流文字顯示
- Tab 補全支援 `/quit`、`/clear` 等指令
- Agent 思考時可以打字中斷其思考過程
- **對話記錄**自動儲存到 `~/.cache/familiar-ai/chat.log`

在另一個終端機監看記錄（便於複製貼上）：
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## 個性定義（ME.md）

你的夥伴的個性定義在 `ME.md` 中。這個檔案在 gitignore 中 — 它完全屬於你。

參考 [`persona-template/en.md`](./persona-template/en.md) 查看英文範例，或 [`persona-template/ja.md`](./persona-template/ja.md) 查看日文版本。

---

## 常見問題

**Q: 沒有 GPU 可以執行嗎？**
可以。嵌入模型（multilingual-e5-small）在 CPU 上執行良好。GPU 會讓速度更快，但不是必需的。

**Q: 可以用除 Tapo 以外的攝影機嗎？**
任何支援 ONVIF + RTSP 的攝影機都可以。我們測試過的是 Tapo C220。

**Q: 我的資料會被傳送到哪裡？**
影像和文字會被傳送到你選擇的大型語言模型 API 進行處理。記憶資料儲存在本機的 `~/.familiar_ai/`。

**Q: 為什麼 Agent 寫 `（...）` 而不是說話？**
確保設定了 `ELEVENLABS_API_KEY`。沒有它的話，語音功能會被停用，Agent 只會輸出文字。

## 授權條款

[MIT](./LICENSE)
