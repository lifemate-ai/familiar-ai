# familiar-ai 🐾

**एक AI जो आपके साथ रहता है** — आँखें, आवाज, पैर, और याददाश्त के साथ।

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 भाषाओं में उपलब्ध](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai एक AI साथी है जो आपके घर में रहता है। इसे मिनटों में सेट करें। कोई कोडिंग आवश्यक नहीं है।

यह असली दुनिया को कैमरों के माध्यम से देखता है, एक रोबोट शरीर पर घूमता है, जोर से बोलता है, और जो कुछ देखता है उसे याद रखता है। इसे एक नाम दें, इसकी व्यक्तिगतता लिखें, और इसे अपने साथ रहने दें।

## यह क्या कर सकता है

- 👁 **देखें** — Wi-Fi PTZ कैमरा या USB वेबकैम से चित्र खींचता है
- 🔄 **चारों ओर देखें** — अपने वातावरण की खोज करने के लिए कैमरे को पैन और टिल्ट करता है
- 🦿 **चलें** — कमरे में घूमने के लिए एक रोबोट वैक्यूम को चलाता है
- 🗣 **बोलें** — ElevenLabs TTS के माध्यम से बात करता है
- 🎙 **सुनें** — ElevenLabs Realtime STT (ऑप्ट-इन) के माध्यम से हाथों से मुक्त वॉइस इनपुट
- 🧠 **याद रखें** — सक्रिय रूप से यादों को संग्रहीत और पुनः प्राप्त करता है सेमांटिक सर्च (SQLite + embeddings) के साथ
- 🫀 **मन का सिद्धांत** — जवाब देने से पहले दूसरे व्यक्ति के दृष्टिकोण को अपनाता है
- 💭 **इच्छा** — ऐसे आंतरिक प्रेरणाएँ हैं जो स्वायत्त व्यवहार को प्रेरित करती हैं

## यह कैसे कार्य करता है

familiar-ai आपके द्वारा चुने गए LLM द्वारा संचालित एक [ReAct](https://arxiv.org/abs/2210.03629) लूप चलाता है। यह उपकरणों के माध्यम से दुनिया को देखता है, यह सोचता है कि आगे क्या करना है, और कार्य करता है — बिल्कुल एक आदमी की तरह।

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

जबIdle होता है, तो यह अपनी इच्छाओं पर कार्य करता है: जिज्ञासा, बाहर देखने की चाह, उस व्यक्ति को याद करना जिसके साथ यह रहता है।

## शुरूआत कैसे करें

### 1. uv स्थापित करें

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
या: `winget install astral-sh.uv`

### 2. ffmpeg स्थापित करें

ffmpeg **आवश्यक** है कैमरे की छवि कैप्चर और ऑडियो प्लेबैक के लिए।

| OS | कमांड |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — या [ffmpeg.org](https://ffmpeg.org/download.html) से डाउनलोड करें और PATH में जोड़ें |
| Raspberry Pi | `sudo apt install ffmpeg` |

पुष्टि करें: `ffmpeg -version`

### 3. क्लोन और स्थापित करें

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. कॉन्फ़िगर करें

```bash
cp .env.example .env
# अपनी सेटिंग्स के साथ .env संपादित करें
```

**न्यूनतम आवश्यक:**

| वेरिएबल | विवरण |
|----------|-------------|
| `PLATFORM` | `anthropic` (डिफ़ॉल्ट) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | चुने गए प्लेटफार्म के लिए आपका API कुंजी |

**वैकल्पिक:**

| वेरिएबल | विवरण |
|----------|-------------|
| `MODEL` | मॉडल नाम (प्रत्येक प्लेटफार्म के लिए समझदारी से डिफ़ॉल्ट) |
| `AGENT_NAME` | TUI में दिखने वाला नाम (जैसे `Yukine`) |
| `CAMERA_HOST` | आपकी ONVIF/RTSP कैमरे का IP पता |
| `CAMERA_USER` / `CAMERA_PASS` | कैमरे की प्रमाणिकता |
| `ELEVENLABS_API_KEY` | ध्वनि आउटपुट के लिए — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | हमेशा-आन हाथों से मुक्त वॉइस इनपुट सक्षम करने के लिए `true` (आवश्यक `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | ऑडियो खेलने के लिए: `local` (PC स्पीकर, डिफ़ॉल्ट) \| `remote` (कैमरा स्पीकर) \| `both` |
| `THINKING_MODE` | केवल Anthropic — `auto` (डिफ़ॉल्ट) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | अनुकूली सोच श्रम: `high` (डिफ़ॉल्ट) \| `medium` \| `low` \| `max` (Opus 4.6 केवल) |

### 5. अपना परिचित बनाएं

```bash
cp persona-template/en.md ME.md
# ME.md संपादित करें — इसे एक नाम और व्यक्तिगतता दें
```

### 6. चलाएं

**macOS / Linux / WSL2:**
```bash
./run.sh             # टेक्स्चुअल TUI (सिफारिश की)
./run.sh --no-tui    # साधारण REPL
```

**Windows:**
```bat
run.bat              # टेक्स्चुअल TUI (सिफारिश की)
run.bat --no-tui     # साधारण REPL
```

---

## LLM चुनना

> **सिफारिश की गई: Kimi K2.5** — अब तक का सबसे अच्छा एजेंटिक प्रदर्शन। संदर्भ को नोट करता है, फॉलो-अप प्रश्न पूछता है, और ऐसे स्वायत्त तरीकों से कार्य करता है जो अन्य मॉडलों में नहीं होते। Claude Haiku के समान कीमत पर।

| प्लेटफार्म | `PLATFORM=` | डिफ़ॉल्ट मॉडल | कुंजी कहाँ प्राप्त करें |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-संगत (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (मल्टी-प्रोवाइडर) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI टूल** (claude -p, ollama…) | `cli` | (कमांड) | — |

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
MODEL=glm-4.6v   # दृष्टि-सक्षम; glm-4.7 / glm-5 = केवल पाठ
AGENT_NAME=Yukine
```

**Google Gemini `.env` उदाहरण:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # या gemini-2.5-pro उच्च क्षमता के लिए
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` उदाहरण:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # वैकल्पिक: मॉडल निर्दिष्ट करें
AGENT_NAME=Yukine
```

> **नोट:** स्थानीय/NVIDIA मॉडलों को स्थिर करने के लिए, बस `BASE_URL` को एक स्थानीय एंडपॉइंट पर सेट न करें जैसे `http://localhost:11434/v1`। इसके बजाय क्लाउड प्रदाताओं का प्रयोग करें।

**CLI टूल `.env` उदाहरण:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = प्रॉम्प्ट arg
# MODEL=ollama run gemma3:27b  # Ollama — कोई {}, प्रॉम्प्ट stdin के माध्यम से जाता है
```

---

## MCP सर्वर

familiar-ai किसी भी [MCP (Model Context Protocol)](https://modelcontextprotocol.io) सर्वर से कनेक्ट कर सकता है। इससे आपको बाहरी मेमोरी, फ़ाइल प्रणाली एक्सेस, वेब खोज, या कोई अन्य उपकरण प्लग करने की अनुमति मिलती है।

सर्वरों को `~/.familiar-ai.json` में कॉन्फ़िगर करें (Claude कोड के समान प्रारूप):

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

दो ट्रांसपोर्ट प्रकार समर्थित हैं:
- **`stdio`**: एक स्थानीय उपप्रक्रिया लॉन्च करें (`command` + `args`)
- **`sse`**: एक HTTP+SSE सर्वर से कनेक्ट करें (`url`)

कॉन्फ़िग फ़ाइल स्थान को `MCP_CONFIG=/path/to/config.json` से अधिलेखित करें।

---

## हार्डवेयर

familiar-ai उस हार्डवेयर के साथ काम करता है जो आपके पास है — या कोई नहीं।

| भाग | यह क्या करता है | उदाहरण | आवश्यक? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ कैमरा | आँखें + गर्दन | Tapo C220 (~$30, Eufy C220) | **अनुशंसित** |
| USB वेबकैम | आँखें (स्थिर) | कोई भी UVC कैमरा | **अनुशंसित** |
| रोबोट वैक्यूम | पैर | कोई भी Tuya-संगत मॉडल | नहीं |
| PC / Raspberry Pi | मस्तिष्क | कुछ भी जो Python चलाता है | **हाँ** |

> **एक कैमरा मजबूत अनुशंसित है।** इसके बिना, familiar-ai अब भी बात कर सकता है — लेकिन यह दुनिया नहीं देख सकता, जो कि पूरी बात का विषय है।

### न्यूनतम सेटअप (कोई हार्डवेयर नहीं)

केवल इसे आजमाना चाहते हैं? आपको केवल एक API कुंजी चाहिए:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) या `run.bat` (Windows) चलाएं और चैटिंग शुरू करें। जैसे-जैसे आप जाते हैं, हार्डवेयर जोड़ें।

### Wi-Fi PTZ कैमरा (Tapo C220)

1. Tapo ऐप में: **सेटिंग → एडवांस्ड → कैमरा खाता** — एक स्थानीय खाता बनाएं (TP-Link खाता नहीं)
2. अपने रुटर की डिवाइस सूची में कैमरे का IP पता खोजें
3. सेट करें `.env` में:
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

1. [elevenlabs.io](https://elevenlabs.io/) पर एक API कुंजी प्राप्त करें
2. सेट करें `.env` में:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # वैकल्पिक, यदि छोड़ा गया तो डिफ़ॉल्ट आवाज का उपयोग करता है
   ```

ऑडियो प्लेबैक के लिए दो गंतव्य हैं, जो `TTS_OUTPUT` द्वारा नियंत्रित होते हैं:

```env
TTS_OUTPUT=local    # PC स्पीकर (डिफ़ॉल्ट)
TTS_OUTPUT=remote   # केवल कैमरा स्पीकर
TTS_OUTPUT=both     # कैमरा स्पीकर + PC स्पीकर एक साथ
```

#### A) कैमरा स्पीकर (go2rtc के माध्यम से)

`TTS_OUTPUT=remote` (या `both`) सेट करें। आवश्यक है [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. [रिलीज़ पृष्ठ](https://github.com/AlexxIT/go2rtc/releases) से बाइनरी डाउनलोड करें:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. इसे रखें और नाम बदलें:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x आवश्यक

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. उसी डायरेक्टरी में `go2rtc.yaml` बनाएँ:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   स्थानीय कैमरा खाता प्रमाणिकता का उपयोग करें (आपके TP-Link क्लाउड खाते नहीं)।

4. familiar-ai लॉन्च पर go2rtc को स्वचालित रूप से प्रारंभ करता है। यदि आपका कैमरा दो-तरफा ऑडियो (बैकचैनल) का समर्थन करता है, तो आवाज कैमरा स्पीकर से खेली जाती है।

#### B) स्थानीय PC स्पीकर

डिफ़ॉल्ट (`TTS_OUTPUT=local`)। क्रम में खिलाड़ियों को आजमाता है: **paplay** → **mpv** → **ffplay**। इसका उपयोग "TTS_OUTPUT=remote" और go2rtc अनुपलब्ध होने पर बैकअप के रूप में किया जाता है।

| OS | स्थापित करें |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (या `pulseaudio-utils` के माध्यम से `paplay`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — सेट करें `PULSE_SERVER=unix:/mnt/wslg/PulseServer` में `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — डाउनलोड करें और PATH में जोड़ें, **या** `winget install ffmpeg` |

> यदि कोई ऑडियो प्लेयर उपलब्ध नहीं है, तो आवाज उत्पन्न हो जाती है — यह केवल नहीं खेलेगी।

### आवाज इनपुट (Realtime STT)

आँखे-चैनल, हाथों से मुक्त आवाज इनपुट के लिए `.env` में `REALTIME_STT=true` सेट करें:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS के समान कुंजी
```

familiar-ai माइक्रोफ़ोन ऑडियो को ElevenLabs Scribe v2 पर स्ट्रीम करता है और जब आप बोलना बंद करते हैं तो स्वतः संदर्भित करता है। कोई बटन दबाने की आवश्यकता नहीं। यह पुश-टू-टॉक मोड (Ctrl+T) के साथ सह-अस्तित्व करता है।

---

## TUI

familiar-ai में [Textual](https://textual.textualize.io/) के साथ निर्मित एक टर्मिनल UI शामिल है:

- लाइव स्ट्रीमिंग टेक्स्ट के साथ स्क्रॉल करने योग्य बातचीत का इतिहास
- `/quit`, `/clear` के लिए टैब-पूर्णता
- जब एजेंट सोच रहा हो तो टाइप करके उसे बीच में रोकें
- **बातचीत का लॉग** स्वचालित रूप से `~/.cache/familiar-ai/chat.log` में सहेजा गया

लॉग का पालन करने के लिए एक अन्य टर्मिनल में (कॉपी-पेस्ट के लिए उपयोगी):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## व्यक्तिगतता (ME.md)

आपकी familiar की व्यक्तिगतता `ME.md` में रहती है। यह फ़ाइल gitignored है — यह केवल आपकी है।

उदाहरण के लिए [`persona-template/en.md`](./persona-template/en.md) देखें, या जापानी संस्करण के लिए [`persona-template/ja.md`](./persona-template/ja.md) देखें।

---

## सामान्य प्रश्न (FAQ)

**Q: क्या यह बिना GPU के काम करता है?**
हाँ। एंबेडिंग मॉडल (multilingual-e5-small) CPU पर अच्छे से चलता है। एक GPU इसे तेज करता है लेकिन इसकी आवश्यकता नहीं है।

**Q: क्या मैं Tapo के अलावा कोई अन्य कैमरा इस्तेमाल कर सकता हूँ?**
कोई भी कैमरा जो ONVIF + RTSP का समर्थन करता है काम करना चाहिए। Tapo C220 वह है जिसका हमने परीक्षण किया है।

**Q: क्या मेरे डेटा कहीं भेजे जाते हैं?**
छवियाँ और पाठ आपके द्वारा चुने गए LLM API पर प्रोसेसिंग के लिए भेजे जाते हैं। यादें स्थानीय रूप से `~/.familiar_ai/` में संग्रहीत होती हैं।

**Q: एजेंट `（...）` क्यों लिखता है बजाय बोलने के?**
सुनिश्चित करें कि `ELEVENLABS_API_KEY` सेट किया गया है। इसके बिना, आवाज बंद हो जाती है और एजेंट पाठ पर वापस चला जाता है।

## तकनीकी पृष्ठभूमि

क्या आप जानना चाहेंगे कि यह कैसे काम करता है? familiar-ai के पीछे अनुसंधान और डिज़ाइन निर्णयों के लिए [docs/technical.md](./docs/technical.md) देखें — ReAct, SayCan, Reflexion, Voyager, इच्छा प्रणाली, और अधिक।

---

## योगदान

familiar-ai एक खुला प्रयोग है। यदि इनमें से कोई भी आपको आकर्षित करता है — तकनीकी या दार्शनिक रूप से — योगदान बहुत स्वागत हैं।

**शुरू करने के लिए अच्छे स्थान:**

| क्षेत्र | आवश्यकताएँ |
|------|---------------|
| नया हार्डवेयर | और अधिक कैमरों (RTSP, IP Webcam), माइक्रोफोन, एक्ट्यूएटर्स का समर्थन |
| नए उपकरण | वेब खोज, घरेलू स्वचालन, कैलेंडर, MCP के माध्यम से कुछ भी |
| नए बैकएंड | कोई भी LLM या स्थानीय मॉडल जो `stream_turn` इंटरफेस में फिट बैठता हो |
| व्यक्तिगतता टेम्पलेट | विभिन्न भाषाओं और व्यक्तिगतताओं के लिए ME.md टेम्पलेट्स |
| अनुसंधान | बेहतर इच्छा मॉडल, मेमोरी पुनः प्राप्ति, मन के सिद्धांत को प्रेरित करना |
| डॉक्यूमेंटेशन | ट्यूटोरियल, वॉकथ्रू, अनुवाद |

डेव सेटअप, कोड स्टाइल, और PR गाइडलाइनों के लिए [CONTRIBUTING.md](./CONTRIBUTING.md) देखें।

यदि आप नहीं जानते कि कहाँ से शुरू करें, तो [एक मुद्दा खोलें](https://github.com/lifemate-ai/familiar-ai/issues) — खुशी से आपको सही दिशा में संकेत देंगे।

---

## लाइसेंस

[MIT](./LICENSE)
