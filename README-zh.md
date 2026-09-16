# familiar-ai 

<img width="25%" height="25%" alt="familiar-ai-icon" src="https://github.com/user-attachments/assets/944b2023-9ca0-4b30-8240-de766e4439ed" />

**一个与你同居的 AI** — 拥有眼睛、声音、腿和记忆。

[![Lint](https://github.com/lifemate-ai/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/lifemate-ai/familiar-ai/actions/workflows/lint.yml)
[![Test](https://github.com/lifemate-ai/familiar-ai/actions/workflows/test.yml/badge.svg)](https://github.com/lifemate-ai/familiar-ai/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [支持 74 种语言](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai 是一个与你同住的 AI 伙伴。
几分钟内完成安装，无需编码。

它通过摄像头感知现实世界，在机器人身体上移动，大声说话，还能记住它看到的一切。给它起个名字，写好它的性格，然后就可以和你一起生活了。

## 它能做什么

- 👁 **看** — 从 Wi-Fi 云台摄像头或 USB 网络摄像头捕获图像
- 🔄 **四处看看** — 平移和倾斜摄像头探索周围环境
- 🦿 **移动** — 驱动扫地机器人在房间中漫游
- 🗣 **说话** — 通过 ElevenLabs TTS 大声讲话
- 🎙 **倾听** — 通过 ElevenLabs Realtime STT 实现无需按键的语音输入（可选）
- 🧠 **记忆** — 主动存储和回忆记忆，具有语义搜索功能（SQLite + 嵌入向量）
- 🫀 **心理理论** — 在回应前换位思考
- 💭 **欲望** — 有自己的内部驱动力，可引发自主行为
- 🌐 **全局工作空间** — 感知、记忆、欲望和预测相互竞争；只有最突出的才能获胜
- 🔮 **预测** — 追踪预期看到的内容；惊讶降低注意阈值
- 🔍 **注意力图式** — 维护对自己关注内容和原因的自我模型
- 💤 **默认模式** — 闲置时思绪漂散，自发浮现记忆和联想
- 🔬 **元认知** — 观察每一轮中自己的推理步骤

## 工作原理

familiar-ai 运行由你选择的 LLM 驱动的 [ReAct](https://arxiv.org/abs/2210.03629) 循环。它感知世界、思考下一步该做什么、采取行动 — 就像一个人一样。

```
用户输入
  → 思考 → 行动（摄像头/移动/说话/记忆） → 观察 → 思考 → ...
```

闲置时，它根据自己的欲望采取行动：好奇心、想看外面、想念一起生活的人。

### 全局工作空间架构

在底层，familiar-ai 实现了受 [全局工作空间理论](https://arxiv.org/abs/2410.11407) 启发的架构。与其将所有内容转储到 LLM 提示中，专门的处理器每轮在中央工作空间竞争 — 只有赢家才能获得完整表示：

```
专门处理器（每轮并行运行）
  ├─ 欲望       — 它现在想要什么
  ├─ 场景       — 它感知到的内容（预测错误：惊讶 → 提高警觉）
  ├─ 记忆       — 它回忆的内容
  ├─ 心理理论   — 另一个人可能在想什么
  ├─ 自我叙事   — 身份的连贯性
  ├─ 探索       — 对未探索方向的好奇心
  ├─ 注意力图式 — 自己关注内容的自我模型
  ├─ 预测       — 预期与实际世界状态
  └─ 默认模式   — 没有其他内容点燃时的思绪漂散
          │
          ▼  竞争（点燃阈值）
   ┌─────────────┐
   │   工作空间  │  赢家 → LLM 提示（瓶颈）
   │   广播      │  其他 → 外围摘要（每行 1 行）
   └─────────────┘
          │
          └──▶ 元监视器记录每一步（"我在关注什么？"）
```

这创造了**选择性注意** — 并非每一轮都向 LLM 传达所有内容，只有最重要的内容。

## 快速开始

### 1. 安装 uv

**macOS / Linux / WSL2：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)：**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
或：`winget install astral-sh.uv`

### 2. 安装 ffmpeg

ffmpeg 是**必需的**，用于摄像头图像捕获和通过 go2rtc 的摄像头扬声器播放。
本地 PC 音频播放也可以使用内置 OS 播放器（macOS 上的 `afplay`）或纯 Python 回退方案。

| 操作系统 | 命令 |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — 或从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载并添加到 PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

验证：`ffmpeg -version`

### 3. 克隆并安装

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. 配置

```bash
cp .env.example .env
# 编辑 .env 用你的设置
```

如果你喜欢桌面工作流，`./run-gui.sh`（或 `run-gui.bat`）可以在首次启动时在 `API_KEY` 仍缺失时为你打开设置对话框。

**最少必需：**

| 变量 | 说明 |
|----------|-------------|
| `PLATFORM` | `anthropic`（默认）\| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | 选定平台的 API 密钥 |

**可选：**

| 变量 | 说明 |
|----------|-------------|
| `MODEL` | 模型名称（每个平台都有合理的默认值） |
| `AGENT_NAME` | 显示在 TUI 中的显示名称（例如 `Yukine`） |
| `CAMERA_HOST` | ONVIF/RTSP 摄像头的 IP 地址 |
| `CAMERA_USERNAME` / `CAMERA_PASSWORD` | 摄像头凭证 |
| `CAMERA_PTZ_HOST` / `CAMERA_PTZ_USERNAME` / `CAMERA_PTZ_PASSWORD` / `CAMERA_PTZ_PORT` | 可选的 PTZ 覆盖（当控制端点与 RTSP 流端点不同时） |
| `ELEVENLABS_API_KEY` | 用于语音输出 — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` 启用始终开启的无需按键语音输入（需要 `ELEVENLABS_API_KEY`） |
| `TTS_OUTPUT` | 音频播放位置：`local`（PC 扬声器，默认）\| `remote`（摄像头扬声器）\| `both` |
| `THINKING_MODE` | 仅限 Anthropic — `auto`（默认）\| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | 自适应思考努力：`high`（默认）\| `medium` \| `low` \| `max`（仅 Opus 4.6） |

### 5. 创建你的伙伴

```bash
cp persona-template/en.md ME.md
# 编辑 ME.md — 给它起个名字并定义性格
```

### 6. 运行

**macOS / Linux / WSL2：**
```bash
./run.sh             # Textual TUI（向后兼容默认）
./run-gui.sh         # 桌面 GUI 启动器
./run.sh --gui       # 桌面 GUI（与 run-gui.sh 相同）
./run.sh --no-tui    # 纯 REPL
```

**Windows：**
```bat
run.bat              # Textual TUI（向后兼容默认）
run-gui.bat          # 桌面 GUI 启动器
run.bat --gui        # 桌面 GUI（与 run-gui.bat 相同）
run.bat --no-tui     # 纯 REPL
```

---

## 选择 LLM

> **推荐：Kimi K2.5** — 迄今为止测试过的最佳代理性能。注意到上下文，询问后续问题，以其他模型没有的方式自主行动。价格与 Claude Haiku 相似。

| 平台 | `PLATFORM=` | 默认模型 | 获取密钥 |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| **Ollama（本地，原生 API）** | `ollama` | `gemma4:12b-it-qat` | [ollama.com](https://ollama.com) |
| OpenAI 兼容（vllm、LM Studio…） | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai（多提供商） | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI 工具**（claude -p、ollama…） | `cli` | （命令） | — |

**Kimi K2.5 `.env` 示例：**
```env
PLATFORM=kimi
API_KEY=sk-...   # 来自 platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` 示例：**
```env
PLATFORM=glm
API_KEY=...   # 来自 api.z.ai
MODEL=glm-4.6v   # 启用视觉；glm-4.7 / glm-5 = 仅文本
AGENT_NAME=Yukine
```

**Google Gemini `.env` 示例：**
```env
PLATFORM=gemini
API_KEY=AIza...   # 来自 aistudio.google.com
MODEL=gemini-2.5-flash  # 或 gemini-2.5-pro 以获得更高能力
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` 示例：**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # 来自 openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # 可选：指定模型
AGENT_NAME=Yukine
```

> **注意：** 要禁用本地/NVIDIA 模型，只需不将 `BASE_URL` 设置为本地端点（如 `http://localhost:11434/v1`）。改用云提供商。

**Ollama（本地 ~10B）`.env` 示例：**
```env
PLATFORM=ollama
MODEL=gemma4:12b-it-qat          # 测试过的最佳本地 ~10B；qwen3.5:9b 也可以
BASE_URL=http://localhost:11434  # 默认
UTILITY_PLATFORM=ollama          # 情感/摘要辅助调用也保持本地
AGENT_NAME=Yukine
# PROMPT_PROFILE=compact  (本地模型自动) — 简短、示例驱动的提示
# SOCIAL_REFLEX=on        (自动)           — 社交轮次无摄像头，自动说话
# THINKING_MODE=disabled  (自动 = 本地关闭；"extended" 启用 Ollama think)
# OLLAMA_NUM_CTX=16
