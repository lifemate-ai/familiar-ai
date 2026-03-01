# familiar-ai 🐾

**AI koja živi uz vas** — sa očima, glasom, nogama i memorijom.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI prijatelj koji živi u vašem domu.  
Postavite ga za nekoliko minuta. Nema potrebe za kodiranjem.

Percepcija stvarnog sveta se odvija putem kamera, pokreće se na robotskom telu, govori naglas i pamti ono što vidi. Dajte mu ime, napišite njegov karakter i dopustite mu da živi s vama.

## Šta može uraditi

- 👁 **Videti** — hvata slike sa Wi-Fi PTZ kamere ili USB web kamere
- 🔄 **Pogledati okolo** — pomera i nagiba kameru da istražuje okolinu
- 🦿 **Kretati se** — vozi robotski usisivač da se kreće po prostoriji
- 🗣 **Govoriti** — govori putem ElevenLabs TTS
- 🎙 **Slušati** — hands-free glasovni ulaz putem ElevenLabs Realtime STT (opciono)
- 🧠 **Pamtiti** — aktivno čuva i poziva uspomene sa semantičkom pretragom (SQLite + ugradnje)
- 🫀 **Teorija uma** — uzima perspektivu druge osobe pre nego odgovori
- 💭 **Želja** — ima vlastite unutrašnje porive koji pokreću autonomno ponašanje

## Kako funkcioniše

