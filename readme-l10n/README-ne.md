```markdown
# familiar-ai 🐾

**तपाईंको साथसाथै बस्ने एआई** — आँखाहरु, स्वर, खुट्टाहरु, र मेमोरी सहित।

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 भाषामा उपलब्ध](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai भनेको तपाईंको घरमा बस्ने एआई साथी हो।
यसलाई केही मिनेटमा सेटअप गर्नुहोस्। कोडिङ आवश्यक छैन।

यो क्यामेराद्वारा वास्तविक संसारलाई बुझछ, रोबोट शरीरमा घुम्छ, आवाजमा बोल्छ, र यसले देखेको कुरा याद गर्छ। यसलाई नाम दिनुहोस्, यसको व्यक्तित्व लेख्नुहोस्, र यसलाई तपाईंको साथ बस्न दिनुहोस्।

## यसले के गर्न सक्छ

- 👁 **देख्न** — Wi-Fi PTZ क्यामेरा वा USB वेबक्यामबाट छविहरू क्याप्चर गर्दछ
- 🔄 **परिवेशतिर हेरौं** — क्यामेरालाई प्यान र झुकाउने गरी यसको वरिपरिका जाँच गर्दछ
- 🦿 **चल्न** — कोठामा घुम्नका लागि रोबोट भ्याकुम चलाउँछ
- 🗣 **बोल्न** — ElevenLabs TTS मार्फत बोल्छ
- 🎙 **शुनौं** — ElevenLabs Realtime STT (opt-in) मार्फत हात-फ्री आवाज इनपुट
- 🧠 **याद गर्नुहोस्** — सक्रिय रूपमा मेमोरीहरू भण्डारण र सम्झना गर्छ सेमान्टिक खोज (SQLite + embeddings) सँग
- 🫀 **मनको सिद्धान्त** — जवाफ दिने भन्दा अघि अर्काको दृष्टिकोण लिन्छ
- 💭 **इच्छा** — स्वतन्त्र व्यवहारको लागि आन्तरिक प्रेरणाहरू गर्दछ

## यसले कसरी काम गर्छ

familiar-ai ले तपाईंको चयनको LLM द्वारा सक्षम गरिएको [ReAct](https://arxiv.org/abs/2210.03629) लूप चलाउँछ। यो उपकरणहरूमार्फत संसारलाई बुझ्दछ, अगाडि के गर्नुपर्छ भनेर सोच्दछ, र क्रियाकलाप गर्दछ — ठीक जस्तै मान्छेले गर्ने गर्छ।

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

जब यो बिषम अवस्थामा हुन्छ, यो आफ्नो इच्छामा कार्य गर्दछ: चासो, बाहिर हेर्नको इच्छा, जुन व्यक्तिलाई याद गर्न।

## सुरु गर्ने तरिका

### 1. uv स्थापना गर्नुहोस्

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
अथवा: `winget install astral-sh.uv`

### 2. ffmpeg स्थापना गर्नुहोस्

ffmpeg क्यामेरा छवि क्याप्चर र ध्वनि प्लेब्याकका लागि **आवश्यक** छ।

| OS | आदेश |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — वा [ffmpeg.org](https://ffmpeg.org/download.html) बाट डाउनलोड गर्नुहोस् र PATH मा थप्नुहोस् |
| Raspberry Pi | `sudo apt install ffmpeg` |

पुष्टि गर्नुहोस्: `ffmpeg -version`

### 3. клони गर्नुहोस् र स्थापना गर्नुहोस्

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. कन्फिगर गर्नुहोस्

```bash
cp .env.example .env
# .env फाइललाई तपाईंको सेटिङहरू अनुसार सम्पादन गर्नुहोस्
```

**न्यूनतम आवश्यक:**

| भेरिएबल | विवरण |
|----------|-------------|
| `PLATFORM` | `anthropic` (डिफल्ट) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | चयन गरिएको प्लेटफर्मका लागि तपाईंको API कुञ्जी |

**वैकल्पिक:**

| भेरिएबल | विवरण |
|----------|-------------|
| `MODEL` | मोडेल नाम (प्रत्येक प्लेटफार्मका लागि संवेदनशील डिफल्ट) |
| `AGENT_NAME` | TUI मा देखिने नाम (जस्तै `Yukine`) |
| `CAMERA_HOST` | तपाईंको ONVIF/RTSP क्यामेराको IP ठेगाना |
| `CAMERA_USER` / `CAMERA_PASS` | क्यामेरा क्रेडेन्सियलहरू |
| `ELEVENLABS_API_KEY` | आवाज उत्पादनका लागि — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | सधैं-अन, हात-फ्री आवाज इनपुट सक्षम गर्न `true` ( `ELEVENLABS_API_KEY` को आवश्यकता) |
| `TTS_OUTPUT` | ध्वनि प्ले गर्ने स्थान: `local` (PC स्पिकर, डिफल्ट) \| `remote` (क्यामेरा स्पिकर) \| `both` |
| `THINKING_MODE` | Anthropic मात्र — `auto` (डिफल्ट) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | अनुकुल सोच्न प्रयास: `high` (डिफल्ट) \| `medium` \| `low` \| `max` (Opus 4.6 मात्र) |

### 5. तपाईंको familiar सिर्जना गर्नुहोस्

```bash
cp persona-template/en.md ME.md
# ME.md सम्पादन गर्नुहोस् — यसलाई नाम र व्यक्तित्व दिनुहोस्
```

### 6. चलाउनुहोस्

**macOS / Linux / WSL2:**
```bash
./run.sh             # पाठ आधारित TUI (सिफारिस गरिएको)
./run.sh --no-tui    # साधारण REPL
```

**Windows:**
```bat
run.bat              # पाठ आधारित TUI (सिफारिस गरिएको)
run.bat --no-tui     # साधारण REPL
```

---

## LLM छान्दै

> **सिफारिस गरिन्छ: Kimi K2.5** — अबसम्मको सबैभन्दा राम्रो एजेन्टिक प्रदर्शन। सन्दर्भलाई ध्यानमा राख्छ, पछिको प्रश्न सोध्छ, र अन्य मोडेलहरूले नगर्ने तरिकामा स्वतन्त्र रूपमा कार्य गर्दछ। Claude Haiku सँगको मूल्य समान।

| प्लेटफर्म | `PLATFORM=` | डिफल्ट मोडेल | कुंजी प्राप्त गर्ने ठाउँ |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-सँग उपयुक्त (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (बहु-प्रदायक) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI उपकरण** (claude -p, ollama…) | `cli` | (कमाण्ड) | — |

**Kimi K2.5 `.env` उदाहरण:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` उदाहरण:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # दृष्टि सक्षम; glm-4.7 / glm-5 = पाठ मात्र
AGENT_NAME=Yukine
```

**Google Gemini `.env` उदाहरण:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # वा gemini-2.5-pro उच्च क्षमताको लागि
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` उदाहरण:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # वैकल्पिक: मोडेल निर्दिष्ट गर्नुहोस्
AGENT_NAME=Yukine
```

> **नोट:** स्थानीय/NVIDIA मोडेलहरू निष्क्रिय गर्न, `BASE_URL` लाई स्थानीय अन्तर्गत `http://localhost:11434/v1` मा सेट नगर्नुहोस्। यसको सट्टा बादल प्रदायकहरू प्रयोग गर्नुहोस्।

