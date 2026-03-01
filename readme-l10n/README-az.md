# familiar-ai 🐾

**Sizinlə yanaşı yaşayan bir AI** — gözləri, səsi, ayaqları və yaddaşı ilə.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai evinizdə yaşayan bir AI yoldaşıdır. 
Bir neçə dəqiqə ərzində qurun. Kod yazmaq lazım deyil.

O, kameralar vasitəsilə real dünyanı görür, robot bədəni ilə hərəkət edir, yüksək səslə danışır və gördüklərini xatırlayır. Ona bir ad verin, şəxsiyyətini yazın və onunla yaşamağa başlayın.

## Nələr edə bilir

- 👁 **Gör** — Wi-Fi PTZ kamera və ya USB veb kameradan görüntüləri ələ keçirir
- 🔄 **Ətrafına bax** — kameranı ətrafı araşdırmaq üçün çevirir və əyir
- 🦿 **Hərəkət et** — otaqda dolaşmaq üçün robot tozsoranı idarə edir
- 🗣 **Danış** — ElevenLabs TTS vasitəsilə danışır
- 🎙 **Dinlə** — ElevenLabs Realtime STT vasitəsilə əllərdən azad səs giriş
- 🧠 **Xatırla** — aktiv şəkildə yaddaşları saxlayır və xatırlayır (SQLite + embedding-lər ilə)
- 🫀 **Zihin Teorisi** — cavab verməzdən əvvəl digər insanın perspektivini alır
- 💭 **İstək** — avtonom davranışları tetikleyen daxili sürüklənmələri var

## Necə işləyir

