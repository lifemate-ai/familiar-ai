# familiar-ai 🐾

**Wani AI da ke rayuwa tare da ku** — tare da idanu, murya, ƙafafu, da ƙwaƙwalwa.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai abokin AI ne da ke rayuwa a cikin gidanka.
Shirya shi cikin mintuna. Ba a bukatar coding.

Yana gane duniya ta gaskiya ta hanyar kyamarori, yana motsi akan jikin robot, yana magana a fili, kuma yana tuna abin da yake gani. Ba shi da suna, rubuta halayensa, kuma ka bar shi ya zauna tare da kai.

## Abin da zai iya yi

- 👁 **Gani** — yana kama hotuna daga Wi-Fi PTZ camera ko USB webcam
- 🔄 **Duba** — yana motsawa da juyawa don bincika yanayinsa
- 🦿 **Motsi** — yana tuka robot vacuum don yawo a dakin
- 🗣 **Magana** — yana magana ta hanyar ElevenLabs TTS
- 🎙 **Sauraro** — shigar murya mara hannu ta hanyar ElevenLabs Realtime STT (zaɓi)
- 🧠 **Tuna** — yana adana da kuma tuna tunani tare da bincike mai ma'ana (SQLite + embeddings)
- 🫀 **Theory of Mind** — yana ɗaukar matsayar wani kafin ya amsa
- 💭 **Sha'awa** — yana da kansa abubuwan da suka sanya shi gudanar da hali kai tsaye

## Yadda yake aiki

