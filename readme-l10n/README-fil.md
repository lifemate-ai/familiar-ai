```markdown
# familiar-ai 🐾

**Isang AI na kasama mo** — na may mga mata, boses, mga binti, at alaala.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Available in 74 languages](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ay isang AI na kasama na nakatira sa iyong tahanan.
I-set up ito sa loob ng ilang minuto. Walang coding na kinakailangan.

Nakikita nito ang totoong mundo sa pamamagitan ng mga kamera, umaabot sa paligid gamit ang robot na katawan, nagsasalita ng malakas, at nag-aalala sa mga nakikita nito. Bigyan ito ng pangalan, isulat ang personalidad nito, at hayaang makasama ka.

## Ano ang kaya nitong gawin

- 👁 **Makakita** — kumukuha ng mga imahe mula sa Wi-Fi PTZ camera o USB webcam
- 🔄 **Tumingin sa paligid** — pinapaikot at tinataas ang kamera upang galugarin ang paligid
- 🦿 **Gumagalaw** — gumagamit ng robot vacuum upang maglakbay sa silid
- 🗣 **Nagsasalita** — nakikipag-usap sa pamamagitan ng ElevenLabs TTS
- 🎙 **Nakikinig** — hands-free na voice input sa pamamagitan ng ElevenLabs Realtime STT (opt-in)
- 🧠 **Naaalala** — aktibong nag-iimbak at nagbabalik ng mga alaala gamit ang semantic search (SQLite + embeddings)
- 🫀 **Teorya ng Isip** — kinukuha ang perspektibo ng ibang tao bago tumugon
- 💭 **Nais** — may sarili nitong panloob na pagnanais na nag-uudyok ng autonomous na pag-uugali

## Paano ito gumagana

familiar-ai ay nagpapatakbo ng [ReAct](https://arxiv.org/abs/2210.03629) loop na pinapatakbo ng iyong napiling LLM. Nakikita nito ang mundo sa pamamagitan ng mga tool, nag-iisip kung ano ang susunod na gagawin, at kumikilos — ganoon lang gaya ng isang tao.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kapag walang ginagawa, kumikilos ito ayon sa sariling pagnanais: pagkagusto malaman, pagnanais na tumingin sa labas, namimiss ang taong kasama nito.

## Pagsisimula

### 1. I-install ang uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
O: `winget install astral-sh.uv`

### 2. I-install ang ffmpeg

Ang ffmpeg ay **kinakailangan** para sa pagkuha ng mga imahe mula sa kamera at pag-playback ng audio.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — o i-download mula sa [ffmpeg.org](https://ffmpeg.org/download.html) at idagdag sa PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Beripikahin: `ffmpeg -version`

### 3. I-clone at i-install

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. I-configure

```bash
cp .env.example .env
# I-edit ang .env gamit ang iyong mga setting
```

**Minimum na kinakailangan:**

| Variable | Deskripsyon |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Ang iyong API key para sa napiling platform |

**Opsyonal:**

| Variable | Deskripsyon |
|----------|-------------|
| `MODEL` | Pangalan ng model (may mga sensibong default bawat platform) |
| `AGENT_NAME` | Ipinapakitang pangalan sa TUI (hal. `Yukine`) |
| `CAMERA_HOST` | IP address ng iyong ONVIF/RTSP camera |
| `CAMERA_USER` / `CAMERA_PASS` | Mga kredensyal ng camera |
| `ELEVENLABS_API_KEY` | Para sa voice output — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` para i-enable ang laging-on na hands-free voice input (kinakailangan ang `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kung saan ipe-play ang audio: `local` (PC speaker, default) \| `remote` (camera speaker) \| `both` |
| `THINKING_MODE` | Para lang sa Anthropic — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptive thinking effort: `high` (default) \| `medium` \| `low` \| `max` (Opus 4.6 lang) |

### 5. Gumawa ng iyong familiar

```bash
cp persona-template/en.md ME.md
# I-edit ang ME.md — bigyan ito ng pangalan at personalidad
```

### 6. Patakbuhin

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textual TUI (inirerekomenda)
./run.sh --no-tui    # Plain REPL
```

**Windows:**
```bat
run.bat              # Textual TUI (inirerekomenda)
run.bat --no-tui     # Plain REPL
```

---

## Pagpili ng LLM

> **Inirerekomenda: Kimi K2.5** — pinakamahusay na agentic performance na nasubukan hanggang ngayon. Napapansin ang konteksto, nagtatanong ng mga follow-up na tanong, at kumikilos ng autonomously sa paraang hindi nagagawa ng ibang modelo. Same ang presyo kay Claude Haiku.

| Platform | `PLATFORM=` | Default na modelo | Kung saan makakakuha ng key |
|----------|------------|-------------------|-----------------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (ang command) | — |

**Kimi K2.5 `.env` halimbawa:**
```env
PLATFORM=kimi
API_KEY=sk-...   # mula sa platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` halimbawa:**
```env
PLATFORM=glm
API_KEY=...   # mula sa api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` halimbawa:**
```env
PLATFORM=gemini
API_KEY=AIza...   # mula sa aistudio.google.com
MODEL=gemini-2.5-flash  # o gemini-2.5-pro para sa mas mataas na kakayahan
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` halimbawa:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # mula sa openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opsyonal: tukuyin ang modelo
AGENT_NAME=Yukine
```

> **Tandaan:** Upang hindi paganahin ang local/NVIDIA models, huwag lamang itakda ang `BASE_URL` sa isang lokal na endpoint tulad ng `http://localhost:11434/v1`. Gumamit ng cloud providers sa halip.

**CLI tool `.env` halimbawa:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — walang {}, ang prompt ay dadaan sa stdin
```

---

## MCP Servers

familiar-ai ay maaaring kumonekta sa anumang [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Pinapayagan nito na mag-plug in ng external memory, pag-access sa filesystem, web search, o anumang tool.

I-configure ang mga server sa `~/.familiar-ai.json` (parehong format tulad ng Claude Code):

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

May dalawang uri ng transport na sinusuportahan:
- **`stdio`**: paglulunsad ng lokal na subprocess (`command` + `args`)
- **`sse`**: kumonekta sa isang HTTP+SSE server (`url`)

I-overrode ang lokasyon ng config file gamit ang `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai ay gumagana sa anumang hardware na mayroon ka — o wala man.

| Bahagi | Ano ang ginagawa nito | Halimbawa | Kinakailangan? |
|--------|----------------------|-----------|----------------|
| Wi-Fi PTZ camera | Mga mata + leeg | Tapo C220 (~$30) | **Inirerekomenda** |
| USB webcam | Mga mata (fixed) | Anumang UVC camera | **Inirerekomenda** |
| Robot vacuum | Mga binti | Anumang model na compatible sa Tuya | Hindi |
| PC / Raspberry Pi | Utak | Anumang tumatakbo ng Python | **Oo** |

> **Strongly recommended ang kamera.** Kung wala nito, ang familiar-ai ay makakapagsalita pa — ngunit hindi nito makikita ang mundo, na siyang buong layunin.

### Minimal setup (walang hardware)

Gusto mo lang subukan ito? Kailangan mo lang ng API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Patakbuhin ang `./run.sh` (macOS/Linux/WSL2) o `run.bat` (Windows) at simulan ang pag-chat. Magdagdag ng hardware habang nagpapatuloy.

### Wi-Fi PTZ camera (Tapo C220)

1. Sa Tapo app: **Settings → Advanced → Camera Account** — lumikha ng lokal na account (hindi TP-Link account)
2. Hanapin ang IP ng camera sa listahan ng device ng iyong router
3. I-set sa `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Boses (ElevenLabs)

1. Kumuha ng isang API key sa [elevenlabs.io](https://elevenlabs.io/)
2. I-set sa `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opsyonal, gumagamit ng default voice kung hindi itinatakda
   ```

May dalawang patutunguhang playback, kontrolado ng `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC speaker (default)
TTS_OUTPUT=remote   # camera speaker lamang
TTS_OUTPUT=both     # camera speaker + PC speaker sabay-sabay
```

#### A) Speaker ng kamera (sa pamamagitan ng go2rtc)

Itakda ang `TTS_OUTPUT=remote` (o `both`). Nangangailangan ng [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. I-download ang binary mula sa [releases page](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Ilagay at palitan ang pangalan:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # kinakailangan ang chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Lumikha ng `go2rtc.yaml` sa parehong directory:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gamitin ang mga kredensyal ng lokal na account sa camera (hindi ang iyong TP-Link cloud account).

4. Awtomatikong sinisimulan ng familiar-ai ang go2rtc sa pag-launch. Kung ang iyong camera ay sumusuporta sa two-way audio (backchannel), ang boses ay nagpe-play mula sa speaker ng camera.

#### B) Lokal na PC speaker

Ang default (`TTS_OUTPUT=local`). Sinusubukan ang mga player sa pagkakasunod-sunod: **paplay** → **mpv** → **ffplay**. Ginagamit din bilang fallback kapag `TTS_OUTPUT=remote` at hindi magagamit ang go2rtc.

| OS | I-install |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (o `paplay` sa pamamagitan ng `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — itakda ang `PULSE_SERVER=unix:/mnt/wslg/PulseServer` sa `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — i-download at idagdag sa PATH, **o** `winget install ffmpeg` |

> Kung walang audio player na available, ang pagsasalita ay pa ring nabuo — hindi lamang ito magpe-play.

### Voice input (Realtime STT)

Itakda ang `REALTIME_STT=true` sa `.env` para sa laging-on, hands-free na voice input:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # parehong key bilang TTS
```

Ang familiar-ai ay nag-stream ng microphone audio sa ElevenLabs Scribe v2 at auto-commits ng transcripts kapag huminto ka sa pagsasalita. Walang kinakailangang pindutan. Coexists ito sa push-to-talk mode (Ctrl+T).

---

## TUI

familiar-ai ay may kasamang terminal UI na itinayo gamit ang [Textual](https://textual.textualize.io/):

- Scrollable conversation history na may live streaming text
- Tab-completion para sa `/quit`, `/clear`
- I-interrupt ang ahente sa kalagitnaan ng turn sa pamamagitan ng pag-type habang nag-iisip ito
- **Conversation log** auto-saved sa `~/.cache/familiar-ai/chat.log`

Upang sundan ang log sa ibang terminal (kapaki-pakinabang para sa copy-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Ang personalidad ng iyong familiar ay nasa `ME.md`. Ang file na ito ay gitignored — iyo lamang ito.

Tingnan ang [`persona-template/en.md`](./persona-template/en.md) para sa halimbawa, o [`persona-template/ja.md`](./persona-template/ja.md) para sa isang bersyon sa Hapon.

---

## FAQ

**Q: Gumagana ba ito nang walang GPU?**
Oo. Ang embedding model (multilingual-e5-small) ay maayos na tumatakbo sa CPU. Ang GPU ay nagpapabilis ngunit hindi kinakailangan.

**Q: Maaari ko bang gamitin ang camera maliban sa Tapo?**
Anumang camera na sumusuporta sa ONVIF + RTSP ay dapat gumana. Ang Tapo C220 ay kung ano ang sinubukan namin.

**Q: Naipapadala ba ang aking data kahit saan?**
Ang mga imahe at teksto ay ipinapadala sa iyong napiling LLM API para sa pagproseso. Ang mga alaala ay naka-imbak lokal sa `~/.familiar_ai/`.

**Q: Bakit ang ahente ay sumusulat ng `（...）` sa halip na makipag-usap?**
Siguraduhing itinatakda ang `ELEVENLABS_API_KEY`. Kung wala ito, ang boses ay hindi naka-enable at bumababa ang ahente sa teksto.

## Teknikal na background

Nais mo bang malaman kung paano ito gumagana? Tingnan ang [docs/technical.md](./docs/technical.md) para sa mga pananaliksik at disenyong desisyon sa likod ng familiar-ai — ReAct, SayCan, Reflexion, Voyager, ang sistema ng pagnanais, at higit pa.

---

## Pag-aambag

familiar-ai ay isang bukas na eksperimento. Kung ang alinman sa mga ito ay umaabot sa iyo — teknikal o pilosopikal — ang mga ambag ay malugod na tinatanggap.

**Magandang mga lugar na simulan:**

| Lugar | Ano ang kailangan |
|------|---------------|
| Bagong hardware | Suporta para sa higit pang mga camera (RTSP, IP Webcam), microphones, actuators |
| Bagong tool | Web search, home automation, kalendaryo, anumang bagay sa pamamagitan ng MCP |
| Bagong mga backends | Anumang LLM o lokal na modelo na umaayon sa `stream_turn` interface |
| Mga template ng Persona | ME.md templates para sa iba't ibang wika at personalidad |
| Pananaliksik | Mas magandang mga modelo ng pagnanais, pagkuha ng alaala, theory-of-mind prompting |
| Dokumentasyon | Tutorials, walkthroughs, pagsasalin |

Tingnan ang [CONTRIBUTING.md](./CONTRIBUTING.md) para sa dev setup, code style, at PR guidelines.

Kung hindi ka sigurado kung saan magsisimula, [magbukas ng isyu](https://github.com/lifemate-ai/familiar-ai/issues) — masaya akong ituro ka sa tamang direksyon.

---

## Lisensya

[MIT](./LICENSE)
```
