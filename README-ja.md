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
- 🧠 **覚える** — 観察を意味検索つきで保存（SQLite + embedding）
- 💭 **欲求を持つ** — 好奇心や寂しさなど、自発的に行動するドライブ

## しくみ

Claude（Anthropic）を使った[ReAct](https://arxiv.org/abs/2210.03629)ループで動いています。ツールを通じて世界を知覚し、次の行動を考え、実行します。

放っておくと欲求に従って自発的に動きます。「外が気になる」「コウタはどこだろう」など。

## はじめかた

### 必要なもの

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- Anthropic APIキー
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
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) で取得 |
| `TAPO_CAMERA_HOST` | Wi-FiカメラのIPアドレス（任意） |
| `ELEVENLABS_API_KEY` | 音声出力を使う場合（任意） |

全項目の説明は [`.env.example`](./.env.example) を参照。

### 使い魔を作る

```bash
cp persona-template/ja.md ME.md
# ME.md を編集 — 名前と性格を書く
```

### 起動

```bash
uv run familiar
```

## 使い魔の性格（ME.md）

使い魔の性格は `ME.md` に書きます。このファイルは `.gitignore` 済みなので、コミットされません。

[`persona-template/ja.md`](./persona-template/ja.md) に記入例があります。

## ハードウェア

市販の安価なハードウェアで動きます。

| パーツ | 役割 | 例 |
|--------|------|-----|
| Wi-Fi PTZカメラ | 目・首 | Tapo C220（約3,980円） |
| 掃除機ロボット | 足 | Tuya対応モデル |
| PC / ラズパイ | 脳 | Pythonが動けばなんでも |

## ライセンス

MIT
