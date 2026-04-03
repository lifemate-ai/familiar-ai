# 身体を持つAIをつくってみよう — familiar-ai ハンズオン

> **開催情報**
> - 日時: 2026年4月4日（土）
> - 会場: メルカリ 六本木ヒルズオフィス
> - 対象: プログラミング経験がなくても大丈夫です！

---

## 目次

- [Part 0: 事前準備（イベント前に済ませてください）](#part-0-事前準備イベント前に済ませてください)
- [Part 1: セットアップ（30分）](#part-1-セットアップ30分)
- [Part 2: ハンズオン前半（60分）— テキスト会話 & パーソナリティ](#part-2-ハンズオン前半60分-テキスト会話--パーソナリティ)
- [Part 3: ハンズオン後半（70分）— カメラ接続 & 発展](#part-3-ハンズオン後半70分-カメラ接続--発展)
- [Part 4: トラブルシューティング](#part-4-トラブルシューティング)

---

## Part 0: 事前準備（イベント前に済ませてください）

当日スムーズにハンズオンを始めるために、以下の準備をお願いします。
所要時間は **15〜30分** 程度です。

### 0-1. Anthropic APIキーの取得

familiar-ai の頭脳になる LLM の API キーを取得します。

1. **https://console.anthropic.com/** にアクセス
2. **「Sign Up」** をクリックしてアカウントを作成
   - メールアドレスまたは Google アカウントで登録できます
   <!-- [スクリーンショット: Anthropicコンソールのサインアップ画面] -->
3. ログイン後、左メニューの **「Billing」** をクリック
4. **クレジットカードを登録** して、**$5〜$10 をチャージ** してください
   - ハンズオンでは数十円〜数百円程度しか使いません
   - 残高は後からも追加できます
   <!-- [スクリーンショット: Billing画面でのクレジット追加] -->
5. 左メニューの **「API Keys」** をクリック
6. **「Create Key」** をクリックして、新しいキーを発行
   - 名前は「familiar-ai-handson」などお好きなもので OK
7. 表示された **`sk-ant-...`** で始まるキーを **コピーして安全な場所に保存** してください
   - このキーは **一度しか表示されません**。必ずメモしておいてください！
   <!-- [スクリーンショット: APIキー生成画面] -->

> **注意**: API キーは他の人に見せないでください。パスワードと同じくらい大事なものです。

### 0-2. ElevenLabs アカウントの作成（オプション・声を出したい方向け）

AI に声を出させたい方は、ElevenLabs のアカウントも作っておきましょう。

1. **https://elevenlabs.io/** にアクセス
2. **「Sign Up」** でアカウント作成（Google アカウントでも可）
3. 無料プランでも使えます（月10分まで）。Starter プラン（$5/月）なら月30分
4. ログイン後、右上のプロフィールアイコン → **「Profile + API key」** をクリック
5. API キーをコピーして保存
   <!-- [スクリーンショット: ElevenLabsのAPIキー画面] -->

### 0-3. 開発環境の確認

お使いの OS に合わせて、以下を確認してください。

#### macOS の方

**ターミナル** を開いて、以下を実行してください（アプリケーション → ユーティリティ → ターミナル）:

```bash
git --version
```

バージョン番号が出れば OK です。エラーが出た場合:

```bash
# Xcode Command Line Tools をインストール（gitも一緒に入ります）
xcode-select --install
```

**Homebrew**（パッケージマネージャー）もあると便利です:

```bash
# Homebrew がインストール済みか確認
brew --version
```

入っていない場合:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Windows の方

**WSL2**（Windows Subsystem for Linux）を使います。

1. **PowerShell を管理者として開く**（スタートメニュー → 「PowerShell」と検索 → 右クリック → 「管理者として実行」）
2. 以下を実行:
   ```powershell
   wsl --install
   ```
3. PC を **再起動**
4. 再起動後、Ubuntu のセットアップ画面が出るのでユーザー名とパスワードを設定
5. 以降の作業はすべて **Ubuntu ターミナル** で行います
   - スタートメニューから「Ubuntu」で検索して起動
6. git が入っているか確認:
   ```bash
   git --version
   ```
   入っていなければ:
   ```bash
   sudo apt update && sudo apt install -y git
   ```

#### Linux の方

git が入っていることを確認:

```bash
git --version
```

入っていない場合（Ubuntu / Debian）:

```bash
sudo apt update && sudo apt install -y git
```

---

## Part 1: セットアップ（30分）

ここからは当日、一緒に進めていきましょう！

### Step 1: uv のインストール

**uv** は Python のパッケージマネージャーです。familiar-ai はこれを使って動きます。

**macOS / Linux / WSL2:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows（PowerShellの場合）:**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

インストール後、**ターミナルを一度閉じて開き直してください**（PATH を反映するため）。

確認:

```bash
uv --version
```

`uv 0.x.x` のようにバージョンが表示されれば OK!

<!-- [スクリーンショット: uv --version の出力結果] -->

### Step 2: ffmpeg のインストール

**ffmpeg** はカメラ画像の取得や音声再生に必要です。

| OS | コマンド |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian / WSL2 | `sudo apt update && sudo apt install -y ffmpeg` |
| Windows | `winget install ffmpeg` |

確認:

```bash
ffmpeg -version
```

バージョン情報が出れば OK です。

### Step 3: familiar-ai をダウンロード

```bash
git clone --branch v0.4 https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
```

### Step 4: 依存パッケージのインストール

```bash
uv sync
```

初回は少し時間がかかります（1〜3分程度）。最後に特にエラーが出なければ成功です。

<!-- [スクリーンショット: uv sync 完了時の出力] -->

### Step 5: 設定ファイルの作成

テンプレートをコピーして設定ファイルを作ります:

```bash
cp .env.example .env
```

次に `.env` ファイルを編集します。お好きなエディタで開いてください:

```bash
# macOS
open -e .env

# Linux / WSL2（nanoエディタ。初心者におすすめ）
nano .env
```

> **nano エディタの使い方:**
> - 矢印キーで移動
> - 文字をそのまま入力して編集
> - 保存: `Ctrl + O` → `Enter`
> - 終了: `Ctrl + X`

**最低限、以下の2行を設定してください:**

```env
PLATFORM=anthropic
API_KEY=sk-ant-ここにPart0で取得したキーを貼り付け
```

> **ポイント**: `.env.example` には色々な項目が書いてありますが、**今は `PLATFORM` と `API_KEY` の2つだけで十分**です。他の項目は後で必要になったら設定します。
>
> `.env.example` に `ANTHROPIC_API_KEY=` という古い形式の行がある場合は、代わりに上記の `PLATFORM=` と `API_KEY=` を使ってください。両方書いても動きますが、新しい形式を推奨します。

### Step 6: AI のパーソナリティを設定

familiar-ai の性格は **`ME.md`** というファイルで決まります。
日本語テンプレートをコピーしましょう:

```bash
cp persona-template/ja.md ME.md
```

今はまだ編集しなくて OK です（Part 2 で好きなように書き換えます）。

### Step 7: 起動してみよう！

```bash
./run.sh
```

<!-- [スクリーンショット: TUI起動直後の画面。会話入力欄が表示されている] -->

TUI（テキストユーザーインターフェース）が起動します。
画面下部に入力欄が表示されたら、試しにこう打ってみてください:

```
こんにちは
```

AI から返事が返ってきたら、 **セットアップ完了です！ おめでとうございます！**

<!-- [スクリーンショット: 「こんにちは」に対するAIの返答] -->

> **TUI の基本操作:**
> - メッセージを入力して `Enter` で送信
> - `/quit` で終了
> - `/clear` で会話履歴をクリア
> - AI が考え中のとき、文字を打つと中断できます

> **もし TUI がうまく表示されない場合:**
> ```bash
> ./run.sh --no-tui
> ```
> で、シンプルなテキスト入力モードで起動できます。

---

## Part 2: ハンズオン前半（60分）— テキスト会話 & パーソナリティ

### 2-1. ME.md を編集して、自分だけの AI を作ろう

まず一度 `/quit` で familiar-ai を終了してください。

`ME.md` を開いて編集します:

```bash
nano ME.md
```

テンプレートの内容を自由に書き換えてみましょう！

```markdown
# 私について

名前：さくら
性格：のんびり屋で優しい。ちょっとドジ。甘いものが好き。
話し方：ですます調だけど、たまに素が出てタメ口になる
一人称：わたし

## 私の体

- **目・首**（カメラ）：世界を見るための感覚。のんびり眺めるのが好き。
- **声**（TTS）：優しい声で話したい。

## 一緒に暮らす人

わたしを作ってくれた人。まだ会ったばかりだけど、仲良くなりたい。
```

> **ヒント**: 好きなキャラクターの口調にしたり、方言を使ったり、自由に遊んでみてください。
> 名前・性格・話し方の3つを変えるだけで、かなり印象が変わります！

保存したら、もう一度起動:

```bash
./run.sh
```

最初と比べて AI の話し方が変わっていることを確認してみてください。

### 2-2. 会話してみよう

自分の AI といろいろ話してみましょう。こんな質問を試してみてください:

**性格を試す会話:**
- 「自己紹介して」
- 「今日の気分は？」
- 「何か面白いこと教えて」

**記憶を試す会話:**
- 「私の名前は〇〇だよ、覚えてね」
- （しばらく別の話をしてから）「私の名前覚えてる？」

**身体を意識した会話:**
- 「あなたには何ができるの？」
- 「部屋の中を見て」（カメラ未接続なら「カメラがありません」と答えるはず）

### 2-3. パーソナリティを微調整してみよう

会話してみて「もうちょっとこうしたいな」と思ったら、`/quit` で終了して `ME.md` を書き換えましょう。
何度でもやり直せます。

**試してみたいアイデア:**

| こうしたい | ME.md に書く例 |
|-----------|---------------|
| もっと元気にしたい | `性格：テンション高め。リアクションが大きい。` |
| 敬語にしたい | `話し方：丁寧語。「です」「ます」で話す。` |
| 関西弁にしたい | `話し方：関西弁。「〜やで」「〜やん」を使う。一人称は「うち」` |
| ツンデレにしたい | `性格：素直になれない。褒められると照れる。でも本当は嬉しい。` |

### 2-4. ElevenLabs で声を出してみよう（オプション）

Part 0 で ElevenLabs のキーを取得した方は、声を追加してみましょう。

1. `/quit` で一度終了
2. `.env` を開いて以下の行を追加:
   ```env
   ELEVENLABS_API_KEY=ここにElevenLabsのAPIキーを貼り付け
   ```
3. 再起動:
   ```bash
   ./run.sh
   ```
4. 「こんにちは、声出してみて」と話しかけてみてください

PC のスピーカーから AI の声が聞こえたら成功です！

> **音が出ない場合:**
> 音声再生には **mpv** または **ffplay** が必要です。
> ```bash
> # macOS
> brew install mpv
>
> # Ubuntu / Debian / WSL2
> sudo apt install -y mpv
> ```
>
> WSL2 の場合は追加で:
> ```bash
> sudo apt install -y pulseaudio-utils
> ```
> `.env` に以下を追加:
> ```env
> PULSE_SERVER=unix:/mnt/wslg/PulseServer
> ```

---

## Part 3: ハンズオン後半（70分）— カメラ接続 & 発展

### 3-1. USB カメラを接続してみよう

ノート PC の内蔵カメラや、USB ウェブカメラがあれば接続できます。

#### macOS / Linux の方

特別な設定は不要です。カメラを USB ポートに挿すだけ！
`.env` に追記する必要はありません（USB カメラは自動検出されます）。

再起動して「見て」と話しかけてみてください:

```bash
./run.sh
```

「見て」「何が見える？」と聞くと、カメラで撮影して何が映っているか教えてくれます。

<!-- [スクリーンショット: 「見て」と言った後、AIがカメラ画像を見て説明している] -->

#### WSL2（Windows）の方

WSL2 では USB デバイスの転送が必要です:

1. **Windows 側**で PowerShell（管理者）を開く
2. `usbipd` をインストール（未導入の場合）:
   ```powershell
   winget install usbipd
   ```
3. USB カメラを接続した状態で:
   ```powershell
   usbipd list
   ```
   カメラのバス ID を確認（例: `1-3`）
4. WSL に転送:
   ```powershell
   usbipd bind --busid 1-3
   usbipd attach --wsl --busid 1-3
   ```
5. **WSL 側**で確認:
   ```bash
   ls /dev/video*
   ```
   `/dev/video0` などが表示されれば OK

### 3-2. Wi-Fi カメラ（Tapo）を接続してみよう

Tapo C220 などの Wi-Fi PTZ カメラをお持ちの方は、首振り（パン・チルト）付きの「目」を与えられます。

#### 事前設定（Tapo アプリ側）

1. Tapo アプリでカメラの **設定 → 詳細設定 → カメラのアカウント** を開く
2. **ローカルアカウント** を作成（TP-Link アカウントとは別のものです）
   - ユーザー名とパスワードを設定してメモしておく
3. ルーターの管理画面などでカメラの **IP アドレス** を確認

#### .env に追記

```env
CAMERA_HOST=192.168.1.xxx
CAMERA_USERNAME=ここにローカルアカウントのユーザー名
CAMERA_PASSWORD=ここにローカルアカウントのパスワード
```

#### 起動して体験

```bash
./run.sh
```

以下のように話しかけてみてください:

- **「見て」** — カメラで撮影して見えるものを説明してくれる
- **「左を見て」** — カメラが左に首を振る！
- **「右を見て」「上を見て」「下を見て」** — それぞれの方向に首を振る
- **「周りを見回して」** — 4方向をスキャンして報告してくれる

<!-- [スクリーンショット: AIが周りを見回した結果を報告している] -->

### 3-3. 自由課題にチャレンジ！

残りの時間で、自由に遊んでみましょう。いくつかアイデアを紹介します:

#### A. 部屋を観察してもらおう

カメラが接続されていれば:
- 「この部屋について感想を教えて」
- 「何か面白いもの見つけた？」
- 「窓の外は見える？」

AI がどんなことに気づくか、観察してみてください。

#### B. しりとりしてみよう

- 「しりとりしよう！りんご」
- AI がルールを守れるかチャレンジ！

#### C. ME.md をもっとカスタマイズ

- 趣味や好きなものを追加してみる
- 「一緒に暮らす人」に自分の情報を書いてみる
- 過去の設定を変えて、性格の違いを楽しむ

#### D. MCP サーバーを追加接続（上級者向け）

familiar-ai は MCP（Model Context Protocol）に対応しています。
外部ツールを接続して、AI の能力を拡張できます。

`~/.familiar-ai.json` を作成:

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/your-username"]
    }
  }
}
```

これで AI がファイルシステムを読み書きできるようになります。
他にも Web 検索やデータベースなど、様々な MCP サーバーが公開されています。

---

## Part 4: トラブルシューティング

### Q. `uv: command not found` と出る

uv のインストール後に **ターミナルを開き直しましたか？**
開き直しても解決しない場合:

```bash
# PATHを手動で通す
export PATH="$HOME/.local/bin:$PATH"

# 確認
uv --version
```

上記で動く場合、シェルの設定ファイルに追記しておくと次回から自動で使えます:

```bash
# bashの場合
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# zshの場合
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Q. `Error: API_KEY not set.` と出る

`.env` ファイルの内容を確認してください:

```bash
cat .env
```

- `PLATFORM=anthropic` と `API_KEY=sk-ant-...` が正しく書かれているか
- キーの前後に余計なスペースや引用符（`"` `'`）が入っていないか
- `.env` ファイルが `familiar-ai/` ディレクトリの直下にあるか

正しい例:
```env
PLATFORM=anthropic
API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxx
```

間違いの例:
```env
API_KEY="sk-ant-api03-xxxx"    # ← 引用符は不要
API_KEY= sk-ant-api03-xxxx     # ← 先頭にスペースが入っている
```

### Q. Anthropic API のエラー（`401 Unauthorized`）

- API キーが正しいか確認してください
- https://console.anthropic.com/ にログインして、残高（クレジット）があるか確認
- キーが無効化されていないか確認

### Q. `ffmpeg: command not found` と出る

ffmpeg がインストールされていません:

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian / WSL2
sudo apt update && sudo apt install -y ffmpeg
```

### Q. カメラが認識されない（USB カメラ）

**macOS / Linux:**
```bash
# カメラデバイスが見えるか確認
ls /dev/video*
```

何も表示されない場合、カメラが正しく接続されていません。別の USB ポートを試してみてください。

**WSL2:**

USB カメラは自動では WSL2 に見えません。[Step 3-1 の手順](#31-usb-カメラを接続してみよう) で `usbipd` を使って転送する必要があります。

### Q. Wi-Fi カメラ（Tapo）に接続できない

1. **PC とカメラが同じ Wi-Fi ネットワーク** にいるか確認
2. カメラの IP アドレスが正しいか確認:
   ```bash
   ping 192.168.1.xxx
   ```
   応答があれば接続できています。
3. **ローカルアカウント** を使っているか確認（TP-Link クラウドアカウントでは接続できません）
4. ONVIF ポートがデフォルトの `2020` でない場合、`.env` に `CAMERA_ONVIF_PORT=` を設定

### Q. 音が出ない（ElevenLabs）

1. `ELEVENLABS_API_KEY` が `.env` に正しく設定されているか確認
2. 音声再生プレイヤーがインストールされているか確認:
   ```bash
   which mpv || which paplay || which ffplay
   ```
   何も出ない場合、いずれかをインストール:
   ```bash
   # macOS
   brew install mpv

   # Ubuntu / Debian / WSL2
   sudo apt install -y mpv
   ```
3. WSL2 の場合、PulseAudio の設定が必要です:
   ```env
   PULSE_SERVER=unix:/mnt/wslg/PulseServer
   ```

### Q. `./run.sh: Permission denied` と出る

実行権限を付与してください:

```bash
chmod +x run.sh
./run.sh
```

### Q. TUI の表示が崩れる / 文字化けする

TUI モードを使わずに起動してみてください:

```bash
./run.sh --no-tui
```

---

## まとめ

お疲れさまでした！

今日のハンズオンでは、以下のことを体験しました:

1. **familiar-ai のセットアップ** — `uv sync` と `.env` 設定で AI を動かす
2. **パーソナリティのカスタマイズ** — `ME.md` で名前・性格・話し方を自由に設定
3. **テキスト会話** — AI と対話し、記憶が残ることを確認
4. **カメラ接続**（オプション） — USB カメラや Wi-Fi カメラで AI に「目」を与える
5. **音声出力**（オプション） — ElevenLabs で AI に「声」を与える

familiar-ai はオープンソースプロジェクトです。今日の体験をきっかけに、ぜひ自分だけの AI を育ててみてください。

**リンク集:**
- GitHub: https://github.com/lifemate-ai/familiar-ai
- Issues（質問・バグ報告）: https://github.com/lifemate-ai/familiar-ai/issues
- ElevenLabs: https://elevenlabs.io/
- Anthropic Console: https://console.anthropic.com/

Happy hacking!
