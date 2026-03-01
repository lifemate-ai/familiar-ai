```markdown
# familiar-ai 🐾

**Nglembara AI sing urip bebarengan karo sampeyan** — kanthi mripat, swara, sikil, lan memori.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai iku minangka teman AI sing urip ing omah sampeyan.
Pasang ing menit. Orak perlu coding.

Iku ngerteni jagad nyata liwat kamera, obah ing awak robot, omong kanthi keras, lan eling apa sing dideleng. Wenehi jeneng, tulis kepribadian, lan ayo urip bareng sampeyan.

## Apa sing bisa ditindakake

- 👁 **Ndelok** — njupuk gambar saka kamera Wi-Fi PTZ utawa webcam USB
- 🔄 **Ndelok sekitar** — nyusup lan nyemak kamera kanggo njelajah sekitar
- 🦿 **Obah** — ngalor ngidul nganggo robot vacuum kanggo muter ing ruang
- 🗣 **Ngomong** — obrolan liwat ElevenLabs TTS
- 🎙 **Ngrungokake** — input swara tanpa tangan liwat ElevenLabs Realtime STT (opt-in)
- 🧠 **Eleng** — aktif nyimpen lan ngelingi memori kanthi telusuran semantik (SQLite + embeddings)
- 🫀 **Teori Pikiran** — njupuk perspektif wong liya sadurunge balesan
- 💭 **Kepinginan** — nduweni dorongan internal dhewe sing nyebabake perilaku otonom

## Carane kerjane

familiar-ai mlaku ing loop [ReAct](https://arxiv.org/abs/2210.03629) sing didorong dening pilihan LLM sampeyan. Iku ngerteni jagad liwat alat, mikir babagan apa sing kudu ditindakake sabanjure, lan tumindak — padha kaya wong.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Nalika ora ana aktivitas, iku tumindak adhedhasar kepinginan dhewe: rasa penasaran, pengin ndeleng metu, kangen wong sing urip bareng.

## Miwiti

### 1. Instal uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instal ffmpeg

ffmpeg iku **diperlukan** kanggo njupuk gambar kamera lan pemutaran audio.

| OS | Perintah |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — utawa download saka [ffmpeg.org](https://ffmpeg.org/download.html) lan tambahake menyang PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifikasi: `ffmpeg -version`

### 3. Klon lan instal

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Konfigurasi

```bash
cp .env.example .env
# Edit .env kanthi setelan sampeyan
```

**Minimal sing dibutuhake:**

| Variabel | Keterangan |
|----------|-------------|
| `PLATFORM` | `anthropic` (standar) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Kunci API sampeyan kanggo platform sing dipilih |

**Opsional:**

| Variabel | Keterangan |
|----------|-------------|
| `MODEL` | Jeneng model (default sing wajar miturut platform) |
| `AGENT_NAME` | Jeneng tampilan sing dituduhake ing TUI (contoh: `Yukine`) |
| `CAMERA_HOST` | Alamat IP kamera ONVIF/RTSP sampeyan |
| `CAMERA_USER` / `CAMERA_PASS` | Kredensial kamera |
| `ELEVENLABS_API_KEY` | Kanggo output swara — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` kanggo ngaktifake input swara tanpa tangan sing selamanya aktif (mbutuhake `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Ngendi muter audio: `local` (speaker PC, default) \| `remote` (speaker kamera) \| `both` |
| `THINKING_MODE` | Mung Anthropic — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Upaya berpikir adaptif: `high` (default) \| `medium` \| `low` \| `max` (Opus 4.6 mung) |

### 5. Ciptakna familiar sampeyan

```bash
cp persona-template/en.md ME.md
# Edit ME.md — wenehi jeneng lan kepribadian
```

### 6. Lakoni

```bash
./run.sh             # TUI teks (disaranake)
./run.sh --no-tui    # REPL polos
```

---

## Milih LLM

> **Disaranake: Kimi K2.5** — kinerja agen terbaik sing dites nganti saiki. Ngetokake konteks, takon pertanyaan terus, lan tumindak otonom kanthi cara sing ora ditindakake model liyane. Regane mirip karo Claude Haiku.

| Platform | `PLATFORM=` | Model default | Ngendi entuk kunci |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-kompatibel (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (perintah) | — |

**Contoh `.env` Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # saka platform.moonshot.ai
AGENT_NAME=Yukine
```

**Contoh `.env` Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # saka api.z.ai
MODEL=glm-4.6v   # bisa ndeleng; glm-4.7 / glm-5 = mung teks
AGENT_NAME=Yukine
```

**Contoh `.env` Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # saka aistudio.google.com
MODEL=gemini-2.5-flash  # utawa gemini-2.5-pro kanggo kapabilitas luwih dhuwur
AGENT_NAME=Yukine
```

**Contoh `.env` OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # saka openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opsional: spésifikasi model
AGENT_NAME=Yukine
```

> **Catatan:** Kanggo mateni model lokal/NVIDIA, cukup aja set `BASE_URL` menyang endpoint lokal kaya `http://localhost:11434/v1`. Gunakake penyedia cloud minangka gantine.

**Contoh `.env` CLI tool:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argumen prompt
# MODEL=ollama run gemma3:27b  # Ollama — ora {}, prompt mlebu liwat stdin
```

---

## Server MCP

familiar-ai bisa nyambung menyang server [MCP (Model Context Protocol)](https://modelcontextprotocol.io) endi wae. Iki ngidini sampeyan nyambungake memori eksternal, akses sistem file, telusuri web, utawa alat liyane.

Konfigurasi server ing `~/.familiar-ai.json` (format sing padha karo Claude Code):

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

Dua jinis transport didhukung:
- **`stdio`**: ngluncurake subprocess lokal (`command` + `args`)
- **`sse`**: nyambung menyang server HTTP+SSE (`url`)

Override lokasi file konfigurasi nganggo `MCP_CONFIG=/path/to/config.json`.

---

## Perangkat keras

familiar-ai bisa digunakake nganggo perangkat keras apa wae — utawa ora ana.

| Bagian | Apa sing ditindakake | Contoh | Diperlukan? |
|------|-------------|---------|-----------|
| Kamera Wi-Fi PTZ | Mripat + rangka | Tapo C220 (~$30) | **Disaranake** |
| Webcam USB | Mripat (tetep) | Sapa kamera UVC | **Disaranake** |
| Robot vacuum | Sikil | Sapa model sing kompatibel Tuya | Ora |
| PC / Raspberry Pi | Otak | Apa wae sing mlaku Python | **Ya** |

> **Kamera atrak banget disaranake.** Tanpa siji, familiar-ai isih bisa omong — nanging ora bisa ndeleng jagad, sing sejatine maksude.

### Setelan minimal (tanpa perangkat keras)

Cukup pengin nyoba? Sampeyan mung butuh kunci API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Lakoni `./run.sh` lan miwiti ngobrol. Tambahake perangkat keras kaya sing sampeyan jalani.

### Kamera Wi-Fi PTZ (Tapo C220)

1. Ing aplikasi Tapo: **Setelan → Advanced → Kamera Akun** — nggawe akun lokal (ora akun TP-Link)
2. Goleki IP kamera ing dhaptar perangkat router sampeyan
3. Setel ing `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Suara (ElevenLabs)

1. Entuk kunci API ing [elevenlabs.io](https://elevenlabs.io/)
2. Setel ing `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opsional, nggunakake swara default yen dilalekake
   ```

Ana rong tujuan pemutaran, diatur dening `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # speaker PC (default)
TTS_OUTPUT=remote   # speaker kamera wae
TTS_OUTPUT=both     # speaker kamera + speaker PC kanthi sekaligus
```

#### A) Speaker kamera (via go2rtc)

Setel `TTS_OUTPUT=remote` (utawa `both`). Mbutuhake [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Download biner saka [halaman rilis](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Tempatake lan ganti jeneng:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x dibutuhake

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Ciptakna `go2rtc.yaml` ing direktori sing padha:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gunakake kredensial akun kamera lokal (ora akun cloud TP-Link sampeyan).

4. familiar-ai miwiti go2rtc kanthi otomatis nalika diluncurake. Yen kamera sampeyan ndhukung audio loro arah (backchannel), swara bakal metu saka speaker kamera.

#### B) Speaker PC lokal

Default (`TTS_OUTPUT=local`). Nyoba pemain ing urutan: **paplay** → **mpv** → **ffplay**. Uga digunakake minangka fallback nalika `TTS_OUTPUT=remote` lan go2rtc ora kasedhiya.

| OS | Instal |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (utawa `paplay` liwat `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — set `PULSE_SERVER=unix:/mnt/wslg/PulseServer` ing `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — download lan tambahake menyang PATH, **utawa** `winget install ffmpeg` |

> Yen ora ana pemain audio sing kasedhiya, ucapan isih digawe — mung ora bakal muter.

### Input suara (Realtime STT)

Setel `REALTIME_STT=true` ing `.env` kanggo input suara tanpa tangan sing selamanya aktif:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # kunci sing padha kaya TTS
```

familiar-ai ngalir audio mikrofon menyang ElevenLabs Scribe v2 lan otomatis nyimpen transkrip nalika sampeyan mandheg ngomong. Ora perlu penek tombol. Coexist karo mode push-to-talk (Ctrl+T).

---

## TUI

familiar-ai nyakup UI terminal sing dibangun nganggo [Textual](https://textual.textualize.io/):

- Riwayat obrolan sing bisa digulir kanthi teks streaming langsung
- Tab-completion kanggo `/quit`, `/clear`
- Nginterupsi agen nalika mikir kanthi ngetik nalika lagi mikir
- **Log obrolan** disimpen otomatis ing `~/.cache/familiar-ai/chat.log`

Kanggo ngekor log ing terminal liyane (berguna kanggo copy-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Kepribadian familiar sampeyan urip ing `ME.md`. File iki diabaikan ing git — iki mung dadi milik sampeyan.

Goleki [`persona-template/en.md`](./persona-template/en.md) kanggo conto, utawa [`persona-template/ja.md`](./persona-template/ja.md) kanggo versi Jepang.

---

## FAQ

**Q: Apa bisa digunakake tanpa GPU?**
Ya. Model embedding (multilingual-e5-small) mlaku kanthi apik ing CPU. GPU nggawe luwih cepet nanging ora dibutuhake.

**Q: Apa bisa nggunakake kamera liyane kajaba Tapo?**
Kamera apa wae sing ndhukung ONVIF + RTSP kudu bisa digunakake. Tapo C220 iku sing kita uji.

**Q: Apa data saya dikirim menyang endi wae?**
Gambar lan teks dikirim menyang API LLM sing sampeyan pilih kanggo diproses. Memori disimpen lokal ing `~/.familiar_ai/`.

**Q: Kenapa agen nulis `（...）` tinimbang ngomong?**
Mastani `ELEVENLABS_API_KEY` wis disetel. Tanpa iki, swara dinonaktifake lan agen bali menyang teks.

## Latar Belakang Teknologi

Penasaran babagan cara kerjane? Delengen [docs/technical.md](./docs/technical.md) kanggo riset lan keputusan desain sing ana ing mburi familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistem kepinginan, lan liya-liyane.

---

## Nyumbang

familiar-ai minangka eksperimen terbuka. Yen sampeyan krasa salah siji saka iki — sacara teknis utawa filosofis — sumbangan banget disambut.

**Papan sing apik kanggo miwiti:**

| Area | Apa sing dibutuhake |
|------|---------------|
| Hardware anyar | Dhukungan kanggo luwih akeh kamera (RTSP, IP Webcam), mikrofon, aktor |
| Alat anyar | Telusuran web, otomasi omah, kalender, apa wae liwat MCP |
| Backend anyar | Sembarang LLM utawa model lokal sing cocog karo antarmuka `stream_turn` |
| Template persona | Template ME.md kanggo basa lan kepribadian sing beda |
| Riset | Model kepinginan sing luwih apik, pemulihan memori, prompting teori-pikiran |
| Dokumentasi | Tutorial, pandhuan, terjemahan |

Delengen [CONTRIBUTING.md](./CONTRIBUTING.md) kanggo setelan dev, gaya kode, lan pedoman PR.

Yen sampeyan ora yakin kudu miwiti ngendi, [buka masalah](https://github.com/lifemate-ai/familiar-ai/issues) — seneng nuntun sampeyan ing arah sing bener.

---

## Lisensi

[MIT](./LICENSE)
```
