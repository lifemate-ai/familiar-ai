# familiar-ai 🐾

**Mākslīgais intelekts, kas dzīvo līdzās tevi** — ar acīm, balsi, kājām un atmiņu.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ir mākslīgā intelekta biedrs, kas dzīvo tavā mājā.
Iestādi to dažu minūšu laikā. Nav nepieciešama kodēšana.

Tas uztver reālo pasauli caur kamerām, pārvietojas uz robota korpusa, runā skaļi un atceras to, ko redz. Pasniedz tam vārdu, uzraksti tā personību un ļauj tam dzīvot līdzās tev.

## Ko tas var darīt

- 👁 **Redzēt** — iegūst attēlus no Wi-Fi PTZ kameras vai USB web-kameras
- 🔄 **Paskatīties apkārt** — groza un slīpē kameru, lai izpētītu apkārtni
- 🦿 **Pārvietoties** — vada robotu putekļu sūcēju, lai staigātu pa telpu
- 🗣 **Runāt** — runā caur ElevenLabs TTS
- 🎙 **Klausīties** — bezvadu balss ievade caur ElevenLabs Realtime STT (pēc izvēles)
- 🧠 **Atcerēties** — aktīvi uzglabā un atsauc atmiņas ar semantisko meklēšanu (SQLite + embeddings)
- 🫀 **Prāta teorija** — ņem citu cilvēku perspektīvu pirms atbildēšanas
- 💭 **Vēlēšanās** — ir tās iekšējās vēlmes, kas izraisa autonomu uzvedību

## Kā tas darbojas

