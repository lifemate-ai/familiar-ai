# familiar-ai 🐾

**AI a chónaíonn leat** — le súile, guth, cos, agus cuimhne.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Ar fáil i 74 teanga](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai is AI companion a chónaíonn i do theach.
Socraigh é laistigh de nóiméad. Ní bhfuil cód ag teastáil.

Tuigeann sé an domhan réalaíoch trí cheamaraí, gluaiseann sé timpeall ar chorp róbó, labhraíonn sé os ard, agus cuimhneamh ar a bhfeiceann sé. Tabhair ainm dó, scríobh a phearsantacht, agus lig dó cónaí leat.

## Cad is féidir leis a dhéanamh

- 👁 **Feic** — ghabhann íomhánaí ó cheamara PTZ Wi-Fi nó webcam USB
- 🔄 **Féach timpeall** — pivot agus tilts an cheamara chun a thimpealla
- 🦿 **Gluais** — gluaiseann robó vacaim chun an seomra a chíoradh
- 🗣 **Labhraigh** — labhraíonn trí ElevenLabs TTS
- 🎙 **Éisteacht** — ionchur guth gan lámh trí ElevenLabs Realtime STT (tacaíocht)
- 🧠 **Cuimhnigh** — stórann gníomhach agus cuireann cuimhní i gcuimhne le cuardach sémantach (SQLite + embeddings)
- 🫀 **Teoiric an Intinn** — tógann sé peirspictíocht an duine eile sular freagraíonn sé
- 💭 **Dóchas** — tá tiomantais inmheánacha aige a spreagann gníomhartha uathrialta

## Conas a oibríonn sé

familiar-ai reáchtálann gnáthchiorcal [ReAct](https://arxiv.org/abs/2210.03629) atá neartaithe ag do rogha LLM. Tuigeann sé an domhan trí uirlisí, smaoineamh ar an gníomhaíocht atá le déanamh, agus gníomhaíonn — díreach mar a dhéanfaí le duine.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Nuair a bhíonn sé neamhghníomhach, gníomhaíonn sé ar a dhóchas féin: fiosracht, ag iarraidh breathnú amach, ag mothú ar an duine atá ina chónaí leis.

## Conas le tosú

### 1. Suiteáil uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Nó: `winget install astral-sh.uv`

### 2. Suiteáil ffmpeg

ffmpeg is **gá** le haghaidh ghabháil íomhánna ceamara agus playback fuaime.

| OS | Orduithe |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — nó íoslódáil ó [ffmpeg.org](https://ffmpeg.org/download.html) agus cuir isteach sa PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Deimhnigh: `ffmpeg -version`

### 3. Clone agus suiteáil

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configir

```bash
cp .env.example .env
# Edit .env with your settings
```

**Riachtanach íosta:**

| Comhlacht | Cur Síos |
|----------|-------------|
| `PLATFORM` | `anthropic` (réamhshocrú) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Do eochair API don ardán a roghnaigh |

**Roghnach:**

| Comhlacht | Cur Síos |
|----------|-------------|
| `MODEL` | Ainm an mhúnla (réamhshocrú ciallmhar de réir ardáin) |
| `AGENT_NAME` | Ainm taispeána a thaispeántar sa TUI (e.g. `Yukine`) |
| `CAMERA_HOST` | Seoladh IP do cheamara ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Creidiúnaithe an cheamara |
| `ELEVENLABS_API_KEY` | Le haghaidh guth aschur — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` le haghaidh ionchur guth saor ó lámh (teastaíonn `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Áit le haghaidh playback fuaime: `local` (speakear PC, réamhshocrú) \| `remote` (speakear ceamara) \| `both` |
| `THINKING_MODE` | Níl ach do Anthropic — `auto` (réamhshocrú) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Effort smaoineachta oiriúnach: `high` (réamhshocrú) \| `medium` \| `low` \| `max` (Opus 4.6 amháin) |

### 5. Cruthaigh do familiar

```bash
cp persona-template/en.md ME.md
# Edit ME.md — tabhair ainm agus pearsantacht dó
```

### 6. Rith

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI téacs (molta)
./run.sh --no-tui    # REPL gnaoí
```

**Windows:**
```bat
run.bat              # TUI téacs (molta)
run.bat --no-tui     # REPL gnaoí
```

---

## Roghnú LLM

> **Molta: Kimi K2.5** — is é an gníomhaí is fearr a tástáladh go dtí seo. Tugann sé faoi deara an comhthéacs, ceisteanna leanúnacha a chur, agus gníomhaíonn sé uathrialta ar bhealaachtaí nach ndéanann múnlaí eile. Praghsála cosúil le Claude Haiku.

| Ardán | `PLATFORM=` | Múnla réamhshocraithe | Cá háit le h-eochair a fháil |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Uirlis CLI** (claude -p, ollama…) | `cli` | (an t-ord) | — |

**Sampla `.env` do Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # ó platform.moonshot.ai
AGENT_NAME=Yukine
```

**Sampla `.env` do Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # ó api.z.ai
MODEL=glm-4.6v   # taobh súil; glm-4.7 / glm-5 = téacs amháin
AGENT_NAME=Yukine
```

**Sampla `.env` do Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # ó aistudio.google.com
MODEL=gemini-2.5-flash  # nó gemini-2.5-pro le haghaidh cumas níos airde
AGENT_NAME=Yukine
```

**Sampla `.env` do OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # ó openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # roghnach: sonraigh múnla
AGENT_NAME=Yukine
```

> **Nóta:** Chun múnlaí áitiúla/NVIDIA a dhíghníomhachtú, déan deifir nach socraigh `BASE_URL` chuig pointe deiridh áitiúil mar `http://localhost:11434/v1`. Úsáid soláthraithe néaróg níos fearr.

**Sampla `.env` do uirlis CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = arg propmt
# MODEL=ollama run gemma3:27b  # Ollama — gan {}, cuireadh an promt trí stdin
```

---

## Freastal MCP

familiar-ai féidir ceangal le haon freastalaí [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Tosaíonn sé seo tú a chur ar leataobh am cuimhne, rochtain ar chórais, cuardach gréasáin, nó aon uirlis eile.

Conas freastalóirí a shocrú i `~/.familiar-ai.json` (an comhoibriú céanna leis an gCoidíonn Claude):

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

Dáileadh dhá chineál iompair:
- **`stdio`**: seol subproceso áitiúil (`command` + `args`)
- **`sse`**: ceangal le freastalaí HTTP+SSE (`url`)

Athróidh an comhad comhoibríochta le `MCP_CONFIG=/path/to/config.json`.

---

## Crua-earraí

familiar-ai oibríonn le haon chrua-earraí atá agat — nó gan aon chrua-earraí ar chor ar bith.

| Páirt | Cad a dhéanann sé | Sampla | Riachtanach? |
|------|-------------|---------|-----------|
| Ceamara PTZ Wi-Fi | Súil + muineál | Tapo C220 (~$30) | **Moltar** |
| Webcam USB | Súil (duillín) | Aon cheamara UVC | **Moltar** |
| Vacuím róbó | Cosanna | Aon mhúnla comhoiriúnach Tuya | Níl |
| PC / Raspberry Pi | Cuimhne | Aon rud a reáchtálann Python | **Sea** |

> **Moltar ceamara go forte.** Gan ceamara, is féidir le familiar-ai labhairt — ach ní féidir leis an domhan a fheiceáil, rud atá i ndáiríre mar an pointe ar fad.

### Socrú íosta (gan crua-earraí)

Ná fonn le triail? Ní gá duit ach eochair API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Rith `./run.sh` (macOS/Linux/WSL2) nó `run.bat` (Windows) agus tús a chur le comhrá. Cuir crua-earraí isteach de réir a chéile.

### Ceamara PTZ Wi-Fi (Tapo C220)

1. Sa aip Tapo: **Socruithe → Casta → Cuntais Ceamara** — cruthaigh cuntas áitiúil (ní cuntas TP-Link)
2. Faigh IP an cheamara i liosta feistí do ródaire
3. Socraigh isteach i `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=do-úsáideoir-áitiúil
   CAMERA_PASS=do-idirbhearta-áitiúla
   ```

### Glór (ElevenLabs)

1. Faigh eochair API ag [elevenlabs.io](https://elevenlabs.io/)
2. Socraigh isteach i `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # roghnach, úsáideann guth réamhshocraithe más neamh
   ```

Tá dhá chinn playback ann, a rialófar trí `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Speakear PC (réamhshocraithe)
TTS_OUTPUT=remote   # speakear ceamara amháin
TTS_OUTPUT=both     # speakear ceamara + speakear PC go comhthreomhar
```

#### A) Speakear ceamara (trí go2rtc)

Socraigh `TTS_OUTPUT=remote` (nó `both`). Teastaíonn [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Íoslódáil an méid ó [an leathanach d’uisce](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Cuardaigh agus athainm sé:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x riachtanach

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Cruthaigh `go2rtc.yaml` sa áit chéanna:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Úsáid creidiúnachtaí an chuntais áitiúil do cheamara (ní cuntas do chuntasa TP-Link).

4. Tosaíonn familiar-ai go2rtc go huathoibríoch ag an tús. Má tá do cheamara comhoiriúnach le guth péirí (canál cuid), imríonn an guth as seomra an cheamara.

#### B) Speakear áitiúil PC

An réamhshocrú (`TTS_OUTPUT=local`). Déanann sé iarracht imreoirí i gcruth: **paplay** → **mpv** → **ffplay**. Úsáidtear freisin mar thacaíocht nuair a bhíonn `TTS_OUTPUT=remote` agus nach bhfuil go2rtc ar fáil.

| OS | Suiteáil |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (nó `paplay` trí `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — socraigh `PULSE_SERVER=unix:/mnt/wslg/PulseServer` i `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — íoslódáil agus cuir isteach sa PATH, **nó** `winget install ffmpeg` |

> Más rud é nach bhfuil imreoir fuaime ar fáil, tógfar an guth fós — ní imreoidh sé.

### Ionchur guth (Realtime STT)

Socraigh `REALTIME_STT=true` i `.env` le haghaidh ionchur guth saor ó lámh i gcónaí:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # an eochair céanna le TTS
```

familiar-ai sruthlaíonn fuaim an micreafón do ElevenLabs Scribe v2 agus seolaimid clár/subh na mona nuair a stopann tú ag labhairt. Ní gá duilleog a bhrú. Coexists le mód push-to-talk (Ctrl+T).

---

## TUI

familiar-ai comhoibrítear UI téarmaíneach a tógadh le [Textual](https://textual.textualize.io/):

- Stair comhoibrithe atá ag scrollaíocht le téacs ag sruthlú beo
- Comhoiriúnacht ghabhála don `/quit`, `/clear`
- Braith ar an ngníomhaí ag deireadh an chrua-script nuair a tá sé ag smaoineamh
- **Log comhrá** a shábháil go huathoibríoch chuig `~/.cache/familiar-ai/chat.log`

Chun na loga a leanúint i dteirminal eile (úsáideach le haghaidh cóipeáil-placeholder):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

Maireann pearsantacht do familiar i `ME.md`. Tá an comhad seo gitignored — is é féin amháin é.

Féach [`persona-template/en.md`](./persona-template/en.md) le haghaidh sampla, nó [`persona-template/ja.md`](./persona-template/ja.md) do leagan Seapórach.

---

## FAQ

**Q: An oibríonn sé gan GPU?**
Sea. Oibríonn an múnla embedding (multilingual-e5-small) go maith ar an CPU. Déanann GPU sé níos gasta ach ní gá.

**Q: An féidir liom ceamara eile a úsáid seachas Tapo?**
Ba chóir go mbeadh oiriúnach aon cheamara a thacaíonn le ONVIF + RTSP. Is é Tapo C220 an ceann a thástáil muid.

**Q: An bhfuil mo shonraí curtha chuig aon áit?**
Tugtar íomhánna agus téacs chuig do LLM API roghnaithe le haghaidh próiseála. Stóráiltear cuimhní áitiúla i `~/.familiar_ai/`.

**Q: Cén fáth a scríobhann an gníomhaí `（...）` seachas ag labhairt?**
Déantar deimhin go mbeidh `ELEVENLABS_API_KEY` socraithe. Murach sin, tá guth diúltaithe agus téann an gníomhaí ar ais chuig téacs.

## Cúlra teicniúil

Fonn ar conas a oibríonn sé? Féach [docs/technical.md](./docs/technical.md) don taighde agus na cinntí dearaidh a bhaineann le familiar-ai — ReAct, SayCan, Reflexion, Voyager, an córas dóchais, agus níos mó.

---

## Contributing

familiar-ai is turgnamh oscailte. Más gá dhó go bhfuil aon rud seo a chuireann le do chuid — teicniúil nó fealsúnachta — tá fáilte roimh na cur chuige.

**Áiteanna maithe le tosú:**

| Réimse | Cad atá ag teastáil |
|------|---------------|
| Crua-earraí nua | Tacaíocht do níos mó ceamaraí (RTSP, IP Webcam), micreafóin, gníomhaireachtaí |
| Uirlisí nua | Cuardach gréasáin, uathoibriú baile, féilire, éin a dhéanann via MCP |
| Nue cúirteanna | Aon LLM nó múnla áitiúil a oireann leis an gclár `stream_turn` |
| Sainaithint samplaí | ME.md samplaí do theangacha agus pearsantachtaí éagsúla |
| Taighde | Samhlacha dóchais níos fearr, faighte cuimhne, prómpáil teoirice-an-intinn |
| Doiciméadú | Treoracha, siúlóidí, aistriúcháin |

Féach [CONTRIBUTING.md](./CONTRIBUTING.md) do shocrú forbartha, stíl chód, agus treoirlínte PR.

Más neamhshásúil atá tú ar conas a thosú, [oscail ábhar](https://github.com/lifemate-ai/familiar-ai/issues) — beidh áthas orm tú a chur ar an treo ceart.

---

## Ceadúnas

[MIT](./LICENSE)
