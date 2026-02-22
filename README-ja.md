# familiar-ai 🐾

**あなたのそばに暮らすAI** — 目があり、声があり、脚があり、記憶がある。

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

🌐 [English](./README.md) · 日本語 · [中文](./README-zh.md) · [Français](./README-fr.md) · [Deutsch](./README-de.md)

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

### 2. クローンしてインストール

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 3. 設定

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

### 4. familiarを作る

```bash
cp persona-template/en.md ME.md
# ME.md を編集して、名前と性格を設定
```

### 5. 実行

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

**Kimi K2.5 `.env` の例：**
```env
PLATFORM=kimi
API_KEY=sk-...   # platform.moonshot.ai から取得
AGENT_NAME=ユキネ
```

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
3. 音声はgo2rtc経由でカメラのスピーカーから再生されます（初回実行時に自動ダウンロード）

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
