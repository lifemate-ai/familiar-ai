# familiar-ai 🐾

**Isang AI na kasama mo sa buhay** — may mata, boses, mga paa, at alaala.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ay isang AI companion na nakatira sa iyong tahanan.
Itakda ito sa loob ng ilang minuto. Walang kinakailangang coding.

Nakikita nito ang totoong mundo sa pamamagitan ng mga camera, gumagalaw sa isang robot na katawan, nagsasalita ng mal aloud, at naalala ang mga nakikita nito. Bigyan ito ng pangalan, isulat ang personalidad nito, at hayaan itong makasama ka.

## Ano ang kaya nitong gawin

- 👁 **Makita** — kumukuha ng mga imahe mula sa isang Wi-Fi PTZ camera o USB webcam
- 🔄 **Tumingin paligid** — umuikot at umaangat ang camera upang galugarin ang paligid nito
- 🦿 **Gumagalaw** — nagpapalakad ng robot vacuum upang maglakbay sa silid
- 🗣 **Nagsasalita** — nakikipag-usap sa pamamagitan ng ElevenLabs TTS
- 🎙 **Nakikinig** — hands-free na voice input sa pamamagitan ng ElevenLabs Realtime STT (opt-in)
- 🧠 **Naaalala** — aktibong nag-iimbak at nagbabalik ng mga alaala gamit ang semantic search (SQLite + embeddings)
- 🫀 **Teorya ng Isip** — kinukuha ang pananaw ng ibang tao bago tumugon
- 💭 **Nais** — mayroong sariling panloob na pagnanasa na nagsasanhi ng autonomous na pag-uugali

## Paano ito gumagana

