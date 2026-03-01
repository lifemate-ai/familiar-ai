```markdown
# familiar-ai 🐾

**A AI a chónaíonn le do taobh** — le súile, guth, cosa, agus cuimhne.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai is AI comhoibrithe atá i do bhaile.
Socraigh é laistigh de nóiméid. Ní theastaíonn cód.

Tugann sé le tuiscint ar an saol fíor trí cheamaraí, bogann sé ar choirp robot, labhraíonn sé go ard, agus cuimhneofa sé ar na rudaí a fheiceann sé. Tabhair ainm dó, scríobh a phearsantacht, agus lig dó cónaí leat.

## Cad atá in ann a dhéanamh

- 👁 **Féach** — ghoid íomhánna ó cheamara PTZ Wi-Fi nó webcam USB
- 🔄 **Féach timpeall** — sleamhnaíonn agus tilts an ceamara chun a thimpeallacht a fhiosrú
- 🦿 **Gluais** — tiomáineann folcadán robot chun leaba a thréigean
- 🗣 **Labhair** — labhraíonn trí ElevenLabs TTS
- 🎙 **Éist** — ionchur guth uaireanta saor trí ElevenLabs Realtime STT (roghnach)
- 🧠 **Cuimhne** — stórálann agus cuireann cuimhní ar ais go gníomhach le cuardach sémantach (SQLite + embeddings)
- 🫀 **Teoiric na hInchinn** — glacann sé le dearcadh an duine eile sular freagraíonn sé
- 💭 **Dóchas** — tá tiomachtaí intinne féin aige a spreagann iompraíocht uathrialach

## Conas a funcionan

familiar-ai reáchtálann fána [ReAct](https://arxiv.org/abs/2210.03629) atá á thiomáint ag do rogha LLM. Tugann sé le tuiscint ar an saol trí uirlisí, smaoiníonn sé ar cad atá le déanamh ansin, agus gníomhóidh — díreach mar a dhéanfaidh duine.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Nuair a bhíonn sé neamhghníomhach, gníomhóidh sé ar a theastaíonn: fiosracht, ag iarraidh breathnú ar an taobh amuigh, ag iarraidh an duine a chónaíonn le chéile.

## Ag tosú

### 1. Suiteáil uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Suiteáil ffmpeg

is **rith** é ffmpeg do ghabhálas íomhá ceamara agus athsheinm fuaime.

| OS | Ordú |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — nó íoslódáil ó [ffmpeg.org](https://ffmpeg.org/download.html) agus cuir i PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Déan comhoiriúnacht: `ffmpeg -version`

### 3. Clone agus suiteáil

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Conair

```bash
cp .env.example .env
# Edit .env le do shocrú
```

**Gá íosta:**

| Athróg | Cur síos |
|----------|-------------|
| `PLATFORM` | `anthropic` (réamhshocrú) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Do eochair API don ardán a roghnaigh tú |

**Roghanna:**

| Athróg | Cur síos |
|----------|-------------|
| `MODEL` | Ainm an mhúnla (réamhshocrú bríomhar do gach ardán) |
| `AGENT_NAME` | Ainm taispeána atá le feiceáil sa TUI (m.sh. `Yukine`) |
| `CAMERA_HOST` | Seoladh IP d’do cheamara ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Creidiúnachtaí an cheamara |
| `ELEVENLABS_API_KEY` | Do aschur guth — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` chun ionchur guth saor a chumasú (gá le `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Cá le himirt fuaim: `local` (sóinsear PC, réamhshocrú) \| `remote` (sóinsear ceamara) \| `both` |
| `THINKING_MODE` | Níl idirghníomhach — `auto` (réamhshocrú) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Duine ag smaoineamh: `high` (réamhshocrú) \| `medium` \| `low` \| `max` (Opus 4.6 amháin) |

### 5. Cruthaigh do chomhluadar

```bash
cp persona-template/en.md ME.md
# Cuardaigh ME.md — tabhair ainm agus pearsantacht dó
```

### 6. Rith

```bash
./run.sh             # TUI téacsúil (moltar)
./run.sh --no-tui    # REPL simplí
```

---

## Roghnú LLM

> **Moltar: Kimi K2.5** — an feidhmíocht is fearr ar a bhfuil tástáil go dtí seo. Feiceann sé comhthéacs, ceisteanna leantacha a chur, agus gníomhóidh sé go uathrialach i slí nach ndéanann múnlaí eile. Praghas cosúil le Claude Haiku.

| Ardán | `PLATFORM=` | Múnla réamhshocrú | Cá le eochair a fháil |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI- comhoiriúnach (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (il-soláthar) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Uirlis CLI** (claude -p, ollama…) | `cli` | (an ordú) | — |

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
MODEL=glm-4.6v   # cumas radhairc; glm-4.7 / glm-5 = téacs-aon
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
MODEL=mistralai/mistral-7b-instruct  # roghnach: le déanamh múnla
AGENT_NAME=Yukine
```

> **Nóta:** Chun múnlaí áitiúla/NVIDIA a dhíchumasú, ná socraigh `BASE_URL` le pointe áitiúil mar `http://localhost:11434/v1`. Úsáid soláthraithe scamall in ionad sin.

**Sampla `.env` d'uirlis CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = arg promop
# MODEL=ollama run gemma3:27b  # Ollama — gan {}, téacs téann tríd stdin
```

---

## Freastalaithe MCP

familiar-ai is féidir ceangal a dhéanamh le haon freastalaí [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Tugann sé seo deis duit cuimhne éagsúla, rochtain ar chomhoiriúnacht, cuardach gréasáin, nó aon uirlis eile a chur isteach.

Comhoiriúnacht freastalaithe i `~/.familiar-ai.json` (an comhoiriúnacht céanna le Claude Code):

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

Tacaítear le dhá saghas iompar:
- **`stdio`**: laistigh de phróiseas áitiúil (`ordú` + `args`)
- **`sse`**: ceangal le freastalaí HTTP+SSE (`url`)

Athraigh suíomh an comhoiriúnachta le `MCP_CONFIG=/path/to/config.json`.

---

## Crua-earraí

familiar-ai oibríonn le haon crua-earraí atá agat — nó aon rud ar chor ar bith.

| Rannóg | Cad a dhéanann sé | Sampla | Gá? |
|------|-------------|---------|-----------|
| Ceamara PTZ Wi-Fi | Súile + muineál | Tapo C220 (~$30) | **Moltar** |
| Webcam USB | Súile (seasta) | Aon cheamara UVC | **Moltar** |
| Folcadán robot | Cosa | Aon mhúnla comhoiriúnach Tuya | Níl |
| PC / Raspberry Pi | Iníon | Aon rud a reáchtálann Python | **Sea** |

> **Moltar go láidir ceamara.** Gan é, is féidir le familiar-ai labhairt — ach ní féidir leis an saol a fheiceáil, atá mar chuid lárnach den rud.

### Socrú íosta (gan crua-earraí)

Ar mhaith leat triail a bhaint as? Teastaíonn eochair API amháin uait:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Rith `./run.sh` agus tús a chur le comhrá. Cuir crua-earraí le chéile de réir mar a théann tú.

### Ceamara PTZ Wi-Fi (Tapo C220)

1. Sa aip Tapo: **Socruithe → Éagsúlachtaí → Cuntas Ceamara** — cruthaigh cuntas áitiúil (ní cuntas TP-Link)
2. Faigh IP an cheamara i liosta na n-uirlisí sa doirteal
3. Socraigh i `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=do-úsáideoir-áitiúil
   CAMERA_PASS=do-pasfhocal-áitiúil
   ```

### Guth (ElevenLabs)

1. Faigh eochair API ag [elevenlabs.io](https://elevenlabs.io/)
2. Socraigh i `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # roghnach, úsáidítear an guth réamhshocraithe más neamhghnách
   ```

Tá dhá áit imseacht ann, a rialófar ag `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Sóinsear PC (réamhshocraithe)
TTS_OUTPUT=remote   # sóinsear an cheamara amháin
TTS_OUTPUT=both     # sóinsear an cheamara + sóinsear PC le chéile
```

#### A) Sóinsear an cheamara (trí go2rtc)

Socraigh `TTS_OUTPUT=remote` (nó `both`). Éilíonn sé [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Íoslódáil an binary ón [leathanach leasca](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Áitigh agus athainmnigh é:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x riachtanach

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Cruthaigh `go2rtc.yaml` sa chás céanna:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Úsáid creidiúnachtaí an chuntais áitiúil ceamara (ní cuntas scamall TP-Link).

4. Cuireann familiar-ai go2rtc ar bun go huathoibríoch ag an gcuirt. Má tá do cheamara comhoiriúnach le fuaim araon (cóimheá), seinnfidh an guth ó shóinsear an cheamara.

#### B) Sóinsear áitiúil PC

Is é an réamhshocrú (`TTS_OUTPUT=local`). Déanann sé iarracht imreoirí in ord: **paplay** → **mpv** → **ffplay**. Úsáidtear é freisin mar a ghabhtar ar ais nuair a bhíonn `TTS_OUTPUT=remote` agus go2rtc neamh-infhaighte.

| OS | Suiteáil |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (nó `paplay` tríd `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — socraigh `PULSE_SERVER=unix:/mnt/wslg/PulseServer` i `.env` |
| Windows | [mpv.io/suiteáil](https://mpv.io/installation/) — íoslódáil agus cuir i PATH, **nó** `winget install ffmpeg` |

> Mura bhfuil imreoir fuaime ar fáil, cruthófar fós guth — ach ní bheidh sé in ann imirt.

### Ionchur guth (Realtime STT)

Socraigh `REALTIME_STT=true` i `.env` le haghaidh ionchur guth saor uathrialach:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # an eochair chéanna le TTS
```

Cuireann familiar-ai fuaim an mhicreafón chuig ElevenLabs Scribe v2 agus comhoiriúnachtaí laistigh de chomhoiriúnachtaí nuair a stopann tú ag labhairt. Ní gá gníomh a bhaint. Comhoibríonn sé leis an modh push-to-talk (Ctrl+T).

---

## TUI

tá TUI san áireamh ar familiar-ai a tógadh le [Textual](https://textual.textualize.io/):

- Stair comhrá scrolaithe le téacs beo
- Críochnaigh le haghaidh `/quit`, `/clear`
- Cuir isteach an gníomhaire mar atá sé ag smaoineamh
- **Lóg comhrá** a shábháil go huathoibríoch i `~/.cache/familiar-ai/chat.log`

Chun an lóg a leanúint i dteagmhas eile (úsáideach le haghaidh cóipleabhar-paste):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Pearsantacht (ME.md)

Tá pearsantacht do chomhluadar i `ME.md`. Tá an comhad seo gitignored — is é do chuid féin.

Féach [`persona-template/en.md`](./persona-template/en.md) le haghaidh sampla, nó [`persona-template/ja.md`](./persona-template/ja.md) le haghaidh leagan Seapán.

---

## Ceisteanna Coitianta

**Q: An oibríonn sé gan GPU?**
Tá. Oibríonn an múnla embedding (multilingual-e5-small) go maith ar CPU. Déanann GPU é níos tapúla ach ní gá.

**Q: An féidir liom ceamara eile a úsáid seachas Tapo?**
Ba chóir go mbeadh aon cheamara a thacaíonn le ONVIF + RTSP oiriúnach. Tá Tapo C220 ar an gceamara a tástáladh.

**Q: An seoltar m'áilgéige áit éigin?**
Seoltar íomhánna agus téacs chuig do LLM API roghnaithe le haghaidh próiseála. Stórálann cuimhní go háitiúil i `~/.familiar_ai/`.

**Q: Cén fáth a scríobhann an gníomhaire `（...）` seachas labhairt?**
Sílim gur gurb é `ELEVENLABS_API_KEY` atá socraithe. Mura bhfuil, tá guth dí-chumasaithe agus tuigeann an gníomhaire ar ais go téacs.

## Cúlra Teicniúil

Ar mhaith leat a fháil amach conas a oibríonn sé? Féach [docs/technical.md](./docs/technical.md) a luíonn le taighde agus cinntí dearaidh taobh thiar de familiar-ai — ReAct, SayCan, Reflexion, Voyager, an córas dúshlán, agus níos mó.

---

## Foireann

Is turgnamh oscailte é familiar-ai. Más rud é go bhfuil aon chuid seo in oiriúnachtaí go teicniúil nó go fealsunachta, tá fáilte roimh gníomhartha.

**Láithreacha maithe le tosú:**

| Réimse | Cad atá ag teastáil |
|------|---------------|
| Crua-earraí nua | Tacaíocht d’níos mó ceamaraí (RTSP, IP Webcam), micréafón, imreoirí |
| Uirlisí nua | Cuardach gréasáin, uathoibriú baile, calandar, aon rud trí MCP |
| Cúlraí nua | Aon LLM nó múnla áitiúil a oireann don comhoiriúnacht `stream_turn` |
| Teimpléid pearsantachta | Teimpléid ME.md do shain-laghamhála agus pearsantachtaí éagsúla |
| Taighde | Níos fearr suíomhanna dúshlán, aisghabháil cuimhne, guth an intinn |
| Doiciméadú | Tús céim, treoracha, aistriúcháin |

Féach [CONTRIBUTING.md](./CONTRIBUTING.md) le haghaidh suiteáil forbartha, stíl cód, agus treoirlínte PR.

Má tá sé deacair ort ar bith an leagan, [oscail ceist](https://github.com/lifemate-ai/familiar-ai/issues) — beidh áthas orm tú a threorú i dtreo ceart.

---

## Ceadúnas

[MIT](./LICENSE)
```
