# familiar-ai 🐾

**AI koji živi uz vas** — s očima, glasom, nogama i memorijom.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Dostupno na 74 jezika](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI pratitelj koji živi u vašem domu.
Postavite ga za nekoliko minuta. Nije potrebna nikakva kodiranja.

Perceptira stvarni svijet kroz kamere, kreće se na robotskom tijelu, govori glasno i pamti što vidi. Dajte mu ime, napišite njegovu osobnost i neka živi s vama.

## Što može raditi

- 👁 **Vidjeti** — snima slike s Wi-Fi PTZ kamere ili USB web kamere
- 🔄 **Gledati okolo** — pomiče i naginje kameru kako bi istražio okolinu
- 🦿 **Kretati se** — vozi robotski usisavač po sobi
- 🗣 **Govoriti** — govori putem ElevenLabs TTS-a
- 🎙 **Slušati** — hands-free glasovni unos putem ElevenLabs Realtime STT (opcionalno)
- 🧠 **Pamtiti** — aktivno pohranjuje i prisjeća se uspomena s semantičkom pretragom (SQLite + ugradnje)
- 🫀 **Teorija uma** — uzima perspektivu druge osobe prije odgovora
- 💭 **Želja** — ima vlastite unutarnje porive koji pokreću autonomno ponašanje

## Kako to funkcionira

familiar-ai pokreće [ReAct](https://arxiv.org/abs/2210.03629) petlju vođenu vašim izborom LLM-a. Perceptira svijet kroz alate, razmišlja o sljedećem što treba učiniti i djeluje — baš kao što bi to činila osoba.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kada je neaktivan, djeluje prema vlastitim željama: znatiželja, želja da pogleda van, nedostajanje osobe s kojom živi.

## Početak rada

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

ffmpeg je **potreban** za prikupljanje slika s kamere i reprodukciju audiozapisa.

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
# Uredite .env s vašim postavkama
```

**Minimalno potrebno:**

| Varijabla | Opis |
|----------|-------------|
| `PLATFORM` | `anthropic` (zadano) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Vaš API ključ za odabranu platformu |

**Opcionalno:**

| Varijabla | Opis |
|----------|-------------|
| `MODEL` | Ime modela (razumne zadatke prema platformi) |
| `AGENT_NAME` | Prikazano ime u TUI-ju (npr. `Yukine`) |
| `CAMERA_HOST` | IP adresa vaše ONVIF/RTSP kamere |
| `CAMERA_USER` / `CAMERA_PASS` | Akreditivi kamere |
| `ELEVENLABS_API_KEY` | Za audio izlaz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` za omogućavanje uvijek uključenog hands-free glasovnog unosa (potreban `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Gdje reproducirati audio: `local` (PC zvučnik, zadano) \| `remote` (zvučnik kamere) \| `both` |
| `THINKING_MODE` | Samo za Anthropic — `auto` (zadano) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptivni napor razmišljanja: `high` (zadano) \| `medium` \| `low` \| `max` (samo Opus 4.6) |

### 5. Stvorite svog familiar

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

> **Preporučeno: Kimi K2.5** — najbolja agenta izvedba do sada testirana. Primjećuje kontekst, postavlja dodatna pitanja i djeluje autonomno na načine na koje drugi modeli ne rade. Cijenjen je slično kao Claude Haiku.

| Platforma | `PLATFORM=` | Zadani model | Gdje dobiti ključ |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibilan (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provajatelj) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI alat** (claude -p, ollama…) | `cli` | (komanda) | — |

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
MODEL=glm-4.6v   # s podrškom za viziju; glm-4.7 / glm-5 = samo tekst
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

> **Napomena:** Da biste onemogućili lokalne/NVIDIA modele, jednostavno nemojte postaviti `BASE_URL` na lokalnu točku kao što je `http://localhost:11434/v1`. Umjesto toga koristite cloud pružatelje.

**Primjer CLI alata `.env`:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — ne {}, prompt ide putem stdin
```

---

## MCP Poslužitelji

familiar-ai se može povezati s bilo kojim [MCP (Model Context Protocol)](https://modelcontextprotocol.io) poslužiteljem. Ovo vam omogućuje da uključite vanjsku memoriju, pristup datotečnom sustavu, web pretraživanje ili bilo koji drugi alat.

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

Podržani su dva tipa transporta:
- **`stdio`**: pokreće lokalni podproces (`command` + `args`)
- **`sse`**: povezuje se s HTTP+SSE poslužiteljem (`url`)

Prepišite lokaciju konfiguracijske datoteke s `MCP_CONFIG=/path/to/config.json`.

---

## Hardver

familiar-ai radi s bilo kojim hardverom koji imate — ili čak i bez njega.

| Dio | Što radi | Primjer | Obavezno? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kamera | Oči + vrata | Tapo C220 (~$30) | **Preporučeno** |
| USB web kamera | Oči (fiksne) | Bilo koja UVC kamera | **Preporučeno** |
| Robotski usisavač | Noge | Bilo koji model kompatibilan s Tuya | Ne |
| PC / Raspberry Pi | Mozak | Bilo što što pokreće Python | **Da** |

> **Kamera je snažno preporučena.** Bez nje, familiar-ai još uvijek može govoriti — ali ne može vidjeti svijet, što je prilično bitno.

### Minimalna postavka (bez hardvera)

Želite samo isprobati? Trebate samo API ključ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Pokrenite `./run.sh` (macOS/Linux/WSL2) ili `run.bat` (Windows) i počnite čavrljati. Dodajte hardver kako idete.

### Wi-Fi PTZ kamera (Tapo C220)

1. U Tapo aplikaciji: **Postavke → Napredno → Račun za kameru** — kreirajte lokalni račun (ne TP-Link račun)
2. Pronađite IP kamere u popisu uređaja vašeg usmjerivača
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
   ELEVENLABS_VOICE_ID=...   # opcionalno, koristi zadani glas ako je izostavljeno
   ```

Postoje dvije destinacije za reprodukciju, kontrolirane `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC zvučnik (zadano)
TTS_OUTPUT=remote   # samo zvučnik kamere
TTS_OUTPUT=both     # zvučnik kamere + PC zvučnik istovremeno
```

#### A) Zvučnik kamere (putem go2rtc)

Postavite `TTS_OUTPUT=remote` (ili `both`). Potrebno je [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Preuzmite binarnu datoteku s [stranice izdanja](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Postavite i preimenujte:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x potrebno

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Kreirajte `go2rtc.yaml` u istom direktoriju:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Koristite akreditive lokalnog računa kamere (ne svoj TP-Link cloud račun).

4. familiar-ai automatski pokreće go2rtc pri pokretanju. Ako vaša kamera podržava dvosmjerni audio (natrag kanal), glas se reproducira s zvučnika kamere.

#### B) Lokalne PC zvučnike

Zadano (`TTS_OUTPUT=local`). Pokušava igrače redom: **paplay** → **mpv** → **ffplay**. Također se koristi kao fallback kada je `TTS_OUTPUT=remote` i go2rtc nije dostupan.

| OS | Instalacija |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ili `paplay` putem `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — postavite `PULSE_SERVER=unix:/mnt/wslg/PulseServer` u `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — preuzmite i dodajte u PATH, **ili** `winget install ffmpeg` |

> Ako nijedan audio player nije dostupan, govor se još uvijek generira — samo se neće reproducirati.

### Glasovni unos (Realtime STT)

Postavite `REALTIME_STT=true` u `.env` za uvijek aktivan, hands-free glasovni unos:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # isti ključ kao TTS
```

familiar-ai prenosi audio sa mikrofona na ElevenLabs Scribe v2 i automatski pohranjuje transkripte kada prestanete govoriti. Nije potrebna nikakva tipka. Koegzistira s načinom pritiskanja za razgovor (Ctrl+T).

---

## TUI

familiar-ai uključuje terminal UI izgrađen s [Textual](https://textual.textualize.io/):

- Pomicalna povijest razgovora s tekstom u živoj struji
- Dovršavanje kartica za `/quit`, `/clear`
- Prekidanje agenta tijekom razmišljanja tipkanjem dok razmišlja
- **Dnevnik razgovora** automatski pohranjuje u `~/.cache/familiar-ai/chat.log`

Da pratite dnevnik u drugom terminalu (korisno za kopiranje) :
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Osobnost vašeg familiara živi u `ME.md`. Ova datoteka je gitignored — samo je vaša.

Pogledajte [`persona-template/en.md`](./persona-template/en.md) za primjer, ili [`persona-template/ja.md`](./persona-template/ja.md) za japansku verziju.

---

## Često postavljana pitanja

**P: Radi li bez GPU-a?**
Da. Model ugradnje (multilingual-e5-small) dobro radi na CPU-u. GPU ga čini bržim, ali nije potreban.

**P: Mogu li koristiti kameru osim Tapo?**
Bilo koja kamera koja podržava ONVIF + RTSP trebala bi raditi. Tapo C220 je ono s čime smo testirali.

**P: Da li se moji podaci šalju negdje?**
Slike i tekst šalju se na vašu odabranu LLM API za obradu. Uspomene se lokalno pohranjuju u `~/.familiar_ai/`.

**P: Zašto agent piše `（...）` umjesto da govori?**
Provjerite da je `ELEVENLABS_API_KEY` postavljen. Bez njega, glas je onemogućen i agent se vraća na tekst.

## Tehnička pozadina

Zanima vas kako to radi? Pogledajte [docs/technical.md](./docs/technical.md) za istraživanje i dizajnerske odluke iza familiar-ai — ReAct, SayCan, Reflexion, Voyager, sustav želja i još mnogo toga.

---

## Sudjelovanje

familiar-ai je otvoreni eksperiment. Ako vam bilo što od ovoga rezonira — tehnički ili filozofski — doprinosi su vrlo dobrodošli.

**Dobra mjesta za početak:**

| Područje | Što je potrebno |
|------|---------------|
| Novi hardver | Podrška za više kamera (RTSP, IP Webcam), mikrofone, aktuatora |
| Novi alati | Web pretraživanje, automatizacija kućanstva, kalendar, bilo što putem MCP-a |
| Nove pozadine | Bilo koji LLM ili lokalni model koji odgovara `stream_turn` sučelju |
| Predlošci osobnosti | ME.md predlošci za različite jezike i osobnosti |
| Istraživanje | Bolji modeli želja, dohvat memorije, poziv na teoriju uma |
| Dokumentacija | Tutorijali, upute, prijevodi |

Pogledajte [CONTRIBUTING.md](./CONTRIBUTING.md) za postavljanje razvojne sredine, stil kodiranja i smjernice za PR.

Ako niste sigurni gdje početi, [otvorite problem](https://github.com/lifemate-ai/familiar-ai/issues) — rado ću vam ukazati na pravi put.

---

## Licenca

[MIT](./LICENSE)
