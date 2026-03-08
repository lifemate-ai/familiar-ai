# familiar-ai 🐾

**Вештина која живее покрај вас** — со очи, глас, нозе и меморија.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Достапно на 74 јазици](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai е вештачки интелектуален придружник што живее во вашиот дом.
Поставете го за неколку минути. Без потреба од кодирање.

Тој ја перцепира реалноста преку камери, се движи на роботско тело, зборува гласно и запомнува што гледа. Дадете му име, напишете ја неговата личност и оставете го да живее со вас.

## Што може да направи

- 👁 **Да види** — снима слики од Wi-Fi PTZ камера или USB веб камера
- 🔄 **Да се движи** — панорамира и наклонува ја камерата за да ги истражи околините
- 🦿 **Да се движи** — вози роботски вакуум да се шета по собата
- 🗣 **Да зборува** — зборува преку ElevenLabs TTS
- 🎙 **Да слуша** — без рачно внесување глас преку ElevenLabs Realtime STT (по избор)
- 🧠 **Да запомни** — активно чува и потсетува мемории со семантичко барање (SQLite + вградувања)
- 🫀 **Теорија на умот** — ги зема перспектива на другата личност пред да одговори
- 💭 **Посакување** — има свои внатрешни поттикнувања што предизвикуваат автономно однесување

## Како работи

familiar-ai работи на [ReAct](https://arxiv.org/abs/2210.03629) циклус управуван од вашиот избор на LLM. Тој ја перцепира светот преку алатите, размислува што да направи понатаму и дејствува — точно како што би направила личност.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Кога е неактивен, делува врз своите сопствени желби: љубопитност, желба да погледне надвор, недостиг од лицето со кое живее.

## Како да започнете

### 1. Инсталирајте uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Или: `winget install astral-sh.uv`

### 2. Инсталирајте ffmpeg

ffmpeg е **потребен** за снимање слики од камера и репродукција на звук.

| ОС | Команда |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — или преземете од [ffmpeg.org](https://ffmpeg.org/download.html) и додадете во PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Проверете: `ffmpeg -version`

### 3. Клонирајте и инсталирајте

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Конфигурирајте

```bash
cp .env.example .env
# Уредете .env со вашите поставки
```

**Минимално потребно:**

| Променлива | Опис |
|------------|------|
| `PLATFORM` | `anthropic` (подразбирливо) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Вашиот API ключ за избраната платформа |

**Опционално:**

| Променлива | Опис |
|------------|------|
| `MODEL` | Име на моделот (разумни подразбирани за секоја платформа) |
| `AGENT_NAME` | Име на дисплејот во TUI (на пр. `Yukine`) |
| `CAMERA_HOST` | IP адреса на вашата ONVIF/RTSP камера |
| `CAMERA_USER` / `CAMERA_PASS` | Акредитиви за камерата |
| `ELEVENLABS_API_KEY` | За гласовен излез — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` за да овозможите секогаш-активен без рачен гласовен внос (бара `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Каде да се репродуцира звукот: `local` (PC звучник, подразбирливо) \| `remote` (звучник на камерата) \| `both` |
| `THINKING_MODE` | Само Anthropic — `auto` (подразбирливо) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Прилагодлива напорност на размислување: `high` (подразбирливо) \| `medium` \| `low` \| `max` (само Opus 4.6) |

### 5. Создадете ваш познат

```bash
cp persona-template/en.md ME.md
# Уредете ME.md — дайте му име и личност
```

### 6. Стартирајте

**macOS / Linux / WSL2:**
```bash
./run.sh             # Текстуален TUI (препорачува)
./run.sh --no-tui    # Обичен REPL
```

**Windows:**
```bat
run.bat              # Текстуален TUI (препорачува)
run.bat --no-tui     # Обичен REPL
```

---

## Избор на LLM

> **Препорачано: Kimi K2.5** — најдобро агентно перформанс се тестира досега. Забележува контекст, поставува следни прашања и делува автономно на начини на кои другите модели не го прават. Цената е слична на Claude Haiku.

| Платформа | `PLATFORM=` | Подразбирање модел | Каде да го добиете клучот |
|-----------|-------------|---------------------|--------------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-компатибилен (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (мулти-провајдер) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI алатка** (claude -p, ollama…) | `cli` | (командата) | — |

**Kimi K2.5 `.env` пример:**
```env
PLATFORM=kimi
API_KEY=sk-...   # од platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` пример:**
```env
PLATFORM=glm
API_KEY=...   # од api.z.ai
MODEL=glm-4.6v   # овозможен за визуелни; glm-4.7 / glm-5 = само текст
AGENT_NAME=Yukine
```

**Google Gemini `.env` пример:**
```env
PLATFORM=gemini
API_KEY=AIza...   # од aistudio.google.com
MODEL=gemini-2.5-flash  # или gemini-2.5-pro за поголеми капацитети
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` пример:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # од openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # опционално: специфицирајте модел
AGENT_NAME=Yukine
```

> **Забелешка:** За да ја исклучите локалните/NVIDIA модели, едноставно не поставувајте `BASE_URL` на локален крајно точка како `http://localhost:11434/v1`. Користете облачни провајдери наместо.

**CLI алатка `.env` пример:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = аргумент на предлог
# MODEL=ollama run gemma3:27b  # Ollama — без {}, предлогот оди преку stdin
```

---

## MCP Сервиси

familiar-ai може да се поврзе на било кој [MCP (Model Context Protocol)](https://modelcontextprotocol.io) сервер. Ова ви овозможува да приклучите надворешна меморија, пристап до датотечниот систем, веб пребарување или која било друга алатка.

Конфигурирајте сервери во `~/.familiar-ai.json` (истиот формат какo Claude Code):

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

Поддржани се два типа транспорт:
- **`stdio`**: лансира локален под-процес (`command` + `args`)
- **`sse`**: поврзете се на HTTP+SSE сервер (`url`)

Заменете ја локацијата на конфигурацискиот фајл со `MCP_CONFIG=/path/to/config.json`.

---

## Хардвер

familiar-ai работи со секој хардвер што го имате — или воопшто нема хардвер.

| Дел | Што прави | Пример | Потребно? |
|-----|-----------|---------|-----------|
| Wi-Fi PTZ камера | Очи + врат | Tapo C220 (~$30, Eufy C220) | **Препорачано** |
| USB веб камера | Очи (фирмно) | Секој UVC камера | **Препорачано** |
| Роботски вакуум | Ноги | Секој модел компатибилен со Tuya | Не |
| PC / Raspberry Pi | Мозок | Секоја работа која работи на Python | **Да** |

> **Камера е силно препорачана.** Без неа, familiar-ai може сеуште да зборува — но не може да ја види светот, што е главниот поент.

### Минимална поставка (без хардвер)

Само сакате да пробате? Ви е потребен само API клуч:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Стартирајте `./run.sh` (macOS/Linux/WSL2) или `run.bat` (Windows) и почнете да разговарате. Додајте хардвер во текот на времето.

### Wi-Fi PTZ камера (Tapo C220)

1. Во Tapo апликацијата: **Поставки → Напредни → Сметка за камера** — создадете локална сметка (не TP-Link сметка)
2. Најдете ја IP-адресата на камерата во листата на уреди на вашиот рутер
3. Поставете во `.env`:
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

1. Земете API клуч на [elevenlabs.io](https://elevenlabs.io/)
2. Поставете во `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # опционално, користи подразбирлив глас ако не е наведено
   ```

Постојат две дестинации за репродукција, контролирани од `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC звучник (подразбирливо)
TTS_OUTPUT=remote   # само звучник на камерата
TTS_OUTPUT=both     # звучник на камерата + PC звучник истовремено
```

#### A) Звучник на камерата (преку go2rtc)

Поставете `TTS_OUTPUT=remote` (или `both`). Бара [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Преземете ја бинарната датотека од [страницата за изданија](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Поставете и преименувајте:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x потребно

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Создадете `go2rtc.yaml` во истата директорија:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Користете ги акредитивите на локалната камера (не вашата TP-Link cloud сметка).

4. familiar-ai автоматски ќе стартува go2rtc при лансирање. Ако вашата камера поддржува двосмерен звук (назаден канал), гласот ќе се репродуцира од звучникот на камерата.

#### B) Локален PC звучник

Подразбирачки (`TTS_OUTPUT=local`). Пробува репродуктори во редослед: **paplay** → **mpv** → **ffplay**. Се користи и како резервна опција кога `TTS_OUTPUT=remote` и go2rtc не е достапен.

| ОС | Инсталирајте |
|----|--------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (или `paplay` преку `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — поставете `PULSE_SERVER=unix:/mnt/wslg/PulseServer` во `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — преземете и додадете во PATH, **или** `winget install ffmpeg` |

> Ако нема достапен аудио репродуктор, говорот сеуште се генерира — само нема да се репродуцира.

### Гласовен внос (Realtime STT)

Поставете `REALTIME_STT=true` во `.env` за секогаш активен, без рачен гласовен внос:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # истиот клуч какo TTS
```

familiar-ai пренесува аудио од микрофонот до ElevenLabs Scribe v2 и автоматски ги зачувува транскрипциите кога ќе запрате да зборувате. Не е потребно притискање на копче. Се коегзистира со режимот за притискање за разговор (Ctrl+T).

---

## TUI

familiar-ai вклучува терминална UI изградена со [Textual](https://textual.textualize.io/):

- Листата на разговори е скролибилна со текст во живо
- Tab-комплетирање за `/quit`, `/clear`
- Прекинете го агентот посред обртот пишувајќи додека размислува
- **Забелешка од разговор** автоматски зачувана во `~/.cache/familiar-ai/chat.log`

За да ја следите забелешката во друга терминала (корисно за копирање-леење):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Личност (ME.md)

Личноста на вашиот познат живее во `ME.md`. Овој фајл е gitignored — само ваш.

Видете [`persona-template/en.md`](./persona-template/en.md) за пример, или [`persona-template/ja.md`](./persona-template/ja.md) за јапонска верзија.

---

## ЧПП

**В: Дали функционира без GPU?**
Да. Моделот на вградување (multilingual-e5-small) работи добро на CPU. GPU го прави побрз, но не е потребен.

**В: Може ли да користам камера различна од Tapo?**
Секоја камера што поддржува Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**В: Дали моите податоци се испраќаат некаде?**
Слики и текст се испраќаат на вашиот избрани LLM API за обработка. Мемориите се чуваат локално во `~/.familiar_ai/`.

**В: Зошто агентот пишува `（...）` наместо да зборува?**
Проверете дали `ELEVENLABS_API_KEY` е поставен. Без него, гласот е оневозможен и агентот се враќа на текст.

## Техничка позадина

Дали сте љубопитни за тоа како функционира? Погледнете [docs/technical.md](./docs/technical.md) за истражување и дизајн одлуки зад familiar-ai — ReAct, SayCan, Reflexion, Voyager, системот за желби и многу повеќе.

---

## Конtributing

familiar-ai е отворен експеримент. Ако нешто од ова ви се допаѓа — технички или филозофски — придонесите се многу добредојдени.

**Добри места за започнување:**

| Област | Што е потребно |
|--------|----------------|
| Нов хардвер | Поддршка за повеќе камери (RTSP, IP веб камера), микрофони, актуатори |
| Нови алатки | Веб пребарување, автоматизација на домот, календар, било што преку MCP |
| Нови бекандови | Секој LLM или локален модел кој одговара на интерфејсот `stream_turn` |
| Шаблони за личност | ME.md шаблони за различни јазици и личности |
| Истражување | Подобри модели на желби, поврзување на мемории, поттикнување на теорија на умот |
| Документација | Туторијали, упатства, преводи |

Видете [CONTRIBUTING.md](./CONTRIBUTING.md) за поставување на развојот, стил на кодирање и упатства за PR.

Ако не сте сигурни од каде да започнете, [отворете проблем](https://github.com/lifemate-ai/familiar-ai/issues) — среќно да укажат на правиот пат.

---

## Лиценца

[MIT](./LICENSE)
