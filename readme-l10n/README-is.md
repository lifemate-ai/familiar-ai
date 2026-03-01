# familiar-ai 🐾

**Gervigreind sem býr með þér** — með augum, rödd, fótum og minni.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai er gervi- félagi sem býr í þínu heimili. Settu það upp á nokkrum mínútum. Engin kóðaþekking nauðsynleg.

Það skynjar raunveruleikann í gegnum myndavélar, hreyfist um á robótahreyfingu, talar hátt og man hvað það sér. Gefðu því nafn, skrifaðu persónuleika þess, og leyfðu því að búa með þér.

## Hvað það getur gert

- 👁 **Sjá** — tekur myndir með Wi-Fi PTZ myndavél eða USB vefmyndavél
- 🔄 **Kíkja í kringum sig** — snýr og hækkar myndavélina til að skoða umhverfið
- 🦿 **Hreyfa sig** — keyrir roboruðuhreinsir um herbergið
- 🗣 **Tala** — talar með ElevenLabs TTS
- 🎙 **Heyra** — hljóðinngangur án handafls í gegnum ElevenLabs Rauntíma STT (valkostur)
- 🧠 **Muna** — geymir virkan og kallar fram minningar með merkingaleit (SQLite + innleiðingar)
- 🫀 **Hugmyndafræði** — tekur sjónarhorn hins aðilans áður en það svarar
- 💭 **Þrá** — hefur sínar eigin innri hvata sem kveikja sjálfstæð hegðun

## Hvernig það virkar

