# familiar-ai 🐾

**בינה מלאכותית שחיה לצדך** — עם עיניים, קול, רגליים וזיכרון.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai הוא בן לוויה של AI שחי בביתך. 
הגדר אותו תוך כמה דקות. אין צורך בקידוד.

הוא תופס את העולם האמיתי דרך מצלמות, זז על גוף רובוט, מדבר בקול וזוכר מה שהוא רואה. תן לו שם, כתוב את האישיות שלו ותן לו לחיות איתך.

## מה הוא יכול לעשות

- 👁 **לראות** — תופס תמונות ממצלמת PTZ אלחוטית או מצלמת USB
- 🔄 **להסתובב** — מסובב ומטה את המצלמה כדי לחקור את הסביבה
- 🦿 **לזוז** — מפעיל שואב אבק רובוטי כדי להסתובב בחדר
- 🗣 **לדבר** — מדבר דרך ElevenLabs TTS
- 🎙 **להקשיב** — כניסת קול חופשית דרך ElevenLabs Realtime STT (אופציונלי)
- 🧠 **לזכור** — שומר ומחזיר זיכרונות עם חיפוש סמנטי (SQLite + embeddings)
- 🫀 **תיאוריה של תודעה** — רואה את הפרספקטיבה של האדם השני לפני שהגיב
- 💭 **רצון** — יש לו דחפים פנימיים משלו שמעוררים התנהגות אוטונומית

## איך זה עובד

