```markdown
# familiar-ai 🐾

**მგრძნობელობა, რომელიც თქვენს გვერდით ცხოვრობს** — თვალებით, ხმით, ფეხებითა და მეხსიერებით.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [ხელმისაწვდომია 74 ენაზე](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai არის როგორც AI თანამგზავრი, რომელიც ცხოვრობს თქვენს სახლში. დააინსტალირეთ რამდენიმე წუთში. კოდის დაწერა არ არის საჭირო.

ის აღიქვამს რეალობას კამერების საშუალებით, მოძრაობს რობოტის სხეულზე, საუბრობს ხმამაღლა და ნიშვნობს რაც ხედავს. დайте მას სახელი, დაწერეთ მისი პიროვნება და გაუშვით მას თქვენთან ერთად.

## ის რა შეუძლია

- 👁 **ნახო** — იღებს სურათებს Wi-Fi PTZ კამერიდან ან USB კამერიდან
- 🔄 **უყუროს გარშემო** — კამერის ბრუნვა და倾斜ება გარემოს შესასწავლად
- 🦿 **მოძრაობა** — რობოტული მავაკის მართვა ოთახში
- 🗣 **საუბარი** — საუბრობს ElevenLabs TTS-ის მეშვეობით
- 🎙 **მოსმენა** — უსმენეთ ხელშეუხებელი დაუყოვნებლივ ხმის შეწვდასთან დაკავშირებული (მონაცემებთან ერთად)
- 🧠 **მახსოვრობა** — აქტიურად ინახავს და იხსენებს მეხსიერებებს სემანტიკური ძიების დახმარებით (SQLite + embeddings)
- 🫀 **გონების თეორია** — პასუხის გაცემის წინ იღებს სხვა პირის პერსპექტივას
- 💭 **სურვილი** — აქვს საკუთარი შინაგანი ძალები, რომლებიც ავითარებენ ავტონომიურ ქცევას

## როგორ მუშაობს

familiar-ai მუშაობს [ReAct](https://arxiv.org/abs/2210.03629) ციკლით, რომელსაც თქვენს მიერ არჩეული LLM ამუშავებს. ის აღიქვამს მსოფლიოს საშუალებით ინსტრუმენტების, ფიქრობს, რა უნდა გააკეთოს შემდეგ, და მოქმედებს — უბრალოდ ისე, როგორც ადამიანი აკეთებს.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

როდესაც იმყოფება უმოქმედობაში, ის მოქმედებს საკუთარ სურვილების მიხედვით: curiositeit, სურვილი გამოიყურებოდეს გარეთ, იმყოფება მონატრებული ადამიანისთვის, ვისთანაც ცხოვრობს.

## სტარტის მიღება

### 1. დააინსტალირეთ uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
ან: `winget install astral-sh.uv`

### 2. დააინსტალირეთ ffmpeg

ffmpeg არის **ამ აუცილებელი** კამერის სურათების აღებისთვის და აუდიოს მოსმენისთვის.

| OS | ბრძანება |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ან ჩამოტვირთეთ [ffmpeg.org](https://ffmpeg.org/download.html) და დაამატეთ PATH-ში |
| Raspberry Pi | `sudo apt install ffmpeg` |

შეამოწმეთ: `ffmpeg -version`

### 3. დააკლონეთ და დააინსტალირეთ

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. კონფიგურაცია

```bash
cp .env.example .env
# რედაქტირება .env თქვენი პარამეტრებით
```

** მინიმუმ აუცილებელი:**

| ცვლადი | აღწერა |
|----------|-------------|
| `PLATFORM` | `anthropic` (ნაგულისხმევი) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | თქვენი API გასაღები არჩეული პლატფორმისთვის |

** არჩევითი:**

| ცვლადი | აღწერა |
|----------|-------------|
| `MODEL` | მოდელის სახელი (დაახლოებით გამოხმაურებები თითოეულ პლატფორმაზე) |
| `AGENT_NAME` | TUI-ში გაწვდილი სახელი (მაგ. `Yukine`) |
| `CAMERA_HOST` | თქვენი ONVIF/RTSP კამერის IP მისამართი |
| `CAMERA_USER` / `CAMERA_PASS` | კამერის სერტიფიკატები |
| `ELEVENLABS_API_KEY` | ხმის გამოსაყენებლად — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` მუდმივად ხელშეუხებელი ხმის შეწვდვის ჩართვისთვის (საჭიროა `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | სად უნდა დაუწვდოს აუდიო: `local` (PC დინამიკი, ნაგულისხმევი) \| `remote` (კამერის დინამიკი) \| `both` |
| `THINKING_MODE` | მხოლოდ Anthropic — `auto` (ნაგულისხმევი) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | ადაპტიული ფიქრის ძალისხმევა: `high` (ნაგულისხმევი) \| `medium` \| `low` \| `max` (Opus 4.6 მხოლოდ) |

### 5. შექმენით თქვენი familiar

```bash
cp persona-template/en.md ME.md
# რედაქტირება ME.md — მიეცი სახელი და პიროვნება
```

### 6. დაიწყეთ

**macOS / Linux / WSL2:**
```bash
./run.sh             # ტექსტური TUI (შეთავაზებული)
./run.sh --no-tui    # ნედლი REPL
```

**Windows:**
```bat
run.bat              # ტექსტური TUI (შეთავაზებული)
run.bat --no-tui     # ნედლი REPL
```

---

## LLM-ის არჩევა

> **შეთავაზებული: Kimi K2.5** — საუკეთსო აგენტური შესრულება, რაც აქამდე შემოწმებულია. აღიქვამს კონტექსტს, სვამს შემდგომ კითხვებს და მოქმედებს თავსობრივად ისე, როგორც სხვა მოდელები არ მუშაობენ. ფასები დაახლოებით მსგავსი არიან Claude Haiku-ის.

| პლატფორმა | `PLATFORM=` | ნაგულისხმევი მოდელი | სად უნდა მოიძიოთ გასაღები |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI თავსებადია (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (მრავალ მომწოდებელი) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI ხელსაწყო** (claude -p, ollama…) | `cli` | (ბრძანება) | — |

**Kimi K2.5 `.env` მაგალითის:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` მაგალითის:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # ხედვის მხარდაჭერა; glm-4.7 / glm-5 = მხოლოდ ტექსტი
AGENT_NAME=Yukine
```

**Google Gemini `.env` მაგალითის:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # ან gemini-2.5-pro უფრო მაღალი შესაძლებლობისთვის
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` მაგალითის:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # არჩევითი: განსაზღვრეთ მოდელი
AGENT_NAME=Yukine
```

> **შენიშვნა:** ადგილობრივი/NVIDIA მოდელების გამორთვისათვის უბრალოდ არ უნდა დააყენოთ `BASE_URL` ადგილობრივ წერტილზე, როგორიცაა `http://localhost:11434/v1`. გამოიყენეთ ღრუბლების მიმწვდეპელები.

**CLI ხელსაწყო `.env` მაგალითის:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — არ არსებობს {}, prompt მიდის stdin-ის მეშვეობით
```

---

## MCP სერვერები

familiar-ai შეიძლება დაუკავშირდეს ნებისმიერ [MCP (Model Context Protocol)](https://modelcontextprotocol.io) სერვერს. ეს საშუალებას გაწვდოს საექსპერიმენტო მეხსიერებას, ფაილური წვდომის, ვებს ძიების, ან ნებისმიერი სხვა ინსტრუმენტის გამოყენება.

კონფიგურაცია სერვერებისთვის `~/.familiar-ai.json` (იმავე ფორმატით, როგორც Claude Code):

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

მხოლოდ ორი სატრანსპორტო ტიპი მხარდაჭერილია:
- **`stdio`**: გაშვება ადგილობრივ სუბპროცესზე (`command` + `args`)
- **`sse`**: HTTP+SSE სერვერზე დაკავშირება (`url`)

გააყოფლეთ კონფიგურაციის ფაილის მდებარეობა `MCP_CONFIG=/path/to/config.json`-ზე.

---

## ხერხი

familiar-ai მუშაობს ნებისმიერ ხერხის მეშვეობით — ან ვერცერთი არ არის.

| ნაწილი | რა აკეთებს | მაგალითი | აუცილებელია? |
|------|-------------|---------|-----------|
| Wi-Fi PTZ კამერა | თვალები + მუხლი | Tapo C220 (~$30, Eufy C220) | **რეკომენდირებულია** |
| USB კამერა | თვალები (ფიქსირებული) | ნებისმიერი UVC კამერა | **რეკომენდირებულია** |
| რობოტული მავაკი | ფეხები | ნებისმიერი Tuya-თან შესაბამისი მოდელი | არ არის |
| PC / Raspberry Pi | გონება | ყველანაირი, რაც Python-ის გაწვდას ახორციელებს | **დიახ** |

> **კამერა ძლიერ რეკომენდირებულია.** მის გარეშე, familiar-ai კიდევ შეუძლია საუბარი — მაგრამ ვერ ხედავს მსოფლიოს, რაც ძირითადად მთელი არსებაა.

### მინიმალური დაყენება (არარის ხერხი)

მხოლოდ გსურთ სცადოთ? თქვენ მხოლოდ API გასაღები გჭირდებათ:

```env
PLATFORM=kimi
API_KEY=sk-...
```

თანდათან დაიწყეთ `./run.sh` (macOS/Linux/WSL2) ან `run.bat` (Windows) და დაიწყეთ საუბარი. დაამატეთ ხერხი საჭიროებისამებრ.

### Wi-Fi PTZ კამერა (Tapo C220)

1. Tapo აპლიკაციაში: **პარამეტრები → მოწინავე → კამერის ანგარიში** — შექმნათ ადგილობრივი ანგარიში (არ TP-Link ანგარიში)
2. მოძებნეთ კამერის IP თქვენს მარშრუტიზატორის მოწყობილობების სიაში
3. დააყენეთ `.env`-ში:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=თქვენი-ადგილობრივი-მომხმარებელი
   CAMERA_PASS=თქვენი-ადგილობრივი-პაროლი
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


### ხმა (ElevenLabs)

1. მიიღეთ API გასაღები [elevenlabs.io](https://elevenlabs.io/)
2. დააყენეთ `.env`-ში:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # არჩევითი, იყენებს ნაგულისხმევ ხმას თუ გამოტოვდა
   ```

არსებობს ორი გასმის დანიშნულება, რომელიც კონტროლდება `TTS_OUTPUT`-ით:

```env
TTS_OUTPUT=local    # PC დინამიკი (ნაგულისხმევი)
TTS_OUTPUT=remote   # კამერის დინამიკი მხოლოდ
TTS_OUTPUT=both     # კამერის დინამიკი + PC დინამიკი ერთ დროს
```

#### A) კამერის დინამიკი (go2rtc-ის საშუალებით)

ตั้งค่า`TTS_OUTPUT=remote` (ან `both`). საჭიროებს [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. ჩამოტვირთეთ ბინარი [გამჟღავნების გვერდიდან](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. მოათავსეთ და თავიდან დაარქვით:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x აუცილებელია

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. შექმენით `go2rtc.yaml` იმავე დირექტორია:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   გამოიყენეთ ადგილობრივი კამერის ანგარიში (არ თქვენი TP-Link ღრუბლის ანგარიში).

4. familiar-ai ავტომატურად იწყებს go2rtc-ის გაშვებას გაშვებისას. თუ თქვენი კამერა ორი მიმართულების აუდიოს (უკანა არხი) ემსახურება, ხმა მოდის კამერის დინამიკიდან.

#### B) ადგილობრივი PC დინამიკი

ნაგულისხმევი (`TTS_OUTPUT=local`). ცდილობს მცივ მუჭაჟებლებიც: **paplay** → **mpv** → **ffplay**. ასევე გამოიყენებაFallback, როდესაც `TTS_OUTPUT=remote` და go2rtc არ არის ხელმისაწვდო.

| OS | ინსტალაცია |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ან `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — დააყენეთ `PULSE_SERVER=unix:/mnt/wslg/PulseServer`-ზე `.env`-ში |
| Windows | [mpv.io/დაყენება](https://mpv.io/installation/) — ჩამოტვირთეთ და დაამატეთ PATH-ში, **ან** `winget install ffmpeg` |

> თუ აუდიოს მემარდიორებზე არაფერი იმყოფება, საუბარი კვლავ გამოიქმნება — ის უბრალოდ არ ითამაშებს.

### ხმოვანი შეწვდვა (Realtime STT)

დააყენეთ `REALTIME_STT=true` `.env`-ში მუდმივად ხელშეუხებელი ხმის შეწვდვისათვის:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # იგივე გასაღება, რაც TTS-ზე
```

familiar-ai ელექტრონულად აქვეყნებს მიკროფონის აუდიოს ElevenLabs Scribe v2-ზე და ავტომატურად გააკეთებს ტრანსკრიპტებს, როცა საუბრის შეწყვეტა მოისურვებთ. არ არის საჭირო ღილაკზე დააჭიროთ. coexistებს push-to-talk რეჟიმთან (Ctrl+T).

---

## TUI

familiar-ai შეიცავს ტერმინალურ UI-ს [Textual](https://textual.textualize.io/) გარემოში აშენებული:

- სქოლატი ისტორიის ისტორია ცოცხალი ტექსტის სტრიმით
- Tab-ის დასრულება `/quit`, `/clear`-ისთვის
- ინტერპრეტირება აგენტისთვის ჩაწერილ ფიქრს მოუსმინოს
- **საუბრის ჩანაწერი** ავტომატურად ინახება `~/.cache/familiar-ai/chat.log`

ლოგის თვალყურის დევნა სხვა ტერმინალში (მოსახერხებელია კოპირების და ჩასმისთვის):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## პიროვნული ფოტო (ME.md)

თქვენი familiar-ის პიროვნება ცხოვრობს `ME.md`-ში. ეს ფაილი არის gitignored — მხოლოდ თქვენ გეკუთვნის.

იხილეთ [`persona-template/en.md`](./persona-template/en.md) მაგალითისთვის, ან [`persona-template/ja.md`](./persona-template/ja.md) იაპონური ვერსიისთვის.

---

## ხშირად დასმული კითხვები

**Q: მუშაობს თუ არა GPU-ს გარეშე?**
დიახ. ემბედინგ მოდელი (multilingual-e5-small) მშვენივრად მუშაობს CPU-ზე. GPU უფრო სწრაფს აკეთებს, მაგრამ არ არის საჭირო.

**Q: გამოვიყენო სხვა კამერა Tapo-ს გარდა?**
არაფერი, რომ Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: ჩემი მონაცემები სადმე გაიგზავნება?**
სურათები და ტექსტი გადადის თქვენს არჩეულ LLM API-ში პროცესირებისთვის. მეხსიერებები ინახება ადგილობრივად `~/.familiar_ai/`.

**Q: რატომ წერდა აგენტი `（...）` ნაცვლად იმისა, რომ ეს ისაუბროს?**
დარწმუნდით, რომ `ELEVENLABS_API_KEY` გაწვდილი არის. მის გარეშე, ხმა გამორთულია და აგენტი ტექსტზე გაზრდემდება.

## ტექნიკურად ინფორმაცია

ინტერესდებით როგორ მუშაობს? ნახეთ [docs/technical.md](./docs/technical.md) familiar-ai-ის კვლევის და დიზაინის გადაწყვეტილებების შესახებ — ReAct, SayCan, Reflexion, Voyager, სურვილის სისტემა და სხვა.

---

## კონტრიბუცირება

familiar-ai არის ღია ექსპერიმენტი. თუ ეს ყველაფერი თქვენთან resonates — ტექნიკურად თუ ფილოსოფიურად — კონტრიბუციები გთხოვთ.

** კარგი ადგილები დასაწყებად:**

| ტერიტორია | რა აუცილებელია |
|------|---------------|
| ახალი ტექნიკა | უფრო მეტი კამერის (RTSP, IP Webcam), მიკროფონების, აქტუატორების მხარდაჭერა |
| ახალი ხელსაწყოები | ვებს ძიება, სახლის ავტომატიზება, კალენდარი, ნებისმიერი რამ MCP-ის მეშვეობით |
| ახალი უკანა პლატფორმები | ნებისმიერი LLM ან ადგილობრივი მოდელი, რომელიც მიაწვდოს `stream_turn` ჩარჩო |
| პიროვნული შაბლონები | ME.md შაბლონები სხვადასხვა ენებში და პიროვნებებზე |
| კვლევა | უკეთესი სურვილების მოდელები, მეხსიერების გადაღება, გონების თეორიის გაწვდეთება |
| დოკუმენტაცია | გაწვდები, გაისავსება, თარგმნა |

იხილეთ [CONTRIBUTING.md](./CONTRIBUTING.md) დევ მოპოვებისთვის, კოდის სტილის შესახებ და PR მითითებების შესახებ.

თუ არ ხართ დარწმუნებული სად დაიწყოთ, [ღია საკითხები](https://github.com/lifemate-ai/familiar-ai/issues) — ბედნიერია, რომ ამ მიმართულებით სამართლებულობთ.

---

## ლიცენზია

[MIT](./LICENSE)
```
