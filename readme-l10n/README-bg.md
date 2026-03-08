# familiar-ai 🐾

**Изкуствен интелект, който живее до теб** — с очи, глас, крака и памет.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Достъпен на 74 езика](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai е изкуствен интелект, който живее в твоя дом.
Настрой го за минути. Не е необходимо кодиране.

Той възприема реалния свят чрез камери, движи се на роботско тяло, говори на глас и запомня това, което вижда. Дай му име, напиши му личността и го остави да живее с теб.

## Какво може да направи

- 👁 **Виж** — заснема изображения от Wi-Fi PTZ камера или USB уеб камера
- 🔄 **Огледай се** — върти и накланя камерата, за да проучи обстановката
- 🦿 **Движи се** — управлява робот-прахосмукачка, за да обикаля стаята
- 🗣 **Говори** — говори чрез ElevenLabs TTS
- 🎙 **Слушай** — безжично гласово въвеждане чрез ElevenLabs Realtime STT (по желание)
- 🧠 **Помни** — активно съхранява и извиква спомени с семантично търсене (SQLite + ембеддии)
- 🫀 **Теория на ума** — взима гледната точка на другия човек преди да отговори
- 💭 **Желание** — има свои собствени вътрешни стремежи, които предизвикват автономно поведение

## Как работи

familiar-ai работи на [ReAct](https://arxiv.org/abs/2210.03629) цикъл, захранван от твоя избор на LLM. Той възприема света чрез инструменти, обмисля какво да направи след това и действа — точно както би направил човек.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Когато е в покой, той действа в зависимост от собствените си желания: любопитство, желание да погледа навън, желание за присъствието на човека, с когото живее.

## Как да започнете

### 1. Инсталирайте uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Или: `winget install astral-sh.uv`

### 2. Инсталирайте ffmpeg

ffmpeg е **необходимо** за улавяне на изображения от камерата и възпроизвеждане на аудио.

| ОС | Команда |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — или свалете от [ffmpeg.org](https://ffmpeg.org/download.html) и добавете в PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Проверка: `ffmpeg -version`

### 3. Клонирайте и инсталирайте

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Конфигурирайте

```bash
cp .env.example .env
# Редактирайте .env с вашите настройки
```

**Минимално изискуеми:**

| Променлива | Описание |
|----------|-------------|
| `PLATFORM` | `anthropic` (по подразбиране) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Вашият API ключ за избраната платформа |

**По избор:**

| Променлива | Описание |
|----------|-------------|
| `MODEL` | Име на модела (разумни подразбиращи по платформа) |
| `AGENT_NAME` | Покажете име, показано в TUI (например `Yukine`) |
| `CAMERA_HOST` | IP адрес на вашата ONVIF/RTSP камера |
| `CAMERA_USER` / `CAMERA_PASS` | Удостоверение за камерата |
| `ELEVENLABS_API_KEY` | За гласово изход — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` за включване на постоянно включено гласово въвеждане (изисква `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Къде да се воспроизводи аудио: `local` (PC говорител, по подразбиране) \| `remote` (камера говорител) \| `both` |
| `THINKING_MODE` | Само за Anthropic — `auto` (по подразбиране) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Адаптивно мислене усилие: `high` (по подразбиране) \| `medium` \| `low` \| `max` (само Opus 4.6) |

### 5. Създайте своето familiar

```bash
cp persona-template/en.md ME.md
# Редактирайте ME.md — дайте му име и личност
```

### 6. Изпълнете

**macOS / Linux / WSL2:**
```bash
./run.sh             # Текстов TUI (препоръчително)
./run.sh --no-tui    # Обикновен REPL
```

**Windows:**
```bat
run.bat              # Текстов TUI (препоръчително)
run.bat --no-tui     # Обикновен REPL
```

---

## Избор на LLM

> **Препоръчително: Kimi K2.5** — най-добрата агентично представяне тествано досега. Забелязва контекста, задава последващи въпроси и действа автономно по начини, които други модели не правят. Цената е подобна на Claude Haiku.

| Платформа | `PLATFORM=` | Модел по подразбиране | Къде да получа ключ |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-съвместими (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (много-доставчик) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI инструмент** (claude -p, ollama…) | `cli` | (командата) | — |

**Kimi K2.5 `.env` пример:**
```env
PLATFORM=kimi
API_KEY=sk-...   # от platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` пример:**
```env
PLATFORM=glm
API_KEY=...   # от api.z.ai
MODEL=glm-4.6v   # с визуални способности; glm-4.7 / glm-5 = само текст
AGENT_NAME=Yukine
```

**Google Gemini `.env` пример:**
```env
PLATFORM=gemini
API_KEY=AIza...   # от aistudio.google.com
MODEL=gemini-2.5-flash  # или gemini-2.5-pro за по-високи способности
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` пример:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # от openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # по избор: задайте модела
AGENT_NAME=Yukine
```

> **Забележка:** За да деактивирате местни/NVIDIA модели, просто не задавайте `BASE_URL` на местен край на типа `http://localhost:11434/v1`. Използвайте облачни доставчици вместо това.

**CLI инструмент `.env` пример:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = аргумент за подканване
# MODEL=ollama run gemma3:27b  # Ollama — без {}, подканата минава през stdin
```

---

## MCP Сървъри

familiar-ai може да се свърже с всеки [MCP (Model Context Protocol)](https://modelcontextprotocol.io) сървър. Това ви позволява да включвате външна памет, достъп до файловата система, уеб търсене или всякакви други инструменти.

Конфигурирайте сървърите в `~/.familiar-ai.json` (същия формат като Claude Code):

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

Поддържат се два типа транспорт:
- **`stdio`**: стартиране на локален subprocess (`command` + `args`)
- **`sse`**: свързване с HTTP+SSE сървър (`url`)

Сменете местоположението на конфигурационния файл с `MCP_CONFIG=/path/to/config.json`.

---

## Хардуер

familiar-ai работи с какъвто и да е хардуер, който имате — или без никакъв.

| Час | Какво прави | Пример | Изисква ли се? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ камера | Очи + врат | Tapo C220 (~$30, Eufy C220) | **Препоръчително** |
| USB уеб камера | Очи (фиксирана) | Всяка UVC камера | **Препоръчително** |
| Робот-прахосмукачка | Крака | Всякакъв модел, съвместим с Tuya | Не |
| PC / Raspberry Pi | Мозък | Нещо, което работи на Python | **Да** |

> **Камера е силно препоръчителна.** Без такава, familiar-ai все още може да говори — но не може да вижда света, което е по същество целта.

### Минимална настройка (без хардуер)

Искате само да опитате? Нужен ви е само API ключ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Стартирайте `./run.sh` (macOS/Linux/WSL2) или `run.bat` (Windows) и започнете да чатите. Добавяйте хардуер по пътя.

### Wi-Fi PTZ камера (Tapo C220)

1. В приложението Tapo: **Настройки → Разширени → Акаунт на камерата** — създайте локален акаунт (не TP-Link акаунт)
2. Намерете IP адреса на камерата в списъка с устройства на вашия рутер
3. Задайте в `.env`:
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


### Глас (ElevenLabs)

1. Вземете API ключ на [elevenlabs.io](https://elevenlabs.io/)
2. Задайте в `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # по желание, ползва се глас по подразбиране ако е пропуснато
   ```

Има две дестинации за възпроизвеждане, контролиран от `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC говорител (по подразбиране)
TTS_OUTPUT=remote   # само говорител на камерата
TTS_OUTPUT=both     # говорител на камерата + PC говорител едновременно
```

#### A) Говорител на камерата (чрез go2rtc)

Задайте `TTS_OUTPUT=remote` (или `both`). Изисква [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Изтеглете бинарника от [страницата с версии](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Поставете и го преименувайте:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # изисква chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Създайте `go2rtc.yaml` в същата директория:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Използвайте локалните удостоверителни данни на камерата (не вашия TP-Link облачен акаунт).

4. familiar-ai автоматично стартира go2rtc при стартиране. Ако вашата камера поддържа двупосочно аудио (обратна връзка), гласът ще се възпроизвежда от говорителя на камерата.

#### B) Локален PC говорител

По подразбиране (`TTS_OUTPUT=local`). Опитва да възпроизвежда в следния ред: **paplay** → **mpv** → **ffplay**. Също така се използва като резервно при положение, че `TTS_OUTPUT=remote` и go2rtc не е наличен.

| ОС | Инсталирайте |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (или `paplay` чрез `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — задайте `PULSE_SERVER=unix:/mnt/wslg/PulseServer` в `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — изтеглете и добавете в PATH, **или** `winget install ffmpeg` |

> Ако няма наличен аудио плеър, речта все още се генерира — просто няма да се възпроизвежда.

### Гласово въвеждане (Realtime STT)

Задайте `REALTIME_STT=true` в `.env` за постоянно включено, безжично гласово въвеждане:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # същият ключ като за TTS
```

familiar-ai поточно предава аудио от микрофона до ElevenLabs Scribe v2 и автоматично комитва протоколите, когато спреш да говориш. Не е необходимо натискане на бутон. Съществува в съвместимост с режима за натискане за говорене (Ctrl+T).

---

## TUI

familiar-ai включва терминален потребителски интерфейс, построен с [Textual](https://textual.textualize.io/):

- Превъртаща история на разговорите с поточно текстово излъчване
- Завършване на табулации за `/quit`, `/clear`
- Прекъсване на агента по време на размисъл, като пишеш, докато мисли
- **Журнал на разговора** автоматично запазен в `~/.cache/familiar-ai/chat.log`

За да следите журнала в друг терминал (полезно за копиране/поставяне):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Личност (ME.md)

Личността на твоето familiar се намира в `ME.md`. Т този файл е игнориран от git — той е само твой.

Виж [`persona-template/en.md`](./persona-template/en.md) за пример, или [`persona-template/ja.md`](./persona-template/ja.md) за японска версия.

---

## Често задавани въпроси

**В: Работи ли без GPU?**
Да. Моделът за вграждане (multilingual-e5-small) работи чудесно на CPU. GPU ускорява, но не е задължителен.

**В: Мога ли да използвам камера, различна от Tapo?**
Всяка камера, която поддържа Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**В: Изпращат ли се данните ми някъде?**
Изображения и текст се изпращат до избрания LLM API за обработка. Спомените се запазват локално в `~/.familiar_ai/`.

**В: Защо агентът пише `（...）` вместо да говори?**
Убедете се, че `ELEVENLABS_API_KEY` е зададен. Без него, гласът е деактивиран и агентът се връща на текстов режим.

## Технически фон

Любопитен за начина, по който работи? Вижте [docs/technical.md](./docs/technical.md) за изследванията и проектните решения зад familiar-ai — ReAct, SayCan, Reflexion, Voyager, системата за желания и много други.

---

## Принос

familiar-ai е открит експеримент. Ако нещо от това резонира с вас — технически или философски — приноси са много добре дошли.

**Добри места за начало:**

| Област | Какво е необходимо |
|------|---------------|
| Нов хардуер | Поддръжка за повече камери (RTSP, IP Webcam), микрофони, актюатори |
| Нови инструменти | Уеб търсене, домашна автоматизация, календар, всичко чрез MCP |
| Нови бекенди | Всеки LLM или локален модел, който пасва на интерфейса `stream_turn` |
| Шаблони за личност | Шаблони за ME.md за различни езици и личности |
| Изследвания | По-добри модели на желания, извличане на памет, насочване на теория на ума |
| Документация | Уроци, ръководства, преводи |

Вижте [CONTRIBUTING.md](./CONTRIBUTING.md) за настройка на разработката, стил на кода и насоки за PR.

Ако не сте сигурни откъде да започнете, [отворете проблем](https://github.com/lifemate-ai/familiar-ai/issues) — хапливи сме да ви насочим в правилната посока.

---

## Лиценз

[MIT](./LICENSE)
