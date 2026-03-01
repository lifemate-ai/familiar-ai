# familiar-ai 🐾

**Satu AI yang hidup bersama anda** — dengan mata, suara, kaki, dan ingatan.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai adalah teman AI yang tinggal di rumah anda. 
Setel ia dalam beberapa minit. Tiada pengkodan diperlukan.

Ia memahami dunia nyata melalui kamera, bergerak di badan robot, berbicara dengan suara, dan mengingat apa yang dilihat. Beri ia nama, tulis personalitinya, dan biarkan ia hidup dengan anda.

## Apa yang boleh dilakukannya

- 👁 **Melihat** — menangkap gambar dari kamera PTZ Wi-Fi atau webcam USB
- 🔄 **Melihat sekeliling** — menggerakkan dan memiringkan kamera untuk menjelajahi sekeliling
- 🦿 **Bergerak** — menggerakkan penyedut debu robot untuk menjelajahi bilik
- 🗣 **Bercakap** — berbicara melalui ElevenLabs TTS
- 🎙 **Mendengar** — input suara tanpa tangan melalui ElevenLabs Realtime STT (opt-in)
- 🧠 **Ingat** — aktif menyimpan dan mengingati memori dengan carian semantik (SQLite + embeddings)
- 🫀 **Teori Minda** — mengambil perspektif orang lain sebelum memberi respons
- 💭 **Keinginan** — mempunyai dorongan dalaman yang memicu tingkah laku autonomi

## Bagaimana ia berfungsi

