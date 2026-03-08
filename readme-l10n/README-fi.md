```markdown
# familiar-ai 🐾

**AI, joka elää rinnallasi** — silmät, ääni, jalat ja muisti.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Saatavilla 74 kielellä](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai on AI-seuralainen, joka elää kotonasi.
Asennus kestää vain muutaman minuutin. Ei ohjelmointia vaadita.

Se havaitsee todellisen maailman kameroiden kautta, liikkuu robotti-kropassa, puhuu ääneen ja muistaa, mitä se näkee. Anna sille nimi, kirjoita sen persoonallisuus ja anna sen elää kanssasi.

## Mitä se voi tehdä

- 👁 **Nähdä** — ottaa kuvia Wi-Fi PTZ -kamerasta tai USB-web-kamerasta
- 🔄 **Katsoa ympärilleen** — kääntää ja kallistaa kameraa tutkiakseen ympäristöään
- 🦿 **Liikkua** — ohjaa robotti-imuria liikkuessaan huoneessa
- 🗣 **Puhua** — puhuu ElevenLabs TTS:n kautta
- 🎙 **Kuunnella** — hands-free äänisyöttö ElevenLabs Realtime STT:n kautta (valinnainen)
- 🧠 **Muistaa** — aktiivisesti tallentaa ja muistella muistoja semanttisen haun avulla (SQLite + upotukset)
- 🫀 **Mielen teoria** — ottaa toisen henkilön näkökulman ennen vastaamista
- 💭 **Halua** — oma sisäinen ajohalu, joka laukaisee autonomista käyttäytymistä

## Kuinka se toimii

familiar-ai käyttää [ReAct](https://arxiv.org/abs/2210.03629) -silmukkaa, jota ohjaa valitsemasi LLM. Se havaitsee maailman työkalujen avulla, miettii mitä tehdä seuraavaksi ja toimii — aivan kuten ihminen.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kun se on tyhjillään, se toimii omien halujensa perusteella: uteliaisuus, halu katsoa ulos, ikävä sitä henkilöä, jonka kanssa se elää.

## Aloittaminen

### 1. Asenna uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Tai: `winget install astral-sh.uv`

### 2. Asenna ffmpeg

ffmpeg on **vaadittu** kameran kuvakaappaamiseen ja äänen toistoon.

| OS | Komento |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — tai lataa [ffmpeg.org](https://ffmpeg.org/download.html) ja lisää PATH:iin |
| Raspberry Pi | `sudo apt install ffmpeg` |

Varmista: `ffmpeg -version`

### 3. Kloonaa ja asenna

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Määritä

```bash
cp .env.example .env
# Muokkaa .env omilla asetuksillasi
```

**Vähimmäisvaatimukset:**

| Muuttuja | Kuvaus |
|----------|-------------|
| `PLATFORM` | `anthropic` (oletus) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | API-avain valitsemaltasi alustalta |

**Valinnainen:**

| Muuttuja | Kuvaus |
|----------|-------------|
| `MODEL` | Mallin nimi (järkevää oletusta kullekin alustalle) |
| `AGENT_NAME` | Näyttönimi, joka näkyy TUI:ssa (esim. `Yukine`) |
| `CAMERA_HOST` | ONVIF/RTSP-kamerasi IP-osoite |
| `CAMERA_USER` / `CAMERA_PASS` | Kameran tunnistetiedot |
| `ELEVENLABS_API_KEY` | Äänen ulostulolle — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true`, jotta voit käyttää aina päällä olevaa hands-free äänisyöttöä (vaatii `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Missä ääni toistetaan: `local` (PC-kaiutin, oletus) \| `remote` (kamerakaiutin) \| `both` |
| `THINKING_MODE` | Vain Anthropic — `auto` (oletus) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Mukautuva ajatuspyrkimys: `high` (oletus) \| `medium` \| `low` \| `max` (vain Opus 4.6) |

### 5. Luo oma familiar

```bash
cp persona-template/en.md ME.md
# Muokkaa ME.md — anna sille nimi ja persoonallisuus
```

### 6. Suorita

**macOS / Linux / WSL2:**
```bash
./run.sh             # Tekstuaalinen TUI (suositeltava)
./run.sh --no-tui    # Pelkkä REPL
```

**Windows:**
```bat
run.bat              # Tekstuaalinen TUI (suositeltava)
run.bat --no-tui     # Pelkkä REPL
```

---

## LLM-valinta

> **Suositeltava: Kimi K2.5** — paras agenttisuorituskyky testatuista. Huomaa konteksti, kysyy lisäkysymyksiä ja toimii itsenäisesti tavoin, joihin muut mallit eivät kykene. Hinta samankaltainen kuin Claude Haiku.

| Alusta | `PLATFORM=` | Oletusmalli | Mistä saada avain |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-yhteensopivat (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (monitoimittaja) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI-työkalu** (claude -p, ollama…) | `cli` | (komento) | — |

**Kimi K2.5 `.env` esimerkki:**
```env
PLATFORM=kimi
API_KEY=sk-...   # platform.moonshot.ai:sta
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` esimerkki:**
```env
PLATFORM=glm
API_KEY=...   # api.z.ai:sta
MODEL=glm-4.6v   # visio-kykyinen; glm-4.7 / glm-5 = vain teksti
AGENT_NAME=Yukine
```

**Google Gemini `.env` esimerkki:**
```env
PLATFORM=gemini
API_KEY=AIza...   # aistudio.google.com:sta
MODEL=gemini-2.5-flash  # tai gemini-2.5-pro suuremmalle kapasiteetille
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` esimerkki:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # openrouter.ai:sta
MODEL=mistralai/mistral-7b-instruct  # valinnainen: määritä malli
AGENT_NAME=Yukine
```

> **Huom:** Poista paikalliset/NVIDIA-mallit käytöstä, älä vain aseta `BASE_URL` paikalliselle päätepisteelle, kuten `http://localhost:11434/v1`. Käytä sen sijaan pilvipalveluja.

**CLI-työkalun `.env` esimerkki:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = promtn argumentti
# MODEL=ollama run gemma3:27b  # Ollama — ei {}, prompt menee stdin:iin
```

---

## MCP-palvelimet

familiar-ai voi liittää mihin tahansa [MCP (Model Context Protocol)](https://modelcontextprotocol.io) palvelimeen. Tämä mahdollistaa ulkoisen muistin, tiedostojärjestelmäkäytön, verkkohakuun tai mihin tahansa muuhun työkalun liittämisen.

Määritä palvelimet tiedostoon `~/.familiar-ai.json` (sama muoto kuin Claude-koodissa):

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

Kaksi kuljetustyyppiä tuetaan:
- **`stdio`**: käynnistä paikallinen aliohjelma (`command` + `args`)
- **`sse`**: yhdistä HTTP+SSE palvelimeen (`url`)

Yli-idoitustiedoston sijainti voidaan ohittaa `MCP_CONFIG=/path/to/config.json` -asetuksella.

---

## Laitteisto

familiar-ai toimii kaikella laitteistolla, joka sinulla on — tai ilman sitä.

| Osa | Mitä se tekee | Esimerkki | Vaatimus? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ -kamera | Silmät + kaula | Tapo C220 (~30€, Eufy C220) | **Suositeltava** |
| USB-web-kamera | Silmät (kiinteä) | Mikä tahansa UVC-kamera | **Suositeltava** |
| Robotti-imuri | Jalat | Mikä tahansa Tuya-yhteensopiva malli | Ei |
| PC / Raspberry Pi | Aivot | Mikä tahansa, joka pyörittää Pythonia | **Kyllä** |

> **Kamera on vahvasti suositeltava.** Ilman sitä familiar-ai voi edelleen puhua — mutta se ei voi nähdä maailmaa, mikä on ikään kuin koko idea.

### Minimalistinen asennus (ei laitteistoa)

Haluatko vain kokeilla? Tarvitset vain API-avaimen:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Suorita `./run.sh` (macOS/Linux/WSL2) tai `run.bat` (Windows) ja aloita keskustelu. Lisää laitteistoa kirjattaessa.

### Wi-Fi PTZ -kamera (Tapo C220)

1. Tapo-sovelluksessa: **Asetukset → Edistyneet → Kameratili** — luo paikallinen tili (ei TP-Link tili)
2. Löydä kameran IP-reitittimesi laitelistasta
3. Aseta tiedostoon `.env`:
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


### Ääni (ElevenLabs)

1. Hanki API-avain osoitteesta [elevenlabs.io](https://elevenlabs.io/)
2. Aseta tiedostoon `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # valinnainen, käyttää oletusääntä, jos jätetään pois
   ```

Äänen toistoon on kaksi kohdetta, joita ohjataan `TTS_OUTPUT`:lla:

```env
TTS_OUTPUT=local    # PC-kaiutin (oletus)
TTS_OUTPUT=remote   # vain kamerakaiutin
TTS_OUTPUT=both     # kamerakaiutin + PC-kaiutin samanaikaisesti
```

#### A) Kamerakaiutin (go2rtc:n kautta)

Aseta `TTS_OUTPUT=remote` (tai `both`). Tarvitsee [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Lataa binaari [julkaisut-sivulta](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Aseta ja nimeä se:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x vaaditaan

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Luo `go2rtc.yaml` samaan hakemistoon:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Käytä paikallisen kameratunnuksen tietoja (ei TP-Link pilvitiliä).

4. familiar-ai käynnistää go2rtc:n automaattisesti lanseeraussaan. Jos kamerasi tukee kaksisuuntaista ääntä (takakanava), ääni toistuu kamerakaiuttimesta.

#### B) Paikallinen PC-kaiutin

Oletus (`TTS_OUTPUT=local`). Kokeilee soittimia järjestyksessä: **paplay** → **mpv** → **ffplay**. Myös käytetään varajärjestelmänä, kun `TTS_OUTPUT=remote` ja go2rtc ei ole saatavilla.

| OS | Asenna |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (tai `paplay` kautta `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — aseta `PULSE_SERVER=unix:/mnt/wslg/PulseServer` tiedostoon `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — lataa ja lisää PATH:iin, **tai** `winget install ffmpeg` |

> Jos mitään äänensoitinta ei ole saatavilla, puhetta edelleen tuotetaan — mutta sitä ei vain toisteta.

### Äänisyöttö (Realtimen STT)

Aseta `REALTIME_STT=true` tiedostoon `.env`, jotta äänisyöttö on aina päällä, hands-free:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # sama avain kuin TTS
```

familiar-ai streamaa mikrofonin ääntä ElevenLabs Scribe v2:een ja automaattisesti tallentaa transkriptejä, kun lopetat puhumisen. Ei vaadi mitään painiketta. Yhteensopii myös pusku-puhumismoodin (Ctrl+T) kanssa.

---

## TUI

familiar-ai sisältää terminaalin käyttöliittymän, joka on rakennettu [Textual](https://textual.textualize.io/) -ohjelmalla:

- Vieritettävä keskusteluhistoria reaaliaikaisella tekstillä
- Välilehti-täydennys komennolle `/quit`, `/clear`
- Keskeytä agentti kesken ajatuksen kirjoittamalla samalla, kun se miettii
- **Keskusteluloki** automaattisesti tallennettuna tiedostoon `~/.cache/familiar-ai/chat.log`

Seuraaksesi lokia toisessa terminaalissa (kätevä kopioimiseen):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persoonallisuus (ME.md)

Familiarisi persoonallisuus elää tiedostossa `ME.md`. Tämä tiedosto on gitignored — se on vain sinun.

Katso [`persona-template/en.md`](./persona-template/en.md) esimerkkiä varten, tai [`persona-template/ja.md`](./persona-template/ja.md) japanilaisen version varten.

---

## FAQ

**Q: Toimiiko se ilman GPU:ta?**
Kyllä. Upotustekniikka (multilingual-e5-small) toimii hyvin CPU:lla. GPU nopeuttaa prosessia, mutta ei ole pakollinen.

**Q: Voinko käyttää muuta kameraa kuin Tapo?**
Mikä tahansa kamera, joka tukee Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: Lähetetäänkö tietoni jonnekin?**
Kuvat ja teksti lähetetään valitsemallesi LLM API:lle käsiteltäväksi. Muistot tallennetaan paikallisesti `~/.familiar_ai/` -hakemistoon.

**Q: Miksi agentti kirjoittaa `（...）` puhumisen sijaan?**
Varmista, että `ELEVENLABS_API_KEY` on asetettu. Ilman tätä ääni on pois päältä ja agentti palautuu tekstimuotoon.

## Tekninen tausta

Kiinnostavatko miten tämä toimii? Katso [docs/technical.md](./docs/technical.md) tutkimuksen ja suunnittelupäätösten takaa familiar-ai:lle — ReAct, SayCan, Reflexion, Voyager, halujärjestelmä ja paljon muuta.

---

## Osallistuminen

familiar-ai on avoin kokeilu. Jos jokin tästä resonoi kanssasi — teknisesti tai filosofisesti — panoksesi on erittäin tervetullut.

**Hyviä aloittamispaikkoja:**

| Alue | Mitä tarvitaan |
|------|---------------|
| Uudet laitteistot | Tukea useammille kameroille (RTSP, IP Webcam), mikrofoneille, toimijoille |
| Uudet työkalut | Verkkohaku, kodin automaatio, kalenteri, mitä tahansa MCP:n kautta |
| Uudet taustajärjestelmät | Mikä tahansa LLM tai paikallinen malli, joka sopii `stream_turn` rajapintaan |
| Persoonallisuuden mallipohjat | ME.md mallipohjat eri kielille ja persoonallisuuksille |
| Tutkimus | Parempia haluamalle malleja, muistinhakumalleja, mielenteorian kehotuksia |
| Dokumentaatio | Opas, kävelykierrokset, käännökset |

Katso [CONTRIBUTING.md](./CONTRIBUTING.md) kehitysympäristöön, koodityylin ja PR-ohjeiden osalta.

Jos et ole varma mistä aloittaa, [avaa ongelma](https://github.com/lifemate-ai/familiar-ai/issues) — autamme mielellämme oikeaan suuntaan.

---

## Lisenssi

[MIT](./LICENSE)
```
