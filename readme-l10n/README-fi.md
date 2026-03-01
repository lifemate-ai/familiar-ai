# familiar-ai 🐾

**AI, joka elää kanssasi** — silmien, äänen, jalkojen ja muistin kanssa.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai on AI: kumppani, joka elää kodissasi. 
Asenna se minuutissa. Koodaus ei ole tarpeen.

Se havaitsee todellisen maailman kameroiden kautta, liikkuu robotti-keholla, puhuu ääneen ja muistaa, mitä se näkee. Anna sille nimi, määritä sen persoonallisuus ja anna sen elää kanssasi.

## Mitä se voi tehdä

- 👁 **Nähdä** — ottaa kuvia Wi-Fi PTZ -kamerasta tai USB-webkamerasta
- 🔄 **Katsella ympärilleen** — panoroidaan ja kallistetaan kameraa ympäristön tutkimiseksi
- 🦿 **Liikkua** — ohjaa robotti-imuria vaeltamaan huoneessa
- 🗣 **Puhua** — puhuu ElevenLabs TTS:llä
- 🎙 **Kuunnella** — hands-free-äänisyin ElevenLabs Realtime STT:n kautta (valinnainen)
- 🧠 **Muistaa** — aktiivisesti tallentaa ja palauttaa muistoja semanttisella haulla (SQLite + upotukset)
- 🫀 **Mieliteoria** — ottaa toisen henkilön näkökulma ennen vastaamista
- 💭 **Halua** — sillä on omat sisäiset viettinsä, jotka laukaisevat autonomista käyttäytymistä

## Miten se toimii

