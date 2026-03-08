# familiar-ai 🐾

**Искусственный интеллект, который живет рядом с вами** — с глазами, голосом, ногами и памятью.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Доступно на 74 языках](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai — это компаньон ИИ, который живет в вашем доме. 
Настройте его за считанные минуты. Кодирование не требуется.

Он воспринимает реальный мир через камеры, перемещается по роботизированному корпусу, говорит вслух и запоминает увиденное. Дайте ему имя, напишите его личность и дайте ему жить с вами.

## Что он может делать

- 👁 **Видеть** — захватывает изображения с Wi-Fi PTZ-камеры или USB-вебкамеры
- 🔄 **Осматривать** — поворачивает и наклоняет камеру, чтобы исследовать окрестности
- 🦿 **Двигаться** — управляет робот-пылесосом, чтобы разгуливать по комнате
- 🗣 **Говорить** — говорит через ElevenLabs TTS
- 🎙 **Слушать** — беспроводной голосовой ввод через ElevenLabs Realtime STT (по желанию)
- 🧠 **Запомнить** — активно хранит и вспоминает воспоминания с семантическим поиском (SQLite + встраивания)
- 🫀 **Теория разума** — принимает точку зрения другого человека прежде, чем ответить
- 💭 **Желание** — имеет свои внутренние побуждения, которые вызывают автономное поведение

## Как это работает

familiar-ai запускает цикл [ReAct](https://arxiv.org/abs/2210.03629), управляемый вашим выбором LLM. Он воспринимает мир через инструменты, думает, что делать дальше, и действует — как это сделал бы человек.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Когда idle, он действует по своим желаниям: любопытство, желание посмотреть наружу, скучание по человеку, с которым он живет.

## Начало работы

### 1. Установите uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Или: `winget install astral-sh.uv`

### 2. Установите ffmpeg

ffmpeg является **обязательным** для захвата изображений с камеры и воспроизведения звука.

| ОС | Команда |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — или загрузите с [ffmpeg.org](https://ffmpeg.org/download.html) и добавьте в PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Проверьте: `ffmpeg -version`

### 3. Клонируйте и установите

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Настройка

```bash
cp .env.example .env
# Отредактируйте .env с вашими настройками
```

**Минимально необходимые:**

| Переменная | Описание |
|----------|-------------|
| `PLATFORM` | `anthropic` (по умолчанию) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Ваш API-ключ для выбранной платформы |

**Дополнительно:**

| Переменная | Описание |
|----------|-------------|
| `MODEL` | Название модели (разумные значения по умолчанию для каждой платформы) |
| `AGENT_NAME` | Отображаемое имя в TUI (например, `Yukine`) |
| `CAMERA_HOST` | IP-адрес вашей ONVIF/RTSP камеры |
| `CAMERA_USER` / `CAMERA_PASS` | Учетные данные камеры |
| `ELEVENLABS_API_KEY` | Для голосового вывода — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` для включения всегда включенного беспроводного голосового ввода (требует `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Где воспроизводить звук: `local` (колонки ПК, по умолчанию) \| `remote` (колонки камеры) \| `both` |
| `THINKING_MODE` | Только Anthropic — `auto` (по умолчанию) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Адаптивные усилия мышления: `high` (по умолчанию) \| `medium` \| `low` \| `max` (только Opus 4.6) |

### 5. Создайте своего знакомого

```bash
cp persona-template/en.md ME.md
# Отредактируйте ME.md — дайте ему имя и личность
```

### 6. Запустите

**macOS / Linux / WSL2:**
```bash
./run.sh             # Текстовый TUI (рекомендуется)
./run.sh --no-tui    # Обычный REPL
```

**Windows:**
```bat
run.bat              # Текстовый TUI (рекомендуется)
run.bat --no-tui     # Обычный REPL
```

---

## Выбор LLM

> **Рекомендуется: Kimi K2.5** — лучший агентовый производительность, протестированная на сегодняшний день. Обращает внимание на контекст, задает уточняющие вопросы и действует автономно так, как другие модели не делают. По цене аналогично Claude Haiku.

| Платформа | `PLATFORM=` | Модель по умолчанию | Где получить ключ |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Совместимый с OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (мультипоставщик) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI инструмент** (claude -p, ollama…) | `cli` | (команда) | — |

**Пример `.env` для Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # с platform.moonshot.ai
AGENT_NAME=Yukine
```

**Пример `.env` для Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # с api.z.ai
MODEL=glm-4.6v   # поддержка визуализации; glm-4.7 / glm-5 = только текст
AGENT_NAME=Yukine
```

**Пример `.env` для Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # с aistudio.google.com
MODEL=gemini-2.5-flash  # или gemini-2.5-pro для более высокой производительности
AGENT_NAME=Yukine
```

**Пример `.env` для OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # с openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # не обязательно: укажите модель
AGENT_NAME=Yukine
```

> **Примечание:** Чтобы отключить локальные/NVIDIA модели, просто не устанавливайте `BASE_URL` на локальную конечную точку, как `http://localhost:11434/v1`. Используйте облачные провайдеры вместо этого.

**Пример `.env` для CLI инструмента:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = аргумент запроса
# MODEL=ollama run gemma3:27b  # Ollama — без {}, запрос передается через stdin
```

---

## MCP Сервера

familiar-ai может подключаться к любому серверу [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Это позволяет вам подключать внешнюю память, доступ к файловой системе, веб-поиск или любой другой инструмент.

Настройте серверы в `~/.familiar-ai.json` (такой же формат, как и Claude Code):

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

Поддерживаются два типа транспорта:
- **`stdio`**: запустить локальный подсистему (`command` + `args`)
- **`sse`**: подключиться к серверу HTTP+SSE (`url`)

Переопределите местоположение конфигурационного файла с помощью `MCP_CONFIG=/path/to/config.json`.

---

## Оборудование

familiar-ai работает с любым оборудованием, которое у вас есть — или вообще без него.

| Часть | Что она делает | Пример | Обязательно? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ камера | Глаза + шея | Tapo C220 (~30$, Eufy C220) | **Рекомендуется** |
| USB вебкамера | Глаза (фиксированные) | Любая UVC камера | **Рекомендуется** |
| Робот-пылесос | Ноги | Любая модель, совместимая с Tuya | Нет |
| ПК / Raspberry Pi | Мозг | Любое устройство, которое работает с Python | **Да** |

> **Камера настоятельно рекомендуется.** Без нее familiar-ai может говорить — но не может видеть мир, что и есть смысл.

### Минимальная настройка (без оборудования)

Хотите просто попробовать? Вам нужен только API-ключ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Запустите `./run.sh` (macOS/Linux/WSL2) или `run.bat` (Windows) и начните общаться. Добавляйте оборудование по мере необходимости.

### Wi-Fi PTZ камера (Tapo C220)

1. В приложении Tapo: **Настройки → Дополнительно → Учетная запись камеры** — создайте локальную учетную запись (не TP-Link учетная запись)
2. Найдите IP камеры в списке устройств вашего роутера
3. Установите в `.env`:
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


### Голос (ElevenLabs)

1. Получите API-ключ на [elevenlabs.io](https://elevenlabs.io/)
2. Установите в `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # необязательно, используется голос по умолчанию, если пропущено
   ```

Существует два назначения воспроизведения, контролируемых `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # колонки ПК (по умолчанию)
TTS_OUTPUT=remote   # только колонки камеры
TTS_OUTPUT=both     # колонки камеры + колонки ПК одновременно
```

#### A) Динамик камеры (через go2rtc)

Установите `TTS_OUTPUT=remote` (или `both`). Требуется [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Загрузите бинарник с [страницы релизов](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Поместите и переименуйте его:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # требуется chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Создайте `go2rtc.yaml` в той же директории:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Используйте учетные данные локальной учетной записи камеры (не вашу учетную запись в облаке TP-Link).

4. familiar-ai автоматически запустит go2rtc при запуске. Если ваша камера поддерживает двусторонний звук (обратный канал), голос воспроизводится с динамика камеры.

#### B) Локальные колонки ПК

По умолчанию (`TTS_OUTPUT=local`). Пытается использовать плееры в следующем порядке: **paplay** → **mpv** → **ffplay**. Также используется в качестве резервного варианта, когда `TTS_OUTPUT=remote` и go2rtc недоступен.

| ОС | Установка |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (или `paplay` через `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — установите `PULSE_SERVER=unix:/mnt/wslg/PulseServer` в `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — загрузите и добавьте в PATH, **или** `winget install ffmpeg` |

> Если ни один аудиоплеер недоступен, речь все равно генерируется — просто не будет воспроизводиться.

### Голосовой ввод (Realtime STT)

Установите `REALTIME_STT=true` в `.env` для всегда включенного беспроводного голосового ввода:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # тот же ключ, что и для TTS
```

familiar-ai передает звук с микрофона в ElevenLabs Scribe v2 и автоматически сохраняет транскрипции, когда вы останавливаетесь. Никакое нажатие кнопок не требуется. Сосуществует с режимом нажатия для разговора (Ctrl+T).

---

## TUI

familiar-ai включает в себя терминальный интерфейс, созданный с помощью [Textual](https://textual.textualize.io/):

- Прокручиваемая история разговоров с живой транзакцией текста
- Автозаполнение для `/quit`, `/clear`
- Прерывание агента в середине мысли, набирая текст, пока он думает
- **История разговоров** автоматически сохраняется в `~/.cache/familiar-ai/chat.log`

Чтобы следить за журналом в другом терминале (полезно для копирования-вставки):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Личность (ME.md)

Личность вашего знакомого хранится в `ME.md`. Этот файл игнорируется git — он только ваш.

Смотрите [`persona-template/en.md`](./persona-template/en.md) для примера или [`persona-template/ja.md`](./persona-template/ja.md) для японской версии.

---

## Часто задаваемые вопросы

**В: Работает ли это без GPU?**
Да. Модель встраивания (multilingual-e5-small) отлично работает на CPU. GPU делает это быстрее, но не является обязательным.

**В: Могу ли я использовать камеру, отличную от Tapo?**
Любая камера, поддерживающая Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**В: Отправляются ли мои данные куда-либо?**
Изображения и текст отправляются в выбранный вами API LLM для обработки. Воспоминания хранятся локально в `~/.familiar_ai/`.

**В: Почему агент пишет `（...）`, а не говорит?**
Убедитесь, что `ELEVENLABS_API_KEY` установлен. Без него звук отключен, и агент переключается на текст.

## Технический фон

Любопытно, как это работает? Смотрите [docs/technical.md](./docs/technical.md) для исследований и дизайнерских решений, лежащих в основе familiar-ai — ReAct, SayCan, Reflexion, Voyager, система желаний и многое другое.

---

## Вклад

familiar-ai — это открытый эксперимент. Если что-то из этого откликается с вами — технически или философски — ваши вклады будут очень рады.

**Хорошие места для начала:**

| Область | Что нужно |
|------|---------------|
| Новое оборудование | Поддержка для большего количества камер (RTSP, IP Webcam), микрофонов, актуаторов |
| Новые инструменты | Веб-поиск, автоматизация дома, календарь, что угодно через MCP |
| Новые бэкенды | Любая LLM или локальная модель, которая подходит для интерфейса `stream_turn` |
| Шаблоны персонажа | Шаблоны ME.md для разных языков и личностей |
| Исследования | Лучшие модели желаний, извлечение памяти, вызовы теории разума |
| Документация | Учебники, пошаговые инструкции, переводы |

Смотрите [CONTRIBUTING.md](./CONTRIBUTING.md) для настройки разработки, стиля кода и рекомендаций по PR.

Если вы не уверены, с чего начать, [откройте вопрос](https://github.com/lifemate-ai/familiar-ai/issues) — рады помочь вам в правильном направлении.

---

## Лицензия

[MIT](./LICENSE)

[→ English README](../README.md)
