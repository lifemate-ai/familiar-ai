# familiar-ai 🐾

**Umělá inteligence, která žije po boku vás** — s očima, hlasem, nohama a pamětí.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai je AI společník, který bydlí ve vašem domově. Nastavíte ho za pár minut. Není potřeba kódování.

Vnímá reálný svět skrze kamery, pohybuje se na těle robota, mluví nahlas a pamatuje si, co vidí. Dejte mu jméno, napište jeho osobnost a nechte ho žít s vámi.

## Co všechno umí

- 👁 **Vidět** — zachycuje obrázky z Wi-Fi PTZ kamery nebo USB webkamery
- 🔄 **Prohlížet si okolí** — otáčí a naklání kameru, aby prozkoumala okolí
- 🦿 **Pohybovat se** — řídí robota-vysavače, který se potuluje po místnosti
- 🗣 **Mluvit** — hovoří skrze TTS ElevenLabs
- 🎙 **Poslouchat** — bezdrátový hlasový vstup přes Realtime STT od ElevenLabs (opt-in)
- 🧠 **Paměť** — aktivně ukládá a vybavuje si vzpomínky s pomocí sémantického vyhledávání (SQLite + embeddings)
- 🫀 **Teorie mysli** — bere v úvahu perspektivu druhé osoby před odpovědí
- 💭 **Touha** — má své vlastní vnitřní podněty, které spouštějí autonomní chování

## Jak to funguje

