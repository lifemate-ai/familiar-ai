# familiar-ai 🐾

**Sebuah AI yang hidup di samping Anda** — dengan mata, suara, kaki, dan memori.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai adalah teman AI yang hidup di rumah Anda. 
Atur dalam hitungan menit. Tidak perlu coding.

Ia mempersepsikan dunia nyata melalui kamera, bergerak di atas tubuh robot, berbicara keras, dan mengingat apa yang dilihatnya. Beri nama, tulis kepribadiannya, dan biarkan ia hidup dengan Anda.

## Apa yang bisa dilakukannya

- 👁 **Melihat** — menangkap gambar dari kamera PTZ Wi-Fi atau webcam USB
- 🔄 **Melihat sekitar** — memutar dan memiringkan kamera untuk menjelajahi sekitarnya
- 🦿 **Bergerak** — menggerakkan robot vakum untuk berkeliaran di ruangan
- 🗣 **Bicara** — berbicara melalui ElevenLabs TTS
- 🎙 **Dengarkan** — input suara tanpa tangan melalui ElevenLabs Realtime STT (opt-in)
- 🧠 **Ingat** — secara aktif menyimpan dan mengingat memori dengan pencarian semantik (SQLite + embeddings)
- 🫀 **Teori Pikiran** — mengambil perspektif orang lain sebelum merespons
- 💭 **Keinginan** — memiliki dorongan internal sendiri yang memicu perilaku otonom

## Cara kerjanya

