```markdown
# familiar-ai 🐾

**AI sing urip bebarengan karo sampeyan** — nganggo mata, suara, sikil, lan memori.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Tersedia ing 74 bahasa](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai iku kanca AI sing urip ing omah sampeyan.
Atur sajrone menit. Ora perlu coding.

Iku ngrasakake jagad nyata liwat kamera, obah ing badan robot, ngomong kanthi nyaring, lan ngelingi apa sing dideleng. Ganti jeneng, tulis pribadine, lan biarkan urip bareng sampeyan.

## Apa sing bisa dilakoni

- 👁 **Deleng** — njupuk gambar saka kamera Wi-Fi PTZ utawa webcam USB
- 🔄 **Ndeleng sakupeng** — ngusap lan nuntun kamera kanggo njelajah lingkungan sekitar
- 🦿 **Obah** — nggerakake vacuum robot kanggo mlaku-mlaku ing ruangan
- 🗣 **Ngomong** — ngomong liwat ElevenLabs TTS
- 🎙 **Ngrungokake** — input suara tanpa tangan liwat ElevenLabs Realtime STT (opt-in)
- 🧠 **Eling** — aktif nyimpen lan eling kenangan nganggo panelusuran semantik (SQLite + embedding)
- 🫀 **Teori Pikiran** — njupuk perspektif wong liya sadurunge nanggapi
- 💭 **Keinginan** — nduweni dorongan internal sing nyebabake perilaku otonom

## Carane iki bisa

familiar-ai nglakokake loop [ReAct](https://arxiv.org/abs/2210.03629) sing didhukung dening pilihan LLM sampeyan. Iku ngrasakake jagad liwat alat, mikir apa sing kudu ditindakake sabanjure, lan tumindak — persis kaya wong.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Nalika nganggur, iku tumindak adhedhasar keinginan dhewe: kepinginan, pengin ndeleng njaba, kangen marang wong sing diduduki.

## Miwiti

### 1. Instal uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Utawa: `winget install astral-sh.uv`

### 2. Instal ffmpeg

ffmpeg iku **diperlukan** kanggo njupuk gambar kamera lan muter audio.

| OS | Perintah |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — utawa download saka [ffmpeg.org](https://ffmpeg.org/download.html) lan tambahake PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifikasi: `ffmpeg -version`

### 3. Clone lan instal

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

**Minimum dibutuhkan:**

| Variabel | Deskripsi |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Kunci API sampeyan kanggo platform sing dipilih |

**Pilihan:**

| Variabel | Deskripsi |
|----------|-------------|
| `MODEL` | Jeneng model (default wajar per platform) |
| `AGENT_NAME` | Jeneng tampilan sing dituduhake ing TUI (contoh: `Yukine`) |
| `CAMERA_HOST` | Alamat IP kamera ONVIF/RTSP sampeyan |
| `CAMERA_USER` / `CAMERA_PASS` | Kredensial kamera |
| `ELEVENLABS_API_KEY` | Kanggo output suara — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` kanggo ngaktifake input suara tanpa tangan sing terus-terusan (mbutuhake `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Ngendi kanggo muter audio: `local` (speaker PC, default) \| `remote` (speaker kamera) \| `both` |
| `THINKING_MODE` | Anthropic mung — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Usaha mikir adaptif: `high` (default) \| `medium` \| `low` \| `max` (Opus 4.6 mung) |

### 5. Gawé familiar sampeyan

```bash
cp persona-template/en.md ME.md
# Edit ME.md — ganti jeneng lan pranatan
```

### 6. Mlaku

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI tekstual (disaranake)
./run.sh --no-tui    # REPL polos
```

**Windows:**
```bat
run.bat              # TUI tekstual (disaranake)
run.bat --no-tui     # REPL polos
```

---

## Pilih LLM

> **Disaranake: Kimi K2.5** — performa agen sing paling apik sing wis dites nganti saiki. Nggatekake konteks, takon pitakon lan tumindak otonom kanthi cara sing ora ditindakake model liyane. Regane padha karo Claude Haiku.

| Platform | `PLATFORM=` | Model default | Ngendi entuk kunci |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Kompatibel OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
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
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = mung teks
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
MODEL=mistralai/mistral-7b-instruct  # opsional: nemtokake model
AGENT_NAME=Yukine
```

> **Cathetan:** Kanggo mateni model lokal/NVIDIA, cukup ora nyetel `BASE_URL` kanthi titik akhir lokal kaya `http://localhost:11434/v1`. Gunakake penyedia awan kanthi langkah iki.

**Contoh `.env` alat CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = arg prompt
# MODEL=ollama run gemma3:27b  # Ollama — ora {}, prompt liwat stdin
```

---

## MCP Servers

familiar-ai bisa nyambung menyang sembarang server [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Iki ngidini sampeyan nyambungake memori eksternal, akses sistem file, panelusuran web, utawa alat liyane.

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

Ngganti lokasi file konfigurasi karo `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai bisa digunakake kanthi hardware apa wae sing sampeyan duwe — utawa ora ana sama sekali.

| Bagian | Apa sing dilakoni | Contoh | Diperlukan? |
|------|-------------|---------|-----------|
| Kamera Wi-Fi PTZ | Mata + leher | Tapo C220 (~$30) | **Disaranake** |
| Webcam USB | Mata (tetep) | Sembarang kamera UVC | **Disaranake** |
| Vacuum robot | Sikil | Sembarang model kompatibel Tuya | Ora |
| PC / Raspberry Pi | Otak | Apa wae sing mlaku Python | **Ya** |

> **Kamera disaranake banget.** Tanpa kamera, familiar-ai isih bisa ngomong — nanging ora bisa ndeleng jagad, sing iku kita'repè ngatur.

### Setelan minimal (tanpa hardware)

Cukup pengin nyoba? Sampeyan mung butuh kunci API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Mlaku `./run.sh` (macOS/Linux/WSL2) utawa `run.bat` (Windows) lan mulai obrolan. Tambahake hardware nalika sampeyan mlaku.

### Kamera Wi-Fi PTZ (Tapo C220)

1. Ing app Tapo: **Setelan → Lanjut → Akun Kamera** — nggawe akun lokal (ora akun TP-Link)
2. Temokake IP kamera ing dhaptar piranti router sampeyan
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
   ELEVENLABS_VOICE_ID=...   # opsional, nggunakake swara default yen dicopot
   ```

Ana loro tujuan pemutaran, dikontrol déning `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # speaker PC (default)
TTS_OUTPUT=remote   # speaker kamera wae
TTS_OUTPUT=both     # speaker kamera + speaker PC bebarengan
```

#### A) Speaker kamera (liwat go2rtc)

Setel `TTS_OUTPUT=remote` (utawa `both`). Mbutuhake [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Download biner saka [kaca rilis](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Panggonake lan ganti jeneng:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x dibutuhake

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Gawé `go2rtc.yaml` ing direktori sing padha:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gunakake kredensial akun kamera lokal (ora akun awan TP-Link sampeyan).

4. familiar-ai miwiti go2rtc kanthi otomatis nalika diluncurake. Yen kamera sampeyan ndhukung audio dua arah (jalur mbalikke), suara bakal diputar saka speaker kamera.

#### B) Speaker PC lokal

Default (`TTS_OUTPUT=local`). Nyoba pemain kanthi urutan: **paplay** → **mpv** → **ffplay**. Uga digunakake minangka fallback nalika `TTS_OUTPUT=remote` lan go2rtc ora kasedhiya.

| OS | Instal |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (utawa `paplay` liwat `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — setel `PULSE_SERVER=unix:/mnt/wslg/PulseServer` ing `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — download lan tambahake PATH, **utawa** `winget install ffmpeg` |

> Yen ora ana pemutar audio sing kasedhiya, ucapan isih digawé — mung ora bakal muter.

### Input suara (Realtime STT)

Setel `REALTIME_STT=true` ing `.env` kanggo input suara tanpa tangan sing terus-terusan:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # kunci sing padha karo TTS
```

familiar-ai nstream audio mikrofon menyang ElevenLabs Scribe v2 lan otomatis nyimpen transkrip nalika sampeyan mandheg ngomong. Ora perlu pencet tombol. Bisa bareng mode push-to-talk (Ctrl+T).

---

## TUI

familiar-ai kalebu antarmuka terminal sing dibangun nganggo [Textual](https://textual.textualize.io/):

- Riwayat obrolan sing bisa digulung kanthi teks streaming langsung
- Tab-completion kanggo `/quit`, `/clear`
- Ganggu agen ing tengah giliran kanthi ngetik nalika lagi mikir
- **Log obrolan** disimpen otomatis menyang `~/.cache/familiar-ai/chat.log`

Kanggo ndhukung log ing terminal liyane (migunani kanggo nyalin-tempel):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Pribadine familiar sampeyan ana ing `ME.md`. File iki diabaikan dening git — iki duweke sampeyan dhewe.

Deleng [`persona-template/en.md`](./persona-template/en.md) kanggo conto, utawa [`persona-template/ja.md`](./persona-template/ja.md) kanggo versi Jepang.

---

## FAQ

**Q: Apa iki bisa digunakake tanpa GPU?**
Ya. Model embedding (multilingual-e5-small) mlaku kanthi apik ing CPU. GPU nggawe luwih cepet nanging ora dibutuhake.

**Q: Apa aku bisa nggunakake kamera liya kajaba Tapo?**
Sembarang kamera sing ndhukung ONVIF + RTSP kudu bisa digunakake. Tapo C220 iku sing kita uji.

**Q: Apa data aku dikirim menyang ngendi?**
Gambar lan teks dikirim menyang API LLM sing sampeyan pilih kanggo proses. Kenangan disimpen sacara lokal ing `~/.familiar_ai/`.

**Q: Kenapa agen nulis `（...）` tinimbang ngomong?**
Priksa manawa `ELEVENLABS_API_KEY` disetel. Tanpa iki, suara dinonaktifake lan agen ngalih menyang teks.

## Latar belakang teknis

Penasaran babagan carane kerjane? Deleng [docs/technical.md](./docs/technical.md) kanggo riset lan keputusan desain ing balik familiar-ai — ReAct, SayCan, Reflexion, Voyager, sistem keinginan, lan liya-liyane.

---

## Nyumbang

familiar-ai iku eksperimen terbuka. Yen ana sing nyambung karo sampeyan — teknis utawa filosofis — kontribusi banget disambut.

**Panggonan sing apik kanggo miwiti:**

| Area | Apa sing dibutuhake |
|------|---------------|
| Hardware anyar | Dukungan kanggo luwih akeh kamera (RTSP, IP Webcam), mikrofon, aktuator |
| Alat anyar | Panelusuran web, otomatisasi omah, kalender, apa wae liwat MCP |
| Backend anyar | Sembarang LLM utawa model lokal sing pas karo antarmuka `stream_turn` |
| Template persona | Template ME.md kanggo basa lan pribadine sing beda |
| Riset | Model keinginan sing luwih apik, pengambilan memori, prompting teori-pikiran |
| Dokumentasi | Tutorial, walkthroughs, terjemahan |

Deleng [CONTRIBUTING.md](./CONTRIBUTING.md) kanggo setelan dev, gaya kode, lan pedoman PR.

Yen sampeyan ora yakin kudu miwiti saka endi, [bukak masalah](https://github.com/lifemate-ai/familiar-ai/issues) — seneng bisa nuduhake sampeyan arah sing bener.

---

## Lisensi

[MIT](./LICENSE)
```