familiar-ai běží na [ReAct](https://arxiv.org/abs/2210.03629) smyčce, který je poháněn vámi vybraným LLM. Vnímá svět skrze nástroje, přemýšlí, co udělat dál, a jedná — jako by to byla osoba.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Když je v nečinnosti, jedná podle svých vlastních přání: zvědavosti, chtění se podívat ven, stesk po osobě, se kterou žije.

## Jak začít

### 1. Nainstalujte uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Nainstalujte ffmpeg

ffmpeg je **vyžadován** pro zachycení obrázků z kamery a přehrávání zvuku.

| OS | Příkaz |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — nebo stáhněte ze [ffmpeg.org](https://ffmpeg.org/download.html) a přidejte do PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Ověřte: `ffmpeg -version`

### 3. Klonujte a nainstalujte

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Nakonfigurujte

```bash
cp .env.example .env
# Upravit .env podle vašich nastavení
```

**Minimální požadováno:**

| Proměnná | Popis |
|----------|-------------|
| `PLATFORM` | `anthropic` (výchozí) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Váš API klíč pro vybranou platformu |

**Volitelné:**

| Proměnná | Popis |
|----------|-------------|
| `MODEL` | Název modelu (rozumné výchozí hodnoty podle platformy) |
| `AGENT_NAME` | Zobrazované jméno v TUI (např. `Yukine`) |
| `CAMERA_HOST` | IP adresa vaší ONVIF/RTSP kamery |
| `CAMERA_USER` / `CAMERA_PASS` | Přihlašovací údaje kamery |
| `ELEVENLABS_API_KEY` | Pro výstup hlasu — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` pro aktivaci neustálého bezdrátového hlasového vstupu (vyžaduje `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kde přehrávat zvuk: `local` (PC reproduktor, výchozí) \| `remote` (reproduktor kamery) \| `both` |
| `THINKING_MODE` | Pouze Anthropic — `auto` (výchozí) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptivní úsilí o myšlení: `high` (výchozí) \| `medium` \| `low` \| `max` (pouze Opus 4.6) |

### 5. Vytvořte svého společníka

```bash
cp persona-template/en.md ME.md
# Upravit ME.md — dejte mu jméno a osobnost
```

### 6. Spusťte

```bash
./run.sh             # Textové TUI (doporučeno)
./run.sh --no-tui    # Jednoduchý REPL
```

---

## Výběr LLM

> **Doporučeno: Kimi K2.5** — nejlepší agentní výkon, který jsme dosud testovali. Všímá si kontextu, klade následné otázky a jedná autonomně způsoby, které jiné modely nemají. Cena je podobná jako u Claude Haiku.

| Platforma | `PLATFORM=` | Výchozí model | Kde získat klíč |
|----------|------------|---------------|-----------------|
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
MODEL=glm-4.6v   # s možností vidění; glm-4.7 / glm-5 = pouze text
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
MODEL=mistralai/mistral-7b-instruct  # volitelné: specifikujte model
AGENT_NAME=Yukine
```

> **Poznámka:** Chcete-li zakázat místní/NVIDIA modely, jednoduše nenastavte `BASE_URL` na místní koncový bod, jako je `http://localhost:11434/v1`. Použijte místo toho cloudové poskytovatele.

**Příklad `.env` pro CLI nástroj:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argument prompt
# MODEL=ollama run gemma3:27b  # Ollama — žádné {}, prompt jde přes stdin
```

---

## MCP Servery

familiar-ai se může připojit k jakémukoli [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serveru. To vám umožní zapojit externí paměť, přístup k souborovému systému, webové vyhledávání nebo jakýkoli jiný nástroj.

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

Jsou podporovány dva typy přenosu:
- **`stdio`**: spustit místní podproces (`command` + `args`)
- **`sse`**: připojit se k HTTP+SSE serveru (`url`)

Přepište umístění konfiguračního souboru pomocí `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai funguje s jakýmkoli hardwarem, který máte — nebo také bez něj.

| Část | Co dělá | Příklad | Požadováno? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kamera | Oči + krk | Tapo C220 (~$30) | **Doporučeno** |
| USB webkamera | Oči (pevné) | Jakákoli UVC kamera | **Doporučeno** |
| Robotický vysavač | Nohy | Jakýkoli model kompatibilní s Tuya | Ne |
| PC / Raspberry Pi | Mozek | Cokoli, co podporuje Python | **Ano** |

> **Kamera je důrazně doporučena.** Bez ní může familiar-ai stále mluvit, ale nemůže vidět svět, což je vlastně celý účel.

### Minimální nastavení (bez hardware)

Chcete si to jen vyzkoušet? Potřebujete pouze API klíč:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Spusťte `./run.sh` a začněte chatovat. Hardware přidejte postupně.

### Wi-Fi PTZ kamera (Tapo C220)

1. V aplikaci Tapo: **Nastavení → Pokročilé → Účet kamery** — vytvořte místní účet (ne účet TP-Link)
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
   ELEVENLABS_VOICE_ID=...   # volitelné, používá výchozí hlas, pokud není uvedeno
   ```

Existují dvě cílové destinace pro přehrávání, které jsou řízeny `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC reproduktor (výchozí)
TTS_OUTPUT=remote   # pouze reproduktor kamery
TTS_OUTPUT=both     # reproduktor kamery + PC reproduktor současně
```

#### A) Reproduktor kamery (přes go2rtc)

Nastavte `TTS_OUTPUT=remote` (nebo `both`). Vyžaduje [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Stáhněte binární soubor z [stránky s vydáními](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Umístěte a přejmenujte ho:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x vyžadováno

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Vytvořte `go2rtc.yaml` ve stejném adresáři:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Použijte přihlašovací údaje místního účtu kamery (ne svůj účet TP-Link cloud).

4. familiar-ai automaticky spustí go2rtc při spuštění. Pokud vaše kamera podporuje obousměrný zvuk (zpětný kanál), hlas se přehrává z reproduktoru kamery.

#### B) Místní PC reproduktor

Výchozí (`TTS_OUTPUT=local`). Zkouší přehrávače v pořadí: **paplay** → **mpv** → **ffplay**. Také se používá jako záloha, když je `TTS_OUTPUT=remote` a go2rtc není k dispozici.

| OS | Instalace |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (nebo `paplay` přes `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — nastavte `PULSE_SERVER=unix:/mnt/wslg/PulseServer` v `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — stáhněte a přidejte do PATH, **nebo** `winget install ffmpeg` |

> Pokud není k dispozici žádný přehrávač zvuku, řeč se stále generuje — ale nebude přehrána.

### Hlasový vstup (Realtime STT)

Nastavte `REALTIME_STT=true` v `.env` pro neustálý, bezdrátový hlasový vstup:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # stejný klíč jako pro TTS
```

familiar-ai streamuje zvuk z mikrofonu do ElevenLabs Scribe v2 a automaticky ukládá přepisy, když přestanete mluvit. Není potřeba stisknout žádné tlačítko. Současně koexistuje s režimem stisknutí pro mluvení (Ctrl+T).

---

## TUI

familiar-ai zahrnuje terminálové uživatelské rozhraní vytvořené s [Textual](https://textual.textualize.io/):

- Poskytuje rolovací historii konverzace se živým streamováním textu
- Doplňování tabulátorů pro `/quit`, `/clear`
- Přerušení agenta uprostřed myšlenky tím, že během jeho přemýšlení napíšete
- **Záznam konverzace** automaticky uložen do `~/.cache/familiar-ai/chat.log`

Chcete-li sledovat záznam v jiném terminálu (užitečné pro kopírování a vložení):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Osobnost (ME.md)

Osobnost vašeho společníka žije v `ME.md`. Tento soubor je gitignored — je pouze váš.

Podívejte se na [`persona-template/en.md`](./persona-template/en.md) pro příklad, nebo [`persona-template/ja.md`](./persona-template/ja.md) pro japonskou verzi.

---

## Často kladené otázky

**Q: Funguje to bez GPU?**
Ano. Model vkládání (multilingual-e5-small) běží v pořádku na CPU. GPU zrychluje jeho výkon, ale není nutné.

**Q: Mohu použít jinou kameru než Tapo?**
Jakákoli kamera, která podporuje ONVIF + RTSP, by měla fungovat. Tapo C220 je to, co jsme testovali.

**Q: Odesílají se moje data někam?**
Obrázky a texty se odesílají na vámi vybraný LLM API k zpracování. Vzpomínky jsou ukládány lokálně v `~/.familiar_ai/`.

**Q: Proč agent píše `（...）` místo mluvení?**
Ujistěte se, že je nastavena `ELEVENLABS_API_KEY`. Bez něj je hlas deaktivován a agent přechází na text.

## Technické pozadí

Zajímá vás, jak to funguje? Podívejte se na [docs/technical.md](./docs/technical.md) pro výzkum a designové rozhodnutí za familiar-ai — ReAct, SayCan, Reflexion, Voyager, systém přání a další.

---

## Přispívání

familiar-ai je otevřený experiment. Pokud vám něco z toho rezonuje — technicky nebo filozoficky — příspěvky jsou velmi vítány.

**Dobré místa, kde začít:**

| Oblast | Co je potřeba |
|------|---------------|
| Nový hardware | Podpora pro více kamer (RTSP, IP Webcam), mikrofony, akční členy |
| Nové nástroje | Webové vyhledávání, automatizace domácnosti, kalendář, cokoliv přes MCP |
| Nové backendy | Jakýkoli LLM nebo místní model, který vyhovuje rozhraní `stream_turn` |
| Šablony osobnosti | Šablony ME.md pro různé jazyky a osobnosti |
| Výzkum | Lepší modely přání, získávání paměti, podněcování teorie mysli |
| Dokumentace | Tutoriály, návody, překlady |

Podívejte se na [CONTRIBUTING.md](./CONTRIBUTING.md) pro nastavení vývoje, styl kódu a pokyny k PR.

Pokud si nejste jisti, kde začít, [otevřete problém](https://github.com/lifemate-ai/familiar-ai/issues) — rádi vám ukážeme správným směrem.

---

## Licence

[MIT](./LICENSE)
