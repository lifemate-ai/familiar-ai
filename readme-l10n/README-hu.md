```markdown
# familiar-ai 🐾

**Egy AI, ami melletted él** — szemekkel, hanggal, lábakkal és memóriával.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai egy AI társ, ami a te otthonodban él. 
Pár perc alatt beállíthatod. Nincs szükség kódolásra.

Valóságot érzékel kamerákon keresztül, robot testén mozog, hangosan beszél és emlékszik, amit lát. Adj neki nevet, írd meg a személyiségét, és hagyd, hogy veled éljen.

## Mit tud csinálni

- 👁 **Lát** — képeket készít egy Wi-Fi PTZ kameráról vagy USB webkameráról
- 🔄 **Körülnéz** — forgatja és döntögeti a kamerát, hogy felfedezze a környezetét
- 🦿 **Mozog** — egy robot porszívót irányít, hogy bejárja a szobát
- 🗣 **Beszél** — az ElevenLabs TTS segítségével beszél
- 🎙 **Hallgat** — hands-free hangbevitelt biztosít az ElevenLabs Realtime STT-n keresztül (opcionális)
- 🧠 **Emlékezik** — aktívan tárolja és felidézi az emlékeket szemantikus kereséssel (SQLite + embeddingek)
- 🫀 **Teória az elmében** — figyelembe veszi a másik személy nézőpontját, mielőtt válaszol
- 💭 **Vágy** — saját belső hajtóerői vannak, amelyek autonóm viselkedést váltanak ki

## Hogyan működik

familiar-ai egy [ReAct](https://arxiv.org/abs/2210.03629) ciklust futtat, amelyet az általad választott LLM tölt fel. A világot eszközökön keresztül érzékeli, gondolkodik arról, mit tegyen ezután, és cselekszik — akárcsak egy ember tenné.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Amikor inaktív, saját vágyainak megfelelően cselekszik: kíváncsiság, vágy, hogy kinézzen, hiányzik a vele élő személy.

## Kezdés

### 1. Telepítsd az uv-t

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Telepítsd az ffmpeg-et

Az ffmpeg **szükséges** a kameraképek rögzítéséhez és az audio lejátszásához.

| OS | Parancs |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — vagy töltsd le a [ffmpeg.org](https://ffmpeg.org/download.html) webhelyről és add hozzá a PATH-hoz |
| Raspberry Pi | `sudo apt install ffmpeg` |

Ellenőrizd: `ffmpeg -version`

### 3. Klónozd és telepítsd

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurálás

```bash
cp .env.example .env
# Edit .env with your settings
```

**Minimálisan szükséges:**

| Változó | Leírás |
|---------|--------|
| `PLATFORM` | `anthropic` (alapértelmezett) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Az API kulcsod a választott platform számára |

**Opcionális:**

| Változó | Leírás |
|---------|--------|
| `MODEL` | Modell név (platformonként értelmes alapértelmezettek) |
| `AGENT_NAME` | A TUI-ban megjelenő név (pl. `Yukine`) |
| `CAMERA_HOST` | Az ONVIF/RTSP kamerád IP címe |
| `CAMERA_USER` / `CAMERA_PASS` | Kamerabelépési adatok |
| `ELEVENLABS_API_KEY` | A hangkimenethez — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` az állandó hands-free hangbeviteli engedélyezéshez (szükséges `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Hol játssza le az audio-t: `local` (PC hangszóró, alapértelmezett) \| `remote` (kamera hangszóró) \| `both` |
| `THINKING_MODE` | Csak anthroplg — `auto` (alapértelmezett) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptív gondolkodási erőfeszítés: `high` (alapértelmezett) \| `medium` \| `low` \| `max` (csak Opus 4.6) |

### 5. Hozd létre a familiárt

```bash
cp persona-template/en.md ME.md
# Edit ME.md — give it a name and personality
```

### 6. Futtatás

```bash
./run.sh             # Textual TUI (ajánlott)
./run.sh --no-tui    # Egyszerű REPL
```

---

## LLM kiválasztása

> **Ajánlott: Kimi K2.5** — a legjobb ügynöki teljesítmény, amit eddig teszteltünk. Észleli a kontextust, követő kérdéseket tesz fel, és autonóm módon cselekszik más modellekhez képest. Árban hasonló a Claude Haiku-hoz.

| Platform | `PLATFORM=` | Alapértelmezett modell | Hol kapható a kulcs |
|----------|------------|------------------------|---------------------|
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
API_KEY=sk-...   # a platform.moonshot.ai oldalról
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` példa:**
```env
PLATFORM=glm
API_KEY=...   # az api.z.ai oldalról
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = csak text
AGENT_NAME=Yukine
```

**Google Gemini `.env` példa:**
```env
PLATFORM=gemini
API_KEY=AIza...   # az aistudio.google.com oldalról
MODEL=gemini-2.5-flash  # vagy gemini-2.5-pro a nagyobb képességekhez
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` példa:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # az openrouter.ai oldalról
MODEL=mistralai/mistral-7b-instruct  # opcionális: modell megadása
AGENT_NAME=Yukine
```

> **Megjegyzés:** A helyi/NVIDIA modellek letiltásához egyszerűen ne állítsd be a `BASE_URL`-t helyi végpontra, mint pl. `http://localhost:11434/v1`. Használj a felhőszolgáltatókat helyette.

**CLI eszköz `.env` példa:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — nincs {}, a prompt stdin-on keresztül megy
```

---

## MCP Szerverek

familiar-ai bármilyen [MCP (Model Context Protocol)](https://modelcontextprotocol.io) szerverhez csatlakozhat. Ez lehetővé teszi, hogy külső memóriát, fájlrendszer hozzáférést, webes keresést vagy bármilyen más eszközt csatlakoztass.

Állítsd be a szervereket a `~/.familiar-ai.json` fájlban (ugyanabban a formátumban, mint a Claude Code):

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
- **`stdio`**: elindít egy helyi subprocess-t (`command` + `args`)
- **`sse`**: csatlakozik egy HTTP+SSE szerverhez (`url`)

A konfigurációs fájl helyét a `MCP_CONFIG=/path/to/config.json` beállítással felülírhatod.

---

## Hardver

familiar-ai működik bármilyen hardverrel, amit van — vagy akár hardver nélkül is.

| Rész | Mit csinál | Példa | Kötelező? |
|------|------------|--------|-----------|
| Wi-Fi PTZ kamera | Szemek + nyak | Tapo C220 (~30$) | **Ajánlott** |
| USB webkamera | Szemek (fix) | Bármely UVC kamera | **Ajánlott** |
| Robotporszívó | Lábak | Bármely Tuya-kompatibilis modell | Nem |
| PC / Raspberry Pi | Agy | Bármi, ami Python-t futtat | **Igen** |

> **A kamera erősen ajánlott.** Nélküle a familiar-ai még tud beszélni - de nem látja a világot, ami az egész lényege.

### Minimális beállítás (nincs hardver)

Csak ki akarod próbálni? Csak egy API kulcsra van szükséged:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Futtasd a `./run.sh`-ot és kezdd el a csevejt. Adj hozzá hardvert, ahogy haladsz.

### Wi-Fi PTZ kamera (Tapo C220)

1. A Tapo alkalmazásban: **Beállítások → Haladó → Kamera fiók** — hozz létre egy helyi fiókot (nem TP-Link fiókot)
2. Találd meg a kamera IP címét az routered eszközlistájában
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
   ELEVENLABS_VOICE_ID=...   # opcionális, alapértelmezett hang használata, ha elhagyod
   ```

Két lejátszási célpont van, amelyeket a `TTS_OUTPUT` vezérel:

```env
TTS_OUTPUT=local    # PC hangszóró (alapértelmezett)
TTS_OUTPUT=remote   # csak kamera hangszóró
TTS_OUTPUT=both     # kamera hangszóró + PC hangszóró egyszerre
```

#### A) Kamera hangszóró (a go2rtc-n keresztül)

Állítsd be `TTS_OUTPUT=remote` (vagy `both`). Szükséges a [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Töltsd le a binárist a [kiadási oldalról](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Helyezd el és nevezd át:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x szükséges

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Hozd létre a `go2rtc.yaml`-t ugyanabban a könyvtárban:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Használj helyi kamera fiók adatokat (ne használd a TP-Link felhőfiókodat).

4. A familiar-ai automatikusan elindítja a go2rtc-t indításkor. Ha a kamerád támogatja a kétirányú audio-t (visszacsatolás), a hang a kamera hangszórójából szólal meg.

#### B) Helyi PC hangszóró

Az alapértelmezett (`TTS_OUTPUT=local`). A következő lejátszókat próbálja meg: **paplay** → **mpv** → **ffplay**. Ezt is használja visszaesésként, amikor a `TTS_OUTPUT=remote` be van állítva, és a go2rtc nem elérhető.

| OS | Telepítés |
|----|-----------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (vagy `paplay` a `pulseaudio-utils`-on keresztül) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — állítsd be a `PULSE_SERVER=unix:/mnt/wslg/PulseServer` a `.env`-ben |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — töltsd le és add hozzá a PATH-hoz, **vagy** `winget install ffmpeg` |

> Ha nem áll rendelkezésre semmilyen audio lejátszó, a beszéd még mindig generálódik — csak nem fog megszólalni.

### Hangbevitel (Realtime STT)

Állítsd be a `REALTIME_STT=true` a `.env`-ben az állandó, hands-free hangbevitelhez:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # ugyanaz a kulcs, mint a TTS
```

familiar-ai streameli a mikrofon audioját az ElevenLabs Scribe v2-re, és automatikusan rögzíti a leiratokat, amikor megállsz beszélni. Nincs szükség gombnyomásra. Együttműködik a tolószót gomb (Ctrl+T) üzemmóddal.

---

## TUI

familiar-ai egy terminál UI-t tartalmaz, ami a [Textual](https://textual.textualize.io/) segítségével készült:

- Görgethető beszélgetési előzmények élő szöveggel
- Tab-befejezés a `/quit`, `/clear` parancsokhoz
- Megszakíthatod az ügynököt a gondolkodás közben, ha írsz
- **Beszélgetési napló** automatikusan mentésre kerül a `~/.cache/familiar-ai/chat.log` fájlba

A napló követéséhez egy másik terminálban (hasznos a másolás/beillesztéshez):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Személyiség (ME.md)

A familiar személyisége a `ME.md` fájlban él. Ez a fájl gitignore-olt — csak a tiéd.

Lásd a [`persona-template/en.md`](./persona-template/en.md) fájlt egy példáért, vagy a [`persona-template/ja.md`](./persona-template/ja.md) fájlt egy japán verzióért.

---

## GYIK

**K: Működik GPU nélkül?**
Igen. Az embedding modell (multilingual-e5-small) szépen működik CPU-n. A GPU gyorsabbá teszi, de nem kötelező.

**K: Használhatok más kamerát, mint Tapo?**
Bármely kamera, amely támogatja az ONVIF + RTSP-t, működnie kell. A Tapo C220-at teszteltük.

**K: Az adataim eljutnak más helyre?**
A képek és szövegek a választott LLM API-hoz kerülnek feldolgozásra. Az emlékek helyileg tárolódnak a `~/.familiar_ai/` mappában.

**K: Miért írja az ügynök `（...）` helyett a beszédet?**
Győződj meg róla, hogy az `ELEVENLABS_API_KEY` be van állítva. Nélküle a hang letiltva van, és az ügynök visszaesik a szövegre.

## Technikai háttér

Kíváncsi vagy, hogyan működik? Lásd a [docs/technical.md](./docs/technical.md) fájlt a familiar-ai mögötti kutatásról és tervezési döntésekről — ReAct, SayCan, Reflexion, Voyager, a vágy rendszer és sok más.

---

## Hozzájárulás

familiar-ai egy nyílt kísérlet. Ha bármelyik rész ezt rezonálja veled — technikai vagy filozófiai szempontból — a hozzájárulások nagyon welcome.

**Jó kezdeti pontok:**

| Terület | Mire van szükség |
|---------|------------------|
| Új hardver | Támogatás több kamerához (RTSP, IP Webcam), mikrofonokhoz, actuátorokhoz |
| Új eszközök | Webes keresés, otthoni automatizálás, naptár, bármi MCP-n keresztül |
| Új háttér | Bármely LLM vagy helyi modell, ami megfelel a `stream_turn` interfésznek |
| Személyiség sablonok | ME.md sablonok különböző nyelvekhez és személyiségekhez |
| Kutatás | Jobb vágy modellek, memóriakeresés, elmélet az elmében promping |
| Dokumentáció | Útmutatók, bemutatók, fordítások |

Lásd a [CONTRIBUTING.md](./CONTRIBUTING.md) fájlt a fejlesztési beállításhoz, kód stílushoz és PR irányelvekhez.

Ha nem vagy biztos benne, hol kezdj, [nyiss egy hibát](https://github.com/lifemate-ai/familiar-ai/issues) — szívesen segítek a helyes irányba.

---

## Licenc

[MIT](./LICENSE)
```
