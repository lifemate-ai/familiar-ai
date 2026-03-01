# familiar-ai 🐾

**Umelá inteligencia, ktorá žije vedľa vás** — s očami, hlasom, nohami a pamäťou.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI spoločník, ktorý žije vo vašej domácnosti. Nastavte ho za pár minút. Nie je potrebné žiadne kódovanie.

Vníma skutočný svet cez kamery, pohybuje sa na robotickom tele, rozpráva nahlas a pamätá si to, čo vidí. Dajte mu meno, napíšte jeho osobnosť a nechajte ho žiť s vami.

## Čo dokáže

- 👁 **Vidieť** — zachytáva obrázky z Wi-Fi PTZ kamery alebo USB webkamery
- 🔄 **Pozerať sa okolo** — otáča a nakláňa kameru, aby preskúmala okolité prostredie
- 🦿 **Hýbať sa** — poháňa robotický vysávač, aby sa pohyboval po miestnosti
- 🗣 **Hovoriť** — hovorí cez ElevenLabs TTS
- 🎙 **Počúvať** — hlasový vstup hands-free cez ElevenLabs Realtime STT (po súhlase)
- 🧠 **Pamätať** — aktívne ukladá a vyvoláva spomienky so semantickým vyhľadávaním (SQLite + embeddings)
- 🫀 **Teória mysle** — berie do úvahy perspektívu druhej osoby pred tým, ako odpovie
- 💭 **Túžba** — má svoje vlastné vnútorné pohony, ktoré spúšťajú autonómne správanie

## Ako to funguje

