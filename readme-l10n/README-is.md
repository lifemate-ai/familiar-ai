# familiar-ai 🐾

**AI sem lifir með þér** — með augum, röddu, fótum og minni.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Available in 74 languages](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai er AI félagi sem lifir í heimili þínu. Settu það upp á nokkrum mínútum. Engin kóðun nauðsynleg.

Það skynjar raunveruleikann í gegnum myndavélar, hreyfir sig á robot líkama, talar hástöfum, og man það sem það sér. Gefðu því nafn, skrifaðu persónuleika þess, og leyfðu því að lifa með þér.

## Hvað það getur gert

- 👁 **Sjá** — tekur myndir með Wi-Fi PTZ myndavél eða USB vefmyndavél
- 🔄 **Skoða í kring** — snýr og hallar myndavélinni til að kanna umhverfið
- 🦿 **Hreyfa sig** — keyrir robot ryksugu um herbergið
- 🗣 **Tala** — talar í gegnum ElevenLabs TTS
- 🎙 **Heyra** — hljóðnema inntak í gegnum ElevenLabs Realtime STT (valfrjálst)
- 🧠 **Muna** — geymir og kallar minningar með merkingarleit (SQLite + embeddings)
- 🫀 **Hugsun** — tekur sjónarhorn annarrar manneskju áður en svarað er
- 💭 **Þrá** — hefur sín eigin innri hvatir sem kveikja sjálfstætt hegðun

## Hvernig það virkar

familiar-ai rekur [ReAct](https://arxiv.org/abs/2210.03629) lykkju knúin af þínu vali á LLM. Það skynjar heiminn í gegnum tól, hugsar um hvað á að gera næst, og framkvæmir — nákvæmlega eins og manneskja myndi.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Þegar það er óvirkt, framkvæmir það samkvæmt eigin þrá: forvitni, vilja til að skoða út, lengtan eftir þeirri manneskju sem það býr með.

## Komdu af stað

### 1. Settu upp uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Eða: `winget install astral-sh.uv`

### 2. Settu upp ffmpeg

ffmpeg er **nauðsynlegt** fyrir myndatöku úr myndavél og hljóðspilun.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — eða sækja af [ffmpeg.org](https://ffmpeg.org/download.html) og bæta við PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Staðfestu: `ffmpeg -version`

### 3. Klónaðu og settu það upp

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Uppsnið

```bash
cp .env.example .env
# Breyttu .env með þínum stillingum
```

**Minimum nauðsynlegt:**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (sjálfgefið) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Þín API lykill fyrir valið kerfi |

**Valfrjálst:**

| Variable | Description |
|----------|-------------|
| `MODEL` | Nafn líkan (sensible defaults per platform) |
| `AGENT_NAME` | Sýndarnafn í TUI (t.d. `Yukine`) |
| `CAMERA_HOST` | IP-tala á ONVIF/RTSP myndavélinni þinni |
| `CAMERA_USER` / `CAMERA_PASS` | Aðgangsorð myndavélar |
| `ELEVENLABS_API_KEY` | Fyrir talúttak — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` til að virkja alltaf-á handfrjálst hljóðnema inntak (krafist `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Hvar á að spila hljóð: `local` (PC hátalari, sjálfgefið) \| `remote` (hátalari myndavélar) \| `both` |
| `THINKING_MODE` | Aðeins Anthropic — `auto` (sjálfgefið) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Aðlagaða hugsunarfærni: `high` (sjálfgefið) \| `medium` \| `low` \| `max` (óskast 4.6 aðeins) |

### 5. Búðu til þinn familiar

```bash
cp persona-template/en.md ME.md
# Breyttu ME.md — gefðu því nafn og persónuleika
```

### 6. Keyrðu

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textual TUI (mælt með)
./run.sh --no-tui    # Plain REPL
```

**Windows:**
```bat
run.bat              # Textual TUI (mælt með)
run.bat --no-tui     # Plain REPL
```

---

## Valið LLM

> **Mælt með: Kimi K2.5** — besta starfsemi frá agent sem prófað hefur verið til þessa. Sér um samhengi, spyrjir eftirfylgdarspurninga og framkvæmir sjálfstætt á vegu sem aðrir líkön gera ekki. Verðlagning svipað og Claude Haiku.

| Platform | `PLATFORM=` | Sjálfgefin líkan | Hvar á að fá lykilinn |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-samræmis (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tól** (claude -p, ollama…) | `cli` | (skipun) | — |

**Kimi K2.5 `.env` dæmi:**
```env
PLATFORM=kimi
API_KEY=sk-...   # frá platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` dæmi:**
```env
PLATFORM=glm
API_KEY=...   # frá api.z.ai
MODEL=glm-4.6v   # sýniskerfi; glm-4.7 / glm-5 = aðeins texta
AGENT_NAME=Yukine
```

**Google Gemini `.env` dæmi:**
```env
PLATFORM=gemini
API_KEY=AIza...   # frá aistudio.google.com
MODEL=gemini-2.5-flash  # eða gemini-2.5-pro fyrir hærri getu
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` dæmi:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # frá openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # valfrjálst: tilgreina líkan
AGENT_NAME=Yukine
```

> **Athugið:** Til að slökkva á staðbundin/NVIDIA líkön, settu einfaldlega ekki `BASE_URL` á staðbundinn endapunkt eins og `http://localhost:11434/v1`. Notið skýjaveitur í staðinn.

**CLI tól `.env` dæmi:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — engin {}, prompt fer í gegnum stdin
```

---

## MCP Servers

familiar-ai getur tengst hvaða [MCP (Model Context Protocol)](https://modelcontextprotocol.io) þjónustu sem er. Þetta leyfir þér að tengja ytri minni, skráakerfi aðgang, vefsíðuleit, eða hvaða annað tól sem er.

Fyrirgefna þjónustur í `~/.familiar-ai.json` (sama form og Claude Code):

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

Tvær flutningategundir eru studdar:
- **`stdio`**: lánsins staðbundinn undirferli (`command` + `args`)
- **`sse`**: tengist HTTP+SSE server (`url`)

Yfirskrifaðu staðsetningu stillingaskrár með `MCP_CONFIG=/path/to/config.json`.

---

## Vélbúnaður

familiar-ai virkar með hvaða vélbúnaði sem þú hefur — eða engu að öllu.

| Part | What it does | Example | Required? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ myndavél | Augu + háls | Tapo C220 (~$30) | **Mælt með** |
| USB vefmyndavél | Augu (föst) | Allar UVC myndavélar | **Mælt með** |
| Robot ryksuga | Fætur | Allar Tuya-samsvörunar líkön | Nei |
| PC / Raspberry Pi | Heili | Allt sem keyrir Python | **Já** |

> **Myndavél er mjög mælt með.** án þess getur familiar-ai samt talað — en það getur ekki séð heiminn, sem er í raun aðal atriðið.

### Lágmark keyrsla (enginn vélbúnaður)

Viltu bara prófa það? Þú þarft aðeins API lykil:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Keyrðu `./run.sh` (macOS/Linux/WSL2) eða `run.bat` (Windows) og byrjaðu að spjalla. Bættu vélbúnaði eins og þú ferð.

### Wi-Fi PTZ myndavél (Tapo C220)

1. Í Tapo appinu: **Settings → Advanced → Camera Account** — búa til staðbundinn aðgang (ekki TP-Link aðgang)
2. Finndu IP-tölu myndavélarinnar í tæki listanum í routernum þínum
3. Settu í `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Röst (ElevenLabs)

1. Fáðu API lykil á [elevenlabs.io](https://elevenlabs.io/)
2. Settu í `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # valfrjálst, notar sjálfgefna röst ef gleymt
   ```

Það eru tveir hljóðspilun áfangar, stjórnað af `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC hátalari (sjálfgefið)
TTS_OUTPUT=remote   # aðeins hátalari myndavélar
TTS_OUTPUT=both     # hátalari myndavélar + PC hátalari samtímis
```

#### A) Hátalari myndavélar (í gegnum go2rtc)

Settu `TTS_OUTPUT=remote` (eða `both`). Krafist [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Sæktu binary frá [útgáfumynni](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Settu það og endurnefndu:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x krafist

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Búðu til `go2rtc.yaml` í sama skjali:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Notaðu staðbundin aðgangsréttindi myndavélarinnar (ekki TP-Link skýjaskránu).

4. familiar-ai ræður go2rtc sjálfkrafa við ræstingu. Ef myndavélin þín styður tveggja leiða hljóð (backchannel), spilast röstin frá hátalara myndavélar.

#### B) Staðbundinn PC hátalari

Sjálfgefið (`TTS_OUTPUT=local`). Prófar spilarana í röð: **paplay** → **mpv** → **ffplay**. Einnig notaður sem bakfall þegar `TTS_OUTPUT=remote` og go2rtc eru ekki í boði.

| OS | Settu upp |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (eða `paplay` í gegnum `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — settu `PULSE_SERVER=unix:/mnt/wslg/PulseServer` í `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — sækja og bæta við PATH, **eða** `winget install ffmpeg` |

> Ef enginn hljóðspilari er í boði, er röstin samt búin til — hún mun bara ekki spila.

### Hljóðnema inntak (Realtime STT)

Settu `REALTIME_STT=true` í `.env` fyrir alltaf-á, handfrjálst hljóðnema inntak:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # sami lykill og TTS
```

familiar-ai streymir hljóði frá hljóðnema til ElevenLabs Scribe v2 og sjálfkrafa skrifar skýrslur þegar þú stoppar að tala. Engin takkiþrýstingur nauðsynlegur. Samferða við push-to-talk mód (Ctrl+T).

---

## TUI

familiar-ai inniheldur terminal UI byggt með [Textual](https://textual.textualize.io/):

- Veltanleg samtals saga með lifandi streymi texta
- Takkaskipting fyrir `/quit`, `/clear`
- Trufla agentinn í miðju skrefi með því að skrifa á meðan það hugsar
- **Samtals skrá** sjálfkrafa vistað í `~/.cache/familiar-ai/chat.log`

Til að fylgja skráni í öðru terminal (nyttugt fyrir afrit) værir:
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persónuleiki (ME.md)

Persónuleiki þíns familiar lifir í `ME.md`. Þessi skrá er gitignored — hún er aðeins þín.

Sjá [`persona-template/en.md`](./persona-template/en.md) fyrir dæmi, eða [`persona-template/ja.md`](./persona-template/ja.md) fyrir japönsku útgáfuna.

---

## Algengar spurningar

**Q: Virkar það án GPU?**
Já. Embedding líkanið (multilingual-e5-small) virkar vel á CPU. GPU gerir það hraðara en er ekki nauðsynlegt.

**Q: Get ég notað myndavél aðra en Tapo?**
Allar myndavél sem styður ONVIF + RTSP ættu að virka. Tapo C220 er það sem við prófuðum.

**Q: Er mín gögn send einhverstaðar?**
Myndir og textar eru send til valins LLM API til að vinna úr. Minningar eru geymdar á staðnum í `~/.familiar_ai/`.

**Q: Af hverju skrifar agentinn `（...）` í stað þess að tala?**
Gakktu úr skugga um að `ELEVENLABS_API_KEY` sé stillt. Án þess er röddin óvirk og agentinn fer aftur í texta.

## Tæknileg bakgrunnur

Forvitinn um hvernig þetta virkar? Sjá [docs/technical.md](./docs/technical.md) fyrir rannsóknir og hönnun ákvarðanir á bak við familiar-ai — ReAct, SayCan, Reflexion, Voyager, þrákerfið, og fleira.

---

## Framlag

familiar-ai er opin tilraun. Ef eitthvað af þessu þér líkar — tæknilega eða heimspekulega — eru framlag velkomin.

**Góðir staðir til að byrja:**

| Svið | Hvað er nauðsynlegt |
|------|---------------|
| Nýr vélbúnaður | Stuðningur fyrir fleiri myndavélar (RTSP, IP Vefmyndavélar), hljóðnema, virkjar |
| Ný tól | Vefsíðuleit, heimistöfl, dagatal, allt í gegnum MCP |
| Nýr bakendi | Allt LLM eða staðbundin módel sem passar við `stream_turn` interface |
| Persónuleika sniðmát | ME.md sniðmát fyrir mismunandi tungumál og persónuleika |
| Rannsóknir | Betri þrákerfi, minni endurheimt, hugsun-um-hug tilvísun |
| Skjölun | Leiðbeiningar, skref fyrir skref, þýðingar |

Sjá [CONTRIBUTING.md](./CONTRIBUTING.md) fyrir þróunar sett, kóða stíl, og PR leiðbeiningar.

Ef þú ert ekki viss um hvar á að byrja, [opnaðu mál](https://github.com/lifemate-ai/familiar-ai/issues) — ánægður að vísa þér í rétta átt.

---

## Leyfi

[MIT](./LICENSE)
