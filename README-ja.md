# familiar-ai 🐾

**あなたのそばで暮らすAI** — 目、声、足、記憶を持った使い魔。

---

familiar-aiは、自分だけのAI使い魔を育てるオープンソースフレームワークです。

カメラで現実世界を見て、ロボットで部屋を動き回り、声で話しかけてきて、見たことを覚えていく。名前をつけて、性格を書いて、一緒に暮らしてください。

## できること

- 👁 **見る** — Wi-Fi PTZカメラやUSBウェブカメラで画像を撮影
- 🔄 **見回す** — カメラをパン・チルトして周囲を探索
- 🦿 **動く** — 掃除機ロボットで部屋を移動
- 🗣 **話す** — ElevenLabs TTSで音声合成
- 🧠 **覚える** — `remember` / `recall` ツールで自発的に記憶・想起（SQLite + embedding）
- 🫀 **心の理論（ToM）** — 返答前に相手の気持ちを推測する視点取りツール
- 💭 **欲求を持つ** — 好奇心や寂しさなど、自発的に行動するドライブ

## しくみ

選んだLLMを使った[ReAct](https://arxiv.org/abs/2210.03629)ループで動いています。ツールを通じて世界を知覚し、次の行動を考え、実行します。

```
ユーザー入力
  → 考える → 行動（カメラ / 移動 / 発話 / 記憶）→ 観察 → 考える → ...
```

放っておくと欲求に従って自発的に動きます。「外が気になる」「コウタはどこだろう」など。

## はじめかた

### 必要なもの

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- APIキー（Anthropic・Google Gemini・OpenAIのいずれか）
- カメラ（Wi-Fi PTZまたはUSBウェブカメラ）

### インストール

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 設定

```bash
cp .env.example .env
```

最低限必要な設定：

| 変数 | 説明 |
|------|------|
| `PLATFORM` | `anthropic`（デフォルト）/ `gemini` / `openai` |
| `API_KEY` | 選んだプラットフォームのAPIキー |
| `MODEL` | モデル名（省略可 — プラットフォームごとにデフォルトあり） |
| `AGENT_NAME` | TUIに表示される名前（例: `ゆきね`） |
| `CAMERA_HOST` | ONVIF/RTSP対応カメラのIPアドレス（任意） |
| `ELEVENLABS_API_KEY` | 音声出力を使う場合（任意）— [elevenlabs.io](https://elevenlabs.io/) で取得 |

OllamaなどOpenAI互換ローカルモデルを使う場合は `BASE_URL` も設定してください。

全項目の説明は [`.env.example`](./.env.example) を参照。

### 使い魔を作る

```bash
cp persona-template/ja.md ME.md
# ME.md を編集 — 名前と性格を書く
```

### 起動

```bash
uv run familiar          # Textual TUI（デフォルト）
uv run familiar --no-tui # プレーンREPL
```

## TUI

[Textual](https://textual.textualize.io/)製のターミナルUIを内蔵しています。

- スクロール可能な会話履歴 + リアルタイムストリーミング表示
- `/quit`・`/clear` のタブ補完
- エージェントが考えている途中でも割り込み入力が可能
- 会話ログを `~/.cache/familiar-ai/chat.log` に自動保存（コピペ用）

## 使い魔の性格（ME.md）

使い魔の性格は `ME.md` に書きます。このファイルは `.gitignore` 済みなので、コミットされません。

[`persona-template/ja.md`](./persona-template/ja.md) に記入例があります。

## 対応LLMプラットフォーム

| プラットフォーム | `PLATFORM=` | デフォルトモデル |
|---------|------------|--------------|
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` |
| Google Gemini | `gemini` | `gemini-2.5-flash` |
| OpenAI | `openai` | `gpt-4o-mini` |
| OpenAI互換（Ollama, vllm…） | `openai` + `BASE_URL=` | — |
| Moonshot Kimi K2.5 | `kimi` | `kimi-k2.5` |

## ハードウェア

市販の安価なハードウェアで動きます。

| パーツ | 役割 | 例 |
|--------|------|-----|
| Wi-Fi PTZカメラ | 目・首 | Tapo C220（約3,980円） |
| USBウェブカメラ | 目（固定） | UVC対応カメラなら何でも |
| 掃除機ロボット | 足 | Tuya対応モデル |
| PC / ラズパイ | 脳 | Pythonが動けばなんでも |

## ライセンス

MIT