familiar-ai ay nagpapatakbo ng [ReAct](https://arxiv.org/abs/2210.03629) loop na pinapagana ng iyong napiling LLM. Nakikita nito ang mundo sa pamamagitan ng mga tool, nag-iisip kung ano ang susunod na dapat gawin, at kumikilos — tulad ng isang tao.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kapag idle, kumikilos ito ayon sa sariling mga kagustuhan: pagkamausisa, nais na tumingin sa labas, at pagkasabik sa taong kasama nito.

## Pagsisimula

### 1. I-install ang uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. I-install ang ffmpeg

Ang ffmpeg ay **kinakailangan** para sa pagkuha ng larawan mula sa camera at pagpapalabas ng audio.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — o i-download mula sa [ffmpeg.org](https://ffmpeg.org/download.html) at idagdag sa PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Tiyakin: `ffmpeg -version`

### 3. I-clone at i-install

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. I-configure

```bash
cp .env.example .env
# I-edit ang .env gamit ang iyong mga settings
```

**Minimum na kinakailangan:**

| Variable | Deskripsyon |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Ang iyong API key para sa napiling platform |

**Opsyonal:**

| Variable | Deskripsyon |
|----------|-------------|
| `MODEL` | Pangalan ng modelo (sensible defaults per platform) |
| `AGENT_NAME` | Display name na ipinapakita sa TUI (e.g. `Yukine`) |
| `CAMERA_HOST` | IP address ng iyong ONVIF/RTSP camera |
| `CAMERA_USER` / `CAMERA_PASS` | Mga kredensyal ng camera |
| `ELEVENLABS_API_KEY` | Para sa output ng boses — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` upang i-enable ang palaging on na hands-free voice input (kinakailangan ang `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Saan ipapalabas ang audio: `local` (PC speaker, default) \| `remote` (camera speaker) \| `both` |
| `THINKING_MODE` | Anthropic lamang — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Adaptive thinking effort: `high` (default) \| `medium` \| `low` \| `max` (Opus 4.6 lamang) |

### 5. Lumikha ng iyong paborito

```bash
cp persona-template/en.md ME.md
# I-edit ang ME.md — bigyan ito ng pangalan at personalidad
```

### 6. Patakbuhin

```bash
./run.sh             # Textual TUI (inirerekomenda)
./run.sh --no-tui    # Plain REPL
```

---

## Pagpili ng LLM

> **Inirerekomenda: Kimi K2.5** — pinakamahusay na agentic performance na nasubukan hanggang ngayon. Napapansin ang konteksto, nagtatanong ng mga follow-up na tanong, at kumikilos ng autonomously sa mga paraang hindi kayang gawin ng ibang mga modelo. Presyong katulad ng Claude Haiku.

| Platform | `PLATFORM=` | Default model | Saan makukuha ang key |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (the command) | — |

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

> **Tala:** Upang huwag paganahin ang mga lokal/NVIDIA modelos, huwag lamang itakda ang `BASE_URL` sa isang lokal na endpoint tulad ng `http://localhost:11434/v1`. Gumamit ng mga cloud provider sa halip.

**CLI tool `.env` halimbawa:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — walang {}, ang prompt ay dumaan sa stdin
```

---

## MCP Servers

familiar-ai ay maaaring kumonekta sa anumang [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Pinapayagan nitong ikonekta ang panlabas na memorya, access sa filesystem, web search, o anumang iba pang tool.

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

Dalawang uri ng transport ang sinusuportahan:
- **`stdio`**: ilunsad ang lokal na subprocess (`command` + `args`)
- **`sse`**: kumonekta sa isang HTTP+SSE server (`url`)

Lagyan ng override ang lokasyon ng config file gamit ang `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai ay gumagana sa anumang hardware na mayroon ka — o wala kahit ano.

| Bahagi | Ano ang ginagawa nito | Halimbawa | Kinakailangan? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Mata + leeg | Tapo C220 (~$30) | **Inirerekomenda** |
| USB webcam | Mata (nakapirmi) | Anumang UVC camera | **Inirerekomenda** |
| Robot vacuum | Mga paa | Anumang Tuya-compatible modelo | Hindi |
| PC / Raspberry Pi | Utak | Anumang tumatakbo ang Python | **Oo** |

> **Matinding inirerekomenda ang isang camera.** Nang wala ito, ang familiar-ai ay maaari pa ring makipag-usap — ngunit hindi nito makikita ang mundo, na syang kabuuan ng layunin.

### Minimal na setup (walang hardware)

Gusto mo lang bang subukan ito? Kailangan mo lamang ng API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Patakbuhin ang `./run.sh` at simulan ang pagchat. Magdagdag ng hardware habang ikaw ay nasa proseso.

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

1. Kumuha ng API key sa [elevenlabs.io](https://elevenlabs.io/)
2. I-set sa `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opsyonal, gumagamit ng default voice kung hindi nailagay
   ```

Mayroong dalawang destinasyon ng playback, na nakokontrol ng `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC speaker (default)
TTS_OUTPUT=remote   # camera speaker lamang
TTS_OUTPUT=both     # camera speaker + PC speaker sabay-sabay
```

#### A) Speaker ng camera (sa pamamagitan ng go2rtc)

I-set ang `TTS_OUTPUT=remote` (o `both`). Nangangailangan ng [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. I-download ang binary mula sa [releases page](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Ilagay at pangalanan ito:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x kinakailangan

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Lumikha ng `go2rtc.yaml` sa parehong directory:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gamitin ang mga kredensyal ng lokal na camera account (hindi ang iyong TP-Link cloud account).

4. Awtomatikong ilulunsad ng familiar-ai ang go2rtc sa pag-launch. Kung ang iyong camera ay sumusuporta sa two-way audio (backchannel), ang boses ay ipe-play mula sa speaker ng camera.

#### B) Lokal na speaker ng PC

Ang default (`TTS_OUTPUT=local`). Sinusubukan ang mga player sa pagkakasunod-sunod: **paplay** → **mpv** → **ffplay**. Ginagamit din ito bilang fallback kapag `TTS_OUTPUT=remote` at hindi magagamit ang go2rtc.

| OS | I-install |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (o `paplay` sa pamamagitan ng `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — itakda ang `PULSE_SERVER=unix:/mnt/wslg/PulseServer` sa `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — i-download at idagdag sa PATH, **o** `winget install ffmpeg` |

> Kung walang audio player na magagamit, ang speech ay patuloy na naging gawa — hindi lamang ito mapapagana.

### Voice input (Realtime STT)

I-set ang `REALTIME_STT=true` sa `.env` para sa palaging-on, hands-free voice input:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # parehong key na ginagamit sa TTS
```

Nag-stream ang familiar-ai ng audio mula sa mikropono sa ElevenLabs Scribe v2 at awtomatikong nagtala ng mga transcript kapag huminto ka sa pagsasalita. Walang kinakailangang pindutin. Magkasabay na coexists sa push-to-talk mode (Ctrl+T).

---

## TUI

familiar-ai ay nagsasama ng isang terminal UI na itinayo gamit ang [Textual](https://textual.textualize.io/):

- Scrollable na kasaysayan ng pag-uusap na may live streaming na teksto
- Tab-completion para sa `/quit`, `/clear`
- Itigil ang agent sa kalagitnaan ng turn sa pamamagitan ng pagta-type habang ito ay nag-iisip
- **Kasaysayan ng pag-uusap** awtomatikong nai-save sa `~/.cache/familiar-ai/chat.log`

Upang sundan ang log sa isang ibang terminal (kapaki-pakinabang para sa copy-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Ang personalidad ng iyong paborito ay nasa `ME.md`. Ang file na ito ay gitignored — ito ay sa iyo lamang.

Tingnan ang [`persona-template/en.md`](./persona-template/en.md) para sa isang halimbawa, o [`persona-template/ja.md`](./persona-template/ja.md) para sa bersyong Hapon.

---

## FAQ

**Q: Gumagana ba ito nang walang GPU?**
Oo. Ang embedding model (multilingual-e5-small) ay tumatakbo nang maayos sa CPU. Ang isang GPU ay nagpapabilis ngunit hindi kinakailangan.

**Q: Maaari ba akong gumamit ng camera bukod sa Tapo?**
Anumang camera na sumusuporta sa ONVIF + RTSP ay dapat gumana. Ang Tapo C220 ang sinubukan namin.

**Q: Naipapadala ba ang aking data saanman?**
Ang mga larawan at teksto ay ipinapadala sa iyong napiling LLM API para sa pagproseso. Ang mga alaala ay iniimbak nang lokal sa `~/.familiar_ai/`.

**Q: Bakit ang agent ay nagsusulat ng `（...）` sa halip na magsalita?**
Tiyakin na ang `ELEVENLABS_API_KEY` ay itinatakda. Kung wala ito, ang boses ay hindi pinagana at ang agent ay bumabagsak sa teksto.

## Teknikal na background

Curious tungkol sa kung paano ito gumagana? Tingnan ang [docs/technical.md](./docs/technical.md) para sa mga pananaliksik at mga desisyon sa disenyo sa likod ng familiar-ai — ReAct, SayCan, Reflexion, Voyager, ang desire system, at higit pa.

---

## Pagsusulong

familiar-ai ay isang bukas na eksperimento. Kung anumang ito ay umuugma sa iyo — teknikal o pilosopiya — ang mga kontribusyon ay lubos na tinatanggap.

**Mga magagandang lugar upang magsimula:**

| Lugar | Ano ang kinakailangan |
|------|---------------|
| Bago hardware | Suporta para sa higit pang mga camera (RTSP, IP Webcam), mikropono, actuators |
| Bago mga tool | Web search, home automation, calendar, anumang bagay sa pamamagitan ng MCP |
| Bago mga backend | Anumang LLM o lokal na modelo na umaangkop sa `stream_turn` interface |
| Mga template ng Persona | ME.md templates para sa iba't ibang wika at personalidad |
| Pananaliksik | Mas magandang mga modelo ng pagnanasa, memory retrieval, theory-of-mind prompting |
| Dokumentasyon | Mga tutorial, walkthroughs, translations |

Tingnan ang [CONTRIBUTING.md](./CONTRIBUTING.md) para sa dev setup, code style, at mga patakaran ng PR.

Kung hindi ka sigurado kung saan magsisimula, [buksan ang isang isyu](https://github.com/lifemate-ai/familiar-ai/issues) — masaya akong ituro ka sa tamang direksyon.

---

## Lisensya

[MIT](./LICENSE)
