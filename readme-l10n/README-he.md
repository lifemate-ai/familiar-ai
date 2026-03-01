# familiar-ai 🐾

**בינה מלאכותית שחיה לצידך** — עם עיניים, קול, רגליים וזיכרון.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [זמין ב-74 שפות](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai הוא בן לוויה בינה מלאכותית שחי בביתך.
הקדם אותה בכמה דקות. אין צורך בקידוד.

היא תופסת את העולם האמיתי דרך מצלמות, נעה על גוף רובוטי, מדברת בקול, וזוכרת מה שהיא רואה. תן לה שם, תכתוב את האישיות שלה, ותן לה לחיות איתך.

## מה היא יכולה לעשות

- 👁 **לראות** — תופסת תמונות ממצלמת Wi-Fi PTZ או מצלמת USB
- 🔄 **להסתכל סביב** — פונה ומטה את המצלמה כדי לחקור את הסביבה שלה
- 🦿 **לזוז** — נוהגת בשואב רובוטי כדי לנדוד בחדר
- 🗣 **לדבר** — מדברת באמצעות ElevenLabs TTS
- 🎙 **להקשיב** — קלט קול ללא ידיים באמצעות ElevenLabs Realtime STT (בהסכמה)
- 🧠 **לזכור** — שומרת ומשחזרת זיכרונות באמצעות חיפוש סמנטי (SQLite + הטמעות)
- 🫀 **תיאוריה של תודעה** — לוקחת את נקודת המבט של האדם האחר לפני שהיא מגיבה
- 💭 **רצון** — יש לה מניעים פנימיים שגורמים להתנהגות אוטונומית

## איך זה עובד

familiar-ai מפעילה לולאת [ReAct](https://arxiv.org/abs/2210.03629) שמופעלת על ידי הבחירה שלך ב-LLM. היא תופסת את העולם דרך כלים, חושבת מה לעשות הלאה, ופועלת — בדיוק כמו שאדם היה עושה.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

כאשר היא ללא פעולה, היא פועלת בהתאם לרצונותיה: סקרנות, רצון להסתכל החוצה, געגועים לאדם שהיא חיה איתו.

## איך להתחיל

### 1. התקן uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
או: `winget install astral-sh.uv`

### 2. התקן ffmpeg

ffmpeg הוא **דרישה** לתפיסת תמונות מצלמה וניגון אודיו.

| מערכת הפעלה | פקודה |
|--------------|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — או הורד מ-[ffmpeg.org](https://ffmpeg.org/download.html) והוסף ל-PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

אמת: `ffmpeg -version`

### 3. שכפל והתקן

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. קונפיגורציה

```bash
cp .env.example .env
# ערוך את .env עם ההגדרות שלך
```

**מינימום דרוש:**

| משתנה | תיאור |
|--------|--------|
| `PLATFORM` | `anthropic` (ברירת מחדל) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | מפתח ה-API שלך לפלטפורמה הנבחרת |

**אופציונלי:**

| משתנה | תיאור |
|--------|--------|
| `MODEL` | שם המודל (ברירות מחדל סבירות לפי פלטפורמה) |
| `AGENT_NAME` | שם התצוגה המוצג ב-TUI (למשל, `Yukine`) |
| `CAMERA_HOST` | כתובת ה-IP של מצלמת ONVIF/RTSP שלך |
| `CAMERA_USER` / `CAMERA_PASS` | פרטי ההזדהות של המצלמה |
| `ELEVENLABS_API_KEY` | עבור פלט קול — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` כדי להפעיל קלט קול תמידי ללא ידיים (דורש `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | היכן לנגן אודיו: `local` (רמקול PC, ברירת מחדל) \| `remote` (רמקול מצלמה) \| `both` |
| `THINKING_MODE` | אנתרופית בלבד — `auto` (ברירת מחדל) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | מאמץ חשיבה אדפטיבי: `high` (ברירת מחדל) \| `medium` \| `low` \| `max` (רק Opus 4.6) |

### 5. צור את המוכר שלך

```bash
cp persona-template/en.md ME.md
# ערוך את ME.md — תן לו שם ואישיות
```

### 6. הפעל

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textual TUI (מומלץ)
./run.sh --no-tui    # REPL פשוט
```

**Windows:**
```bat
run.bat              # Textual TUI (מומלץ)
run.bat --no-tui     # REPL פשוט
```

---

## בחירת LLM

> **מומלץ: Kimi K2.5** — הביצועים הייעודיים הטובים ביותר שנבדקו עד כה. מבחינה בהקשר, שואל שאלות נוספות, ופועל באופן אוטונומי בדרכים שמודלים אחרים לא עושים. במחיר דומה ל-Claude Haiku.

| פלטפורמה | `PLATFORM=` | מודל ברירת מחדל | היכן להשיג מפתח |
|----------|------------|----------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| תואם OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (מספר ספקים) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (הפקודה) | — |

**דוגמה ל-.env של Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # מ-platform.moonshot.ai
AGENT_NAME=Yukine
```

**דוגמה ל-.env של Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # מ-api.z.ai
MODEL=glm-4.6v   # עם אפשרות ראייה; glm-4.7 / glm-5 = טקסט בלבד
AGENT_NAME=Yukine
```

**דוגמה ל-.env של Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # מ-aistudio.google.com
MODEL=gemini-2.5-flash  # או gemini-2.5-pro עבור יכולות גבוהות יותר
AGENT_NAME=Yukine
```

**דוגמה ל-.env של OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # מ-openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # אופציה: ציין מודל
AGENT_NAME=Yukine
```

> **הערה:** כדי להשבית מודלים מקומיים/NVIDIA, פשוט אל תגדיר `BASE_URL` לנקודת קצה מקומית כמו `http://localhost:11434/v1`. השתמש בספקי ענן במקום.

**דוגמה ל-.env של CLI tool:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = פרמטר הפנייה
# MODEL=ollama run gemma3:27b  # Ollama — ללא {}, הפנייה ממועברת דרך stdin
```

---

## שרתי MCP

familiar-ai יכולה להתחבר לכל שרת [MCP (Model Context Protocol)](https://modelcontextprotocol.io). זה מאפשר לך לחבר זיכרון חיצוני, גישה למערכת קבצים, חיפוש באינטרנט, או כל כלי אחר.

קבע שרתים ב- `~/.familiar-ai.json` (באותו פורמט כמו Claude Code):

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

שני סוגי חיבור נתמכים:
- **`stdio`**: השקת תהליך מקומי (`command` + `args`)
- **`sse`**: חיבור לשרת HTTP+SSE (`url`)

עקוף את מיקום קובץ הקונפיגורציה עם `MCP_CONFIG=/path/to/config.json`.

---

## חומרה

familiar-ai פועלת עם כל חומרה שיש לך — או אפילו בלי חומרה.

| חלק | מה זה עושה | דוגמה | דרוש? |
|------|-------------|---------|-----------|
| מצלמת Wi-Fi PTZ | עיניים + צוואר | Tapo C220 (~$30) | **מומלץ** |
| מצלמת USB | עיניים (קבועות) | כל מצלמת UVC | **מומלץ** |
| שואב רובוטי | רגליים | כל מודל תואם Tuya | לא |
| PC / Raspberry Pi | מוח | כל דבר שרץ על Python | **כן** |

> **מצלמה היא מומלצת מאוד.** בלי אחת, familiar-ai יכולה עדיין לדבר — אבל היא לא יכולה לראות את העולם, שזה די בעצם כל הרעיון.

### התקנה מינימלית (בלי חומרה)

רק רוצה לנסות? אתה צריך רק מפתח API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

הרץ `./run.sh` (macOS/Linux/WSL2) או `run.bat` (Windows) והתחל לשוחח. הוסף חומרה בהמשך הדרך.

### מצלמת Wi-Fi PTZ (Tapo C220)

1. באפליקציית Tapo: **הגדרות → מתקדם → חשבון מצלמה** — צור חשבון מקומי (לא חשבון TP-Link)
2. מצא את כתובת ה-IP של המצלמה ברשימת המכשירים של הנתב שלך
3. הגדר ב- `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### קול (ElevenLabs)

1. קבל מפתח API ב-[elevenlabs.io](https://elevenlabs.io/)
2. הגדר ב-.env:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # אופציונלי, משתמש בקול ברירת המחדל אם לא צוין
   ```

ישנם שני יעדי ניגון, שנשלטים על ידי `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # רמקול PC (ברירת מחדל)
TTS_OUTPUT=remote   # רמקול מצלמה בלבד
TTS_OUTPUT=both     # רמקול מצלמה + רמקול PC בו זמנית
```

#### א) רמקול מצלמה (באמצעות go2rtc)

הגדיר `TTS_OUTPUT=remote` (או `both`). דורש [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. הורד את הקובץ מה[דף הגרסאות](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. מקם ושנה את שמו:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # יש צורך ב-chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. צור `go2rtc.yaml` באותה תיקייה:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   השתמש בפרטי ההזדהות של החשבון המקומי במצלמה (ולא בחשבון הענן של TP-Link שלך).

4. familiar-ai מתחילה את go2rtc באופן אוטומטי בעת ההפעלה. אם המצלמה שלך תומכת באודיו דו-כיווני (ערוץ אחורי), הקול מנוגן מהרמקול של המצלמה.

#### ב) רמקול PC מקומי

הברירת המחדל (`TTS_OUTPUT=local`). מנסה נגנים בסדר: **paplay** → **mpv** → **ffplay**. גם משמש כשחזור כאשר `TTS_OUTPUT=remote` ו-go2rtc אינו זמין.

| מערכת הפעלה | התקנה |
|--------------|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (או `paplay` דרך `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — הגדר `PULSE_SERVER=unix:/mnt/wslg/PulseServer` ב-.env |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — הורד והוסף ל-PATH, **או** `winget install ffmpeg` |

> אם אין נגן אודיו זמין, הדיבור עדיין נוצר — פשוט לא ינוגן.

### קלט קול (Realtime STT)

הגדר `REALTIME_STT=true` ב-.env עבור קלט קול תמידי ללא ידיים:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # אותו מפתח כמו TTS
```

familiar-ai משפיעה על אודיו מהמיקרופון ל-ElevenLabs Scribe v2 ומתחייבת אוטומטית על תמלילים כאשר אתה מפסיק לדבר. אין צורך בלחיצת כפתור. מקביל למצב לחיצה לדבר (Ctrl+T).

---

## TUI

familiar-ai כוללת ממשק טרמינל שנבנה עם [Textual](https://textual.textualize.io/):

- היסטוריית שיחות ניתנת לגולל עם טקסט זרם חי
- השלמת טאבים עבור `/quit`, `/clear`
- להפסיק את הסוכן בזמן שהוא חושב על ידי הקלדה בזמן
- **יומן שיחה** שנשמר אוטומטית ל- `~/.cache/familiar-ai/chat.log`

כדי לעקוב אחרי היומן בטרמינל אחר (מועיל להעתקה והדבקה):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## אישיות (ME.md)

האישיות של המוכר שלך חיה ב- `ME.md`. קובץ זה נמצא באי-זיהוי גיט — הוא רק שלך.

ראה [`persona-template/en.md`](./persona-template/en.md) לדוגמה, או [`persona-template/ja.md`](./persona-template/ja.md) עבור גרסה יפנית.

---

## שאלות נפוצות

**ש: האם זה עובד בלי GPU?**
כן. מודל ההטמעות (multilingual-e5-small) רץ מצוין על CPU. GPU הופך את זה למהיר יותר אבל אינו דרוש.

**ש: האם אני יכול להשתמש במצלמה אחרת חוץ מ-Tapo?**
כל מצלמה שתומכת ב-ONVIF + RTSP אמורה לעבוד. Tapo C220 היא המצלמה שבדקנו.

**ש: האם הנתונים שלי נשלחים לשום מקום?**
תמונות וטקסט נשלחים ל-LLM API הנבחר על ידך לעיבוד. זיכרונות נשמרים מקומית ב- `~/.familiar_ai/`.

**ש: מדוע הסוכן כותב `（...）` במקום לדבר?**
וודא ש-`ELEVENLABS_API_KEY` מוגדר. בלעדיו, הקול מושבת והסוכן חוזר לטקסט.

## רקע טכני

סקרן לגבי איך זה עובד? ראה [docs/technical.md](./docs/technical.md) עבור מחקר והחלטות עיצוב מאחורי familiar-ai — ReAct, SayCan, Reflexion, Voyager, מערכת הרצון, ועוד.

---

## תרומות

familiar-ai הוא ניסוי פתוח. אם משהו מזה מדבר אליך — טכני או פילוסופי — תרומות מתקבלות בברכה.

**מקומות טובים להתחיל:**

| אזור | מה נדרש |
|------|---------------|
| חומרה חדשה | תמיכה עבור יותר מצלמות (RTSP, IP Webcam), מיקרופונים, מפעילים |
| כלים חדשים | חיפוש באינטרנט, אוטומציה ביתית, לוח שנה, כל דבר דרך MCP |
| רקעים חדשים | כל LLM או מודל מקומי שמתאימים לממשק `stream_turn` |
| תבניות אישיות | תבניות ME.md לשפות ואישויות שונות |
| מחקר | מודלים טובים יותר של רצון, שחזור זיכרון, טיזינג לתיאוריה של תודעה |
| תיעוד | מדריכים, הסברים, תרגומים |

ראה [CONTRIBUTING.md](./CONTRIBUTING.md) עבור קביעת הגדרת הפיתוח, סגנון הקוד, והנחיות PR.

אם אינך בטוח איפה להתחיל, [פתח נושא](https://github.com/lifemate-ai/familiar-ai/issues) — נשמח להכוון אותך בכיוון הנכון.

---

## רישיון

[MIT](./LICENSE)