familiar-ai prevádzkuje [ReAct](https://arxiv.org/abs/2210.03629) slučku poháňanú vašou voľbou LLM. Vníma svet cez nástroje, premýšľa, čo robiť ďalej, a koná — presne ako by to urobil človek.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Keď je nečinný, jedná podľa svojich túžob: zvedavosť, chcú sa pozrieť von, chýba mu osoba, s ktorou žije.

## Začiatok

### 1. Nainštalujte uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Nainštalujte ffmpeg

ffmpeg je **povinný** pre zachytávanie obrázkov z kamery a prehrávanie zvuku.

| OS | Príkaz |
|----|--------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — alebo stiahnite z [ffmpeg.org](https://ffmpeg.org/download.html) a pridajte do PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Overte: `ffmpeg -version`

### 3. Klonujte a nainštalujte

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurujte

```bash
cp .env.example .env
# Upravte .env podľa svojich nastavení
```

**Minimálne požiadavky:**

| Premenná | Popis |
|----------|-------|
| `PLATFORM` | `anthropic` (predvolené) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Váš API kľúč pre vybranú platformu |

**Voliteľné:**

| Premenná | Popis |
|----------|-------|
| `MODEL` | Názov modelu (rozumné predvolené hodnoty podľa platformy) |
| `AGENT_NAME` | Zobrazované meno v TUI (napr. `Yukine`) |
| `CAMERA_HOST` | IP adresa vašej ONVIF/RTSP kamery |
| `CAMERA_USER` / `CAMERA_PASS` | Prihlasovacie údaje kamery |
| `ELEVENLABS_API_KEY` | Pre hlasový výstup — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` na povolenie trvalého hlasového vstupu hands-free (vyžaduje `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Miesto prehrávania zvuku: `local` (PC reproduktor, predvolené) \| `remote` (reproduktor kamery) \| `both` |
| `THINKING_MODE` | Iba Anthropic — `auto` (predvolené) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptívny mentálny výkon: `high` (predvolené) \| `medium` \| `low` \| `max` (iba Opus 4.6) |

### 5. Vytvorte svojho spoločníka

```bash
cp persona-template/en.md ME.md
# Upravte ME.md — dajte mu meno a osobnosť
```

### 6. Spustite

```bash
./run.sh             # Textové TUI (odporúčané)
./run.sh --no-tui    # Čistý REPL
```

---

## Výber LLM

> **Odporúča sa: Kimi K2.5** — najlepší agentický výkon zatiaľ testovaný. Všimne si kontext, kladie doplňujúce otázky a jedná autonómne tak, ako to iné modely nerobia. Cenu má podobnú ako Claude Haiku.

| Platforma | `PLATFORM=` | Predvolený model | Kde získať kľúč |
|-----------|------------|------------------|------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibilné (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI nástroj** (claude -p, ollama…) | `cli` | (príkaz) | — |

**Kimi K2.5 `.env` príklad:**
```env
PLATFORM=kimi
API_KEY=sk-...   # z platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` príklad:**
```env
PLATFORM=glm
API_KEY=...   # z api.z.ai
MODEL=glm-4.6v   # valorový enabled; glm-4.7 / glm-5 = iba text
AGENT_NAME=Yukine
```

**Google Gemini `.env` príklad:**
```env
PLATFORM=gemini
API_KEY=AIza...   # z aistudio.google.com
MODEL=gemini-2.5-flash  # alebo gemini-2.5-pro pre vyššie možnosti
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` príklad:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # z openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # voliteľné: špecifikujte model
AGENT_NAME=Yukine
```

> **Poznámka:** Ak chcete zakázať miestne/NVIDIA modely, jednoducho nenastavujte `BASE_URL` na miestny koncový bod ako `http://localhost:11434/v1`. Použite namiesto toho cloudových poskytovateľov.

**CLI nástroj `.env` príklad:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — žiadna {}, prompt prechádza cez stdin
```

---

## MCP Servery

familiar-ai sa môže pripojiť k akémukoľvek [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serveru. To vám umožňuje pripojiť externú pamäť, prístup k súborovému systému, webové vyhľadávanie alebo akýkoľvek iný nástroj.

Konfigurujte servery v `~/.familiar-ai.json` (rovnaký formát ako Claude Code):

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

Podporujú sa dva typy prenosu:
- **`stdio`**: spustite miestne spracovanie (`command` + `args`)
- **`sse`**: pripojte sa k HTTP+SSE serveru (`url`)

Prepisujte umiestnenie konfiguračného súboru s `MCP_CONFIG=/path/to/config.json`.

---

## Hardvér

familiar-ai funguje s akýmkoľvek hardvérom, ktorý máte — alebo žiadnym.

| Diel | Čo robí | Príklad | Povinné? |
|------|---------|---------|----------|
| Wi-Fi PTZ kamera | Oči + krk | Tapo C220 (~30 dolárov) | **Odporúčané** |
| USB webkamera | Oči (pevné) | Akákoľvek UVC kamera | **Odporúčané** |
| Robotický vysávač | Nohy | Akýkoľvek model kompatibilný s Tuya | Nie |
| PC / Raspberry Pi | Mozog | Čokoľvek, čo spustí Python | **Áno** |

> **Kamera je silne odporúčaná.** Bez nej môže familiar-ai stále rozprávať — ale nemôže vidieť svet, čo je tak trochu celá pointa.

### Minimálne nastavenie (bez hardvéru)

Chcete si to len vyskúšať? Potrebujete len API kľúč:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Spustite `./run.sh` a začnite chatovať. Hardvér pridajte, keď budete chcieť.

### Wi-Fi PTZ kamera (Tapo C220)

1. V aplikácii Tapo: **Nastavenia → Rozšírené → Účet kamery** — vytvorte lokálny účet (nie TP-Link účet)
2. Nájdite IP adresu kamery v zozname zariadení vo vašom smerovači
3. Nastavte v `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Hlas (ElevenLabs)

1. Získajte API kľúč na [elevenlabs.io](https://elevenlabs.io/)
2. Nastavte v `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # voliteľné, používa predvolený hlas, ak je vynechané
   ```

Existujú dve destinácie prehrávania, ovládané `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC reproduktor (predvolené)
TTS_OUTPUT=remote   # len reproduktor kamery
TTS_OUTPUT=both     # reproduktor kamery + PC reproduktor súčasne
```

#### A) Reproduktor kamery (cez go2rtc)

Nastavte `TTS_OUTPUT=remote` (alebo `both`). Vyžaduje [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Stiahnite binárny súbor z [stránky vydaní](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Umiestnite a premenovať:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x required

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. V rovnakom adresári vytvorte `go2rtc.yaml`:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Použite miestne prihlasovacie údaje kamery (nie vašu TP-Link cloud účet).

4. familiar-ai automaticky spustí go2rtc pri spustení. Ak vaša kamera podporuje obojsmerný zvuk (záložný kanál), hlas sa reprodukuje z reproduktora kamery.

#### B) Lokálny PC reproduktor

Predvolené (`TTS_OUTPUT=local`). Snaží sa prehrávače v poradí: **paplay** → **mpv** → **ffplay**. Používa sa tiež ako záloha, keď je `TTS_OUTPUT=remote` a go2rtc nie je k dispozícii.

| OS | Nainštalujte |
|----|--------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (alebo `paplay` pomocou `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — nastavte `PULSE_SERVER=unix:/mnt/wslg/PulseServer` v `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — stiahnite a pridajte do PATH, **alebo** `winget install ffmpeg` |

> Ak nie je k dispozícii žiadny prehrávač zvuku, reč sa stále generuje — len sa neprehrá.

### Hlasový vstup (Realtime STT)

Nastavte `REALTIME_STT=true` v `.env` pre trvalý, hands-free hlasový vstup:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # rovnaký kľúč ako TTS
```

familiar-ai streamuje zvuk z mikrofónu do ElevenLabs Scribe v2 a automaticky ukladaje prepisy, keď prestanete hovoriť. Niet potreby stlačiť žiadne tlačidlo. Zároveň funguje s režimom stlačenia na rozprávanie (Ctrl+T).

---

## TUI

familiar-ai obsahuje terminálové UI postavené na [Textual](https://textual.textualize.io/):

- Posúvateľná história konverzácie s živým textom
- Doplňovanie tabuliek pre `/quit`, `/clear`
- Prerušte agenta uprostred jeho úvahy tým, že píšete, keď sa sústredí
- **Záznam konverzácie** automaticky uložený na `~/.cache/familiar-ai/chat.log`

Aby ste sledovali záznam v inom termináli (užitočné pre kopírovanie a vkladanie):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Osobnosť vášho spoločníka žije v `ME.md`. Tento súbor je gitignored — je len váš.

Pozrite sa na [`persona-template/en.md`](./persona-template/en.md) pre príklad alebo [`persona-template/ja.md`](./persona-template/ja.md) pre japonskú verziu.

---

## FAQ

**Q: Funguje to bez GPU?**
Áno. Model embedding (multilingual-e5-small) pracuje dobre na CPU. GPU to zrýchľuje, ale nie je to povinné.

**Q: Môžem použiť inú kameru ako Tapo?**
Akákoľvek kamera, ktorá podporuje ONVIF + RTSP, by mala fungovať. Tapo C220 je to, s čím sme testovali.

**Q: Sú moje údaje niekam posielané?**
Obrázky a texty sú odosielané na váš vybraný LLM API na spracovanie. Spomienky sa ukladajú lokálne v `~/.familiar_ai/`.

**Q: Prečo agent píše `（...）` namiesto toho, aby hovoril?**
Uistite sa, že je nastavený `ELEVENLABS_API_KEY`. Bez neho je hlas zakázaný a agent prechádza na text.

## Technické pozadie

Zaujíma vás, ako to funguje? Pozrite si [docs/technical.md](./docs/technical.md) pre výskum a dizajnové rozhodnutia za familiar-ai — ReAct, SayCan, Reflexion, Voyager, systém túžby a ďalšie.

---

## Prispievanie

familiar-ai je otvorený experiment. Ak vás niečo z toho oslovuje — technicky alebo filozoficky — príspevky sú veľmi vítané.

**Dobré miesta, kde začať:**

| Oblast | Čo je potrebné |
|--------|----------------|
| Nový hardvér | Podpora pre viac kamier (RTSP, IP Webcam), mikrofóny, akčné členy |
| Nové nástroje | Webové vyhľadávanie, automatizácia domácnosti, kalendár, čokoľvek cez MCP |
| Nové backendy | Akýkoľvek LLM alebo miestny model, ktorý vyhovuje rozhraniu `stream_turn` |
| Šablóny osobnosti | ME.md šablóny pre rôzne jazyky a osobnosti |
| Výskum | Lepšie modely túžby, vyhľadávanie pamäti, prompting teórie mysle |
| Dokumentácia | Tutoriály, prechody, preklad |

Pozrite sa na [CONTRIBUTING.md](./CONTRIBUTING.md) pre dev nastavenie, štýl kódu a PR smernice.

Ak si nie ste istí, kde začať, [otvorte problém](https://github.com/lifemate-ai/familiar-ai/issues) — radi vám ukážeme správny smer.

---

## Licencia

[MIT](./LICENSE)
