# familiar-ai 🐾

**AI imene imakhala ndi inu** — yomwe ili ndi maso, mawu, magazi, komanso ndangomera.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Zikulimbikitsidwa mu 74 chitchulidwe](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai ndi chida cha AI chomwe chili m'nyumba mwanu.
Ikani m'masitole. Sitigula mau.

Imawona dziko lenileni kudzera pa makamera, imatembenukira pa thupi la robot, imalankhula, ndipo imakumbukira zomwe imawona. Mupatseni dzina, lembani machitidwe ake, ndipo muzimupirira.

## Zomwe angachite

- 👁 **Onani** — imapeza zithunzi kuchokera ku Wi-Fi PTZ kamera kapena USB webcam
- 🔄 **Kuwona momwemo** — imapanga komanso kutembenuka kwa kamera kuti iwone zinthu zomwe zikuchitika
- 🦿 **Kuyenda** — imatembenukira ndi vacuum robot kuti iphunzire m'nyumba
- 🗣 **Lankhulani** — imalankhula kudzera pa ElevenLabs TTS
- 🎙 **Mvetsera** — mawu osapatsika kudzera pa ElevenLabs Realtime STT (opt-in)
- 🧠 **Kumbukirani** — imakhala ndi kukumbukira komanso kukumbukira ndi kufufuza kwa semantics (SQLite + embeddings)
- 🫀 **Malangizo a Siriku** — imatengera maganizo a munthu ena musanafike
- 💭 **Kufuna** — imakhala ndi zolinga zake zokha zomwe zimapangitsa kuchita zakutchula

## Momwe imagwira

familiar-ai imayambitsa [ReAct](https://arxiv.org/abs/2210.03629) loop yomwe imapangidwa ndi LLM yomwe mukusankha. Imawona dziko kudzera mu zida, imaganiza momwe angachitire pambuyo pake, ndipo imachita - monga momwe munthu angachitire.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Ikakhala yokhalamo, imachita malinga ndi zofuna zake: kufuna, kufuna kuwona kunja, kukumbukira munthu yomwe ili naye.

## Kuyang'ana

### 1. Ikani uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Kapena: `winget install astral-sh.uv`

### 2. Ikani ffmpeg

ffmpeg ndi **wing'amba** yofunika kuti mugwiritse ntchito kufufuza zithunzi zamakamera ndi kuyimba mawu.

| OS | Malangizo |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — kapena download kuchokera ku [ffmpeg.org](https://ffmpeg.org/download.html) ndikuwonjezera ku PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Onetsetsani: `ffmpeg -version`

### 3. Chitani ndiku ikani

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Kukhazikitsa

```bash
cp .env.example .env
# Sinthani .env ndi masetup anu
```

**Zofunika kwambiri:**

| Variable | Kufotokozera |
|----------|-------------|
| `PLATFORM` | `anthropic` (mankhwala) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | API key yanu yopita ku platform yomwe mwachita |

**Zosankha:**

| Variable | Kufotokozera |
|----------|-------------|
| `MODEL` | Dzina la model (zokwana pa phunziro) |
| `AGENT_NAME` | Dzina looneka mu TUI (mwachitsanzo `Yukine`) |
| `CAMERA_HOST` | IP adilesi ya kamera yanu ya ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Makalata a kamera |
| `ELEVENLABS_API_KEY` | Pachitani mawu — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` kuti muike nthawi zonse kuti mukhale ndi mawu (ikufunika `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Komwe ku playwa mawu: `local` (PC speaker, mankhwala) \| `remote` (kamera speaker) \| `both` |
| `THINKING_MODE` | Anthropic chabe — `auto` (mankhwala) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Luso losinthasintha: `high` (mankhwala) \| `medium` \| `low` \| `max` (Opus 4.6 chabe) |

### 5. Pangani zanu

```bash
cp persona-template/en.md ME.md
# Sinthani ME.md — mutapatsa dzina ndi machitidwe
```

### 6. Yendani

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textual TUI (zolimbikitsidwa)
./run.sh --no-tui    # Plain REPL
```

**Windows:**
```bat
run.bat              # Textual TUI (zolimbikitsidwa)
run.bat --no-tui     # Plain REPL
```

---

## Kusayiza LLM

> **Zokhulupirira: Kimi K2.5** — kuchita bwino kwambiri ngati chida chomwe takatengera. Imagwira ntchito m'njira zingapo, ikufunsa masomphenya omwe mukuwona, ndikuchita mwachilendo. Zimapangidwa molingana ndi Claude Haiku.

| Platform | `PLATFORM=` | Model yamakonda | Kodi mwapeza dikasiyoni |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-otsogoloko (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (malangizo) | — |

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
MODEL=glm-4.6v   # njira yanu; glm-4.7 / glm-5 = malemba okha
AGENT_NAME=Yukine
```

**Google Gemini `.env` chitsanzo:**
```env
PLATFORM=gemini
API_KEY=AIza...   # kuchokera ku aistudio.google.com
MODEL=gemini-2.5-flash  # kapena gemini-2.5-pro chifukwa chosavuta kwambiri
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` chitsanzo:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # kuchokera ku openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # zosankha: notched model
AGENT_NAME=Yukine
```

> **Chidule:** Kuti musawonongedwe m'njira zapanjali / NVIDIA, ingowonjezani `BASE_URL` kuti ikhale pamalo a lokal monga `http://localhost:11434/v1`. Gwiritsani ntchito opanga mawu.

**CLI tool `.env` chitsanzo:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = dikasiyoni ya kasamalidwe
# MODEL=ollama run gemma3:27b  # Ollama — palibe {}, dikasiyoni imagwirizanitsidwa ndi stdin
```

---

## MCP Servers

familiar-ai ingagwire ntchito ndi **[MCP (Model Context Protocol)](https://modelcontextprotocol.io)** server. Izi zimakuthandizani kuwonjezera njira ya chifuniro, kuchita m’magalimoto, kufufuza pa web, kapena chida china chilichonse.

Kukhazikitsa ma server mu `~/.familiar-ai.json` (chofanana ndi Claude Code):

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

Amakhala ndi mitundu iwiri ya kutumiza:
- **`stdio`**: kutsegula pulogalamu ya lokal (`command` + `args`)
- **`sse`**: kulumikizana ndi HTTP+SSE server (`url`)

Sinthani malo a fayilo ya config ndi `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai ikugwira ntchito ndi hardware yanu iliyonse — kapena ilibe chilichonse.

| Gawo | Zomwe amachita | Mwachitsanzo | Zofunika? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Maso + khosi | Tapo C220 (~$30) | **Zokhulupirira** |
| USB webcam | Maso (omangidwa) | Kamera iliyonse ya UVC | **Zokhulupirira** |
| Robot vacuum | Magazi | Chochita chilichonse cha Tuya | Ayi |
| PC / Raspberry Pi | Maganizo | Chilichonse chomwe chimagwiritsidwa ntchito ndi Python | **Chofunika** |

> **Kamera iyenera kuthandizidwa.** Popanda imwe, familiar-ai ingalankhule — koma siyikuwona dziko, zomwe zili kundochita mopanga.

### Kukhazikitsa koyamba (popanda hardware)

Mukufuna kuyesa? Mukangofuna API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Yendani `./run.sh` (macOS/Linux/WSL2) kapena `run.bat` (Windows) ndikuyamba kuyankhulana. Onjezerani hardware mukamayenda.

### Wi-Fi PTZ camera (Tapo C220)

1. Mu app ya Tapo: **Settings → Advanced → Camera Account** — pangani akaunti yokhazikika (sitiyi TP-Link)
2. Fufuzani IP ya kamera mu mndandanda wa zida zanu
3. Onjezani mu `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Mawu (ElevenLabs)

1. Pankhani API key pa [elevenlabs.io](https://elevenlabs.io/)
2. Onjezani mu `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # yosankha, imagwiritsa ntchito mawu omaliza ngati ngakhale sinachitike
   ```

Pali malo awiri oimba, omwe amalamulira ndi `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # PC speaker (mankhwala)
TTS_OUTPUT=remote   # kamera weksiper
TTS_OUTPUT=both     # kamera speaker + PC speaker ndikuwonongera
```

#### A) Kamera speaker (ndikukhala go2rtc)

Onjezani `TTS_OUTPUT=remote` (kapena `both`). Ikufunika [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Download binary kuchokera pa [zotsatira](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Ikani komanso badiritsani:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x ikufunika

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Pangani `go2rtc.yaml` mu directory yomweyo:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Gwiritsani ntchito mawala a khama osiyanasiyana (osati akaunti yanu ya TP-Link).

4. familiar-ai imayambitsa go2rtc otumikira pakugodzira. Ngati kamera yanu imathandizidwa ndi mawu a aliyense (backchannel), mawu akhalabe kuchokera mu kamera speaker.

#### B) Local PC speaker

Mankhwala (`TTS_OUTPUT=local`). Imayesera osewera molingana: **paplay** → **mpv** → **ffplay**. Ikagwidwa ngati fallback pamene `TTS_OUTPUT=remote` ndipo go2rtc ikukhalabe.

| OS | Ikani |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (kapena `paplay` kudzera mu `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — onjezani `PULSE_SERVER=unix:/mnt/wslg/PulseServer` mu `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — download ndikuwonjezera ku PATH, **kapena** `winget install ffmpeg` |

> Ngati palibe wosewera wa mawu, mawu akhala akuchitika — sama amwano.

### Mawu Olankhulira (Realtime STT)

Onjezani `REALTIME_STT=true` mu `.env` kuti mukhale nthawi zonse, ambiri:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # ndikofanana ndi TTS
```

familiar-ai imatenga mawu a maekala kudzera pa ElevenLabs Scribe v2 ndipo imatchula zolembedwa pamene mutakhazikitsa. Palibe chotsatira chofunika. Ikhoza kuchitira pamene pamene push-to-talk mode (Ctrl+T).

---

## TUI

familiar-ai ikuphatikizapo banja la terminal limapangidwa ndi [Textual](https://textual.textualize.io/):

- Zolemba zolembedwenso pamasomphenya ndi mawu oyang'ana
- Tab-completion ya `/quit`, `/clear`
- Khalani mmbuyomo kuchita kumaliza zoyankhulana
- **Log ya zoyankhulana** imasungidwa pa `~/.cache/familiar-ai/chat.log`

Kuti muwone log mu terminal ina (zothandiza momwe mungachitire):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Machitidwe a familiar anu ali mu `ME.md`. Fayilo iyi ikulembedwanso mu git — ndi yanu yekha.

Onani [`persona-template/en.md`](./persona-template/en.md) kuti muone chitsanzo, kapena [`persona-template/ja.md`](./persona-template/ja.md) kuti muone chikhalidwe cha Japanese.

---

## FAQ

**Q: Ngati sichita ntchito popanda GPU?**
Inde. Model ya embedding (multilingual-e5-small) imagwira bwino pa CPU. GPU imathandizira mwachangu koma si chofunika.

**Q: Ngati ndikufuna kuika kamera ina kuposa Tapo?**
Kamera iliyonse yomwe imathandizira ONVIF + RTSP iyenera kuthandizidwa. Tapo C220 ndiye yomwe takuchita.

**Q: Kodi data yanga ikupita kuti?**
Zithunzi komanso mawu amatumizidwa ku LLM API yanu yopezeka. Zomwe zili mukumbukira zimakhala lokha mu `~/.familiar_ai/`.

**Q: Nchedzerenge malankhulidwe ngati `（...）` m'malo molankhula?**
Onetsetani kuti `ELEVENLABS_API_KEY` ikukhazikidwa. Popanda izo, mawu siyikhale ndipo chida chili mu mkwatibochi lipoti.

## Technical background

Mukuzonda momwe imagwirira ntchito? Onani [docs/technical.md](./docs/technical.md) pomwe muonera kafuko kake ndi kuchita kapena ndondomeko zaposachedwa za familiar-ai — ReAct, SayCan, Reflexion, Voyager, njira yofuna, ndi zina zambiri.

---

## Kuthandizira

familiar-ai ndi kulimbikitsa kumene. Ngati chilichonse chikuchepetsera — mwachipanga kapena filozofiya — chithandizo chimakhala chovomerezeka.

**Malo abwino oyambirira:**

| Malo | Zomwe zikufunika |
|------|---------------|
| Hardware yatsopano | Kuthandiza ma camera angapo (RTSP, IP Webcam), ma microfone, ma actuator |
| Zida zatsopano | Kufufuza pa web, kuwonjezera m'nyumba, kalendala, chilichonse kudzera mu MCP |
| Backends yatsopano | LLM iliyonse kapena model yokhala pansi yomwe ikugwirizana ndi `stream_turn` |
| Templates ya Persona | Ma template a ME.md a mitundu yosiyanasiyana ndi machitidwe |
| Kafukufuku | Machitidwe abwino m'njira, kukumbukira, njira ya mamaso |
| Zotsatizana | Zokwaniritsa, zotsatizana, kutanthauzira |

Onani [CONTRIBUTING.md](./CONTRIBUTING.md) kuti muwonetsetse kugwira ntchito, masitepe a kode, ndi malangizo a PR.

Ngati simukudziwa momwe mungayambe, [tsegulani mlandu](https://github.com/lifemate-ai/familiar-ai/issues) — ndifuna kutsegula mwamphamvu m'njira yabwino.

---

## Mikalata

[MIT](./LICENSE)
