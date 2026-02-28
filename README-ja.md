# familiar-ai 🐾

**あなたのそばに暮らすAI** — 目があり、声があり、脚があり、記憶がある。

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[English README](./README.md)

---

[![デモ動画](https://img.youtube.com/vi/D5U8msRib10/0.jpg)](https://youtu.be/D5U8msRib10)

---

familiar-ai はあなたの家に暮らすAIコンパニオンです。
数分でセットアップできます。コーディング不要。

カメラを通じて現実世界を認識し、ロボットボディで動き回り、声を出して話し、見たものを覚えています。名前をつけて、性格を書いて、一緒に暮らしましょう。

## できること

- 👁 **見る** — Wi-Fi PTZカメラまたはUSBウェブカメラから画像をキャプチャ
- 🔄 **周囲を見回す** — カメラをパン・チルトさせて周囲を探索
- 🦿 **動く** — ロボット掃除機で部屋を移動
- 🗣 **話す** — ElevenLabs TTSで声を出す
- 🧠 **覚える** — セマンティック検索を使って能動的に記憶を保存・想起（SQLite + embeddings）
- 🫀 **心の理論** — 相手の立場に立ってから返答
- 💭 **欲望** — 自律的な行動をトリガーする内的動機を持つ

## 仕組み

familiar-ai は選んだLLMで動く [ReAct](https://arxiv.org/abs/2210.03629) ループを実行します。ツールを通じて世界を認識し、次に何をすべきか考えて、行動します — ちょうど人間のように。

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

アイドル状態では、独自の欲求に従って動きます：好奇心、外を見たい気持ち、一緒に暮らす人に会いたい気持ち。

## はじめる

### 1. uv をインストール

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. ffmpeg をインストール

ffmpegは**必須**です。カメラ画像のキャプチャと音声再生に使用します。

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
# .env を編集して設定を入力
```


**必須項目：**

| 変数 | 説明 |
|------|------|
| `PLATFORM` | `anthropic`（デフォルト）\| `gemini` \| `openai` \| `kimi` |
| `API_KEY` | 選んだプラットフォームのAPIキー |

**オプション：**

| 変数 | 説明 |
|------|------|
| `MODEL` | モデル名（プラットフォームごとにデフォルト値あり） |
| `AGENT_NAME` | TUIに表示される名前（例：`ユキネ`） |
| `CAMERA_HOST` | ONVIF/RTSPカメラのIPアドレス |
| `CAMERA_USER` / `CAMERA_PASS` | カメラの認証情報 |
| `ELEVENLABS_API_KEY` | 音声出力用 — [elevenlabs.io](https://elevenlabs.io/) |
| `TTS_OUTPUT` | 音声出力先：`local`（PCスピーカー、デフォルト）\| `remote`（カメラスピーカー）\| `both`（両方同時） |
| `THINKING_MODE` | Anthropic専用 — `auto`（デフォルト）\| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptive thinking の深度：`high`（デフォルト）\| `medium` \| `low` \| `max`（Opus 4.6のみ） |

### 5. familiarを作る

```bash
cp persona-template/en.md ME.md
# ME.md を編集して、名前と性格を設定
```

### 6. 実行

```bash
./run.sh             # Textual TUI（推奨）
./run.sh --no-tui    # プレーンREPL
```

---

## LLMを選ぶ

> **推奨：Kimi K2.5** — テスト済みの中で最高のエージェント性能。文脈に気づき、フォローアップの質問をし、他のモデルにはない方法で自律的に行動します。Claude Haiku と同様の価格帯。

| プラットフォーム | `PLATFORM=` | デフォルトモデル | キーを取得 |
|------------|------------|---------------|----------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI互換（Ollama、vllmなど） | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai（マルチプロバイダー） | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLIツール**（claude -p、ollamaなど） | `cli` | （コマンド） | — |

**Kimi K2.5 `.env` の例：**
```env
PLATFORM=kimi
API_KEY=sk-...   # platform.moonshot.ai から取得
AGENT_NAME=ユキネ
```

**Google Gemini `.env` の例：**
```env
PLATFORM=gemini
API_KEY=AIza...   # aistudio.google.com から取得
MODEL=gemini-2.5-flash  # または gemini-2.5-pro
AGENT_NAME=ユキネ
```

**OpenRouter.ai `.env` の例：**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # openrouter.ai から取得
MODEL=mistralai/mistral-7b-instruct  # オプション
AGENT_NAME=ユキネ
```

> **注意：** ローカル/NVIDIAモデルを無効化するには、`BASE_URL` を `http://localhost:11434/v1` のようなローカルエンドポイントに設定しないでください。クラウドプロバイダーを使用してください。

**CLIツールの `.env` 例：**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI（https://llm.datasette.io）— {} = プロンプト引数
# MODEL=ollama run gemma3:27b  # Ollama — {} なし、stdinでプロンプトを渡す
```

---

## MCPサーバー

familiar-ai は任意の [MCP（Model Context Protocol）](https://modelcontextprotocol.io) サーバーに接続できます。外部メモリ、ファイルシステムアクセス、Web検索など、あらゆるツールを追加できます。

`~/.familiar-ai.json` にサーバーを設定します（Claude Codeと同じ形式）：

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

サポートしているトランスポートタイプ：
- **`stdio`**: ローカルサブプロセスを起動（`command` + `args`）
- **`sse`**: HTTP+SSEサーバーに接続（`url`）

設定ファイルの場所は `MCP_CONFIG=/path/to/config.json` で変更できます。

---

## ハードウェア

familiar-ai は何を持っていても動きます — 何もなくても大丈夫。

| パーツ | 役割 | 例 | 必須？ |
|-------|------|-----|--------|
| Wi-Fi PTZカメラ | 目 + 首 | Tapo C220（約$30） | **推奨** |
| USBウェブカメラ | 目（固定） | 任意のUVCカメラ | **推奨** |
| ロボット掃除機 | 脚 | Tuya互換の任意のモデル | いいえ |
| PC / Raspberry Pi | 脳 | Python が動く任意のマシン | **はい** |

> **カメラの使用を強く推奨します。** カメラがないと、familiar-ai は話せますが、世界が見えないので、本来の意味がありません。

### 最小限のセットアップ（ハードウェアなし）

試してみたいだけですか？必要なのはAPIキーだけです：

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` を実行してチャットを始めましょう。後からハードウェアを追加できます。

### Wi-Fi PTZカメラ（Tapo C220）

1. Tapoアプリで：**設定 → 詳細設定 → カメラアカウント** — ローカルアカウントを作成（TP-Link アカウントではなく）
2. ルータのデバイスリストからカメラのIPを確認
3. `.env` に設定：
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### 音声（ElevenLabs）

1. [elevenlabs.io](https://elevenlabs.io/) でAPIキーを取得
2. `.env` に設定：
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # オプション、省略時はデフォルト音声を使用
   ```

音声の再生先は `TTS_OUTPUT` で切り替えられます：

```env
TTS_OUTPUT=local    # PCスピーカー（デフォルト）
TTS_OUTPUT=remote   # カメラスピーカーのみ
TTS_OUTPUT=both     # カメラスピーカー + PCスピーカー同時再生
```

#### A) カメラのスピーカーから再生（go2rtc 経由）

`TTS_OUTPUT=remote`（または `both`）を設定した場合に使用します。[go2rtc](https://github.com/AlexxIT/go2rtc/releases) のセットアップが必要です：

1. [リリースページ](https://github.com/AlexxIT/go2rtc/releases) からバイナリをダウンロード：
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. 以下の場所に配置・リネーム：
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc       # chmod +x が必要

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. 同じディレクトリに `go2rtc.yaml` を作成：
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   ※ `YOUR_CAM_USER` / `YOUR_CAM_PASS` は Tapoアプリで作成したローカルアカウント。`YOUR_CAM_IP` はカメラのIPアドレス。

4. familiar-ai 起動時に go2rtc が自動起動します。カメラが双方向音声（バックチャンネル）に対応していれば、カメラのスピーカーから声が出ます。

#### B) PCのスピーカーから再生

デフォルト（`TTS_OUTPUT=local`）。**paplay** → **mpv** → **ffplay** の順で試みます。`TTS_OUTPUT=remote` でgo2rtcが使えない場合のフォールバックにもなります。

| OS | インストール方法 |
|----|----------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv`（または `pulseaudio-utils` で paplay）|
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` に `PULSE_SERVER=unix:/mnt/wslg/PulseServer` を設定 |
| Windows | [mpv.io/installation](https://mpv.io/installation/) からダウンロードしてPATHに追加、**または** `winget install ffmpeg` |

> go2rtc・mpv・ffplay がいずれも未設定でも、音声生成自体（ElevenLabs API呼び出し）は動作します。再生がスキップされるだけです。

---

## TUI

familiar-ai には [Textual](https://textual.textualize.io/) で構築されたターミナルUIが含まれています：

- スクロール可能な会話履歴とリアルタイムストリーミングテキスト
- `/quit`、`/clear` のタブ補完
- エージェントが考えている最中に入力して、途中で中断可能
- **会話ログ** は自動的に `~/.cache/familiar-ai/chat.log` に保存

別のターミナルでログを追跡（コピペに便利）：
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona（ME.md）

あなたの familiar の性格は `ME.md` に住んでいます。このファイルは gitignore されています — あなただけのものです。

[`persona-template/en.md`](./persona-template/en.md) で例を見るか、[`persona-template/ja.md`](./persona-template/ja.md) で日本語版を見てください。

---

## FAQ

**Q: GPUなしで動きますか？**
はい。埋め込みモデル（multilingual-e5-small）はCPUで問題なく動きます。GPUはあれば速いですが、必須ではありません。

**Q: Tapo以外のカメラは使えますか？**
ONVIF + RTSP をサポートするカメラなら動くはずです。Tapo C220 はテスト済みです。

**Q: データはどこかに送られますか？**
画像とテキストは処理のために選んだLLM APIに送られます。メモリはローカルの `~/.familiar_ai/` に保存されます。

**Q: エージェントが話す代わりに `（...）` と書くのはなぜ？**
`ELEVENLABS_API_KEY` が設定されていることを確認してください。ないと、音声は無効になり、エージェントはテキストにフォールバックします。

## ライセンス

[MIT](./LICENSE)
