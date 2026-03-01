```markdown
# familiar-ai 🐾

**AI, kuris gyvena šalia tavęs** — su akimis, balsu, kojomis ir atmintimi.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai yra AI kompanionas, kuris gyvena tavo namuose.
Sukonfigūruok jį per keletą minučių. Kodas nereikalingas.

Jis suvokia tikrą pasaulį per kameras, juda roboto korpusu, kalba garsiai ir atsimena, ką mato. Duok jam vardą, parašyk jo asmenybę ir leisk jam gyventi su tavimi.

## Ką jis gali daryti

- 👁 **Matyti** — užfiksuoja vaizdus iš Wi-Fi PTZ kameros arba USB web kameros
- 🔄 **Apsidairyti** — sukasi ir pasviria kamera, kad ištirtų aplinką
- 🦿 **Judėti** — valdo roboto dulkių siurblį, kad naršytų po kambarį
- 🗣 **Kalbėti** — kalba per ElevenLabs TTS
- 🎙 **Klausytis** — balso įvestis be rankų per ElevenLabs Realtime STT (pagal pageidavimą)
- 🧠 **Atsiminti** — aktyviai saugo ir atkuria prisiminimus su semantine paieška (SQLite + embeddingai)
- 🫀 **Proto teorija** — prieš atsakydamas atsižvelgia į kito asmens perspektyvą
- 💭 **Noras** — turi savo vidinius troškimus, kurie sukelia savarankišką elgesį

## Kaip tai veikia

familiar-ai vykdo [ReAct](https://arxiv.org/abs/2210.03629) ciklą, kurį varo tavo pasirinktas LLM. Jis suvokia pasaulį per įrankius, galvoja, ką daryti toliau, ir veikia — lyg žmogus.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kai neveikia, jis veikia pagal savo troškimus: smalsumą, norą pažiūrėti lauk, pasiilgstant asmens, su kuriuo gyvena.

## Pradžia

### 1. Įdiek uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Įdiek ffmpeg

ffmpeg yra **būtinas** kameros vaizdų fiksavimui ir garso atkūrimui.

| OS | Komanda |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — arba atsisiųsk iš [ffmpeg.org](https://ffmpeg.org/download.html) ir pridėk prie PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Patikrink: `ffmpeg -version`

### 3. Klonuok ir įdiek

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Suconfigūruok

```bash
cp .env.example .env
# Redaguok .env su savo nustatymais
```

**Minimalūs reikalavimai:**

| Kintamasis | Aprašymas |
|------------|-----------|
| `PLATFORM` | `anthropic` (numatytasis) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Tavo API raktas pasirinktai platformai |

**Pasirinktinai:**

| Kintamasis | Aprašymas |
|------------|-----------|
| `MODEL` | Modelio pavadinimas (sąmoningi numatytieji parametrai pagal platformą) |
| `AGENT_NAME` | Atvaizduojamas vardas, rodomas TUI (pvz. `Yukine`) |
| `CAMERA_HOST` | Tavo ONVIF/RTSP kameros IP adresas |
| `CAMERA_USER` / `CAMERA_PASS` | Kamero kredencialai |
| `ELEVENLABS_API_KEY` | Balso išėjimui — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, kad įjungti visada veikiančią be rankų balso įvestį (reikia `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kur leisti garsą: `local` (PC garsiakalbis, numatyta) \| `remote` (kamero garsiakalbis) \| `both` |
| `THINKING_MODE` | Tik Anthropic — `auto` (numatytasis) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptuojamas mąstymo pastangų lygis: `high` (numatytasis) \| `medium` \| `low` \| `max` (tik Opus 4.6) |

### 5. Sukurk savo familiar

```bash
cp persona-template/en.md ME.md
# Redaguok ME.md — duok jam vardą ir asmenybę
```

### 6. Vykdyk

```bash
./run.sh             # Tekstinis TUI (rekomenduojama)
./run.sh --no-tui    # Paprastas REPL
```

---

## Pasirinkimas LLM

> **Rekomenduojama: Kimi K2.5** — geriausias agentinis našumas, kurį esame testavę. Atkreipia dėmesį į kontekstą, užduoda papildomus klausimus ir veikia savarankiškai taip, kaip kiti modeliai to nedaro. Kaina panaši į Claude Haiku.

