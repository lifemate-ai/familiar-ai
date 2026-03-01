# familiar-ai 🐾

**AI yomwe imakhala pambali panu** — yokhala ndi maso, mawu, mapazi, ndi kukumbukira.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ndi bwenzi la AI yomwe imakhala m'banja mwanu.
Iikwanira mu mphindi. Palibe coding yomwe ikufunika.

Imadziwitsidwa ndi dziko lenileni kudzera mu kamera, imayenda pa thupi la robot, imakamba, ndipo imakumbukira zomwe imawona. Perekani dzina, lembani makhalidwe ake, ndiponso mupeze imakhala nanu.

## Zomwe ikhoza kuchita

- 👁 **Onani** — imakonzera zithunzi kuchokera ku Wi-Fi PTZ kamera kapena USB webcam
- 🔄 **Onani m'zinthu** — imapita ndi kukwezera kamera kuti iphunzitse zomwe zili pafupi
- 🦿 **Yenda** — imagwira robot vacuum kuti ikhale mu chipinda
- 🗣 **Lankhulani** — imakambirana kudzera pa ElevenLabs TTS
- 🎙 **Mvetsereni** — mawu osavomerezeka kudzera pa ElevenLabs Realtime STT (osankha)
- 🧠 **Kumbukirani** — imakonza ndikuika bwino kukumbukira ndi kafukafuka ka semantic (SQLite + embeddings)
- 🫀 **Nzeru za Moyo** — imadhulitsa mtima wa munthu wina musanayankhule
- 💭 **Chimwemwe** — imakhala ndi mtundu wake wokhazikika womwe umadzasokoneza uphawi wokhulupilira

## Momwe zimatangira

