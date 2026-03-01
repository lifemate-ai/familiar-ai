```markdown
# familiar-ai 🐾

**AI, který žije vedle vás** — s očima, hlasem, nohama a pamětí.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Dostupné ve 74 jazycích](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI společník, který žije ve vašem domě. 
Nastavte ho za pár minut. Nepotřebujete žádné kódování.

Vnímá reálný svět prostřednictvím kamer, pohybuje se na robotickém těle, mluví nahlas a pamatuje si, co vidí. Dejte mu jméno, napište jeho osobnost a nechte ho žít s vámi.

## Co dokáže

- 👁 **Vidět** — zachycuje obrázky z Wi-Fi PTZ kamery nebo USB webové kamery
- 🔄 **Ohlédnout se** — natáčí a naklání kameru, aby prozkoumala své okolí
- 🦿 **Pohybovat se** — ovládá robotický vysavač, aby se pohyboval po místnosti
- 🗣 **Mluvit** — mluví pomocí ElevenLabs TTS
- 🎙 **Poslouchat** — bezdrátový hlasový vstup pomocí ElevenLabs Realtime STT (opt-in)
- 🧠 **Pamatovat** — aktivně ukládá a vybavuje si vzpomínky s použitím sémantického vyhledávání (SQLite + embeddings)
- 🫀 **Teorie mysli** — přejímá perspektivu druhé osoby před odpovědí
- 💭 **Touha** — má své vlastní vnitřní pohony, které vyvolávají autonomní chování

## Jak to funguje

familiar-ai běží na [ReAct](https://arxiv.org/abs/2210.03629) smyčce napájeném vaší volbou LLM. Vnímá svět prostřednictvím nástrojů, přemýšlí, co dělat dál, a jedná — přesně jako by to udělal člověk.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Když je nečinný, jedná podle svých vlastních touh: zvědavost, chtění podívat se ven, stýskání si po osobě, se kterou žije.

## Začínáme

### 1. Nainstalujte uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Nebo: `winget install astral-sh.uv`

### 2. Nainstalujte ffmpeg

ffmpeg je **požadován** pro zachycení obrázků z kamery a přehrávání zvuku.

| OS | Příkaz |
|----|--------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — nebo stáhněte z [ffmpeg.org](https://ffmpeg.org/download.html) a přidejte do PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Ověřte: `ffmpeg -version`

### 3. Klonujte a nainstalujte

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurujte

```bash
cp .env.example .env
# Upravte .env se svými nastaveními
```

**Minimální požadavky:**

| Proměnná | Popis |
|----------|-------|
| `PLATFORM` | `anthropic` (výchozí) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Váš API klíč pro zvolenou platformu |

**Volitelné:**

| Proměnná | Popis |
|----------|-------|
| `MODEL` | Název modelu (rozumné výchozí hodnoty podle platformy) |
| `AGENT_NAME` | Zobrazované jméno ve TUI (např. `Yukine`) |
| `CAMERA_HOST` | IP adresa vaší ONVIF/RTSP kamery |
| `CAMERA_USER` / `CAMERA_PASS` | Přihlašovací údaje kamery |
| `ELEVENLABS_API_KEY` | Pro výstup hlasu — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` pro povolení hlasového vstupu bez použití rukou (vyžaduje `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kde přehrávat zvuk: `local` (reproduktor PC, výchozí) \| `remote` (reproduktor kamery) \| `both` |
| `THINKING_MODE` | Pouze Anthropic — `auto` (výchozí) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptivní míra úsilí o přemýšlení: `high` (výchozí) \| `medium` \| `low` \| `max` (pouze Opus 4.6) |

### 5. Vytvořte svého známého

```bash
cp persona-template/en.md ME.md
# Upravte ME.md — dejte mu jméno a osobnost
```

### 6. Spusťte

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textové TUI (doporučeno)
./run.sh --no-tui    # Prostý REPL
```

**Windows:**
```bat
run.bat              # Textové TUI (doporučeno)
run.bat --no-tui     # Prostý REPL
```

---

## Výběr LLM

> **Doporučeno: Kimi K2.5** — nejlepší agentní výkon, který byl dosud testován. Všímá si kontextu, klade doplňující otázky a jedná autonomně způsoby, které jiné modely nedělají. Cenově srovnatelné s Claude Haiku.

| Platforma | `PLATFORM=` | Výchozí model | Kde získat klíč |
|-----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibilní (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI nástroj** (claude -p, ollama…) | `cli` | (příkaz) | — |

**Příklad `.env` pro Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # z platform.moonshot.ai
AGENT_NAME=Yukine
```

**Příklad `.env` pro Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # z api.z.ai
MODEL=glm-4.6v   # s viděním; glm-4.7 / glm-5 = pouze text
AGENT_NAME=Yukine
```

**Příklad `.env` pro Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # z aistudio.google.com
MODEL=gemini-2.5-flash  # nebo gemini-2.5-pro pro vyšší schopnosti
AGENT_NAME=Yukine
```

**Příklad `.env` pro OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # z openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # volitelné: zadejte model
AGENT_NAME=Yukine
```

> **Pozor:** Pro zakázání místních/NVIDIA modelů jednoduše nenastavujte `BASE_URL` na místní koncový bod jako `http://localhost:11434/v1`. Místo toho použijte cloudové poskytovatele.

**Příklad `.env` pro CLI nástroj:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argument prompt
# MODEL=ollama run gemma3:27b  # Ollama — bez {}, prompt jde přes stdin
```

---

## MCP Servery

familiar-ai se može připojit k jakémukoli [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serveru. To vám umožňuje zapojit externí paměť, přístup k souborovému systému, webové vyhledávání nebo jakýkoli jiný nástroj.

Nakonfigurujte servery v `~/.familiar-ai.json` (stejný formát jako Claude Code):

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

Podporované jsou dva typy přenosu:
- **`stdio`**: spustit místní podproces (`command` + `args`)
- **`sse`**: připojit se k HTTP+SSE serveru (`url`)

Přepište umístění konfiguračního souboru pomocí `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai funguje s jakýmkoli hardwarem, který máte — nebo ani s jedním.

| Část | Co dělá | Příklad | Požadováno? |
|------|---------|---------|-------------|
| Wi-Fi PTZ kamera | Oči + krk | Tapo C220 (~$30) | **Doporučeno** |
| USB webová kamera | Oči (pevné) | Jakákoli UVC kamera | **Doporučeno** |
| Robotický vysavač | Nohy | Jakýkoli model kompatibilní s Tuya | Ne |
| PC / Raspberry Pi | Mozek | Cokoli, co spuští Python | **Ano** |

> **Kamera je velmi doporučena.** Bez ní může familiar-ai stále mluvit — ale nemůže vidět svět, což je vlastně celé to, o co jde.

### Minimální nastavení (bez hardwaru)

Chcete to jen vyzkoušet? Potřebujete jen API klíč:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Spusťte `./run.sh` (macOS/Linux/WSL2) nebo `run.bat` (Windows) a začněte chatovat. Přidejte hardware, jak budete pokračovat.

### Wi-Fi PTZ kamera (Tapo C220)

1. V aplikaci Tapo: **Nastavení → Pokročilé → Účet kamery** — vytvořte místní účet (ne TP-Link účet)
2. Najděte IP adresu kamery v seznamu zařízení vašeho routeru
3. Nastavte v `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Hlas (ElevenLabs)

1. Získejte API klíč na [elevenlabs.io](https://elevenlabs.io/)
2. Nastavte v `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # volitelné, používá výchozí hlas, pokud je vynecháno
   ```

Jsou zde dvě destinace přehrávání, ovládané `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # reproduktor PC (výchozí)
TTS_OUTPUT=remote   # pouze reproduktor kamery
TTS_OUTPUT=both     # reproduktor kamery + reproduktor PC současně
```

#### A) Reproduktor kamery (přes go2rtc)

Nastavte `TTS_OUTPUT=remote` (nebo `both`). Vyžaduje [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Stáhněte binární soubor z [stránky vydání](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Umístěte a přejmenujte jej:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x je požadováno

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Vytvořte `go2rtc.yaml` ve stejném adresáři:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Použijte přihlašovací údaje místního účtu kamery (ne svůj TP-Link cloud účet).

4. familiar-ai automaticky spouští go2rtc při spuštění. Pokud vaše kamera podporuje obousměrný audio (zpětný kanál), hlas se přehrává z reproduktoru kamery.

#### B) Lokální reproduktor PC

Výchozí (`TTS_OUTPUT=local`). Zkouší přehrávače v pořadí: **paplay** → **mpv** → **ffplay**. Také používán jako záloha, když je `TTS_OUTPUT=remote` a go2rtc není k dispozici.

| OS | Instalace |
|----|-----------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (nebo `paplay` přes `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — nastavte `PULSE_SERVER=unix:/mnt/wslg/PulseServer` v `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — stáhněte a přidejte do PATH, **nebo** `winget install ffmpeg` |

> Pokud žádný audio přehrávač není k dispozici, řeč je stále generována — jen se nebude přehrávat.

### Hlasový vstup (Realtime STT)

Nastavte `REALTIME_STT=true` v `.env` pro stále aktivní, bezdrátový hlasový vstup:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # stejný klíč jako pro TTS
```

familiar-ai streamuje zvuk mikrofonu do ElevenLabs Scribe v2 a automaticky ukládá přepisy, když přestanete mluvit. Není potřebné tisknutí tlačítka. Koexistuje s režimem stisknutí pro mluvení (Ctrl+T).

---

## TUI

familiar-ai obsahuje terminálové UI postavené s [Textual](https://textual.textualize.io/):

- Posouvatelná historie konverzace s živým textem
- Automatické doplňování pro `/quit`, `/clear`
- Přerušte agenta uprostřed myšlení tím, že začnete psát
- **Historie konverzace** automaticky ukládána do `~/.cache/familiar-ai/chat.log`

Chcete-li sledovat log v jiném terminálu (užitečné pro kopírování a vkládání):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Osobnost (ME.md)

Osobnost vašeho známého žije v `ME.md`. Tento soubor je gitignored — je jen váš.

Podívejte se na [`persona-template/en.md`](./persona-template/en.md) pro příklad, nebo [`persona-template/ja.md`](./persona-template/ja.md) pro verzi v japonštině.

---

## FAQ

**Q: Funguje to bez GPU?**
Ano. Model embedding (multilingual-e5-small) funguje dobře na CPU. GPU to zrychluje, ale není vyžadován.

**Q: Mohu použít jinou kameru než Tapo?**
Jakákoli kamera, která podporuje ONVIF + RTSP, by měla fungovat. Tapo C220 je to, co jsme testovali.

**Q: Odesílají se nějaká má data někam?**
Obrázky a texty jsou odesílány na vybranou LLM API k zpracování. Vzpomínky jsou ukládány lokálně v `~/.familiar_ai/`.

**Q: Proč agent píše `（...）` místo mluvení?**
Ujistěte se, že je nastaveno `ELEVENLABS_API_KEY`. Bez něj je hlas deaktivován a agent se vrátí k textu.

## Technické pozadí

Zajímá vás, jak to funguje? Podívejte se na [docs/technical.md](./docs/technical.md) pro výzkum a rozhodování o designu za familiar-ai — ReAct, SayCan, Reflexion, Voyager, systém touh a další.

---

## Přispívání

familiar-ai je otevřený experiment. Pokud vás něco z toho oslovuje — technicky nebo filozoficky — příspěvky jsou velmi vítány.

**Dobrým místem pro začátek:**

| Oblast | Co je potřeba |
|--------|---------------|
| Nový hardware | Podpora pro více kamer (RTSP, IP Webcam), mikrofony, aktuatory |
| Nové nástroje | Webové vyhledávání, domácí automatizace, kalendář, cokoliv přes MCP |
| Nové backendy | Jakýkoli LLM nebo lokální model, který vyhovuje rozhraní `stream_turn` |
| Šablony osobnosti | Šablony ME.md pro různé jazyky a osobnosti |
| Výzkum | Lepší modely touh, získávání paměti, vyvolávání teorie mysli |
| Dokumentace | Tutoriály, průvodce, překlady |

Podívejte se na [CONTRIBUTING.md](./CONTRIBUTING.md) pro nastavení vývoje, styl kódu a pokyny k PR.

Pokud si nejste jisti, kde začít, [otevřete issue](https://github.com/lifemate-ai/familiar-ai/issues) — rádi vám ukážeme správný směr.

---

## Licence

[MIT](./LICENSE)
```
