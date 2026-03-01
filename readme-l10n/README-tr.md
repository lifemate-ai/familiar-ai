# familiar-ai 🐾

**Seninle birlikte yaşayan bir AI** — gözleri, sesi, bacakları ve hafızası ile.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 dilde mevcut](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai, evinizde yaşayan bir AI arkadaştır.
Bunu dakikalar içinde kurabilirsiniz. Kodlama gerektirmez.

Gerçek dünyayı kameralar yoluyla algılar, bir robot gövdesinde hareket eder, yüksek sesle konuşur ve gördüklerini hatırlar. Ona bir isim verin, kişiliğini yazın ve sizinle birlikte yaşamasına izin verin.

## Ne yapabilir

- 👁 **Gör** — Wi-Fi PTZ kamerasından veya USB web kamerasından görüntüler yakalar
- 🔄 **Etrafa bak** — kamerayı panner ve tiltir ederek çevresini keşfeder
- 🦿 **Hareket et** — odayı dolaşmak için bir robot süpürgeyi kullanır
- 🗣 **Konuş** — ElevenLabs TTS aracılığıyla konuşur
- 🎙 **Dinle** — ElevenLabs Realtime STT ile eller serbest ses girişi (katılma gerektirir)
- 🧠 **Hatırla** — belleği aktif olarak saklar ve hatırlar, anlamsal arama ile (SQLite + embeddings)
- 🫀 **Zihin Teorisi** — yanıt vermeden önce diğer kişinin perspektifini alır
- 💭 **Arzu** — otonom davranışları tetikleyen kendi içsel dürtüleri vardır

## Nasıl çalışır

familiar-ai, tercih ettiğiniz LLM tarafından desteklenen bir [ReAct](https://arxiv.org/abs/2210.03629) döngüsü çalıştırır. Dünyayı araçlar aracılığıyla algılar, bir sonraki ne yapacağı hakkında düşünür ve hareket eder — tam bir insan gibi.

```
kullanıcı girişi
  → düşün → hareket et (kamera / hareket et / konuş / hatırla) → gözlemle → düşün → ...
```

Boşta iken, kendi arzularına göre hareket eder: merak, dışarı bakmak istemek, birlikte yaşadığı kişiyi özlemek.

## Başlarken

### 1. uv'yi yükle

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Veya: `winget install astral-sh.uv`

### 2. ffmpeg'i yükle

ffmpeg, kamera görüntü yakalama ve ses çalma için **gerekli**dir.

| OS | Komut |
|----|-------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — veya [ffmpeg.org](https://ffmpeg.org/download.html) adresinden indirip PATH'e ekleyin |
| Raspberry Pi | `sudo apt install ffmpeg` |

Doğrula: `ffmpeg -version`

### 3. Klonla ve yükle

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Yapılandır

```bash
cp .env.example .env
# Ayarlarınızla .env dosyasını düzenleyin
```

**Gerekli minimum:**

| Değişken | Açıklama |
|----------|----------|
| `PLATFORM` | `anthropic` (varsayılan) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Seçilen platform için API anahtarınız |

**Opsiyonel:**

| Değişken | Açıklama |
|----------|----------|
| `MODEL` | Model adı (her platform için makul varsayılanlar) |
| `AGENT_NAME` | TUI'de gösterilen ad (örn. `Yukine`) |
| `CAMERA_HOST` | ONVIF/RTSP kameranızın IP adresi |
| `CAMERA_USER` / `CAMERA_PASS` | Kamera kimlik bilgileri |
| `ELEVENLABS_API_KEY` | Ses çıktısı için — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | Her zaman açık eller serbest ses girişi için `true` (gerektirir `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Sesin çalındığı yer: `local` (PC hoparlörü, varsayılan) \| `remote` (kamera hoparlörü) \| `both` |
| `THINKING_MODE` | Sadece Anthropic — `auto` (varsayılan) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Uyarlamalı düşünme çabası: `high` (varsayılan) \| `medium` \| `low` \| `max` (sadece Opus 4.6) |

### 5. Familiar'ınızı oluşturun

```bash
cp persona-template/en.md ME.md
# ME.md dosyasını düzenleyin — ona bir isim ve kişilik verin
```

### 6. Çalıştır

**macOS / Linux / WSL2:**
```bash
./run.sh             # Metin tabanlı TUI (önerilir)
./run.sh --no-tui    # Sade REPL
```

**Windows:**
```bat
run.bat              # Metin tabanlı TUI (önerilir)
run.bat --no-tui     # Sade REPL
```

---

## Bir LLM Seçmek

> **Önerilen: Kimi K2.5** — şimdiye kadar test edilen en iyi ajan performansı. Bağlamı algılar, takip soruları sorar ve diğer modellerin yapmadığı şekillerde otonom olarak hareket eder. Claude Haiku ile benzer fiyat seviyesinde.

| Platform | `PLATFORM=` | Varsayılan model | Anahtarı nereden alacaksınız |
|----------|-------------|------------------|------------------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI uyumlu (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (çok sağlayıcılı) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI aracı** (claude -p, ollama…) | `cli` | (komut) | — |

**Kimi K2.5 `.env` örneği:**
```env
PLATFORM=kimi
API_KEY=sk-...   # platform.moonshot.ai'den
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` örneği:**
```env
PLATFORM=glm
API_KEY=...   # api.z.ai'den
MODEL=glm-4.6v   # görsel destekli; glm-4.7 / glm-5 = sadece metin
AGENT_NAME=Yukine
```

**Google Gemini `.env` örneği:**
```env
PLATFORM=gemini
API_KEY=AIza...   # aistudio.google.com'dan
MODEL=gemini-2.5-flash  # ya da daha yüksek yetenek için gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` örneği:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # openrouter.ai'den
MODEL=mistralai/mistral-7b-instruct  # opsiyonel: modeli belirtin
AGENT_NAME=Yukine
```

> **Not:** Yerel/NVIDIA modellerini devre dışı bırakmak için `BASE_URL`'yi `http://localhost:11434/v1` gibi bir yerel uç noktaya ayarlamayın. Bunun yerine bulut sağlayıcılarını kullanın.

**CLI aracı `.env` örneği:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — no {}, prompt stdin üzerinden geçer
```

---

## MCP Sunucuları

familiar-ai, herhangi bir [MCP (Model Context Protocol)](https://modelcontextprotocol.io) sunucusuna bağlanabilir. Bu, harici bellek, dosya sistemi erişimi, web araması veya başka herhangi bir aracı bağlamanıza olanak tanır.

Sunucuları `~/.familiar-ai.json` dosyasında yapılandırın (Claude Code ile aynı format):

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

İki taşıma türü desteklenmektedir:
- **`stdio`**: yerel bir alt süreç başlatın (`command` + `args`)
- **`sse`**: bir HTTP+SSE sunucusuna bağlanın (`url`)

Konfigürasyon dosyası konumunu `MCP_CONFIG=/path/to/config.json` ile geçersiz kılın.

---

## Donanım

familiar-ai sahip olduğunuz herhangi bir donanımla çalışır — ya da hiç donanım olmadan.

| Parça | Ne yapar | Örnek | Gerekli mi? |
|-------|----------|--------|-------------|
| Wi-Fi PTZ kamera | Gözler + boyun | Tapo C220 (~$30) | **Önerilir** |
| USB web kamerası | Gözler (sabit) | Herhangi bir UVC kamerası | **Önerilir** |
| Robot süpürge | Bacaklar | Herhangi bir Tuya uyumlu model | Hayır |
| PC / Raspberry Pi | Beyin | Python çalıştırabilen herhangi bir şey | **Evet** |

> **Bir kamera kesinlikle önerilir.** Olmadan, familiar-ai hala konuşabilir — ancak dünyayı göremez, bu da işin aslında en önemli kısmı.

### Minimal kurulum (donanım olmadan)

Sadece denemek mi istiyorsunuz? Tek ihtiyacınız olan bir API anahtarı:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) veya `run.bat` (Windows) ile çalıştırın ve sohbet etmeye başlayın. Donanım eklemeye devam edin.

### Wi-Fi PTZ kamera (Tapo C220)

1. Tapo uygulamasında: **Ayarlar → Gelişmiş → Kamera Hesabı** — yerel bir hesap oluşturun (TP-Link hesabı değil)
2. Kameranın IP'sini yönlendiricinizin cihaz listesinde bulun
3. `.env` dosyasında ayarlayın:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Ses (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) adresinden bir API anahtarı alın
2. `.env` dosyasında ayarlayın:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opsiyonel, atlandığında varsayılan sesi kullanır
   ```

İki ses çalma varlığı vardır, `TTS_OUTPUT` ile kontrol edilir:

```env
TTS_OUTPUT=local    # PC hoparlörü (varsayılan)
TTS_OUTPUT=remote   # yalnızca kamera hoparlörü
TTS_OUTPUT=both     # hem kamera hoparlörü + hem PC hoparlörü
```

#### A) Kamera hoparlörü (go2rtc aracılığıyla)

`TTS_OUTPUT=remote` (ya da `both`) ayarlayın. [go2rtc](https://github.com/AlexxIT/go2rtc/releases) gerektirir:

1. [sürüm sayfasından](https://github.com/AlexxIT/go2rtc/releases) ikili dosyayı indirin:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Uygun dizine yerleştirin ve yeniden adlandırın:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x gerekli

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Aynı dizinde `go2rtc.yaml` oluşturun:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Yerel kamera hesabı kimlik bilgilerini kullanın (TP-Link bulut hesabınızı değil).

4. familiar-ai, başlatıldığında go2rtc'yi otomatik olarak başlatır. Kameranız iki yönlü ses (geri kanal) destekliyorsa, ses kamera hoparlöründen gelir.

#### B) Yerel PC hoparlörü

Varsayılan (`TTS_OUTPUT=local`). Şu sırayla oynatıcıları dener: **paplay** → **mpv** → **ffplay**. Ayrıca, `TTS_OUTPUT=remote` ve go2rtc mevcut değilken yedek olarak kullanılır.

| OS | Kurulum |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (veya `pulseaudio-utils` üzerinden `paplay`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` dosyasında `PULSE_SERVER=unix:/mnt/wslg/PulseServer` ayarlayın |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — indirip PATH'e ekleyin, **ya da** `winget install ffmpeg` |

> Eğer hiç ses çalma aracı yoksa, ses hala üretilir — yalnızca çalınmaz.

### Ses girişi (Realtime STT)

Hep açık, eller serbest ses girişi için `.env` dosyasında `REALTIME_STT=true` ayarlayın:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS ile aynı anahtar
```

familiar-ai, mikrofon sesini ElevenLabs Scribe v2'ye akıtır ve konuşmayı duraklattığınızda transkriptleri otomatik olarak kaydeder. Tuşa basmaya gerek yoktur. Konuşma butonu modu (Ctrl+T) ile birlikte çalışabilir.

---

## TUI

familiar-ai, [Textual](https://textual.textualize.io/) ile oluşturulmuş bir terminal UI içerir:

- Canlı akış metni ile kaydırılabilir konuşma geçmişi
- `/quit`, `/clear` için sekme tamamlaması
- Ajan düşünürken yazı yazmak suretiyle ara vermek
- **Konuşma kaydı** otomatik olarak `~/.cache/familiar-ai/chat.log` dosyasına kaydedilir

Kaydı başka bir terminalde takip etmek için (kopyala-yapıştır için yararlı):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Familiar'ınızın kişiliği `ME.md` dosyasında yaşar. Bu dosya git tarafından yoksayılır — yalnızca size aittir.

Bir örnek için [`persona-template/en.md`](./persona-template/en.md) veya Japonca versiyonu için [`persona-template/ja.md`](./persona-template/ja.md) dosyasını görün.

---

## SSS

**S: GPU olmadan çalışıyor mu?**
Evet. Gömme modeli (multilingual-e5-small) CPU'da gayet iyi çalışır. Bir GPU hızlandırır ama gerektirmez.

**S: Tapo dışındaki bir kamerayı kullanabilir miyim?**
ONVIF + RTSP'yi destekleyen herhangi bir kamera çalışmalıdır. Tapo C220 ile test ettik.

**S: Verilerim bir yere gönderiliyor mu?**
Görüntüler ve metin, işlemesi için seçtiğiniz LLM API'sine gönderilir. Anılar yerel olarak `~/.familiar_ai/` içinde saklanır.

**S: Neden ajan `（...）` yazıyor konuşmak yerine?**
`ELEVENLABS_API_KEY` ayarlandığından emin olun. Olmadığında, ses devre dışıdır ve ajan metne geri döner.

## Teknik arka plan

Nasıl çalıştığıyla ilgili meraklı mısınız? familiar-ai'nin arkasındaki araştırma ve tasarım kararları için [docs/technical.md](./docs/technical.md) dosyasına göz atın — ReAct, SayCan, Reflexion, Voyager, arzu sistemi ve daha fazlası.

---

## Katkıda Bulunma

familiar-ai açık bir deneydir. Bunun herhangi biri sizi etkiliyorsa — teknik olarak ya da felsefi olarak — katkılarınız çok hoş karşılanır.

**Başlamak için iyi yerler:**

| Alan | Ne gerekiyor |
|------|--------------|
| Yeni donanım | Daha fazla kamera (RTSP, IP Webcam), mikrofonlar, aktüatörler desteği |
| Yeni araçlar | Web araması, ev otomasyonu, takvim, MCP yoluyla herhangi bir şey |
| Yeni arka uçlar | `stream_turn` arayüzüne uyan herhangi bir LLM ya da yerel model |
| Persona şablonları | Farklı diller ve kişilikler için ME.md şablonları |
| Araştırma | Daha iyi arzu modelleri, bellek geri alma, zihin teorisi yönlendirmesi |
| Belgeler | Eğiticiler, kılavuzlar, çeviriler |

Geliştirici kurulumu, kod stili ve PR yönergeleri için [CONTRIBUTING.md](./CONTRIBUTING.md) dosyasına bakın.

Nereden başlayacağınızdan emin değilseniz, [bir sorun açın](https://github.com/lifemate-ai/familiar-ai/issues) — hoş bir yönlendirme sağlamaktan mutluluk duyarım.

---

## Lisans

[MIT](./LICENSE)