familiar-ai menjalankan gelung [ReAct](https://arxiv.org/abs/2210.03629) yang dipacu oleh pilihan LLM anda. Ia memahami dunia melalui alat, berfikir tentang apa yang perlu dilakukan seterusnya, dan bertindak — sama seperti seseorang.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Ketika tidak aktif, ia bertindak berdasarkan keinginannya sendiri: rasa ingin tahu, ingin melihat ke luar, merindui orang yang tinggal bersamanya.

## Mengambil langkah pertama

### 1. Pasang uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Pasang ffmpeg

ffmpeg adalah **diperlukan** untuk menangkap gambar kamera dan memainkan audio.

| OS | Perintah |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — atau muat turun dari [ffmpeg.org](https://ffmpeg.org/download.html) dan tambah ke PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Sahkan: `ffmpeg -version`

### 3. Klon dan pasang

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurasi

```bash
cp .env.example .env
# Edit .env dengan tetapan anda
```

**Minimum yang diperlukan:**

| Pembolehubah | Penerangan |
|--------------|-------------|
| `PLATFORM` | `anthropic` (lalai) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Kunci API anda untuk platform yang dipilih |

**Pilihan:**

| Pembolehubah | Penerangan |
|--------------|-------------|
| `MODEL` | Nama model (lalai yang munasabah setiap platform) |
| `AGENT_NAME` | Nama paparan yang ditunjukkan dalam TUI (contoh: `Yukine`) |
| `CAMERA_HOST` | Alamat IP kamera ONVIF/RTSP anda |
| `CAMERA_USER` / `CAMERA_PASS` | Kelayakan kamera |
| `ELEVENLABS_API_KEY` | Untuk output suara — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` untuk mengaktifkan input suara tanpa tangan yang sentiasa aktif (memerlukan `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Tempat untuk memainkan audio: `local` (pembesar suara PC, lalai) \| `remote` (pembesar suara kamera) \| `both` |
| `THINKING_MODE` | Hanya untuk Anthropic — `auto` (lalai) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Usaha berfikir yang adaptif: `high` (lalai) \| `medium` \| `low` \| `max` (Opus 4.6 sahaja) |

### 5. Cipta familiar anda

```bash
cp persona-template/en.md ME.md
# Edit ME.md — beri ia nama dan personaliti
```

### 6. Jalankan

```bash
./run.sh             # TUI teks (disyorkan)
./run.sh --no-tui    # REPL biasa
```

---

## Memilih LLM

> **Disyorkan: Kimi K2.5** — prestasi agens terbaik yang diuji setakat ini. Menyendari konteks, bertanya soalan susulan, dan bertindak secara autonomi dengan cara yang tidak dilakukan oleh model lain. Harga serupa dengan Claude Haiku.

| Platform | `PLATFORM=` | Model lalai | Di mana untuk mendapatkan kunci |
|----------|------------|-------------|---------------------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Alat CLI** (claude -p, ollama…) | `cli` | (perintah) | — |

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
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Contoh `.env` Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # dari aistudio.google.com
MODEL=gemini-2.5-flash  # atau gemini-2.5-pro untuk keupayaan lebih tinggi
AGENT_NAME=Yukine
```

**Contoh `.env` OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # dari openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # pilihan: tentukan model
AGENT_NAME=Yukine
```

> **Nota:** Untuk menyahaktifkan model tempatan/NVIDIA, cukup jangan set `BASE_URL` ke titik akhir tempatan seperti `http://localhost:11434/v1`. Gunakan penyedia awan sebaliknya.

**Contoh `.env` alat CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = arg prompt
# MODEL=ollama run gemma3:27b  # Ollama — tiada {}, prompt pergi melalui stdin
```

---

## Pelayan MCP

familiar-ai boleh menyambung ke mana-mana pelayan [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Ini membolehkan anda menyambungkan memori luaran, akses sistem fail, carian web, atau mana-mana alat lain.

Konfigurasi pelayan dalam `~/.familiar-ai.json` (format yang sama seperti Claude Code):

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

Dua jenis pengangkutan disokong:
- **`stdio`**: melancarkan subprocess tempatan (`command` + `args`)
- **`sse`**: menyambung ke pelayan HTTP+SSE (`url`)

Tindakan override lokasi fail konfigurasi dengan `MCP_CONFIG=/path/to/config.json`.

---

## Perkakasan

familiar-ai berfungsi dengan apa jua perkakasan yang anda ada — atau tiada sama sekali.

| Bahagian | Apa yang dilakukannya | Contoh | Diperlukan? |
|----------|----------------------|--------|-------------|
| Kamera PTZ Wi-Fi | Mata + leher | Tapo C220 (~$30) | **Disyorkan** |
| Webcam USB | Mata (tetap) | Sebarang kamera UVC | **Disyorkan** |
| Penyedut debu robot | Kaki | Mana-mana model yang serasi dengan Tuya | Tidak |
| PC / Raspberry Pi | Otak | Apa sahaja yang menjalankan Python | **Ya** |

> **Kamera sangat disyorkan.** Tanpa satu, familiar-ai masih boleh bercakap — tetapi ia tidak dapat melihat dunia, yang merupakan keseluruhan tujuan.

### Persediaan minimal (tanpa perkakasan)

Hanya ingin mencubanya? Anda hanya perlu kunci API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Jalankan `./run.sh` dan mula berbual. Tambahkan perkakasan bila perlu.

### Kamera PTZ Wi-Fi (Tapo C220)

1. Dalam aplikasi Tapo: **Tetapan → Lanjutan → Akaun Kamera** — buat akaun tempatan (bukan akaun TP-Link)
2. Cari IP kamera dalam senarai peranti router anda
3. Tetapkan dalam `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Suara (ElevenLabs)

1. Dapatkan kunci API di [elevenlabs.io](https://elevenlabs.io/)
2. Tetapkan dalam `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # pilihan, menggunakan suara lalai jika tidak dinyatakan
   ```

Terdapat dua destinasi playback, dikawal oleh `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Pembesar suara PC (lalai)
TTS_OUTPUT=remote   # pembesar suara kamera sahaja
TTS_OUTPUT=both     # pembesar suara kamera + pembesar suara PC secara serentak
```

#### A) Pembesar suara kamera (melalui go2rtc)

Tetapkan `TTS_OUTPUT=remote` (atau `both`). Memerlukan [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Muat turun binari dari [halaman rilis](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Letakkan dan namakan semula:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x diperlukan

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Cipta `go2rtc.yaml` dalam direktori yang sama:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gunakan kelayakan akaun kamera tempatan (bukan akaun awan TP-Link anda).

4. familiar-ai memulakan go2rtc secara automatik pada pelancaran. Jika kamera anda menyokong audio dua hala (backchannel), suara akan dimainkan dari pembesar suara kamera.

#### B) Pembesar suara PC tempatan

Lalai (`TTS_OUTPUT=local`). Mencuba pemain dalam urutan: **paplay** → **mpv** → **ffplay**. Juga digunakan sebagai fallback ketika `TTS_OUTPUT=remote` dan go2rtc tidak tersedia.

| OS | Pasang |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (atau `paplay` melalui `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — set `PULSE_SERVER=unix:/mnt/wslg/PulseServer` dalam `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — muat turun dan tambah ke PATH, **atau** `winget install ffmpeg` |

> Jika tiada pemutar audio tersedia, suara masih dihasilkan — ia cuma tidak akan dimainkan.

### Input suara (Realtime STT)

Tetapkan `REALTIME_STT=true` dalam `.env` untuk input suara tanpa tangan yang sentiasa aktif:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # kunci yang sama seperti TTS
```

familiar-ai menstrim audio mikrofon ke ElevenLabs Scribe v2 dan secara automatik menyimpan transkrip apabila anda berhenti bercakap. Tiada butang tekan diperlukan. Bersama dengan mod tekan-untuk-bicara (Ctrl+T).

---

## TUI

familiar-ai menyertakan UI terminal yang dibina dengan [Textual](https://textual.textualize.io/):

- Sejarah percakapan boleh skrol dengan teks penstriman langsung
- Lengkap-tabi untuk `/quit`, `/clear`
- Ganggu agen tengah giliran dengan menaip semasa ia berfikir
- **Log perbualan** disimpan secara automatik ke `~/.cache/familiar-ai/chat.log`

Untuk mengikuti log dalam terminal lain (berguna untuk salin-tampal):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Personaliti familiar anda berada dalam `ME.md`. Fail ini diabaikan oleh git — ia hanya untuk anda.

Lihat [`persona-template/en.md`](./persona-template/en.md) untuk contoh, atau [`persona-template/ja.md`](./persona-template/ja.md) untuk versi Jepun.

---

## FAQ

**S: Adakah ia berfungsi tanpa GPU?**
Ya. Model embedding (multilingual-e5-small) berjalan dengan baik di CPU. GPU membuatnya lebih cepat tetapi tidak diperlukan.

**S: Bolehkah saya menggunakan kamera selain Tapo?**
Sebarang kamera yang menyokong ONVIF + RTSP harus berfungsi. Tapo C220 adalah yang kami uji.

**S: Adakah data saya dihantar ke mana-mana?**
Imej dan teks dihantar ke API LLM pilihan anda untuk pemprosesan. Memori disimpan secara tempatan di `~/.familiar_ai/`.

**S: Kenapa agen menulis `（...）` dan bukan bercakap?**
Pastikan `ELEVENLABS_API_KEY` ditetapkan. Tanpanya, suara dinyahaktifkan dan agen kembali ke teks.

## Latar Belakang Teknikal

Ingin tahu bagaimana ia berfungsi? Lihat [docs/technical.md](./docs/technical.md) untuk penyelidikan dan keputusan reka bentuk di sebalik familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistem keinginan, dan banyak lagi.

---

## Sumbangan

familiar-ai adalah eksperimen terbuka. Jika mana-mana daripada ini sesuai dengan anda — secara teknikal atau falsafah — sumbangan sangat dialu-alukan.

**Tempat yang baik untuk bermula:**

| Bidang | Apa yang diperlukan |
|--------|---------------------|
| Perkakasan baru | Sokongan untuk lebih banyak kamera (RTSP, IP Webcam), mikrofon, aktuator |
| Alat baru | Carian web, automasi rumah, kalendar, apa sahaja melalui MCP |
| Backend baru | Sebarang LLM atau model tempatan yang sesuai dengan antara muka `stream_turn` |
| Templat persona | Templat ME.md untuk pelbagai bahasa dan personaliti |
| Penyelidikan | Model keinginan yang lebih baik, pengambilan memori, prompting teori-minda |
| Dokumentasi | Tutorial, panduan, terjemahan |

Lihat [CONTRIBUTING.md](./CONTRIBUTING.md) untuk penyediaan dev, gaya kode, dan garis panduan PR.

Jika anda tidak pasti di mana untuk bermula, [buka isu](https://github.com/lifemate-ai/familiar-ai/issues) — gembira untuk menunjukkan arah yang betul.

---

## Lesen

[MIT](./LICENSE)
