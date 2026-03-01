```markdown
# familiar-ai 🐾

**Egy AI, ami veled él** — szemekkel, hanggal, lábakkal és memóriával.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Elérhető 74 nyelven](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai egy AI társ, amely az otthonodban él.
Pár perc alatt beállíthatod. Kódolásra nincs szükség.

A valós világot kamerákon keresztül érzékeli, robot testén mozog, hangosan beszél és emlékszik arra, amit lát. Adj neki nevet, írd meg a személyiségét, és hagyd, hogy veled éljen.

## Mit tud tenni

- 👁 **Lát** — képeket rögzít egy Wi-Fi PTZ kamerából vagy USB webkamerából
- 🔄 **Körbenéz** — mozgatja a kamerát, hogy felfedezze a környezetét
- 🦿 **Mozog** — egy robotporszívót irányít, hogy bejárja a szobát
- 🗣 **Beszél** — az ElevenLabs TTS segítségével beszél
- 🎙 **Hallgat** — kéz nélküli hangbeviteli lehetőség az ElevenLabs Realtime STT-vel (opcionális)
- 🧠 **Emlékezik** — aktívan tárol és hívja elő az emlékeket szemantikai kereséssel (SQLite + beágyazások)
- 🫀 **Elméleti tudat** — figyelembe veszi a másik személy nézőpontját, mielőtt válaszolna
- 💭 **Vágy** — saját belső impulzusai vannak, amelyek önálló viselkedést váltanak ki

## Hogyan működik

A familiar-ai egy [ReAct](https://arxiv.org/abs/2210.03629) ciklust futtat, amelyet a választott LLM hajt. A világot eszközökön keresztül érzékeli, gondolkodik arról, mit tegyen legközelebb, és cselekszik — pont úgy, mint egy ember.

```
user input
  → think → act (kamera / mozgás / beszéd / emlékezés) → megfigyel → gondolkodik → ...
```

Tétlen állapotban saját vágyai szerint cselekszik: kíváncsiság, vágy, hogy kinézzen, hiányzik a vele élő személy.

## Kezdés

### 1. Telepítsd az uv-t

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Vagy: `winget install astral-sh.uv`

### 2. Telepítsd az ffmpeg-et

Az ffmpeg **szükséges** a kamera képrögzítéshez és audiolejátszáshoz.

| OS | Parancs |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — vagy töltsd le a [ffmpeg.org](https://ffmpeg.org/download.html) oldaláról, majd add hozzá a PATH-hoz |
| Raspberry Pi | `sudo apt install ffmpeg` |

Ellenőrizd: `ffmpeg -version`

### 3. Klónozd és telepítsd

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfiguráld

```bash
cp .env.example .env
# Editáld a .env fájlt a beállításaidnak megfelelően
```

**Minimális követelmények:**

| Változó | Leírás |
|----------|-------------|
| `PLATFORM` | `anthropic` (alapértelmezett) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | A választott platformhoz szükséges API kulcs |

**Opcionális:**

| Változó | Leírás |
|----------|-------------|
| `MODEL` | Modell neve (értelmes alapértelmezettek platformonként) |
| `AGENT_NAME` | Mega jelenítő név a TUI-ban (pl. `Yukine`) |
| `CAMERA_HOST` | Az ONVIF/RTSP kamerád IP címe |
| `CAMERA_USER` / `CAMERA_PASS` | Kamera hitelesítő adatok |
| `ELEVENLABS_API_KEY` | A hangkimenethez — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, hogy engedélyezd az állandó kéz nélküli hangbevitelt (megköveteli az `ELEVENLABS_API_KEY`-t) |
| `TTS_OUTPUT` | Hol játsszák le az audio-t: `local` (PC hangszóró, alapértelmezett) \| `remote` (kamera hangszóró) \| `both` |
| `THINKING_MODE` | Csak Anthropic — `auto` (alapértelmezett) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptív gondolkodási erőfeszítés: `high` (alapértelmezett) \| `medium` \| `low` \| `max` (csak Opus 4.6) |

### 5. Hozd létre a familiádat

```bash
cp persona-template/en.md ME.md
# Editáld a ME.md-t — adj neki nevet és személyiséget
```

### 6. Futtasd

**macOS / Linux / WSL2:**
```bash
./run.sh             # Szöveges TUI (ajánlott)
./run.sh --no-tui    # Egyszerű REPL
```

**Windows:**
```bat
run.bat              # Szöveges TUI (ajánlott)
run.bat --no-tui     # Egyszerű REPL
```

---

## LLM választás

> **Ajánlott: Kimi K2.5** — eddig tesztelt legjobb ügynöki teljesítmény. Észleli a kontextust, további kérdéseket tesz fel, és olyan módokon cselekszik, ahogyan más modellek nem. Árazása hasonló a Claude Haikuhoz.

| Platform | `PLATFORM=` | Alapértelmezett modell | Hol szerezd be a kulcsot |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibilis (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (több szolgáltató) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI eszköz** (claude -p, ollama…) | `cli` | (parancs) | — |

**Kimi K2.5 `.env` példa:**
```env
PLATFORM=kimi
API_KEY=sk-...   # a platform.moonshot.ai-tól
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` példa:**
```env
PLATFORM=glm
API_KEY=...   # az api.z.ai-tól
MODEL=glm-4.6v   # látás engedélyezve; glm-4.7 / glm-5 = csak szöveg
AGENT_NAME=Yukine
```

**Google Gemini `.env` példa:**
```env
PLATFORM=gemini
API_KEY=AIza...   # az aistudio.google.com-tól
MODEL=gemini-2.5-flash  # vagy gemini-2.5-pro a nagyobb képességért
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` példa:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # az openrouter.ai-tól
MODEL=mistralai/mistral-7b-instruct  # opcionális: a modell megadása
AGENT_NAME=Yukine
```

