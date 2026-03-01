# familiar-ai 🐾

**Sztuczna inteligencja, która żyje obok ciebie** — ma oczy, głos, nogi i pamięć.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai to towarzysz AI, który mieszka w twoim domu. Skonfiguruj go w kilka minut. Nie wymaga programowania.

Postrzega prawdziwy świat przez kamery, porusza się na robotycznym ciele, mówi na głos i pamięta, co widzi. Nadaj mu imię, opisz jego osobowość i pozwól mu mieszkać z tobą.

## Co potrafi

- 👁 **Widzieć** — rejestruje obrazy z kamery Wi-Fi PTZ lub kamery USB
- 🔄 **Rozglądać się** — obraca i przechyla kamerę, aby zbadać otoczenie
- 🦿 **Poruszać się** — prowadzi robota odkurzacza po pokoju
- 🗣 **Mówić** — rozmawia za pomocą ElevenLabs TTS
- 🎙 **Słuchać** — bezprzewodowe wejście głosowe za pomocą ElevenLabs Realtime STT (opcjonalne)
- 🧠 **Pamiętać** — aktywnie przechowuje i przypomina sobie wspomnienia z semantycznym wyszukiwaniem (SQLite + embeddingi)
- 🫀 **Teoria umysłu** — przyjmuje perspektywę drugiej osoby przed odpowiedzią
- 💭 **Pragnienie** — ma swoje wewnętrzne potrzeby, które wyzwalają autonomiczne zachowanie

## Jak to działa

