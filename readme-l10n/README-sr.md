```markdown
# familiar-ai 🐾

**AI koji živi uz vas** — sa očima, glasom, nogama i memorijom.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI saputnik koji živi u vašem domu. 
Postavite ga za nekoliko minuta. Nema potrebe za kodiranjem.

Oseća stvarni svet kroz kamere, kreće se na robotu, govori naglas i pamti šta vidi. Dajte mu ime, napišite njegovu ličnost i pustite ga da živi s vama.

## Šta može da uradi

- 👁 **Vidi** — hvata slike sa Wi-Fi PTZ kamere ili USB web kamere
- 🔄 **Gleda oko sebe** — pomera i naginje kameru da istraži okolinu
- 🦿 **Pokreće se** — upravlja robot usisivačem da se kreće po prostoriji
- 🗣 **Govori** — priča putem ElevenLabs TTS
- 🎙 **Sluša** — glasovni unos bez ruku putem ElevenLabs Realtime STT (opcija)
- 🧠 **Pamti** — aktivno čuva i pretražuje sećanja putem semantičke pretrage (SQLite + embeddings)
- 🫀 **Teorija uma** — pre uzvraćanja uzima u obzir perspektivu druge osobe
- 💭 **Želja** — ima svoje unutrašnje impulse koji pokreću autonomno ponašanje

## Kako to funkcioniše

familiar-ai pokreće [ReAct](https://arxiv.org/abs/2210.03629) petlju koja se oslanja na vaš izbor LLM. On percipira svet kroz alate, razmišlja o tome šta da uradi sledeće, i deluje — baš kao što bi to uradila osoba.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kada je neaktivan, deluje prema sopstvenim željama: radoznalosti, želji da izgleda napolje, nedostajanju osobe s kojom živi.

## Kako početi

### 1. Instalirajte uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instalirajte ffmpeg

ffmpeg je **neophodan** za hvatanje slika sa kamere i reprodukciju zvuka.

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
# Uredite .env sa vašim podešavanjima
```

**Minimalno neophodno:**

| Varijabla | Opis |
|-----------|------|
| `PLATFORM` | `anthropic` (podrazumevano) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Vaš API ključ za odabranu platformu |

**Opcionalno:**

| Varijabla | Opis |
|-----------|------|
| `MODEL` | Ime modela (razumna podrazumevana podešavanja po platformi) |
| `AGENT_NAME` | Prikazano ime u TUI (npr. `Yukine`) |
| `CAMERA_HOST` | IP adresa vaše ONVIF/RTSP kamere |
| `CAMERA_USER` / `CAMERA_PASS` | Akreditivi za kameru |
| `ELEVENLABS_API_KEY` | Za glasovni izlaz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` da omogućite uvek uključeni glasovni unos bez ruku (zahteva `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Gde se reprodukuje zvuk: `local` (PC zvučnik, podrazumevano) \| `remote` (zvučnik kamere) \| `both` |
| `THINKING_MODE` | Samo Anthropic — `auto` (podrazumevano) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Prilagodljivi nivo razmišljanja: `high` (podrazumevano) \| `medium` \| `low` \| `max` (samo Opus 4.6) |

### 5. Kreirajte svog familiar

```bash
cp persona-template/en.md ME.md
# Uredite ME.md — dajte mu ime i ličnost
```

### 6. Pokrenite

```bash
./run.sh             # Tekstualni TUI (preporučeno)
./run.sh --no-tui    # Običan REPL
```

---

## Odabir LLM-a

> **Preporučeno: Kimi K2.5** — najbolja agentna performansa do sada testirana. Primećuje kontekst, postavlja dodatna pitanja i deluje autonomno na načine na koje drugi modeli to ne rade. Cene su slične onima Claude Haiku.

