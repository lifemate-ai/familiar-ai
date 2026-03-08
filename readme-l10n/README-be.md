[→ English README](../README.md)

# familiar-ai 🐾

**Штучны інтэлект, які жыве побач з вамі** — з вачыма, голасам, нагамі і памяццю.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Даступна на 74 мовах](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai — гэта суправаджальны ШІ, які жыве ў вашым доме. Настройце яго за некалькі хвілін. Код не патрабуецца.

Ён успрымае рэальны свет праз камеры, рухаецца на целе робата, гаворыць вухам і запамінае тое, што бачыць. Дайце яму імя, напішыце яго асобы і дазвольце яму жыць з вамі.

## Што ён можа зрабіць

- 👁 **Відзіць** — захоплівае выявы з Wi-Fi PTZ камеры або USB вэб-камеры
- 🔄 **Агляд** — панарама і нахіл камеры для даследавання наваколля
- 🦿 **Рухацца** — кіруе робатам-пыласосам, каб пакутаваць па пакоі
- 🗣 **Гаварыць** — гаворыць праз ElevenLabs TTS
- 🎙 **Слухаць** — бездрадзьджавае галасавое ўводзіна праз ElevenLabs Realtime STT (опцыя)
- 🧠 **Запамінаць** — актыўна захоўвае і ўспамінае ўспаміны з семантычным пошукам (SQLite + укладкі)
- 🫀 **Тэорыя розуму** — прымае перспектыву іншага чалавека перад тым, як адказаць
- 💭 **Жаданне** — мае ўласныя ўнутраныя імпульсы, якія выклікаюць аўтаномнае паводзіны

## Як гэта працуе

familiar-ai запускае цыкл [ReAct](https://arxiv.org/abs/2210.03629), падтрымліваючы выбраны вамі LLM. Ён успрымае свет праз інструменты, разважае, што рабіць наступным, і дзейнічае — так, як гэта зрабіў бы чалавек.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Калі бездзейны, ён дзейнічае з уласнымі жаданнямі: цікаўнасць, жаданне паглядзець вонкі, адсутнасць чалавека, з якім ён жыве.

## Як пачаць

### 1. Устанавіце uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Або: `winget install astral-sh.uv`

### 2. Устанавіце ffmpeg

ffmpeg з'яўляюцца **неабходнымі** для захопу вобразаў з камеры і адтворэння гуку.

| OS | Каманда |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — або загрузіце з [ffmpeg.org](https://ffmpeg.org/download.html) і дадайце ў PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Праверце: `ffmpeg -version`

### 3. Клануйце і ўсталюйце

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Наладзьце

```bash
cp .env.example .env
# Рэдагуйце .env з вашымі наладамі
```

**Мінімальныя патрабаванні:**

| Пераменная | Апісанне |
|------------|-----------|
| `PLATFORM` | `anthropic` (па змаўчанні) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Ваш API ключ для абранай платформы |

**Неабавязкова:**

| Пераменная | Апісанне |
|------------|-----------|
| `MODEL` | Імя мадэлі (разумныя значэнні па змаўчанні для кожнай платформы) |
| `AGENT_NAME` | Выяўленае імя, якое паказваецца ў TUI (напрыклад, `Yukine`) |
| `CAMERA_HOST` | IP-адрас вашай ONVIF/RTSP камеры |
| `CAMERA_USER` / `CAMERA_PASS` | Уліковыя дадзеныя камеры |
| `ELEVENLABS_API_KEY` | Для выводу голасу — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, каб уключыць вечна ўключаны бездрадзьджавае галасавое ўводзіна (патрабуе `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Дзе прайграць аўдыё: `local` (PC дынамік, па змаўчанні) \| `remote` (камерны дынамік) \| `both` |
| `THINKING_MODE` | Толькі Anthropic — `auto` (па змаўчанні) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Адаптыўная намаганне думаць: `high` (па змаўчанні) \| `medium` \| `low` \| `max` (толькі Opus 4.6) |

### 5. Стварыце свайго знаёмага

```bash
cp persona-template/en.md ME.md
# Рэдагуйце ME.md — дайце яму імя і асобы
```

### 6. Запусціце

**macOS / Linux / WSL2:**
```bash
./run.sh             # Тэкставы TUI (рэкамендуецца)
./run.sh --no-tui    # Просты REPL
```

**Windows:**
```bat
run.bat              # Тэкставы TUI (рэкамендуецца)
run.bat --no-tui     # Просты REPL
```

---

## Выбар LLM

> **Рэкамендуецца: Kimi K2.5** — лепшая агентная прадукцыйнасць, якая была праверана дагэтуль. Заўважае кантэкст, задае пытанні, актыўна дзейнічае так, як не робяць іншыя мадэлі. Кошт падобны да Claude Haiku.

| Платформа | `PLATFORM=` | Дэфолтная мадэль | Дзе атрымаць ключ |
|-----------|-------------|-------------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Сумяшчальныя з OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (мультыправайдэр) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI інструмент** (claude -p, ollama…) | `cli` | (каманда) | — |

**Прыклад `.env` для Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # з platform.moonshot.ai
AGENT_NAME=Yukine
```

**Прыклад `.env` для Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # з api.z.ai
MODEL=glm-4.6v   # з магчымасцю візуалізацыі; glm-4.7 / glm-5 = толькі тэкст
AGENT_NAME=Yukine
```

**Прыклад `.env` для Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # з aistudio.google.com
MODEL=gemini-2.5-flash  # або gemini-2.5-pro для большай магчымасці
AGENT_NAME=Yukine
```

**Прыклад `.env` для OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # з openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # неабавязкова: спецыфікацыя мадэлі
AGENT_NAME=Yukine
```

> **Заўвага:** Для дэактывацыі мясцовых/NVIDIA мадэляў проста не ўсталюйце `BASE_URL` на мясцовы канец, такі як `http://localhost:11434/v1`. Выкарыстоўвайце хмарныя пастаўшчыкі замест гэтага.

**Прыклад `.env` для CLI інструмента:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = аргумент для запыту
# MODEL=ollama run gemma3:27b  # Ollama — без {}, запыт перадаецца праз stdin
```

---

## MCP серверы

familiar-ai можа падключацца да любога сервера [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Гэта дазваляе вам падключыць знешнюю памяць, доступ да файлавай сістэмы, вэб-пошук або любы іншы інструмент.

Наладзьце серверы ў `~/.familiar-ai.json` (той жа фармат, што і Claude Code):

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

Падтрымліваюцца два тыпы транспарціроўкі:
- **`stdio`**: запуск мясцовага падпрацэсу (`command` + `args`)
- **`sse`**: падключэнне да HTTP+SSE сервера (`url`)

Перазапісвайце месца файла канфігурацыі з дапамогай `MCP_CONFIG=/path/to/config.json`.

---

## Абсталяванне

familiar-ai працуе з любым абсталяваннем, якое вы маеце — або зусім без яго.

| Частка | Што яна робіць | Прыкладанне | Абавязкова? |
|--------|----------------|--------------|-------------|
| Wi-Fi PTZ камера | Вочы + шыя | Tapo C220 (~$30, Eufy C220) | **Рэкамендуецца** |
| USB вэб-камера | Вочы (фіксаваная) | Любы UVC камера | **Рэкамендуецца** |
| Робат-пыласос | Ногі | Любы мадэль, сумяшчальны з Tuya | Не |
| ПК / Raspberry Pi | Мозг | Усё, што працуе на Python | **Так** |

> **Камера настойліва рэкамендуецца.** Без яе familiar-ai можа ўсё роўна казаць — але ён не можа бачыць свету, што, па сутнасці, і ёсць сэнс.

### Мінімальная ўстаноўка (без абсталявання)

Простае жаданне паспрабаваць? Вам патрэбен толькі API ключ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Запусціце `./run.sh` (macOS/Linux/WSL2) або `run.bat` (Windows) і пачніце размаўляць. Дадавайце абсталяванне па меры неабходнасці.

### Wi-Fi PTZ камера (Tapo C220)

1. У прыкладанні Tapo: **Настройкі → Дадатковае → Уліковы запіс камеры** — стварыце лакальны акаўнт (не акаўнт TP-Link)
2. Знайдзіце IP камеры ў спісе прылад вашага маршрутизатара.
3. Усталюйце ў `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Wi-Fi Camera (Eufy C220)

[Eufy C220 on Amazon Japan](https://www.amazon.co.jp/dp/B0CQQQ5NZ1/)

> **Tested and confirmed working.** Follow these steps carefully — a few settings differ from Tapo.

1. In the Eufy Security app: go to the camera → **Settings → NAS(RTSP)** and enable it
2. Set **Authentication** to **Basic** (Digest authentication does NOT work)
3. Set a streaming username and password
4. Note the RTSP URL shown in the app (format: `rtsp://username:password@ip/live0`)
5. Set in `.env` — use the **full RTSP URL** as `CAMERA_HOST`:
   ```env
   CAMERA_HOST=rtsp://your-username:your-password@192.168.1.xxx/live0
   CAMERA_USERNAME=
   CAMERA_PASSWORD=
   ```
   Leave `CAMERA_USERNAME` and `CAMERA_PASSWORD` empty — credentials are already in the URL.

> **Note:** Eufy C220 allows only **one simultaneous RTSP connection**. Stop other apps connected to the camera before starting familiar-ai.


### Голас (ElevenLabs)

1. Атрымацце API ключ на [elevenlabs.io](https://elevenlabs.io/)
2. Усталюйце ў `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # неабавязкова, выкарыстоўвае дэфолтны голас, калі прапушчана
   ```

Ёсць два месцы адтворэння, якія кантралююцца `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # дынамік ПК (па змаўчанні)
TTS_OUTPUT=remote   # толькі дынамік камеры
TTS_OUTPUT=both     # дынамік камеры + дынамік ПК адначасова
```

#### A) Дынамік камеры (праз go2rtc)

Усталюйце `TTS_OUTPUT=remote` (альбо `both`). Патрабуе [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Загрузіце бінарны файл з [старонкі выпускаў](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Пакладзіце і перайменуйце яго:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # патрэбна chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Стварыце `go2rtc.yaml` у той жа тэчцы:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Выкарыстоўвайце ўліковыя дадзеныя лакальнага акаўнта камеры (не ваш акаўнт у воблаку TP-Link).

4. familiar-ai аўтаматычна запускае go2rtc пры запуску. Калі ваша камера падтрымлівае двухбаковы гук (зваротны канал), голас прайграў з дынаміка камеры.

#### B) Лакальны дынамік ПК

Дэкретная опцыя (`TTS_OUTPUT=local`). Прабуе прайгравальнікі па парадку: **paplay** → **mpv** → **ffplay**. Таксама выкарыстоўваецца ў якасці рэзервовага варыянту, калі `TTS_OUTPUT=remote` і go2rtc недаступны.

| OS | Усталёўка |
|----|-----------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ці `paplay` праз `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — усталюйце `PULSE_SERVER=unix:/mnt/wslg/PulseServer` у `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — загрузіце і дадайце ў PATH, **альбо** `winget install ffmpeg` |

> Калі няма ніякага прайгравальніка гуку, маўленне ўсё роўна генеруецца — яно проста не будзе прайгравацца.

### Галасавы ўвод (Рэальныя STT)

Усталюйце `REALTIME_STT=true` у `.env` для вечна ўключанага, бездрадзьджавага галасавога ўваходу:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # той самы ключ, што і для TTS
```

familiar-ai транслюе аўдыё з мікрафона ў ElevenLabs Scribe v2 і аўтаматычна захоўвае транскрыпціі, калі вы спыняеце гаварыць. Ніякага націскання кнопак не патрабуецца. Сумяшчаецца з рэжымам націскання для размовы (Ctrl+T).

---

## TUI

familiar-ai ўключае ў сябе тэрмінальны інтэрфейс, складзены з [Textual](https://textual.textualize.io/):

- Пачасная гісторыя размоваў з жывым струменевым тэкстам
- Завяршэнне табуляцыі для `/quit`, `/clear`
- Перарыванне агента падчас разгляду, калі вы набіраеце падчас яго разважанняў
- **Журнал размовы** аўтаматычна захоўваецца ў `~/.cache/familiar-ai/chat.log`

Каб сачыць за журналам у іншым тэрмінале (зручна для копіяваць-вставкі):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Асоба (ME.md)

Асоба вашага знаёмага жыве ў `ME.md`. Гэты файл игнорируется git — ён толькі ваш.

Дачытайце [`persona-template/en.md`](./persona-template/en.md) для прыкладу, або [`persona-template/ja.md`](./persona-template/ja.md) для японскай версіі.

---

## FAQ

**Q: Ці працуе ён без GPU?**
Так. Мадэль укладкі (multilingual-e5-small) добра працуе на ЦП. GPU робіць яго хутчэй, але не абавязкова.

**Q: Ці магу я выкарыстоўваць камеру, якая не з Tapo?**
Любыя камеры, якія падтрымліваюць Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: Ці адпраўляюцца мае дадзеныя куды-небудзь?**
Выявы і тэксты адпраўляюцца на выбраны вамі LLM API для апрацоўкі. Успаміны захоўваюцца лакальна ў `~/.familiar_ai/`.

**Q: Чаму агент піша `（...）` замест таго, каб гаварыць?**
Пераканайцеся, што `ELEVENLABS_API_KEY` усталяваны. Без яго голас адключаецца, і агент пераходзіць на тэкст.

## Тэхнічны фон

Ці цікава, як гэта працуе? Паглядзіце [docs/technical.md](./docs/technical.md) на даследаванні і дызайнерскія рашэнні за familiar-ai — ReAct, SayCan, Reflexion, Voyager, сістэма жаданняў і многае іншае.

---

## Уклад

familiar-ai — гэта адкрыты эксперымент. Калі што-небудзь з гэтага супадае з вашымі перакананнямі — тэхнічна ці філасофскі — уклад вельмі вітаецца.

**Добрыя месцы, каб пачаць:**

| Сфера | Што патрэбна |
|-------|--------------|
| Новае абсталяванне | Падтрымка большай колькасці камер (RTSP, IP Webcam), мікрафонаў, актуятараў |
| Новыя інструменты | Вэб-пошук, хатняя аўтаматызацыя, каляндар, усё гэта праз MCP |
| Новыя пастаўшчыкі | Любы LLM або мясцовая мадэль, якая адпавядае інтэрфейсу `stream_turn` |
| Шаблоны асобы | Шаблоны ME.md для розных моў і асобы |
| Даследаванні | Лепшыя мадэлі жаданняў, аднаўленне памяці, падштурхоўванне тэорыі розуму |
| Дакументацыя | Ўрокі, кіраўніцтва, пераклады |

Дачытайце [CONTRIBUTING.md](./CONTRIBUTING.md) для ўсталёўкі распрацоўкі, стылю кода і правілаў PR.

Калі вы не ведаеце, з чаго пачаць, [адкрыйце запыт](https://github.com/lifemate-ai/familiar-ai/issues) — з задавальненнем накажу вас у правільным напрамку.

---

## Ліцэнзія

[MIT](./LICENSE)