familiar-ai uruchamia pętlę [ReAct](https://arxiv.org/abs/2210.03629) zasilaną przez wybrany model LLM. Postrzega świat przez narzędzia, myśli o tym, co zrobić następnie, i działa — tak jak zrobiłby to człowiek.

```
user input
  → think → act (kamera / ruch / mówienie / pamiętanie) → obserwuj → myśl → ...
```

Gdy jest bezczynny, działa zgodnie z własnymi pragnieniami: ciekawością, chęcią spojrzenia na zewnątrz, tęsknotą za osobą, z którą mieszka.

## Jak zacząć

### 1. Zainstaluj uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Zainstaluj ffmpeg

ffmpeg jest **wymagany** do rejestracji obrazu z kamery i odtwarzania dźwięku.

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
# Edytuj .env swoimi ustawieniami
```

**Minimalne wymagania:**

| Zmienna | Opis |
|---------|------|
| `PLATFORM` | `anthropic` (domyślnie) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Twój klucz API dla wybranej platformy |

**Opcjonalnie:**

| Zmienna | Opis |
|---------|------|
| `MODEL` | Nazwa modelu (rozsądne domyślne dla każdej platformy) |
| `AGENT_NAME` | Wyświetlana nazwa w TUI (np. `Yukine`) |
| `CAMERA_HOST` | Adres IP twojej kamery ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Poświadczenia kamery |
| `ELEVENLABS_API_KEY` | Do wyjścia głosowego — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, aby włączyć zawsze aktywne wejście głosowe (wymaga `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Gdzie odtwarzać dźwięk: `local` (głośnik komputera, domyślnie) \| `remote` (głośnik kamery) \| `both` |
| `THINKING_MODE` | Tylko Anthropic — `auto` (domyślnie) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptacyjny wysiłek myślenia: `high` (domyślnie) \| `medium` \| `low` \| `max` (tylko Opus 4.6) |

### 5. Stwórz swojego towarzysza

```bash
cp persona-template/en.md ME.md
# Edytuj ME.md — nadaj mu imię i osobowość
```

### 6. Uruchom

```bash
./run.sh             # Tekstowe TUI (zalecane)
./run.sh --no-tui    # Prosty REPL
```

---

## Wybór LLM

> **Zalecane: Kimi K2.5** — najlepsza wydajność agentów testowanych do tej pory. Zauważa kontekst, zadaje pytania dodatkowe i działa autonomicznie w sposób, w jaki inne modele tego nie robią. Cenowo porównywalne z Claude Haiku.

| Platforma | `PLATFORM=` | Domyślny model | Gdzie uzyskać klucz |
|-----------|-------------|----------------|---------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Kompatybilne z OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
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
MODEL=glm-4.6v   # z włączoną wizją; glm-4.7 / glm-5 = tylko tekst
AGENT_NAME=Yukine
```

**Przykład `.env` dla Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # z aistudio.google.com
MODEL=gemini-2.5-flash  # lub gemini-2.5-pro dla wyższej wydajności
AGENT_NAME=Yukine
```

**Przykład `.env` dla OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # z openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcjonalnie: określ model
AGENT_NAME=Yukine
```

> **Uwaga:** Aby wyłączyć lokalne modele/NVIDIA, po prostu nie ustawiaj `BASE_URL` na lokalny punkt końcowy, jak `http://localhost:11434/v1`. Użyj dostawców chmurowych zamiast tego.

**Przykład `.env` dla narzędzia CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argument prompt
# MODEL=ollama run gemma3:27b  # Ollama — bez {}, prompt przechodzi przez stdin
```

---

## Serwery MCP

familiar-ai może łączyć się z każdym serwerem [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Umożliwia to podłączenie zewnętrznej pamięci, dostępu do systemu plików, wyszukiwania w sieci lub jakiegokolwiek innego narzędzia.

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
- **`stdio`**: uruchom lokalny podproces (`command` + `args`)
- **`sse`**: połącz się z serwerem HTTP+SSE (`url`)

Zmień lokalizację pliku konfiguracyjnego za pomocą `MCP_CONFIG=/path/to/config.json`.

---

## Sprzęt

familiar-ai działa z dowolnym sprzętem, który masz — lub wcale nie.

| Część | Co robi | Przykład | Wymagane? |
|-------|---------|----------|-----------|
| Kamera Wi-Fi PTZ | Oczy + szyja | Tapo C220 (~$30) | **Zalecane** |
| Kamera USB | Oczy (stałe) | Dowolna kamera UVC | **Zalecane** |
| Robot odkurzacz | Nogi | Dowolny model komplementarny Tuya | Nie |
| PC / Raspberry Pi | Mózg | Cokolwiek, co uruchamia Pythona | **Tak** |

> **Kamera jest zdecydowanie zalecana.** Bez niej familiar-ai wciąż może mówić — ale nie widzi świata, co jest całkiem istotnym punktem.

### Minimalna konfiguracja (bez sprzętu)

Chcesz tylko spróbować? Potrzebujesz tylko klucza API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Uruchom `./run.sh` i zacznij rozmawiać. Dodaj sprzęt, gdy będziesz gotowy.

### Kamera Wi-Fi PTZ (Tapo C220)

1. W aplikacji Tapo: **Ustawienia → Zaawansowane → Konto kamery** — utwórz lokalne konto (nie TP-Link)
2. Znajdź adres IP kamery na liście urządzeń twojego routera
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

Istnieją dwa miejsca docelowe odtwarzania, sterowane przez `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Głośnik komputera (domyślnie)
TTS_OUTPUT=remote   # tylko głośnik kamery
TTS_OUTPUT=both     # głośnik kamery + głośnik komputera jednocześnie
```

#### A) Głośnik kamery (przez go2rtc)

Ustaw `TTS_OUTPUT=remote` (lub `both`). Wymaga [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Pobierz plik binarny z [strony wydań](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Umieść i zmień nazwę:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # wymagana zmiana uprawnień chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Stwórz `go2rtc.yaml` w tym samym katalogu:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Użyj poświadczeń lokalnego konta kamery (nie swojego konta w chmurze TP-Link).

4. familiar-ai automatycznie uruchomi go2rtc podczas startu. Jeśli twoja kamera obsługuje dwukierunkowy dźwięk (kanał zwrotny), głos będzie odtwarzany z głośnika kamery.

#### B) Głośnik lokalny PC

Domyślne ustawienie (`TTS_OUTPUT=local`). Próbuj odtwarzaczy w kolejności: **paplay** → **mpv** → **ffplay**. Używane również jako fallback, gdy `TTS_OUTPUT=remote` i go2rtc jest niedostępny.

| OS | Instalacja |
|----|------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (lub `paplay` za pomocą `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — ustaw `PULSE_SERVER=unix:/mnt/wslg/PulseServer` w `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — pobierz i dodaj do PATH, **lub** `winget install ffmpeg` |

> Jeśli żaden odtwarzacz audio nie jest dostępny, mowa i tak zostanie wygenerowana — po prostu nie będzie odtwarzana.

### Wejście głosowe (Realtime STT)

Ustaw `REALTIME_STT=true` w `.env`, aby włączyć zawsze aktywne, bezprzewodowe wejście głosowe:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # ten sam klucz co TTS
```

familiar-ai przesyła dźwięk z mikrofonu do ElevenLabs Scribe v2 i automatycznie zapisuje transkrypcje, gdy przestajesz mówić. Nie wymaga naciśnięcia przycisku. Koegzystuje z trybem push-to-talk (Ctrl+T).

---

## TUI

familiar-ai zawiera interfejs terminalowy zbudowany z [Textual](https://textual.textualize.io/):

- Przewijalna historia rozmowy z tekstem na żywo
- Autouzupełnianie dla `/quit`, `/clear`
- Przerywanie agenta w trakcie myślenia, pisząc, gdy myśli
- **Dziennik rozmów** automatycznie zapisywany w `~/.cache/familiar-ai/chat.log`

Aby śledzić dziennik w innym terminalu (przydatne do kopiowania-wklejania):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Osobowość twojego towarzysza znajduje się w `ME.md`. Ten plik jest ignorowany przez git — jest tylko twój.

Zobacz [`persona-template/en.md`](./persona-template/en.md) jako przykład lub [`persona-template/ja.md`](./persona-template/ja.md) dla japońskiej wersji.

---

## FAQ

**Q: Czy działa bez GPU?**
Tak. Model embeddingowy (multilingual-e5-small) działa dobrze na CPU. GPU przyspiesza, ale nie jest wymagane.

**Q: Czy mogę użyć innej kamery niż Tapo?**
Dowolna kamera, która obsługuje ONVIF + RTSP, powinna działać. Tapo C220 to ta, którą testowaliśmy.

**Q: Czy moje dane są wysyłane gdziekolwiek?**
Obrazy i tekst są wysyłane do wybranego API LLM w celu przetwarzania. Wspomnienia są przechowywane lokalnie w `~/.familiar_ai/`.

**Q: Dlaczego agent pisze `（...）` zamiast mówić?**
Upewnij się, że `ELEVENLABS_API_KEY` jest ustawiony. Bez niego głos jest wyłączony i agent wraca do tekstu.

## Tło techniczne

Ciekawy, jak to działa? Zobacz [docs/technical.md](./docs/technical.md) dla badań i decyzji projektowych dotyczących familiar-ai — ReAct, SayCan, Reflexion, Voyager, system pragnień i inne.

---

## Wkład

familiar-ai to otwarty eksperyment. Jeśli któreś z tego rezonuje z tobą — technicznie lub filozoficznie — wkłady są bardzo mile widziane.

**Dobre miejsca na początek:**

| Obszar | Co jest potrzebne |
|--------|------------------|
| Nowy sprzęt | Wsparcie dla większej ilości kamer (RTSP, IP Webcam), mikrofonów, aktuatorów |
| Nowe narzędzia | Wyszukiwanie w sieci, automatyzacja domowa, kalendarz, cokolwiek przez MCP |
| Nowe backendy | Dowolny LLM lub lokalny model, który pasuje do interfejsu `stream_turn` |
| Szablony osobowości | Szablony ME.md dla różnych języków i osobowości |
| Badania | Lepsze modele pragnień, odzyskiwanie pamięci, promptowanie teorii umysłu |
| Dokumentacja | Samouczki, przewodniki, tłumaczenia |

Zobacz [CONTRIBUTING.md](./CONTRIBUTING.md) dla zestawu dewelopera, stylu kodu i wytycznych PR.

Jeśli nie wiesz, od czego zacząć, [otwórz zgłoszenie](https://github.com/lifemate-ai/familiar-ai/issues) — chętnie wskażę ci właściwy kierunek.

---

## Licencja

[MIT](./LICENSE)