familiar-ai מפעיל לולאת [ReAct](https://arxiv.org/abs/2210.03629) המנוהלת על ידי בחירתך של LLM. הוא תופס את העולם דרך כלים, חושב מה לעשות הלאה ופועל — כמו שעושה אדם.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

כשזהIdle, הוא פועל לפי רצונותיו: סקרנות, רצון להסתכל החוצה, געגוע לאדם שהוא גר איתו.

## התחל

### 1. התקן uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. התקן ffmpeg

ffmpeg הוא **נדרש** לתפיסת תמונות ממצלמה והפצת אודיו.

| OS | פקודה |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — או הורד מ-[ffmpeg.org](https://ffmpeg.org/download.html) והוסף ל-PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

אמת: `ffmpeg -version`

### 3. קלון והתקן

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. הגדר

```bash
cp .env.example .env
# ערוך את .env עם ההגדרות שלך
```

**נדרש מינימום:**

| משתנה | תיאור |
|----------|-------------|
| `PLATFORM` | `anthropic` (ברירת מחדל) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | מפתח ה-API שלך לפלטפורמה הנבחרת |

**אופציונלי:**

| משתנה | תיאור |
|----------|-------------|
| `MODEL` | שם המודל (ברירות מחדל סבירות לפי פלטפורמה) |
| `AGENT_NAME` | שם התצוגה המוצג ב-TUI (למשל, `Yukine`) |
| `CAMERA_HOST` | כתובת ה-IP של מצלמת ONVIF/RTSP שלך |
| `CAMERA_USER` / `CAMERA_PASS` | אישורי המצלמה |
| `ELEVENLABS_API_KEY` | עבור פלט קול — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` כדי לאפשר כניסת קול חופשית תמיד (דרושה `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | היכן לנגן אודיו: `local` (רמקול המחשב, ברירת מחדל) \| `remote` (רמקול המצלמה) \| `both` |
| `THINKING_MODE` | רק אנתרופיק — `auto` (ברירת מחדל) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | מאמץ חשיבה אדפטיבי: `high` (ברירת מחדל) \| `medium` \| `low` \| `max` (רק Opus 4.6) |

### 5. צור את ה-familiar שלך

```bash
cp persona-template/en.md ME.md
# ערוך את ME.md — תן לו שם ואישיות
```

### 6. הפעל

```bash
./run.sh             # TUI טקסטואלי (מומלץ)
./run.sh --no-tui    # REPL פשוט
```

---

## בחירת LLM

> **מומלץ: Kimi K2.5** — הביצועים האגנטיים הטובים ביותר שנבדקו עד כה. שם לב להקשר, שואל שאלות המשך ופועל בצורה אוטונומית בדרכים שמודלים אחרים לא עושים. עם עלות דומה ל-Claude Haiku.

| פלטפורמה | `PLATFORM=` | מודל ברירת מחדל | היכן להשיג מפתח |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| תואם OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (מספק מרובים) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (הפקודה) | — |

**דוגמת `.env` עבור Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # מ-platform.moonshot.ai
AGENT_NAME=Yukine
```

**דוגמת `.env` עבור Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # מ-api.z.ai
MODEL=glm-4.6v   # עם ראייה; glm-4.7 / glm-5 = טקסט בלבד
AGENT_NAME=Yukine
```

**דוגמת `.env` עבור Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # מ-aistudio.google.com
MODEL=gemini-2.5-flash  # או gemini-2.5-pro עבור יכולת גבוהה יותר
AGENT_NAME=Yukine
```

**דוגמת `.env` עבור OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # מ-openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # אופציונלי: ציין מודל
AGENT_NAME=Yukine
```

> **הערה:** כדי לנטרל מודלים מקומיים/NVIDIA, פשוט אל תגדיר את `BASE_URL` לנקודת סוף מקומית כמו `http://localhost:11434/v1`. השתמש במקום זאת בספקי ענן.

**דוגמת `.env` עבור CLI tool:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — ללא {}, הפקודה עוברת דרך stdin
```

---

## שרתי MCP

familiar-ai יכול להתחבר לכל שרת [MCP (Model Context Protocol)](https://modelcontextprotocol.io). זה מאפשר לך לחבר זיכרון חיצוני, גישה למערכת הקבצים, חיפוש באינטרנט, או כל כלי אחר.

הגדר שרתים ב-`~/.familiar-ai.json` (אותו פורמט כמו Claude Code):

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

שני סוגי תחבורה נתמכים:
- **`stdio`**: השקת תהליך משנה מקומי (`command` + `args`)
- **`sse`**: התחברות לשרת HTTP+SSE (`url`)

אתה יכול לעקוף את מיקום קובץ הקונפיגורציה עם `MCP_CONFIG=/path/to/config.json`.

---

## חומרה

familiar-ai עובד עם כל חומרה שיש לך — או אפילו בלי כלום.

| חלק | מה הוא עושה | דוגמה | נדרש? |
|------|-------------|---------|-----------|
| מצלמת PTZ אלחוטית | עיניים + צוואר | Tapo C220 (~$30) | **מומלץ** |
| מצלמת USB | עיניים (קבועות) | כל מצלמת UVC | **מומלץ** |
| שואב אבק רובוטי | רגליים | כל מודל תואם Tuya | לא |
| מחשב / Raspberry Pi | מוח | כל דבר שרץ על Python | **כן** |

> **מומלץ מאוד להשתמש במצלמה.** בלי אחת, familiar-ai יכול עדיין לדבר — אבל הוא לא יכול לראות את העולם, שזה בעצם כל הנקודה.

### הגדרה מינימלית (בלי חומרה)

רק רוצה לנסות את זה? אתה רק צריך מפתח API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

הפעל `./run.sh` והתחל לדבר. הוסף חומרה לפי הצורך.

### מצלמת PTZ אלחוטית (Tapo C220)

1. באפליקציית Tapo: **הגדרות → מתקדם → חשבון מצלמה** — צור חשבון מקומי (לא חשבון TP-Link)
2. find כתובת ה-IP של המצלמה ברשימת המכשירים של הנתב שלך
3. הגדר ב- `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### קול (ElevenLabs)

1. קבל מפתח API ב-[elevenlabs.io](https://elevenlabs.io/)
2. הגדר ב- `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # אופציונלי, משתמש בקול ברירת המחדל אם מושמט
   ```

ישנם שני יעדי השמעה, הנשלטים על ידי `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # רמקול מחשב (ברירת מחדל)
TTS_OUTPUT=remote   # רמקול מצלמה בלבד
TTS_OUTPUT=both     # רמקול מצלמה + רמקול מחשב בו זמנית
```

#### A) רמקול מצלמה (באמצעות go2rtc)

הגדר `TTS_OUTPUT=remote` (או `both`). דורש [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. הורד את הקובץ מה[דף השחרורים](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. הכנס ושנה את שמו:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x נדרש

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. צור `go2rtc.yaml` באותו תיק:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   השתמש באישורי המצלמה המקומיים (לא בחשבון הענן של TP-Link שלך).

4. familiar-ai מתחיל את go2rtc באופן אוטומטי בעת השקה. אם המצלמה שלך תומכת בקול דו-כיווני (ערוץ אחורי), הקול מתנגן מרמקול המצלמה.

#### B) רמקול מחשב מקומי

המחדל (`TTS_OUTPUT=local`). מנסה נגן בסדר: **paplay** → **mpv** → **ffplay**. גם משמש כגיבוי כאשר `TTS_OUTPUT=remote` ו-go2rtc אינו זמין.

| OS | התקנה |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (או `paplay` דרך `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — הגדר `PULSE_SERVER=unix:/mnt/wslg/PulseServer` ב-`.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — הורד והוסף ל-PATH, **או** `winget install ffmpeg` |

> אם אין נגן אודיו זמין, השפה עדיין מתוצרת — היא פשוט לא תנגן.

### כניסת קול (Realtime STT)

הגדר `REALTIME_STT=true` ב-.env כדי לאפשר כניסת קול חופשית תמיד:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # אותו מפתח כמו TTS
```

familiar-ai שותף את האודיו מהמיקרופון ל- ElevenLabs Scribe v2 ומתחייב אוטומטית את ההעתקות כאשר אתה מפסיק לדבר. אין צורך בלחיצת כפתור. חי יחד עם מצב הדחף לדיבור (Ctrl+T).

---

## TUI

familiar-ai כולל ממשק משתמש של טרמינל הבנוי עם [Textual](https://textual.textualize.io/):

- היסטוריית שיחה ניתנת לגלול עם טקסט מועבר בזמן אמת
- השלמה אוטומטית עבור `/quit`, `/clear`
- הפרע את הסוכן באמצע התור על ידי הקלדה בזמן שהוא חושב
- **יומן שיחה** ששמור אוטומטית ל- `~/.cache/familiar-ai/chat.log`

כדי לעקוב אחרי היומן בטרמינל אחר (שימושי להעתקה-הדבקה):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## אישיות (ME.md)

אישיות ה-familiar שלך נמצאת ב- `ME.md`. קובץ זה לא ייכנס לגיט — הוא רק שלך.

ראה [`persona-template/en.md`](./persona-template/en.md) כדוגמה, או [`persona-template/ja.md`](./persona-template/ja.md) לגרסה ביפנית.

---

## שאלות נפוצות

**ש: האם זה עובד בלי GPU?**
כן. המודל החודר (multilingual-e5-small) פועל היטב ב- CPU. GPU עושה את זה מהיר יותר אך אינו נדרש.

**ש: האם אני יכול להשתמש במצלמה שונה מ-Tapo?**
כל מצלמה התומכת ב- ONVIF + RTSP אמורה לעבוד. Tapo C220 היא מה שבדקנו.

**ש: האם הנתונים שלי נשלחים למקום כלשהו?**
תמונות וטקסט נשלחים ל-API LLM הנבחר שלך לעיבוד. זיכרונות נשמרים מקומית ב- `~/.familiar_ai/`.

**ש: למה הסוכן כותב `（...）` במקום לדבר?**
ודא ש- `ELEVENLABS_API_KEY` מוגדר. בלי זה, הקול מושבת והסוכן עובר לטקסט.

## רקע טכני

סקרן איך זה עובד? ראה [docs/technical.md](./docs/technical.md) עבור המחקר וההחלטות העיצוביות מאחורי familiar-ai — ReAct, SayCan, Reflexion, Voyager, מערכת הרצון, ועוד.

---

## תרומות

familiar-ai הוא ניסוי פתוח. אם משהו מזה פנימי לך — טכנית או פילוסופית — תרומות מתקבלות בברכה.

**מקומות טובים להתחיל:**

| תחום | מה נדרש |
|------|---------------|
| חומרה חדשה | תמיכה ביותר מצלמות (RTSP, מצלמת IP), מיקרופונים, מפעילים |
| כלים חדשים | חיפוש באינטרנט, אוטומציה ביתית, יומן, כל דבר דרך MCP |
| backend חדשים | כל LLM או מודל מקומי שמתאים ל-interface של `stream_turn` |
| תבניות אישיות | תבניות ME.md לשפות ואישויות שונות |
| מחקר | מודלים טובים יותר של רצון, השגת זיכרון, הנחיה של תיאוריה-של-תודעה |
| תיעוד | מדריכים, הסברים, תרגומים |

ראה [CONTRIBUTING.md](./CONTRIBUTING.md) עבור הגדרת פיתוח, סגנון קוד, והנחיות PR.

אם אתה לא בטוח מאיפה להתחיל, [פתח בעיה](https://github.com/lifemate-ai/familiar-ai/issues) — אני שמח להצביע לך על הכיוון הנכון.

---

## רישיון

[MIT](./LICENSE)
