# familiar-ai 

<img width="25%" height="25%" alt="familiar-ai-icon" src="https://github.com/user-attachments/assets/944b2023-9ca0-4b30-8240-de766e4439ed" />

**あなたのそばに生きるAI** — 目があり、声があり、足があり、記憶がある。

[![Lint](https://github.com/lifemate-ai/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/lifemate-ai/familiar-ai/actions/workflows/lint.yml)
[![Test](https://github.com/lifemate-ai/familiar-ai/actions/workflows/test.yml/badge.svg)](https://github.com/lifemate-ai/familiar-ai/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74の言語に対応](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai は、家に暮らすAIコンパニオンです。
セットアップは数分で完了。コーディング不要です。

カメラを通じて現実世界を認知し、ロボットボディで動き回り、声を出して話し、見たものを覚えています。名前を付けて、性格を作ってあげれば、一緒に生活できます。

## できること

- 👁 **見る** — Wi-Fi PTZカメラまたはUSBウェブカメラから画像をキャプチャ
- 🔄 **周囲を見回る** — カメラをパン/チルトして周囲を探索
- 🦿 **動く** — ロボット掃除機で部屋を移動
- 🗣 **話す** — ElevenLabsのTTSで音声を出力
- 🎙 **聞く** — ElevenLabsリアルタイムSTTでハンズフリー音声入力（オプション）
- 🧠 **覚える** — セマンティック検索で記憶を積極的に保存・想起（SQLite + 埋め込み）
- 🫀 **心の理論** — 相手の視点を考慮してから応答
- 💭 **欲求** — 自分自身の内的な動機を持ち、自律的な行動を引き起こす
- 🌐 **グローバルワークスペース** — 知覚、記憶、欲求、予測が注意を奪い合い、最も重要なもののみが勝つ
- 🔮 **予測** — 見えると予測したものを追跡。予想外が起こると注意閾値が下がる
- 🔍 **注意スキーマ** — 自分が何に焦点を当てているか、なぜかの自己モデルを保持
- 💤 **デフォルトモード** — アイドル時に心が彷徨い、記憶や関連性が自発的に浮かぶ
- 🔬 **メタ認知** — 毎ターン自分の推論ステップを観察

## 仕組み

familiar-ai は選択したLLMで動く [ReAct](https://arxiv.org/abs/2210.03629) ループを実行します。世界を認知し、次の行動を考え、実行する — ちょうど人間のように。

```
ユーザー入力
  → 考える → 行動する（カメラ / 移動 / 話す / 覚える） → 観察する → 考える → ...
```

アイドル中は、独自の欲求に基づいて行動します：好奇心、外を見たい、一緒に過ごしている人を思う気持ち。

### グローバルワークスペース・アーキテクチャ

内部では、familiar-ai は [グローバルワークスペース理論](https://arxiv.org/abs/2410.11407) にインスパイアされたアーキテクチャを実装しています。すべてをLLMプロンプトに詰め込む代わりに、専門的なプロセッサが毎ターン中央ワークスペースをめぐって競争し、勝者だけが完全な表現を獲得します：

```
専門的なプロセッサ（毎ターン並列実行）
  ├─ 欲求          — 今何が欲しいか
  ├─ シーン         — 何が見えているか（予測誤差：驚き → 高い認識）
  ├─ 記憶          — 何を思い出しているか
  ├─ 心の理論      — 相手は何を考えているか
  ├─ 自己叙述      — アイデンティティの継続性
  ├─ 探索          — 未訪問の方向への好奇心
  ├─ 注意スキーマ  — 自分の焦点の自己モデル
  ├─ 予測          — 予期される vs 実際の世界状態
  └─ デフォルトモード — 何も点火しないときの心の彷徨
          │
          ▼  競争する（点火閾値）
   ┌─────────────┐
   │  ワークスペース │  勝者 → LLMプロンプト（ボトルネック）
   │  ブロードキャスト│  その他 → 周辺要約（各1行）
   └─────────────┘
          │
          └──▶ メタモニター が各ステップを記録（「何に注意を向けていた？」）
```

これにより **選択的注意** が生まれます — すべてが毎ターンLLMに到達するのではなく、最も重要なものだけです。

## 始めましょう

### 1. uv をインストール

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
または: `winget install astral-sh.uv`

### 2. ffmpeg をインストール

ffmpeg はカメラ画像キャプチャと go2rtc 経由のカメラスピーカー再生に **必須** です。
ローカルPC音声再生は組み込みOSプレイヤー（macOS の `afplay`）または
Python純正フォールバックも使用できます。

| OS | コマンド |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — または [ffmpeg.org](https://ffmpeg.org/download.html) からダウンロードしてPATHに追加 |
| Raspberry Pi | `sudo apt install ffmpeg` |

確認: `ffmpeg -version`

### 3. クローンしてインストール

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. 設定

```bash
cp .env.example .env
# .env を編集して設定する
```

デスクトップフローを使いたい場合、`./run-gui.sh`（または `run-gui.bat`）はまだ `API_KEY` がない初回起動時にセットアップダイアログを開けます。

**最小限必須:**

| 変数 | 説明 |
|----------|-------------|
| `PLATFORM` | `anthropic`（デフォルト） \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | 選択したプラットフォームのAPIキー |

**オプション:**

| 変数 | 説明 |
|----------|-------------|
| `MODEL` | モデル名（プラットフォームごとに合理的なデフォルト） |
| `AGENT_NAME` | TUIに表示される名前（例 `Yukine`） |
| `CAMERA_HOST` | ONVIF/RTSPカメラのIPアドレス |
| `CAMERA_USERNAME` / `CAMERA_PASSWORD` | カメラ認証情報 |
| `CAMERA_PTZ_HOST` / `CAMERA_PTZ_USERNAME` / `CAMERA_PTZ_PASSWORD` / `CAMERA_PTZ_PORT` | PTZ制御エンドポイントがRTSPストリームエンドポイントと異なる場合のオプション上書き |
| `ELEVENLABS_API_KEY` | 音声出力用 — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` で常時ハンズフリー音声入力を有効化（`ELEVENLABS_API_KEY` が必須） |
| `TTS_OUTPUT` | 音声再生先: `local`（PCスピーカー、デフォルト） \| `remote`（カメラスピーカー） \| `both` |
| `THINKING_MODE` | Anthropic のみ — `auto`（デフォルト） \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | 適応的思考レベル: `high`（デフォルト） \| `medium` \| `low` \| `max`（Opus 4.6 のみ） |

### 5. familiar を作成

```bash
cp persona-template/en.md ME.md
# ME.md を編集 — 名前と性格を付与
```

### 6. 実行

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textual TUI（後方互換性のあるデフォルト）
./run-gui.sh         # デスクトップGUIランチャー
./run.sh --gui       # デスクトップGUI（run-gui.sh と同じ）
./run.sh --no-tui    # プレーンREPL
```

**Windows:**
```bat
run.bat              # Textual TUI（後方互換性のあるデフォルト）
run-gui.bat          # デスクトップGUIランチャー
run.bat --gui        # デスクトップGUI（run-gui.bat と同じ）
run.bat --no-tui     # プレーンREPL
```

---

## LLM を選ぶ

> **推奨: Kimi K2.5** — テスト済みの中で最高のエージェント性能。文脈に気づき、フォローアップ質問をし、他のモデルにはない自律的な行動をします。Claude Haiku と同等の価格。

| プラットフォーム | `PLATFORM=` | デフォルトモデル | キーの取得先 |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| **Ollama（ローカル、ネイティブAPI）** | `ollama` | `gemma4:12b-it-qat` | [ollama.com](https://ollama.com) |
| OpenAI互換（vllm、LM Studio…） | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai（マルチプロバイダー） | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLIツール** （claude -p、ollama…） | `cli` | （コマンド） | — |

**Kimi K2.5 `.env` 例:**
```env
PLATFORM=kimi
API_KEY=sk-...   # platform.moonshot.ai から
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` 例:**
```env
PLATFORM=glm
API_KEY=...   # api.z.ai から
MODEL=glm-4.6v   # ビジョン対応; glm-4.7 / glm-5 = テキストのみ
AGENT_NAME=Yukine
```

**Google Gemini `.env` 例:**
```env
PLATFORM=gemini
API_KEY=AIza...   # aistudio.google.com から
MODEL=gemini-2.5-flash  # または gemini-2.5-pro でより高い能力
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` 例:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # openrouter.ai から
MODEL=mistralai/mistral-7b-instruct  # オプション: モデル指定
AGENT_NAME=Yukine
```

> **注:** ローカル/NVIDIA モデルを無効にするには、`BASE_URL` を `http://localhost:11434/v1` のようなローカルエンドポイントに設定しないでください。代わりにクラウドプロバイダーを使用してください。

**Ollama（ローカル ~10B） `.env` 例:**
```env
PLATFORM=ollama
MODEL=gemma4:12b-it-qat          # テスト済みローカル ~10B の最良; qwen3.5:9b も
