# familiar-ai 🐾

**Сиздин жаныңызда жашай турган ИИ** — көздөр, үн, буттар жана жүрүм-турум менен.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 тилде жеткиликтүү](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai - сиздин үйүңүздө жашаган ИИ коштоочу.
Аны бир нече мүнөттө орнотуңуз. Код жазуу талап кылынбайт.

Ал камералар аркылуу чыныгы дүйнөнү кабыл алат, робот денеси менен кыймылдайт, Үн чыгарат жана көргөндөрүн эстеп калат. Ага ат бериңиз, анын жаратылышын жазыңыз жана сиз менен жашоосуна уруксат бериңиз.

## Алар эмне кыла алат

- 👁 **Көрүү** — Wi-Fi PTZ камерасынан же USB веб-камерадан сүрөттөрдү тартуу
- 🔄 **Айлануу** — камераны айлантып, курчап турган кеңешти изилдөө
- 🦿 **Кыймылдоо** — бөлмөдө кээ бир вакуумдук роботторду жетектөө
- 🗣 **Сүйлөө** — ElevenLabs TTS аркылуу сүйлөйт
- 🎙 **Угуу** — ElevenLabs реалдуу убакыттагы STT (опция)
- 🧠 **Эс тутуу** — активдүү эс тутумдарды сактоо жана чакыруу семантикалык издөөлөр менен (SQLite + эмбеддингдер)
- 🫀 **Адамдын ойлонуу теориясы** — жооп берер алдында башка адамдын көз карашын кабыл алат
- 💭 **Тилек** — автономдуу жүрүм-турумду түрткү берүүчү ички мотивдерге ээ

## Ал кандай иштейт

familiar-ai сиздин тандаган LLM'иңиз аркылуу [ReAct](https://arxiv.org/abs/2210.03629) циклын жүргүзөт. Ал дүйнөнү куралдар аркылуу кабыл алат, кийинки кандай иш кылуу жөнүндө ойлонот жана аракеттенет — адам сыяктуу.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Эгер токтоп турган болсо, ал өз каалоолоруна жараша аракет кылат: кызыгуу, сыртка карап турак умтулуу, жаныдагы адамды сагына алуу.

## Баштоо

### 1. uv орнотуңуз

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Немесе: `winget install astral-sh.uv`

### 2. ffmpeg орнотуңуз

ffmpeg - камера сүрөтүн тартуу жана үн ойнотуу үчүн **талап кылынат**.

| OS | Команда |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — же [ffmpeg.org](https://ffmpeg.org/download.html) сайтынан жүктөп алып, PATH'ка кошуңуз |
| Raspberry Pi | `sudo apt install ffmpeg` |

Текшериңиз: `ffmpeg -version`

### 3. Клонирлеп, орнотуңуз

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Конфигурируйте

```bash
cp .env.example .env
# Өз параметрлериңиз менен .env файлын түзөтүңүз
```

**Минималдуу талап кылынган:**

| Өзгөчөлүк | Сүрөттөмө |
|----------|-------------|
| `PLATFORM` | `anthropic` (бул стандарт) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Тандалган платформаңыз үчүн API ачкычы |

**Опционалдуу:**

| Өзгөчөлүк | Сүрөттөмө |
|----------|-------------|
| `MODEL` | Модель аты (платформа боюнча акылга сыярлык стандарт) |
| `AGENT_NAME` | TUI'да көрсөтүлүүчү ат (мисалы, `Yukine`) |
| `CAMERA_HOST` | ONVIF/RTSP камераңыздын IP дареги |
| `CAMERA_USER` / `CAMERA_PASS` | Камеранын маалыматы |
| `ELEVENLABS_API_KEY` | Үн чыгарышка — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` — коёлук колдук кандай болсо да үн киргизүү (талап кылат `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Эмне жерде үн ойнотуу: `local` (ПК динамиги, стандарт) \| `remote` (камера динамиги) \| `both` |
| `THINKING_MODE` | Anthropic үчүн гана — `auto` (стандарт) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Адаптивдүү ойлоо жөндөмү: `high` (стандарт) \| `medium` \| `low` \| `max` (Opus 4.6 үчүн гана) |

### 5. Сиздин гана жакынкыңызды түзүңүз

```bash
cp persona-template/en.md ME.md
# ME.md файлын түзөтүңүз — ага ат бериниз жана жаратылышы
```

### 6. Жүргүзүү

**macOS / Linux / WSL2:**
```bash
./run.sh             # Текстуалдуу TUI (тунук чыгаруу)
./run.sh --no-tui    # Жөнөкөй REPL
```

**Windows:**
```bat
run.bat              # Текстуалдуу TUI (тунук чыгаруу)
run.bat --no-tui     # Жөнөкөй REPL
```

---

## LLM тандап алуу

> **Тандалган: Kimi K2.5** — азыркыга чейин эң жакшы агенттик иштөөлөр. Контекстин байкап, суроолор бериңиз, жана угуучунун өз алдынча аракеттери. Баасы Claude Haiku'га окшош.

| Платформа | `PLATFORM=` | Стандартты модель | Ачкычты кайдан алууга болот |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI'га ылайыктуу (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (бири-бирине подключа)- | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI куралы** (claude -p, ollama…) | `cli` | (команда) | — |

**Kimi K2.5 `.env` мисалы:**
```env
PLATFORM=kimi
API_KEY=sk-...   # platform.moonshot.ai'дан
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` мисалы:**
```env
PLATFORM=glm
API_KEY=...   # api.z.ai'дан
MODEL=glm-4.6v   # көрүүнү камсыз кылат; glm-4.7 / glm-5 = текс гана
AGENT_NAME=Yukine
```

**Google Gemini `.env` мисалы:**
```env
PLATFORM=gemini
API_KEY=AIza...   # aistudio.google.com'дан
MODEL=gemini-2.5-flash  # же gemini-2.5-pro жогорку мүмкүнчүлүк үчүн
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` мисалы:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # openrouter.ai'дан
MODEL=mistralai/mistral-7b-instruct  # опция: моделди көрсөтүңүз
AGENT_NAME=Yukine
```

> **Эскертүү:** Локалдуу/NVIDIA модельдерди өчүрүү үчүн, жөн гана `BASE_URL`'ды локалдуу эндпоинтке орнотуунун кереги жок, мисалы, `http://localhost:11434/v1`. Бул кызматтарды кыйынчылыксыз колдонуу үчүн пайдаланбаңыз.

**CLI куралы `.env` мисалы:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt аргументи
# MODEL=ollama run gemma3:27b  # Ollama — {} жок, prompt stdin аркылуу өтөт
```

---

## MCP Серверлери

familiar-ai бардык [MCP (Model Context Protocol)](https://modelcontextprotocol.io) серверлерине туташууга мүмкүндүк берет. Бул сизге сырттан эс тутумду, файл системасын, веб издөөнү же башка куралдарды колдонууга мүмкүндүк берет.

Серверлерди `~/.familiar-ai.json` файлына конфигурациялаңыз (Claude Carbon кодунун форматы):

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

Эки транспорт түрү колдоого алынган:
- **`stdio`**: жергиликтүү жүктоп колдонууну (команда + аргументтер)
- **`sse`**: HTTP+SSE серверине туташуу (`url`)

Конфигурация файлынын жерин `MCP_CONFIG=/path/to/config.json` аркылуу өзгөртүңүз.

---

## Жабдык

familiar-ai сиздин колуңузда бар жабдыктар менен же эч нерсе менен иштейт.

| Бөлүк | Эмне кылат | Мисалы | Талап кылынабы? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ камера | Көздөр + мурут | Tapo C220 (~$30, Eufy C220) | **Жакшы сунуштала турган** |
| USB веб-камера | Көздөр (туруктуу) | Ар кандай UVC камера | **Жакшы сунуштала турган** |
| Робот-вакуум | Пот | Ар кандай Tuya'га шайкеш модель | Жок |
| ПК / Raspberry Pi | Ми | Python иштөөнү камсыз кыла турган нерсе | **Ооба** |

> **Камераны колдонуу күчтүү сунушталат.** Эгерде камерасыз болсо, familiar-ai сапаттай сүйлөйт — бирок дүйнөнү көрө албайт, бул анын негизги себеби.

### Минималдуу орнотуу (жабдыксыз)

Жөн гана аракет кылгым келет деп жатасызбы? Сизге болгону API ачкычы эле керек:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) же `run.bat` (Windows) командасын иштетиңиз. Жабдыктарды кошуп аласыз.

### Wi-Fi PTZ камера (Tapo C220)

1. Tapo тиркемесинде: **Настройки → Продвинутый → Камера аккаунт** — жергиликтүү аккаунт түзүңүз (TP-Link аккаунт эмес)
2. Роутердин буюмдар тизмесинде камераңыздын IP дарегин табыңыз
3. `.env` файлына орнотуңуз:
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


### Үн (ElevenLabs)

1. API ачкычын алыңыз [elevenlabs.io](https://elevenlabs.io/)
2. `.env` файлына орнотуңуз:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # опционалдуу, эгерде берилбесе, стандарт үн колдонулат
   ```

Эки үн ойноп берүү орундары `TTS_OUTPUT` тарабынан көзөмөлдөнөт:

```env
TTS_OUTPUT=local    # ПК динамиги (стандарт)
TTS_OUTPUT=remote   # только камера динамиги
TTS_OUTPUT=both     # кезекте камера динамиги + ПК динамиги
```

#### A) Камера динамиги (go2rtc аркылуу)

`TTS_OUTPUT=remote` (же `both`) орнотуңуз. [go2rtc](https://github.com/AlexxIT/go2rtc/releases) талап кылынат:

1. Релиздер бетинен бингди жүктөп алыңыз:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Орундатуу жери жана атын өзгөртіңиз:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x талап кылынат

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Ошол папкада `go2rtc.yaml` файлын түзүңүз:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Жергиликтүү камера аккаунтунун маалыматын (TP-Link булуту аккаунтунан эмес) колдонуңуз.

4. familiar-ai автоматтык түрдө go2rtc'ты иштете баштайт. Эгер сиздин камера эки тараптуу үндү (кайрылышчу) колдосо, үн камера динамигинен угулат.

#### B) Жергиликтүү ПК динамиги

Стандарттык (`TTS_OUTPUT=local`). Төмөндөгү оюнчу сөздөрдү буйрутуп көрсөтөт: **paplay** → **mpv** → **ffplay**. Бул ошондой эле `TTS_OUTPUT=remote` башкаруусунун жоголгон учурда резерв катары колдонулат.

| OS | Орнотуу |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (же `paplay` аркылуу `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` файлында `PULSE_SERVER=unix:/mnt/wslg/PulseServer` орнотуңуз |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — жүктөп алып, PATH'ка кошуңуз, **же** `winget install ffmpeg` |

> Эгер үн ойноп берүүчү жок болсо, сүйлөө дагы жасалат — бирок ал ойнобойт.

### Үн киргизүү (Realtime STT)

`REALTIME_STT=true` орнотуңузж `.env` файлында дайыма активдүү, колсуз үн киргизүү үчүн:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS менен бирдей ачкыч
```

familiar-ai микрофондун үнүн ElevenLabs Scribe v2'ге агып, сүйлөөнү токтоткондо транскрипцияларды авто-кайта жазады. Кнопканын басылышы талап кылынбайт. Пушки сүйлөшүү режиминде ("Ctrl+T") да түндүн маанисин бөлүшө алат.

---

## TUI

familiar-ai [Textual](https://textual.textualize.io/) менен түзүлгөн терминалдык UI камтыйт:

- Түз текст менен диалог тарыхы
- `/quit`, `/clear` үчүн таб-тапшырма
- Ойлоно турган учурда агентти тыныгуу бериштирүү жазууга мүмкүнчүлүк берет
- **Сүйлөшүү журналы** автоматтык түрдө `~/.cache/familiar-ai/chat.log` файлында сакталат

Журналды башка терминалда көрүү үчүн (канчалык колдонуп көрүү үчүн пайдалуу):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Персона (ME.md)

Сиздин жакыныңыздын жеке жаратылышы `ME.md` файлына жазылат. Бул файл gitIgnored — ал бир гана сиздики.

[`persona-template/en.md`](./persona-template/en.md) файлын мисал катары, же [`persona-template/ja.md`](./persona-template/ja.md) япон версиясын карап чыгыңыз.

---

## Жаңылыктар

**С: GPUсыз иштейбиби?**
Ооба. Эмбеддинг модели (multilingual-e5-small) CPU'да жакшы иштейт. GPU аны тездетет, бирок керек эмес.

**С: Tapoдан башка камераны колдоно аламбы?**
Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**С: Менин маалыматтарым кайдадыр жөнөтүлүүдөбү?**
Сүрөттөр жана текст тандалган LLM API'га иштетүү үчүн жөнөтүлөт. Эс тутум жергиликтүү `~/.familiar_ai/` файлына сакталат.

**С: Агент эмне үчүн `（...）` жазат, сүйлөбөйт?**
`ELEVENLABS_API_KEY` орнотулгандыгын текшериңиз. Эгерде жок болсо, үн өчүрүлөт жана агент текстке кайтууга аргасыз.

## Техникалык фон

Кайда мектеп бар, ал кандайча иштейт? [docs/technical.md](./docs/technical.md) бөлүмүндө familiar-ai'нын изилдөөлөрүнө жана долбоорлоо чечимдерине кайрылып көрүңүз — ReAct, SayCan, Reflexion, Voyager, тилек системасы жана башкалар.

---

## Кошулуу

familiar-ai ачык эксперимент. Эгерде ушул жерде сиздин кызыгууларыңыз болсо — техникалык же философиялык — салымдарга абдан кубанычтабыз.

**Баштоо үчүн жакшы жерлер:**

| Область | Нужды |
|------|---------------|
| Жаңы жабдыктар | Көп камераларды (RTSP, IP Webcam), микрофондорду, акчалардын колдоосу |
| Жаңы куралдар | Веб издейли, дому автоматизация, күнтүзгү, MCP аркылуу ар кандай |
| Жаңы бэкенддер | `stream_turn` интерфейсине туура келген ар кандай LLM же локалдуу модель |
| Персона шаблондору | Түрдүү тилдерде жана жаратылыштарда ME.md шаблондору |
| Изилдөө | Кепилденген моделдер, эс тутумду кайтаруу, ойлонуу теориясын суроолор |
| Документация | Сабақтар, өткөрмөлөр, котормолор |

[CONTRIBUTING.md](./CONTRIBUTING.md) бөлүмүндө иштеп чыгуу курулушу, код стили жана PR буйруктары жөнүндө маалымат алууга болот.

Эгер каяктан башталаарын билбей жатсаңыз, [мурдагы масала ачуу](https://github.com/lifemate-ai/familiar-ai/issues) — сизди туура багыттоого кубанычтабыз.

---

## Лицензия

[MIT](./LICENSE)
