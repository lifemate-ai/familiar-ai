# familiar-ai 🐾

**Штучний інтелект, що живе поряд з вами** — з очима, голосом, ногами і пам’яттю.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Доступно 74 мовами](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai — це компаньйон ШІ, який живе у вашому домі. Налаштуйте його за кілька хвилин. Кодинг не потрібен.

Він сприймає реальний світ через камери, пересувається на роботизованому тілі, говорить вголос і запам’ятовує, що бачить. Дайте йому ім’я, напишіть його особистість і нехай він живе з вами.

## Що він може зробити

- 👁 **Бачити** — захоплює зображення з Wi-Fi PTZ камери або USB веб-камери
- 🔄 **Оглядатись** — панорамно і нахиляє камеру, щоб дослідити оточення
- 🦿 **Переміщатись** — керує роботизованим пилососом для переміщення по кімнаті
- 🗣 **Говорити** — розмовляє за допомогою ElevenLabs TTS
- 🎙 **Слухати** — безконтактний голосовий ввід через ElevenLabs Realtime STT (за бажанням)
- 🧠 **Запам’ятовувати** — активно зберігає та згадує спогади за допомогою семантичного пошуку (SQLite + embeddings)
- 🫀 **Теорія розуму** — приймає перспективу іншої особи перед тим, як відповісти
- 💭 **Бажання** — має свої власні внутрішні потяги, що викликають автономну поведінку

## Як це працює

familiar-ai виконує цикл [ReAct](https://arxiv.org/abs/2210.03629), керований вибором LLM. Він сприймає світ через інструменти, думає про те, що робити далі, і діє — так само, як це зробила б людина.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Коли він бездіяльний, він діє за власними бажаннями: цікавість, захотіти подивитись на вулицю, сумувати за людиною, з якою живе.

## Як почати

### 1. Встановіть uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Або: `winget install astral-sh.uv`

### 2. Встановіть ffmpeg

ffmpeg є **необхідним** для захоплення зображень з камери та відтворення звуку.

| ОС | Команда |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — або завантажити з [ffmpeg.org](https://ffmpeg.org/download.html) і додати до PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Перевірте: `ffmpeg -version`

### 3. Клонуйте та встановіть

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Налаштуйте

```bash
cp .env.example .env
# Редагуйте .env з вашими налаштуваннями
```

**Мінімально необхідно:**

| Змінна | Опис |
|--------|------|
| `PLATFORM` | `anthropic` (за замовчуванням) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Ваш API ключ для обраної платформи |

**За бажанням:**

| Змінна | Опис |
|--------|------|
| `MODEL` | Назва моделі (раціональні значення за замовчуванням для кожної платформи) |
| `AGENT_NAME` | Відображуване ім’я в TUI (наприклад, `Yukine`) |
| `CAMERA_HOST` | IP-адреса вашої ONVIF/RTSP камери |
| `CAMERA_USER` / `CAMERA_PASS` | Облікові дані камери |
| `ELEVENLABS_API_KEY` | Для голосового виходу — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, щоб увімкнути завжди-включений безконтактний голосовий ввід (потрібен `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Де відтворювати аудіо: `local` (динамік ПК, за замовчуванням) \| `remote` (динамік камери) \| `both` |
| `THINKING_MODE` | Лише Anthropic — `auto` (за замовчуванням) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Адаптивне зусилля мислення: `high` (за замовчуванням) \| `medium` \| `low` \| `max` (тільки Opus 4.6) |

### 5. Створіть свого знайомого

```bash
cp persona-template/en.md ME.md
# Редагуйте ME.md — дайте йому ім’я та особистість
```

### 6. Запустіть

**macOS / Linux / WSL2:**
```bash
./run.sh             # Текстовий TUI (рекомендується)
./run.sh --no-tui    # Звичайний REPL
```

**Windows:**
```bat
run.bat              # Текстовий TUI (рекомендується)
run.bat --no-tui     # Звичайний REPL
```

---

## Вибір LLM

> **Рекомендується: Kimi K2.5** — найкраща агентна продуктивність, протестована донині. Звертає увагу на контекст, ставить уточнюючі запитання та діє автономно, як інші моделі не роблять. Ціна схожа на Claude Haiku.

| Платформа | `PLATFORM=` | Модель за замовчуванням | Де отримати ключ |
|-----------|-------------|-------------------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Сумісні з OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (багатопостачальник) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI інструмент** (claude -p, ollama…) | `cli` | (команда) | — |

**Приклад .env для Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # з platform.moonshot.ai
AGENT_NAME=Yukine
```

**Приклад .env для Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # з api.z.ai
MODEL=glm-4.6v   # з можливістю зору; glm-4.7 / glm-5 = лише текст
AGENT_NAME=Yukine
```

**Приклад .env для Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # з aistudio.google.com
MODEL=gemini-2.5-flash  # або gemini-2.5-pro для більшої потужності
AGENT_NAME=Yukine
```

**Приклад .env для OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # з openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # за бажанням: вкажіть модель
AGENT_NAME=Yukine
```

> **Примітка:** Щоб відключити локальні/NVIDIA моделі, просто не встановлюйте `BASE_URL` на локальний кінець, як-от `http://localhost:11434/v1`. Використовуйте замість цього хмарних постачальників.

**Приклад .env для CLI інструмента:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = аргумент запиту
# MODEL=ollama run gemma3:27b  # Ollama — без {}, запит передається через stdin
```

---

## MCP Сервери

familiar-ai може підключатись до будь-якого [MCP (Model Context Protocol)](https://modelcontextprotocol.io) сервера. Це дозволяє вам підключити зовнішню пам’ять, доступ до файлових систем, веб-пошук або будь-який інший інструмент.

Налаштуйте сервери у `~/.familiar-ai.json` (той же формат, що й Claude Code):

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

Підтримуються два типи транспорту:
- **`stdio`**: запуск локального підпроцесу (`command` + `args`)
- **`sse`**: підключення до HTTP+SSE сервера (`url`)

Перезапишіть розташування файлу конфігурації за допомогою `MCP_CONFIG=/path/to/config.json`.

---

## Апаратне забезпечення

familiar-ai працює з будь-яким апаратним забезпеченням, яке у вас є — або зовсім без нього.

| Частина | Що вона робить | Приклад | Обов’язково? |
|---------|----------------|---------|--------------|
| Wi-Fi PTZ камера | Очі + шия | Tapo C220 (~$30, Eufy C220) | **Рекомендується** |
| USB веб-камера | Очі (фіксовані) | Будь-яка UVC камера | **Рекомендується** |
| Роботизований пилосос | Ноги | Будь-яка модель, сумісна з Tuya | Ні |
| ПК / Raspberry Pi | Мозок | Усе, що працює на Python | **Так** |

> **Камеру настійно рекомендується мати.** Без неї familiar-ai все ще може говорити — але він не може бачити світ, а це якраз вся суть.

### Мінімальна настройка (без апаратного забезпечення)

Просто хочете спробувати? Вам лише потрібен API ключ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Запустіть `./run.sh` (macOS/Linux/WSL2) або `run.bat` (Windows) і почніть спілкування. Додавайте апаратне забезпечення за потребою.

### Wi-Fi PTZ камера (Tapo C220)

1. У додатку Tapo: **Налаштування → Додатково → Обліковий запис камери** — створіть локальний обліковий запис (не обліковий запис TP-Link)
2. Знайдіть IP-адресу камери у списку пристроїв вашого маршрутизатора
3. Встановіть у `.env`:
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

1. Отримайте API ключ на [elevenlabs.io](https://elevenlabs.io/)
2. Встановіть у `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # за бажанням, використовує голос за замовчуванням, якщо пропущено
   ```

Існують два напрямки відтворення, контрольовані `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Динамік ПК (за замовчуванням)
TTS_OUTPUT=remote   # Тільки динамік камери
TTS_OUTPUT=both     # Динамік камери + Динамік ПК одночасно
```

#### A) Динамік камери (через go2rtc)

Встановіть `TTS_OUTPUT=remote` (або `both`). Потрібен [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Завантажте двійник з [сторінки випусків](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Помістіть та перейменуйте його:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # потрібно chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Створіть `go2rtc.yaml` у тому ж каталозі:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Використовуйте локальні облікові дані камери (не ваш обліковий запис TP-Link cloud).

4. familiar-ai автоматично запускає go2rtc при запуску. Якщо ваша камера підтримує двостороннє аудіо (зворотний канал), голос звучатиме з динаміка камери.

#### B) Локальний динамік ПК

За замовчуванням (`TTS_OUTPUT=local`). Пробує відтворювачі в порядку: **paplay** → **mpv** → **ffplay**. Також використовується як резервний варіант, коли `TTS_OUTPUT=remote` і go2rtc недоступний.

| ОС | Встановлення |
|----|--------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (або `paplay` через `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — встановіть `PULSE_SERVER=unix:/mnt/wslg/PulseServer` у `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — завантажте та додайте до PATH, **або** `winget install ffmpeg` |

> Якщо відтворювач аудіо недоступний, мова все ще генерується — просто не буде відтворення.

### Голосовий ввід (Realtime STT)

Встановіть `REALTIME_STT=true` у `.env` для завжди включеного, безконтактного голосового вводу:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # той же ключ, що й TTS
```

familiar-ai транслює аудіо мікрофона до ElevenLabs Scribe v2 і автоматично зберігає транскрипти, коли ви зупиняєтеся. Ніякого натискання кнопки не потрібно. Існує в режимі push-to-talk (Ctrl+T).

---

## TUI

familiar-ai містить термінальний інтерфейс, створений за допомогою [Textual](https://textual.textualize.io/):

- Прокручувана історія розмови з текстом у реальному часі
- Завершення табуляції для `/quit`, `/clear`
- Перервати агента в середині черги, набираючи під час роздумів
- **Журнал розмови** автоматично зберігається у `~/.cache/familiar-ai/chat.log`

Щоб стежити за журналом в іншому терміналі (корисно для копіювання-вставлення):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Персона (ME.md)

Особистість вашого знайомого живе у `ME.md`. Цей файл ігнорується git — він тільки ваш.

Подивіться [`persona-template/en.md`](./persona-template/en.md) для прикладу або [`persona-template/ja.md`](./persona-template/ja.md) для японської версії.

---

## Поширені запитання

**Q: Чи працює без GPU?**
Так. Модель векторного представлення (multilingual-e5-small) працює нормально на CPU. GPU робить швидше, але не є обов’язковим.

**Q: Чи можу я використовувати іншу камеру, окрім Tapo?**
Будь-яка камера, що підтримує Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: Чи надсилаються мої дані кудись?**
Зображення та текст надсилаються до API обраного LLM для обробки. Спогади зберігаються локально в `~/.familiar_ai/`.

**Q: Чому агент пише `（...）`, а не говорить?**
Переконайтеся, що `ELEVENLABS_API_KEY` встановлено. Без нього голос відключено, і агент повертається до тексту.

## Технічний фон

Цікаво, як це працює? Дивіться [docs/technical.md](./docs/technical.md) для дослідження та рішень у дизайні, що стоять за familiar-ai — ReAct, SayCan, Reflexion, Voyager, система бажань і багато іншого.

---

## Внесок

familiar-ai є відкритим експериментом. Якщо щось з цього резонує з вами — технічно чи філософськи — ваші внески будуть дуже бажаними.

**Гарні місця для початку:**

| Область | Що потрібно |
|---------|-------------|
| Нове апаратне забезпечення | Підтримка більше камер (RTSP, IP Webcam), мікрофонів, актуаторів |
| Нові інструменти | Веб-пошук, автоматизація будинку, календар, усе через MCP |
| Нові бекенди | Будь-який LLM або локальна модель, яка відповідає інтерфейсу `stream_turn` |
| Шаблони персонажів | Шаблони ME.md для різних мов і особистостей |
| Дослідження | Кращі моделі бажань, відновлення пам’яті, запити теорії розуму |
| Документація | Туторіали, інструкції, переклади |

Дивіться [CONTRIBUTING.md](./CONTRIBUTING.md) для налаштування розробки, стилю коду та керівництв по PR.

Якщо ви не впевнені, з чого почати, [відкрийте запитання](https://github.com/lifemate-ai/familiar-ai/issues) — раді будемо вказати вам правильний напрямок.

---

## Ліцензія

[MIT](./LICENSE)
