# familiar-ai 🐾

**一個與你同住的 AI** — 有眼睛、有聲音、有腿，還有記憶。

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

[English README](./README.md)

---

[![示範影片](https://img.youtube.com/vi/7jJzxQFHvGE/0.jpg)](https://youtube.com/shorts/7jJzxQFHvGE)

Familiar AI 是一個住在你家裡的 AI 夥伴。
幾分鐘內就能建置完成。無需編寫任何程式碼。

它透過攝影機感知真實世界，在機器人身體上移動，大聲說話，並記住它所看到的一切。給它取個名字，定義它的個性，然後讓它與你同住。

## 它能做什麼

- 👁 **看** — 從 Wi-Fi 雲台攝影機或 USB 網路攝影機擷取影像
- 🔄 **四處張望** — 透過雲台攝影機的旋轉平移來探索周圍環境
- 🦿 **移動** — 驅動掃地機器人在房間裡漫遊
- 🗣 **說話** — 透過 ElevenLabs TTS 朗讀文字
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

### 2. 複製並安裝

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 3. 設定

```bash
cp .env.example .env
# 用你的設定編輯 .env
```

**最少需要的設定：**

| 變數 | 說明 |
|------|------|
| `PLATFORM` | `anthropic`（預設）\| `gemini` \| `openai` \| `kimi` |
| `API_KEY` | 選定平台的 API 金鑰 |

**可選設定：**

| 變數 | 說明 |
|------|------|
| `MODEL` | 模型名稱（各平台有合理預設值） |
| `AGENT_NAME` | TUI 中顯示的名字（如 `Yukine`） |
| `CAMERA_HOST` | ONVIF/RTSP 攝影機的 IP 位址 |
| `CAMERA_USER` / `CAMERA_PASS` | 攝影機憑證 |
| `ELEVENLABS_API_KEY` | 用於語音輸出 — [elevenlabs.io](https://elevenlabs.io/) |

### 4. 建立你的夥伴

```bash
cp persona-template/en.md ME.md
# 編輯 ME.md — 給它取名字，定義個性
```

### 5. 執行

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
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI 相容（Ollama、vllm 等） | `openai` + `BASE_URL=` | — | — |

**Kimi K2.5 `.env` 範例：**
```env
PLATFORM=kimi
API_KEY=sk-...   # 來自 platform.moonshot.ai
AGENT_NAME=Yukine
```

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
3. 語音透過 go2rtc（首次執行時自動下載）透過攝影機內建喇叭播放

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