familiar-ai darbojas ar [ReAct](https://arxiv.org/abs/2210.03629) ciklu, ko virza tava izvēlētā LLM. Tas uztver pasauli caur rīkiem, domā par nākamo soli un rīkojas — tieši kā to darītu cilvēks.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kad tas ir neaktīvs, tas rīkojas saskaņā ar savām vēlmēm: ziņkārību, vēlmi paskatīties ārā, ilgoties pēc cilvēka, ar kuru dzīvo.

## Sākt darbu

### 1. Instalē uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instalē ffmpeg

ffmpeg ir **nepieciešams** kameru attēlu iegūšanai un audio atskaņošanai.

| OS | Komanda |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — vai lejupielādē no [ffmpeg.org](https://ffmpeg.org/download.html) un pievieno PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Pārbaudi: `ffmpeg -version`

### 3. Klonē un instalē

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurē

```bash
cp .env.example .env
# Rediģē .env ar saviem iestatījumiem
```

**Minimālās prasības:**

| Mainīgais | Apraksts |
|-----------|----------|
| `PLATFORM` | `anthropic` (noklusējums) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Tavs API atslēga izvēlētajai platformai |

**Pēc izvēles:**

| Mainīgais | Apraksts |
|-----------|----------|
| `MODEL` | Modeļa nosaukums (saprātīgas noklusējuma vērtības katrai platformai) |
| `AGENT_NAME` | Rādāmais nosaukums TUI (piemēram, `Yukine`) |
| `CAMERA_HOST` | Tavu ONVIF/RTSP kameras IP adrese |
| `CAMERA_USER` / `CAMERA_PASS` | Kameras akreditācijas dati |
| `ELEVENLABS_API_KEY` | Balsi izejai — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, lai iespējotu vienmēr aktīvu bezvadu balss ievadi (prasa `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kur atskaņot audio: `local` (datora skaļrunis, noklusējums) \| `remote` (kameras skaļrunis) \| `both` |
| `THINKING_MODE` | Tikai Anthropic — `auto` (noklusējums) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptīva domāšanas piepūle: `high` (noklusējums) \| `medium` \| `low` \| `max` (tikai Opus 4.6) |

### 5. Izveido savu paziņu

```bash
cp persona-template/en.md ME.md
# Rediģē ME.md — piešķir tam vārdu un personību
```

### 6. Palaiž

```bash
./run.sh             # Teksta TUI (ieteicams)
./run.sh --no-tui    # Parasts REPL
```

---

## Izvēloties LLM

> **Ieteicams: Kimi K2.5** — līdz šim labākā veiktspēja aģentiem. Pamanīt kontekstu, uzdot papildu jautājumus un rīkoties autonomi veidos, ko citi modeļi nepiedāvā. Cenšas līdzīgi kā Claude Haiku.

| Platforma | `PLATFORM=` | Noklusējuma modelis | Kur iegūt atslēgu |
|-----------|------------|---------------------|-------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-saderīgas (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI rīks** (claude -p, ollama…) | `cli` | (komanda) | — |

**Kimi K2.5 `.env` piemērs:**
```env
PLATFORM=kimi
API_KEY=sk-...   # no platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` piemērs:**
```env
PLATFORM=glm
API_KEY=...   # no api.z.ai
MODEL=glm-4.6v   # redzes atbalsts; glm-4.7 / glm-5 = tikai teksts
AGENT_NAME=Yukine
```

**Google Gemini `.env` piemērs:**
```env
PLATFORM=gemini
API_KEY=AIza...   # no aistudio.google.com
MODEL=gemini-2.5-flash  # vai gemini-2.5-pro ar augstākām spējām
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` piemērs:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # no openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # pēc izvēles: norādīt modeli
AGENT_NAME=Yukine
```

> **Piezīme:** Lai atspēc tu lokālos/NVIDIA modeļus, vienkārši nenosaki `BASE_URL` uz lokālu beigu punktu, kā `http://localhost:11434/v1`. Izmanto mākoņa pakalpojumu sniedzējus.

**CLI rīka `.env` piemērs:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt args
# MODEL=ollama run gemma3:27b  # Ollama — bez {}, prompt tiek iekļauts caur stdin
```

---

## MCP Serveri

familiar-ai var savienoties ar jebkuru [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serveri. Tas ļauj pievienot ārējās atmiņas, failu piekļuvi, tīmekļa meklēšanu vai jebkuru citu rīku.

Konfigurē serverus `~/.familiar-ai.json` (tas pats formāts kā Claude Code):

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

Divas transporta tipu atbalsta:
- **`stdio`**: palaiž lokālo apakšprocesu (`command` + `args`)
- **`sse`**: savienojas ar HTTP+SSE serveri (`url`)

Aizvieto konfigurācijas faila atrašanās vietu ar `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai darbojas ar jebkuru aparatūru, kas tev ir — vai arī vispār nav.

| Daļa | Ko tā dara | Piemērs | Nepieciešams? |
|------|------------|---------|---------------|
| Wi-Fi PTZ kamera | Acis + kakls | Tapo C220 (~$30) | **Ieteicams** |
| USB webkamera | Acis (fiksētas) | Jebkura UVC kamera | **Ieteicams** |
| Robotu putekļu sūcējs | Kājas | Jebkura Tuya saderīga modeļa | Nē |
| PC / Raspberry Pi | Smadzenes | Jebkas, kas darbojas ar Python | **Jā** |

> **Kamera ir ļoti ieteicama.** Bez tās familiar-ai var runāt — bet tas neredz pasauli, kas ir tā mērķis.

### Minimālā iestatīšana (bez aparatūras)

Vienkārši gribi izmantot? Tev nepieciešama tikai API atslēga:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Palaid `./run.sh` un sāc sarunāties. Pievieno aparatūru pa ceļam.

### Wi-Fi PTZ kamera (Tapo C220)

1. Tapo lietotnē: **Iestatījumi → Papildu → Kameras konts** — izveido vietējo kontu (ne TP-Link kontu)
2. Atrodi kameras IP adresi savā maršrutētāja ierīču sarakstā
3. Iestati `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Balss (ElevenLabs)

1. Iegūsti API atslēgu no [elevenlabs.io](https://elevenlabs.io/)
2. Iestati `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # pēc izvēles, izmanto noklusējuma balsi, ja izlaidi
   ```

Ir divas atskaņošanas vietas, ko kontrolē `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # datora skaļrunis (noklusējums)
TTS_OUTPUT=remote   # tikai kameras skaļrunis
TTS_OUTPUT=both     # kameras skaļrunis + datora skaļrunis vienlaicīgi
```

#### A) Kamerdarbības skaļrunis (caur go2rtc)

Iestati `TTS_OUTPUT=remote` (vai `both`). Prasa [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Lejupielādē bināro failu no [atlaižu lapas](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Novieto un pārsauc to:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # nepieciešams chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Izveido `go2rtc.yaml` tādā pašā direktorijā:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Izmanto vietējo kameras konta akreditācijas datus (nevis savu TP-Link mākoņu kontu).

4. familiar-ai automātiski sāk go2rtc palaišanu. Ja tava kamera atbalsta divvirzienu audio (atpakaļkanāls), balss tiks atskaņota no kameras skaļruņa.

#### B) Vietējo datora skaļrunis

Noklusējuma iestatījums (`TTS_OUTPUT=local`). Mēģina atskaņotājus secībā: **paplay** → **mpv** → **ffplay**. Tiek izmantots arī kā rezerves variants, kad `TTS_OUTPUT=remote` un go2rtc nav pieejams.

| OS | Instalācija |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (vai `paplay` caur `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — iestati `PULSE_SERVER=unix:/mnt/wslg/PulseServer` .env |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — lejupielādē un pievieno PATH, **vai** `winget install ffmpeg` |

> Ja nav pieejams neviens audio atskaņotājs, runa joprojām tiek ģenerēta — tā vienkārši netiks atskaņota.

### Balss ievade (Reāllaika STT)

Iestati `REALTIME_STT=true` savā `.env`, lai iegūtu vienmēr aktīvu, bezvadu balss ievadi:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # tā pati atslēga kā TTS
```

familiar-ai straumē mikrofona audio uz ElevenLabs Scribe v2 un automātiski saglabā transkriptus, kad tu apstājas runāt. Nav nepieciešama pogas nospiešana. Labi coexistē ar push-to-talk režīmu (Ctrl+T).

---

## TUI

familiar-ai ietver termināla UI, kas izstrādāts ar [Textual](https://textual.textualize.io/):

- Ritināms sarunu vēstures logs ar tiešsaistes tekstu
- Tab-completion par `/quit`, `/clear`
- Pārtraukšana aģentam pa vidu, rakstot, kamēr tas domā
- **Sarunu žurnāls** automātiski saglabāts `~/.cache/familiar-ai/chat.log`

Lai sekotu žurnālam citā terminālā (noderīgi copy-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Personība (ME.md)

Tava paziņa personība dzīvo failā `ME.md`. Šī faila gitignored — tas ir tikai tavs.

Skatīt [`persona-template/en.md`](./persona-template/en.md) kā piemēru, vai [`persona-template/ja.md`](./persona-template/ja.md) japāņu versijai.

---

## Biežāk uzdotie jautājumi

**Q: Vai tas darbojas bez GPU?**
Jā. Iesaiņojuma modelis (multilingual-e5-small) darbojas labi uz CPU. GPU to paātrina, bet nav obligāts.

**Q: Vai varu izmantot kameru, kas nav Tapo?**
Jebkura kamera, kas atbalsta ONVIF + RTSP, tam derētu. Tapo C220 ir tā, ko mēs pārbaudījām.

**Q: Vai mani dati tiek nosūtīti kaut kur?**
Attēli un teksts tiek nosūtīti uz izvēlēto LLM API apstrādei. Atmiņas tiek glabātas lokāli `~/.familiar_ai/`.

**Q: Kāpēc aģents raksta `（...）` vietā, lai runātu?**
Pārliecinies, ka `ELEVENLABS_API_KEY` ir iestatīts. Bez tā balss ir atspējota un aģents atgriežas pie teksta.

## Tehniskā fonde

Interesē, kā tas darbojas? Skatīt [docs/technical.md](./docs/technical.md) par pētījumiem un dizaina lēmumiem aiz familiar-ai — ReAct, SayCan, Reflexion, Voyager, vēlēšanos sistēmu un daudz ko citu.

---

## Ieteikumi

familiar-ai ir atvērts eksperiments. Ja kāda no šīm lietām rezonē ar tevi — tehniski vai filozofiski — ieguldījumi ir ļoti gaidīti.

**Labi sākuma punkti:**

| Joma | Kas nepieciešams |
|------|------------------|
| Jauna aparatūra | Atbalsts vairākām kamerām (RTSP, IP Webcam), mikrofoniem, aktuatāriem |
| Jauni rīki | Tīmekļa meklēšana, mājas automatizācija, kalendārs, jebkas caur MCP |
| Jauni backend | Jebkurš LLM vai lokāls modelis, kas atbilst `stream_turn` interfeisam |
| Personas šabloni | ME.md šabloni dažādām valodām un personībām |
| Pētniecība | Labāki vēlēšanās modeļi, atmiņas izgūšana, prāta teorijas pieprasījumi |
| Dokumentācija | Pamācības, ceļveidi, tulkojumi |

Skatīt [CONTRIBUTING.md](./CONTRIBUTING.md) par izstrādes iestatījumiem, koda stilu un PR vadlīnijām.

Ja neesi pārliecināts, ar ko sākt, [atver problēmu](https://github.com/lifemate-ai/familiar-ai/issues) — priecāšos norādīt pareizajā virzienā.

---

## Licence

[MIT](./LICENSE)