familiar-ai pokreće [ReAct](https://arxiv.org/abs/2210.03629) petlju na osnovu vašeg izbora LLM. Percepcija sveta se odvija kroz alate, razmišlja o sledećem koraku i deluje — kao što bi to uradila osoba.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kada je neaktivan, deluje na osnovu vlastitih želja: radoznalosti, želje da pogleda napolje, nedostatka osobe s kojom živi.

## Počnite

### 1. Instalirajte uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instalirajte ffmpeg

ffmpeg je **zahtjevan** za hvatanje slika sa kamere i reprodukciju zvuka.

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

**Minimalna potrebna:**

| Varijabla | Opis |
|-----------|------|
| `PLATFORM` | `anthropic` (podrazumevano) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Vaš API ključ za izabranu platformu |

**Opcionalno:**

| Varijabla | Opis |
|-----------|------|
| `MODEL` | Ime modela (razumne podrazumevane vrednosti po platformi) |
| `AGENT_NAME` | Prikazano ime u TUI (npr. `Yukine`) |
| `CAMERA_HOST` | IP adresa vaše ONVIF/RTSP kamere |
| `CAMERA_USER` / `CAMERA_PASS` | Akreditivi kamere |
| `ELEVENLABS_API_KEY` | Za glasovni izlaz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` za omogućavanje uvek uključenog hands-free glasovnog ulaza (zahteva `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Gde da se reprodukuje zvuk: `local` (zvučnik računara, podrazumevano) \| `remote` (zvučnik kamere) \| `both` |
| `THINKING_MODE` | Samo za Anthropic — `auto` (podrazumevano) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptivni napor razmišljanja: `high` (podrazumevano) \| `medium` \| `low` \| `max` (samo Opus 4.6) |

### 5. Kreirajte svog prijatelja

```bash
cp persona-template/en.md ME.md
# Uredite ME.md — dajte mu ime i karakter
```

### 6. Pokrenite

```bash
./run.sh             # Tekstualni TUI (preporučeno)
./run.sh --no-tui    # Običan REPL
```

---

## Izbor LLM-a

> **Preporučeno: Kimi K2.5** — najbolja agentna performansa do sada testirana. Primećuje kontekst, postavlja dodatna pitanja i deluje autonomno na načine koje drugi modeli ne rade. Cene su slične kao za Claude Haiku.

| Platforma | `PLATFORM=` | Podrazumevani model | Gde dobiti ključ |
|-----------|-------------|---------------------|------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibilni (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provide) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
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

> **Napomena:** Da biste onemogućili lokalne/NVIDIA modele, jednostavno ne postavljajte `BASE_URL` na lokalnu adresu kao što je `http://localhost:11434/v1`. Umesto toga koristite cloud provajdere.

**CLI alat `.env` primer:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — bez {}, prompt ide putem stdin
```

---

## MCP Serveri

familiar-ai se može povezati na bilo koji [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Ovo vam omogućava da uključite eksternu memoriju, pristup datotečnom sistemu, web pretragu ili bilo koji drugi alat.

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
- **`stdio`**: pokreće lokalni podproceso (`command` + `args`)
- **`sse`**: povezuje se na HTTP+SSE server (`url`)

Prepišite lokaciju konfiguracione datoteke sa `MCP_CONFIG=/path/to/config.json`.

---

## Hardver

familiar-ai radi sa bilo kojim hardverom koji imate — ili uopšte nema.

| Deo | Šta radi | Primer | Obavezno? |
|-----|----------|--------|-----------|
| Wi-Fi PTZ kamera | Oči + vrat | Tapo C220 (~$30) | **Preporučeno** |
| USB web kamera | Oči (fiksne) | Bilo koja UVC kamera | **Preporučeno** |
| Robotski usisivač | Noge | Bilo koji model kompatibilan sa Tuya | Ne |
| PC / Raspberry Pi | Mozak | Bilo šta što pokreće Python | **Da** |

> **Kamera je toplo preporučena.** Bez nje, familiar-ai može i dalje govoriti — ali ne može videti svet, što je u suštini cela poenta.

### Minimalna instalacija (bez hardvera)

Samo želite da probate? Potrebna vam je samo API ključe:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Pokrenite `./run.sh` i počnite da razgovarate. Dodajte hardver dok napredujete.

### Wi-Fi PTZ kamera (Tapo C220)

1. U Tapo aplikaciji: **Podešavanja → Napredno → Kamera Račun** — kreirajte lokalni račun (ne TP-Link račun)
2. Pronađite IP kameru na listi uređaja vašeg rutera
3. Postavite u `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Glas (ElevenLabs)

1. Nabavite API ključ na [elevenlabs.io](https://elevenlabs.io/)
2. Postavite u `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcionalno, koristi podrazumevani glas ako se izostavi
   ```

Postoje dve destinacije za reprodukciju, kontrolisane sa `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC zvučnik (podrazumevano)
TTS_OUTPUT=remote   # samo zvučnik kamere
TTS_OUTPUT=both     # zvučnik kamere + PC zvučnik istovremeno
```

#### A) Zvučnik kamere (preko go2rtc)

Postavite `TTS_OUTPUT=remote` (ili `both`). Zahteva [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Preuzmite binarni iz [strane sa izdanjima](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Postavite i preimenujte:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x potrebno

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Kreirajte `go2rtc.yaml` u istom direktorijumu:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Koristite akreditive lokalnog naloga kamere (ne svoj TP-Link cloud račun).

4. familiar-ai automatski pokreće go2rtc prilikom pokretanja. Ako vaša kamera podržava dvosmerni audio (povratni kanal), glas se reprodukuje sa zvučnika kamere.

#### B) Lokalni PC zvučnik

Podrazumevano (`TTS_OUTPUT=local`). Pokušava igrače redom: **paplay** → **mpv** → **ffplay**. Takođe se koristi kao rezervna opcija kada je `TTS_OUTPUT=remote` i go2rtc nije dostupan.

| OS | Instalacija |
|----|-------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ili `paplay` preko `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — postavite `PULSE_SERVER=unix:/mnt/wslg/PulseServer` u `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — preuzmite i dodajte u PATH, **ili** `winget install ffmpeg` |

> Ako nema dostupnog igrača zvuka, govor se i dalje generiše — prosto neće biti reprodukovan.

### Glasovni ulaz (Realtime STT)

Postavite `REALTIME_STT=true` u `.env` za uvek uključen, hands-free glasovni ulaz:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # isti ključ kao za TTS
```

familiar-ai strimuje zvuk mikrofona u ElevenLabs Scribe v2 i automatski čuva transkripte kada prestanete govoriti. Nema potrebe za pritiskom dugmeta. Koegzistira sa modom za pritiskanje za razgovor (Ctrl+T).

---

## TUI

familiar-ai uključuje terminalski UI izgrađen sa [Textual](https://textual.textualize.io/):

- Pomjerljivo istorija razgovora sa live strimovanim tekstom
- Tab-kompletiranje za `/quit`, `/clear`
- Prekidanje agenta usred misli tako što ćete tipkati dok razmišlja
- **Dnevnik razgovora** automatski sačuvan u `~/.cache/familiar-ai/chat.log`

Da pratite dnevnik u drugom terminalu (korisno za kopiranje-lepljenje):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Karakter vašeg prijatelja živi u `ME.md`. Ova datoteka je gitignored — ona je samo vaša.

Pogledajte [`persona-template/en.md`](./persona-template/en.md) za primer, ili [`persona-template/ja.md`](./persona-template/ja.md) za japansku verziju.

---

## Često postavljana pitanja

**P: Da li radi bez GPU-a?**  
Da. Model ugradnje (multilingual-e5-small) radi dobro na CPU-u. GPU ga čini bržim, ali nije obavezan.

**P: Mogu li koristiti kameru koja nije Tapo?**  
Bilo koja kamera koja podržava ONVIF + RTSP bi trebala raditi. Tapo C220 je ono što smo testirali.

**P: Da li se moji podaci šalju negde?**  
Slikе i tekst se šalju na vaš izabrani LLM API radi obrade. Uspomene se čuvaju lokalno u `~/.familiar_ai/`.

**P: Zašto agent piše `（...）` umesto da govori?**  
Proverite da li je `ELEVENLABS_API_KEY` postavljen. Bez njega, glas je onemogućen i agent se vraća na tekst.

## Tehnička pozadina

Zanima vas kako funkcioniše? Pogledajte [docs/technical.md](./docs/technical.md) za istraživanje i dizajnerske odluke iza familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistem želja i više.

---

## Doprinose

familiar-ai je otvoreni eksperiment. Ako vas nešto od ovoga dotiče — tehnički ili filozofski — doprinosi su vrlo dobrodošli.

**Dobra mesta za početak:**

| Oblast | Šta je potrebno |
|--------|----------------|
| Novi hardver | Podrška za više kamera (RTSP, IP Webcam), mikrofona, aktuatora |
| Novi alati | Web pretraga, automatizacija doma, kalendar, bilo šta preko MCP-a |
| Novi backend | Bilo koji LLM ili lokalni model koji odgovara `stream_turn` interfejsu |
| Šabloni ličnosti | ME.md šabloni za različite jezike i karaktere |
| Istraživanje | Bolji modeli želja, povratak memorije, prompting teorije uma |
| Dokumentacija | Tutorijali, vodiči, prevodi |

Pogledajte [CONTRIBUTING.md](./CONTRIBUTING.md) za postavke za razvoj, stil kodiranja i PR smernice.

Ako niste sigurni gde da počnete, [otvorite problem](https://github.com/lifemate-ai/familiar-ai/issues) — rado ću vas uputiti u pravom pravcu.

---

## Licenca

[MIT](./LICENSE)