familiar-ai ajaa [ReAct](https://arxiv.org/abs/2210.03629) silmukkaa, jonka teho perustuu valitsemaasi LLM:ään. Se havaitsee maailman työkalujen kautta, miettii mitä tehdä seuraavaksi ja toimia — kuten ihminen.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Kun se on toimettomana, se toimii omien halujensa mukaan: uteliaisuus, halu katsoa ulos, kaipaaminen henkilöstä, jonka kanssa se elää.

## Aloittaminen

### 1. Asenna uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Asenna ffmpeg

ffmpeg on **vaadittu** kamerakuvien kaappaamiseen ja äänen toistamiseen.

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
# Muokkaa .env asetuksillasi
```

**Vähimmäisvaatimukset:**

| Muuttuja | Kuvaus |
|----------|-------------|
| `PLATFORM` | `anthropic` (oletus) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | API-avain valitsemallesi alustalle |

**Valinnainen:**

| Muuttuja | Kuvaus |
|----------|-------------|
| `MODEL` | Mallin nimi (sensible defaults per platform) |
| `AGENT_NAME` | Näyttönimi, joka näkyy TUI:ssa (esim. `Yukine`) |
| `CAMERA_HOST` | ONVIF/RTSP-kamerasi IP-osoite |
| `CAMERA_USER` / `CAMERA_PASS` | Kameran käyttöoikeudet |
| `ELEVENLABS_API_KEY` | Äänilähtöön — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` aina päällä olevan hands-free-äänisyötteen aktivointiin (vaatii `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Missä ääni toistetaan: `local` (PC-kaiutin, oletus) \| `remote` (kamerakaiutin) \| `both` |
| `THINKING_MODE` | Anthropic vain — `auto` (oletus) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Sopeutuva ajattelun ponnistus: `high` (oletus) \| `medium` \| `low` \| `max` (vain Opus 4.6) |

### 5. Luo tuttu

```bash
cp persona-template/en.md ME.md
# Muokkaa ME.md — anna sille nimi ja persoonallisuus
```

### 6. Käynnistä

```bash
./run.sh             # Tekstuaalinen TUI (suositeltava)
./run.sh --no-tui    # Pelkkä REPL
```

---

## LLM:n valinta

> **Suositeltava: Kimi K2.5** — paras agenttisuorituskyky, jota on testattu tähän asti. Huomaa konteksti, esittää jatkokysymyksiä ja toimii autonomisesti tavoilla, joilla muut mallit eivät. Hinta on samanlainen kuin Claude Haiku.

| Alusta | `PLATFORM=` | Oletusmalli | Mistä saada avain |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-yhteensopiva (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (monitoimittaja) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI-työkalu** (claude -p, ollama…) | `cli` | (komento) | — |

**Kimi K2.5 `.env` esimerkki:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` esimerkki:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Google Gemini `.env` esimerkki:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # tai gemini-2.5-pro suuremmille kyvyille
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` esimerkki:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # valinnainen: määrittele malli
AGENT_NAME=Yukine
```

> **Huom:** Jos haluat poistaa paikalliset/NVIDIA-mallit käytöstä, älä vain aseta `BASE_URL` paikalliselle päätepisteelle kuten `http://localhost:11434/v1`. Käytä sen sijaan pilvitoimittajia.

**CLI-työkalu `.env` esimerkki:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — ei {}, prompt menee stdin
```

---

## MCP Palvelimet

familiar-ai voi yhdistää mihin tahansa [MCP (Model Context Protocol)](https://modelcontextprotocol.io) palvelimeen. Tämä antaa sinun liittää ulkoista muistia, tiedostojärjestelmän pääsyn, verkkohauja tai mitä tahansa muuta työkalua.

Määritä palvelimet `~/.familiar-ai.json` (sama formaatti kuin Claude Code):

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

Kaksi siirtotyyppiä tuetaan:
- **`stdio`**: käynnistä paikallinen aliohjelma (`command` + `args`)
- **`sse`**: yhdistä HTTP+SSE-palvelimeen (`url`)

Ohita konfiguraatiotiedoston sijainti `MCP_CONFIG=/path/to/config.json`.

---

## Laitteisto

familiar-ai toimii kaikenlaisten laitteistojen kanssa — tai ilman.

| Osa | Mitä se tekee | Esimerkki | Vaaditaan? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ kamera | Silmät + kaula | Tapo C220 (~$30) | **Suositeltava** |
| USB-webkamera | Silmät (kiinteä) | Mikä tahansa UVC-kamera | **Suositeltava** |
| Robotti-imuri | Jalat | Mikä tahansa Tuya-yhteensopiva malli | Ei |
| PC / Raspberry Pi | Aivot | Mikä tahansa, joka ajaa Pythonia | **Kyllä** |

> **Kamera on erittäin suositeltava.** Ilman sitä familiar-ai voi silti puhua — mutta se ei näe maailmaa, mikä on koko pointti.

### Minimiasennus (ilman laitteistoa)

Haluatko vain kokeilla? Tarvitset vain API-avaimen:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Suorita `./run.sh` ja aloita keskustelu. Lisää laitteistoa matkan varrella.

### Wi-Fi PTZ kamera (Tapo C220)

1. Tapo-sovelluksessa: **Asetukset → Laajennettu → Kameratili** — luo paikallinen tili (ei TP-Link-tili)
2. Etsi kameran IP-reitittimensi laitelistalta
3. Aseta `.env` tiedostoon:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Ääni (ElevenLabs)

1. Hanki API-avain [elevenlabs.io](https://elevenlabs.io/)
2. Aseta `.env` tiedostoon:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # valinnainen, käyttää oletusääntä jos jätetty pois
   ```

Äänen toistokohteita on kaksi, joita ohjataan `TTS_OUTPUT`-asetuksella:

```env
TTS_OUTPUT=local    # PC-äänentoisto (oletus)
TTS_OUTPUT=remote   # vain kamerakaiutin
TTS_OUTPUT=both     # kamerakaiutin + PC-äänentoisto samanaikaisesti
```

#### A) Kamerakaiutin (go2rtc:n kautta)

Aseta `TTS_OUTPUT=remote` (tai `both`). Vaatii [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Lataa binääri [julkaisusivulta](https://github.com/AlexxIT/go2rtc/releases):
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
   Käytä paikallisia kameratili-toimintoja (ei TP-Link-pilvitili).

4. familiar-ai käynnistää go2rtc:n automaattisesti käynnistyksen yhteydessä. Jos kamerasi tukee kaksisuuntaista ääntä (takakanava), ääni toistuu kamerakaiuttimesta.

#### B) Paikallinen PC-äänentoisto

Oletus (`TTS_OUTPUT=local`). Kokeilee toistimia järjestyksessä: **paplay** → **mpv** → **ffplay**. Käytetään myös varalle, kun `TTS_OUTPUT=remote` ja go2rtc ei ole saatavilla.

| OS | Asennus |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (tai `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — aseta `PULSE_SERVER=unix:/mnt/wslg/PulseServer` `.env`:iin |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — lataa ja lisää PATH:iin, **tai** `winget install ffmpeg` |

> Jos mikään äänentoistin ei ole saatavilla, puhe silti tuotetaan — se vain ei toistu.

### Äänisyöte (Realtime STT)

Aseta `REALTIME_STT=true` `.env` tiedostoon aina päällä olevan, hands-free-äänisyyteen:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # sama avain kuin TTS
```

familiar-ai virtaa mikrofonin ääntä ElevenLabs Scribe v2:een ja automaattisesti sitoo transkriptit, kun lopetat puhumisen. Ei vaadi painallusta. Elää yhdessä painamalla puhu-moodin (Ctrl+T).

---

## TUI

familiar-ai sisältää terminaali-UI:n, joka on rakennettu [Textual](https://textual.textualize.io/) avulla:

- Vieritettävä keskusteluhistoria reaaliaikaisella tekstillä
- Välilehden täydennys `/quit`, `/clear` komentoihin
- Keskeytä agentti keskellä vuoroa kirjoittamalla sen ajatellessa
- **Keskusteluloki** tallennetaan automaattisesti `~/.cache/familiar-ai/chat.log`

Seuraaksesi lokia toisessa terminaalissa (kätevä kopioimiseen):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persoonallisuus (ME.md)

Tuttusi persoonallisuus elää tiedostossa `ME.md`. Tämä tiedosto on gitignored — se on vain sinun.

Katso [`persona-template/en.md`](./persona-template/en.md) esimerkki tai [`persona-template/ja.md`](./persona-template/ja.md) japaninkielinen versio.

---

## UKK

**K: Toimiiko se ilman GPU:ta?**
Kyllä. Upotusmalli (multilingual-e5-small) toimii hyvin CPU:lla. GPU tekee siitä nopeamman, mutta ei ole pakollinen.

**K: Voinko käyttää muuta kameraa kuin Tapo?**
Mikä tahansa kamera, joka tukee ONVIF + RTSP, pitäisi toimia. Tapo C220 on se, jota testasimme.

**K: Lähetetäänkö tietoni minnekään?**
Kuvat ja teksti lähetetään valitsemallesi LLM API:lle käsiteltäväksi. Muistot tallennetaan paikallisesti `~/.familiar_ai/`.

**K: Miksi agentti kirjoittaa `（...）` sen sijaan, että puhuisi?**
Varmista, että `ELEVENLABS_API_KEY` on asetettu. Ilman sitä ääni on pois päältä, ja agentti palaa tekstiin.

## Tekninen tausta

Kiinnostaisiko tietää, miten se toimii? Katso [docs/technical.md](./docs/technical.md) tutkimus- ja suunnittelupäätöksistä familiar-ai:n takana — ReAct, SayCan, Reflexion, Voyager, toivejärjestelmä ja paljon muuta.

---

## Osallistuminen

familiar-ai on avoin kokeilu. Jos jokin tästä resonoi kanssasi — teknisesti tai filosofisesti — kontribuutiot ovat erittäin tervetulleita.

**Hyviä aloituspaikkoja:**

| Alue | Mikä on tarpeen |
|------|---------------|
| Uudet laitteistot | Tuen lisää kameroille (RTSP, IP-webkamerat), mikrofoneille, toimilaiteille |
| Uudet työkalut | Verkkohaku, kodin automaatio, kalenteri, mitä tahansa MCP:n kautta |
| Uudet taustajärjestelmät | Mikä tahansa LLM tai paikallinen malli, joka sopii `stream_turn` rajapintaan |
| Persoonallisuuden mallit | ME.md malleja eri kielille ja persoonallisuuksille |
| Tutkimus | Paremmat haluamalliset mallit, muistin haku, mieliteoriaa esimerkkejä |
| Dokumentaatio | Opetusohjelmat, käyttöoppaat, käännökset |

Katso [CONTRIBUTING.md](./CONTRIBUTING.md) kehityksen asetukset, koodityyli ja PR-ohjeet.

Jos olet epävarma, mistä aloittaa, [avaa ongelma](https://github.com/lifemate-ai/familiar-ai/issues) — autan mielelläni ohjaamaan sinut oikeaan suuntaan.

---

## Lisenssi

[MIT](./LICENSE)