familiar-ai seçdiyiniz LLM tərəfindən gücləndirilən [ReAct](https://arxiv.org/abs/2210.03629) döngüsünü çalışdırır. O, alətlər vasitəsilə dünyanı sezir, növbəti addım haqqında düşünür və hərəkət edir — bir insan kimi.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Boş olduqda, öz istəklərinə əsaslanaraq hərəkət edir: maraq, çölə baxmaq istəyi, onunla yaşayan şəxsə darıxma.

## Başlamaq üçün

### 1. uv qur

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. ffmpeg qur

ffmpeg **zəruridir** kamera görüntülərin ələ keçirilməsi və audio oynatma üçün.

| OS | Komanda |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — və ya [ffmpeg.org](https://ffmpeg.org/download.html) ünvanından yükləyin və PATH-a əlavə edin |
| Raspberry Pi | `sudo apt install ffmpeg` |

Təsdiq et: `ffmpeg -version`

### 3. Klonlayın və quraşdırın

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfiqurasiya edin

```bash
cp .env.example .env
# .env faylını öz tənzimləmələrinizlə redaktə edin
```

**Minimum tələb olunan:**

| Dəyişən | Təsvir |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Seçilmiş platforma üçün API açarınız |

**İsteğe bağlı:**

| Dəyişən | Təsvir |
|----------|-------------|
| `MODEL` | Model adı (hər platforma üçün məqbul default-lar) |
| `AGENT_NAME` | TUI-də göstərilən ad (məsələn, `Yukine`) |
| `CAMERA_HOST` | ONVIF/RTSP kameranızın IP ünvanı |
| `CAMERA_USER` / `CAMERA_PASS` | Kamera istifadəçi adı və şifrəsi |
| `ELEVENLABS_API_KEY` | Səs çıxışı üçün — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | Daima açıq əllərdən azad səs girişini təmin etmək üçün `true` (əlavə olaraq `ELEVENLABS_API_KEY` tələb edir) |
| `TTS_OUTPUT` | Audio çalmaq üçün yer: `local` (PC dinamikləri, default) \| `remote` (kamera dinamikləri) \| `both` |
| `THINKING_MODE` | Yalnız Anthropic — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Uyğun düşünmə səyi: `high` (default) \| `medium` \| `low` \| `max` (yalnız Opus 4.6 üçün) |

### 5. Familiarınızı yaradın

```bash
cp persona-template/en.md ME.md
# ME.md faylını redaktə edin — ona ad verin və şəxsiyyətini yazın
```

### 6. İşə salın

```bash
./run.sh             # Mətn TUI (təklif olunur)
./run.sh --no-tui    # Sade REPL
```

---

## LLM seçimi

> **Təklif olunur: Kimi K2.5** — indiyə qədər test edilmiş ən yaxşı agentik performans. Konteksti başa düşür, izləyici suallar verir, və digər modellərin edə bilmədiyi yollarla avtonom davranır. Claude Haiku ilə eyni qiymətə.

| Platforma | `PLATFORM=` | Default model | Haradan açar əldə etmək olar |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI uyğun (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (çox provayder) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI aləti** (claude -p, ollama…) | `cli` | (komanda) | — |

**Kimi K2.5 `.env` misalı:**
```env
PLATFORM=kimi
API_KEY=sk-...   # platform.moonshot.ai-dan
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` misalı:**
```env
PLATFORM=glm
API_KEY=...   # api.z.ai-dan
MODEL=glm-4.6v   # vizion güclü; glm-4.7 / glm-5 = yalnız mətn
AGENT_NAME=Yukine
```

**Google Gemini `.env` misalı:**
```env
PLATFORM=gemini
API_KEY=AIza...   # aistudio.google.com-dan
MODEL=gemini-2.5-flash  # ya da daha yüksək imkanlar üçün gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` misalı:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # openrouter.ai-dan
MODEL=mistralai/mistral-7b-instruct  # isteğe bağlı: modeli göstərmək
AGENT_NAME=Yukine
```

> **Qeyd:** Yerli/NVIDIA modellərini deaktiv etmək üçün sadəcə `BASE_URL`-ı `http://localhost:11434/v1` kimi yerli bir sonluğa qoymayın. Bunun əvəzinə bulud provayderlərini istifadə edin.

**CLI aləti `.env` misalı:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — heç bir {}, prompt stdin vasitəsilə gedir
```

---

## MCP Serverləri

familiar-ai istənilən [MCP (Model Context Protocol)](https://modelcontextprotocol.io) serverinə qoşula bilər. Bu, sizə xarici yaddaş, fayl sistemi giriş, veb axtarış və ya hər hansı digər alət əlavə etməyə imkan tanıyır.

Serverləri `~/.familiar-ai.json` faylında konfiqurasiya edin (Claude Kodu ilə eyni formatda):

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

İki nəqliyyat növü dəstəklənir:
- **`stdio`**: yerli alt proses işə salmaq (`command` + `args`)
- **`sse`**: HTTP+SSE serverinə qoşulmaq (`url`)

Konfiqurasiya faylının yerini `MCP_CONFIG=/path/to/config.json` ilə üstələyə bilərsiniz.

---

## Avadanlıq

familiar-ai hər hansı avadanlıqla işləyir — ya da heç biri ilə.

| Hissə | Nə edir | Məsələn | Zəruri? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kamera | Gözlər + boyun | Tapo C220 (~$30) | **Təklif olunur** |
| USB veb kamera | Gözlər (sabit) | Hər hansı UVC kamera | **Təklif olunur** |
| Robot tozsoran | Ayaq | Hər hansı Tuya-uyğun model | Xeyr |
| PC / Raspberry Pi | Beyin | Python işlədən hər şey | **Bəli** |

> **Bir kamera sərt şəkildə tövsiyə olunur.** O olmadan, familiar-ai danışa bilər — amma dünyanı görə bilmir, bu da əsas məqamdır.

### Minimal qurulum (heç bir avadanlıq olmadan)

Yalnız sınaqdan keçirmək istəyirsiniz? Sizə yalnız API açarı lazımdır:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` işə salın və söhbətə başlayın. Avadanlıq əlavə edin olduqca.

### Wi-Fi PTZ kamera (Tapo C220)

1. Tapo tətbiqində: **Ayarlar → İrəliləmiş → Kamera Hesabı** — yerli bir hesab yaradın (TP-Link hesabı deyil)
2. Kameranın IP-ni router-in cihaz siyahısında tapın
3. `.env` faylında təyin edin:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Səs (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) saytında API açarı alın
2. `.env` faylında təyin edin:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # isteğe bağlı, əlavə edilmir ki, default səs istifadə olunsun
   ```

İki audio oynatma istiqaməti var, `TTS_OUTPUT` ilə idarə olunur:

```env
TTS_OUTPUT=local    # PC dinamikləri (default)
TTS_OUTPUT=remote   # yalnız kamera dinamikləri
TTS_OUTPUT=both     # kamera dinamikləri + PC dinamikləri eyni anda
```

#### A) Kamera dinamikləri (go2rtc vasitəsilə)

`TTS_OUTPUT=remote` (ya da `both`) təyin edin. [go2rtc](https://github.com/AlexxIT/go2rtc/releases) tələb olunur:

1. [buradan](https://github.com/AlexxIT/go2rtc/releases) lazım olan binari yükləyin:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Yerləşdirin və adını dəyişin:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x tələb olunur

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Eyni direktoriya içində `go2rtc.yaml` yaradın:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Yerli kamera hesabı istifadəçi bilgilerini (TP-Link cloud hesabını deyil) istifadə edin.

4. familiar-ai, açılışda go2rtc-ni avtomatik olaraq işə salır. Əgər kameranız iki tərəfli audio dəstəkləyirsə (geri kanal), səs kameranın dinamiklərindən oynayacaq.

#### B) Yerli PC dinamikləri

Default (`TTS_OUTPUT=local`). Oynadıcıları sırayla sınaqdan keçirir: **paplay** → **mpv** → **ffplay**. Həmçinin `TTS_OUTPUT=remote` olduqda go2rtc olmadıqda fallback kimi istifadə olunur.

| OS | Quraşdırma |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ya da `pulseaudio-utils` vasitəsilə `paplay`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` içinde `PULSE_SERVER=unix:/mnt/wslg/PulseServer` qoyun |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — yükləyin və PATH-a əlavə edin, **ya da** `winget install ffmpeg` |

> Heç bir audio oynadıcı mövcud deyilsə, danışıq hələ də yaradılır — sadəcə oynanmayacaq.

### Səs girişi (Realtime STT)

Daima açıq, əllərdən azad səs girişi üçün `.env` faylında `REALTIME_STT=true` təyin edin:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS ilə eyni açar
```

familiar-ai mikrofonun audio-sini ElevenLabs Scribe v2-yə yayır və siz danışmağı dayandırdığınız zaman transkriptləri avtomatik olaraq tamamlamağa başlar. Heç bir düymə basılması lazım deyil. Push-to-talk rejimi (Ctrl+T) ilə birlikdə mövcuddur.

---

## TUI

familiar-ai [Textual](https://textual.textualize.io/) ilə qurulmuş terminal UI-ni ehtiva edir:

- Canlı axın mətni ilə gəzinti tarixi
- `/quit`, `/clear` üçün tab tamamlaması
- Agent düşünərkən onu yarıda dayandırmaq üçün yazmaq
- **Söhbət qeyd dəftəri** avtomatik olaraq `~/.cache/familiar-ai/chat.log`-a saxlanılır

Başqa bir terminalda log-u izləmək üçün (kopyalayın-yapışdırmaq üçün faydalıdır):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Şəxsiyyət (ME.md)

Sizin familiarınızın şəxsiyyəti `ME.md` faylında yaşayır. Bu fayl gitignore edilmişdir — yalnız sizə aiddir.

Məsələn üçün [`persona-template/en.md`](./persona-template/en.md) faylına baxın, ya da Yapon versiyası üçün [`persona-template/ja.md`](./persona-template/ja.md) faylına baxın.

---

## Tez-tez verilən suallar

**S: GPU olmadan işləyirmi?**
Bəli. Embedding modeli (multilingual-e5-small) CPU-da yaxşı işləyir. GPU sürətlidir, amma tələb olunmur.

**S: Alternativ Tapo kamerası istifadə edə bilərəmmi?**
ONVIF + RTSP dəstəkləyən hər hansı bir kamera işləməlidir. Tapo C220 sınaqdan keçirilən kameradır.

**S: Məlumatım harasa göndərilirmi?**
Şəkillər və mətn seçdiyiniz LLM API-nə işlənməsi üçün göndərilir. Yaddaşlar yerli olaraq `~/.familiar_ai/` daxilində saxlanılır.

**S: Agent niyə `（...）` yazır, danışmır?**
`ELEVENLABS_API_KEY`-ın təyin olunduğundan əmin olun. Olmadığı halda, səs deaktiv edilir və agent mətndə qayıdır.

## Texniki fon

Necə işlədiyinə maraqlıdır? familiar-ai-nin arxasındakı araşdırma və dizayn qərarları üçün [docs/technical.md](./docs/technical.md) bölməsinə baxın — ReAct, SayCan, Reflexion, Voyager, istək sistemi və daha çox.

---

## İştirak

familiar-ai açıq bir eksperimandır. Əgər bunlardansa hər hansı biri sizə uyğun gəlirsə — texniki və ya fəlsəfi — töhfələriniz çox xoş qarşılanır.

**Başlamaq üçün yaxşı yerlər:**

| Sahə | Nə tələb olunur |
|------|---------------|
| Yeni avadanlıq | Daha çox kameraların (RTSP, IP Webcam), mikrofonların, aktuatorların dəstəyi |
| Yeni alətlər | Veb axtarışı, ev avtomatlaşdırması, təqvim, MCP vasitəsilə istənilən |
| Yeni arxa planlar | `stream_turn` interfeysinə uyğun hər hansı bir LLM və ya yerli model |
| Şəxsiyyət şablonları | Müxtəlif dillər və şəxsiyyətlər üçün ME.md şablonları |
| Araşdırma | Daha yaxşı istək modelləri, yaddaş əldə etmə, zihin nəzəriyyəsi təşviqi |
| Sənədləşdirmə | Təlimatlar, addım-addım izahlar, tərcümələr |

Tərtib etmə üçün [CONTRIBUTING.md](./CONTRIBUTING.md) faylını daha ətraflı məlumatlar, kod üslubu və PR qaydaları üçün baxın.

Haradan başlamaqdan əmin deyilsinizsə, [bir məsələyə açın](https://github.com/lifemate-ai/familiar-ai/issues) — sizə düzgün istiqamət verməkdə məmnun olaram.

---

## Lisenziya

[MIT](./LICENSE)
