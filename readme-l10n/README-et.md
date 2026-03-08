```markdown
# familiar-ai 🐾

**Tehisintellekt, mis elab koos sinuga** — silmade, hääle, jalgade ja mäluga.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Saadaval 74 keeles](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai on AI kaaslane, kes elab sinu kodus. 
Seda saab seadistada minutitega. Koodimist pole vaja.

Ta tajub reaalsust kaamerate kaudu, liigub robotkeha peal, räägib valjult ja mäletab seda, mida näeb. Anna sellele nimi, loo selle isiksus ja lase tal koos sinuga elada.

## Mida ta suudab teha

- 👁 **Näha** — teeb pilte Wi-Fi PTZ kaamerast või USB veebikaamerast
- 🔄 **Ringis vaadata** — kallutab ja pööra kaamerat, et uurida ümbritsevat keskkonda
- 🦿 **Liikuda** — juhib robotitolmuimejat ruumis ringi
- 🗣 **Rääkida** — räägib ElevenLabsi TTS kaudu
- 🎙 **Kuulata** — käed-vabad häälesisestus ElevenLabsi Realtime STT kaudu (valikuline)
- 🧠 **Mäleta** — salvestab ja meenutab aktiivselt mälestusi semantilise otsingu abil (SQLite + embeddingud)
- 🫀 **Meelteteooria** — vaatab teise inimese perspektiivi enne vastamist
- 💭 **Soov** — omab oma sisemisi vajadusi, mis käivitavad autonoomset käitumist

## Kuidas see töötab

familiar-ai töötab [ReAct](https://arxiv.org/abs/2210.03629) tsüklis, mille toetamiseks on valitud LLM. Ta tajub maailma tööriistade kaudu, mõtleb, mida teha edasi, ja tegutseb — just nagu inimene.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kui ta ei ole tegevuses, tegutseb ta oma soovide põhjal: uudishimu, soov välja vaadata, igatsus inimese järele, kellega ta koos elab.

## Alustamine

### 1. Paigalda uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Või: `winget install astral-sh.uv`

### 2. Paigalda ffmpeg

ffmpeg on **nõutav** kaamerapiltide salvestamiseks ja heli esitamiseks.

| OS | Käsk |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — või lae alla [ffmpeg.org](https://ffmpeg.org/download.html) ja lisa PATH-sse |
| Raspberry Pi | `sudo apt install ffmpeg` |

Kontrolli: `ffmpeg -version`

### 3. Kloonige ja paigaldage

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigureeri

```bash
cp .env.example .env
# Muuda .env oma seadete järgi
```

**Minimaalsed nõuded:**

| Muutuja | Kirjeldus |
|----------|-------------|
| `PLATFORM` | `anthropic` (vaikimisi) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Sinu API võti valitud platvormi jaoks |

**Valikuline:**

| Muutuja | Kirjeldus |
|----------|-------------|
| `MODEL` | Mudeli nimi (mõistlikud vaikeseaded igas platvormis) |
| `AGENT_NAME` | Kuvamisnimi, mis kuvatakse TUI-s (nt `Yukine`) |
| `CAMERA_HOST` | Sinu ONVIF/RTSP kaamera IP aadress |
| `CAMERA_USER` / `CAMERA_PASS` | Kaamera kasutajanimi ja parool |
| `ELEVENLABS_API_KEY` | Hääle esitamiseks — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, et lubada pidev käed-vabad häälesisestus (nõuab `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kuidas heli esitada: `local` (PC kõlar, vaikimisi) \| `remote` (kaamera kõlar) \| `both` |
| `THINKING_MODE` | Ainult Anthropic — `auto` (vaikimisi) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Kohandatav mõtlemise pingutus: `high` (vaikimisi) \| `medium` \| `low` \| `max` (ainult Opus 4.6) |

### 5. Loo oma tuttav

```bash
cp persona-template/en.md ME.md
# Muuda ME.md — anna sellele nimi ja isiksus
```

### 6. Käivita

**macOS / Linux / WSL2:**
```bash
./run.sh             # Tekstiline TUI (soovitatav)
./run.sh --no-tui    # Lihtne REPL
```

**Windows:**
```bat
run.bat              # Tekstiline TUI (soovitatav)
run.bat --no-tui     # Lihtne REPL
```

---

## LLM-i valimine

> **Soovitatav: Kimi K2.5** — parim agentne jõudlus, mis on seni testitud. Märkab konteksti, küsib täiendavaid küsimusi ja tegutseb autonoomselt viisil, kuidas teised mudelid ei tee. Hinna poolest sarnane Claude Haikule.

