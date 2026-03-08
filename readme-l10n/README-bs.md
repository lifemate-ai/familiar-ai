# familiar-ai 🐾

**AI koji živi uz vas** — s očima, glasom, nogama i memorijom.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Dostupno na 74 jezika](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI pratilac koji živi u vašem domu.
Postavite ga za nekoliko minuta. Nema potrebe za kodiranjem.

Percepcija stvarnog svijeta kroz kamere, kreće se na robotickom tijelu, govori naglas i pamti ono što vidi. Dajte mu ime, napišite njegovu osobnost i pustite ga da živi s vama.

## Šta može uraditi

- 👁 **Vidjeti** — snima slike sa Wi-Fi PTZ kamere ili USB web kamere
- 🔄 **Pogledati oko sebe** — naginje i okreće kameru da istražuje okolinu
- 🦿 **Kretati se** — upravlja robot usisivačem da se kreće po prostoriji
- 🗣 **Govori** — komunicira putem ElevenLabs TTS
- 🎙 **Sluša** — hands-free glasovni unos putem ElevenLabs Realtime STT (opt-in)
- 🧠 **Pamti** — aktivno pohranjuje i prisjeća se uspomena uz semantičko pretraživanje (SQLite + ugradnja)
- 🫀 **Teorija uma** — uzima perspektivu druge osobe prije nego što odgovori
- 💭 **Želja** — ima unutarnje porive koji pokreću autonomno ponašanje

## Kako to radi

familiar-ai pokreće [ReAct](https://arxiv.org/abs/2210.03629) petlju pokretanu vašim izborom LLM. Percepcija svijeta kroz alate, razmišlja o sljedećem potezu i djeluje — baš kao što bi to uradila osoba.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kada nije aktivan, djeluje prema svojim željama: znatiželja, želja da pogleda napolje, nedostajanje osobe s kojom živi.

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

ffmpeg je **neophodan** za snimanje slika s kamere i reprodukciju zvuka.

| OS | Komanda |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ili preuzmite sa [ffmpeg.org](https://ffmpeg.org/download.html) i dodajte u PATH |
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
# Uredite .env s vašim postavkama
```

**Minimalno potrebno:**

| Varijabla | Opis |
|-----------|------|
| `PLATFORM` | `anthropic` (podrazumijevano) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Vaš API ključ za odabranu platformu |

**Opcionalno:**

| Varijabla | Opis |
|-----------|------|
| `MODEL` | Ime modela (senzibilni podrazumijevani postavke po platformi) |
| `AGENT_NAME` | Ime prikazano u TUI (npr. `Yukine`) |
| `CAMERA_HOST` | IP adresa vaše ONVIF/RTSP kamere |
| `CAMERA_USER` / `CAMERA_PASS` | Podaci za prijavu za kameru |
| `ELEVENLABS_API_KEY` | Za glasovni izlaz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` za aktiviranje stalnog hands-free glasovnog unosa (zahtijeva `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Gdje reproducirati zvuk: `local` (PC zvučnik, podrazumijevano) \| `remote` (zvučnik kamere) \| `both` |
| `THINKING_MODE` | Samo za Anthropic — `auto` (podrazumijevano) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptivno razmišljanje: `high` (podrazumijevano) \| `medium` \| `low` \| `max` (samo Opus 4.6) |

### 5. Kreirajte svog familiar

```bash
cp persona-template/en.md ME.md
# Uredite ME.md — dajte mu ime i osobnost
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

> **Preporučeno: Kimi K2.5** — najbolja agentna performansa do sada testirana. Primjećuje kontekst, postavlja dodatna pitanja i djeluje autonomno na načine na koje drugi modeli ne rade. Cijena je slična kao kod Claude Haiku.

| Platforma | `PLATFORM=` | Podrazumijevani model | Gdje dobiti ključ |
|-----------|------------|-----------------------|-------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibilni (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-providera) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI alat** (claude -p, ollama…) | `cli` | (komanda) | — |

**Kimi K2.5 `.env` primjer:**
```env
PLATFORM=kimi
API_KEY=sk-...   # sa platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` primjer:**
```env
PLATFORM=glm
API_KEY=...   # sa api.z.ai
MODEL=glm-4.6v   # omogućena vizija; glm-4.7 / glm-5 = samo tekst
AGENT_NAME=Yukine
```

**Google Gemini `.env` primjer:**
```env
PLATFORM=gemini
API_KEY=AIza...   # sa aistudio.google.com
MODEL=gemini-2.5-flash  # ili gemini-2.5-pro za veću sposobnost
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` primjer:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # sa openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcionalno: specificirajte model
AGENT_NAME=Yukine
```

> **Napomena:** Da onemogućite lokalne/NVIDIA modele, jednostavno nemojte postaviti `BASE_URL` na lokalnu tačku kao što je `http://localhost:11434/v1`. Koristite cloud provajdere umjesto toga.

**CLI alat `.env` primjer:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — bez {}, prompt ide putem stdin
```

---

## MCP Servers

familiar-ai se može povezati na bilo koji [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Ovo vam omogućava da priključite eksternu memoriju, pristup datotečnom sistemu, pretragu na mreži, ili bilo koji drugi alat.

Konfigurirajte servere u `~/.familiar-ai.json` (isti format kao Claude Code):

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

Podržavaju se dva tipa transporta:
- **`stdio`**: pokreće lokalni podproces (`command` + `args`)
- **`sse`**: povezuje se na HTTP+SSE server (`url`)

Override-ujte lokaciju config fajla s `MCP_CONFIG=/path/to/config.json`.

---

## Hardver

familiar-ai radi sa bilo kojim hardverom koji imate — ili ni sa čim.

| Deo | Šta radi | Primer | Neophodno? |
|-----|----------|--------|------------|
| Wi-Fi PTZ kamera | Oči + vrat | Tapo C220 (~$30, Eufy C220) | **Preporučeno** |
| USB web kamera | Oči (fiksno) | Bilo koja UVC kamera | **Preporučeno** |
| Robot usisivač | Noge | Bilo koji Tuya-kompatibilni model | Ne |
| PC / Raspberry Pi | Mozak | Bilo šta što pokreće Python | **Da** |

> **Kamera je toplo preporučena.** Bez nje, familiar-ai i dalje može govoriti — ali ne može vidjeti svijet, što je suština.

### Minimalna postavka (bez hardvera)

Samo želite probati? Potreban vam je samo API ključ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Pokrenite `./run.sh` (macOS/Linux/WSL2) ili `run.bat` (Windows) i počnite razgovarati. Dodajte hardver kako budete išli.

### Wi-Fi PTZ kamera (Tapo C220)

1. U Tapo aplikaciji: **Postavke → Napredno → Račun kamere** — kreirajte lokalni račun (ne TP-Link račun)
2. Pronađite IP kamere na listi uređaja vašeg rutera
3. Postavite u `.env`:
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


### Glas (ElevenLabs)

1. Nabavite API ključ na [elevenlabs.io](https://elevenlabs.io/)
2. Postavite u `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcionalno, koristi podrazumijevani glas ako je izostavljen
   ```

Postoje dva odredišta za reprodukciju, kontrolisana sa `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC zvučnik (podrazumijevano)
TTS_OUTPUT=remote   # samo zvučnik kamere
TTS_OUTPUT=both     # zvučnik kamere + PC zvučnik istovremeno
```

#### A) Zvučnik kamere (putem go2rtc)

Postavite `TTS_OUTPUT=remote` (ili `both`). Zahteva [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Preuzmite izvršni fajl sa [strane za preuzimanje](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Postavite i preimenujte:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x je potreban

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Kreirajte `go2rtc.yaml` u istom direktoriju:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Koristite lokalne podatke za prijavu kamere (ne vaš TP-Link cloud nalog).

4. familiar-ai automatski pokreće go2rtc pri pokretanju. Ako vaša kamera podržava dvostrani audio (povratni kanal), glas se reprodukuje preko zvučnika kamere.

#### B) Lokalni PC zvučnik

Podrazumijevano (`TTS_OUTPUT=local`). Pokušava igrače u redoslijedu: **paplay** → **mpv** → **ffplay**. Takođe se koristi kao rezervna opcija kada je `TTS_OUTPUT=remote` i go2rtc nije dostupan.

| OS | Instalacija |
|----|-------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ili `paplay` putem `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — postavite `PULSE_SERVER=unix:/mnt/wslg/PulseServer` u `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — preuzmite i dodajte u PATH, **ili** `winget install ffmpeg` |

> Ako nema dostupnog audio plejera, govor se i dalje generiše — samo se neće reprodukovati.

### Glasovni unos (Realtime STT)

Postavite `REALTIME_STT=true` u `.env` za stalni, hands-free glasovni unos:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # isti ključ kao TTS
```

familiar-ai streamuje audio sa mikrofona do ElevenLabs Scribe v2 i automatski potvrđuje transkripte kada prestanete govoriti. Nema potrebe za pritiskanjem dugmeta. Koegzistira sa režimom za pritisak na govor (Ctrl+T).

---

## TUI

familiar-ai uključuje terminalski UI izgrađen s [Textual](https://textual.textualize.io/):

- Pomjerljiva istorija razgovora sa uživo streamovanjem teksta
- Automatsko dovršavanje za `/quit`, `/clear`
- Prekinite agenta usred rekacije tako što ćete tipkati dok razmišlja
- **Log razgovora** automatski sačuvan u `~/.cache/familiar-ai/chat.log`

Da biste pratili log u drugom terminalu (korisno za kopiranje-pasting):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Osobnost (ME.md)

Osobnost vašeg familiara živi u `ME.md`. Ova datoteka je gitignored — samo je vaša.

Pogledajte [`persona-template/en.md`](./persona-template/en.md) za primer, ili [`persona-template/ja.md`](./persona-template/ja.md) za japansku verziju.

---

## Često postavljana pitanja

**Q: Da li radi bez GPU-a?**
Da. Model za ugradnju (multilingual-e5-small) radi dobro na CPU-u. GPU ga čini bržim, ali nije neophodan.

**Q: Mogu li koristiti kameru koja nije Tapo?**
Svaka kamera koja podržava Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: Da li se moji podaci šalju negde?**
Slike i tekst se šalju vašem izabranom LLM API-ju na obradu. Uspomene se pohranjuju lokalno u `~/.familiar_ai/`.

**Q: Zašto agent piše `（...）` umesto da govori?**
Uverite se da je `ELEVENLABS_API_KEY` postavljen. Bez njega, glas je onemogućen i agent se vraća na tekst.

## Tehnička pozadina

Zanima vas kako to funkcioniše? Pogledajte [docs/technical.md](./docs/technical.md) za istraživanje i dizajnerske odluke iza familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistem želja i još mnogo toga.

---

## Doprinos

familiar-ai je otvoreni eksperiment. Ako vam je nešto od ovoga zanimljivo — tehnički ili filozofski — doprinosi su veoma dobrodošli.

**Dobre stvari za početak:**

| Oblast | Šta je potrebno |
|--------|-----------------|
| Novi hardver | Podrška za više kamera (RTSP, IP Webcam), mikrofona, aktuatora |
| Novi alati | Pretraga na mreži, automatizacija doma, kalendar, bilo šta putem MCP |
| Nove pozadinske usluge | Bilo koji LLM ili lokalni model koji odgovara `stream_turn` interfejsu |
| Šabloni ličnosti | ME.md šabloni za različite jezike i osobnosti |
| Istraživanje | Bolji modeli želja, povlačenje memorije, promptovanje teorije uma |
| Dokumentacija | Tutorijali, vodiči, prevodi |

Pogledajte [CONTRIBUTING.md](./CONTRIBUTING.md) za postavke za razvoj, stil koda i PR smjernice.

Ako niste sigurni odakle da krenete, [otvorite issue](https://github.com/lifemate-ai/familiar-ai/issues) — rado ćemo vas usmjeriti.

---

## Licenca

[MIT](./LICENSE)

[→ English README](../README.md)
