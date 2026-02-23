# familiar-ai 🐾

**一个与你同住的 AI** — 有眼睛、有声音、有腿，还有记忆。

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

[English README](./README.md)

---

[![演示视频](https://img.youtube.com/vi/7jJzxQFHvGE/0.jpg)](https://youtube.com/shorts/7jJzxQFHvGE)

Familiar AI 是一个住在你家里的 AI 伙伴。
几分钟内就能搭建完成。无需编写任何代码。

它通过摄像头感知真实世界，在机器人身体上移动，大声说话，并记住它所看到的一切。给它起个名字，定义它的性格，然后让它与你同住。

## 它能做什么

- 👁 **看** — 从 Wi-Fi 云台摄像头或 USB 网络摄像头捕捉图像
- 🔄 **四处张望** — 通过云台摄像头的旋转平移来探索周围环境
- 🦿 **移动** — 驱动扫地机器人在房间里漫游
- 🗣 **说话** — 通过 ElevenLabs TTS 朗读文本
- 🧠 **记住** — 主动储存和回忆记忆，支持语义搜索（SQLite + 向量嵌入）
- 🫀 **心智理论** — 在回应前换位思考
- 💭 **欲望** — 有自己的内在驱动，会触发自主行为

## 工作原理

Familiar AI 运行一个由你选择的大语言模型驱动的 [ReAct](https://arxiv.org/abs/2210.03629) 循环。它通过工具感知世界，思考接下来要做什么，然后行动 — 就像一个人一样。

```
用户输入
  → 思考 → 行动（摄像头 / 移动 / 说话 / 记忆） → 观察 → 思考 → ...
```

闲置时，它会根据自己的欲望行动：好奇心、想看看窗外、想念与它同住的人。

## 快速开始

### 1. 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 克隆并安装

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 3. 配置

```bash
cp .env.example .env
# 用你的配置编辑 .env
```

**最少需要的配置：**

| 变量 | 说明 |
|------|------|
| `PLATFORM` | `anthropic`（默认）\| `gemini` \| `openai` \| `kimi` |
| `API_KEY` | 选定平台的 API 密钥 |

**可选配置：**

| 变量 | 说明 |
|------|------|
| `MODEL` | 模型名称（各平台有合理默认值） |
| `AGENT_NAME` | TUI 中显示的名字（如 `Yukine`） |
| `CAMERA_HOST` | ONVIF/RTSP 摄像头的 IP 地址 |
| `CAMERA_USER` / `CAMERA_PASS` | 摄像头凭证 |
| `ELEVENLABS_API_KEY` | 用于语音输出 — [elevenlabs.io](https://elevenlabs.io/) |

### 4. 创建你的伙伴

```bash
cp persona-template/en.md ME.md
# 编辑 ME.md — 给它起名字，定义性格
```

### 5. 运行

```bash
./run.sh             # 文本 UI（推荐）
./run.sh --no-tui    # 纯命令行交互
```

---

## 选择大语言模型

> **推荐：Kimi K2.5** — 目前测试效果最好的 Agent 模型。它能注意到上下文、提出追问、以及用其他模型做不到的方式自主行动。价格与 Claude Haiku 相近。

| 平台 | `PLATFORM=` | 默认模型 | 获取密钥 |
|------|-----------|---------|--------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI 兼容（Ollama、vllm 等） | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai（多供应商） | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |

**Kimi K2.5 `.env` 示例：**
```env
PLATFORM=kimi
API_KEY=sk-...   # 来自 platform.moonshot.ai
AGENT_NAME=Yukine
```

**Google Gemini `.env` 示例：**
```env
PLATFORM=gemini
API_KEY=AIza...   # 来自 aistudio.google.com
MODEL=gemini-2.5-flash  # 或 gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` 示例：**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # 来自 openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # 可选
AGENT_NAME=Yukine
```

> **注意：** 要禁用本地/NVIDIA 模型，请勿将 `BASE_URL` 设置为本地端点如 `http://localhost:11434/v1`。请使用云服务提供商。

---

## 硬件

Familiar AI 可以用任何你拥有的硬件运行 — 或者根本不需要。

| 部件 | 功能 | 示例 | 必需？ |
|-----|------|------|-------|
| Wi-Fi 云台摄像头 | 眼睛 + 脖子 | Tapo C220（约 $30） | **推荐** |
| USB 网络摄像头 | 眼睛（固定） | 任何 UVC 摄像头 | **推荐** |
| 扫地机器人 | 腿 | 任何兼容涂鸦的型号 | 否 |
| PC / 树莓派 | 大脑 | 任何能运行 Python 的设备 | **是** |

> **强烈推荐配备摄像头。** 没有摄像头的话，Familiar AI 仍然可以说话 — 但它看不到世界，这有点违背了设计初衷。

### 最小化配置（无硬件）

只想试试？你只需要一个 API 密钥：

```env
PLATFORM=kimi
API_KEY=sk-...
```

运行 `./run.sh` 开始聊天。之后可以逐步添加硬件。

### Wi-Fi 云台摄像头（Tapo C220）

1. 在 Tapo 应用中：**设置 → 高级 → 摄像头账户** — 创建本地账户（不是 TP-Link 账户）
2. 在路由器的设备列表中找到摄像头的 IP
3. 在 `.env` 中设置：
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### 语音（ElevenLabs）

1. 在 [elevenlabs.io](https://elevenlabs.io/) 获取 API 密钥
2. 在 `.env` 中设置：
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # 可选，省略则使用默认声音
   ```
3. 语音通过 go2rtc（首次运行时自动下载）通过摄像头内置扬声器播放

---

## TUI

Familiar AI 包含一个使用 [Textual](https://textual.textualize.io/) 构建的终端 UI：

- 可滚动的对话历史，支持实时流式文本显示
- 制表符补全支持 `/quit`、`/clear` 等命令
- Agent 思考时可以打字中断其思考过程
- **对话日志**自动保存到 `~/.cache/familiar-ai/chat.log`

在另一个终端监视日志（便于复制粘贴）：
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## 性格定义（ME.md）

你的伙伴的性格定义在 `ME.md` 中。这个文件在 gitignore 中 — 它完全属于你。

参考 [`persona-template/en.md`](./persona-template/en.md) 查看英文示例，或 [`persona-template/ja.md`](./persona-template/ja.md) 查看日文版本。

---

## 常见问题

**Q: 没有 GPU 可以运行吗？**
可以。嵌入模型（multilingual-e5-small）在 CPU 上运行良好。GPU 会让速度更快，但不是必需的。

**Q: 可以用除 Tapo 以外的摄像头吗？**
任何支持 ONVIF + RTSP 的摄像头都可以。我们测试过的是 Tapo C220。

**Q: 我的数据会被发送到哪里？**
图像和文本会被发送到你选择的大语言模型 API 进行处理。记忆数据存储在本地的 `~/.familiar_ai/`。

**Q: 为什么 Agent 写 `（...）` 而不是说话？**
确保设置了 `ELEVENLABS_API_KEY`。没有它的话，语音功能会被禁用，Agent 会只输出文本。

## 许可证

[MIT](./LICENSE)