| Platforma | `PLATFORM=` | Podrazumevani model | Gde dobiti ključ |
|-----------|------------|--------------------|------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibilni (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
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
MODEL=glm-4.6v   # model sa podrškom za viziju; glm-4.7 / glm-5 = samo tekst
AGENT_NAME=Yukine
```

**Google Gemini `.env` primer:**
```env
PLATFORM=gemini
API_KEY=AIza...   # sa aistudio.google.com
MODEL=gemini-2.5-flash  # ili gemini-2.5-pro za veću funkcionalnost
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

> **Napomena:** Da onemogućite lokalne/NVIDIA modele, jednostavno nemojte postaviti `BASE_URL` na lokalnu tačku kao što je `http://localhost:11434/v1`. Umesto toga koristite cloud provajdere.

**CLI alat `.env` primer:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — bez {}, prompt ide putem stdin
```

---

## MCP Serveri

familiar-ai se može povezati sa bilo kojim [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serverom. To vam omogućava da uključite eksternu memoriju, pristup datotečnom sistemu, web pretragu ili bilo koji drugi alat.

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

Podržani su dva tipa transporta:
- **`stdio`**: pokreće lokalni podproces (`command` + `args`)
- **`sse`**: povezuje se na HTTP+SSE server (`url`)

Prepisivanje lokacije konfiguracione datoteke sa `MCP_CONFIG=/path/to/config.json`.

---

## Hardver

familiar-ai radi sa bilo kojim hardverom koji imate — ili čak i bez njega.

| Deo | Šta radi | Primer | Da li je potrebno? |
|-----|----------|--------|-------------------|
| Wi-Fi PTZ kamera | Oči + vrat | Tapo C220 (~$30) | **Preporučeno** |
| USB web kamera | Oči (fiksne) | Bilo koja UVC kamera | **Preporučeno** |
| Robot usisivač | Noge | Bilo koji model kompatibilan sa Tuya | Ne |
| PC / Raspberry Pi | Mozak | Bilo šta što pokreće Python | **Da** |

> **Kamera je snažno preporučena.** Bez nje, familiar-ai i dalje može govoriti — ali ne može videti svet, što je suština cele priče.

### Minimalna konfiguracija (bez hardvera)

Samo želite da probate? Potrebno vam je samo API ključ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Pokrenite `./run.sh` i počnite da časkate. Dodajte hardver kako budete išli.

### Wi-Fi PTZ kamera (Tapo C220)

1. U Tapo aplikaciji: **Podešavanja → Napredno → Račun kamere** — kreirajte lokalni račun (ne TP-Link račun)
2. Pronađite IP kamere na listi uređaja vašeg rutera
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
   ELEVENLABS_VOICE_ID=...   # opcionalno, koristi podrazumevani glas ako je izostavljeno
   ```

Postoje dva odredišta reprodukcije, kontrolisana sa `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC zvučnik (podrazumevano)
TTS_OUTPUT=remote   # samo zvučnik kamere
TTS_OUTPUT=both     # zvučnik kamere + PC zvučnik istovremeno
```

#### A) Zvučnik kamere (preko go2rtc)

Postavite `TTS_OUTPUT=remote` (ili `both`). Zahteva [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Preuzmite binarnu datoteku sa [strane sa izdanjima](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Postavite i preimenujte:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # potrebno je chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Kreirajte `go2rtc.yaml` u istom direktorijumu:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Koristite lokalne akreditive za kameru (ne svoj TP-Link nalog u oblaku).

4. familiar-ai automatski pokreće go2rtc prilikom pokretanja. Ako vaša kamera podržava dvosmerni audio (backchannel), glas se reprodukuje sa zvučnika kamere.

#### B) Lokalni PC zvučnik

Podrazumevano (`TTS_OUTPUT=local`). Pokušava plejere redom: **paplay** → **mpv** → **ffplay**. Takođe se koristi kao rezervna opcija kada je `TTS_OUTPUT=remote` i go2rtc nije dostupan.

| OS | Instalirajte |
|----|-------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ili `paplay` putem `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — postavite `PULSE_SERVER=unix:/mnt/wslg/PulseServer` u `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — preuzmite i dodajte u PATH, **ili** `winget install ffmpeg` |

> Ako ni jedan audio plejer nije dostupan, govor se i dalje generiše — samo se neće reproducirati.

### Glasovni unos (Realtime STT)

Postavite `REALTIME_STT=true` u `.env` za uvek uključen, glasovni unos bez ruku:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # isti ključ kao TTS
```

familiar-ai streamuje audio sa mikrofona na ElevenLabs Scribe v2 i automatski čuva transkripte kada prestanete da govorite. Nije potrebno pritiskati dugme. Koegzistira sa režimom za razgovor (Ctrl+T).

---

## TUI

familiar-ai uključuje terminalski UI napravljen sa [Textual](https://textual.textualize.io/):

- Pomera istoriju razgovora sa live streaming tekstom
- Automatsko dovršavanje za `/quit`, `/clear`
- Prekinite agenta tokom razmišljanja tako što ćete kucati dok razmišlja
- **Dnevnik razgovora** automatski se čuva u `~/.cache/familiar-ai/chat.log`

Da pratite dnevnik u drugom terminalu (korisno za kopiranje-zalepivanje):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Ličnost (ME.md)

Ličnost vašeg familiara živi u `ME.md`. Ova datoteka je gitignored — samo je vaša.

Pogledajte [`persona-template/en.md`](./persona-template/en.md) za primer, ili [`persona-template/ja.md`](./persona-template/ja.md) za japansku verziju.

---

## Često postavljana pitanja

**P: Da li radi bez GPU?**
Da. Model za uparivanje (multilingual-e5-small) lepo funkcioniše na CPU. GPU ga čini bržim, ali nije neophodan.

**P: Mogu li da koristim kameru osim Tapo?**
Svaka kamera koja podržava ONVIF + RTSP bi trebala da radi. Tapo C220 je ono što smo testirali.

**P: Da li se moji podaci šalju negde?**
Slike i tekst se šalju na vašu odabranu LLM API za obradu. Sećanja se čuvaju lokalno u `~/.familiar_ai/`.

**P: Zašto agent piše `（...）` umesto da govori?**
Uverite se da je `ELEVENLABS_API_KEY` postavljen. Bez toga, glas je onemogućen i agent se vraća na tekst.

## Tehnička pozadina

Zanima vas kako to funkcioniše? Pogledajte [docs/technical.md](./docs/technical.md) za istraživanje i dizajnerske odluke iza familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistem želja, i još mnogo toga.

---

## Doprinos

familiar-ai je otvoren eksperiment. Ako vam bilo šta od ovoga odgovara — tehnički ili filozofski — priloge su uvek dobrodošli.

**Dobra mesta za početak:**

| Oblast | Šta je potrebno |
|--------|----------------|
| Novi hardver | Podrška za više kamera (RTSP, IP Webcam), mikrofone, aktuatore |
| Novi alati | Web pretraga, automatizacija doma, kalendar, bilo šta putem MCP |
| Novi backendovi | Bilo koji LLM ili lokalni model koji odgovara `stream_turn` interfejsu |
| Šabloni ličnosti | ME.md šabloni za različite jezike i ličnosti |
| Istraživanje | Bolji modeli želja, preuzimanje sećanja, prompting teorije uma |
| Dokumentacija | Tutorijali, vodiči, prevodi |

Pogledajte [CONTRIBUTING.md](./CONTRIBUTING.md) za postavke za razvoj, stil kodiranja i PR smernice.

Ako niste sigurni odakle da krenete, [otvorite problem](https://github.com/lifemate-ai/familiar-ai/issues) — rado ću vam ukazati na pravi put.

---

## Licenca

[MIT](./LICENSE)
```
