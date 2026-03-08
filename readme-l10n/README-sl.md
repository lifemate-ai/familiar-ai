# familiar-ai 🐾

**AI, ki živi ob vas** — z očmi, glasom, nogami in spominom.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Na voljo v 74 jezikih](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI spremljevalec, ki živi v vašem domu. 
Nastavite ga v nekaj minutah. Programiranje ni potrebno.

Zaznava resnični svet preko kamer, se premika na robotskem telesu, govori na glas in si zapomni, kar vidi. Imejte mu ime, napišite njegovo osebnost in pustite mu, da živi z vami.

## Kaj lahko stori

- 👁 **Vidite** — zajemanje slik iz Wi-Fi PTZ kamere ali USB kamere
- 🔄 **Poglejte okoli** — premika in nagiba kamero, da raziskuje okolico
- 🦿 **Premik** — vozi robotski sesalnik po prostoru
- 🗣 **Govorite** — govori preko ElevenLabs TTS
- 🎙 **Poslušajte** — brezrokovni glasovni vhod preko ElevenLabs Realtime STT (opt-in)
- 🧠 **Zapomnite si** — aktivno shrani in prikliče spomine s semantičnim iskanjem (SQLite + embeddings)
- 🫀 **Teorija uma** — upošteva perspektivo druge osebe, preden odgovori
- 💭 **Želja** — ima svoje notranje usmeritve, ki sprožijo avtonomno vedenje

## Kako deluje

familiar-ai vodi [ReAct](https://arxiv.org/abs/2210.03629) zanko, ki jo poganja vaša izbira LLM. Zaznava svet preko orodij, razmišlja, kaj storiti naprej, in deluje — prav tako kot bi to storila oseba.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Ko je pri miru, deluje po lastnih željah: radovednost, želja po pogledu zunaj, pogrešanje osebe, s katero živi.

## Kako začeti

### 1. Namestite uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Ali: `winget install astral-sh.uv`

### 2. Namestite ffmpeg

ffmpeg je **zahtevan** za zajemanje slik iz kamere in predvajanje zvoka.

| OS | Ukaz |
|----|------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ali prenesite s [ffmpeg.org](https://ffmpeg.org/download.html) in dodajte v PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Preverite: `ffmpeg -version`

### 3. Klonirajte in namestite

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurirajte

```bash
cp .env.example .env
# Uredite .env s svojimi nastavitvami
```

**Minimalno zahtevano:**

| Spremenljivka | Opis |
|---------------|------|
| `PLATFORM` | `anthropic` (privzeto) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Vaš API ključ za izbrano platformo |

**Opcionalno:**

| Spremenljivka | Opis |
|---------------|------|
| `MODEL` | Ime modela (smiselne privzete nastavitve na platformi) |
| `AGENT_NAME` | Prikazano ime v TUI (npr. `Yukine`) |
| `CAMERA_HOST` | IP naslov vaše ONVIF/RTSP kamere |
| `CAMERA_USER` / `CAMERA_PASS` | Akreditivi kamere |
| `ELEVENLABS_API_KEY` | Za glasovni izhod — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, da omogočite vseprisoten brezrokovni glasovni vhod (zahteva `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kje predvajati zvok: `local` (zvočnik računalnika, privzeto) \| `remote` (zvočnik kamere) \| `both` |
| `THINKING_MODE` | Le za Anthropic — `auto` (privzeto) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Prilagodljiv napor pri razmišljanju: `high` (privzeto) \| `medium` \| `low` \| `max` (samo Opus 4.6) |

### 5. Ustvarite svojega spremljevalca

```bash
cp persona-template/en.md ME.md
# Uredite ME.md — dajte mu ime in osebnost
```

### 6. Zaženite

**macOS / Linux / WSL2:**
```bash
./run.sh             # Besedilni TUI (priporočeno)
./run.sh --no-tui    # Navaden REPL
```

**Windows:**
```bat
run.bat              # Besedilni TUI (priporočeno)
run.bat --no-tui     # Navaden REPL
```

---

## Izbira LLM

> **Priporočeno: Kimi K2.5** — najboljša agentna učinkovitost, ki jo testiramo do sedaj. Upošteva kontekst, postavlja nadaljnja vprašanja in deluje avtonomno na načine, ki jih drugi modeli ne. Cena je podobna Claude Haiku.

| Platforma | `PLATFORM=` | Privzeti model | Kje pridobiti ključ |
|-----------|-------------|----------------|---------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibilni (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (več ponudnikov) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI orodje** (claude -p, ollama…) | `cli` | (ukaz) | — |

**Primer `.env` za Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # iz platform.moonshot.ai
AGENT_NAME=Yukine
```

**Primer `.env` za Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # iz api.z.ai
MODEL=glm-4.6v   # podprt vizualno; glm-4.7 / glm-5 = samo besedilo
AGENT_NAME=Yukine
```

**Primer `.env` za Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # iz aistudio.google.com
MODEL=gemini-2.5-flash  # ali gemini-2.5-pro za višjo zmogljivost
AGENT_NAME=Yukine
```

**Primer `.env` za OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # iz openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcionalno: določite model
AGENT_NAME=Yukine
```

> **Opomba:** Da onemogočite lokalne/NVIDIA modele, preprosto ne nastavite `BASE_URL` na lokalno končno točko, kot je `http://localhost:11434/v1`. Namesto tega uporabite oblačne ponudnike.

**Primer `.env` za CLI orodje:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argument za poziv
# MODEL=ollama run gemma3:27b  # Ollama — brez {}, poziv gre preko stdin
```

---

## MCP Strežniki

familiar-ai se lahko poveže s katerim koli [MCP (Model Context Protocol)](https://modelcontextprotocol.io) strežnikom. To vam omogoča, da vklopite zunanji spomin, dostop do datotečnega sistema, iskanje po spletu ali katero koli drugo orodje.

Konfigurirajte strežnike v `~/.familiar-ai.json` (isti format kot Claude Code):

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

Podprta sta dva tipa prenosa:
- **`stdio`**: zagon lokalnega podprocesa (`command` + `args`)
- **`sse`**: povezava s HTTP+SSE strežnikom (`url`)

Prepisujte lokacijo konfiguracijske datoteke z `MCP_CONFIG=/pot/do/config.json`.

---

## Strojna oprema

familiar-ai deluje z vsemi napravami, ki jih imate — ali pa tudi brez njih.

| Del | Kaj počne | Primer | Zahtevano? |
|-----|-----------|---------|------------|
| Wi-Fi PTZ kamera | Oči + vrat | Tapo C220 (~30 $, Eufy C220) | **Priporočeno** |
| USB kamera | Oči (fiksne) | Vsaka UVC kamera | **Priporočeno** |
| Robotski sesalnik | Noge | Vsak model, ki je združljiv s Tuya | Ne |
| Računalnik / Raspberry Pi | Možgani | Kakršna koli naprava, ki deluje v Pythonu | **Da** |

> **Kamera je zelo priporočena.** Brez nje lahko familiar-ai še vedno govori — vendar ne more videti sveta, kar je nekako njegov glavni namen.

### Minimalna nastavitev (brez strojne opreme)

Želite le poskusiti? Potrebujete le API ključ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Zaženite `./run.sh` (macOS/Linux/WSL2) ali `run.bat` (Windows) in začnite klepetati. Dodajte strojno opremo po potrebi.

### Wi-Fi PTZ kamera (Tapo C220)

1. V aplikaciji Tapo: **Nastavitve → Napredno → Račun kamere** — ustvarite lokalni račun (ne TP-Link račun)
2. Poiščite IP kamere v seznamu naprav vašega usmerjevalnika
3. Nastavite v `.env`:
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

1. Pridobite API ključ na [elevenlabs.io](https://elevenlabs.io/)
2. Nastavite v `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcionalno, uporablja privzeti glas, če ni določeno
   ```

Obstajajo dve destinaciji predvajanja, ki ju nadzira `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # zvočnik računalnika (privzeto)
TTS_OUTPUT=remote   # samo zvočnik kamere
TTS_OUTPUT=both     # zvočnik kamere + zvočnik računalnika hkrati
```

#### A) Zvočnik kamere (prek go2rtc)

Nastavite `TTS_OUTPUT=remote` (ali `both`). Zahteva [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Prenesite binarno datoteko s [strani izdaj](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Postavite in preimenujte:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # potrebno je chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Ustvarite `go2rtc.yaml` v isti imenik:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Uporabite akreditive lokalnega računa kamere (ne vašega TP-Link oblačnega računa).

4. familiar-ai samodejno zažene go2rtc ob zagonu. Če vaša kamera podpira dvosmerni zvok (povratni kanal), se glas predvaja iz zvočnika kamere.

#### B) Lokalen zvočnik računalnika

Privzeti (`TTS_OUTPUT=local`). Poskusi predvajalnike v tem vrstnem redu: **paplay** → **mpv** → **ffplay**. Uporablja se tudi kot varnostna možnost, ko je `TTS_OUTPUT=remote` in go2rtc ni na voljo.

| OS | Namestitev |
|----|------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ali `paplay` preko `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — nastavite `PULSE_SERVER=unix:/mnt/wslg/PulseServer` v `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — prenesite in dodajte v PATH, **ali** `winget install ffmpeg` |

> Če ni na voljo nobenega predvajalnika, se govor še vedno generira — le ne bo se predvajal.

### Glasovni vhod (Realtime STT)

Nastavite `REALTIME_STT=true` v `.env` za vseprisoten, brezrokovni glasovni vhod:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # isti ključ kot TTS
```

familiar-ai pretaka avdio iz mikrofona v ElevenLabs Scribe v2 in samodejno shrani transkripte, ko prenehate govoriti. Ni potrebe po pritisku na gumb. Koexistira z načinom pritisni-za-govor (Ctrl+T).

---

## TUI

familiar-ai vključuje terminalski UI, zgrajen s [Textual](https://textual.textualize.io/):

- Zgodovina pogovora, ki jo je mogoče pomikati s sprotnim pretakanjem besedila
- Dopolnjevanje za ukaze `/quit`, `/clear`
- Prekinitev delovanja agenta s tipkanjem, ko razmišlja
- **Dnevnik pogovora** se samodejno shranjuje v `~/.cache/familiar-ai/chat.log`

Da sledite dnevniku v drugem terminalu (koristno za kopiranje-in-lepljenje):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Osebnost (ME.md)

Osebnost vašega spremljevalca živi v `ME.md`. Ta datoteka je gitignored — je vaša.

Poglejte [`persona-template/en.md`](./persona-template/en.md) za primer, ali [`persona-template/ja.md`](./persona-template/ja.md) za različico v japonščini.

---

## Pogosta vprašanja

**Q: Ali deluje brez GPU?**
Da. Model za embeddings (multilingual-e5-small) deluje dobro na CPU. GPU ga pospeši, a ni obvezen.

**Q: Ali lahko uporabim kamero, ki ni Tapo?**
Vsaka kamera, ki podpira Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: Ali so moji podatki poslani nekam?**
Slike in besedilo so poslana na vašo izbrano LLM API za obdelavo. Spomini so shranjeni lokalno v `~/.familiar_ai/`.

**Q: Zakaj agent piše `（...）` namesto, da govori?**
Prepričajte se, da je nastavljen `ELEVENLABS_API_KEY`. Brez tega je glas onemogočen in agent preide na besedilo.

## Tehnična ozadja

Ste radovedni, kako deluje? Oglejte si [docs/technical.md](./docs/technical.md) za raziskave in oblikovne odločitve, ki stojijo za familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistem želja in še več.

---

## Prispevanje

familiar-ai je odprt eksperiment. Če vam karkoli od tega ustreza — tehnično ali filozofsko — so prispevki zelo dobrodošli.

**Dobre točke za začetek:**

| Področje | Kaj je potrebno |
|----------|-----------------|
| Nova strojna oprema | Podpora za več kamer (RTSP, IP Webcam), mikrofone, aktuatorje |
| Nova orodja | Iskanje po spletu, avtomatizacija doma, koledar, karkoli preko MCP |
| Nova ozadja | Kateri koli LLM ali lokalni model, ki ustreza vmesniku `stream_turn` |
| Predloge osebnosti | Predloge ME.md za različne jezike in osebnosti |
| Raziskovanje | Boljši modeli želja, iskanje spomina, izzivanje teorije uma |
| Dokumentacija | Vodniki, navodila, prevodi |

Oglejte si [CONTRIBUTING.md](./CONTRIBUTING.md) za nastavitev za razvoj, slog kode in smernice za PR.

Če niste prepričani, kje začeti, [odprite težavo](https://github.com/lifemate-ai/familiar-ai/issues) — z veseljem vas usmerimo v pravo smer.

---

## Licenca

[MIT](./LICENSE)