familiar-ai imangogwirira ntchito [ReAct](https://arxiv.org/abs/2210.03629) loop yomwe ikuyendetsedwa ndi LLM yomwe mumasankha. Imadziwa dziko kudzera mu zida, imaganizira zomwe zidzachitike, ndiponso imayankha — monga munthu.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Ikamakhala, imachita zokondedwa zawo: curiosity, kufuna kuona kunja, kuda munthu amene imakhala naye.

## Kukhazikika

### 1. Ikani uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Ikani ffmpeg

ffmpeg ndi **chofunika** kuti mukhale ndi zithunzi kuchokera ku kamera ndi mawu amaperekedwa.

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — kapena download kuchokera ku [ffmpeg.org](https://ffmpeg.org/download.html) ndiyeno ikani mu PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Onetsetsani: `ffmpeg -version`

### 3. Clone ndi kugwiritsa ntchito

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Sinthani

```bash
cp .env.example .env
# Sinthani .env ndi zokonzedwe zanu
```

**Zofunika pansi:**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (default) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | API key yanu ya platfomu yomwe mumasankha |

**Zosankha:**

| Variable | Description |
|----------|-------------|
| `MODEL` | Dzina la model (zofunikira zofunika monga pa platfomu) |
| `AGENT_NAME` | Dzina lomwe limawonekeratu mu TUI (e.g. `Yukine`) |
| `CAMERA_HOST` | IP adilesi ya kamera yanu ya ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Maonekedwe a kamera |
| `ELEVENLABS_API_KEY` | Kwa mawu amaperekedwa — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` kuti ikhale pansi pa mawu osavomerezeka (ikufuna `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Kumene kumaperekedwa mawu: `local` (PC speaker, default) \| `remote` (kamera speaker) \| `both` |
| `THINKING_MODE` | Anthropic pokha — `auto` (default) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Kulimbikira kwa kukumbukira: `high` (default) \| `medium` \| `low` \| `max` (Opus 4.6 pokha) |

### 5. Pangani familiar yanu

```bash
cp persona-template/en.md ME.md
# Sinthani ME.md — perekani dzina ndi makhalidwe
```

### 6. Dziwitsani

```bash
./run.sh             # Textual TUI (yoyenera)
./run.sh --no-tui    # Plain REPL
```

---

## Kusankha LLM

> **Zoyenera: Kimi K2.5** — magwiridwe abwino a agent omwe adapita bwino mpaka pano. Imadziwa maonekedwe, ndiyeno ikufunsa mafunso otsatirapo, ndipo imachita nokha monga momwe ma modeli ena safunira. Mtengo ukugwirizana ndi Claude Haiku.

| Platform | `PLATFORM=` | Model ya default | Kumene mungapeze mlandu |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (the command) | — |

**Kimi K2.5 `.env` chitsanzo:**
```env
PLATFORM=kimi
API_KEY=sk-...   # kuchokera ku platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` chitsanzo:**
```env
PLATFORM=glm
API_KEY=...   # kuchokera ku api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` chitsanzo:**
```env
PLATFORM=gemini
API_KEY=AIza...   # kuchokera ku aistudio.google.com
MODEL=gemini-2.5-flash  # kapena gemini-2.5-pro kuti ikhale ndi mphamvu zambiri
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` chitsanzo:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # kuchokera ku openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # zogwirizana: onani model
AGENT_NAME=Yukine
```

> **Nkhani:** Kuti mutseke malo a local/NVIDIA models, ingosankha kuti `BASE_URL` ikhale pa endpoint yanga ya m'kati monga `http://localhost:11434/v1`. Mugwiritse ntchito ogulitsa a mu mtambo m'malo.

**CLI tool `.env` chitsanzo:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — palibe {}, prompt imapita kudzera pa stdin
```

---

## MCP Servers

familiar-ai ikhoza kulumikizana ndi [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server iliyonse. Izi zimakupatsani mwayi wotheka kuika kukumbukira kwina, kupeza ma filesystem, kufufuza pa web, kapena zida zina.

Sinthani ma server mu `~/.familiar-ai.json` (mfundo yomweyo monga Claude Code):

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

Mitundu iwiri ya ma transport imathandizidwa:
- **`stdio`**: yambani subprocess ya m'kati (`command` + `args`)
- **`sse`**: njira ku HTTP+SSE server (`url`)

Sinthani malo a config file ndi `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai ikhoza kugwira ntchito ndi hardware iliyonse yomwe muli nayo — kapena palibe ngakhale.

| Part | Zomwe zimachita | Chitsanzo | Zofunika? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Maso + mphuno | Tapo C220 (~$30) | **Zoyenera** |
| USB webcam | Maso (osavuta) | Kamera iliyonse ya UVC | **Zoyenera** |
| Robot vacuum | Mapazi | Model iliyonse yomwe ili ndi Tuya | Ayi |
| PC / Raspberry Pi | Brain | Chilichonse chomwe chimalimbikitsa Python | **Inde** |

> **Kamera ikugwiritsidwa ntchito kwambiri.** Pwithout kamera imatha kulankhula — koma ikhoza kuona dziko, zomwe ndizomwe zingathetse.

### Minimal setup (palibe hardware)

Mukufuna kuiyesa? Muyenera kungobwezeretsa API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Dziwitseni `./run.sh` ndiponso yanu. Ikani hardware monga mukupitilira.

### Wi-Fi PTZ camera (Tapo C220)

1. Mu Tapo app: **Settings → Advanced → Camera Account** — pangani akaunti ya lokal (osati TP-Link account)
2. Pitani ku IP ya kamera mu mndandanda wa zida zanu
3. Sinthani mu `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Voice (ElevenLabs)

1. Pezani API key ku [elevenlabs.io](https://elevenlabs.io/)
2. Sinthani mu `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # zosankha, zimagwiritsa ntchito mawu a default
   ```

Kukhala malo awiri ochezera, omwe angagwiritsidwe ntchito ndi `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC speaker (default)
TTS_OUTPUT=remote   # kamera speaker yokha
TTS_OUTPUT=both     # kamera speaker + PC speaker nthawi imodzi
```

#### A) Kamera speaker (kupita kwa go2rtc)

Set `TTS_OUTPUT=remote` (kapena `both`). Ikufuna [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Dziwani the binary kuchokera ku [releases page](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Ikani ndi kutchedwa:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x akufunika

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Pangani `go2rtc.yaml` mu mndandanda womwewo:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gwiritsani ntchito ma adiresi a akaunti ya kamera (osati akaunti ya TP-Link cloud).

4. familiar-ai imayambitsa go2rtc mwachangu pa nthawi ya kukhazikika. Ngati kamera yanu ikugwira ntchito ya mawu awiri (backchannel), mawu amatuluka kuchokera ku kamera speaker.

#### B) Local PC speaker

Chosankha (TTS_OUTPUT=local). Imayesa wosewera m'njira: **paplay** → **mpv** → **ffplay**. Izi zimagwira ntchito ngati chotsatira pamene `TTS_OUTPUT=remote` ndi go2rtc sikupatikana.

| OS | Ikani |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (kapena `paplay` kudzera pa `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — set `PULSE_SERVER=unix:/mnt/wslg/PulseServer` mu `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — download ndi ikani mu PATH, **kapena** `winget install ffmpeg` |

> Ngati sitikuphatikizidwa, mawu amakhala, koma sadzalembedwa.

### Voice input (Realtime STT)

Set `REALTIME_STT=true` mu `.env` kuti ikhale ikugwira mawu osavomerezeka:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # mlandu womwe mumagwiritsa ntchito monga TTS
```

familiar-ai imalimbikira kudesala mawu kuchokera ku ElevenLabs Scribe v2 ndikuikapo zipangizo zikalembedwa mukamacheza. Palibe dinani pomwe mukulankhula. Itha kupanga zokondedwa zam'mbuyo (Ctrl+T).

---

## TUI

familiar-ai ili ndi terminal UI yolembedwa ndi [Textual](https://textual.textualize.io/):

- Zowonjezera zokumbukira zomwe zimachitika ndi mawu osankhidwa
- Tab-completion ya `/quit`, `/clear`
- Kukana ma agent musanayambe kutchula
- **Log ya kasamalidwe** ikutsa mawonekedwe ku `~/.cache/familiar-ai/chat.log`

Kuti muwone log mu terminal ina (zofunikira pa copy-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Makhalidwe a familiar yanu amakhala mu `ME.md`. Fayilo iyi ikugwiritsidwa ntchito — ndi yanu yokha.

Onani [`persona-template/en.md`](./persona-template/en.md) kuti mupeze chitsanzo, kapena [`persona-template/ja.md`](./persona-template/ja.md) kuti mupeze chikhalidwe cha Chijapani.

---

## FAQ

**Q: Ndikhoza kugwiritsa ntchito popanda GPU?**
Inde. Mphamvu ya embedding model (multilingual-e5-small) ikhoza kugwiritsidwa ntchito bwino pa CPU. GPU imakhala yothandiza kwambiri koma sikofunika.

**Q: Ndikhoza kugwiritsa ntchito kamera yina kupatulira Tapo?**
Kamera iliyonse yomwe imakhala ndi ONVIF + RTSP ikhoza kugwira ntchito. Tapo C220 ndicho chomwe takupitirira.

**Q: Kodi data yanga imatumizidwa kulikonse?**
Zithunzi ndi zolembedwa zimatumizidwa ku mlandu wanu wa LLM yosankhidwa kuti ifufuzidwe. Zokumbukira zimakulungidwa m'thumba la `~/.familiar_ai/`.

**Q: N'chifukwa chiani agent yozilankhulira `（...）` m'malo mochita?**
Onetsetsani kuti `ELEVENLABS_API_KEY` yaperekedwa. Ngati sichikuyendetsedwa, mawu amathera ndipo agent imabwerera ku text.

## Technical background

Mukufuna kudziwa momwe zimakhalira? Onani [docs/technical.md](./docs/technical.md) kuti muwone kafukufuku ndi kuganizira za zomwe zili kuseri kwa familiar-ai — ReAct, SayCan, Reflexion, Voyager, dongosolo la chikhumbo, ndi zambiri.

---

## Contributing

familiar-ai ndi chiyesero chopenya. Ngati chilichonse cha ichi chimakukhudzani — molimbikitsa kapena mwachidziwitso — zolimbikitsa zikuwelcome kwambiri.

**Madera abwino oyamba:**

| Madera | Zomwe zikufunika |
|------|---------------|
| Hardware yatsopano | Thandizo la kamera zingapo (RTSP, IP Webcam), ma microphone, actuators |
| Zida zatsopano | Web search, kukwaniritsa kwathu, nthawi, chilichonse kudzera pa MCP |
| Backends zatsopano | LLM iliyonse kapena model yochitikira yomwe ikugwirizana ndi `stream_turn` interface |
| Templates za Persona | ME.md ma templates a mitundu yatsopano ndi makhalidwe |
| Research | Zitsulo zaposachedwapa chimwemwe, kukumbukira, mawu osalankhulira |
| Documentation | Tutorials, walkthroughs, ma translations |

Onani [CONTRIBUTING.md](./CONTRIBUTING.md) kuti mupeze akapolo, kalembedwe kachitidwe, ndi mawu a PR.

Ngati mukuganiza kuti mukuchita bwino bwanji, [yambitsani phunziro](https://github.com/lifemate-ai/familiar-ai/issues) — ndikuwona posachedwa.

---

## License

[MIT](./LICENSE)
