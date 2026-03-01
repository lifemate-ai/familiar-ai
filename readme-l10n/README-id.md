# familiar-ai 🐾

**Sebuah AI yang hidup di sampingmu** — dengan mata, suara, kaki, dan memori.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Tersedia dalam 74 bahasa](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai adalah teman AI yang hidup di rumahmu. 
Setel dalam hitungan menit. Tidak perlu coding.

Ia mempersepsikan dunia nyata melalui kamera, bergerak di tubuh robot, berbicara dengan suara keras, dan mengingat apa yang dilihatnya. Beri namanya, tulis kepribadiannya, dan biarkan ia hidup bersamamu.

## Apa yang dapat dilakukan

- 👁 **Melihat** — menangkap gambar dari kamera PTZ Wi-Fi atau webcam USB
- 🔄 **Melihat sekitar** — memutar dan memiringkan kamera untuk menjelajahi sekeliling
- 🦿 **Bergerak** — menggerakkan robot vacuum untuk menjelajahi ruangan
- 🗣 **Berbicara** — berbicara melalui ElevenLabs TTS
- 🎙 **Dengar** — input suara tanpa tangan melalui ElevenLabs Realtime STT (opsional)
- 🧠 **Ingat** — secara aktif menyimpan dan mengingat memori dengan pencarian semantik (SQLite + embeddings)
- 🫀 **Teori Pikiran** — mengambil perspektif orang lain sebelum merespons
- 💭 **Keinginan** — memiliki dorongan internal yang memicu perilaku otonom

## Cara kerjanya

familiar-ai menjalankan loop [ReAct](https://arxiv.org/abs/2210.03629) yang didukung oleh pilihan LLMmu. Ia mempersepsikan dunia melalui alat, berpikir tentang apa yang harus dilakukan selanjutnya, dan bertindak — seperti halnya manusia.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Saat tidak aktif, ia bertindak berdasarkan keinginannya sendiri: rasa ingin tahu, ingin melihat ke luar, merindukan orang yang ia tinggali.

## Memulai

### 1. Install uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Atau: `winget install astral-sh.uv`

### 2. Install ffmpeg

ffmpeg adalah **wajib** untuk menangkap gambar kamera dan pemutaran audio.

| OS | Perintah |
|----|----------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — atau unduh dari [ffmpeg.org](https://ffmpeg.org/download.html) dan tambahkan ke PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifikasi: `ffmpeg -version`

### 3. Clone dan install

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurasi

```bash
cp .env.example .env
# Edit .env dengan pengaturanmu
```

**Minimal yang diperlukan:**

| Variabel | Deskripsi |
|----------|-----------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Kunci API untuk platform yang dipilih |

**Opsional:**

| Variabel | Deskripsi |
|----------|-----------|
| `MODEL` | Nama model (default normal per platform) |
| `AGENT_NAME` | Nama tampilan yang ditampilkan di TUI (mis. `Yukine`) |
| `CAMERA_HOST` | Alamat IP dari kamera ONVIF/RTSP milikmu |
| `CAMERA_USER` / `CAMERA_PASS` | Kredensial kamera |
| `ELEVENLABS_API_KEY` | Untuk output suara — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` untuk mengaktifkan input suara tanpa tangan yang selalu aktif (memerlukan `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Di mana untuk memutar audio: `local` (speaker PC, default) \| `remote` (speaker kamera) \| `both` |
| `THINKING_MODE` | Hanya untuk Anthropic — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Usaha berpikir adaptif: `high` (default) \| `medium` \| `low` \| `max` (hanya Opus 4.6) |

### 5. Buat familiar-mu

```bash
cp persona-template/en.md ME.md
# Edit ME.md — berikan nama dan kepribadian
```

### 6. Jalankan

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI berbasis teks (direkomendasikan)
./run.sh --no-tui    # REPL biasa
```

**Windows:**
```bat
run.bat              # TUI berbasis teks (direkomendasikan)
run.bat --no-tui     # REPL biasa
```

---

## Memilih LLM

> **Direkomendasikan: Kimi K2.5** — kinerja agensi terbaik yang telah diuji sejauh ini. Memahami konteks, menanyakan pertanyaan lanjut, dan bertindak secara otonom dengan cara yang tidak bisa dilakukan model lain. Harganya serupa dengan Claude Haiku.

| Platform | `PLATFORM=` | Model default | Di mana mendapatkan kunci |
|----------|-------------|---------------|---------------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Kompatibel OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Alat CLI** (claude -p, ollama…) | `cli` | (perintah) | — |

**Contoh `.env` untuk Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # dari platform.moonshot.ai
AGENT_NAME=Yukine
```

**Contoh `.env` untuk Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # dari api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Contoh `.env` untuk Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # dari aistudio.google.com
MODEL=gemini-2.5-flash  # atau gemini-2.5-pro untuk kemampuan lebih tinggi
AGENT_NAME=Yukine
```

**Contoh `.env` untuk OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # dari openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opsional: tentukan model
AGENT_NAME=Yukine
```

> **Catatan:** Untuk menonaktifkan model lokal/NVIDIA, cukup jangan set `BASE_URL` ke endpoint lokal seperti `http://localhost:11434/v1`. Gunakan penyedia cloud sebagai gantinya.

**Contoh `.env` untuk alat CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = arg prompt
# MODEL=ollama run gemma3:27b  # Ollama — tidak {}, prompt dikirim melalui stdin
```

---

## Server MCP

familiar-ai dapat terhubung ke server [MCP (Model Context Protocol)](https://modelcontextprotocol.io) manapun. Ini memungkinkanmu menyambungkan memori eksternal, akses sistem file, pencarian web, atau alat lainnya.

Konfigurasi server di `~/.familiar-ai.json` (format yang sama seperti Claude Code):

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

Dua jenis transport yang didukung:
- **`stdio`**: meluncurkan subprocess lokal (`command` + `args`)
- **`sse`**: terhubung ke server HTTP+SSE (`url`)

Override lokasi file konfigurasi dengan `MCP_CONFIG=/path/to/config.json`.

---

## Perangkat Keras

familiar-ai bekerja dengan perangkat keras apa pun yang kau miliki — atau bahkan tanpa perangkat keras sama sekali.

| Bagian | Apa yang dilakukannya | Contoh | Diperlukan? |
|--------|----------------------|--------|-------------|
| Kamera PTZ Wi-Fi | Mata + leher | Tapo C220 (~$30) | **Direkomendasikan** |
| Webcam USB | Mata (statis) | Kamera UVC mana saja | **Direkomendasikan** |
| Robot vacuum | Kaki | Model kompatibel Tuya mana saja | Tidak |
| PC / Raspberry Pi | Otak | Apa saja yang menjalankan Python | **Ya** |

> **Sebuah kamera sangat dianjurkan.** Tanpa satu, familiar-ai masih dapat berbicara — tetapi ia tidak dapat melihat dunia, yang merupakan inti dari tujuan ini.

### Pengaturan minimal (tanpa perangkat keras)

Ingin mencobanya? Kau hanya perlu kunci API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Jalankan `./run.sh` (macOS/Linux/WSL2) atau `run.bat` (Windows) dan mulailah mengobrol. Tambahkan perangkat keras seiring waktu.

### Kamera PTZ Wi-Fi (Tapo C220)

1. Di aplikasi Tapo: **Pengaturan → Lanjutan → Akun Kamera** — buat akun lokal (bukan akun TP-Link)
2. Temukan IP kamera di daftar perangkat routermu
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
   ELEVENLABS_VOICE_ID=...   # opsional, menggunakan suara default jika diabaikan
   ```

Ada dua tujuan pemutaran, yang dikontrol oleh `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Speaker PC (default)
TTS_OUTPUT=remote   # Hanya speaker kamera
TTS_OUTPUT=both     # Speaker kamera + speaker PC secara bersamaan
```

#### A) Speaker kamera (melalui go2rtc)

Set `TTS_OUTPUT=remote` (atau `both`). Memerlukan [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Unduh biner dari [halaman rilis](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Tempatkan dan ganti namanya:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x diperlukan

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Buat `go2rtc.yaml` di direktori yang sama:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gunakan kredensial akun kamera lokal (bukan akun cloud TP-Linkmu).

4. familiar-ai akan memulai go2rtc secara otomatis saat diluncurkan. Jika kameramu mendukung audio dua arah (backchannel), suara akan diputar dari speaker kamera.

#### B) Speaker PC lokal

Defaultnya (`TTS_OUTPUT=local`). Mencoba pemutar secara berurutan: **paplay** → **mpv** → **ffplay**. Juga digunakan sebagai cadangan saat `TTS_OUTPUT=remote` dan go2rtc tidak tersedia.

| OS | Install |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (atau `paplay` melalui `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — set `PULSE_SERVER=unix:/mnt/wslg/PulseServer` di `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — unduh dan tambahkan ke PATH, **atau** `winget install ffmpeg` |

> Jika tidak ada pemutar audio yang tersedia, suara tetap dihasilkan — hanya saja tidak akan diputar.

### Input suara (Realtime STT)

Set `REALTIME_STT=true` di `.env` untuk input suara tanpa tangan yang selalu aktif:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # kunci yang sama seperti TTS
```

familiar-ai melakukan streaming audio mikrofon ke ElevenLabs Scribe v2 dan secara otomatis menyimpan transkrip saat kamu berhenti berbicara. Tidak perlu menekan tombol. Berfungsi berdampingan dengan mode tekan-untuk-bicara (Ctrl+T).

---

## TUI

familiar-ai menyertakan antarmuka terminal yang dibangun dengan [Textual](https://textual.textualize.io/):

- Riwayat percakapan yang dapat digulir dengan teks streaming langsung
- Penyelesaian tab untuk `/quit`, `/clear`
- Interupsi agen di tengah giliran dengan mengetik saat ia berpikir
- **Log percakapan** disimpan otomatis ke `~/.cache/familiar-ai/chat.log`

Untuk mengikuti log di terminal lain (berguna untuk menyalin-tempel):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Kepribadian familiar-mu terdapat di `ME.md`. File ini tidak akan diambil oleh git — hanya milikmu.

Lihat [`persona-template/en.md`](./persona-template/en.md) untuk contoh, atau [`persona-template/ja.md`](./persona-template/ja.md) untuk versi Jepang.

---

## FAQ

**T: Apakah ini berfungsi tanpa GPU?**
Ya. Model embedding (multilingual-e5-small) berjalan baik di CPU. GPU membuatnya lebih cepat tetapi tidak diperlukan.

**T: Bisakah saya menggunakan kamera lain selain Tapo?**
Kamera mana saja yang mendukung ONVIF + RTSP seharusnya dapat berfungsi. Tapo C220 adalah yang kami uji.

**T: Apakah data saya dikirim ke mana pun?**
Gambar dan teks dikirim ke API LLM yang kamu pilih untuk diproses. Memori disimpan secara lokal di `~/.familiar_ai/`.

**T: Mengapa agen menulis `（...）` alih-alih berbicara?**
Pastikan `ELEVENLABS_API_KEY` diatur. Tanpa itu, suara dinonaktifkan dan agen jatuh kembali ke teks.

## Latar Belakang Teknis

Penasaran bagaimana cara kerjanya? Lihat [docs/technical.md](./docs/technical.md) untuk penelitian dan keputusan desain di balik familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistem keinginan, dan lainnya.

---

## Kontribusi

familiar-ai adalah eksperimen terbuka. Jika ada yang beresonansi denganmu — secara teknis atau filosofis — kontribusi sangat diterima.

**Tempat yang baik untuk memulai:**

| Area | Apa yang dibutuhkan |
|------|---------------------|
| Perangkat keras baru | Dukungan untuk lebih banyak kamera (RTSP, IP Webcam), mikrofon, aktuator |
| Alat baru | Pencarian web, otomasi rumah, kalender, apa pun melalui MCP |
| Backend baru | Model LLM atau lokal mana saja yang sesuai dengan antarmuka `stream_turn` |
| Template persona | Template ME.md untuk berbagai bahasa dan kepribadian |
| Penelitian | Model keinginan yang lebih baik, pengambilan memori, prompting teori-pikiran |
| Dokumentasi | Tutorial, penjelasan, terjemahan |

Lihat [CONTRIBUTING.md](./CONTRIBUTING.md) untuk pengaturan dev, gaya kode, dan pedoman PR.

Jika kamu ragu mau mulai dari mana, [buka sebuah isu](https://github.com/lifemate-ai/familiar-ai/issues) — senang hati membantumu ke arah yang benar.

---

## Lisensi

[MIT](./LICENSE)

[→ English README](../README.md)
