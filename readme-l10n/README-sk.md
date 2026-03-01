# familiar-ai 🐾

**AI, ktorá žije po tvojom boku** — s očami, hlasom, nohami a pamäťou.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Dostupné v 74 jazykoch](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI spoločník, ktorý žije vo vašej domácnosti.
Nastavte ho za pár minút. Nie sú potrebné žiadne kódy.

Vníma reálny svet prostredníctvom kamier, pohybuje sa na robotickom tele, hovorí nahlas a pamätá si, čo vidí. Dajte mu meno, napíšte jeho osobnosť a nechajte ho žiť s vami.

## Čo dokáže

- 👁 **Vidieť** — zachytáva obrázky z Wi-Fi PTZ kamery alebo USB webkamery
- 🔄 **Pozerať sa okolo** — panning a naklonenie kamery na preskúmanie okolia
- 🦿 **Pohybovať sa** — jazdí na robotickom vysávači po miestnosti
- 🗣 **Hovoriť** — hovorí cez ElevenLabs TTS
- 🎙 **Počúvať** — hlasový vstup bez rúk cez ElevenLabs Realtime STT (opt-in)
- 🧠 **Pamätať si** — aktívne ukladá a pripomína si spomienky pomocou sémantického vyhľadávania (SQLite + embeddings)
- 🫀 **Teória mysle** — zohľadňuje perspektívu druhej osoby pred odpovedaním
- 💭 **Túžba** — má svoje vnútorné podnety, ktoré spúšťajú autonómne správanie

## Ako to funguje

familiar-ai prevádzkuje [ReAct](https://arxiv.org/abs/2210.03629) slučku, ktorú poháňa váš výber LLM. Vníma svet cez nástroje, premýšľa, čo robiť ďalej, a koná — presne ako by to robil človek.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Keď je neaktívny, jedná podľa svojich vlastných túžob: zvedavosť, túžba pozerať sa vonku, chýbanie osoby, s ktorou žije.

## Začíname

### 1. Nainštalujte uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Alebo: `winget install astral-sh.uv`

### 2. Nainštalujte ffmpeg

ffmpeg je **povinný** na zachytávanie obrázkov z kamier a prehrávanie zvuku.

| OS | Príkaz |
|----|--------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — alebo stiahnuť z [ffmpeg.org](https://ffmpeg.org/download.html) a pridať do PATH |
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
# Upravte .env so svojimi nastaveniami
```

**Minimálne požadované:**

| Premenná | Opis |
|----------|------|
| `PLATFORM` | `anthropic` (predvolené) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Váš API kľúč pre vybranú platformu |

**Voliteľné:**

| Premenná | Opis |
|----------|------|
| `MODEL` | Názov modelu (rozumné predvolené hodnoty podľa platformy) |
| `AGENT_NAME` | Zobrazované meno zobrazené v TUI (napr. `Yukine`) |
| `CAMERA_HOST` | IP adresa vašej ONVIF/RTSP kamery |
| `CAMERA_USER` / `CAMERA_PASS` | Prihlasovacie údaje kamery |
| `ELEVENLABS_API_KEY` | Pre výstup hlasu — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` na aktiváciu neustáleho hlasového vstupu bez rúk (vyžaduje `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kde prehrávať zvuk: `local` (reproduktor PC, predvolené) \| `remote` (reproduktor kamery) \| `both` |
| `THINKING_MODE` | Iba Anthropic — `auto` (predvolené) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptívny myšlienkový výkon: `high` (predvolené) \| `medium` \| `low` \| `max` (iba Opus 4.6) |

### 5. Vytvorte svojho spoločníka

```bash
cp persona-template/en.md ME.md
# Upravte ME.md — dajte mu meno a osobnosť
```

### 6. Spustite

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textový TUI (odporúčané)
./run.sh --no-tui    # Jednoduchý REPL
```

**Windows:**
```bat
run.bat              # Textový TUI (odporúčané)
run.bat --no-tui     # Jednoduchý REPL
```

---

## Výber LLM

> **Odporúčané: Kimi K2.5** — najlepšia agentická výkonnosť testovaná doteraz. Všímava kontext, kladie následné otázky a jedná autonómne spôsobmi, akými iné modely nie. Cenovo porovnateľné s Claude Haiku.

| Platforma | `PLATFORM=` | Predvolený model | Kde získať kľúč |
|-----------|-------------|------------------|------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Kompatibilný s OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI nástroj** (claude -p, ollama…) | `cli` | (príkaz) | — |

**Príklad `.env` pre Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # z platform.moonshot.ai
AGENT_NAME=Yukine
```

**Príklad `.env` pre Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # z api.z.ai
MODEL=glm-4.6v   # s podporou pre víziu; glm-4.7 / glm-5 = iba text
AGENT_NAME=Yukine
```

**Príklad `.env` pre Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # z aistudio.google.com
MODEL=gemini-2.5-flash  # alebo gemini-2.5-pro pre vyššiu schopnosť
AGENT_NAME=Yukine
```

**Príklad `.env` pre OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # z openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # voliteľné: špecifikujte model
AGENT_NAME=Yukine
```

> **Poznámka:** Na zakázanie miestnych/NVIDIA modelov jednoducho nenastavujte `BASE_URL` na miestny koncový bod ako `http://localhost:11434/v1`. Použite namiesto toho cloudových providerov.

**Príklad `.env` pre CLI nástroj:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argument prompt
# MODEL=ollama run gemma3:27b  # Ollama — bez {}, prompt ide cez stdin
```

---

## MCP Servery

familiar-ai sa môže pripojiť k akémukoľvek [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serveru. To vám umožní zapojiť externú pamäť, prístup k súborom, webové vyhľadávanie alebo akýkoľvek iný nástroj.

Nastavte servery v `~/.familiar-ai.json` (rovnaký formát ako Claude Code):

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

Podporované sú dva typy prenosu:
- **`stdio`**: spustenie miestneho subprocessu (`command` + `args`)
- **`sse`**: pripojenie k HTTP+SSE serveru (`url`)

Prepisujte umiestnenie konfiguračného súboru pomocou `MCP_CONFIG=/cesta/k/konfiguracnemu.json`.

---

## Hardvér

familiar-ai funguje s akýmkoľvek hardvérom, ktorý máte — alebo úplne bez neho.

| Časť | Čo robí | Príklad | Povinné? |
|------|---------|---------|---------|
| Wi-Fi PTZ kamera | Oči + krk | Tapo C220 (~30 USD) | **Odporúčané** |
| USB webkamera | Oči (pevné) | Akákoľvek UVC kamera | **Odporúčané** |
| Robotický vysávač | Nohy | Akýkoľvek model kompatibilný s Tuya | Nie |
| PC / Raspberry Pi | Mozog | Čokoľvek, čo spustí Python | **Áno** |

> **Kamera je silne odporúčaná.** Bez nej môže familiar-ai stále hovoriť — ale nemôže vidieť svet, čo je vlastne celý zmysel.

### Minimalistické nastavenie (bez hardvéru)

Chcete to len vyskúšať? Potrebujete iba API kľúč:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Spustite `./run.sh` (macOS/Linux/WSL2) alebo `run.bat` (Windows) a začnite chatovať. Pridajte hardvér pri ceste.

### Wi-Fi PTZ kamera (Tapo C220)

1. V aplikácii Tapo: **Nastavenia → Pokročilé → Účet kamery** — vytvorte lokálny účet (nie účet TP-Link)
2. Nájdite IP kameru vo svojom zozname zariadení routera
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

Existujú dva výstupné miesta, ovládané `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Reproduktor PC (predvolené)
TTS_OUTPUT=remote   # Iba reproduktor kamery
TTS_OUTPUT=both     # Reproduktor kamery + reproduktor PC súčasne
```

#### A) Reproduktor kamery (cez go2rtc)

Nastavte `TTS_OUTPUT=remote` (alebo `both`). Vyžaduje [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Stiahnite si binárny súbor z [stránky vydania](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Umiestnite a premenovajte ho:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x potrebné

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Vytvorte `go2rtc.yaml` v rovnakom adresári:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Použite miestne prihlasovacie údaje kamery (nie váš účet TP-Link cloud).

4. familiar-ai automaticky spúšťa go2rtc pri spustení. Ak vaša kamera podporuje obojsmerný zvuk (spätný kanál), hlas sa prehráva z reproduktora kamery.

#### B) Miestny reproduktor PC

Predvolené (`TTS_OUTPUT=local`). Snaží sa o prehrávače v poradí: **paplay** → **mpv** → **ffplay**. Tiež sa používa ako záložný plán, keď je `TTS_OUTPUT=remote` a go2rtc nie je dostupný.

| OS | Inštalácia |
|----|------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (alebo `paplay` cez `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — nastavte `PULSE_SERVER=unix:/mnt/wslg/PulseServer` v `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — stiahnite a pridajte do PATH, **alebo** `winget install ffmpeg` |

> Ak nie je k dispozícii žiadny prehrávač zvuku, reč sa stále generuje — jednoducho sa neprehrá.

### Hlasový vstup (Realtime STT)

Nastavte `REALTIME_STT=true` v `.env` pre neustály, bezhandský hlasový vstup:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # rovnaký kľúč ako TTS
```

familiar-ai streamuje zvuk z mikrofónu do ElevenLabs Scribe v2 a automaticky ukladá prepisy, keď prestanete hovoriť. Nie je potrebné žiadne stlačenie tlačidla. Existuje súbežne s režimom stlačenia na rozprávanie (Ctrl+T).

---

## TUI

familiar-ai obsahuje terminálové UI postavené na [Textual](https://textual.textualize.io/):

- Posúvateľná história konverzácie so živým streamovaným textom
- Automatické doplnenie pre `/quit`, `/clear`
- Prestaňte agenta v polovičnej odpovedi tak, že budete písať, kým premýšľa
- **Záznam konverzácie** automaticky uložený do `~/.cache/familiar-ai/chat.log`

Aby ste mohli sledovať záznam v inom termináli (užitočné na kopírovanie a prilepenie):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Osobnosť vášho spoločníka žije v `ME.md`. Tento súbor je ignorovaný gitom — je len váš.

Pozrite sa na [`persona-template/en.md`](./persona-template/en.md) pre príklad, alebo [`persona-template/ja.md`](./persona-template/ja.md) pre japonskú verziu.

---

## FAQ

**Q: Funguje to bez GPU?**
Áno. Model embedding (multilingual-e5-small) beží bez problémov na CPU. GPU robí výkon rýchlejším, ale nie je potrebný.

**Q: Môžem použiť kameru, ktorá nie je Tapo?**
Akákoľvek kamera, ktorá podporuje ONVIF + RTSP, by mala fungovať. Tapo C220 je to, s čím sme testovali.

**Q: Je moje údaje niekam odosielané?**
Obrázky a text sú odosielané do vybranej LLM API na spracovanie. Spomienky sú uložené lokálne v `~/.familiar_ai/`.

**Q: Prečo agent píše `（...）` namiesto rozprávania?**
Uistite sa, že `ELEVENLABS_API_KEY` je nastavený. Bez neho je hlas zakázaný a agent prechádza na text.

## Technické pozadie

Zaujíma vás, ako to funguje? Pozrite sa na [docs/technical.md](./docs/technical.md) pre výskum a rozhodnutia o dizajne za familiar-ai — ReAct, SayCan, Reflexion, Voyager, systém túžby a ďalšie.

---

## Prispievanie

familiar-ai je otvorený experiment. Ak vám niečo z toho rezonuje — technicky alebo filozoficky — príspevky sú veľmi vítané.

**Dobré miesta na začatie:**

| Oblasť | Čo je potrebné |
|--------|----------------|
| Nový hardvér | Podpora pre viac kamier (RTSP, IP Webcam), mikrofóny, akčné členy |
| Nové nástroje | Webové vyhľadávanie, automatizácia domácnosti, kalendár, čokoľvek cez MCP |
| Nové backendy | Akékoľvek LLM alebo miestny model, ktorý vyhovuje rozhraniu `stream_turn` |
| Šablóny persona | ME.md šablóny pre rôzne jazyky a osobnosti |
| Výskum | Lepšie modely túžby, vyhľadávanie pamäte, podnecovanie teórie mysle |
| Dokumentácia | Tutoriály, krok za krokom, preklady |

Pozrite sa na [CONTRIBUTING.md](./CONTRIBUTING.md) pre nastavenie vývoja, štýl kódu a pokyny pre PR.

Ak si nie ste istí, kde začať, [otvorte problém](https://github.com/lifemate-ai/familiar-ai/issues) — radi vás nasmerujeme správnym smerom.

---

## Licencia

[MIT](./LICENSE)
