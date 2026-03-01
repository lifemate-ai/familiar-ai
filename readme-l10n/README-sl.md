# familiar-ai 🐾

**AI, ki živi ob vas** — z očmi, glasom, nogami in spominom.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI spremljevalec, ki živi v vašem domu. 
Nastavite ga v nekaj minutah. Ni potrebnega kodiranja.

Zamislite si, kako zaznava resnični svet preko kamer, se giblje na robotiziranem telesu, govori na glas in si zapomni, kar vidi. Dajte mu ime, oblikujte njegovo osebnost in pustite, naj živi z vami.

## Kaj lahko počne

- 👁 **Videti** — zajema slike iz Wi-Fi PTZ kamere ali USB spletne kamere
- 🔄 **Razgledati se** — premika in nagiba kamero, da raziskuje okolico
- 🦿 **Premikati se** — vozi robotski sesalnik po prostoru
- 🗣 **Govori** — govori preko ElevenLabs TTS
- 🎙 **Poslušaj** — brezrokovni glasovni vhod preko ElevenLabs Realtime STT (opt-in)
- 🧠 **Zapomniti si** — aktivno shrani in prikliče spomine z semantičnim iskanjem (SQLite + embeddings)
- 🫀 **Teorija uma** — upošteva perspektivo druge osebe pred odgovarjanjem
- 💭 **Želja** — ima svoje notranje vzgibe, ki sprožijo avtonomno vedenje

## Kako deluje