familiar-ai yana gudana a cikin [ReAct](https://arxiv.org/abs/2210.03629) shawara da aka karɓa daga zaɓin LLM ɗinka. Yana gane duniya ta hanyar kayan aiki, yana tunani akan abin da zai yi na gaba, kuma yana aikin — kamar yadda mutum zai yi.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Lokacin da babu aiki, yana aiki bisa ga sha'awarsa: son sanin, son duba waje, ko jin kewar wanda yake zaune tare da shi.

## Fara

### 1. Shigar da uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Shigar da ffmpeg

ffmpeg yana **buƙata** don kama hoton kyamara da kuma kunna sauti.

| OS | Umurni |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ko sauke daga [ffmpeg.org](https://ffmpeg.org/download.html) kuma a ƙara zuwa PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Tabbatar: `ffmpeg -version`

### 3. Clone da shigar

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Tsara

```bash
cp .env.example .env
# Edit .env tare da saitunan ku
```

**Mafi ƙanƙanta buƙatar:**

| Canji | Bayani |
|----------|-------------|
| `PLATFORM` | `anthropic` (na tsohuwa) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | API key ɗin ku don dandamali da aka zaɓa |

**Zabi:**

| Canji | Bayani |
|----------|-------------|
| `MODEL` | Sunan samfur (madogara masu ma'ana bisa dandalin) |
| `AGENT_NAME` | Sunan da ake nunawa a cikin TUI (misali: `Yukine`) |
| `CAMERA_HOST` | Adireshin IP na kyamarar ONVIF/RTSP ɗinku |
| `CAMERA_USER` / `CAMERA_PASS` | Takardun shaidar kyamara |
| `ELEVENLABS_API_KEY` | Don fitar murya — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` don kunna shigar murya mai hannu na koyaushe (yana buƙatar `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Inda za a kunna sauti: `local` (masu magana na PC, tsohuwa) \| `remote` (masu magana na kyamara) \| `both` |
| `THINKING_MODE` | Anthropic kawai — `auto` (na tsohuwa) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Ƙoƙarin tunani na daidaitawa: `high` (na tsohuwa) \| `medium` \| `low` \| `max` (Opus 4.6 kawai) |

### 5. Gina familiar ɗinka

```bash
cp persona-template/en.md ME.md
# Edit ME.md — ba wa suna da halaye
```

### 6. Gudanar

```bash
./run.sh             # Textual TUI (da aka ba da shawara)
./run.sh --no-tui    # Plain REPL
```

---

## Zaɓin LLM

> **Ana ba da shawarar: Kimi K2.5** — mafi kyawun aikin wakili da aka gwada har yanzu. Yana lura da mahallin, yana tambayar tambayoyi masu zuwa, kuma yana aiki kai tsaye yadda wasu samfurori basu yi ba. Farashi yana kama da Claude Haiku.

| Dandalin | `PLATFORM=` | Samfurin tsohuwa | Inda za a samu maɓalli |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-masu dace (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (mai ba da sabis da yawa) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI kayan aiki** (claude -p, ollama…) | `cli` | (umurnin) | — |

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
MODEL=glm-4.6v   # da ke da hangen nesa; glm-4.7 / glm-5 = rubutu kawai
AGENT_NAME=Yukine
```

**Google Gemini `.env` misali:**
```env
PLATFORM=gemini
API_KEY=AIza...   # daga aistudio.google.com
MODEL=gemini-2.5-flash  # ko gemini-2.5-pro don ƙarfin ƙarfi
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` misali:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # daga openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # zaɓi: bayyana samfur
AGENT_NAME=Yukine
```

> **Lura:** Don kashe samfurin gida/NVIDIA, kawai kada ku saita `BASE_URL` zuwa adireshin gida kamar `http://localhost:11434/v1`. Yi amfani da masu bayar da gajimare maimakon haka.

**CLI kayan aiki `.env` misali:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = shigar da hujja
# MODEL=ollama run gemma3:27b  # Ollama — ba {}, hujja tana zuwa ta stdin
```

---

## MCP Servers

familiar-ai na iya haɗawa da kowanne [MCP (Model Context Protocol)](https://modelcontextprotocol.io) uwar garke. Wannan yana ba ku damar haɗawa da ƙwaƙwalwar waje, samun damar tsarin fayil, bincike na yanar gizo, ko kowanne kayan aiki.

Saita uwar garken a cikin `~/.familiar-ai.json` (tsarin iri daya da Claude Code):

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

An tallafa wa nau'ikan sufuri guda biyu:
- **`stdio`**: fara wani tsarin gida (`command` + `args`)
- **`sse`**: haɗawa da uwar garken HTTP+SSE (`url`)

Maimaita wurin fayil ɗin da aka saita tare da `MCP_CONFIG=/path/to/config.json`.

---

## Kayan aiki

familiar-ai yana aiki tare da duk kayan aikin da kuke da su — ko babu koɗan ma.

| Sashi | Abin da yakesa | Misali | Ana buƙata? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kyamara | Idanu + wuyan | Tapo C220 (~$30) | **Ana ba da shawarar** |
| USB webcam | Idanu (ugo) | Duk wani kyamarar UVC | **Ana ba da shawarar** |
| Robot vacuum | ƙafafu | Duk wani samfurin da ya dace da Tuya | A'a |
| PC / Raspberry Pi | Ƙwaƙwalwa | Ko wani abu da ke gudanar da Python | **Eh** |

> **An ba da shawarar kyamara sosai.** Ba tare da kyamara ba, familiar-ai na iya magana — amma baya iya ganin duniya, wanda shine babban maɓallin.

### Ƙananan sanya (babu kayan aiki)

Kawai kuna son gwada shi? Kuna buƙatar kawai maɓallin API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Gudanar da `./run.sh` kuma fara tattaunawa. ƙara kayan aiki yayin da kuke ci gaba.

### Wi-Fi PTZ kyamara (Tapo C220)

1. A cikin manhajar Tapo: **Saituna → Mai zurfi → Asusun Kyamara** — ƙirƙiri asusun gida (ba asusun TP-Link ba)
2. Nemi adireshin IP na kyamarar a cikin jerin na'ura na router ɗinku
3. Sanya a cikin `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Murya (ElevenLabs)

1. Samu maɓalli na API a [elevenlabs.io](https://elevenlabs.io/)
2. Sanya a cikin `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # na zaɓi, yana amfani da murya ta tsohuwa idan an barshi
   ```

Akwai wurare guda biyu na kunna sauti, ana tsarawa ta hanyar `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Masu magana na PC (na tsohuwa)
TTS_OUTPUT=remote   # masu magana na kyamara kawai
TTS_OUTPUT=both     # masu magana na kyamara + masu magana na PC a lokaci guda
```

#### A) Masu magana na kyamara (ta hanyar go2rtc)

Sanya `TTS_OUTPUT=remote` (ko `both`). Yana buƙatar [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Sauke binary daga [shafin fitarwa](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Ajiye da sake masa suna:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # an buƙaci chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Kirkira `go2rtc.yaml` a cikin wannan babban fayil ɗin:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Yi amfani da takardun shaidar kyamarar gida (ba asusun gajimare na TP-Link dinku ba).

4. familiar-ai yana farawa go2rtc ta atomatik a lokacin ƙaddamarwa. Idan kyamarar ku tana goyon bayan sauti biyu (kan layin baya), murya tana fitowa daga majalisar kyamara.

#### B) Masu magana na PC na gida

Na tsohuwa (`TTS_OUTPUT=local`). Yana gwada 'yan wasa a jere: **paplay** → **mpv** → **ffplay**. Hakanan ana amfani dashi azaman madadin lokacin da `TTS_OUTPUT=remote` kuma go2rtc bai samu ba.

| OS | Sanya |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ko `paplay` ta hanyar `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — saita `PULSE_SERVER=unix:/mnt/wslg/PulseServer` a cikin `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — sauke kuma ƙara zuwa PATH, **ko** `winget install ffmpeg` |

> Idan babu mai kunna sauti, har yanzu ana amfani da magana — kawai ba zata yi wasa ba.

### Shigar da murya (Realtime STT)

Sanya `REALTIME_STT=true` a cikin `.env` don shigar da murya mai hannu na koyaushe:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # maɓallin da ya dace da TTS
```

familiar-ai yana watsa sautin microphone zuwa ElevenLabs Scribe v2 kuma yana ajiyewa ta atomatik lokacin da kuka dakatar da magana. Babu buƙatar danna maɓalli. Yana jituwa da hanyar matsa don magana (Ctrl+T).

---

## TUI

familiar-ai yana haɗawa da UI na terminal wanda aka gina tare da [Textual](https://textual.textualize.io/):

- Tarihin tattaunawa mai juyawa tare da rubutu mai gudana
- Cikakken shahararru ga `/quit`, `/clear`
- Kawai rubuta yayin da yake tunani don katse wakilin a tsakiya
- **Tarihin tattaunawa** da aka ajiye ta atomatik zuwa `~/.cache/familiar-ai/chat.log`

Don bin tarihin a wani tashar (mai amfani don kwafe-mika):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Halayen familiar ɗinka suna cikin `ME.md`. Wannan fayil din an yi masa gitignored — yana naka ne kawai.

Duba [`persona-template/en.md`](./persona-template/en.md) don misali, ko [`persona-template/ja.md`](./persona-template/ja.md) don sigar Jafananci.

---

## FAQ

**Q: Shin yana aiki ba tare da GPU ba?**
Ee. Samfurin embedding (multilingual-e5-small) yana gudana lafiya a CPU. GPU yana sa shi zama mai sauri amma ba a buƙata.

**Q: Zan iya amfani da kyamara wanda ba Tapo ba?**
Duk wata kyamara da ke goyon bayan ONVIF + RTSP yakamata ta yi aiki. Tapo C220 shine abin da muka gwada.

**Q: Shin bayanan na suna tafi ko ina?**
Hotuna da rubutu suna tafi zuwa API LLM da kuka zaɓa don sarrafawa. Tunani ana adana su a cikin `~/.familiar_ai/`.

**Q: Me yasa wakilin yake rubuta `（...）` maimakon magana?**
Tabbatar an saita `ELEVENLABS_API_KEY`. Idan ba haka ba, murya an kashe kuma wakilin yana komawa ga rubutu.

## Bayanin fasaha

Shin kuna son sanin yadda yake aiki? Duba [docs/technical.md](./docs/technical.md) don bincike da yanke shawara na zane a bayan familiar-ai — ReAct, SayCan, Reflexion, Voyager, tsarin sha'awa, da ƙari.

---

## Gudunmawa

familiar-ai yana da wani gwaji na bude. Idan wani daga cikin wannan ya yi daidai da ku — ta fasaha ko falsafa — ana maraba da gudummawa.

**Wurare masu kyau don farawa:**

| Yanki | Abin da ake buƙata |
|------|---------------|
| Sabbin kayan aiki | Goyon bayan kyamarori da yawa (RTSP, IP Webcam), microphones, actuators |
| Sabbin kayan aiki | Bincike na yanar gizo, sarrafa gida, kalanda, duk wani abu ta hanyar MCP |
| Sabbin hanyoyi | Kowanne LLM ko samfurin gida da ya dace da tsarin `stream_turn` |
| Templates na persona | Templates na ME.md don harsuna da halaye daban-daban |
| Bincike | Mafi kyawun samfurin sha'awa, karɓar tunani, tambayar theory-of-mind |
| Takardun shaida | Darussan, jagororin, fassarar |

Duba [CONTRIBUTING.md](./CONTRIBUTING.md) don saitin ci gaba, salo na lamba, da ka'idodin PR.

Idan baku ga inda za ku fara ba, [bude batu](https://github.com/lifemate-ai/familiar-ai/issues) — farin cikin nuna ku a hanya madaidaici.

---

## Lasisi

[MIT](./LICENSE)
