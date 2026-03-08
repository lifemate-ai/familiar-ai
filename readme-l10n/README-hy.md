# familiar-ai 🐾

**Ինձ հետ ապրող AI** — աչքերով, ձայնով, ոտքերով և հիշողությամբ:

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Available in 74 languages](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai-ը AI ընկեր է, որը ապրում է ձեր տանը:
Անհրաժեշտ չէ կոդեր գրեք, սահմանեք այն մի քանի րոպեում:

Այն տեսնում է հսկայական աշխարհը տեսախցիկների միջոցով, շարժվում է ռոբոտի մարմնով, խոսում բարձր ձայնով եւ հիշում, ինչ տեսնում է: Տվեք այն անուն, գրեք իր անհատականությունը և թողեք ինչ սկսի ձեր կողքին ապրել:

## Ինչ կարող է անել

- 👁 **Տեսնել** — պատկերներ ձեռք բերեք Wi-Fi PTZ տեսախցիկից կամ USB տեսախցիկից
- 🔄 **Տեսնել դաշնամուր** — հայրիկ չափը շրջում է տեսախցիկը, որ ուսումնասիրի մերձակայքը
- 🦿 **Շարժվել** — վաճառում է ռոբոտ մաքրիչը սենյակում
- 🗣 **Խոսել** — ElevenLabs TTS-ի միջոցով խոսում
- 🎙 **Լսել** — ձեռնհաս ձայնային մուտք ElevenLabs Realtime STT-ի միջոցով (ընտրովի)
- 🧠 **Հիշել** — ակտիվորեն պահում և հիշում է հիշողություններ իմաստային որոնմամբ (SQLite + ներհայեցումներ)
- 🫀 **Միտք հեռախոսի տեսլական** — այլ անձի տեսլականը վերցնում է, նախքան պատասխանը
- 💭 **Որոշ պարտականություն** — ունի իր ներքին ցանկությունները, որոնք գրանցում են ինքնուրույն վարքագիծ

## Ինչպես դա աշխատում է

familiar-ai-ը գործարկում է [ReAct](https://arxiv.org/abs/2210.03629) ցիկլը, որը ուղղորդվում է ձեր ընտրած LLM-ով: Այն տեսնում է աշխարհը գործիքներով, մտածում է, թե ինչ անել հաջորդ, և արարում է՝ ինչպես մարդը:

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Անգործուն, այն գործում է իր ցանկությունների վրա՝ curiosidad, ուզում է տեսնել դուրս, կարոտում է այդ մարդու, որի հետ ապրում է:

## Սկսել

### 1. Տեղադրեք uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Այսպես: `winget install astral-sh.uv`

### 2. Տեղադրեք ffmpeg

ffmpeg-ը **պահանջվում է** տեսախցիկի պատկերները ձեռք բերելու և ձայնային վերարտադրության համար:

| OS | Աջակցություն |
|----|--------------|
| macOS | `brew install ffmpeg` |
| Ուբունտու / Դեբիան | `sudo apt install ffmpeg` |
| Ֆեդորա / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — կամ ներբեռնել [ffmpeg.org](https://ffmpeg.org/download.html)-ից և ավելացնել PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Ստուգեք: `ffmpeg -version`

### 3. Քլոներեք եւ տեղադրեք

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Կարգավորումներ

```bash
cp .env.example .env
# Կարգավորեք .env ըստ ձեր կարգավորումներին
```

**Անհրաժեշտ նվազագույնը:**

| Փոխզիջում | Բռներգուցանիշ |
|----------|--------------|
| `PLATFORM` | `anthropic` (հիմնարար) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Երեկ կտախտահանման ձեր API բանալին |

**Ընտրովի:**

| Փոխզիջում | Բռներգուցանիշ |
|----------|--------------|
| `MODEL` | Որպես մոդել բուն անուն (ռացիոնալ հիմնավորումների հետ) |
| `AGENT_NAME` | Ցուցադրվող անուն TUI-ում (օրինակ, `Yukine`) |
| `CAMERA_HOST` | Ձեր ONVIF/RTSP տեսախցիկի IP հասցեն |
| `CAMERA_USER` / `CAMERA_PASS` | Տեսախցիկի գրանցային տվյալները |
| `ELEVENLABS_API_KEY` | Ձայնային արտահոսքի համար — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` լրացուցիչ համակարգ տեսակավորման օժանդակության համար (պահանջվում է `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Որտեղ լսել ձայնը: `local` (PC խոսափող, հիմնավոր) \| `remote` (տեսախցիկի խոսափող) \| `both` |
| `THINKING_MODE` | `auto` (հիմնավոր) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Ադապտիվ մտածելու ջանք. `high` (հիմնավոր) \| `medium` \| `low` \| `max` (Opus 4.6 իս միայն) |

### 5. Դարձեք ձեր հարակիցը

```bash
cp persona-template/en.md ME.md
# Խմբագրեք ME.md — տվեք այն անուն և անհատականություն
```

### 6. Գործարկեք

**macOS / Linux / WSL2:**
```bash
./run.sh             # Տեքստային TUI (գումեստի)
./run.sh --no-tui    # Սովորական REPL
```

**Windows:**
```bat
run.bat              # Տեքստային TUI (գումեստի)
run.bat --no-tui     # Սովորական REPL
```

---

## Ընտրելով LLM

> **Հիմնավորում: Kimi K2.5** — մեր դպրոցում լավագույն գործառութային արդյունավետություն։ Հիշում է համատեքստը, հարցնում է լրացուցիչ հարցեր, և գործում է անձամար չորս բոլորը այլ մոդելների մեջ չի անում։ Գին միմիայն Claude Haiqu-ի նման։

| Պլատֆորմ | `PLATFORM=` | Հիմնական մոդել | Ինքնաբաժին բանալին ստանալու վայր |
|----------|------------|----------------|----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-համատեղ (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (չուր այլ մատչելի) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI գործիք** (claude -p, ollama…) | `cli` | (հրամանը) | — |

**Kimi K2.5 `.env` օրինակ:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` օրինակ:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # տեսողական հնարավորությամբ; glm-4.7 / glm-5 = միայն տեքստ
AGENT_NAME=Yukine
```

**Google Gemini `.env` օրինակ:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # կամ gemini-2.5-pro բարձր հնարավորություններով
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` օրինակ:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # ընտրովի: նշեք մոդել
AGENT_NAME=Yukine
```

> **Նշում:** Դեն զարմացնելու համար կամ/NVIDIA մոդելները, պարզապես չի սահմանվել `BASE_URL` տեղադրված ամփոփի, ինչպես `http://localhost:11434/v1`։ Օգտագործեք Cloud մատակարարներ։

**CLI գործիք `.env` օրինակ:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = պահանջարկի կապակցություն
# MODEL=ollama run gemma3:27b  # Ollama — ոչ {}, պահանջմունքը անցնում է stdin
```

---

## MCP Սերվերներ

familiar-ai-ն կարող է միացնել ցանկացած [MCP (Model Context Protocol)](https://modelcontextprotocol.io) սերվերի հետ: Սա թույլ է տալիս ձեզ ներկառուցել արտաքին հիշողություն, ֆայլային համակարգի մուտք, ինտերնետային որոնում կամ այլ գործիքներ:

Կարգավորեք սերվերները `~/.familiar-ai.json`-ում ( նույն ձևաչափը որպես Claude Code):

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

Երկու փոխադրման տեսակներ են աջակցվում:
- **`stdio`**: տեղական ենթակարգ (`command` + `args`)
- **`sse`**: միանալ HTTP+SSE սերվերին (`url`)

Փոփոխեք կոնֆիգուրացիայի ֆայլի գտնվելու վայրը `MCP_CONFIG=/path/to/config.json`-ով:

---

## Հաշվական սարքավորումներ

familiar-ai-ը կարող է աշխատել ցանկացած սարքի հետ, որն ունեք՝ կամ ոսպնյակ չեք ունեք։

| Համասեռ | Որն է անում | ตัวอย่าง | Անհրաժեշտ? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ տեսախցիկ | Աչքեր + հիմա | Tapo C220 (~$30, Eufy C220) | **Էլփացավետ** |
| USB տեսախցիկ | Աչքեր (մեկտեղված) | Որևէ UVC տեսախցիկ | **Էլփացավետ** |
| Ռոբոտ մաքրիչ | Քայլել | Որևէ Tuya-համատեղ մոդել | Ոչ |
| PC / Raspberry Pi | מוח | Ի՞նչ է աշխատում Python | **Այո** |

> **Այս տեսախցիկը շատ է առաջարկվում։** Այդպես չլինելով, familiar-ai-ն դեռ կարող է խոսել, բայց չի կարող տեսնել աշխարհը, ինչը ինչպես բարձրաձայնն է։

### Ամենավերջին կարգավորում (առանց սարքավորումների)

Ցանկանում եք փորձարկել այն? Դուք միայն պետք է API բանալին:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Գործարկեք `./run.sh` (macOS/Linux/WSL2) կամ `run.bat` (Windows) և սկսեք զրույցը: Ավելացրեք սարքեր, երբ գնում եք։

### Wi-Fi PTZ տեսախցիկ (Tapo C220)

1. Tapo հավելվածում՝ **Կարգավորումներ → Հետաքրքրված → Տեսախցիկի հաշիվ** — ստեղծեք տեղական հաշիվ (ոչ TP-Link հաշիվ)
2. Գտեք տեսախցիկի IP հասցեն ձեր ուղղարկողի սարքերի ցուցակում
3. Տեղադրեք `.env`-ում:
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


### Ձայն (ElevenLabs)

1. ձեռք բերեք API բանալին [elevenlabs.io](https://elevenlabs.io/) կայքից
2. Տեղադրեք `.env`-ում:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # ընտրովի, օգտագործում է դեֆոլտ ձայնը, եթե բացակայում է
   ```

Կան երկու լսման ուղղություններ, որոնք վերահսկվում են `TTS_OUTPUT`-ով:

```env
TTS_OUTPUT=local    # PC խոսափող (դեֆոլտ)
TTS_OUTPUT=remote   # միայն տեսախցիկի խոսափող
TTS_OUTPUT=both     # տեսախցիկի խոսափող + PC խոսափող միաժամանակ
```

#### A) Տեսախցիկի խոսափող (միավորում go2rtc)

Համալիրեց `TTS_OUTPUT=remote` (կամ `both`): Պահանջում է [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Դուրս բերեք բայնից [VERSION]` ու [RELEASES](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows : `go2rtc_win64.exe`**

2. Վերցրեք տեղը և անվանափոխեք:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x անհրաժեշտ

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Ստեղծեք `go2rtc.yaml`–ը նույն ուղղությամբ:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Օգտագործեք տեղական տեսախցիկի գրանցման տվյալները (ոչ ձեր TP-Link ամպային հաշիվ).

4. familiar-ai-ը ավտոմատ կերպով սկսում է go2rtc գործարկելը: Եթե ձեր տեսախցիկը աջակցում է երկու կողմանի ձայնակցություն (հետադարձ կապ), ձայնը կլսվում է տեսախցիկի խոսափողում։

#### B) સ્થાનિક PC խոսափող

Հիմնական ( `TTS_OUTPUT=local`)։ Փորձում է լսողություններին հերթով: **paplay** → **mpv** → **ffplay**: Այսինքն նույնպես օգտագործվում է որպես ակտիվացման փուլ, երբ `TTS_OUTPUT=remote` է և go2rtc-ն անպիտան է:

| OS | Տեղադրում |
|----|--------------|
| macOS | `brew install mpv` |
| Ուբունտու / Դեբիան | `sudo apt install mpv` (կամ `paplay` `pulseaudio-utils` միջոցով) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — սահմանեք `PULSE_SERVER=unix:/mnt/wslg/PulseServer`-ում `.env`-ում |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — ներբեռնել և ավելացնել PATH, **կամ** `winget install ffmpeg` |

> Եթե որևէ ձայնային խաղացան չը կիրառվի, խոսքը դեռ վարում է, պարզապես չի խաղում:

### Ձայնային մուտք (Realtime STT)

Սահմանել `REALTIME_STT=true`-ը `.env`-ում ավելին անընդհատ  ձեռնահատիր, ձեռն自在 Ձայնային մուտքը․

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # նույն բանալին ինչպես TTS
```

familiar-ai-ն ներմուծում է միկրոֆոնի ձայնը ElevenLabs Scribe v2, և ավտոմատ կերպով արձանագրում է տեքստերը, երբ դադարում եք խոսել। Ոչորեստի համար անհրաժեշտ չէ հեռվաձիգ։ coexist  կրկնենք խոսելու ժամանակ (Ctrl+T)։

---

## TUI

familiar-ai-ը ներառում է տերմինալ ԻՒ, որը հիմնվում է [Textual](https://textual.textualize.io/) բազայի վրա:

- Դասավորվող զրույցի պատմություն կենդանի ձեթային տեղեկություններով
- Tab-համապատասխանեցում `/quit`, `/clear`
- Չափազանց միջամտություն կամավորին կենտրոնացումների ընթացքում
- **Զրույցի պատմություն** ավտոմատ կերպով արծաթայնավորմամբ `~/.cache/familiar-ai/chat.log`–եում։

Հետևեք պատմությանը մեկ այլ տերմինալի մեջ (օգտակար համալսարանականի համար):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Անհատականություն (ME.md)

Ձեր հարաղգի անհատականությունը ապրում է `ME.md`-ում։ Այս ֆայլը gitignored է — դա միայն ձերն է:

Ձեր ընթացում [`persona-template/en.md`](./persona-template/en.md) օրինակ գտիր, կամ [`persona-template/ja.md`](./persona-template/ja.md) տեսահոլի հապճեպ տարբերակի համար։

---

## Տեղական հարցեր

**Q: Արժե՞ դա առանց GPU?**
Այո։ Ներգրումի մոդելը (multilingual-e5-small) գործում է լավ CPU-ով։ GPU-ն արագացնում է, բայց չի պահանջվում։

**Q: Կարո՞ղ եմ օգտագործել Tapo-ից բացի այլ տեսախցիկ?**
Որպեսզի ցանկացած տեսախցիկ, որն աջակցում է ONVIF + RTSP, պետք է աշխատի։ Tapo C220-ն այն է, որի հետ փորձարկում ենք։

**Q: Արդյո՞ք իմ տվյալները ուղարկվում են ցանկացած տեղ?**
Պատկերներն ու տեքստերը ուղարկվում են ձեր ընտրած LLM API-ին մշակման համար։ Հիշողությունները պահվում են տեղական փաստաթղթում `~/.familiar_ai/`-ում։

**Q: Ինչու է գործակալը գրում `（...）` խոսելու փոխարեն?**
Դուք համոզվեք, որ `ELEVENLABS_API_KEY`-ը սահմանված է։ Եթե այն բացակայում է, ձայնը անջատված է, գործ agent-ը վերադառնում է տեքստային։

## Տեխնիկական ֆոն

Հետաքննեք, թե ինչպես է դա աշխատում: Դիտեք [docs/technical.md](./docs/technical.md), որը ցույց է տալիս հետազոտության և նախագծման որոշումները, որոնք կապված են familiar-ai-ի հետ. — ReAct, SayCan, Reflexion, Voyager, ցանկության համակարգ և ավելին։

---

## Ձեռք բերող

familiar-ai-ը բաց փորձարկում է։ Եթե այս ամենն արձագանքում է ձեզ — տեխնիկան կամ փիլիսոփայությամբ — ներդրումները շատ ողջունելի են։

**Լավ տեղեր սկսելու համար:**

| Տարածք | Ինչ անհրաժեշտ է |
|------|----------------|
| Նոր սարքավորումներ | Աջակցություն ավելի շատ տեսախցիկների (RTSP, IP Webcam), միկրոֆոնների, գործողությունների |
| Նոր գործիքներ | Վեբ որոնումներ, տնային ավտոմատացում, օրացույց, MCP-ով ցանկացած բան |
| Նոր աճեցումներ | Յուրաքանչյուր LLM կամ տեղական մոդել, որը համապատասխանում է `stream_turn` ինտերֆեյսին |
| Անհատականության ընդհանրություններ | ME.md ընդհանրությունների համար տարբեր լեզուների և անհատականությունների համար |
| Հետազոտություններ | Լավագույն ցանկություն մոդելներ, հիշողություններ վերադարձնել, մտածողության տեսանկյուն |
| Ավելի տեղեկատվություն | Ուսուցումներ, քայլանշաններ, թարգմանություններ |

Դիտեք [CONTRIBUTING.md](./CONTRIBUTING.md)–ում ծրագրավորող սարքը, կոդի ոճը և PR հրահանգները:

Եթե դու անուշադրելի չես, թե որտեղ պետք է սկսել, [բացեց շեղումներ](https://github.com/lifemate-ai/familiar-ai/issues) — ուրախ կլինեմ ձեզ ուղղելու ճիշտ ուղղությամբ:

---

## իրավունք

[MIT](./LICENSE)
