# familiar-ai 🐾

**Umjetna inteligencija koja živi uz vas** — s očima, glasom, nogama i memorijom.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI pratitelj koji živi u vašem domu. 
Postavite ga za nekoliko minuta. Nema potrebe za kodiranjem.

Perceptira stvarni svijet kroz kamere, kreće se na robotskom tijelu, govori na glas, i pamti što vidi. Dajte mu ime, napišite njegovu osobnost i pustite ga da živi s vama.

## Što može raditi

- 👁 **Vidjeti** — hvata slike s Wi-Fi PTZ kamere ili USB web kamere
- 🔄 **Pogledati oko sebe** — pomiče i naginje kameru da istraži okolinu
- 🦿 **Kretati se** — upravlja robotskim usisavačem da se kreće po prostoriji
- 🗣 **Govoriti** — govori putem ElevenLabs TTS
- 🎙 **Slušati** — glasovni ulaz bez ruku putem ElevenLabs Realtime STT (dobrovoljno)
- 🧠 **Pamtiti** — aktivno pohranjuje i prisjeća se uspomena s semantičkom pretragom (SQLite + ugradnje)
- 🫀 **Teorija uma** — uzima perspektivu druge osobe prije nego što odgovori
- 💭 **Želja** — ima vlastite unutarnje nagone koji pokreću autonomno ponašanje

## Kako to funkcionira

