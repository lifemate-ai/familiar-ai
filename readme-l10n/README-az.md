```markdown
# familiar-ai 🐾

**Sizinlə birlikdə yaşayan bir AI** — gözləri, səsi, ayaqları və yaddaşı olan.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 dildə mövcuddur](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai sizin evinizdə yaşayan bir AI yoldaşıdır. Bunu dəqiqələr ərzində qurun. Kodlama tələb olunmur.

O, kameralar vasitəsilə real dünyanı qəbul edir, robot bədəni ilə hərəkət edir, açıqdan danışır və gördüklərini xatırlayır. Ona bir ad verin, onun şəxsiyyətini yazın və bununla birlikdə yaşamasına imkan verin.

## Nə edə bilər

- 👁 **Görmək** — Wi-Fi PTZ kamera və ya USB veb kamerasından görüntü alır
- 🔄 **Dünyaya baxmaq** — ətrafını araşdırmaq üçün kameranı çevirir və əyir
- 🦿 **Hərəkət etmək** — otaqda gəzmək üçün robot tozsoranı idarə edir
- 🗣 **Danışmaq** — ElevenLabs TTS vasitəsilə danışır
- 🎙 **Dinləmək** — ElevenLabs Realtime STT (opt-in) vasitəsilə əllə azad səs girişi
- 🧠 **Yaddaş** — aktiv şəkildə xatirələri saxlayır və çağırır, semantik axtarışla (SQLite + embeddinglər)
- 🫀 **Zehin Teorisi** — cavab vermədən əvvəl digər şəxsin perspektivini alır
- 💭 **İstək** — müstəqil davranışı tetikleyen daxili ehtirasları var

## Necə işləyir

familiar-ai sizin seçdiyiniz LLM ilə güclənmiş [ReAct](https://arxiv.org/abs/2210.03629) döngüsünü işləyir. O, dünyanı alətlər vasitəsilə qəbul edir, növbəti addım barədə düşünür və hərəkət edir — insan kimi.

```
user input
  → think → act (kamera / hərəkət et / danış / yadda saxla) → müşahidə et → düşün → ...
```

Boş qaldıqda, öz arzularını həyata keçirir: maraq, xaricə baxmaq istəyi, yaşadığı şəxsi adamı darıxmaq.

## Başlamaq

### 1. uv quraşdırın

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Yaxud: `winget install astral-sh.uv`

### 2. ffmpeg quraşdırın

ffmpeg kamera görüntülərini tutmaq və audio oynatmaq üçün **tələb olunur**.

| OS | Əmr |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — və ya [ffmpeg.org](https://ffmpeg.org/download.html) saytından yükləyin və PATH-a əlavə edin |
| Raspberry Pi | `sudo apt install ffmpeg` |

Təsdiqlə: `ffmpeg -version`

### 3. Klonlayın və quraşdırın

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfiqurasiya

```bash
cp .env.example .env
# .env faylını öz parametrlərinizlə redaktə edin
```

**Minimal tələb olunan:**

| Dəyişən | Təsvir |
|----------|-------------|
| `PLATFORM` | `anthropic` (defolt) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Seçilən platforma üçün API açarınız |

**İstəyə bağlı:**

| Dəyişən | Təsvir |
|----------|-------------|
| `MODEL` | Modell ad (platforma üzrə məqbul defoltlar) |
| `AGENT_NAME` | TUI-də göstərilən ad (məsələn, `Yukine`) |
| `CAMERA_HOST` | ONVIF/RTSP kameranızın IP ünvanı |
| `CAMERA_USER` / `CAMERA_PASS` | Kamera kredensialları |
| `ELEVENLABS_API_KEY` | Səs çıxışı üçün — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | Həmişə açıq əllə azad səs girişi üçün `true` (tələb edir `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Səsin harada oynadılması: `local` (PC dinamikləri, defolt) \| `remote` (kamera dinamikləri) \| `both` |
| `THINKING_MODE` | Yalnız Anthropic — `auto` (defolt) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptiv düşüncə səy: `high` (defolt) \| `medium` \| `low` \| `max` (yalnız Opus 4.6) |

### 5. Öz familiarınızı yaradın

```bash
cp persona-template/en.md ME.md
# ME.md faylını redaktə edin — ona bir ad və şəxsiyyət verin
```

### 6. İcra edin

**macOS / Linux / WSL2:**
```bash
./run.sh             # Mətn TUI (tövsiyə olunur)
./run.sh --no-tui    # Sadə REPL
```

**Windows:**
```bat
run.bat              # Mətn TUI (tövsiyə olunur)
run.bat --no-tui     # Sadə REPL
```

---

## LLM seçimi

> **Tövsiyə olunur: Kimi K2.5** — indiyə qədər test edilmiş ən yaxşı agentik performans. Konteksti qeyd edir, davamlı suallar soruşur və digər modellərin edə bilmədiyi şəkildə müstəqil hərəkət edir. Claude Haiku ilə oxşar qiymətdədir.