| Platforma | `PLATFORM=` | Numatytoji modelis | Kur gauti raktą |
|-----------|------------|-------------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI suderinami (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
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
MODEL=glm-4.6v   # vizualizacijos galimybė; glm-4.7 / glm-5 = tik tekstui
AGENT_NAME=Yukine
```

**Google Gemini `.env` pavyzdys:**
```env
PLATFORM=gemini
API_KEY=AIza...   # iš aistudio.google.com
MODEL=gemini-2.5-flash  # arba gemini-2.5-pro didesnei galimybei
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` pavyzdys:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # iš openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # neprivaloma: nurodykite modelį
AGENT_NAME=Yukine
```

> **Pastaba:** Norėdami išjungti vietinius/NVIDIA modelius, tiesiog nenustatykite `BASE_URL` kaip vietinio galinio taško, pavyzdžiui, `http://localhost:11434/v1`. Naudokite debesų paslaugų teikėjus.

**CLI įrankio `.env` pavyzdys:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = užklausos argumentas
# MODEL=ollama run gemma3:27b  # Ollama — be {}, užklausa perduodama per stdin
```

---

## MCP serveriai

familiar-ai gali prisijungti prie bet kurio [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serverio. Tai leidžia įterpti išorinę atmintį, failų sistemos prieigą, interneto paiešką ar bet kokį kitą įrankį.

Sukonfigūruok serverius `~/.familiar-ai.json` (tas pats formatas kaip Claude Code):

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

Palaikomi du transporto tipai:
- **`stdio`**: paleidžia vietinį subprocess (`command` + `args`)
- **`sse`**: prisijungia prie HTTP+SSE serverio (`url`)

Perrašyk konfigūracijų failo vietą su `MCP_CONFIG=/path/to/config.json`.

---

## Aparatinė įranga

familiar-ai veikia su bet kokia turima aparatine įranga — arba visai be jos.

| Dalys | Ką ji daro | Pavyzdys | Reikalinga? |
|-------|-------------|----------|-------------|
| Wi-Fi PTZ kamera | Akys + kaklas | Tapo C220 (~$30) | **Rekomenduojama** |
| USB web kamera | Akys (fiksuotos) | Bet kuri UVC kamera | **Rekomenduojama** |
| Roboto dulkių siurblys | Kołos | Bet kuris modelis, suderinamas su Tuya | Ne |
| PC / Raspberry Pi | Smegenys | Bet kas, kas veikia Python | **Taip** |

> **Kamera yra labai rekomenduojama.** Be jos, familiar-ai gali kalbėti — bet negali matyti pasaulio, kas yra pagrindinė mintis.

### Minimalus nustatymas (be aparatinės įrangos)

Tiesiog nori tai išbandyti? Tau tik reikia API rakto:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Paleisk `./run.sh` ir pradėk bendrauti. Pridėk aparatūrą, kai tai reikalinga.

### Wi-Fi PTZ kamera (Tapo C220)

1. Tapo aplikacijoje: **Nustatymai → Išplėstiniai → Kameros paskyra** — sukurk vietinę paskyrą (ne TP-Link paskyrą)
2. Rask kameros IP adresą savo maršrutizatoriaus prietaisų sąraše
3. Nustatyk `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Balsas (ElevenLabs)

1. Gauk API raktą [elevenlabs.io](https://elevenlabs.io/)
2. Nustatyk `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # neprivaloma, naudojama numatytoji balsas, jei praleista
   ```

Yra dvi atkūrimo paskirties vietos, valdoma per `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC garsiakalbis (numatytas)
TTS_OUTPUT=remote   # tik kameros garsiakalbis
TTS_OUTPUT=both     # kameros garsiakalbis + PC garsiakalbis tuo pačiu metu
```

#### A) Kameros garsiakalbis (per go2rtc)

Nustatyk `TTS_OUTPUT=remote` (arba `both`). Reikalingas [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Atsisiųsk binarą iš [išleidimų puslapio](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Padėk ir pervadink jį:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x reikia

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Sukurk `go2rtc.yaml` toje pačioje direktorijoje:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Naudok vietinių kameros paskyros kredencialus (ne savo TP-Link debesų paskyros).

4. familiar-ai automatiškai paleidžia go2rtc paleidimo metu. Jei tavo kamera palaiko dvikryptę garso transliaciją (atgalinį kanalą), balsas skamba iš kameros garsiakalbio.

#### B) Vietinis PC garsiakalbis

Numatyta ( `TTS_OUTPUT=local`). Bando atkūrimo programas eiliškumu: **paplay** → **mpv** → **ffplay**. Taip pat naudojama kaip atsarginė, kai `TTS_OUTPUT=remote` ir go2rtc nėra prieinamas.

| OS | Įdiegti |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (arba `paplay` per `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — nustatyk `PULSE_SERVER=unix:/mnt/wslg/PulseServer` `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — atsisiųsk ir pridėk prie PATH, **arba** `winget install ffmpeg` |

> Jei nėra garso grotuvo, kalba vis tiek generuojama — tiesiog ji nebus grojama.

### Balsas įvestis (Realtime STT)

Nustatyk `REALTIME_STT=true` `.env`, kad gautum nuolat veikiančią, be rankų balso įvestį:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # tas pats raktas kaip TTS
```

familiar-ai transliuoja mikrofono garsą į ElevenLabs Scribe v2 ir automatiškai registruoja transkripcijas, kai tu nustoji kalbėti. Jokio mygtuko paspaudimo nereikia. Tai gali sugyventi su stumti-kalbėti režimu (Ctrl+T).

---

## TUI

familiar-ai apima terminalo UI, sukurtą su [Textual](https://textual.textualize.io/):

- Rulable pokalbių istorija su gyvu tekstu
- Tab-completion `/quit`, `/clear`
- Pertrauk agentą viduryje mąstymo, rašydamas tuo metu
- **Kopijos žurnalas** automatiškai išsaugomas `~/.cache/familiar-ai/chat.log`

Norėdami stebėti žurnalą kitoje terminale (naudinga kopijavimui):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Tavo familiar asmenybė gyvena `ME.md`. Šis failas yra gitignored — jis priklauso tik tau.

Žiūrėk [`persona-template/en.md`](./persona-template/en.md) pavyzdžiui, arba [`persona-template/ja.md`](./persona-template/ja.md) japoniškai versijai.

---

## DUK

**K: Ar jis veikia be GPU?**
Taip. Embedding modelis (multilingual-e5-small) veikia gerai CPU. GPU padaro jį greitesnį, bet nėra būtinas.

**K: Ar galiu naudoti kamerą, kuri nėra Tapo?**
Bet kuri kamera, kuri palaiko ONVIF + RTSP turėtų veikti. Tapo C220 buvo testuota.

**K: Ar mano duomenys siunčiami kur nors?**
Vaizdai ir tekstas siunčiami pasirinktai LLM API apdorojimui. Prisiminimai saugomi lokaliai `~/.familiar_ai/`.

**K: Kodėl agentas rašo `（...）` vietoj kalbėjimo?**
Įsitikink, kad `ELEVENLABS_API_KEY` yra nustatytas. Be jo balsas išjungiamas ir agentas grįžta prie teksto.

## Techninė informacija

Smalsu, kaip tai veikia? Žiūrėk [docs/technical.md](./docs/technical.md) tyrimams ir dizaino sprendimams už familiar-ai — ReAct, SayCan, Reflexion, Voyager, troškimų sistema ir dar daugiau.

---

## Prisidėjimas

familiar-ai yra atviras eksperimentas. Jei kas nors iš to su tavimi rezonuoja — techniškai ar filosofiniu požiūriu — indėliai yra labai laukiami.

**Geros vietos pradėti:**

| Sritis | Kas reikalinga |
|--------|----------------|
| Nauja aparatinė įranga | Daugiau kamerų palaikymas (RTSP, IP web kamera), mikrofonai, veikėjai |
| Naujieji įrankiai | Interneto paieška, namų automatika, kalendorius, bet kas per MCP |
| Nauji galiniai | Bet koks LLM ar vietinis modelis, kuris atitinka `stream_turn` sąsają |
| Persona šablonai | ME.md šablonai skirtingomis kalbomis ir asmenybėmis |
| Tyrimai | Geresni troškimų modeliai, atminties atgaminimas, proto teorijos raginimas |
| Dokumentacija | Pamokos, išsamūs aprašymai, vertimai |

Žiūrėk [CONTRIBUTING.md](./CONTRIBUTING.md) dėl kūrimo nustatymo, kodo stiliaus ir PR gaires.

Jei nesate tikri, nuo ko pradėti, [atidaryk klausimą](https://github.com/lifemate-ai/familiar-ai/issues) — mielai nukreipsiu tave teisinga linkme.

---

## Licencija

[MIT](./LICENSE)
```
