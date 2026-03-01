# familiar-ai 🐾

**Dirbtinis intelektas, gyvenantis šalia tavęs** — su akimis, balsu, kojomis ir atmintimi.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Galima 74 kalbomis](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai yra dirbtinio intelekto kompanionas, gyvenantis tavo namuose. 
Nustatyk jį per kelias minutes. Programavimo nes reikia.

Jis suvokia tikrą pasaulį per kameras, juda robotinėje kūno formoje, kalba garsiai ir prisimena, ką mato. Duok jam vardą, aprašyk jo asmenybę ir leisk jam gyventi su tavimi.

## Ką jis gali daryti

- 👁 **Matyti** — fiksuoja vaizdus iš Wi-Fi PTZ kameros arba USB vaizdo kameros
- 🔄 **Apsidairyti** — pasuka ir pakreipia kamerą, kad ištirtų aplinką
- 🦿 **Judėti** — vairuoja robotinį dulkių siurblį, kad nuskristų po kambarį
- 🗣 **Kalbėti** — kalba per ElevenLabs TTS
- 🎙 **Klausytis** — laisvomis rankomis balsu įvesti per ElevenLabs Realtime STT (opt-in)
- 🧠 **Prisiminti** — aktyviai saugo ir prisimena prisiminimus su semantiniu paieškos (SQLite + embedding)
- 🫀 **Mąstymo teorija** — atsako į kitų asmenų perspektyvą prieš atsakydamas
- 💭 **Norai** — turi savų vidinių potraukių, kurie sukelia autonominį elgesį

## Kaip tai veikia

familiar-ai vykdo [ReAct](https://arxiv.org/abs/2210.03629) ciklą, priklauso nuo tavo pasirinkto LLM. Jis suvokia pasaulį per įrankius, galvoja, ką daryti kitą, ir veikia — kaip ir žmogus.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Būdamas ramybėje, jis veikia pagal savo norus: smalsumą, norą pasižiūrėti į lauką, liūdesį dėl asmens, su kuriuo gyvena.

## Pradėti

### 1. Įdiekite uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Arba: `winget install astral-sh.uv`

### 2. Įdiekite ffmpeg

ffmpeg yra **būtinas** kameros vaizdų fiksavimui ir garso atklausai.

| OS | Komanda |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — arba atsisiųskite iš [ffmpeg.org](https://ffmpeg.org/download.html) ir pridėkite prie PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Patvirtinkite: `ffmpeg -version`

### 3. Klonuokite ir įdiekite

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Suconfiguruokite

```bash
cp .env.example .env
# Redaguokite .env su savo nustatymais
```

**Minimalūs reikalavimai:**

| Kintamasis | Aprašymas |
|------------|-----------|
| `PLATFORM` | `anthropic` (pagal numatytąjį) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Tavo API raktas pasirinktam platformai |

**Pasirinktinai:**

| Kintamasis | Aprašymas |
|------------|-----------|
| `MODEL` | Modelio pavadinimas (logiški numatyti kiekvienai platformai) |
| `AGENT_NAME` | Rodo vardą, kuris rodomas TUI (pvz., `Yukine`) |
| `CAMERA_HOST` | Tavo ONVIF/RTSP kameros IP adresas |
| `CAMERA_USER` / `CAMERA_PASS` | Kameros prisijungimo duomenys |
| `ELEVENLABS_API_KEY` | Balsui – [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, kad įjungtum visada aktyvų balsu be rankų įvedimą (reikia `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kur leisti garsą: `local` (PC garsiakalbis, numatytoji) \| `remote` (kameroje) \| `both` |
| `THINKING_MODE` | Tik Anthropic — `auto` (numatytasis) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Priklausomas mąstymo pastangų: `high` (numatytas) \| `medium` \| `low` \| `max` (tik Opus 4.6) |

### 5. Sukurkite savo familiar

```bash
cp persona-template/en.md ME.md
# Redaguokite ME.md — duokite jam vardą ir asmenybę
```

### 6. Paleiskite

**macOS / Linux / WSL2:**
```bash
./run.sh             # Tekstinis TUI (rekomenduojama)
./run.sh --no-tui    # Paprastas REPL
```

**Windows:**
```bat
run.bat              # Tekstinis TUI (rekomenduojama)
run.bat --no-tui     # Paprastas REPL
```

---

## Pasirinkti LLM

> **Rekomenduojama: Kimi K2.5** — geriausias agentinis našumas, iki šiol išbandytas. Pastebi kontekstą, klausia sekinių klausimų ir veikia autonomiškai būdais, kurių kiti modeliai nepadaro. Kaina panaši į Claude Haiku.

| Platforma | `PLATFORM=` | Numatytoji modelis | Kur gauti raktą |
|-----------|-------------|-------------------|------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI suderinamas (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (daugelio tiekėjų) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI įrankis** (claude -p, ollama…) | `cli` | (komanda) | — |

**Kimi K2.5 `.env` pavyzdys:**
```env
PLATFORM=kimi
API_KEY=sk-...   # iš platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` pavyzdys:**
```env
PLATFORM=glm
API_KEY=...   # iš api.z.ai
MODEL=glm-4.6v   # vaizdo padedamas; glm-4.7 / glm-5 = tik tekstui
AGENT_NAME=Yukine
```

**Google Gemini `.env` pavyzdys:**
```env
PLATFORM=gemini
API_KEY=AIza...   # iš aistudio.google.com
MODEL=gemini-2.5-flash  # arba gemini-2.5-pro didesniam pajėgumui
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` pavyzdys:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # iš openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # pasirenkama: nurodykite modelį
AGENT_NAME=Yukine
```

> **Pastaba:** Norint išjungti vietinius/NVIDIA modelius, tiesiog nenustatykite `BASE_URL` vietinei galinei linijai, pavyzdžiui, `http://localhost:11434/v1`. Vietoje to naudokite debesų paslaugas.

**CLI įrankio `.env` pavyzdys:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = užklausos arg
# MODEL=ollama run gemma3:27b  # Ollama — jokio {}, užklausa siunčiama per stdin
```

---

## MCP Serveriai

familiar-ai gali prisijungti prie bet kurio [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serverio. Tai leidžia jums prijungti išorinę atmintį, failų sistemą, interneto paiešką ar bet kurį kitą įrankį.

Suconfiguruokite serverius `~/.familiar-ai.json` (tas pats formatas kaip Claude Code):

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

Palaikomos dvi transporto rūšys:
- **`stdio`**: paleisti vietinį subprocess (`command` + `args`)
- **`sse`**: prisijungti prie HTTP+SSE serverio (`url`)

Perrašykite konfigūracijų failo vietą su `MCP_CONFIG=/path/to/config.json`.

---

## Aparatinė įranga

familiar-ai veikia su bet kuria turima aparatine įranga — arba visai be jos.

| Dalis | Ką ji daro | Pavyzdys | Būtina? |
|-------|------------|-----------|---------|
| Wi-Fi PTZ kamera | Akys + kaklas | Tapo C220 (~$30) | **Rekomenduojama** |
| USB vaizdo kamera | Akys (fiksuotos) | Bet kuri UVC kamera | **Rekomenduojama** |
| Robotinis dulkių siurblys | Kojos | Bet kuris Tuya suderinamas modelis | Ne |
| PC / Raspberry Pi | Smegenys | Bet kas, kas veikia Python | **Taip** |

> **Kamera stipriai rekomenduojama.** Be jos, familiar-ai vis tiek gali kalbėti — tačiau jis negali matyti pasaulio, kas yra esmė.

### Minimalus nustatymas (be aparatinės įrangos)

Tiesiog nori išbandyti? Tau reikalingas tik API raktas:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Paleisk `./run.sh` (macOS/Linux/WSL2) arba `run.bat` (Windows) ir pradėk bendrauti. Pridėk aparatūrą vėliau.

### Wi-Fi PTZ kamera (Tapo C220)

1. Tapo programėlėje: **Nustatymai → Išplėstinės → Kameros paskyra** — sukurti vietinę paskyrą (ne TP-Link paskyra)
2. Rask kameros IP adresą savo maršruto nustatymuose
3. Nustatykite faile `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Balsas (ElevenLabs)

1. Gauk API raktą iš [elevenlabs.io](https://elevenlabs.io/)
2. Nustatykite faile `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # pasirenkama, naudoja numatytą balsą, jei praleista
   ```

Yra dvi atklausos paskirties, valdomos `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC garsiakalbis (numatytas)
TTS_OUTPUT=remote   # tik kameros garsiakalbis
TTS_OUTPUT=both     # kameros garsiakalbis + PC garsiakalbis vienu metu
```

#### A) Kameros garsiakalbis (per go2rtc)

Nustatykite `TTS_OUTPUT=remote` (arba `both`). Reikia [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Atsisiųskite binarinį failą iš [leidimų puslapio](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Padėkite ir pervadinkite:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x reikia

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Sukurkite `go2rtc.yaml` toje pačioje direktorijoje:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Naudokite vietinės kameros paskyros prisijungimo duomenis (ne savo TP-Link debesų paskyros).

4. familiar-ai automatiškai paleidžia go2rtc paleidimo metu. Jei jūsų kamera palaiko dvipusį garsą (atskyrimą), balsas grojamas iš kameros garsiakalbio.

#### B) Vietinis PC garsiakalbis

Numatytas ( `TTS_OUTPUT=local`). Bando grotuvus eilės tvarka: **paplay** → **mpv** → **ffplay**. Taip pat naudojamas kaip atsarginis, kai `TTS_OUTPUT=remote` ir go2rtc nėra po ranka.

| OS | Įdiegti |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (arba `paplay` per `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — nustatykite `PULSE_SERVER=unix:/mnt/wslg/PulseServer` faile `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — atsisiųskite ir pridėkite prie PATH, **arba** `winget install ffmpeg` |

> Jei nėra jokio garso grotuvų, balsas vis tiek bus sukurtas — tiesiog jis neskambės.

### Balsu įvestis (Realaus laiko STT)

Nustatykite `REALTIME_STT=true` faile `.env`, kad visada būtų aktyvi, be rankų balsinė įvestis:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # tas pats raktas kaip ir TTS
```

familiar-ai perduoda mikrofono garsą į ElevenLabs Scribe v2 ir automatiškai saugo transkriptus, kai tu sustoji kalbėti. Nereikia paspausti jokio mygtuko. Koegzistuoja su paspaudimu kalbėjimui (Ctrl+T).

---

## TUI

familiar-ai apima terminalo UI, sukurtą su [Textual](https://textual.textualize.io/):

- Slenkamas pokalbio istorija su gyvu tiesioginiu tekstu
- Tab-completion „/quit“, „/clear“
- Pertraukti agentą vidury veiksmų, kai jis galvoja
- **Pokalbių žurnalas** automatiškai išsaugomas `~/.cache/familiar-ai/chat.log`

Norint sekti žurnalą kitoje terminale (naudinga kopijuoti-klijuoti):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Asmenybė (ME.md)

Tavo familiar asmenybė gyvena `ME.md`. Šis failas yra gitignored — jis tik tavo.

Žiūrėkite [`persona-template/en.md`](./persona-template/en.md) kaip pavyzdį, arba [`persona-template/ja.md`](./persona-template/ja.md) japonų versijai.

---

## DUK

**K: Ar jis veikia be GPU?**
Taip. Įterpimo modelis (multilingual-e5-small) veikia normaliai su CPU. GPU paspartina, bet nėra būtinas.

**K: Ar galiu naudoti kamerą, kuri nėra Tapo?**
Bet kuri kamera, palaikanti ONVIF + RTSP, turėtų veikti. Tapo C220 buvo mūsų išbandomos.

**K: Ar mano duomenys siunčiami kur nors?**
Vaizdai ir tekstas siunčiami tavo pasirinktam LLM API apdoroti. Prisiminimai saugomi lokaliai `~/.familiar_ai/`.

**K: Kodėl agentas rašo `（...）` vietoj to, kad kalbėtų?**
Įsitikink, kad `ELEVENLABS_API_KEY` nustatytas. Be jos, balsas yra išjungtas ir agentas grįžta prie teksto.

## Techninė informacija

Ar įdomu, kaip tai veikia? Žiūrėkite [docs/technical.md](./docs/technical.md) už tyrimus ir dizaino sprendimus už familiar-ai — ReAct, SayCan, Reflexion, Voyager, norų sistemą ir dar daugiau.

---

## Prisidėjimas

familiar-ai yra atviras eksperimentas. Jei kas nors iš to, kas pasakoma, tau patinka — techniškai ar filosofiniu aspektu — busite labai laukiami prisidėti.

**Geros vietos pradėti:**

| Sritis | Kas reikalinga |
|--------|----------------|
| Nauja aparatinė įranga | Palaikymas daugiau kameros (RTSP, IP vaizdo kamerų), mikrofonų, veikėjų |
| Nauji įrankiai | Interneto paieška, namų automatizavimas, kalendorius, bet kas per MCP |
| Naujai užpakaliams | Bet kuris LLM ar vietinis modelis, atitinkantis `stream_turn` sąsają |
| Asmenybės šablonai | ME.md šablonai skirtingoms kalboms ir asmenybėms |
| Tyrimai | Geresni norų modeliai, atminties atkūrimas, mąstymo teorijos poreikiai |
| Dokumentacija | Pamokos, instrukcijos, vertimai |

Žiūrėkite [CONTRIBUTING.md](./CONTRIBUTING.md) už kūrimo nustatymą, kodo stilių ir PR gaires.

Jei nesate tikri, nuo ko pradėti, [atidarykite problemą](https://github.com/lifemate-ai/familiar-ai/issues) — mielai padėsime.

---

## Licencija

[MIT](./LICENSE)
