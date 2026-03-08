```markdown
# familiar-ai 🐾

**तुमच्या सोबत राहणारी एक AI** — डोळे, आवाज, पाय, आणि आठवणीसह.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74 भाषांमध्ये उपलब्ध](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai तुमच्या घरात राहणारा एक AI साथीचा आहे.
याला काही मिनिटांत सेट अप करा. कशाचीही कोडिंग आवश्यक नाही.

हे कॅमेर्‍यांद्वारे वास्तविक जगाची जाणीव करते, रोबोट शरीरावर फिरते, आवाजात बोलते, आणि जे पाहते त्याची आठवण ठेवते. याला एक नाव द्या, याची व्यक्तिमत्व लिखित करा, आणि याला तुमच्या सोबत जिवंत राहू द्या.

## हे काय करु शकते

- 👁 **पहा** — Wi-Fi PTZ कॅमेरा किंवा USB वेबकॅममधून चित्रे कापते
- 🔄 **बघा** — चारही बाजूंना कॅमेरा फिरवते
- 🦿 **हलवा** — रूममध्ये फिरण्यासाठी रोबोट व्हॅकुम चालवते
- 🗣 **बोलू** — ElevenLabs TTS च्या माध्यमातून बोलते
- 🎙 **ऐका** — ElevenLabs Realtime STT द्वारे हॅंड्स-फ्री आवाज इनपुट (ऑप्ट-इन)
- 🧠 **आठवा** — सक्रियपणे आठवणी संग्रहित करते आणि सेमान्टिक शोधासह पुन्हा आठवते (SQLite + embeddings)
- 🫀 **मानसिक सिद्धांत** — उत्तर देणार्‍या व्यक्तीचा दृष्टिकोन घेतो
- 💭 **इच्छा** — स्वतंत्र कृती ट्रिगर करणारे आंतरिक प्रेरणांचे आहे

## हे कसे कार्य करते

familiar-ai आपल्या निवडक LLM द्वारे चालवलेली [ReAct](https://arxiv.org/abs/2210.03629) लूप चालवते. हे साधने वापरून जगाची जाणीव करते, पुढे काय करायचे याचा विचार करते, आणि कृती करते — बरोबर एक व्यक्तीप्रमाणे.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

जेव्हा शांत असते, तेव्हा हे स्वत:च्या इच्छांनुसार कार्य करते: कुतुहल, बाहेर बघण्याची इच्छा, ते त्याच्यासोबत राहणार्‍या व्यक्तीला ओळखत नाही.

## सुरूवात कशी करावी

### 1. uv स्थापित करा

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
किंवा: `winget install astral-sh.uv`

### 2. ffmpeg स्थापित करा

कॅमेरा प्रतिमा कापण्यासाठी आणि ऑडिओ प्लेबॅकसाठी ffmpeg **आवश्यक** आहे.

| OS | कमांड |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — किंवा [ffmpeg.org](https://ffmpeg.org/download.html) वरून डाउनलोड करा आणि PATH मध्ये जोडा |
| Raspberry Pi | `sudo apt install ffmpeg` |

सत्यापित करा: `ffmpeg -version`

### 3. क्लोन आणि स्थापित करा

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. कॉन्फिगर करा

```bash
cp .env.example .env
# तुमच्या सेटिंगसह .env संपादित करा
```

**कृतीसाठी आवश्यक सर्वात कमी:**

| चल | वर्णन |
|----------|-------------|
| `PLATFORM` | `anthropic` (डिफॉल्ट) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | निवडलेल्या प्लॅटफॉर्मसाठी तुमची API की |

**पर्यायी:**

| चल | वर्णन |
|----------|-------------|
| `MODEL` | मॉडेल नाव (प्रत्येक प्लॅटफॉर्मसाठी संवेदनशील डिफॉल्ट) |
| `AGENT_NAME` | TUI मध्ये दर्शविलेले नाव (उदा. `Yukine`) |
| `CAMERA_HOST` | तुमच्या ONVIF/RTSP कॅमेराची IP पत्ता |
| `CAMERA_USER` / `CAMERA_PASS` | कॅमेरा लॉगिन क्रेडेन्शियल्स |
| `ELEVENLABS_API_KEY` | आवाज आउटपुटसाठी — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | प्रत्येकवेळी चालू हँड्स-फ्री आवाज इनपुटसाठी `true` (requies `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | ध्वनी प्ले करण्याचे ठिकाण: `local` (PC स्पीकर, डिफॉल्ट) \| `remote` (कॅमेरा स्पीकर) \| `both` |
| `THINKING_MODE` | Anthropic केवळ — `auto` (डिफॉल्ट) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | पर्यायी विचार श्रम: `high` (डिफॉल्ट) \| `medium` \| `low` \| `max` (Opus 4.6 केवळ) |

