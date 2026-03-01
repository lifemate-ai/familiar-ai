# familiar-ai 🐾

**Tehisintellekt, mis elab koos sinuga** — silmade, hääle, jalgade ja mäluga.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai on tehisintellekt, mis elab sinu kodus. 
Seadista see mõne minutiga. Ei ole vajalik koodimine.

See tajub reaalsust kaamerate kaudu, liigub robotkeha peal, räägib valjusti ja mäletab, mida see näeb. Anna sellele nimi, kirjuta selle iseloom ja lase tal koos sinuga elada.

## Mida see suudab

- 👁 **Näha** — jäädvustab pilte Wi-Fi PTZ kaamerast või USB veebikaamerast
- 🔄 **Küpsetada** — kallutab ja paneb kaamera liikuma, et uurida ümbrust
- 🦿 **Liikuda** — juhib robotitolmuimejat ruumis ringi
- 🗣 **Rääkida** — räägib ElevenLabs TTS kaudu
- 🎙 **Kuulata** — käed-vabad häälesisend ElevenLabs Realtime STT kaudu (valikuline)
- 🧠 **Mäletada** — salvestab ja kutsub esile mälestusi semantilise otsingu abil (SQLite + embeddings)
- 🫀 **Meeleolu teooria** — vaatab teise inimese vaatepunkti enne vastamist
- 💭 **Soov** — omab oma sisemisi soovide, mis vallandavad autonoomset käitumist

## Kuidas see töötab