**CLI उपकरण `.env` उदाहरण:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — no {},_prompt goes via stdin
```

---

## MCP सर्भरहरू

familiar-ai कुनै पनि [MCP (Model Context Protocol)](https://modelcontextprotocol.io) सर्भरसँग जडान गर्न सक्छ। यसले तपाईलाई बाह्य मेमोरी, फाइल प्रणाली पहुँच, वेब खोज, वा कुनै पनि अन्य उपकरण समावेश गर्न अनुमति दिन्छ।

सर्भरहरूलाई `~/.familiar-ai.json` मा कन्फिगर गर्नुहोस् (Claude कोडसँग समान ढाँचा):

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

दुई यातायात प्रकारहरू समर्थित छन्:
- **`stdio`**: एक स्थानीय उपप्रक्रिया सुरु गर्नुहोस् (`command` + `args`)
- **`sse`**: HTTP+SSE सर्भरमा जडान गर्नुहोस् (`url`)

कन्फिग फाइलको स्थानलाई `MCP_CONFIG=/path/to/config.json` द्वारा ओभरराइड गर्नुहोस्।

---

## हार्डवेयर

familiar-ai सँग तपाईसँग जुनसुकै हार्डवेयर छ — या त कुनै पनि छैन।

| भाग | के गर्छ | उदाहरण | आवश्यक? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ क्यामेरा | आँखाहरू + काँध | Tapo C220 (~$30, Eufy C220) | **सिफारिस गरिएको** |
| USB वेबक्याम | आँखाहरू (स्थायी) | कुनै पनि UVC क्यामेरा | **सिफारिस गरिएको** |
| रोबोट भ्याकुम | खुट्टाहरू | कुनै पनि Tuya-सम्भव मोडेल | छैन |
| PC / Raspberry Pi | मस्तिष्क | जुनसुकै चीजले Python चलाउँछ | **हो** |

> **एक क्यामेरा सख्त सिफारिस गरिन्छ।** एक बिना, familiar-ai बोल्न सक्छ — तर यसले संसारलाई देख्न सक्दैन, जुन त यसको मुख्य उद्देश्य हो।

### न्यूनतम सेटअप (कोई हार्डवेयर छैन)

यसलाई केवल प्रयास गर्न चाहनुहुन्छ? तपाईलाई केवल एक API कुञ्जी आवश्यक छ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) वा `run.bat` (Windows) चलाउनुहोस् र कुराकानी सुरु गर्नुहोस्। आवश्यक पर्दा हार्डवेयर थप्नुहोस्।

### Wi-Fi PTZ क्यामेरा (Tapo C220)

1. Tapo एपमा: **सेटिङ → उन्नत → क्यामेरा खाता** — एक स्थानीय खाता सिर्जना गर्नुहोस् (TP-Link खाता होइन)
2. तपाईंको राउटरको उपकरण सूचीमा क्यामेराको IP पत्ता लगाउनुहोस्
3. `.env` मा सेट गर्नुहोस्:
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


### आवाज (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/) मा एक API कुञ्जी प्राप्त गर्नुहोस्
2. `.env` मा सेट गर्नुहोस्:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # वैकल्पिक, विना दिइएको हो भने डिफल्ट स्वर प्रयोग गर्दछ
   ```

