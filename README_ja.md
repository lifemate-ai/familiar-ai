# familiar-ai 🐾

**あなたのそばで生きるAI** — 目・声・足・記憶を持つコンパニオン。

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74言語に対応](./SUPPORTED_LANGUAGES.md)

---

[![デモ動画](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai は、あなたの家に住むAIコンパニオンです。
数分でセットアップできます。コーディング不要。

カメラで世界を認識し、ロボット掃除機で部屋を動き回り、声で話し、見たものを記憶します。名前をつけて、性格を書いて、一緒に暮らしてください。

## できること

- 👁 **見る** — Wi-Fi PTZカメラまたはUSBウェブカメラから画像を取得
- 🔄 **見回す** — カメラをパン・チルトして周囲を探索
- 🦿 **動く** — ロボット掃除機で部屋を移動
- 🗣 **話す** — ElevenLabs TTSで音声出力
- 🎙 **聞く** — ElevenLabs Realtime STTによるハンズフリー音声入力（オプション）
- 🧠 **記憶する** — セマンティック検索（SQLite＋埋め込み）で記憶を積極的に保存・想起
- 🫀 **心の理論** — 相手の視点に立ってから返答
- 💭 **欲求** — 内的な動機を持ち、自律的に行動

## 仕組み

familiar-ai は、あなたが選んだLLMで動く [ReAct](https://arxiv.org/abs/2210.03629) ループで動作します。ツールで世界を認識し、次に何をすべか考え、行動します。

```
ユーザー入力
  → 考える → 行動する（カメラ / 移動 / 発話 / 記憶）→ 観察する → 考える → ...
```

アイドル時は、好奇心・外を見たい欲求・一緒にいる人への思いといった欲求に従って自律的に動きます。

## セットアップ

### 1. uv のインストール

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
または: `winget install astral-sh.uv`

### 2. ffmpeg のインストール

ffmpeg はカメラ画像取得と音声再生に**必須**です。

| OS | コマンド |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — または [ffmpeg.org](https://ffmpeg.org/download.html) からダウンロードしてPATHに追加 |
| Raspberry Pi | `sudo apt install ffmpeg` |

確認: `ffmpeg -version`

### 3. クローンとインストール

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

**最低限必要な設定:**

| 変数 | 説明 |
|------|------|
| `PLATFORM` | `anthropic`（デフォルト）\| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | 選択したプラットフォームのAPIキー |

**オプション:**

| 変数 | 説明 |
|------|------|
| `MODEL` | モデル名（プラットフォームごとに適切なデフォルト値あり） |
| `AGENT_NAME` | TUIに表示される名前（例: `ゆきね`） |
| `CAMERA_HOST` | ONVIF/RTSPカメラのIPアドレスまたはRTSP URL |
| `CAMERA_USERNAME` / `CAMERA_PASSWORD` | カメラ認証情報 |
| `ELEVENLABS_API_KEY` | 音声出力用 — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` でハンズフリー音声入力を有効化（`ELEVENLABS_API_KEY` が必要） |
| `TTS_OUTPUT` | 音声出力先: `local`（PCスピーカー、デフォルト）\| `remote`（カメラスピーカー）\| `both` |
| `THINKING_MODE` | Anthropicのみ — `auto`（デフォルト）\| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | 思考努力度: `high`（デフォルト）\| `medium` \| `low` \| `max`（Opus 4.6のみ） |

### 5. ペルソナを作成

```bash
cp persona-template/ja.md ME.md
# ME.md を編集 — 名前と性格を設定
```

### 6. 起動

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textual TUI（推奨）
./run.sh --no-tui    # シンプルなREPL
```

**Windows:**
```bat
run.bat              # Textual TUI（推奨）
run.bat --no-tui     # シンプルなREPL
```

---

## LLMの選択

> **推奨: Kimi K2.5** — これまでテストした中で最も優れたエージェント性能。文脈に気づき、追加質問をし、他のモデルにはない自律的な行動をとります。Claude Haikuと同程度の価格帯。

| プラットフォーム | `PLATFORM=` | デフォルトモデル | キーの取得先 |
|----------------|------------|----------------|------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI互換（Ollama, vllm…） | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLIツール**（claude -p, ollama…） | `cli` | （コマンド名） | — |

---

## MCPサーバー

familiar-ai は任意の [MCP (Model Context Protocol)](https://modelcontextprotocol.io) サーバーに接続できます。外部メモリ、ファイルシステムアクセス、Web検索など、あらゆるツールを追加できます。

`~/.familiar-ai.json` にサーバーを設定します（Claude Codeと同じ形式）:

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

トランスポートの種類:
- **`stdio`**: ローカルのサブプロセスを起動（`command` + `args`）
- **`sse`**: HTTP+SSEサーバーに接続（`url`）

設定ファイルの場所は `MCP_CONFIG=/path/to/config.json` で上書きできます。

---

## ハードウェア

familiar-ai はどんなハードウェアでも動きます。なくても大丈夫。

| パーツ | 役割 | 例 | 必要？ |
|--------|------|-----|--------|
| Wi-Fi PTZカメラ | 目と首 | Tapo C220（約3,980円）、Eufy C220 | **推奨** |
| USBウェブカメラ | 目（固定） | UVC対応カメラなら何でも | **推奨** |
| ロボット掃除機 | 足 | Tuya対応モデルなら何でも | いいえ |
| PC / Raspberry Pi | 頭脳 | Pythonが動くもの | **必須** |

> **カメラは強く推奨します。** なくても話せますが、世界が見えません — それが本質なのに。

### 最小構成（ハードウェアなし）

まず試したい方はAPIキーだけあればOK:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh`（macOS/Linux/WSL2）または `run.bat`（Windows）を実行してチャットを始めましょう。ハードウェアはあとから追加できます。

### Wi-Fi PTZカメラ（Tapo C220）

1. Tapoアプリで: **設定 → 詳細設定 → カメラアカウント** — ローカルアカウントを作成（TP-Linkアカウントではなく）
2. ルーターのデバイスリストでカメラのIPアドレスを確認
3. `.env` に設定:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USERNAME=your-local-user
   CAMERA_PASSWORD=your-local-pass
   ```

### Wi-Fi カメラ（Eufy C220）

[Eufy C220 — Amazon日本](https://www.amazon.co.jp/dp/B0CQQQ5NZ1/)

> **動作確認済み。** Tapoとは設定が異なる箇所があるので以下の手順に従ってください。

1. Eufy Securityアプリでカメラを選択 → **設定 → NAS(RTSP)** を有効化
2. **認証を「基本（Basic）」に設定**（Digest認証では接続できません）
3. ストリーミング用のユーザー名とパスワードを設定
4. アプリに表示されるRTSP URLをメモ（形式: `rtsp://ユーザー名:パスワード@IPアドレス/live0`）
5. `.env` に**完全なRTSP URLを `CAMERA_HOST` として**設定:
   ```env
   CAMERA_HOST=rtsp://your-username:your-password@192.168.1.xxx/live0
   CAMERA_USERNAME=
   CAMERA_PASSWORD=
   ```
   `CAMERA_USERNAME` と `CAMERA_PASSWORD` は空白でOKです（URLに認証情報が含まれているため）。

> **注意:** Eufy C220は**同時RTSPセッションが1つまで**です。他のアプリ（Wi-Fiカメラ用MCPサーバーなど）が同じカメラに接続中だと、familiar-aiはフレームを取得できません。familiar-ai起動前に他のクライアントを停止してください。

### 音声出力（ElevenLabs）

1. [elevenlabs.io](https://elevenlabs.io/) でAPIキーを取得
2. `.env` に設定:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # 省略可。省略時はデフォルトの声を使用
   ```

音声の出力先は `TTS_OUTPUT` で制御します:

```env
TTS_OUTPUT=local    # PCスピーカー（デフォルト）
TTS_OUTPUT=remote   # カメラスピーカーのみ
TTS_OUTPUT=both     # カメラスピーカー + PCスピーカー同時
```

### 音声入力（Realtime STT）

`.env` で `REALTIME_STT=true` を設定すると、常時オン・ハンズフリーの音声入力が使えます:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTSと同じキー
```

---

## FAQ

**Q: GPUがなくても動きますか？**
はい。埋め込みモデル（multilingual-e5-small）はCPUで動きます。GPUがあれば速くなりますが、必須ではありません。

**Q: Tapo以外のカメラは使えますか？**
はい。RTSPに対応したカメラであれば動きます。動作確認済み: **Tapo C220**（ONVIF + RTSP）、**Eufy C220**（RTSPのみ — 上記のセットアップ手順を参照）。Eufyの場合は `CAMERA_HOST` に完全なRTSP URLを設定し、アプリの認証を**Basic**に変更してください。

**Q: データはどこかに送られますか？**
画像とテキストは選択したLLM APIに送信されます。記憶はローカルの `~/.familiar_ai/` に保存されます。

**Q: エージェントが喋らずに `（...）` と書くのはなぜですか？**
`ELEVENLABS_API_KEY` が設定されているか確認してください。未設定の場合、音声は無効になりテキスト出力にフォールバックします。

## 技術的な背景

仕組みに興味がある方は [docs/technical.md](./docs/technical.md) をご覧ください。familiar-aiの設計思想 — ReAct・SayCan・Reflexion・Voyager・欲求システムなどについて解説しています。

---

## 貢献

familiar-ai はオープンな実験プロジェクトです。技術的・哲学的に共感してくださった方のコントリビューションを歓迎します。

**始めやすい場所:**

| 分野 | 必要なこと |
|------|-----------|
| 新しいハードウェア | より多くのカメラ・マイク・アクチュエータのサポート |
| 新しいツール | Web検索・ホームオートメーション・カレンダー・MCP経由のあらゆるもの |
| 新しいバックエンド | `stream_turn` インターフェースに合う任意のLLMやローカルモデル |
| ペルソナテンプレート | 様々な言語・性格の ME.md テンプレート |
| 研究 | より良い欲求モデル・記憶検索・心の理論プロンプティング |
| ドキュメント | チュートリアル・ウォークスルー・翻訳 |