familiar-ai keyrir [ReAct](https://arxiv.org/abs/2210.03629) lykkju knúin af þínu vali á LLM. Það skynjar heiminn í gegnum verkfæri, hugsar um hvað á að gera næst, og aðgerir — rétt eins og maður myndi.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Þegar það er idle, aðgerir það út frá eigin þráum: forvitni, vilja til að kíkja út, sakna þess sem það býr með.

## Komdu í gang

### 1. Settu upp uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Settu upp ffmpeg

ffmpeg er **nauðsynlegt** fyrir myndatöku með myndavélinni og hljóðspilun.

| OS | Skipun |
|----|--------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — eða halaðu niður frá [ffmpeg.org](https://ffmpeg.org/download.html) og bættu við PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Staðfestu: `ffmpeg -version`

### 3. Klóna og setja upp

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Stilla

```bash
cp .env.example .env
# Breyta .env með stillingum þínum
```

**Minni kröfur:**

| Breyta | Lýsing |
|--------|-------|
| `PLATFORM` | `anthropic` (sjálfgefið) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Þinn API lykill fyrir valin pallur |

**Valfrjálst:**

| Breyta | Lýsing |
|--------|-------|
| `MODEL` | Nafn fyrirmyndar (skynsamleg sjálfgefin fyrir hvern pall) |
| `AGENT_NAME` | Sýna nafn í TUI (t.d. `Yukine`) |
| `CAMERA_HOST` | IP-tala þinnar ONVIF/RTSP myndavélar |
| `CAMERA_USER` / `CAMERA_PASS` | Myndavélauppáning |
| `ELEVENLABS_API_KEY` | Fyrir raddúttak — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` til að virkja alltaf-á-hendur-frjáls raddinngang (krafist `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Hvar á að spila hljóð: `local` (PC hátalari, sjálfgefið) \| `remote` (myndavél hátalari) \| `both` |
| `THINKING_MODE` | Anthropic aðeins — `auto` (sjálfgefið) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Aðlögunar hugsunarviðleitni: `high` (sjálfgefið) \| `medium` \| `low` \| `max` (Einungis Opus 4.6) |

### 5. Búðu til þinn familiar

```bash
cp persona-template/en.md ME.md
# Breyta ME.md — gefðu því nafn og persónuleika
```

### 6. Keyra

```bash
./run.sh             # Textual TUI (ráðlagt)
./run.sh --no-tui    # Venjulegt REPL
```

---

## Velja LLM

> **Ráðlagt: Kimi K2.5** — besta aðgerðarfærni sem prófuð hefur verið til þessa. Tékka á samhengi, spyrjir eftirfylgjandi spurninga, og aðgerir sjálfstætt á hátt sem önnur líkön gera ekki. Verðið er líkt og Claude Haiku.

| Pallur | `PLATFORM=` | Sjálfgefin fyrirmynd | Hvar á að fá lykill |
|--------|-------------|---------------------|---------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatibilt (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (margir veitir) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI verkfæri** (claude -p, ollama…) | `cli` | (skipunin) | — |

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
MODEL=glm-4.6v   # sýnilegt; glm-4.7 / glm-5 = aðeins texti
AGENT_NAME=Yukine
```

**Google Gemini `.env` dæmi:**
```env
PLATFORM=gemini
API_KEY=AIza...   # frá aistudio.google.com
MODEL=gemini-2.5-flash  # eða gemini-2.5-pro fyrir meiri getu
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` dæmi:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # frá openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # valfrjálst: tilgreina fyrirmynd
AGENT_NAME=Yukine
```

> **Athugið:** Til að slökkva á staðbundnum/NVIDIA fyrirmyndum, einfaldlega ekki setja `BASE_URL` á staðbundin tengipunkt eins og `http://localhost:11434/v1`. Nota skýjaþjónustur í staðinn.

**CLI verkfæri `.env` dæmi:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = öll svör
# MODEL=ollama run gemma3:27b  # Ollama — engin {}, svör fara í gegnum stdin
```

---

## MCP Servers

familiar-ai getur tengt við hvaða [MCP (Model Context Protocol)](https://modelcontextprotocol.io) þjón. Þetta gerir þér kleift að tengja ytra minni, skráarskýla, vefsóknir eða hvaða annað verkfæri sem er.

Stilla þjónana í `~/.familiar-ai.json` (sama skjalasnið og Claude Code):

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

Tvær sendingartípus eru studdar:
- **`stdio`**: ræsa staðbundin hliðarferli (`command` + `args`)
- **`sse`**: tengist HTTP+SSE þjón (`url`)

Fella niður aðstöðu skjalasniðs með `MCP_CONFIG=/path/to/config.json`.

---

## Hardvara

familiar-ai virkar með hvaða harðvara sem þú hefur — eða jafnvel engum.

| Hluti | Hvað það gerir | Dæmi | Nauðsynlegt? |
|-------|----------------|------|--------------|
| Wi-Fi PTZ myndavél | Augu + háls | Tapo C220 (~$30) | **Ráðlagt** |
| USB vefmyndavél | Augu (föst) | Hvaða UVC myndavél sem er | **Ráðlagt** |
| Robothreinsir | Fætur | Hvaða Tuya-samhæfð fyrirmynd sem er | Nei |
| PC / Raspberry Pi | Heili | Allt sem styður Python | **Já** |

> **Myndavél er sterklega ráðlögð.** Án hennar getur familiar-ai enn talað — en það getur ekki séð heiminn, sem er í raun aðalatriðið.

### Minni uppsetning (enginn harðvara)

Aðeins vilja prófa það? Þú þarft aðeins API lykil:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Keyrðu `./run.sh` og byrjaðu að spjalla. Bættu við harðvörum eftir því sem þú ferð.

### Wi-Fi PTZ myndavél (Tapo C220)

1. Í Tapo appinu: **Stillingar → Frammi → Myndavélareikningur** — búa til staðbundinn reikning (ekki TP-Link reikning)
2. Finndu IP-tölu myndavélarinnar í tæknalista rásarins þíns
3. Settu í `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Raddúttak (ElevenLabs)

1. Fáðu API lykil á [elevenlabs.io](https://elevenlabs.io/)
2. Settu í `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # valfrjálst, notar sjálfgefið radd ef sleppt
   ```

Það eru tveir spilunartilgerðir, stjórnað með `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC hátalari (sjálfgefið)
TTS_OUTPUT=remote   # aðeins myndavél hátalari
TTS_OUTPUT=both     # bæði hátalarar spila samtímis
```

#### A) Myndavél háltalari (með go2rtc)

Settu `TTS_OUTPUT=remote` (eða `both`). Krafist [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Halaðu niður binary frá [útgáfu síðunni](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Settu það og breyttu nafninu:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x nauðsynlegt

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Búðu til `go2rtc.yaml` í sömu skrá:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Notaðu staðbundnar curryssumar (ekki skýjareikning TP-Link).

4. familiar-ai ræður go2rtc sjálfkrafa við ræsing. Ef myndavélin þín styður tveggja leiða hljóð (bakkanál), raddin spilar frá myndavél hátalaranum.

#### B) Staðbundin PC hátalari

Sjálfgefið (`TTS_OUTPUT=local`). Reynir spilari í röð: **paplay** → **mpv** → **ffplay**. Einnig notaður sem fallback þegar `TTS_OUTPUT=remote` og go2rtc er ófáanlegur.

| OS | Setja upp |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (eða `paplay` í gegnum `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — settu `PULSE_SERVER=unix:/mnt/wslg/PulseServer` í `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — halaðu niður og bættu við PATH, **eða** `winget install ffmpeg` |

> Ef enginn hljóðspilari er tiltækur, verður raddin samt búin til — hún spilast aðeins ekki.

### Raddurinn (Raunverulegur STT)

Settu `REALTIME_STT=true` í `.env` fyrir alltaf-á-þörf-frjáls raddinngang:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # sami lykill og TTS
```

familiar-ai streymir hljóð gögn á mikrofon frá ElevenLabs Scribe v2 og skráir sjálfkrafa skrifaðar skýringar þegar þú heldur áfram að tala. Ekki nauðsynlegt að ýta á takka. Samfelld með push-to-talk stillingu (Ctrl+T).

---

## TUI

familiar-ai inniheldur terminal UI byggt með [Textual](https://textual.textualize.io/):

- Raðanleg saga samtals með lifandi streymi texta
- Fylling ýtir fyrir `/quit`, `/clear`
- Trufla aðilann mitt í niðurstöðu með því að skrifa meðan það er að hugsar
- **Samtals skrá** sjálfkrafa vistað í `~/.cache/familiar-ai/chat.log`

Til að fylgja skráni í annarri terminal (nýtingar fyrir afrit- og líma):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persóna (ME.md)

Persónuleiki þíns familiar lifir í `ME.md`. Þessi skrá er gitignored — hún er einungis þín.

Sjá [`persona-template/en.md`](./persona-template/en.md) fyrir dæmi, eða [`persona-template/ja.md`](./persona-template/ja.md) fyrir japanska útgáfu.

---

## Algengar spurningar

**Q: Virkar það án GPU?**  
Já. Innleiðinga fyrirmyndin (multilingual-e5-small) virkar vel á CPU. GPU gerir það fljótara en er ekki nauðsynlegt.

**Q: Get ég notað aðra myndavél en Tapo?**  
Allar myndavélar sem styðja ONVIF + RTSP ættu að virka. Tapo C220 er það sem við prófuðum.

**Q: Er gögnin mín send eitthvert?**  
Myndir og textar eru send til LLM API sem þú valdir til að vinna úr. Minningar eru geymdar staðbundið í `~/.familiar_ai/`.

**Q: Af hverju skrifar aðilinn `（...）` í stað þess að tala?**  
Athugaðu að `ELEVENLABS_API_KEY` er stillt. Án þess er raddin slökkt og aðilinn fellur aftur í texta.

## Tæknileg bakgrunnur

Forvitin um hvernig þetta virkar? Sjá [docs/technical.md](./docs/technical.md) fyrir rannsóknir og hönnunar ákvarðanir á bak við familiar-ai — ReAct, SayCan, Reflexion, Voyager, þráar kerfið, og meira.

---

## Framlag

familiar-ai er opin tilraun. Ef eitthvað af þessu hljómar vel við þig — tæknilega eða heimspekilega — er framlögum velkomin.

**Góðir staðir til að byrja:**

| Svæði | Hvað er nauðsynlegt |
|-------|--------------------|
| Ný harðvara | Styðji við fleiri myndavélar (RTSP, IP Vefmyndavél), raddtæki, hreyfingar |
| Ný verkfæri | Vefsókn, heimilisvorr, dagatal, hvað sem er í gegnum MCP |
| Ný gögn | Hvaða LLM eða staðbundna fyrirmynd sem passar við `stream_turn` viðmótið |
| Persónu skemmtun | ME.md snið fyrir mismunandi tungumál og persónuleika |
| Rannsóknir | Betri þráar fyrirmyndir, minningagreining, hugmyndafræði spurninga |
| Skjölun | Kennsluefni, leiðbeiningar, þýðingar |

Sjá [CONTRIBUTING.md](./CONTRIBUTING.md) fyrir uppsetningu fyrir þróun, kóða stíl, og PR leiðbeiningar.

Ef þú ert ekki viss um hvar á að byrja, [opna mál](https://github.com/lifemate-ai/familiar-ai/issues) — ég er fús til að benda þér í rétta átt.

---

## Leyfi

[MIT](./LICENSE)