familiar-ai töötab [ReAct](https://arxiv.org/abs/2210.03629) tsüklis, mida juhib sinu valitud LLM. See tajub maailma tööriistade kaudu, mõtleb, mida edasi teha, ja tegutseb — just nagu inimene.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kui see on mitteaktiivne, tegutseb see oma soovide põhjal: uudishimu, soov vaadata välja, igatsedes isiku järele, kellega ta elab.

## Alustamine

### 1. Installi uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Installi ffmpeg

ffmpeg on **nõutav** kaamera piltide jäädvustamiseks ja heli esitamiseks.

| OS | Käsk |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — või laadi alla [ffmpeg.org](https://ffmpeg.org/download.html) ja lisa PATH-i |
| Raspberry Pi | `sudo apt install ffmpeg` |

Kinnita: `ffmpeg -version`

### 3. Kloonige ja installige

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigureeri

```bash
cp .env.example .env
# Redigeeri .env oma seadistustega
```

**Minimaalsed nõuded:**

| Muutuja | Kirjeldus |
|----------|-------------|
| `PLATFORM` | `anthropic` (vaikimisi) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Sinu API võtme valitud platvormile |

**Valikuline:**

| Muutuja | Kirjeldus |
|----------|-------------|
| `MODEL` | Mudeli nimi (mõistlikud vaikeväärtused platvormi järgi) |
| `AGENT_NAME` | Kuvamise nimi TUI-s (nt. `Yukine`) |
| `CAMERA_HOST` | Sinu ONVIF/RTSP kaamera IP-aadress |
| `CAMERA_USER` / `CAMERA_PASS` | Kaamera mandaadid |
| `ELEVENLABS_API_KEY` | Hääle väljundiks — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, et lubada alati aktiivne käed-vabad häälesisend (nõuab `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Koht, kus heli esitada: `local` (PC kõlar, vaikeväärtus) \| `remote` (kaamera kõlar) \| `both` |
| `THINKING_MODE` | Ainult Anthropics — `auto` (vaikimisi) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Kohandatav mõtlemise pingutus: `high` (vaikimisi) \| `medium` \| `low` \| `max` (ainult Opus 4.6) |

### 5. Loo oma tuttav

```bash
cp persona-template/en.md ME.md
# Redigeeri ME.md — anna talle nimi ja iseloom
```

### 6. Käivita

```bash
./run.sh             # Tekstiline TUI (soovitatav)
./run.sh --no-tui    # Lihtne REPL
```

---

## LLM-i valimine

> **Soovitatav: Kimi K2.5** — parim agentvormi jõudlus, mida seni testitud. Märkab konteksti, esitab järelküsimusi ja tegutseb autonoomselt viisil, kuidas teised mudelid ei tee. Hind on sarnane Claude Haiku’le.

| Platvorm | `PLATFORM=` | Vaike mudel | Kust saada võtme |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI ühilduv (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (mitme pakkuja) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tööriist** (claude -p, ollama…) | `cli` | (käsk) | — |

**Kimi K2.5 `.env` näide:**
```env
PLATFORM=kimi
API_KEY=sk-...   # platvormilt moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` näide:**
```env
PLATFORM=glm
API_KEY=...   # platvormilt api.z.ai
MODEL=glm-4.6v   # visioonitoega; glm-4.7 / glm-5 = ainult tekst
AGENT_NAME=Yukine
```

**Google Gemini `.env` näide:**
```env
PLATFORM=gemini
API_KEY=AIza...   # platvormilt aistudio.google.com
MODEL=gemini-2.5-flash  # või gemini-2.5-pro suuremate võimalustega
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` näide:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # platvormilt openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # valikuline: täpsusta mudel
AGENT_NAME=Yukine
```

> **Märkus:** Kohalikud/NVIDIA mudeleid keelamiseks ära lihtsalt määrake `BASE_URL` kohalikuks lõpp-punktiks nagu `http://localhost:11434/v1`. Kasutage pigem pilveteenuseid.

**CLI tööriist `.env` näide:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — ei {}, prompt läheb stdin kaudu
```

---

## MCP Serverid

familiar-ai suudab ühenduda mis tahes [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serveriga. See võimaldab sul lisada välist mälu, failisüsteemi juurdepääsu, veebipõhiseid otsinguid või mis tahes muud tööriista.

Konfigureeri serverid `~/.familiar-ai.json` failis (sama formaat nagu Claude Code):

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

Kaks transporditüüpi on toetatud:
- **`stdio`**: käivita kohalik alamprotsess (`command` + `args`)
- **`sse`**: ühendus HTTP+SSE serveriga (`url`)

Ümberkirjutamiseks konfigura faili asukoht `MCP_CONFIG=/path/to/config.json`.

---

## Riistvara

familiar-ai töötab igasuguse riistvara või isegi ilma selleta.

| Osa | Mida see teeb | Näide | Nõutav? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kaamera | Silmad + kael | Tapo C220 (~30$) | **Soovitatav** |
| USB veebikaamera | Silmad (paigaldatud) | Mis tahes UVC kaamera | **Soovitatav** |
| Robot tolmuimeja | Jalad | Mis tahes Tuya ühilduv mudel | Ei |
| PC / Raspberry Pi | Aju | Mis tahes, mis töötab Pythoniga | **Jah** |

> **Kaamera on tugevalt soovitatav.** Ilma selleta saab familiar-ai siiski rääkida — kuid see ei näe maailma, mis on natuke kogu idee mõte.

### Minimaalne seadistus (ilma riistvarata)

Kas soovid vaid proovida? Sul on vaja ainult API võtit:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Käivita `./run.sh` ja hakka vestlema. Lisa riistvara, kui vajad.

### Wi-Fi PTZ kaamera (Tapo C220)

1. Tapo rakenduses: **Seaded → Täiustatud → Kaamera konto** — loo kohalik konto (mitte TP-Link konto)
2. Leia kaamerase IP oma ruuteri seadmete loendist
3. Määra `.env` failis:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Hääl (ElevenLabs)

1. Saa API võti [elevenlabs.io](https://elevenlabs.io/)
2. Määra `.env` failis:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # valikuline, kasutab vaikehäält, kui jäetakse vahele
   ```

Heli esitamiseks on kaks sihtkohta, mida kontrollitakse `TTS_OUTPUT` abil:

```env
TTS_OUTPUT=local    # PC kõlar (vaikimisi)
TTS_OUTPUT=remote   # ainult kaamera kõlar
TTS_OUTPUT=both     # kaamera kõlar + PC kõlar samal ajal
```

#### A) Kaamera kõlar (go2rtc kaudu)

Määra `TTS_OUTPUT=remote` (või `both`). Nõuab [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Laadi alla binaarne fail [väljalaske lehelt](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Aseta ja nimeta ümber:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x vajalik

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Loo samaaegselt: `go2rtc.yaml` samas kataloogis:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Kasuta kohaliku kaamera konto mandaate (mitte TP-Linki pilvekonto).

4. familiar-ai käivitab go2rtc automaatselt käivitamisel. Kui su kaamera toetab kahelise heli (tagasiots), siis hääl mängib kaamera kõlarist.

#### B) Kohalik PC kõlar

Vaikimisi (`TTS_OUTPUT=local`). Katsetatakse mängijaid järjekorras: **paplay** → **mpv** → **ffplay**. Kasutatakse ka varukoha jaoks, kui `TTS_OUTPUT=remote` ja go2rtc pole saadaval.

| OS | Installi |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (või `paplay` läbi `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — seada `PULSE_SERVER=unix:/mnt/wslg/PulseServer` `.env` failis |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — laadi alla ja lisa PATH-i, **või** `winget install ffmpeg` |

> Kui mingit helimängijat pole saadaval, genereeritakse siiski kõnet — kuid see lihtsalt ei mängi.

### Häälesisend (Realtime STT)

Määra `.env` failis `REALTIME_STT=true`, et lubada alati aktiivne käed-vabad häälesisend:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # sama võti nagu TTS
```

familiar-ai voogesitab mikrofoni heli ElevenLabs Scribe v2-le ja automaatselt salvestab transkriptsioonid, kui sa rääkimise peatad. Nuppu vajutada ei ole vajalik. Kooseksisteerib push-to-talk režiimi (Ctrl+T) kõrval.

---

## TUI

familiar-ai sisaldab terminali UI-d, mis on loodud [Textual](https://textual.textualize.io/) abil:

- Keritav vestluse ajalugu reaalajas tekstivooluga
- Vahekaartide täiendamine `/quit`, `/clear` jaoks
- Intrigeeri agenti keset mõtlemist kirjutades
- **Vestluse logi** salvestatakse automaatselt `~/.cache/familiar-ai/chat.log`

Logi jälgimiseks teises terminalis (kasulik kopeerimiseks ja kleepimiseks):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Isiksus (ME.md)

Sinu tuttava isiksus elab failis `ME.md`. See fail on gitignore'is — see on ainult sinu oma.

Vaata [`persona-template/en.md`](./persona-template/en.md) näidisena või [`persona-template/ja.md`](./persona-template/ja.md) jaapani versioonile.

---

## Korduma Kippuvad Küsimused

**Q: Kas see töötab ilma GPU-ta?**
Jah. Embedding-mudel (multilingual-e5-small) töötab hästi CPU-l. GPU teeb selle kiiremaks, kuid pole vajalik.

**Q: Kas ma saan kasutada muud kaamerat kui Tapo?**
Mis tahes kaamera, mis toetab ONVIF + RTSP peaks toimima. Tapo C220 on see, millega testisime.

**Q: Kas minu andmed saadetakse kusagile?**
Pildid ja tekst saadetakse sinu valitud LLM API-le töötlemiseks. Mälestused salvestatakse kohalikult `~/.familiar_ai/`.

**Q: Miks kirjutab agent `（...）` asemel räägib?**
Veendu, et `ELEVENLABS_API_KEY` on seadistatud. Ilma selleta on hääl keelatud ja agent tagastab teksti.

## Tehniline taust

Uudis, kuidas see töötab? Vaata [docs/technical.md](./docs/technical.md) uurimist ja disainilahendusi, mis seisavad familiar-ai taga — ReAct, SayCan, Reflexion, Voyager, soovisüsteem ja palju muud.

---

## Panustamine

familiar-ai on avatud katse. Kui mõni sellest kõnetab sind — tehniliselt või filosoofiliselt — on panused väga teretulnud.

**Hea koht alustamiseks:**

| Valdkond | Mida on vajaka |
|------|---------------|
| Uus riistvara | Toetuse saamiseks rohkem kaameraid (RTSP, IP veebikaamera), mikrofone, tegevustooturid |
| Uued tööriistad | Veebipõhine otsing, kodua automatiseerimine, kalendrid, mis tahes MCP kaudu |
| Uued tagaplaanid | Mis tahes LLM või kohaliku mudeli, mis sobib `stream_turn` liidese jaoks |
| Isiksuse mallid | ME.md mallid erinevatele keeltele ja isiksustele |
| Uuring | Paremad soovi mudelid, mälu toomine, meeleolu teooria esilekutsumine |
| Dokumentatsioon | Õpetused, juhised, tõlked |

Vaata [CONTRIBUTING.md](./CONTRIBUTING.md) arendamise seadistamiseks, koodistiili ja PR juhiste jaoks.

Kui sa ei tea, kust alustada, [ava probleem](https://github.com/lifemate-ai/familiar-ai/issues) — olen rõõmus, et saan sind õiges suunas suunata.

---

## Litsents

[MIT](./LICENSE)