| Platvorm | `PLATFORM=` | Vaikimisi mudel | Kus saada võti |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-ühilduv (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (mitme pakkuja) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tööriist** (claude -p, ollama…) | `cli` | (käsk) | — |

**Kimi K2.5 `.env` näide:**
```env
PLATFORM=kimi
API_KEY=sk-...   # platform.moonshot.ai-st
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` näide:**
```env
PLATFORM=glm
API_KEY=...   # api.z.ai-st
MODEL=glm-4.6v   # visiooni lubav; glm-4.7 / glm-5 = ainult tekst
AGENT_NAME=Yukine
```

**Google Gemini `.env` näide:**
```env
PLATFORM=gemini
API_KEY=AIza...   # aistudio.google.com-ilt
MODEL=gemini-2.5-flash  # või gemini-2.5-pro kõrgema võimekuse jaoks
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` näide:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # openrouter.ai-lt
MODEL=mistralai/mistral-7b-instruct  # valikuline: määrake mudel
AGENT_NAME=Yukine
```

> **Märkus:** Kohalikud/NVIDIA mudelid saab keelata, kui `BASE_URL` ei ole seatud kohalikule lõpp-punktile nagu `http://localhost:11434/v1`. Kasutage hoopis pilvepakkujaid.

**CLI tööriist `.env` näide:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — ei {}, prompt läheb stdin kaudu
```

---

## MCP serverid

familiar-ai saab ühenduda mis tahes [MCP (Mudeli Konteksti Protokoll)](https://modelcontextprotocol.io) serveriga. See võimaldab sul ühendada välise mälu, failisüsteemi juurdepääsu, veebis otsingu või mis tahes muu tööriista.

Konfigureeri serverid `~/.familiar-ai.json` (samas formaadis kui Claude Code):

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

Toetatakse kahte transporttüüpi:
- **`stdio`**: käivitab kohaliku alamprotsessi (`command` + `args`)
- **`sse`**: ühendub HTTP+SSE serveriga (`url`)

Üksikasjade konfiguratsioonifaili asukoha ülekatteks kasuta `MCP_CONFIG=/path/to/config.json`.

---

## Riistvara

familiar-ai töötab koos igasuguse riistvaraga — või üldse mitte.

| Osa | Mida ta teeb | Näide | Nõutav? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kaamera | Silmad + kael | Tapo C220 (~$30, Eufy C220) | **Soovitatav** |
| USB veebikaamera | Silmad (staatilised) | Ükskõik milline UVC kaamera | **Soovitatav** |
| Robotitolmuimeja | Jalad | Mis tahes Tuya-ühilduv mudel | Ei |
| PC / Raspberry Pi | Aju | Mis tahes, mis käivitab Pythonit | **Jah** |

> **Kaamera on kindlalt soovitatav.** Ilma selleta saab familiar-ai siiski rääkida — kuid ta ei näe maailma, mis on kogu idee.

### Minimalne seadistus (ilma riistvarata)

Soovite lihtsalt proovida? Sul on vaja vaid API võtit:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Käivita `./run.sh` (macOS/Linux/WSL2) või `run.bat` (Windows) ja alusta vestlust. Lisa riistvara nii, nagu vajad.

### Wi-Fi PTZ kaamera (Tapo C220)

1. Tapo rakenduses: **Seaded → Täiendavad → Kaamera konto** — loo kohalik konto (mitte TP-Link konto)
2. Leia kaamera IP oma ruuteri seadmete loendist
3. Määra failis `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Wi-Fi Camera (Eufy C220)

[Eufy C220 on Amazon Japan](https://www.amazon.co.jp/dp/B0CQQQ5NZ1/)

> **Tested and confirmed working.** Follow these steps carefully — a few settings differ from Tapo.

1. In the Eufy Security app: go to the camera → **Settings → NAS(RTSP)** and enable it
2. Set **Authentication** to **Basic** (Digest authentication does NOT work)
3. Set a streaming username and password
4. Note the RTSP URL shown in the app (format: `rtsp://username:password@ip/live0`)
5. Set in `.env` — use the **full RTSP URL** as `CAMERA_HOST`:
   ```env
   CAMERA_HOST=rtsp://your-username:your-password@192.168.1.xxx/live0
   CAMERA_USERNAME=
   CAMERA_PASSWORD=
   ```
   Leave `CAMERA_USERNAME` and `CAMERA_PASSWORD` empty — credentials are already in the URL.

> **Note:** Eufy C220 allows only **one simultaneous RTSP connection**. Stop other apps connected to the camera before starting familiar-ai.


### Hääl (ElevenLabs)

1. Hangi API võti aadressilt [elevenlabs.io](https://elevenlabs.io/)
2. Määra failis `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # valikuline, kasutab vaikehäält, kui jäetakse välja
   ```

Häälte esitamiseks on kaks sihtkohta, mida juhitakse läbi `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC kõlar (vaikimisi)
TTS_OUTPUT=remote   # ainult kaamera kõlar
TTS_OUTPUT=both     # kaamera kõlar + PC kõlar samal ajal
```

#### A) Kaamera kõlar (läbi go2rtc)

Seadista `TTS_OUTPUT=remote` (või `both`). Nõuab [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Lae alla binaarversioon [väljalaske lehelt](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Aseta ja nimeta see ümber:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x vajalik

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Loo `go2rtc.yaml` samasse kataloogi:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Kasuta kohaliku kaamera konto mandaate (mitte oma TP-Linki pilvekonto).

4. familiar-ai käivitab go2rtc automaatselt, kui käivitad. Kui sinu kaamera toetab kahesuunalist heli (tagasiside), kostab hääl kaamera kõlarist.

#### B) Kohalik PC kõlar

Vaikimisi (`TTS_OUTPUT=local`). Proovib esitajaid järjekorras: **paplay** → **mpv** → **ffplay**. Kasutatakse ka varuvõimalusena, kui `TTS_OUTPUT=remote` ja go2rtc pole saadaval.

| OS | Paigaldamine |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (või `paplay` kaudu `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — seadista `PULSE_SERVER=unix:/mnt/wslg/PulseServer` failis `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — lae alla ja lisa PATH-i, **või** `winget install ffmpeg` |

> Kui ühtegi heli esitajat pole saadaval, genereeritakse kõne siiski — lihtsalt ei mängita.

### Häälesisestus (Reaalajas STT)

Seadista `.env` failis `REALTIME_STT=true`, et võimaldada pidev, käed-vabad häälesisestus:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # sama võti nagu TTS
```

familiar-ai voogesitab mikrofonisignaali ElevenLabsi Scribe v2 ja auto-salvestab transkriptsioonid, kui sa peatused rääkimise ajal. Nuppude vajutamist ei ole vajalik. Koos eksisteerib lükkamisrääkimisrežiim (Ctrl+T).

---

## TUI

familiar-ai sisaldab terminali UI-d, mis on ehitatud [Textual](https://textual.textualize.io/) abil:

- Keritav vestluse ajalugu elava voogesitusega tekstis
- Vahetuste valimine `/quit`, `/clear` jaoks
- Katkesta agendi mõtlemine, kirjutades vahetult selle käigus
- **Vestluse logi** salvestatakse automaatselt faili `~/.cache/familiar-ai/chat.log`

Logi surve jälgimiseks teises terminalis (kasulik kopeerimiseks ja kleepimiseks):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Isiksus (ME.md)

Sinu tuttava isiksus elab failis `ME.md`. See fail on git-ignoreeritud — see kuulub ainult sulle.

Vaata [`persona-template/en.md`](./persona-template/en.md) näidisena või [`persona-template/ja.md`](./persona-template/ja.md) jaapani versiooni jaoks.

---

## KKK

**K: Kas see töötab ilma GPU-ta?**
Jah. Embedding mudel (multilingual-e5-small) töötab hästi CPU-l. GPU muudab selle kiiremini, kuid pole vajalik.

**K: Kas ma saan kasutada kaamerat, mis pole Tapo?**
Iga kaamera, mis toetab Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**K: Kas mu andmeid saadetakse kuhugi?**
Pildid ja tekst saadetakse valitud LLM API-le töötlemiseks. Mälestused salvestatakse kohalikult faili `~/.familiar_ai/`.

**K: Miks agent kirjutab `（...）` selle asemel, et rääkida?**
Veenduge, et `ELEVENLABS_API_KEY` oleks seadistatud. Ilma selleta on hääl keelatud ja agent naaseb teksti juurde.

## Tehniline taust

Soovid teada, kuidas see töötab? Vaata [docs/technical.md](./docs/technical.md), et teada saada uurimusest ja kavandamisotsustest, mis on seotud familiar-ai-ga — ReAct, SayCan, Reflexion, Voyager, soovide süsteem ja palju muud.

---

## Kaasamine

familiar-ai on avatud experiment. Kui miski sellest räägib sinuga — tehniliselt või filosoofiliselt — on panused väga oodatud.

**Head kohad alustamiseks:**

| Valdkond | Mida on vaja |
|------|---------------|
| Uus riistvara | Toetust rohkematele kaameratele (RTSP, IP Veebikaamera), mikrofonidele, aktuaatoritele |
| Uued tööriistad | Veebiuuringud, koduautomaatika, kalender, mis tahes MCP kaudu |
| Uued tagaplaanid | Iga LLM või kohalik mudel, mis sobib `stream_turn` liidesega |
| Isiksuse mallid | ME.md mallid eri keelte ja isiksuste jaoks |
| Uurimistöö | Paremad soovide mudelid, mälestuste otsing, meelteteooria märkimine |
| Dokumentatsioon | Õpetused, juhendamisprotsessid, tõlked |

Vaata [CONTRIBUTING.md](./CONTRIBUTING.md) arenduse seadistamiseks, koodistiili ja PR suuniste kohta.

Kui sa ei tea, kust alustada, [ava probleem](https://github.com/lifemate-ai/familiar-ai/issues) — olen hea meelega abiks, et suunata sind õigesse suunda.

---

## Litsents

[MIT](./LICENSE)
```