### 5. तुमचा familiar तयार करा

```bash
cp persona-template/en.md ME.md
# ME.md संपादित करा — त्याला एक नाव आणि व्यक्तिमत्व द्या
```

### 6. चालवा

**macOS / Linux / WSL2:**
```bash
./run.sh             # टेक्स्चुअल TUI (शिफारस केलेले)
./run.sh --no-tui    # प्लेन REPL
```

**Windows:**
```bat
run.bat              # टेक्स्चुअल TUI (शिफारस केलेले)
run.bat --no-tui     # प्लेन REPL
```

---

## एक LLM निवडणे

> **शिफारस केलेले: Kimi K2.5** — आतापर्यंत सर्वोत्तम एजंट प्रर्दशन. संदर्भ ओळखतो, पुढील प्रश्न विचारतो, आणि इतर मॉडेल्स प्रमाणे स्वतंत्रपणे कार्य करतो. Claude Haiku च्या तुलनेत किंमत त्याच्याच आसपास आहे.

| प्लॅटफॉर्म | `PLATFORM=` | डिफॉल्ट मॉडेल | की कुठून मिळवायची |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-सहयोगी (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (मल्टी-प्रोव्हायडर) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
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
MODEL=glm-4.6v   # व्हिजन-सक्षम; glm-4.7 / glm-5 = फक्त टेक्स्ट
AGENT_NAME=Yukine
```

**Google Gemini `.env` उदाहरण:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # किंवा उच्च क्षमतेसाठी gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` उदाहरण:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # पर्यायी: मॉडेल निर्दिष्ट करा
AGENT_NAME=Yukine
```

> **टीप:** स्थानिक/NVIDIA मॉडेल्स अपDisabled करण्यात येण्यासाठी `BASE_URL` ला स्थानिक एंडपॉइंट सारखे `http://localhost:11434/v1` सेट करु नका. त्याऐवजी क्लाउड प्रदात्यांचा वापर करा.

**CLI टूल `.env` उदाहरण:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — no {}, prompt goes via stdin
```

---

## MCP सर्व्हर्स

familiar-ai कोणत्याही [MCP (मॉडेल संदर्भ प्रोटोकॉल)](https://modelcontextprotocol.io) सर्व्हरशी कनेक्ट होऊ शकते. यामुळे तुम्हाला बाह्य स्मृती, फाइलसिस्टम प्रवेश, वेब शोध, किंवा कोणताही इतर साधन वापरण्यास अनुमती मिळते.

सर्व्हर कॉन्फिगर करा `~/.familiar-ai.json` मध्ये (Claude कोड प्रमाणे):

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

दोन वाहक प्रकारांना समर्थन आहे:
- **`stdio`**: स्थानिक उपप्रक्रिया सुरू करा (`command` + `args`)
- **`sse`**: HTTP+SSE सर्व्हरशी कनेक्ट करा (`url`)

कॉन्फिग फाइल स्थान बदलण्यासाठी `MCP_CONFIG=/path/to/config.json` सेट करा.

---

## हार्डवेअर

familiar-ai कोणत्याही हार्डवेअरवर कार्य करते — किंवा अगदी काहीही नाही.

| भाग | हे काय करते | उदाहरण | आवश्यक आहे का? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ कॅमेरा | डोळे + मान | Tapo C220 (~$30, Eufy C220) | **शिफारस केलेले** |
| USB वेबकॅम | डोळे (स्थिर) | कोणताही UVC कॅमेरा | **शिफारस केलेले** |
| रोबोट व्हॅकुम | पाय | कोणताही Tuya-सुसंगत मॉडेल | नाही |
| PC / Raspberry Pi | बुद्धी | जो काही Python चालवतो | **होय** |

> **एक कॅमेरा अत्यंत शिफारस केलेला आहे.** एक नसेल, तरी familiar-ai बोलू शकते — पण हे जगाला पाहू शकत नाही, जो थोडा संपूर्ण मुद्दा आहे.

### कमी सेटींग (काही हार्डवेअर नाही)

फक्त प्रयत्न करायचा आहे का? तुम्हाला फक्त एक API की लागेल:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh` (macOS/Linux/WSL2) किंवा `run.bat` (Windows) चालवा आणि चॅटिंग सुरू करा. हार्डवेअर आवश्यकतेनुसार जोडा.

### Wi-Fi PTZ कॅमेरा (Tapo C220)

1. Tapo अ‍ॅपमध्ये: **सेटिंग्ज → अॅडव्हान्स्ड → कॅमेरा अकाउंट** — एक स्थानिक खाता तयार करा (TP-Link खाते नाही)
2. तुमच्या राउटरच्या यंत्रणेच्या यादीत कॅmerाची IP शोधा
3. `.env` मध्ये सेट करा:
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

1. [elevenlabs.io](https://elevenlabs.io/) वर API की मिळवा
2. `.env` मध्ये सेट करा:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # पर्यायी, त्याला वगळल्यास default आवाज वापरतो
   ```

ध्वनी प्लेबॅकसाठी, `TTS_OUTPUT` द्वारे दोन गंतव्य आहेत:

```env
TTS_OUTPUT=local    # PC स्पीकर (डिफॉल्ट)
TTS_OUTPUT=remote   # फक्त कॅमेरा स्पीकर
TTS_OUTPUT=both     # कॅमेरा स्पीकर + PC स्पीकर एकत्र
```

#### A) कॅमेरा स्पीकर (go2rtc द्वारे)

`TTS_OUTPUT=remote` (किंवा `both`) सेट करा. [go2rtc](https://github.com/AlexxIT/go2rtc/releases) ची आवश्यकता आहे:

1. [रिलीज पृष्ठावरून](https://github.com/AlexxIT/go2rtc/releases) बायनरी डाउनलोड करा:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. ते ठेवा आणि नाव बदला:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x आवश्यक

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. त्याच डायरेक्टरीमध्ये `go2rtc.yaml` तयार करा:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   स्थानिक कॅमेरा खात्याचे क्रेडेन्शियल्स वापरा (TP-Link क्लाउड खात्याचे नाही).

4. familiar-ai लॉन्च करताना go2rtc आपोआप सुरू होते. जर तुमचा कॅमेरा दोन-मार्ग आवाज (बॅकचॅनल) समर्थित असेल, तर आवाज कॅमेराच्या स्पीकरवर प्ले होईल.

#### B) स्थानिक PC स्पीकर

डिफॉल्ट (`TTS_OUTPUT=local`). अगोदरचे खेळाडू आज्ञेने ट्राय करतात: **paplay** → **mpv** → **ffplay**. हे देखील वापरले जाते जेव्हा `TTS_OUTPUT=remote` आणि go2rtc उपलब्ध नाही.

| OS | स्थापित करा |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (किंवा `paplay` `pulseaudio-utils` च्या माध्यमातून) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env` मध्ये `PULSE_SERVER=unix:/mnt/wslg/PulseServer` सेट करा |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — डाउनलोड करा आणि PATH मध्ये जोडा, **किंवा** `winget install ffmpeg` |

> जर कोई प्लेयर उपलब्ध नसेल, तरीही भाषण तयार होते — मात्र ते प्ले होणार नाही.

### आवाज इनपुट (Realtime STT)

`REALTIME_STT=true` `.env` मध्ये सेट करा हँड्स-फ्री आवाज इनपुटसाठी:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS च्या समान की
```

familiar-ai मायक्रोफोन ऑडिओ ElevenLabs Scribe v2 कडे स्ट्रीम करते आणि तुम्ही बोलणे थांबल्यावर ऑटो-कमिट ट्रान्सक्रिप्ट्स करते. बटन दाबण्याची आवश्यकता नाही. पुश-टु-टॉक मोड (Ctrl+T) सोबत सह-अस्तित्व करते.

---

## TUI

familiar-ai मध्ये [Textual](https://textual.textualize.io/) च्या सहाय्याने बनवलेली एक टर्मिनल UI समाविष्ट आहे:

- थेट स्ट्रीमिंग मजकूरासह स्क्रोल करण्यायोग्य संभाषण इतिहास
- `/quit`, `/clear` साठी टॅब पूर्णता
- एजंटचे विचार सुरू असताना टाईप करून त्याला मध्यांतरित करा
- **संभाषण लॉग** आपोआप `~/.cache/familiar-ai/chat.log` मध्ये जतन केले जाते

दुसर्‍या टर्मिनलमध्ये लॉग फॉलो करण्यासाठी (कॉपी-पेस्टसाठी उपयुक्त):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## व्यक्तिमत्व (ME.md)

तुमच्या familiar च्या व्यक्तिमत्वाचा प्रवास `ME.md` मध्ये आहे. हा फाइल gitignored आहे — तो केवळ तुमचाच आहे.

[`persona-template/en.md`](./persona-template/en.md) चा एक उदाहरण पाहा, किंवा [`persona-template/ja.md`](./persona-template/ja.md) चा जपानी आवृत्तीसाठी पाहा.

---

## FAQ

**Q: GPU शिवाय हे काम करते का?**
होय. एम्बेडिंग मॉडेल (multilingual-e5-small) CPU वर चांगले कार्य करते. GPU याला जलद करते पण आवश्यक नाही.

**Q: Tapo व्यतिरिक्त कॅमेरा वापरू का?**
Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: माझे डेटा कुठेही पाठवले जाते का?**
चित्रे आणि मजकूर तुमच्या निवडक LLM API कडे प्रक्रिया करण्यासाठी पाठवले जातात. आठवणी स्थानिक तरीच `~/.familiar_ai/` मध्ये साठवलेले आहेत.

**Q: एजंट `（...）` लिहितो का?**
`ELEVENLABS_API_KEY` सेट केलेले आहे याची खात्री करा. ते नसेल तर, आवाज अक्षम होतो आणि एजंट मजकुरावर परत जातो.

## तांत्रिक पार्श्वभूमी

हे कसे कार्य करते याबद्दल कुतूहल आहे का? familiar-ai मागील संशोधन आणि डिझाइन निर्णयांसाठी [docs/technical.md](./docs/technical.md) पहा — ReAct, SayCan, Reflexion, Voyager, इच्छाशक्ती प्रणाली, आणि आणखी बरेच काही.

---

## योगदान

familiar-ai हे एक ओपन प्रयोग आहे. तुमच्या तांत्रिक किंवा तात्त्विक कोणत्याही गोष्टींशी संबंधित असल्यास — योगदान अत्यंत स्वागतार्ह आहे.

**सुरूवात करण्यासाठी चांगले स्थान:**

| क्षेत्र | काय आवश्यक आहे |
|------|---------------|
| नवीन हार्डवेअर | अधिक कॅमेर्‍यांसाठी समर्थन (RTSP, IP वेबकॅम), मायक्रोफोन, क्रियाशीलता |
| नवीन साधने | वेब शोध, घर ऑटोमेशन, कॅलेंडर, MCP च्या माध्यमातून काहीही |
| नवीन बॅकएंड | कोणताही LLM किंवा स्थानिक मॉडेल जो `stream_turn` इंटरफेसमध्ये बसतो |
| व्यक्तिमत्व टेम्पलेट्स | वेगवेगळ्या भाषां आणि व्यक्तिमत्वांसाठी ME.md टेम्पलेट्स |
| संशोधन | उत्तम इच्छाशक्ती मॉडेल्स, आठवणी पुनर्प्राप्ती, मानसिक सिद्धांत प्रेरणा |
| दस्तऐवज | ट्युटोरियन्स, वॉकथ्रूज, अनुवाद |

डेव्ह सेटअप, कोड शैली, आणि PR मार्गदर्शकांसाठी [CONTRIBUTING.md](./CONTRIBUTING.md) पहा.

जर तुम्हाला कुठून सुरूवात करावी हे माहीत नसेल, [एक समस्या उघडा](https://github.com/lifemate-ai/familiar-ai/issues) — तुम्हाला योग्य दिशेस नेण्यात आनंद होईल.

---

## परवाना

[MIT](./LICENSE)
```