familiar-ai pokreće [ReAct](https://arxiv.org/abs/2210.03629) petlju koju pokreće vaš izbor LLM-a. Perceptira svijet kroz alate, razmišlja o sljedećem koraku i djeluje — baš kao što bi to učinila osoba.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kada je odvojena, djeluje prema vlastitim željama: znatiželji, želji da pogleda van, nedostajanju osobe s kojom živi.

## Kako započeti

### 1. Instalirajte uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instalirajte ffmpeg

ffmpeg je **uz zahtijev** za hvatanje slike s kamere i reprodukciju zvuka.

| OS | Komanda |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ili preuzmite s [ffmpeg.org](https://ffmpeg.org/download.html) i dodajte u PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Provjerite: `ffmpeg -version`

### 3. Klonirajte i instalirajte

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurirajte

```bash
cp .env.example .env
# Uredite .env sa svojim postavkama
```

**Minimalno potrebno:**

| Varijabla | Opis |
|-----------|------|
| `PLATFORM` | `anthropic` (zadano) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Vaš API ključ za odabranu platformu |

**Opcionalno:**

| Varijabla | Opis |
|-----------|------|
| `MODEL` | Naziv modela (razumljivi zadani postavci po platformi) |
| `AGENT_NAME` | Prikazano ime u TUI (npr. `Yukine`) |
| `CAMERA_HOST` | IP adresa vaše ONVIF/RTSP kamere |
| `CAMERA_USER` / `CAMERA_PASS` | Akreditivi za kameru |
| `ELEVENLABS_API_KEY` | Za glasovni izlaz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` za omogućavanje trajnog glasovnog ulaza bez ruku (treba `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Gdje reproducirati audio: `local` (PC zvučnik, zadano) \| `remote` (zvučnik kamere) \| `both` |
| `THINKING_MODE` | Samo Anthropic — `auto` (zadano) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Prilagodljivi napor razmišljanja: `high` (zadano) \| `medium` \| `low` \| `max` (samo Opus 4.6) |

### 5. Stvorite svog prijatelja

```bash
cp persona-template/en.md ME.md
# Uredite ME.md — dajte mu ime i osobnost
```

### 6. Pokrenite

```bash
./run.sh             # Tekstualni TUI (preporučeno)
./run.sh --no-tui    # Plain REPL
```

---

## Odabir LLM-a

> **Preporučeno: Kimi K2.5** — najbolja izvedba agenata testirana do sada. Primjećuje kontekst, postavlja dodatna pitanja i autonomno djeluje na načine na koje drugi modeli ne. Cijenjen je slično kao Claude Haiku.

| Platforma | `PLATFORM=` | Zadani model | Gdje dobiti ključ |
|-----------|-------------|--------------|------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibilno (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI alat** (claude -p, ollama…) | `cli` | (naredba) | — |

**Primjer `.env` za Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # s platform.moonshot.ai
AGENT_NAME=Yukine
```

**Primjer `.env` za Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # s api.z.ai
MODEL=glm-4.6v   # omogućena vizija; glm-4.7 / glm-5 = samo tekst
AGENT_NAME=Yukine
```

**Primjer `.env` za Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # s aistudio.google.com
MODEL=gemini-2.5-flash  # ili gemini-2.5-pro za veću sposobnost
AGENT_NAME=Yukine
```

**Primjer `.env` za OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # s openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcionalno: odredite model
AGENT_NAME=Yukine
```

> **Napomena:** Da biste onemogućili lokalne/NVIDIA modele, jednostavno ne postavljajte `BASE_URL` na lokalnu točku kao što je `http://localhost:11434/v1`. Umjesto toga koristite cloud pružatelje.

**Primjer `.env` za CLI alat:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — bez {}, prompt ide putem stdin
```

---

## MCP poslužitelji

familiar-ai može se povezati s bilo kojim [MCP (Model Context Protocol)](https://modelcontextprotocol.io) poslužiteljem. Ovo omogućuje povezivanje vanjske memorije, pristup datotečnom sustavu, web pretraživanje ili bilo koji drugi alat.

Konfigurirajte poslužitelje u `~/.familiar-ai.json` (isti format kao Claude Code):

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

Podržana su dva tipa transporta:
- **`stdio`**: pokreće lokalni podproces (`command` + `args`)
- **`sse`**: povezuje se s HTTP+SSE poslužiteljem (`url`)

Prepoznajte lokaciju konfiguracijske datoteke s `MCP_CONFIG=/path/to/config.json`.

---

## Hardver

familiar-ai radi sa svim hardverom koji imate — ili uopće ni s čim.

| Dio | Što radi | Primjer | Potrebno? |
|-----|----------|---------|-----------|
| Wi-Fi PTZ kamera | Oči + vrat | Tapo C220 (~$30) | **Preporučeno** |
| USB web kamera | Oči (fiksne) | Svaka UVC kamera | **Preporučeno** |
| Robotski usisavač | Noge | Svaki model kompatibilan s Tuya | Ne |
| PC / Raspberry Pi | Mozak | Bilo što što pokreće Python | **Da** |

> **Kamera je snažno preporučena.** Bez nje, familiar-ai i dalje može govoriti — ali ne može vidjeti svijet, što je u osnovi cijela svrha.

### Minimalna postava (bez hardvera)

Želite samo isprobati? Potrebujete samo API ključ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Pokrenite `./run.sh` i počnite razgovarati. Dodajte hardver kad vam zatreba.

### Wi-Fi PTZ kamera (Tapo C220)

1. U Tapo aplikaciji: **Postavke → Napredno → Račun kamere** — stvorite lokalni račun (ne TP-Link račun)
2. Pronađite IP kamere u popisu uređaja vašeg usmjerivača
3. Postavite u `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Glas (ElevenLabs)

1. Dobijte API ključ na [elevenlabs.io](https://elevenlabs.io/)
2. Postavite u `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcionalno, koristi zadani glas ako izostavljeni
   ```

Postoje dva odredišta reprodukcije, kontrolirana s `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC zvučnik (zadano)
TTS_OUTPUT=remote   # samo zvučnik kamere
TTS_OUTPUT=both     # zvučnik kamere + PC zvučnik istovremeno
```

#### A) Zvučnik kamere (putem go2rtc)

Postavite `TTS_OUTPUT=remote` (ili `both`). Treba [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Preuzmite izvršne datoteke s [stranice sa izdanjima](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Stavite i preimenujte:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # potrebno chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Stvorite `go2rtc.yaml` u istoj direktoriji:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Koristite akreditive za lokalne račune kamere (ne vaš TP-Link cloud račun).

4. familiar-ai automatski pokreće go2rtc prilikom pokretanja. Ako vaša kamera podržava dvosmjernu audio (povratnu liniju), glas se reproducira sa zvučnika kamere.

#### B) Lokalni PC zvučnik

Zadano (`TTS_OUTPUT=local`). Pokušava igrače redom: **paplay** → **mpv** → **ffplay**. Također se koristi kao rezervna opcija kada je `TTS_OUTPUT=remote` i go2rtc nije dostupan.

| OS | Instalirajte |
|----|--------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ili `paplay` putem `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — postavite `PULSE_SERVER=unix:/mnt/wslg/PulseServer` u `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — preuzmite i dodajte u PATH, **ili** `winget install ffmpeg` |

> Ako nijedan audio igrač nije dostupan, govor se i dalje generira — samo se neće reproducirati.

### Glasovni ulaz (Realtime STT)

Postavite `REALTIME_STT=true` u `.env` za trajni, glasovni ulaz bez ruku:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # isti ključ kao TTS
```

familiar-ai stream-a audio s mikrofona na ElevenLabs Scribe v2 i automatski bilježi transkripte kada prestanete govoriti. Nema potrebe za pritiskanjem gumba. Suvremeni način može koegzistirati s načinom pritiskanja za govor (Ctrl+T).

---

## TUI

familiar-ai uključuje terminal UI izgrađen s [Textual](https://textual.textualize.io/):

- Pomične povijesne razgovore s prijenosom teksta u stvarnom vremenu
- Automatsko dovršavanje za `/quit`, `/clear`
- Prekinite agenta usred prijelaza tipkanjem dok misli
- **Dnevnik razgovora** automatski pohranjen u `~/.cache/familiar-ai/chat.log`

Da biste pratili dnevnik u drugom terminalu (korisno za kopiranje):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Osobnost vašeg prijatelja živi u `ME.md`. Ova datoteka je gitignored — pripada isključivo vama.

Pogledajte [`persona-template/en.md`](./persona-template/en.md) za primjer, ili [`persona-template/ja.md`](./persona-template/ja.md) za japansku verziju.

---

## Česta pitanja

**P: Da li radi bez GPU-a?**
Da. Model ugradnje (multilingual-e5-small) radi odlično na CPU-u. GPU ubrzava, ali nije potreban.

**P: Mogu li koristiti kameru osim Tapo?**
Svaka kamera koja podržava ONVIF + RTSP bi trebala raditi. Tapo C220 je ono s čime smo testirali.

**P: Da li se moji podaci negdje šalju?**
Slike i tekst se šalju vašem odabranom LLM API-u na obradu. Uspomene se pohranjuju lokalno u `~/.familiar_ai/`.

**P: Zašto agent piše `（...）` umjesto da govori?**
Pobrinite se da je `ELEVENLABS_API_KEY` postavljen. Bez njega, glas je onemogućen i agent prelazi na tekst.

## Tehnička pozadina

Zanima vas kako to funkcionira? Pogledajte [docs/technical.md](./docs/technical.md) za istraživanje i odluke o dizajnu iza familiar-ai — ReAct, SayCan, Reflexion, Voyager, sustav želja i još mnogo toga.

---

## Doprinos

familiar-ai je otvoreni eksperiment. Ako vas bilo koja od ovih informacija doima bliskima — tehnički ili filozofski — doprinosi su vrlo dobrodošli.

**Dobra mjesta za početak:**

| Područje | Što je potrebno |
|----------|----------------|
| Novi hardver | Podrška za više kamera (RTSP, IP Webcam), mikrofone, aktuatore |
| Novi alati | Web pretraživanje, automatizacija doma, kalendar, bilo što putem MCP |
| Nove pozadinske usluge | Bilo koji LLM ili lokalni model koji odgovara `stream_turn` sučelju |
| Predlošci osobnosti | ME.md predlošci za različite jezike i osobnosti |
| Istraživanje | Bolji modeli želja, preuzimanje uspomena, poticanje teorije uma |
| Dokumentacija | Tutorijali, vodiči, prijevodi |

Pogledajte [CONTRIBUTING.md](./CONTRIBUTING.md) za postavke za razvoj, stil koda i smjernice za PR.

Ako niste sigurni odakle početi, [otvorite problem](https://github.com/lifemate-ai/familiar-ai/issues) — rado ću vas uputiti u pravom smjeru.

---

## Licenca

[MIT](./LICENSE)
