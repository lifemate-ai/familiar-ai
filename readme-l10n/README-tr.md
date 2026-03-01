# familiar-ai 🐾

**Sizinle birlikte yaşayan bir AI** — gözleri, sesi, bacakları ve hafızası ile.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai, evinizde yaşayan bir AI arkadaş. Dakikalar içinde kurulum yapın. Kodlama gerektirmiyor.

Gerçek dünyayı kameralar aracılığıyla algılar, robotik bir vücutta hareket eder, yüksek sesle konuşur ve gördüklerini hatırlamaktadır. Ona bir isim verin, kişiliğini yazın ve sizinle birlikte yaşamasına izin verin.

## Ne yapabilir

- 👁 **Görmek** — Wi-Fi PTZ kamera veya USB webcam'den görüntü yakalar
- 🔄 **Etrafa bakmak** — kamerayı pansiyoner ve eğimle etrafını keşfeder
- 🦿 **Hareket etmek** — odada dolaşmak için bir robot süpürgeyi kullanır
- 🗣 **Konuşmak** — ElevenLabs TTS aracılığıyla konuşur
- 🎙 **Dinlemek** — ElevenLabs Realtime STT ile eller serbest ses girişi (isteğe bağlı)
- 🧠 **Hatırlamak** — aktif olarak anıları saklar ve anlamlı arama ile geri çağırır (SQLite + embeddings)
- 🫀 **Zihin Teorisi** — yanıt vermeden önce diğer kişinin bakış açısını alır
- 💭 **İstek** — öz disiplinine sahip içsel sürücüleri vardır, bu da otonom davranışları tetikler

## Nasıl çalışır