| Platforma | `PLATFORM=` | Defolt model | Açarın əldə ediləcəyi yer |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-uyğun (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (çox provayder) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI aləti** (claude -p, ollama…) | `cli` | (əməllər) | — |

**Kimi K2.5 `.env` nümunəsi:**
```env
PLATFORM=kimi
API_KEY=sk-...   # platform.moonshot.ai-dan
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` nümunəsi:**
```env
PLATFORM=glm
API_KEY=...   # api.z.ai-dan
MODEL=glm-4.6v   # görmə funksiyalı; glm-4.7 / glm-5 = yalnız mətn
AGENT_NAME=Yukine
```

**Google Gemini `.env` nümunəsi:**
```env
PLATFORM=gemini
API_KEY=AIza...   # aistudio.google.com-dan
MODEL=gemini-2.5-flash  # və ya daha yüksək qabiliyyət üçün gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` nümunəsi:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # openrouter.ai-dan
MODEL=mistralai/mistral-7b-instruct  # isteğe bağlı: modeli müəyyən edin
AGENT_NAME=Yukine
```

> **Qeyd:** Yerli/NVIDIA modelləri deaktiv etmək üçün sadəcə `BASE_URL`-ı `http://localhost:11434/v1` kimi yerli bir uçap etməyin. Bunun əvəzinə bulud provayderlərindən istifadə edin.

**CLI aləti `.env` nümunəsi:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — heç bir {}, prompt stdin ilə gedir
```

---

## MCP Serverləri

familiar-ai hər hansı bir [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serverinə qoşula bilər. Bu, sizə xarici yaddaş, fayl sisteminə giriş, veb axtarış və ya digər alətləri qoşmağa imkan verir.

Serverləri `~/.familiar-ai.json` faylında konfiqurasiya edin (Claude Kodu ilə eyni format):

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

İki daşıma növü dəstəklənir:
- **`stdio`**: yerli subprocess başlatmaq (`command` + `args`)
- **`sse`**: HTTP+SSE serverinə qoşulmaq (`url`)

Konfiqurasiya faylının yerini `MCP_CONFIG=/path/to/config.json` ilə üstələ bilərsiniz.

---

## Hardware

familiar-ai sizin malik olduğunuz hər hansı bir hardware ilə işləyir — ya da heç biri ilə.

| Hissə | Nə edir | Nümunə | Tələb olunur? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kamera | Gözlər + boyun | Tapo C220 (~$30) | **Tövsiyə olunur** |
| USB veb kamera | Gözlər (düzgün) | Hər hansı UVC kamera | **Tövsiyə olunur** |
| Robot tozsoran | Ayaqlar | Hər hansı Tuya-uyğun model | Xeyr |
| PC / Raspberry Pi | Beyin | Python işlətə bilən hər şey | **Bəli** |

> **Bir kamera mütləq tövsiyə olunur.** O olmadan, familiar-ai hələ də danışa bilir — amma dünyanı görə bilmir, bu da tam da məqsədin özüdür.

### Minimal quraşdırma (hardware olmadan)

Sadəcə sınaqdan keçirmək istəyirsiniz? Sizə yalnız bir API açarı lazımdır:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) və ya `run.bat` (Windows) da çalışdırın və söhbətə başlayın. Hardware əlavə edin.

### Wi-Fi PTZ kamera (Tapo C220)

1. Tapo tətbiqində: **Ayarlar → İrəliləmiş → Kamera Hesabı** — yerli bir hesab yaradın (TP-Link hesabı deyil)
2. Kameranın IP ünvanını router-in cihaz siyahısında tapın
3. `.env` faylında təyin edin:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=sizin-yerli-istifadəçi
   CAMERA_PASS=sizin-yerli-parol
   ```

### Səs (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) saytından API açarınızı alın
2. `.env` faylında təyin edin:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # isteğe bağlı, əks halda defolt səsi istifadə edir
   ```

İki playback təyinatı var, `TTS_OUTPUT` ilə idarə olunur:

```env
TTS_OUTPUT=local    # PC dinamikləri (defolt)
TTS_OUTPUT=remote   # yalnız kamera dinamikləri
TTS_OUTPUT=both     # kamera dinamikləri + PC dinamikləri eyni anda
```

#### A) Kamera dinamikləri (go2rtc vasitəsilə)

`TTS_OUTPUT=remote` (və ya `both`) olaraq təyin edin. [go2rtc](https://github.com/AlexxIT/go2rtc/releases) tələb olunur:

1. [buraxılış səhifəsindən](https://github.com/AlexxIT/go2rtc/releases) ikili faylı yükləyin:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Öz yerində yerləşdirin və adını dəyişdirin:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x tələb olunur

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Eyni qovluqda `go2rtc.yaml` yaradın:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://SIZIN_CAM_USER:SIZIN_CAM_PASS@SIZIN_CAM_IP/stream1
   ```
   Yerli kamera hesabınızın kredensiallarını istifadə edin (TP-Link bulud hesabınızın deyil).

4. familiar-ai təsadüfən go2rtc-i avtomatik başlayır. Əgər kameranız iki tərəfli audioyu dəstəkləyirsə (geri kanal), səs kamera dinamikindən gələcək.

#### B) Yerli PC dinamikləri

Defolt (`TTS_OUTPUT=local`). Oynatıcıları sırayla yoxlayır: **paplay** → **mpv** → **ffplay**. `TTS_OUTPUT=remote` vəziyyətində go2rtc mövcud olmadıqda da geriləyir.

| OS | Quraşdırma |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (və ya `paplay` vasitəsilə `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` faylında `PULSE_SERVER=unix:/mnt/wslg/PulseServer` olaraq təyin edin |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — yükləyin və PATH-a əlavə edin, **və ya** `winget install ffmpeg` |

> Əgər heç bir audio oynatıcı mövcud değilse, hələ də danışıq yaradılır — sadəcə oynaya bilməz.

### Səs girişi (Realtime STT)

Həmişə açıq, əllə azad səs girişi üçün `.env` faylında `REALTIME_STT=true` təyin edin:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS ilə eyni açar
```

familiar-ai mikrofon audioyu ElevenLabs Scribe v2-ə axıdaraq, danışmağı dayandırdığınızda avtomatik transkriptləri təqdim edir. Hər hansı bir düymə basmağı tələb etmir. Basmaqdan danışma rejimi (Ctrl+T) ilə birləşir.

---

## TUI

familiar-ai [Textual](https://textual.textualize.io/) ilə qurulmuş bir terminal UI-ni ehtiva edir:

- Canlı axınlı mətni olan çevirilməyə açıq danışıq tarixi
- `/quit`, `/clear` üçün tab-dolğunluğu
- Agent düşüncələrinin arasında bilərsinizdə by əməl etməyi pozun
- **Danışıq qeydi** avtomatik olaraq `~/.cache/familiar-ai/chat.log` -da saxlanılır

Qeydi başqa bir terminalda izləmək (kopyala-yapışdırmak üçün faydalıdır):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Sizin familiarınızın şəxsiyyəti `ME.md`-də yaşayır. Bu fayl gitignore-dur — yalnız sizə aiddir.

[`persona-template/en.md`](./persona-template/en.md) faylında bir nümunəyə baxın, yaxud [`persona-template/ja.md`](./persona-template/ja.md) faylında Yapon versiyasına baxın.

---

## Tez-tez verilən suallar

**S: GPU olmadan işləyirmi?**
Bəli. Embedding modeli (multilingual-e5-small) CPU-da yaxşı işləyir. GPU onu daha sürətli edir, amma tələb olunmur.

**S: Tapo-dan fərqli bir kamera istifadə edə bilərəmmi?**
ONVIF + RTSP-i dəstəkləyən hər hansı bir kamera işləməlidir. Tapo C220 bizim test etdiyimiz kameradır.

**S: Məlumatım harasa göndərilirmi?**
Şəkillər və mətndlər seçilmiş LLM API-nizə işlənmək üçün göndərilir. Xatirələr yerli olaraq `~/.familiar_ai/`-də saxlanılır.

**S: Agent niyə `（...）` yazır, danışmır?**
`ELEVENLABS_API_KEY`-in təyin edildiyinə əmin olun. Olmadığı halda, səs deaktivdir və agent mətni ilə geri dönür.

## Texniki arxa plan

Necə çalışdığını bilmək istəyirsiniz? familiar-ai-nin arxasında olan tədqiqat və dizayn qərarları üçün [docs/technical.md](./docs/technical.md) səhifəsinə baxın — ReAct, SayCan, Reflexion, Voyager, istək sistemi və daha çox.

---

## Töhfə vermək

familiar-ai açıq bir eksperimentdir. Əgər bunlardan hər hansı biri sizin üçün əhəmiyyətli deyilsə — texniki və ya fəlsəfi — töhfələriniz dəyərlidir.

**Başlamaq üçün yaxşı yerlər:**

| Sahə | Nə tələb olunur |
|------|---------------|
| Yeni hardware | Daha çox kameralar üçün dəstək (RTSP, IP Webcam), mikrofonlar, aktuatorlar |
| Yeni alətlər | Veb axtarış, ev avtomatlaşdırması, təqvim, MCP vasitəsilə istənilən şey |
| Yeni backendlər | `stream_turn` interfeysini uyğun gələn hər hansı LLM və ya yerli model |
| Persona şablonları | Fərqli dillər və şəxsiyyətlər üçün ME.md şablonları |
| Tədqiqat | Daha yaxşı istək modelləri, yaddaş girişi, zehin teorisi təşviqi |
| Dokumentasiya | Təlimatlar, dərsliklər, tərcümələr |

Tdevelop set up, kod stil və PR qaydaları üçün [CONTRIBUTING.md](./CONTRIBUTING.md) səhifəsinə baxın.

Hardasa başlamağın necə olduğunu bilmirsinizsə, [bir məsələ açın](https://github.com/lifemate-ai/familiar-ai/issues) — sizi düzgün istiqamətə yönləndirməkdən məmnun qalacam.

---

## Lisenziya

[MIT](./LICENSE)
```