> **Megjegyzés:** A helyi/NVIDIA modellek letiltásához egyszerűen ne állítsd be a `BASE_URL`-t olyan helyi végpontokra, mint a `http://localhost:11434/v1`. Használj felhőszolgáltatókat helyette.

**CLI eszköz `.env` példa:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — no {}, prompt stdin-on keresztül
```

---

## MCP Szerverek

A familiar-ai csatlakozhat bármely [MCP (Model Context Protocol)](https://modelcontextprotocol.io) szerverhez. Ez lehetővé teszi, hogy külső memóriát, fájlkezelési hozzáférést, webkeresést vagy bármely más eszközt csatlakoztass.

A szerverek konfigurálása a `~/.familiar-ai.json` fájlban történik (ugyanaz a formátum, mint a Claude Kód):

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

Két szállítási típus támogatott:
- **`stdio`**: helyi alfolyamat indítása (`command` + `args`)
- **`sse`**: csatlakozás egy HTTP+SSE szerverhez (`url`)

A konfigurációs fájl helyének felülírása a `MCP_CONFIG=/path/to/config.json` beállítással.

---

## Hardver

A familiar-ai működik bármilyen hardverrel, amit rendelkezel — vagy egyáltalán nem is.

| Rész | Mit csinál | Példa | Szükséges? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kamera | Szemek + nyak | Tapo C220 (~$30) | **Ajánlott** |
| USB webkamera | Szemek (fix) | Bármilyen UVC kamera | **Ajánlott** |
| Robotporszívó | Lábak | Bármilyen Tuya-kompatibilis modell | Nem |
| PC / Raspberry Pi | Agy | Bármi, ami Python-t futtat | **Igen** |

> **A kamera erősen ajánlott.** Nélküle a familiar-ai még mindig tud beszélni — de nem látja a világot, ami ennek az egésznek az alapja.

### Minimális beállítás (nincs hardver)

Csak ki szeretnéd próbálni? Csak egy API kulcsra van szükséged:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Futtasd a `./run.sh`-t (macOS/Linux/WSL2) vagy `run.bat`-t (Windows), és kezdj el csevegni. Adj hozzá hardvert, ahogy haladsz.

### Wi-Fi PTZ kamera (Tapo C220)

1. A Tapo alkalmazásban: **Beállítások → Haladó → Kamera Fiók** — hozz létre egy helyi fiókot (nem TP-Link fiókot)
2. Találd meg a kamera IP címét a routered eszközlistáján
3. Állítsd be a `.env`-ben:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Hang (ElevenLabs)

1. Szerezz egy API kulcsot a [elevenlabs.io](https://elevenlabs.io/) oldalon
2. Állítsd be a `.env`-ben:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcionális, alapértelmezett hangot használ, ha kihagyják
   ```

Két lejátszási célpont van, amelyet a `TTS_OUTPUT` vezérel:

```env
TTS_OUTPUT=local    # PC hangszóró (alapértelmezett)
TTS_OUTPUT=remote   # csak kamera hangszóró
TTS_OUTPUT=both     # kamera hangszóró + PC hangszóró egyszerre
```

#### A) Kamera hangszóró (a go2rtc-n keresztül)