familiar-ai, seçtiğiniz LLM tarafından desteklenen bir [ReAct](https://arxiv.org/abs/2210.03629) döngüsü çalıştırır. Dünyayı araçlar aracılığıyla algılar, ne yapacağına karar verir ve davranır — tıpkı bir insan gibi.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Boşta olduğunda, kendi isteklerine göre hareket eder: merak, dışarı bakmak istemek, yaşadığı kişiyi özlemek.

## Başlarken

### 1. uv'yi yükleyin

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. ffmpeg'i yükleyin

ffmpeg, kamera görüntüsü yakalama ve ses çalma için **gerekli**dir.

| OS | Komut |
|----|-------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — veya [ffmpeg.org](https://ffmpeg.org/download.html) adresinden indirin ve PATH'e ekleyin |
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
# Ayarlarınızı .env dosyasında düzenleyin
```

**Minimum gereklilik:**

| Değişken | Açıklama |
|----------|----------|
| `PLATFORM` | `anthropic` (varsayılan) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Seçilen platform için API anahtarınız |

**İsteğe bağlı:**

| Değişken | Açıklama |
|----------|----------|
| `MODEL` | Model adı (her platform için mantıklı varsayılanlar) |
| `AGENT_NAME` | TUI'de gösterilen görüntü adı (örn. `Yukine`) |
| `CAMERA_HOST` | ONVIF/RTSP kameranızın IP adresi |
| `CAMERA_USER` / `CAMERA_PASS` | Kamera kimlik bilgileri |
| `ELEVENLABS_API_KEY` | Ses çıkışı için — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | Her zaman açık eller serbest ses girişi için `true` (gerektirir `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Ses çalınacak yer: `local` (PC hoparlörü, varsayılan) \| `remote` (kamera hoparlörü) \| `both` |
| `THINKING_MODE` | Sadece Anthropic için — `auto` (varsayılan) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptif düşünme çabası: `high` (varsayılan) \| `medium` \| `low` \| `max` (sadece Opus 4.6) |

### 5. Familiar'ınızı oluşturun

```bash
cp persona-template/en.md ME.md
# ME.md dosyasını düzenleyin — ona bir isim verin ve kişilik kazandırın
```

### 6. Çalıştır

```bash
./run.sh             # Metin tabanlı TUI (önerilir)
./run.sh --no-tui    # Sade REPL
```

---

## LLM Seçimi

> **Tavsiye edilen: Kimi K2.5** — şimdiye kadar test edilen en iyi ajans performansı. Bağlamı fark eder, takip soruları sorar ve diğer modellerin yapmadığı şekillerde otonom olarak hareket eder. Claude Haiku ile benzer fiyatlandırmaya sahiptir.

| Platform | `PLATFORM=` | Varsayılan model | Anahtarı nereden alacağım |
|----------|------------|------------------|---------------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI uyumlu (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (çok sağlayıcı) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI aracı** (claude -p, ollama…) | `cli` | (komut) | — |

**Kimi K2.5 `.env` örneği:**
```env
PLATFORM=kimi
API_KEY=sk-...   # platform.moonshot.ai'dan
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` örneği:**
```env
PLATFORM=glm
API_KEY=...   # api.z.ai'dan
MODEL=glm-4.6v   # görüş yeteneğine sahip; glm-4.7 / glm-5 = yalnızca metin
AGENT_NAME=Yukine
```

**Google Gemini `.env` örneği:**
```env
PLATFORM=gemini
API_KEY=AIza...   # aistudio.google.com'dan
MODEL=gemini-2.5-flash  # veya daha yüksek yetenek için gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` örneği:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # openrouter.ai'dan
MODEL=mistralai/mistral-7b-instruct  # isteğe bağlı: modeli belirtin
AGENT_NAME=Yukine
```

> **Not:** Yerel/NVIDIA modellerini devre dışı bırakmak için, `BASE_URL`'yi `http://localhost:11434/v1` gibi bir yerel uç noktaya ayarlamayın. Bunun yerine bulut sağlayıcılarını kullanın.

**CLI aracı `.env` örneği:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — {}, prompt stdin ile gider
```

---

## MCP Sunucuları

familiar-ai, herhangi bir [MCP (Model Context Protocol)](https://modelcontextprotocol.io) sunucusuna bağlanabilir. Bu, harici hafıza, dosya sistemi erişimi, web araması veya herhangi bir başka aracı takmanıza olanak tanır.

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

İki taşıma türü desteklenir:
- **`stdio`**: yerel bir alt işlem başlatın (`command` + `args`)
- **`sse`**: HTTP+SSE sunucusuna bağlanın (`url`)

Yapılandırma dosyası konumunu `MCP_CONFIG=/path/to/config.json` ile geçersiz kılabilirsiniz.

---

## Donanım

familiar-ai, sahip olduğunuz herhangi bir donanımla çalışır — veya hiç donanım olmadan.

| Parça | Ne yapar | Örnek | Gerekli mi? |
|------|----------|--------|-------------|
| Wi-Fi PTZ kamera | Gözler + boyun | Tapo C220 (~$30) | **Önerilir** |
| USB webcam | Gözler (sabit) | Herhangi bir UVC kamera | **Önerilir** |
| Robot süpürge | Bacaklar | Herhangi bir Tuya uyumlu model | Hayır |
| PC / Raspberry Pi | Beyin | Python çalıştırabilen herhangi bir şey | **Evet** |

> **Bir kamera şiddetle önerilir.** Olmadan, familiar-ai hala konuşabilir — ama dünyayı göremez, ki bu aslında tüm amacın ta kendisidir.

### Minimal kurulum (donanım olmadan)

Sadece denemek mi istiyorsunuz? Tek ihtiyacınız olan bir API anahtarı:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` komutunu çalıştırın ve sohbet etmeye başlayın. Donanım ekleyin.

### Wi-Fi PTZ kamera (Tapo C220)

1. Tapo uygulamasında: **Ayarlar → Gelişmiş → Kamera Hesabı** — yerel bir hesap oluşturun (TP-Link hesabı değil)
2. Kameranın IP adresini yönlendiricinizin cihaz listesinde bulun
3. `.env` dosyasına ayarlayın:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Ses (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) adresinden bir API anahtarı alın
2. `.env` dosyasına ayarlayın:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # isteğe bağlı, atlandığında varsayılan sesi kullanır
   ```

İki ses çalma yeri, `TTS_OUTPUT` ile kontrol edilir:

```env
TTS_OUTPUT=local    # PC hoparlörü (varsayılan)
TTS_OUTPUT=remote   # yalnızca kamera hoparlörü
TTS_OUTPUT=both     # kamera hoparlörü + PC hoparlörü eşzamanlı
```

#### A) Kamera hoparlörü (go2rtc aracılığıyla)

`TTS_OUTPUT=remote` (veya `both`) olarak ayarlayın. [go2rtc](https://github.com/AlexxIT/go2rtc/releases) gerektirir:

1. [sürüm sayfasından](https://github.com/AlexxIT/go2rtc/releases) ikili dosyayı indirin:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Yerin ve adını değiştirin:
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
   Yerel kamera hesap kimlik bilgilerini kullanın (TP-Link bulut hesabınızı değil).

4. familiar-ai açılışta go2rtc'yi otomatik olarak başlatır. Kameranız iki yönlü ses desteğine sahip ise (geri bağlantı), ses kamera hoparlöründen çalınır.

#### B) Yerel PC hoparlörü

Varsayılan (`TTS_OUTPUT=local`). Sıralı olarak çalmaya çalışır: **paplay** → **mpv** → **ffplay**. Ayrıca `TTS_OUTPUT=remote` ayarlandığında go2rtc mevcut değilse yedek olarak kullanılır.

| OS | Kurulum |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (veya `pulseaudio-utils` aracılığıyla `paplay`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` dosyasında `PULSE_SERVER=unix:/mnt/wslg/PulseServer` ayarlayın |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — indirip PATH'e ekleyin, **veya** `winget install ffmpeg` |

> Eğer ses çalar yoksa, konuşma hala üretilir — ancak çalınmaz.

### Ses girişi (Realtime STT)

Her zaman açık, eller serbest ses girişi için `.env` dosyasında `REALTIME_STT=true` ayarlayın:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS ile aynı anahtar
```

familiar-ai mikrofon sesini ElevenLabs Scribe v2'ye akıtır ve konuşmayı durdurduğunuzda otomatik olarak transkriptleri kaydeder. Buton basma gerektirmez. PTT moduyla (Ctrl+T) bir arada çalışır.

---

## TUI

familiar-ai, [Textual](https://textual.textualize.io/) ile oluşturulmuş bir terminal UI içerir:

- Canlı akış metniyle kaydırılabilir konuşma geçmişi
- `/quit`, `/clear` için sekme tamamlama
- Düşünürken ajanın ortasında yazı yazarak kesme
- **Konuşma kaydı** otomatik olarak `~/.cache/familiar-ai/chat.log` dosyasına kaydedilir

Başka bir terminalde günlüğü takip etmek için (kopyala-yapıştır için faydalı):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Familiar'ınızın kişiliği `ME.md` dosyasındadır. Bu dosya git ile göz ardı edilir — yalnızca size aittir.

[`persona-template/en.md`](./persona-template/en.md) dosyasına bir örnek için ya da [`persona-template/ja.md`](./persona-template/ja.md) dosyasına Japonca versiyonu için göz atın.

---

## SSS

**S: GPU olmadan çalışıyor mu?**
Evet. Gömülü model (multilingual-e5-small) CPU'da iyi çalışır. Bir GPU onu hızlandırır ama gerekmiyor.

**S: Tapo dışında bir kamera kullanabilir miyim?**
ONVIF + RTSP destekleyen herhangi bir kamera çalışmalıdır. Tapo C220 ile test ettik.

**S: Verilerim herhangi bir yere gönderiliyor mu?**
Görüntüler ve metin, işlenmek üzere seçtiğiniz LLM API'sine gönderilir. Anılar yerel olarak `~/.familiar_ai/` dosyasında saklanır.

**S: Ajan neden `（...）` yazıyor, konuşmuyor?**
`ELEVENLABS_API_KEY` ayarlandığından emin olun. Olmadan, ses devre dışı kalır ve ajan metne geri döner.

## Teknik arka plan

Nasıl çalıştığını merak ettiniz mi? familiar-ai'nin arkasındaki araştırma ve tasarım kararları için [docs/technical.md](./docs/technical.md) belgesine bakın — ReAct, SayCan, Reflexion, Voyager, istek sistemi ve daha fazlası.

---

## Katkıda bulunma

familiar-ai açık bir deney. Eğer bu durumlardan herhangi biri sizinle örtüşüyorsa — teknik veya felsefi olarak — katkılarınız çok hoş karşılanır.

**Başlamak için iyi yerler:**

| Alan | Ne gerekiyor |
|------|--------------|
| Yeni donanım | Daha fazla kamera (RTSP, IP Webcam), mikrofonlar, aktüatörler için destek |
| Yeni araçlar | Web araması, ev otomasyonu, takvim, MCP aracılığıyla herhangi bir şey |
| Yeni arka uçlar | `stream_turn` arayüzüne uyan herhangi bir LLM veya yerel model |
| Persona şablonları | Farklı diller ve kişilikler için ME.md şablonları |
| Araştırma | Daha iyi iste aktarıcıları, hafıza geri getirme, zihin teorisi ifadesi |
| Belgeler | Eğitimler, kılavuzlar, çeviriler |

Geliştirme kurulumu, kod stili ve PR yönergeleri için [CONTRIBUTING.md](./CONTRIBUTING.md) sayfasına bakın.

Nereden başlayacağınızdan emin değilseniz, [bir sorun açın](https://github.com/lifemate-ai/familiar-ai/issues) — doğru yöne sizi yönlendirmekten mutluluk duyarım.

---

## Lisans

[MIT](./LICENSE)
