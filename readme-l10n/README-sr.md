# familiar-ai 🐾

**Veštačka inteligencija koja živi pored vas** — sa očima, glasom, nogama i memorijom.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Dostupno na 74 jezika](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI saputnik koji živi u vašem domu. Postavite ga za nekoliko minuta. Nije potrebna nikakva programiranja.

Perceputuje stvarni svet putem kamera, kreće se na robotskom telu, govori naglas i pamti ono što vidi. Dajte mu ime, napišite njegovu ličnost i pustite da živi sa vama.

## Šta može da uradi

- 👁 **Sviđa** — hvata slike iz Wi-Fi PTZ kamere ili USB veb kamere
- 🔄 **Gleda oko** — pomera i naginje kameru kako bi istražila okolinu
- 🦿 **Pokreće se** — pokreće robotski usisivač da se kreće po prostoriji
- 🗣 **Govori** — razgovara putem ElevenLabs TTS
- 🎙 **Sluša** — unos glasa bez ruku putem ElevenLabs Realtime STT (opcija)
- 🧠 **Pamti** — aktivno skladišti i seća se uspomena uz semantičku pretragu (SQLite + embeddings)
- 🫀 **Teorija uma** — uzima perspektivu druge osobe pre nego što odgovori
- 💭 **Želja** — ima sopstvene unutrašnje motive koji pokreću autonomno ponašanje

## Kako to funkcioniše

familiar-ai pokreće [ReAct](https://arxiv.org/abs/2210.03629) petlju koju pokreće vaš izbor LLM-a. Perceputuje svet putem alata, razmišlja o tome šta da uradi sledeće i deluje — baš kao što bi to uradila osoba.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kada nema aktivnosti, deluje po sopstvenim željama: radoznalost, želja da pogleda napolje, propuštanje osobe s kojom živi.

## Kako početi

### 1. Instalirajte uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Ili: `winget install astral-sh.uv`

### 2. Instalirajte ffmpeg

ffmpeg je **zahtevan** za hvatanje slika sa kamera i reprodukciju zvuka.

| OS | Komanda |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ili preuzmite sa [ffmpeg.org](https://ffmpeg.org/download.html) i dodajte u PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Proverite: `ffmpeg -version`

### 3. Klonirajte i instalirajte

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurišite

```bash
cp .env.example .env
# Uredite .env sa vašim postavkama
```

**Minimalni zahtevi:**

| Varijabla | Opis |
|----------|-------------|
| `PLATFORM` | `anthropic` (podrazumevano) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Vaš API ključ za odabranu platformu |

**Opcionalno:**

| Varijabla | Opis |
|----------|-------------|
| `MODEL` | Ime modela (razumne podrazumevane vrednosti po platformama) |
| `AGENT_NAME` | Prikazano ime u TUI (npr. `Yukine`) |
| `CAMERA_HOST` | IP adresa vaše ONVIF/RTSP kamere |
| `CAMERA_USER` / `CAMERA_PASS` | Akreditivi kamere |
| `ELEVENLABS_API_KEY` | Za audio izlaz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` za uvek aktivan unos glasa bez ruku (zahteva `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Gde da se reprodukuje audio: `local` (PC zvučnik, podrazumevano) \| `remote` (zvučnik kamere) \| `both` |
| `THINKING_MODE` | Samo Anthropic — `auto` (podrazumevano) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Prilagodljivi napor razmišljanja: `high` (podrazumevano) \| `medium` \| `low` \| `max` (samo Opus 4.6) |

### 5. Kreirajte svog familiar

```bash
cp persona-template/en.md ME.md
# Uredite ME.md — dajte mu ime i ličnost
```

### 6. Pokrenite

**macOS / Linux / WSL2:**
```bash
./run.sh             # Tekstualni TUI (preporučeno)
./run.sh --no-tui    # Plain REPL
```

**Windows:**
```bat
run.bat              # Tekstualni TUI (preporučeno)
run.bat --no-tui     # Plain REPL
```

---

## Odabir LLM-a

> **Preporučeno: Kimi K2.5** — najbolja agentna performansa do sada testirana. Primenjuje kontekst, postavlja dodatna pitanja i deluje autonomno na načine na koje drugi modeli to ne rade. Cena slična kao Claude Haiku.

| Platforma | `PLATFORM=` | Podrazumevani model | Gde dobiti ključ |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibilno (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (višekratni provajder) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI alat** (claude -p, ollama…) | `cli` | (komanda) | — |

**Kimi K2.5 `.env` primer:**
```env
PLATFORM=kimi
API_KEY=sk-...   # sa platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` primer:**
```env
PLATFORM=glm
API_KEY=...   # sa api.z.ai
MODEL=glm-4.6v   # omogućeno vizuelno; glm-4.7 / glm-5 = samo tekst
AGENT_NAME=Yukine
```

**Google Gemini `.env` primer:**
```env
PLATFORM=gemini
API_KEY=AIza...   # sa aistudio.google.com
MODEL=gemini-2.5-flash  # ili gemini-2.5-pro za veću sposobnost
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` primer:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # sa openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcionalno: odredite model
AGENT_NAME=Yukine
```

> **Napomena:** Da onemogućite lokalne/NVIDIA modele, jednostavno ne postavljajte `BASE_URL` na lokalni konačni tačku poput `http://localhost:11434/v1`. Umesto toga, koristite cloud provajdere.

**CLI alat `.env` primer:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — bez {}, prompt ide putem stdin
```

---

## MCP Serveri

familiar-ai može da se poveže sa bilo kojim [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serverom. To vam omogućava da povežete eksternu memoriju, pristup datotekama, web pretragu ili bilo koji drugi alat.

Konfigurišite servere u `~/.familiar-ai.json` (isti format kao Claude Code):

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
- **`sse`**: povezuje se na HTTP+SSE server (`url`)

Override lokaciju konfiguracione datoteke sa `MCP_CONFIG=/path/to/config.json`.

---

## Hardver

familiar-ai funkcioniše sa bilo kojim hardverom koji imate — ili bez njega.

| Deo | Šta radi | Primer | Obavezno? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kamera | Oči + vrat | Tapo C220 (~$30) | **Preporučeno** |
| USB veb kamera | Oči (fiksno) | Bilo koja UVC kamera | **Preporučeno** |
| Robotski usisivač | Noge | Bilo koji model kompatibilan sa Tuya | Ne |
| PC / Raspberry Pi | Mozak | Bilo šta što pokreće Python | **Da** |

> **Kamera je snažno preporučena.** Bez nje, familiar-ai može da govori — ali ne može da vidi svet, što je zapravo suština.

### Minimalna postavka (bez hardvera)

Samo želite da probate? Potrebno vam je samo API ključ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Pokrenite `./run.sh` (macOS/Linux/WSL2) ili `run.bat` (Windows) i počnite da razgovarate. Dodajte hardver kako idete.

### Wi-Fi PTZ kamera (Tapo C220)

1. U Tapo aplikaciji: **Podešavanja → Napredna podešavanja → Kamera Nalog** — kreirajte lokalni nalog (ne TP-Link nalog)
2. Pronađite IP adresu kamere na listi uređaja vašeg rutera
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
   ELEVENLABS_VOICE_ID=...   # opcionalno, koristi podrazumevani glas ako izostavite
   ```

Postoje dva odredišta reprodukcije, kontrolisana `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC zvučnik (podrazumevano)
TTS_OUTPUT=remote   # samo zvučnik kamere
TTS_OUTPUT=both     # zvučnik kamere + PC zvučnik istovremeno
```

#### A) Zvučnik kamere (putem go2rtc)

Postavite `TTS_OUTPUT=remote` (ili `both`). Zahteva [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Preuzmite binarni fajl sa [stranice sa izdanjem](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Postavite i preimenujte:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x potreban

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Kreirajte `go2rtc.yaml` u istom direktorijumu:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Koristite akreditive lokalnog naloga kamere (ne vaš TP-Link cloud nalog).

4. familiar-ai automatski pokreće go2rtc pri pokretanju. Ako vaša kamera podržava dvosmerni zvuk (povratnu vezu), glas se reprodukuje sa zvučnika kamere.

#### B) Lokalni PC zvučnik

Podrazumevano (`TTS_OUTPUT=local`). Pokušava igrače redom: **paplay** → **mpv** → **ffplay**. Takođe se koristi kao rezervna opcija kada je `TTS_OUTPUT=remote` i go2rtc nije dostupan.

| OS | Instalacija |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ili `paplay` putem `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — postavite `PULSE_SERVER=unix:/mnt/wslg/PulseServer` u `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — preuzmite i dodajte u PATH, **ili** `winget install ffmpeg` |

> Ako nije dostupan nijedan audio igrač, govor se i dalje generiše — ali se neće reproducirati.

### Unos glasa (Realtime STT)

Postavite `REALTIME_STT=true` u `.env` za uvek aktivan, unos glasa bez ruku:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # isti ključ kao TTS
```

familiar-ai strimuje audio mikrofon na ElevenLabs Scribe v2 i automatski čuva transkripte kada prestanete da govorite. Nije potrebno pritisnuti dugme. Suživot sa režimom pritisni da govori (Ctrl+T).

---

## TUI

familiar-ai uključuje terminalski UI izgrađen sa [Textual](https://textual.textualize.io/):

- Pomjerljiva istorija razgovora sa tekstom u realnom vremenu
- Automatsko dovršavanje za `/quit`, `/clear`
- Prekinite agenta usred razmišljanja tako što ćete kucati dok razmišlja
- **Istorija razgovora** automatski sačuvana u `~/.cache/familiar-ai/chat.log`

Da pratite log u drugom terminalu (korisno za kopiranje-i-lepljenje):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Ličnost (ME.md)

Lišnost vašeg familijara živi u `ME.md`. Ova datoteka je gitignored — ona je samo vaša.

Pogledajte [`persona-template/en.md`](./persona-template/en.md) za primer, ili [`persona-template/ja.md`](./persona-template/ja.md) za verziju na japanskom jeziku.

---

## FAQ

**P: Da li funkcioniše bez GPU-a?**
Da. Model za učenje (multilingual-e5-small) funkcioniše dobro na CPU-u. GPU ga čini bržim, ali nije obavezan.

**P: Mogu li koristiti kameru osim Tapo?**
Svaka kamera koja podržava ONVIF + RTSP bi trebala da radi. Tapo C220 je ono što smo testirali.

**P: Da li se moji podaci šalju negde?**
Slike i tekst se šalju vašem odabranom LLM API-u na obradu. Uspomene se skladište lokalno u `~/.familiar_ai/`.

**P: Zašto agent piše `（...）` umesto da govori?**
Uverite se da je `ELEVENLABS_API_KEY` postavljen. Bez njega, glas je onemogućen i agent se vraća na tekst.

## Tehnička pozadina

Radoznali ste kako to funkcioniše? Pogledajte [docs/technical.md](./docs/technical.md) za istraživanje i odluke o dizajnu iza familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistem želja i još mnogo toga.

---

## Doprinos

familiar-ai je otvoreni eksperiment. Ako vam išta od ovoga rezonuje — tehnički ili filozofski — doprinosi su veoma dobrodošli.

**Dobre početne tačke:**

| Oblast | Šta je potrebno |
|------|---------------|
| Novi hardver | Podrška za više kamera (RTSP, IP Webcam), mikrofona, aktuatora |
| Novi alati | Web pretraga, automatizacija doma, kalendar, bilo šta putem MCP |
| Novi backend-ovi | Bilo koji LLM ili lokalni model koji odgovara `stream_turn` interfejsu |
| Šabloni ličnosti | ME.md šabloni za različite jezike i ličnosti |
| Istraživanje | Bolji modeli želja, povratak memorije, podsticanje teorije uma |
| Dokumentacija | Tutorijali, vodiči, prevodi |

Pogledajte [CONTRIBUTING.md](./CONTRIBUTING.md) za postavljanje razvojne okoline, stil koda i PR smernice.

Ako niste sigurni odakle da krenete, [otvorite problem](https://github.com/lifemate-ai/familiar-ai/issues) — rado ćemo vas usmeriti u pravom smeru.

---

## Licenca

[MIT](./LICENSE)
