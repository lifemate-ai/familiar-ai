# familiar-ai 🐾

**Wannan AI ne da ke zaune tare da kai** — yana da ido, murya, kafafu, da tunani.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Ana samunsa a harshen 74](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai abokin tarayya ne na AI wanda ke zaune a gidanka.
Sanya shi cikin mintuna. Ba a buƙatar kera.

Yana gane duniya ta gaske ta hanyar kyamara, yana motsawa akan jikin robot, yana magana da ƙarfi, kuma yana tunawa da abin da ya gani. Ba shi da suna, rubuta halayensa, kuma bar shi ya zauna tare da kai.

## Me zai iya yi

- 👁 **Gani** — yana ɗaukar hotuna daga kyamara ta Wi-Fi PTZ ko USB webcam
- 🔄 **Duba** — yana juyawa da tsayawa da kyamara don bincika kewayon sa
- 🦿 **Motsi** — yana tuka na'urar shara ta robot don yawo a cikin dakin
- 🗣 **Magana** — yana magana ta ElevenLabs TTS
- 🎙 **Sauraro** — shigar murya mara hannu ta ElevenLabs Realtime STT (zaɓi)
- 🧠 **Tuna** — yana adana da kuma tuna tunane-tunane tare da binciken ma'anar (SQLite + embeddings)
- 🫀 **Tsarin Hankali** — yana ɗaukar hangen nesa na wanda ke tare da shi kafin ya amsa
- 💭 **Sha'awa** — yana da hawa na ciki na kansa wanda ke haifar da halayen kansa

## Yadda yake aiki

familiar-ai na gudanar da [ReAct](https://arxiv.org/abs/2210.03629) zagaye wanda aka ƙarfafa da zaɓin ku na LLM. Yana ganin duniya ta hanyoyi, yana tunani akan abin da za a yi na gaba, kuma yana aikata — kamar yadda mutum zai yi.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Lokacin da ba ya yin komai, yana aikata bisa ga sha'awarsa: son sani, jin dadin kallon waje, rashin wanda yake tare da shi.

## Fara aiki

### 1. Shigar da uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Ko: `winget install astral-sh.uv`

### 2. Shigar da ffmpeg

ffmpeg yana **da muhimmanci** don ɗaukar hotunan kyamara da kunna sauti.

| OS | Umurni |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ko sauke daga [ffmpeg.org](https://ffmpeg.org/download.html) kuma ƙara zuwa PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Tabbatar: `ffmpeg -version`

### 3. Clone da shigar

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Daidaita

```bash
cp .env.example .env
# Gyara .env tare da saitunan ku
```

**Mafi ƙarancin ake buƙata:**

| Canji | Bayani |
|----------|-------------|
| `PLATFORM` | `anthropic` (na tsohuwa) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Mabudin API naka don dandamali da aka zaɓa |

**Zaɓi:**

| Canji | Bayani |
|----------|-------------|
| `MODEL` | Sunan samfur (masu ma'ana na tsohuwa bisa dandamali) |
| `AGENT_NAME` | Sunan da zai bayyana a cikin TUI (misali `Yukine`) |
| `CAMERA_HOST` | Adireshin IP na kyamarar ONVIF/RTSP dinka |
| `CAMERA_USER` / `CAMERA_PASS` | Takaddun shaida na kyamara |
| `ELEVENLABS_API_KEY` | Don fitar da murya — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` don kunna shigar murya mara hannu koyaushe (yana buƙatar `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Inda za a kunna sauti: `local` (muryar PC, na tsohuwa) \| `remote` (muryar kyamara) \| `both` |
| `THINKING_MODE` | Anthropic kawai — `auto` (na tsohuwa) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Tattaunawar tunani mai dacewa: `high` (na tsohuwa) \| `medium` \| `low` \| `max` (Opus 4.6 kawai) |

### 5. Kirkiri familiar dinka

```bash
cp persona-template/en.md ME.md
# Gyara ME.md — ba shi suna da halaye
```

### 6. Gudanar

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI mai rubutu (an ba da shawara)
./run.sh --no-tui    # REPL mai sauƙi
```

**Windows:**
```bat
run.bat              # TUI mai rubutu (an ba da shawara)
run.bat --no-tui     # REPL mai sauƙi
```

---

## Zabar LLM

> **An ba da shawara: Kimi K2.5** — mafi kyawun aikin agentic da aka gwada har zuwa yanzu. Yana lura da mahallin, yana tambayar tambayoyi masu zurfi, kuma yana aikata kansa a hanyoyi da sauran samfuran ba su yi ba. Farashin yana da kusan daidai da Claude Haiku.

| Dandamali | `PLATFORM=` | Samfur na tsohuwa | Inda za a sami mabudi |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (masu bayarwa da yawa) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (umurnin) | — |

**Kimi K2.5 `.env` misali:**
```env
PLATFORM=kimi
API_KEY=sk-...   # daga platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` misali:**
```env
PLATFORM=glm
API_KEY=...   # daga api.z.ai
MODEL=glm-4.6v   # duba; glm-4.7 / glm-5 = rubutacce kawai
AGENT_NAME=Yukine
```

**Google Gemini `.env` misali:**
```env
PLATFORM=gemini
API_KEY=AIza...   # daga aistudio.google.com
MODEL=gemini-2.5-flash  # ko gemini-2.5-pro don ƙarfin iko
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` misali:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # daga openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # zaɓi: ƙayyade samfur
AGENT_NAME=Yukine
```

> **Lura:** Don kashe samfurorin gida/NVIDIA, kawai kada a saita `BASE_URL` zuwa ƙarshen gida kamar `http://localhost:11434/v1`. Yi amfani da masu bayarwa na gajere maimakon haka.

**CLI tool `.env` misali:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = hujja
# MODEL=ollama run gemma3:27b  # Ollama — babu {}, hujja ta yi amfani da stdin
```

---

## MCP Servers

familiar-ai na iya haɗawa da kowanne [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Wannan yana ba ku damar haɗa ƙwaƙwalwar waje, damar fayil, bincike a yanar gizo, ko kowanne kayan aiki.

Daidaita servers a `~/.familiar-ai.json` (irin wannan tsarin da Claude Code):

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

An goyi bayan nau'ikan sufuri guda biyu:
- **`stdio`**: fara wani subprocess na gida (`command` + `args`)
- **`sse`**: haɗa da HTTP+SSE server (`url`)

Canza wurin fayil ɗin saiti tare da `MCP_CONFIG=/path/to/config.json`.

---

## Kayan aiki

familiar-ai yana aiki tare da kowanne kayan aiki da kuke da shi — ko ba komai ba.

| Sashi | Abin da yake yi | Misali | Ana buƙata? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kyamara | Ido + wuya | Tapo C220 (~$30, Eufy C220) | **An ba da shawara** |
| USB webcam | Ido (daskare) | Kowane kyamara UVC | **An ba da shawara** |
| Robot vacuum | Kafafu | Kowane samfurin da ya dace da Tuya | A'a |
| PC / Raspberry Pi | Kwamfuta | Kowane abu da ke gudanar da Python | **Iya** |

> **Ana ba da shawarar kyamara sosai.** Sai dai idan ba shi da ita, familiar-ai na iya magana — amma ba zai iya ganin duniya ba, wanda shine babban dalilin.

### Tsarin karami (ba ainihi)

Kawai kana so ka gwada? Kuna buƙatar kawai mabudin API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Gudanar da `./run.sh` (macOS/Linux/WSL2) ko `run.bat` (Windows) kuma fara tattaunawa. Ƙara kayan aiki yayin da kuke tafiya.

### Wi-Fi PTZ kyamara (Tapo C220)

1. A cikin aikace-aikacen Tapo: **Saituna → Ci gaba → Asusun Kyamera** — ƙirƙiri asusun gida (ba asusun TP-Link ba)
2. Nemo adireshin IP na kyamarar a cikin jerin na'urorin router dinka
3. Saita a cikin `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Wi-Fi Camera (Eufy C220)

[Eufy C220 on Amazon Japan](https://www.amazon.co.jp/dp/B0CQQQ5NZ1/)

> **Tested and confirmed working.** Follow these steps carefully — a few settings differ from Tapo.

1. In the Eufy Security app: go to the camera → **Settings → NAS(RTSP)** and enable it
2. Set **Authentication** to **Basic** (Digest authentication does NOT work)
3. Set a streaming username and password
4. Note the RTSP URL shown in the app (format: `rtsp://username:password@ip/live0`)
5. Set in `.env` — use the **full RTSP URL** as `CAMERA_HOST`:
   ```env
   CAMERA_HOST=rtsp://your-username:your-password@192.168.1.xxx/live0
   CAMERA_USERNAME=
   CAMERA_PASSWORD=
   ```
   Leave `CAMERA_USERNAME` and `CAMERA_PASSWORD` empty — credentials are already in the URL.

> **Note:** Eufy C220 allows only **one simultaneous RTSP connection**. Stop other apps connected to the camera before starting familiar-ai.


### Murya (ElevenLabs)

1. Samu mabudin API a [elevenlabs.io](https://elevenlabs.io/)
2. Saita a cikin `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # zaɓi, yana amfani da murya ta tsohuwa idan an barshi
   ```

Akwai wurare guda biyu na kunna sauti, wanda aka sarrafa ta `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Muryar PC (na tsohuwa)
TTS_OUTPUT=remote   # muryar kyamara kawai
TTS_OUTPUT=both     # muryar kyamara + muryar PC a lokaci guda
```

#### A) Muryar kyamara (ta go2rtc)

Saita `TTS_OUTPUT=remote` (ko `both`). Yana buƙatar [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Sauke binary daga [shafin fitarwa](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Ajiye kuma sake suna:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x yana buƙatar

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Kirkiri `go2rtc.yaml` a cikin wannan kundin:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Yi amfani da takaddun shaida na asusun kyamara na gida (ba asusun gajeren TP-Link dinka ba).

4. familiar-ai yana fara go2rtc ta atomatik a lokacin kaddamarwa. Idan kyamaran ka tana goyon bayan muryar bi-directional (backchannel), murya za ta fito daga muryar kyamara.

#### B) Muryar PC na gida

Na tsohuwa (`TTS_OUTPUT=local`). Yana gwada 'yan wasan kwaikwayo a cikin tsarin: **paplay** → **mpv** → **ffplay**. Hakanan ana amfani da shi a matsayin madadin lokacin da `TTS_OUTPUT=remote` da go2rtc ba su samu ba.

| OS | Shigar |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ko `paplay` ta hanyar `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — saita `PULSE_SERVER=unix:/mnt/wslg/PulseServer` a cikin `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — sauke kuma ƙara zuwa PATH, **ko** `winget install ffmpeg` |

> Idan babu wasan kwaikwayo na sauti, har yanzu ana haifar da magana — kawai ba za ta kunna ba.

### Shigar murya (Realtime STT)

Saita `REALTIME_STT=true` a cikin `.env` don shigar murya mara hannu koyaushe:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # mabuɗin iri ɗaya da TTS
```

familiar-ai yana yada saut din mikrofon ga ElevenLabs Scribe v2 kuma yana ajiyar rubuce-rubucen sa lokacin da ka dakatar da magana. Babu buƙatar danna maɓallin. Yana zama tare da yanayin danna-danna (Ctrl+T).

---

## TUI

familiar-ai yana ƙunshe da UI na terminal mai gina tare da [Textual](https://textual.textualize.io/):

- Tarihin tattaunawa mai jujjuyawa tare da rubutun kai tsaye
- Cikakken shafin don `/quit`, `/clear`
- Tsallake mai wakilta a tsaka-tsaki ta hanyar rubutu yayin da yake tunani
- **Tattalin bayanai** ana adana ta atomatik zuwa `~/.cache/familiar-ai/chat.log`

Don bin bayanan a wani terminal (mafi amfani don kwafin da liƙa):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Halayen abokin tarayya naka suna cikin `ME.md`. Wannan fayil din an yi masa gitignored — naka kadai ne.

Dubi [`persona-template/en.md`](./persona-template/en.md) don misali, ko [`persona-template/ja.md`](./persona-template/ja.md) don sigar Jafananci.

---

## Tambayoyi akai-akai

**Q: Yana aiki ba tare da GPU ba?**
Iya. Samfurin embedding (multilingual-e5-small) yana aiki da kyau akan CPU. GPU yana sa shi ya fi sauri amma ba a buƙatar shi.

**Q: Zan iya amfani da kyamara ta daban da Tapo?**
Kowane kyamara da ke goyon bayan Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: Shin bayanan nawa suna tafi wani waje?**
Hotuna da rubuce-rubuce suna tafi zuwa API na LLM da aka zaɓa don sarrafawa. Tarihin ana adanawa a gida a `~/.familiar_ai/`.

**Q: Me yasa wakilin ke rubuta `（...）` maimakon magana?**
Tabbatar cewa `ELEVENLABS_API_KEY` an saita. Idan ba haka ba, murya ta zama akashe, kuma wakilin yana koma rubutu.

## Bayanin fasaha

Kana sha'awar yadda yake aiki? Duba [docs/technical.md](./docs/technical.md) don binciken da shawarar zane a bayan familiar-ai — ReAct, SayCan, Reflexion, Voyager, tsarin sha'awa, da ƙari.

---

## Gudummawa

familiar-ai gwaji ne na bude. Idan wani daga cikin wannan yana jaje muku — fasaha ko falsafa — ana maraba da gudummawar ku sosai.

**Kyawawan wurare don farawa:**

| Yanki | Abin da ake buƙata |
|------|---------------|
| Sabon kayan aiki | Goyon bayan ƙarin kyamarori (RTSP, IP Webcam), mikrofon da masu motsa jiki |
| Sabbin kayan aiki | Bincike a yanar gizo, sarrafa gida, kalanda, komai ta hanyar MCP |
| Sabbin backend | Kowane LLM ko samfurin gida da ya dace da hanyar `stream_turn` |
| Templates na Persona | Templates ME.md don harsuna da halaye daban-daban |
| Bincike | Mafi kyawun samfuran sha'awa, dawo da ƙwaƙwalwa, tambayar tsarin hankali |
| Takardun shaida | Tutorials, hanyoyi, fassara |

Duba [CONTRIBUTING.md](./CONTRIBUTING.md) don saiti na ci gaba, salon lambar, da ƙa'idodin PR.

Idan ba ku da tabbacin inda za ku fara, [bude batu](https://github.com/lifemate-ai/familiar-ai/issues) — farin ciki don nuna muku hanya mai kyau.

---

## Lasisi

[MIT](./LICENSE)
