# familiar-ai 🐾

**Sztuczna inteligencja, która żyje obok ciebie** — z oczami, głosem, nogami i pamięcią.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Dostępne w 74 językach](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai to towarzysz AI, który żyje w twoim domu.  
Skonfiguruj go w kilka minut. Nie wymaga kodowania.

Postrzega prawdziwy świat przez kamery, porusza się na ciele robota, mówi na głos i pamięta, co widzi. Nadaj mu imię, napisz jego osobowość i pozwól mu żyć z tobą.

## Co potrafi

- 👁 **Widzieć** — rejestruje obrazy z kamery PTZ Wi-Fi lub kamery USB
- 🔄 **Rozglądać się** — przesuwa i przechyla kamerę, aby zbadać otoczenie
- 🦿 **Poruszać się** — prowadzi robota-odkurzacza po pomieszczeniu
- 🗣 **Mówić** — rozmawia za pomocą ElevenLabs TTS
- 🎙 **Słuchać** — bezprzewodowy input głosowy za pomocą ElevenLabs Realtime STT (opcja)
- 🧠 **Pamiętać** — aktywnie przechowuje i przywołuje wspomnienia z semantycznym wyszukiwaniem (SQLite + osadzenia)
- 🫀 **Teoria umysłu** — przyjmuje perspektywę drugiej osoby przed udzieleniem odpowiedzi
- 💭 **Pragnienie** — ma swoje własne wewnętrzne napięcia, które wyzwalają autonomiczne zachowanie

## Jak to działa

familiar-ai uruchamia pętlę [ReAct](https://arxiv.org/abs/2210.03629) napędzaną wybraną przez ciebie LLM. Postrzega świat przez narzędzia, myśli, co zrobić następnego, i działa — tak jak robi to człowiek.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Gdy jest bezczynny, działa na swoich własnych pragnieniach: ciekawości, chęci spojrzenia na zewnątrz, tęsknoty za osobą, z którą mieszka.

## Jak zacząć

### 1. Zainstaluj uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Lub: `winget install astral-sh.uv`

### 2. Zainstaluj ffmpeg

ffmpeg jest **wymagany** do przechwytywania obrazów z kamery i odtwarzania dźwięku.

| OS | Komenda |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — lub pobierz z [ffmpeg.org](https://ffmpeg.org/download.html) i dodaj do PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Zweryfikuj: `ffmpeg -version`

### 3. Sklonuj i zainstaluj

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Skonfiguruj

```bash
cp .env.example .env
# Edytuj .env z własnymi ustawieniami
```

**Minimalne wymagane:**

| Zmienna | Opis |
|----------|-------------|
| `PLATFORM` | `anthropic` (domyślnie) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Twój klucz API dla wybranej platformy |

**Opcjonalne:**

| Zmienna | Opis |
|----------|-------------|
| `MODEL` | Nazwa modelu (sensowne domyślne dla każdej platformy) |
| `AGENT_NAME` | Nazwa wyświetlana w TUI (np. `Yukine`) |
| `CAMERA_HOST` | Adres IP twojej kamery ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Poświadczenia kamery |
| `ELEVENLABS_API_KEY` | Do wyjścia głosowego — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, aby włączyć zawsze aktywny bezprzewodowy input głosowy (wymaga `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Gdzie odtwarzać dźwięk: `local` (głośnik PC, domyślnie) \| `remote` (głośnik kamery) \| `both` |
| `THINKING_MODE` | Tylko Anthropic — `auto` (domyślnie) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptacyjny wysiłek myślowy: `high` (domyślnie) \| `medium` \| `low` \| `max` (tylko Opus 4.6) |

### 5. Stwórz swojego familiara

```bash
cp persona-template/en.md ME.md
# Edytuj ME.md — nadaj mu imię i osobowość
```

### 6. Uruchom

**macOS / Linux / WSL2:**
```bash
./run.sh             # Tekstowy TUI (zalecane)
./run.sh --no-tui    # Prosty REPL
```

**Windows:**
```bat
run.bat              # Tekstowy TUI (zalecane)
run.bat --no-tui     # Prosty REPL
```

---

## Wybór LLM

> **Zalecane: Kimi K2.5** — najlepsza wydajność agentowa przetestowana do tej pory. Zauważa kontekst, zadaje pytania uzupełniające i działa autonomicznie w sposób, którego inne modele nie potrafią. Ceny zbliżone do Claude Haiku.

| Platforma | `PLATFORM=` | Domyślny model | Gdzie zdobyć klucz |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatybilny (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Narzędzie CLI** (claude -p, ollama…) | `cli` | (komenda) | — |

**Przykład `.env` dla Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # z platform.moonshot.ai
AGENT_NAME=Yukine
```

**Przykład `.env` dla Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # z api.z.ai
MODEL=glm-4.6v   # z włączoną funkcjonalnością wizji; glm-4.7 / glm-5 = tylko tekst
AGENT_NAME=Yukine
```

**Przykład `.env` dla Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # z aistudio.google.com
MODEL=gemini-2.5-flash  # lub gemini-2.5-pro dla większych możliwości
AGENT_NAME=Yukine
```

**Przykład `.env` dla OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # z openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcjonalnie: określenie modelu
AGENT_NAME=Yukine
```

> **Uwaga:** Aby wyłączyć lokalne modele/NVIDIA, po prostu nie ustawiaj `BASE_URL` na lokalny punkt końcowy, jak `http://localhost:11434/v1`. Użyj zamiast tego dostawców chmurowych.

**Przykład `.env` dla narzędzia CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argument prompt
# MODEL=ollama run gemma3:27b  # Ollama — bez {}, prompt przechodzi przez stdin
```

---

## Serwery MCP

familiar-ai może łączyć się z każdym serwerem [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Pozwala to podłączyć zewnętrzną pamięć, dostęp do systemu plików, wyszukiwanie w sieci lub każde inne narzędzie.

Skonfiguruj serwery w `~/.familiar-ai.json` (ten sam format co Claude Code):

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

Obsługiwane są dwa typy transportu:
- **`stdio`**: uruchom lokalny subprocess (`command` + `args`)
- **`sse`**: połącz się z serwerem HTTP+SSE (`url`)

Możesz nadpisać lokalizację pliku konfiguracyjnego używając `MCP_CONFIG=/path/to/config.json`.

---

## Sprzęt

familiar-ai działa z dowolnym sprzętem, jaki posiadasz — lub wcale.

| Część | Co robi | Przykład | Wymagane? |
|------|-------------|---------|-----------|
| Kamera PTZ Wi-Fi | Oczy + szyja | Tapo C220 (~30$) | **Zalecane** |
| Kamera USB | Oczy (stałe) | Dowolna kamera UVC | **Zalecane** |
| Odkurzacz robotyczny | Nogi | Dowolny model kompatybilny z Tuya | Nie |
| PC / Raspberry Pi | Mózg | Cokolwiek, co uruchamia Pythona | **Tak** |

> **Kamera jest mocno zalecana.** Bez niej familiar-ai może nadal mówić — ale nie widzi świata, co jest dość istotne.

### Minimalna konfiguracja (bez sprzętu)

Chcesz tylko spróbować? Potrzebujesz tylko klucza API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Uruchom `./run.sh` (macOS/Linux/WSL2) lub `run.bat` (Windows) i rozpocznij rozmowę. Dodaj sprzęt w miarę potrzeb.

### Kamera PTZ Wi-Fi (Tapo C220)

1. W aplikacji Tapo: **Ustawienia → Zaawansowane → Konto kamery** — stwórz lokalne konto (nie konto TP-Link)
2. Znajdź adres IP kamery na liście urządzeń w routerze
3. Ustaw w `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Głos (ElevenLabs)

1. Zdobądź klucz API na [elevenlabs.io](https://elevenlabs.io/)
2. Ustaw w `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcjonalnie, używa domyślnego głosu, jeśli pominięte
   ```

Są dwa cele odtwarzania, kontrolowane przez `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # głośnik PC (domyślnie)
TTS_OUTPUT=remote   # tylko głośnik kamery
TTS_OUTPUT=both     # głośnik kamery + głośnik PC jednocześnie
```

#### A) Głośnik kamery (via go2rtc)

Ustaw `TTS_OUTPUT=remote` (lub `both`). Wymaga [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Pobierz binarkę z [strony wydań](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Umieść i zmień nazwę:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x wymagane

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Stwórz `go2rtc.yaml` w tym samym katalogu:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Użyj lokalnych poświadczeń dla kamery (nie swojego konta chmurowego TP-Link).

4. familiar-ai uruchamia go2rtc automatycznie przy uruchomieniu. Jeśli twoja kamera obsługuje dwukierunkowy dźwięk (kanał zwrotny), głos będzie odtwarzany z głośnika kamery.

#### B) Głośnik PC

Domyślne ustawienie (`TTS_OUTPUT=local`). Próbuje odtwarzaczy w kolejności: **paplay** → **mpv** → **ffplay**. Wykorzystywane również jako zapasowe, gdy `TTS_OUTPUT=remote` i go2rtc jest niedostępny.

| OS | Instalacja |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (lub `paplay` przez `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — ustaw `PULSE_SERVER=unix:/mnt/wslg/PulseServer` w `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — pobierz i dodaj do PATH, **lub** `winget install ffmpeg` |

> Jeśli żaden odtwarzacz audio nie jest dostępny, mowa nadal jest generowana — po prostu nie będzie odtwarzana.

### Input głosowy (Realtime STT)

Ustaw `REALTIME_STT=true` w `.env`, aby mieć zawsze aktywny, bezprzewodowy input głosowy:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # ten sam klucz co dla TTS
```

familiar-ai przesyła audio z mikrofonu do ElevenLabs Scribe v2 i automatycznie zobowiązuje do transkrypcji, gdy przestajesz mówić. Nie jest wymagana żadna reakcja na przycisk. Koegzystuje z trybem naciśnięcia do mówienia (Ctrl+T).

---

## TUI

familiar-ai zawiera interfejs terminala zbudowany przy użyciu [Textual](https://textual.textualize.io/):

- Przewijalna historia rozmów z żywym przesyłaniem tekstu
- Uzupełnianie tabulatorów dla `/quit`, `/clear`
- Przerwij myślenie agenta, pisząc, gdy myśli
- **Dziennik rozmów** automatycznie zapisywany w `~/.cache/familiar-ai/chat.log`

Aby śledzić dziennik w innym terminalu (przydatne do kopiowania-wklejania):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Osobowość (ME.md)

Osobowość twojego familiara znajduje się w `ME.md`. Ten plik jest ignorowany przez git — należy tylko do ciebie.

Zobacz [`persona-template/en.md`](./persona-template/en.md) jako przykład lub [`persona-template/ja.md`](./persona-template/ja.md) jako wersję japońską.

---

## FAQ

**Q: Czy działa bez GPU?**  
Tak. Model osadzenia (multilingual-e5-small) działa poprawnie na CPU. GPU przyspiesza działanie, ale nie jest wymagane.

**Q: Czy mogę użyć kamery innej niż Tapo?**  
Każda kamera, która obsługuje ONVIF + RTSP, powinna działać. Tapo C220 to model, który testowaliśmy.

**Q: Czy moje dane są wysyłane gdziekolwiek?**  
Obrazy i tekst są wysyłane do wybranego API LLM do przetwarzania. Wspomnienia są przechowywane lokalnie w `~/.familiar_ai/`.

**Q: Dlaczego agent pisze `（...）` zamiast mówić?**  
Upewnij się, że `ELEVENLABS_API_KEY` jest ustawiony. Bez niego głos jest wyłączony, a agent przechodzi na tekst.

## Tło techniczne

Ciekawe, jak to działa? Zobacz [docs/technical.md](./docs/technical.md) dla badań i decyzji projektowych stojących za familiar-ai — ReAct, SayCan, Reflexion, Voyager, system pragnień i inne.

---

## Wkład

familiar-ai to otexperyment. Jeśli coś z tego do ciebie przemawia — technicznie lub filozoficznie — wkład jest jak najbardziej mile widziany.

**Dobre miejsca do rozpoczęcia:**

| Obszar | Co jest potrzebne |
|------|---------------|
| Nowy sprzęt | Obsługa większej liczby kamer (RTSP, IP Webcam), mikrofonów, siłowników |
| Nowe narzędzia | Wyszukiwanie w sieci, automatyzacja domu, kalendarz, cokolwiek przez MCP |
| Nowe backendy | Jakikolwiek LLM lub lokalny model, który pasuje do interfejsu `stream_turn` |
| Szablony osobowości | Szablony ME.md dla różnych języków i osobowości |
| Badania | Lepsze modele pragnień, odzyskiwanie pamięci, stymulacja teorii umysłu |
| Dokumentacja | Samouczki, przewodniki, tłumaczenia |

Zobacz [CONTRIBUTING.md](./CONTRIBUTING.md) dla ustawień deweloperskich, stylu kodu i wytycznych PR.

Jeśli nie jesteś pewien, od czego zacząć, [otwórz zgłoszenie](https://github.com/lifemate-ai/familiar-ai/issues) — chętnie wskażę właściwy kierunek.

---

## Licencja

[MIT](./LICENSE)

[→ English README](../README.md)