familiar-ai menjalankan loop [ReAct](https://arxiv.org/abs/2210.03629) yang didorong oleh pilihan LLM Anda. Ia mempersepsikan dunia melalui alat, memikirkan apa yang harus dilakukan selanjutnya, dan bertindak — seperti layaknya seseorang.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Saat tidak aktif, ia bertindak berdasarkan keinginannya sendiri: rasa ingin tahu, ingin melihat ke luar, merindukan orang yang ia tinggal bersama.

## Memulai

### 1. Instal uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instal ffmpeg

ffmpeg adalah **diperlukan** untuk menangkap gambar dari kamera dan pemutaran audio.

| OS | Perintah |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — atau unduh dari [ffmpeg.org](https://ffmpeg.org/download.html) dan tambahkan ke PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifikasi: `ffmpeg -version`

### 3. Clone dan instal

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurasi

```bash
cp .env.example .env
# Edit .env dengan pengaturan Anda
```

**Minimum yang diperlukan:**

| Variabel | Deskripsi |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Kunci API Anda untuk platform yang dipilih |

**Opsional:**

| Variabel | Deskripsi |
|----------|-------------|
| `MODEL` | Nama model (default yang masuk akal per platform) |
| `AGENT_NAME` | Nama tampilan yang ditampilkan di TUI (mis. `Yukine`) |
| `CAMERA_HOST` | Alamat IP kamera ONVIF/RTSP Anda |
| `CAMERA_USER` / `CAMERA_PASS` | Kredensial kamera |
| `ELEVENLABS_API_KEY` | Untuk output suara — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` untuk mengaktifkan input suara tanpa tangan yang selalu aktif (memerlukan `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Tempat memutar audio: `local` (speaker PC, default) \| `remote` (speaker kamera) \| `both` |
| `THINKING_MODE` | Hanya untuk Anthropic — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Usaha berpikir adaptif: `high` (default) \| `medium` \| `low` \| `max` (hanya Opus 4.6) |

### 5. Buat familiar Anda

```bash
cp persona-template/en.md ME.md
# Edit ME.md — beri nama dan kepribadian
```

### 6. Jalankan

```bash
./run.sh             # TUI teks (disarankan)
./run.sh --no-tui    # REPL biasa
```

---

## Memilih LLM

> **Disarankan: Kimi K2.5** — kinerja agen terbaik yang diuji sejauh ini. Memperhatikan konteks, mengajukan pertanyaan lanjutan, dan bertindak secara otonom dengan cara yang tidak dilakukan oleh model lain. Harganya serupa dengan Claude Haiku.

| Platform | `PLATFORM=` | Model default | Di mana mendapatkan kunci |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (perintah) | — |

**Contoh `.env` Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # dari platform.moonshot.ai
AGENT_NAME=Yukine
```

**Contoh `.env` Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # dari api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = teks saja
AGENT_NAME=Yukine
```

**Contoh `.env` Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # dari aistudio.google.com
MODEL=gemini-2.5-flash  # atau gemini-2.5-pro untuk kemampuan yang lebih tinggi
AGENT_NAME=Yukine
```

**Contoh `.env` OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # dari openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opsional: tentukan model
AGENT_NAME=Yukine
```

> **Catatan:** Untuk menonaktifkan model lokal/NVIDIA, cukup jangan atur `BASE_URL` ke endpoint lokal seperti `http://localhost:11434/v1`. Gunakan penyedia cloud sebagai gantinya.

**Contoh `.env` CLI tool:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = arg prompt
# MODEL=ollama run gemma3:27b  # Ollama — tidak ada {}, prompt dikirim melalui stdin
```

---

## Server MCP

familiar-ai dapat terhubung ke server [MCP (Model Context Protocol)](https://modelcontextprotocol.io) mana pun. Ini memungkinkan Anda untuk menghubungkan memori eksternal, akses filesystem, pencarian web, atau alat lainnya.

Konfigurasikan server di `~/.familiar-ai.json` (format yang sama dengan Claude Code):

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

Dua jenis transportasi yang didukung:
- **`stdio`**: luncurkan subprocess lokal (`command` + `args`)
- **`sse`**: sambungkan ke server HTTP+SSE (`url`)

Timpa lokasi file konfigurasi dengan `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai bekerja dengan perangkat keras apapun yang Anda miliki — atau tanpa perangkat keras sama sekali.

| Bagian | Apa yang dilakukannya | Contoh | Diperlukan? |
|------|-------------|---------|-----------|
| Kamera PTZ Wi-Fi | Mata + leher | Tapo C220 (~$30) | **Disarankan** |
| Webcam USB | Mata (statis) | Kamera UVC mana saja | **Disarankan** |
| Robot vakum | Kaki | Model apa saja yang kompatibel dengan Tuya | Tidak |
| PC / Raspberry Pi | Otak | Apa saja yang menjalankan Python | **Ya** |

> **Kamera sangat disarankan.** Tanpa kamera, familiar-ai masih bisa berbicara — tetapi tidak bisa melihat dunia, yang merupakan inti dari tujuan ini.

### Setelan minimal (tanpa perangkat keras)

Hanya ingin mencobanya? Anda hanya perlu kunci API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Jalankan `./run.sh` dan mulai mengobrol. Tambahkan perangkat keras sesuai kebutuhan.

### Kamera PTZ Wi-Fi (Tapo C220)

1. Di aplikasi Tapo: **Pengaturan → Advanced → Kamera Akun** — buat akun lokal (bukan akun TP-Link)
2. Temukan alamat IP kamera di daftar perangkat router Anda
3. Atur di `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Suara (ElevenLabs)

1. Dapatkan kunci API di [elevenlabs.io](https://elevenlabs.io/)
2. Atur di `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opsional, menggunakan suara default jika tidak disebutkan
   ```

Ada dua tujuan pemutaran, dikendalikan oleh `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # speaker PC (default)
TTS_OUTPUT=remote   # speaker kamera saja
TTS_OUTPUT=both     # speaker kamera + speaker PC secara bersamaan
```

#### A) Speaker kamera (melalui go2rtc)

Atur `TTS_OUTPUT=remote` (atau `both`). Memerlukan [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Unduh biner dari [halaman rilis](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Tempatkan dan ganti namanya:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x required

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Buat `go2rtc.yaml` di direktori yang sama:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gunakan kredensial akun kamera lokal (bukan akun cloud TP-Link Anda).

4. familiar-ai secara otomatis memulai go2rtc saat diluncurkan. Jika kamera Anda mendukung audio dua arah (saluran balik), suara akan diputar dari speaker kamera.

#### B) Speaker PC lokal

Default (`TTS_OUTPUT=local`). Mencoba pemutar dalam urutan: **paplay** → **mpv** → **ffplay**. Juga digunakan sebagai fallback saat `TTS_OUTPUT=remote` dan go2rtc tidak tersedia.

| OS | Instal |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (atau `paplay` melalui `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — atur `PULSE_SERVER=unix:/mnt/wslg/PulseServer` di `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — unduh dan tambahkan ke PATH, **atau** `winget install ffmpeg` |

> Jika tidak ada pemutar audio yang tersedia, suara tetap dihasilkan — hanya saja tidak akan diputar.

### Input suara (Realtime STT)

Atur `REALTIME_STT=true` di `.env` untuk input suara tanpa tangan yang selalu aktif:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # kunci yang sama seperti TTS
```

familiar-ai mengalirkan audio mikrofon ke ElevenLabs Scribe v2 dan secara otomatis menyimpan transkrip saat Anda berhenti berbicara. Tidak perlu menekan tombol. Beroperasi bersamaan dengan mode tekan untuk bicara (Ctrl+T).

---

## TUI

familiar-ai menyertakan UI terminal yang dibangun dengan [Textual](https://textual.textualize.io/):

- Riwayat percakapan yang dapat digulir dengan streaming teks langsung
- Penyelesaian tab untuk `/quit`, `/clear`
- Menginterupsi agen di tengah-tengah dengan mengetik saat ia berpikir
- **Log percakapan** yang secara otomatis disimpan ke `~/.cache/familiar-ai/chat.log`

Untuk mengikuti log di terminal lain (berguna untuk salin-tempel):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Kepribadian familiar Anda hidup di `ME.md`. File ini diabaikan oleh git — ini hanya milik Anda.

Lihat [`persona-template/en.md`](./persona-template/en.md) untuk contoh, atau [`persona-template/ja.md`](./persona-template/ja.md) untuk versi Jepang.

---

## FAQ

**T: Apakah ini bekerja tanpa GPU?**  
Ya. Model embedding (multilingual-e5-small) berjalan baik di CPU. GPU membuatnya lebih cepat tetapi tidak diperlukan.

**T: Dapatkah saya menggunakan kamera selain Tapo?**  
Kamera mana saja yang mendukung ONVIF + RTSP seharusnya bisa bekerja. Tapo C220 adalah yang kami uji.

**T: Apakah data saya dikirim ke mana pun?**  
Gambar dan teks dikirim ke API LLM pilihan Anda untuk diproses. Memori disimpan secara lokal di `~/.familiar_ai/`.

**T: Mengapa agen menulis `（...）` alih-alih berbicara?**  
Pastikan `ELEVENLABS_API_KEY` telah diatur. Tanpa itu, suara dinonaktifkan dan agen kembali ke teks.

## Latar Belakang Teknis

Penasaran bagaimana cara kerjanya? Lihat [docs/technical.md](./docs/technical.md) untuk penelitian dan keputusan desain di balik familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistem keinginan, dan banyak lagi.

---

## Kontribusi

familiar-ai adalah eksperimen terbuka. Jika Anda merasa sesuai dengan ini — baik secara teknis maupun filosofis — kontribusi sangat diterima.

**Tempat yang baik untuk memulai:**

| Area | Apa yang dibutuhkan |
|------|---------------|
| Perangkat keras baru | Dukungan untuk lebih banyak kamera (RTSP, IP Webcam), mikrofon, aktuator |
| Alat baru | Pencarian web, automasi rumah, kalender, apa pun melalui MCP |
| Backend baru | Model LLM atau lokal yang sesuai dengan antarmuka `stream_turn` |
| Template persona | Template ME.md untuk berbagai bahasa dan kepribadian |
| Penelitian | Model keinginan yang lebih baik, pengambilan memori, prompt teori-pikiran |
| Dokumentasi | Tutorial, panduan, terjemahan |

Lihat [CONTRIBUTING.md](./CONTRIBUTING.md) untuk pengaturan pengembangan, gaya kode, dan pedoman PR.

Jika Anda tidak yakin di mana untuk memulai, [buka isu](https://github.com/lifemate-ai/familiar-ai/issues) — senang bisa membantu Anda ke arah yang benar.

---

## Lisensi

[MIT](./LICENSE)
