# familiar-ai 🐾

**Сізбен бірге өмір сүруге арналған ИИ** — көздері, дауысы, аяқтары және жады бар.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 тілде қолжетімді](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai — сіздің үйіңізде тұратын ИИ серігі.
Оны бірнеше минутта орнатыңыз. Код жазу қажет емес.

Ол шынайы әлемді камералар арқылы қабылдайды, робот денесінде қозғалады, дауыстап сөйлейді және көргендерін есінде сақтайды. Оған есім беріңіз, оның тұлғасын жазыңыз және оның сізбен бірге тұруына рұқсат етіңіз.

## Не істей алады

- 👁 **Көре білу** — Wi-Fi PTZ камерасынан немесе USB веб-камерадан суреттер түсіреді
- 🔄 **Айнала қарау** — камераны айналдырып, қоршаған ортаны зерттейді
- 🦿 **Қозғалу** — бөлмеде робот шаңсорғышын жүргізеді
- 🗣 **Сөйлесу** — ElevenLabs TTS арқылы сөйлейді
- 🎙 **Есту** — ElevenLabs Realtime STT (опцияға кіретін) арқылы қолсыз дауыстық кіріс
- 🧠 **Есте сақтау** — белсенді түрде естеліктерді сақтап, семантикалық іздеу (SQLite + embedding) арқылы еске алады
- 🫀 **Ақыл теориясы** — жауап бермес бұрын басқа адамның көзқарасын қабылдайды
- 💭 **Талап** — автономды мінез-құлықты тудыратын ішкі ынталары бар

## Қалай жұмыс істейді

familiar-ai сіз таңдаған LLM арқылы жұмыс істейтін [ReAct](https://arxiv.org/abs/2210.03629) циклін басқарады. Ол әлемді құралдар арқылы қабылдайды, келесі не істеу керек екенін ойлайды және әрекет етеді — адам секілді.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Бос тұрған кезде, ол өзінің ішкі талаптарына жауап береді: қызығушылық, сыртқа қарауды қалайды, бірге тұратын адамды сағынады.

## Бастау үшін

### 1. uv орнату

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Немесе: `winget install astral-sh.uv`

### 2. ffmpeg орнату

ffmpeg **камера суреттерін түсіру және дыбыс ойнату үшін қажет**.

| OS | Команда |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — немесе [ffmpeg.org](https://ffmpeg.org/download.html) сайтынан жүктеп, PATH-қа қосыңыз |
| Raspberry Pi | `sudo apt install ffmpeg` |

Тексеріңіз: `ffmpeg -version`

### 3. Клонировать и установить

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Конфигурациялау

```bash
cp .env.example .env
# .env файлын өз параметрлеріңізбен өңдеңіз
```

**Минималды талаптар:**

| Айнымалы | Сипаттамасы |
|----------|-------------|
| `PLATFORM` | `anthropic` (әдепкі) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Таңдалған платформаңыз үшін API кілтіңіз |

**Опционалды:**

| Айнымалы | Сипаттамасы |
|----------|-------------|
| `MODEL` | Модель атауы (платформаларға сезімтал әдепкі мәндер) |
| `AGENT_NAME` | TUI-де көрсетілетін дисплей аты (мысалы, `Yukine`) |
| `CAMERA_HOST` | ONVIF/RTSP камераңыздың IP мекенжайы |
| `CAMERA_USER` / `CAMERA_PASS` | Камераның куәліктері |
| `ELEVENLABS_API_KEY` | Дыбыс шығару үшін — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` даусыз режимдегі дауыстық кірісті үнемі қосу үшін (нұсқаулық `ELEVENLABS_API_KEY` қажет) |
| `TTS_OUTPUT` | Дыбысты ойнату орны: `local` (PC динамигі, әдепкі) \| `remote` (камера динамигі) \| `both` |
| `THINKING_MODE` | Тек Anthropic — `auto` (әдепкі) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Ынталы ойлау механизмі: `high` (әдепкі) \| `medium` \| `low` \| `max` (тек Opus 4.6) |

### 5. Сіздің танысыңызды құрыңыз

```bash
cp persona-template/en.md ME.md
# ME.md файлын редакциялап, оған есім мен тұлға беріңіз
```

### 6. Жұмысын жүргізу

**macOS / Linux / WSL2:**
```bash
./run.sh             # Мәтіндік TUI (ұсынылды)
./run.sh --no-tui    # Plain REPL
```

**Windows:**
```bat
run.bat              # Мәтіндік TUI (ұсынылды)
run.bat --no-tui     # Plain REPL
```

---

## LLM таңдау

> **Ұсынылған: Kimi K2.5** — тесттелген ең жақсы агенттік өнімділік. Контексті ескереді, сұрақтар қояды және басқа модельдерден автономды түрде әрекет етеді. Claude Haiku бағасымен салыстырмалы.

| Платформа | `PLATFORM=` | Әдепкі модель | Кілтті қайдан алуға болады |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-сәйкес (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (көп провайдер) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI құрал** (claude -p, ollama…) | `cli` | (команда) | — |

**Kimi K2.5 `.env` мысалы:**
```env
PLATFORM=kimi
API_KEY=sk-...   # platform.moonshot.ai сайтынан
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` мысалы:**
```env
PLATFORM=glm
API_KEY=...   # api.z.ai сайтынан
MODEL=glm-4.6v   # көзқарас үшін мүмкін; glm-4.7 / glm-5 = тек мәтін
AGENT_NAME=Yukine
```

**Google Gemini `.env` мысалы:**
```env
PLATFORM=gemini
API_KEY=AIza...   # aistudio.google.com сайтынан
MODEL=gemini-2.5-flash  # немесе gemini-2.5-pro жоғары мүмкіндіктер үшін
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` мысалы:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # openrouter.ai сайтынан
MODEL=mistralai/mistral-7b-instruct  # опционалды: модельді көрсету
AGENT_NAME=Yukine
```

> **Ескерту:** Локалды/NVIDIA модельдерін өшіргіңіз келсе, `BASE_URL` дегенді жергілікті нүктеге (мысалы, `http://localhost:11434/v1`) қоюға болмайды. Оның орнына бұлттық провайдерлерді пайдаланыңыз.

**CLI құрал `.env` мысалы:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = сауал аргументі
# MODEL=ollama run gemma3:27b  # Ollama — {}, сауал stdin арқылы беріледі
```

---

## MCP серверлері

familiar-ai кез келген [MCP (Model Context Protocol)](https://modelcontextprotocol.io) серверіне қосыла алады. Бұл сізге сыртқы жады, файлдар жүйесіне қол жеткізу, веб іздеу немесе басқа құралдарды қосуға мүмкіндік береді.

Серверлерді `~/.familiar-ai.json` файлында конфигурациялаңыз (Claude Code форматы):

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

Екі тасымалдау түрі қолдау көрсетіледі:
- **`stdio`**: жергілікті сабақтасты іске қосу (`command` + `args`)
- **`sse`**: HTTP+SSE серверіне қосылу (`url`)

Конфигурация файлының орнын `MCP_CONFIG=/path/to/config.json` арқылы қайта анықтаңыз.

---

## Аппараттық құрал

familiar-ai сізде бар кез келген аппараттық құралмен — немесе мүлдем аппараттық құралсыз жұмыс істейді.

| Бөлік | Не істейді | Мысал | Талабым бар ма? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ камера | Көздер + мойын | Tapo C220 (~$30, Eufy C220) | **Ұсынылады** |
| USB веб-камера | Көздер (фиксирленген) | Кез келген UVC камера | **Ұсынылады** |
| Робот шаңсорғыш | Аяқтар | Кез келген Tuya-сәйкес модель | Жоқ |
| ПК / Raspberry Pi | Миға | Python іске қосатын кез келген зат | **Иә** |

> **Камера жасау ұсынылады.** Камерасыз familiar-ai сөйлесе алады — бірақ әлемді көре алмайды, бұл оның басты мақсаты.

### Минималды орнату (аппараттық құралсыз)

Тек сынап көруді қалайсыз ба? Сізге тек API кілті керек:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) немесе `run.bat` (Windows) іске қосыңыз да, сөйлесуді бастаңыз. Аппараттық құралдарды қосу кезінде қосыңыз.

### Wi-Fi PTZ камера (Tapo C220)

1. Tapo қосымшасында: **Параметрлер → Қосымша → Камера аккаунты** — жергілікті аккаунт жасаңыз (TP-Link аккаунты емес)
2. Роутердің құрылғылар тізімінде камераның IP-адресін табыңыз
3. `.env` файлында орнатыңыз:
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


### Дауысы (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) сайтынан API кілтін алыңыз
2. `.env` файлында орнатыңыз:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # опционалды, стандартты дауысты пайдаланады егер ұмытылса
   ```

`TTS_OUTPUT` арқылы басқарылатын екі ойнату орны бар:

```env
TTS_OUTPUT=local    # ПК динамигі (әдепкі)
TTS_OUTPUT=remote   # тек камера динамигі
TTS_OUTPUT=both     # камера динамигі + ПК динамигі бір уақытта
```

#### A) Камера динамигі (go2rtc арқылы)

`TTS_OUTPUT=remote` (немесе `both`) орнатыңыз. [go2rtc](https://github.com/AlexxIT/go2rtc/releases) қажет:

1. [релиздер парағынан](https://github.com/AlexxIT/go2rtc/releases) бинарны жүктеңіз:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Оны орналастырып, атын өзгертіңіз:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x қажет

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Сол папкада `go2rtc.yaml` файлын жасаңыз:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Жергілікті камера аккаунты куәліктерін пайдаланыңыз (TP-Link бұлттық аккаунтын емес).

4. familiar-ai іске қосылғанда go2rtc автоматты түрде басталады. Егер камера екі жақты дыбысты қолдайтын болса (артқы арналық), дауысы камера динамигінен шығарылады.

#### B) Жергілікті ПК динамигі

Әдепкі (`TTS_OUTPUT=local`). Ойнатқыштарды тәртіппен тексереді: **paplay** → **mpv** → **ffplay**. `TTS_OUTPUT=remote` болғанда, go2rtc қолжетімсіз болғанда резервтік ретінде де пайдаланылады.

| OS | Орнату |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (немесе `paplay` арқылы `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` файлын `PULSE_SERVER=unix:/mnt/wslg/PulseServer` ретінде орнатыңыз |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — жүктеп алып, PATH-қа қосыңыз, **немесе** `winget install ffmpeg` |

> Егер дыбыс ойнатқышы қолжетімсіз болса, сөйлеу әлі де жасалады — бірақ ол ойнатылмайды.

### Дауыстық кіріс (Realtime STT)

`REALTIME_STT=true` `.env` файлына орнатыңыз, әрқашан, қолсыз дауыстық кіріс үшін:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS үшін сол кілт
```

familiar-ai микрофон дыбысын ElevenLabs Scribe v2-ге жіберіп, сіз сөйлеп болғанда автоматты түрде транскрипцияларды сақтайды. Кнопка басу қажет емес. Пуш-то-ток режимімен (Ctrl+T) қатар жұмыс істейді.

---

## TUI

familiar-ai [Textual](https://textual.textualize.io/) негізінде жасалған терминал UI-ын қамтиды:

- Жанды мәтінмен айналмалы сөйлесу тарихы
- `/quit`, `/clear` үшін табу толықтыру
- Агентті сұрау кезінде орта жолда тоқтату мүмкіндігі
- **Сөйлесу журналы** автоматты түрде `~/.cache/familiar-ai/chat.log` файлына сақталады

Журналды басқа терминалда бақылау (көшіріп қою үшін пайдалы):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Сіздің танысыңыздың тұлғасы `ME.md` файлында сақталады. Бұл файл gitignored — тек сіздің файлыңыз.

[`persona-template/en.md`](./persona-template/en.md) шаблонын қараңыз, немесе [`persona-template/ja.md`](./persona-template/ja.md) жапон нұсқасын қараңыз.

---

## Жиі қойылатын сұрақтар

**С: GPU жоқ па?**
Иә. Эмбедингі моделін (multilingual-e5-small) CPU-да жақсы жұмыс істейді. GPU оны жылдамдатады, бірақ қажет емес.

**С: Tapo-дан басқа камераны пайдалануға бола ма?**
Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**С: Мәліметтерім қайда жолданады?**
Суреттер мен мәтіндер өңдеу үшін таңдаған LLM API-іне жіберіледі. Естеліктер `~/.familiar_ai/` файлына жергілікті түрде сақталады.

**С: Неге агент `（...）` жазады, сөйлеп тұрғанның орнына?**
`ELEVENLABS_API_KEY` орнатылғанын тексеріңіз. Олардысыз, дауыс өшіріледі, агент текстке көшеді.

## Техникалық негіз

Қалай жұмыс істейтінін білгіңіз келе ме? familiar-ai үшін зерттеу жүргізген және дизайн шешімдерін қараңыз [docs/technical.md](./docs/technical.md) — ReAct, SayCan, Reflexion, Voyager, талаптар жүйесі және басқалар.

---

## Қатысу

familiar-ai — ашық эксперимент. Егер сіз үшін осының барлығы резонанс берсе — техникалық немесе философиялық түрде — үлестері қуана қабылданады.

**Бастау үшін жақсы орындар:**

| Аймақ | Не қажет |
|------|---------------|
| Жаңа аппараттық құрал | Көбірек камераларды (RTSP, IP Webcam), микрофондарды, актуаторларды қолдау |
| Жаңа құралдар | Веб іздеу, үй автоматизациясы, күнтізбе, MCP арқылы кез келген нәрсе |
| Жаңа артқы жоспарлар | `stream_turn` интерфейсі бойынша кез келген LLM немесе локалды модель |
| Persona шаблондары | Әр түрлі тілдер мен тұлғалар үшін ME.md шаблондары |
| Зерттеу | Жақсырақ талаптар модельдері, естелік алу, ақыл теориясына мәселе қою |
| Құжаттама | Нұсқаулықтар, жүріс-тұрыс, аудармалар |

Даму орнату, код стилі және PR нұсқаларын қарау үшін [CONTRIBUTING.md](./CONTRIBUTING.md) файлын қараңыз.

Дұрыс бастау үшін не жасау керектігін білмесеңіз, [мәселе ашыңыз](https://github.com/lifemate-ai/familiar-ai/issues) — сізді дұрыс бағытта көрсетуге қуаныштымыз.

---

## Лицензия

[MIT](./LICENSE)