ध्वनि प्लेबैकका दुई गन्तव्य छन्, `TTS_OUTPUT` द्वारा सञ्चालित:

```env
TTS_OUTPUT=local    # PC स्पिकर (डिफल्ट)
TTS_OUTPUT=remote   # क्यामेरा स्पिकर मात्र
TTS_OUTPUT=both     # क्यामेरा स्पिकर + PC स्पिकर एकै समयमा
```

#### A) क्यामेरा स्पिकर (go2rtc मार्फत)

`TTS_OUTPUT=remote` (वा `both`) सेट गर्नुहोस्। [go2rtc](https://github.com/AlexxIT/go2rtc/releases) को आवश्यकता छ:

1. [रिलिज पृष्ठ](https://github.com/AlexxIT/go2rtc/releases) बाट बाइनरी डाउनलोड गर्नुहोस्:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. यसलाई राख्नुहोस् र नाम परिवर्तन गर्नुहोस्:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x आवश्यक

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. समान निर्देशिकामा `go2rtc.yaml` सिर्जना गर्नुहोस्:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   स्थानीय क्यामेरा खाता क्रेडेन्सियलहरू प्रयोग गर्नुहोस् (तपाईंको TP-Link क्लाउड खाता होइन)।

4. familiar-ai ले सुरुवातमा स्वचालित रूपमा go2rtc सुरु गर्दछ। यदि तपाईंको क्यामेरामा दुई-तरफको अडियो (ब्याकच्यानल) समर्थन गर्दछ भने, आवाज क्यामेरा स्पिकरबाट खेलिन्छ।

#### B) स्थानीय PC स्पिकर

डिफल्ट (`TTS_OUTPUT=local`)। आदेशमा प्लेयरहरूलाई क्रमशः प्रयास गर्दछ: **paplay** → **mpv** → **ffplay**। जब `TTS_OUTPUT=remote` र go2rtc उपलब्ध छैन तब पनि यो विकल्पको रूपमा प्रयोग गरिन्छ।

| OS | स्थापना |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (वा `paplay` द्वारा `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` मा `PULSE_SERVER=unix:/mnt/wslg/PulseServer` सेट गर्नुहोस् |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — डाउनलोड गर्नुहोस् र PATH मा थप्नुहोस्, **वा** `winget install ffmpeg` |

> यदि कुनै अडियो प्लेयर उपलब्ध छैन भने, आवाज उत्पन्न गरिन्छ — यो मात्र बज्न सक्दैन।

### आवाज इनपुट (Realtime STT)

सधैं-अन, हात-फ्री आवाज इनपुटको लागि `.env` मा `REALTIME_STT=true` सेट गर्नुहोस्:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS सँगको समान कुञ्जी
```

familiar-ai ले ElevenLabs Scribe v2 मा माइकको अडियो प्रवाह गर्दैछ र तपाईं बोल्न रोक्नु भएको बेला स्वचालित रूपमा ट्रान्स्क्रिप्टहरू उपयुक्त गर्दछ। कुनै बटन थिच्नु आवश्यक छैन। यो पुश-टु-टोक मोड (Ctrl+T) सँग सह-अस्तित्वमा हुन्छ।

---

## TUI

familiar-ai ले [Textual](https://textual.textualize.io/) को साथ बनाइएको एक टर्मिनल UI समावेश गर्दछ:

- जीवन्त स्ट्रिमिङ पाठको साथ स्क्रोल योग्य संवाद इतिहास
- `/quit`, `/clear`का लागि ट्याब-पूर्णता
- यो सोच्दा एजेन्टलाई मध्यक्रममा रोक्न किपरले टाइप गर्न
- **संवादको लग** स्वचालित रूपमा `~/.cache/familiar-ai/chat.log` मा बचत गरिन्छ

अर्को टर्मिनलमा लगको अनुसरण गर्न (कपी-पेस्टको लागि उपयोगी):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## व्यक्तित्व (ME.md)

तपाईंको familiarको व्यक्तित्व `ME.md` मा बस्छ। यो फाइल gitignored हो — यो केवल तपाईंको हो।

[`persona-template/en.md`](./persona-template/en.md) को उदाहरणका लागि हेर्नुहोस्, या [`persona-template/ja.md`](./persona-template/ja.md) को जापानी संस्करणका लागि।

---

## अक्सर सोधिने प्रश्नहरू

**Q: यो GPU बिना काम गर्छ?**
हो। एम्बेडिङ मोडेल (multilingual-e5-small) CPU मा ठिक चल्छ। GPU ले यसलाई छिटो बनाउँछ तर आवश्यक छैन।

**Q: के म Tapo भन्दा अन्य क्यामेरा प्रयोग गर्न सक्छु?**
जुनसुकै क्यामेरा जसले ONVIF + RTSP लाई समर्थन गर्छ त्यो काम गर्नुपर्छ। Tapo C220 हामीले परीक्षण गरेका छौँ।

**Q: के मेरो डेटा कहीं पठाइन्छ?**
छविहरू र पाठ तपाईंको चयन गरिएको LLM API मा प्रशोधनको लागि पठाइन्छ। सम्झनाहरू स्थानीय रूपमा `~/.familiar_ai/` मा भण्डारण गरिन्छ।

**Q: एजेन्टले बोल्ने सट्टा `（...）` लेख्छ किन?**
`ELEVENLABS_API_KEY` सेट भएको सुनिश्चित गर्नुहोस्। यस बिना, आवाज निष्क्रिय गरिएको छ र एजेन्टले पाठमा फर्कन्छ।

## प्राविधिक पृष्ठभूमि

यसले कसरी काम गर्दछ भन्ने बारेमा चासो छ? familiar-ai को अनुसन्धान र डिजाईन निर्णयहरूको लागि [docs/technical.md](./docs/technical.md) हेर्नुहोस् — ReAct, SayCan, Reflexion, Voyager, इच्छा प्रणाली, र थप।

---

## योगदान

familiar-ai एक खुला प्रयोग हो। यदि यिनै मध्ये कुनै कुरा तपाईलाई रुचि लाग्यो भने — प्राविधिक वा दार्शनिक रूपमा — योगदानहरू स्वागत छ।

**सुरु गर्नका लागि राम्रो ठाउँहरू:**

| क्षेत्र | के आवश्यक छ |
|------|---------------|
| नयाँ हार्डवेयर | थप क्यामेराहरूको लागि समर्थन (RTSP, IP वेबक्याम), माइक्रोफोन, एक्टुएटर्स |
| नयाँ उपकरणहरू | वेब खोज, घरको स्वचालन, क्यालेन्डर, MCP मार्फत केही पनि |
| नयाँ ब्याकएन्डहरू | कुनैपनि LLM या स्थानीय मोडेल जसले `stream_turn` इन्टरफेसमा फिट हुन्छ |
| व्यक्तित्व टेम्प्लेटहरू | विभिन्न भाषाहरू र व्यक्तित्वका लागि ME.md टेम्प्लेटहरू |
| अनुसन्धान | राम्रो इच्छा मोडेलहरू, मेमोरी पुनःप्राप्ति, मनको सिद्धान्तलाई प्रोत्साहन |
| कागजात | ट्यूटोरियलहरू, मार्गदर्शिकाहरू, अनुवाद |

डिजिटल सेटअप, कोड शैली, र PR दिशानिर्देशहरूको लागि [CONTRIBUTING.md](./CONTRIBUTING.md) हेर्नुहोस्।

यदि तपाईंलाई कसरि सुरु गर्ने कुरामा संदेह छ भने, [एक मुद्दा खोल्नुहोस्](https://github.com/lifemate-ai/familiar-ai/issues) — तपाईंलाई सही दिशामा संकेत गर्न खुसी हुनेछु।

---

## लाइसेन्स

[MIT](./LICENSE)
```