familiar-ai poganja [ReAct](https://arxiv.org/abs/2210.03629) zanko, ki jo napaja vaša izbira LLM. Zaznava svet preko orodij, razmišlja o naslednjih korakih in deluje — tako kot bi to storila oseba.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Ko je v stanju mirovanja, deluje na svoje lastne želje: radovednost, željo pogledati zunaj, pogrešanje osebe, s katero živi.

## Kako začeti

### 1. Namestite uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Namestite ffmpeg

ffmpeg je **potreben** za zajemanje slik s kamere in predvajanje zvoka.

| OS | Ukaz |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ali prenesite s [ffmpeg.org](https://ffmpeg.org/download.html) in dodajte v PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Potrdite: `ffmpeg -version`

### 3. Klonirajte in namestite

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurirajte

```bash
cp .env.example .env
# Uredite .env z vašimi nastavitvami
```

**Minimum zahtevan:**

| Spremenljivka | Opis |
|---------------|------|
| `PLATFORM` | `anthropic` (privzeto) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Vaš API ključ za izbrano platformo |

**Neposredno:**

| Spremenljivka | Opis |
|---------------|------|
| `MODEL` | Ime modela (smiselne privzete vrednosti za posamezne platforme) |
| `AGENT_NAME` | Prikazno ime v TUI (npr. `Yukine`) |
| `CAMERA_HOST` | IP naslov vaše ONVIF/RTSP kamere |
| `CAMERA_USER` / `CAMERA_PASS` | Kredenciali za kamero |
| `ELEVENLABS_API_KEY` | Za glasovni izhod — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, da omogočite vedno vklopljen brezrokovni glasovni vhod (zahteva `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kjer predvajati zvok: `local` (zvočnik računalnika, privzeto) \| `remote` (zvočnik kamere) \| `both` |
| `THINKING_MODE` | Le za Anthropica — `auto` (privzeto) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Prilagodljiv trud pri razmišljanju: `high` (privzeto) \| `medium` \| `low` \| `max` (samo Opus 4.6) |

### 5. Ustvarite svojega spremljevalca

```bash
cp persona-template/en.md ME.md
# Uredite ME.md — dajte mu ime in osebnost
```

### 6. Zaženite

```bash
./run.sh             # Besedilni TUI (priporočeno)
./run.sh --no-tui    # Navadni REPL
```

---

## Izbira LLM

> **Priporočeno: Kimi K2.5** — najboljša agentna zmogljivost do sedaj testirana. Upošteva kontekst, postavlja nadaljnja vprašanja in deluje avtonomno na načine, ki jih drugi modeli ne. Cene so primerljive s Claude Haiku.

| Platforma | `PLATFORM=` | Privzeti model | Kje dobiti ključ |
|-----------|------------|----------------|------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibilen (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
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
MODEL=glm-4.6v   # zmožnosti vizije; glm-4.7 / glm-5 = samo besedilo
AGENT_NAME=Yukine
```

**Primer `.env` za Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # iz aistudio.google.com
MODEL=gemini-2.5-flash  # ali gemini-2.5-pro za višje zmogljivosti
AGENT_NAME=Yukine
```

**Primer `.env` za OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # iz openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcijsko: določite model
AGENT_NAME=Yukine
```

> **Opomba:** Da onemogočite lokalne/NVIDIA modele, preprosto ne nastavite `BASE_URL` na lokalni konektor, kot je `http://localhost:11434/v1`. Uporabite raje ponudnike v oblaku.

**Primer CLI orodja `.env`:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argument zaprosila
# MODEL=ollama run gemma3:27b  # Ollama — brez {}, zaprosilo gre preko stdin
```

---

## MCP strežniki

familiar-ai se lahko poveže z vsakim [MCP (Model Context Protocol)](https://modelcontextprotocol.io) strežnikom. To vam omogoča priključitev zunanjega spomina, dostop do datotečnega sistema, iskanje po spletu ali katero koli drugo orodje.

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

Podprte so dva tipa transporta:
- **`stdio`**: zaženite lokalni podproces (`command` + `args`)
- **`sse`**: povežite se s HTTP+SSE strežnikom (`url`)

Prepisujte lokacijo konfiguracijske datoteke z `MCP_CONFIG=/path/to/config.json`.

---

## Strojna oprema

familiar-ai deluje z vsemi napravami, ki jih imate — ali pa sploh nobeno.

| Del | Kaj počne | Primer | Zahtevano? |
|-----|-----------|--------|------------|
| Wi-Fi PTZ kamera | Oči + vrat | Tapo C220 (~$30) | **Priporočeno** |
| USB spletna kamera | Oči (fiksni) | Katere koli UVC kamera | **Priporočeno** |
| Robotski sesalnik | Noge | Katerekoli model, združljiv s Tuya | Ne |
| PC / Raspberry Pi | Možgani | Česarkoli, kar deluje v Pythonu | **Da** |

> **Kamera se močno priporoča.** Brez nje lahko familiar-ai še vedno govori — vendar ne more videti sveta, kar je nekako celotna ideja.

### Minimalna nastavitev (brez strojne opreme)

Samo želite poskusiti? Potrebujete le API ključ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Zaženite `./run.sh` in začnite klepetati. Dodajte strojno opremo, ko greste.

### Wi-Fi PTZ kamera (Tapo C220)

1. V aplikaciji Tapo: **Nastavitve → Napredno → Račun kamere** — ustvarite lokalni račun (ne TP-Link račun)
2. Poiščite IP kamere v seznamu naprav v vašem usmerjevalniku
3. Nastavite v `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Glas (ElevenLabs)

1. Pridobite API ključ na [elevenlabs.io](https://elevenlabs.io/)
2. Nastavite v `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # neobvezno, uporablja privzeti glas, če je izpuščeno
   ```

Obstajata dva cilja predvajanja, ki jih nadzira `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Zvočnik računalnika (privzeto)
TTS_OUTPUT=remote   # Zvočnik kamere samo
TTS_OUTPUT=both     # Zvočnik kamere + Zvočnik računalnika hkrati
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

3. Ustvarite `go2rtc.yaml` v istem imeniku:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Uporabite lokalne kredenciale za kamerne račune (ne vaš TP-Link račun v oblaku).

4. familiar-ai samodejno zažene go2rtc ob zagonu. Če vaša kamera podpira dvosmerni zvok (povratna povezava), se glas predvaja iz zvočnika kamere.

#### B) Lokalni zvočnik računalnika

Privzeta nastavitev (`TTS_OUTPUT=local`). Poskusite predvajalnike v tem zaporedju: **paplay** → **mpv** → **ffplay**. Uporablja se tudi kot rezervna možnost, ko je `TTS_OUTPUT=remote` in go2rtc ni na voljo.

| OS | Namestitev |
|----|------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ali `paplay` prek `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — nastavite `PULSE_SERVER=unix:/mnt/wslg/PulseServer` v `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — prenesite in dodajte v PATH, **ali pa** `winget install ffmpeg` |

> Če ni na voljo nobenega predvajalnika zvoka, je govor še vedno generiran — le ne bo predvajan.

### Vhod z glasom (Realtime STT)

Nastavite `REALTIME_STT=true` v `.env` za vedno vklopljen, brezrokovni glasovni vhod:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # isti ključ kot TTS
```

familiar-ai streama avdio iz mikrofona v ElevenLabs Scribe v2 in samodejno shrani transkripte, ko prenehate govoriti. Ni potrebno pritiskati na gumb. Soobstoja z načinom pritisni za govor (Ctrl+T).

---

## TUI

familiar-ai vključuje terminalski uporabniški vmesnik, ustvarjen z [Textual](https://textual.textualize.io/):

- Pomik zgodovine pogovorov s tokom besedila v živo
- Dopolnjevanje zavihkov za `/quit`, `/clear`
- Prekinite agenta med razmišljanjem tako, da tipkate, medtem ko razmišlja
- **Dnevnik pogovorov** samodejno shranjen v `~/.cache/familiar-ai/chat.log`

Da sledite dnevniku v drugem terminalu (koristno za kopiranje in lepljenje):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Osebnost (ME.md)

Osebnost vašega spremljevalca živi v `ME.md`. Ta datoteka je izključena iz Git — je samo vaša.

Oglejte si [`persona-template/en.md`](./persona-template/en.md) za primer, ali [`persona-template/ja.md`](./persona-template/ja.md) za različico v japonščini.

---

## Pogosta vprašanja

**V: Ali deluje brez GPU?**
Da. Model za vdelovanje (multilingual-e5-small) deluje dobro na CPU. GPU ga pospeši, vendar ni potreben.

**V: Ali lahko uporabljam kamero, drugačno od Tapo?**
Vsaka kamera, ki podpira ONVIF + RTSP, bi morala delovati. Tapo C220 je bila testirana.

**V: Ali se moji podatki kamorkoli pošljejo?**
Slike in besedila se pošljejo izbrani LLM API za obdelavo. Spomini se shranjujejo lokalno v `~/.familiar_ai/`.

**V: Zakaj agent piše `（...）` namesto, da bi govoril?**
Prepričajte se, da je nastavljen `ELEVENLABS_API_KEY`. Brez njega je glas onemogočen in agent preide na besedilo.

## Tehnična ozadje

Ste radovedni, kako deluje? Oglejte si [docs/technical.md](./docs/technical.md) za raziskave in oblikovalske odločitve za familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistem želja in še več.

---

## Prispevanje

familiar-ai je odprt eksperiment. Če vam to, kar je rečeno, ustreza — tehnično ali filozofsko — so prispevki zelo dobrodošli.

**Dobre točke za začetek:**

| Področje | Kaj je potrebno |
|----------|-----------------|
| Nova strojna oprema | Podpora za več kamer (RTSP, IP Webcam), mikrofone, aktuatorje |
| Nova orodja | Iskanje po spletu, avtomatizacija doma, koledar, karkoli preko MCP |
| Nove povratne povezave | Kakršna koli LLM ali lokalni model, ki ustreza vmesniku `stream_turn` |
| Predloge osebnosti | Predloge ME.md za različne jezike in osebnosti |
| Raziskave | Boljši modeli želja, priklic spomina, spodbujanje teorije uma |
| Dokumentacija | Vadnice, vodniki, prevodi |

Oglejte si [CONTRIBUTING.md](./CONTRIBUTING.md) za nastavitev razvoja, slog kodiranja in smernice za PR.

Če niste prepričani, kje začeti, [odprite težavo](https://github.com/lifemate-ai/familiar-ai/issues) — z veseljem vas bomo usmerili v pravo smer.

---

## Licenca

[MIT](./LICENSE)