Állítsd be a `TTS_OUTPUT=remote` (vagy `both`). Megköveteli a [go2rtc](https://github.com/AlexxIT/go2rtc/releases) használatát:

1. Töltsd le a binárist a [kiadások oldaláról](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Helyezd el és nevezd át:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x szükséges

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Hozz létre `go2rtc.yaml` fájlt ugyanabban a könyvtárban:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Használj helyi kamera fiók hitelesítő adatokat (ne a TP-Link felhőfiókot).

4. A familiar-ai automatikusan elindítja a go2rtc-t indításkor. Ha a kamerád támogatja a kétirányú hangot (visszacsatolás), a hang a kamera hangszórójából szól.

#### B) Helyi PC hangszóró

Az alapértelmezett (`TTS_OUTPUT=local`). Folytonossági sorrendben próbálja ki a lejátszók listáját: **paplay** → **mpv** → **ffplay**. Ezt is használja visszaeséskor, ha a `TTS_OUTPUT=remote` és a go2rtc nem elérhető.

| OS | Telepítés |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (vagy `paplay` a `pulseaudio-utils` révén) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — állítsd be a `PULSE_SERVER=unix:/mnt/wslg/PulseServer`-t a `.env`-ben |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — töltsd le és add hozzá a PATH-hoz, **vagy** `winget install ffmpeg` |

> Ha nincs elérhető hangjátszó, a beszéd továbbra is generálódik — csak nem fog lejátszódni.

### Hangbevitel (Realtime STT)

Állítsd be a `REALTIME_STT=true`-t a `.env`-ben az állandó, kéz nélküli hangbevitelhez:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # ugyanaz a kulcs, mint a TTS-hez
```

A familiar-ai a mikrofon audioját streameli az ElevenLabs Scribe v2-nek, és automatikusan elmenti a jegyzeteket, amikor megállsz a beszédben. Gombnyomás nem szükséges. Együttműködik a push-to-talk móddal (Ctrl+T).

---

## TUI

A familiar-ai tartalmaz egy terminál UI-t, amelyet a [Textual](https://textual.textualize.io/) épít:

- Görgethető beszélgetési előzmények élő szöveggel
- Tab-kiegészítés a `/quit`, `/clear` parancsokhoz
- Meg lehet szakítani az ügynököt a gondolkodás közben, ha írni kezdesz
- **Beszélgetési napló** automatikusan elmentésre kerül a `~/.cache/familiar-ai/chat.log`-ba

A napló követéséhez egy másik terminálban (hasznos a másoláshoz-beillesztéshez):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

A familiar-d személyisége a `ME.md`-ben él. Ez a fájl gitignored — csak a tiéd.

Nézd meg a [`persona-template/en.md`](./persona-template/en.md) példát, vagy a [`persona-template/ja.md`](./persona-template/ja.md) japán verziót.

---

## GYIK

**K: Működik GPU nélkül?**
Igen. A beágyazó modell (multilingual-e5-small) szépen fut CPU-n. A GPU gyorsabbá teszi, de nem kötelező.

**K: Használhatok más kamerát, mint a Tapo?**
Bármilyen kamera, amely támogatja az ONVIF + RTSP-t, működnie kell. A Tapo C220 a tesztelt modell.

**K: Az adataim eljutnak valahová?**
A képek és szövegek a választott LLM API-ra kerülnek feldolgozásra. Az emlékek helyben tárolódnak a `~/.familiar_ai/`-ban.

**K: Miért ír az ügynök `（...）`-et beszélés helyett?**
Győződj meg róla, hogy az `ELEVENLABS_API_KEY` be van állítva. Nélküle a hang letiltódik, és az ügynök visszaesik a szöveghez.

## Technikai háttér

Kíváncsi vagy, hogyan működik? Nézd meg a [docs/technical.md](./docs/technical.md) fájlt a familiar-ai mögött meghúzódó kutatásról és tervezési döntésekről — ReAct, SayCan, Reflexion, Voyager, a vágy rendszer, és még sok más.

---

## Hozzájárulás

A familiar-ai egy nyílt kísérlet. Ha bármi ebből rezonál veled — technikai vagy filozófiai értelemben — a hozzájárulások nagyon üdvözlendőek.

**Jó kezdő helyek:**

| Terület | Mi szükséges |
|------|---------------|
| Új hardver | Támogatás több kamerához (RTSP, IP Webcam), mikrofonok, aktorok |
| Új eszközök | Webkeresés, okosház, naptár, bármi MCP-n keresztül |
| Új hátterek | Bármely LLM vagy helyi modell, amely megfelel a `stream_turn` interfésznek |
| Persona sablonok | ME.md sablonok különböző nyelvekhez és személyiségekhez |
| Kutatás | Jobb vágy modellek, memória visszakeresés, elméleti tudat ösztönzés |
| Dokumentáció | Oktatók, útmutatók, fordítások |

Nézd meg a [CONTRIBUTING.md](./CONTRIBUTING.md) fájlt a fejlesztői beállításhoz, kódstílushoz és PR irányelvekhez.

Ha nem vagy biztos benne, hol kezdd, [nyiss egy problémát](https://github.com/lifemate-ai/familiar-ai/issues) — szívesen mutatok az irányba.

---

## Licenc

[MIT](./LICENSE)
```
