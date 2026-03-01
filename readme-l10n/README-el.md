# familiar-ai 🐾

**Μια AI που ζει δίπλα σου** — με μάτια, φωνή, πόδια και μνήμη.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Διαθέσιμο σε 74 γλώσσες](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai είναι ένα AI σύντροφος που ζει στο σπίτι σου.
Ρύθμισέ το σε λίγα λεπτά. Δεν απαιτείται προγραμματισμός.

Αντιλαμβάνεται τον πραγματικό κόσμο μέσω καμερών, κινείται σε ένα ρομποτικό σώμα, μιλά δυνατά και θυμάται ό,τι βλέπει. Δώσ' του ένα όνομα, γράψε την προσωπικότητά του και άφησέ το να ζήσει μαζί σου.

## Τι μπορεί να κάνει

- 👁 **Βλέπει** — καταγράφει εικόνες από μια κάμερα Wi-Fi PTZ ή USB webcam
- 🔄 **Κοιτάει γύρω** — περιστρέφει και κλίνει την κάμερα για να εξερευνήσει το περιβάλλον
- 🦿 **Μετακινείται** — οδηγεί μια ρομποτική σκούπα για να περιφέρεται στο δωμάτιο
- 🗣 **Μιλά** — μιλά μέσω ElevenLabs TTS
- 🎙 **Ακούει** — hands-free φωνητική είσοδο μέσω ElevenLabs Realtime STT (opt-in)
- 🧠 **Θυμάται** — αποθηκεύει και ανακαλεί ενεργά μνήμες με σημασιολογική αναζήτηση (SQLite + embeddings)
- 🫀 **Θεωρία του Νου** — παίρνει την προοπτική του άλλου πριν απαντήσει
- 💭 **Επιθυμία** — έχει τους δικούς του εσωτερικούς κινδύνους που προκαλούν αυτόνομη συμπεριφορά

## Πώς λειτουργεί

familiar-ai εκτελεί ένα [ReAct](https://arxiv.org/abs/2210.03629) loop που τροφοδοτείται από την επιλογή LLM που έχεις κάνει. Αντιλαμβάνεται τον κόσμο μέσω εργαλείων, σκέφτεται τι να κάνει στη συνέχεια και ενεργεί — όπως θα έκανε και ένας άνθρωπος.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Όταν είναι ανενεργό, ενεργεί με βάση τις δικές του επιθυμίες: περιέργεια, θέληση να κοίταξει έξω, νοσταλγία για το άτομο με το οποίο ζει.

## Ξεκινώντας

### 1. Εγκατάσταση του uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Ή: `winget install astral-sh.uv`

### 2. Εγκατάσταση του ffmpeg

Το ffmpeg είναι **απαραίτητο** για την καταγραφή εικόνας από την κάμερα και την αναπαραγωγή ήχου.

| OS | Εντολή |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ή κατέβασέ το από [ffmpeg.org](https://ffmpeg.org/download.html) και πρόσθεσέ το στο PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Επιβεβαίωσε: `ffmpeg -version`

### 3. Κλωνοποίηση και εγκατάσταση

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Ρύθμιση

```bash
cp .env.example .env
# Επεξεργάσου το .env με τις ρυθμίσεις σου
```

**Ελάχιστα απαιτούμενα:**

| Μεταβλητή | Περιγραφή |
|----------|-------------|
| `PLATFORM` | `anthropic` (προεπιλογή) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Το API key σου για την επιλεγμένη πλατφόρμα |

**Προαιρετικά:**

| Μεταβλητή | Περιγραφή |
|----------|-------------|
| `MODEL` | Όνομα μοντέλου (λογικές προεπιλογές ανά πλατφόρμα) |
| `AGENT_NAME` | Εμφανιζόμενο όνομα στο TUI (π.χ. `Yukine`) |
| `CAMERA_HOST` | Διεύθυνση IP της ONVIF/RTSP κάμερας σου |
| `CAMERA_USER` / `CAMERA_PASS` | Διαπιστευτήρια κάμερας |
| `ELEVENLABS_API_KEY` | Για φωνητική έξοδο — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` για να ενεργοποιήσεις πάντα ενεργή φωνητική είσοδο (απαιτεί `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Πού να αναπαράγεται ο ήχος: `local` (ηχείο υπολογιστή, προεπιλογή) \| `remote` (ηχείο κάμερας) \| `both` |
| `THINKING_MODE` | Μόνο για Anthropic — `auto` (προεπιλογή) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Προσαρμοσμένη σκέψη: `high` (προεπιλογή) \| `medium` \| `low` \| `max` (μόνο για Opus 4.6) |

### 5. Δημιουργία του φιλικού σου

```bash
cp persona-template/en.md ME.md
# Επεξεργάσου το ME.md — δώσ' του ένα όνομα και προσωπικότητα
```

### 6. Εκτέλεση

**macOS / Linux / WSL2:**
```bash
./run.sh             # Textual TUI (συνιστάται)
./run.sh --no-tui    # Απλός REPL
```

**Windows:**
```bat
run.bat              # Textual TUI (συνιστάται)
run.bat --no-tui     # Απλός REPL
```

---

## Επιλέγοντας ένα LLM

> **Συνιστάται: Kimi K2.5** — η καλύτερη επιτευχθείσα απόδοση μέχρι στιγμής. Αντιλαμβάνεται το περιβάλλον, ζητά επόμενες ερωτήσεις και ενεργεί αυτόνομα με τρόπους που άλλα μοντέλα δεν το κάνουν. Η τιμή της είναι παρόμοια με αυτήν του Claude Haiku.

| Πλατφόρμα | `PLATFORM=` | Μοντέλο προεπιλογής | Πού να αποκτήσεις το key |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Συμβατό με OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (πολυσύνθετη παροχή) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI εργαλείο** (claude -p, ollama…) | `cli` | (η εντολή) | — |

**Παράδειγμα `.env` για Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # από platform.moonshot.ai
AGENT_NAME=Yukine
```

**Παράδειγμα `.env` για Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # από api.z.ai
MODEL=glm-4.6v   # ενεργοποιημένο για όραση; glm-4.7 / glm-5 = μόνο κείμενο
AGENT_NAME=Yukine
```

**Παράδειγμα `.env` για Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # από aistudio.google.com
MODEL=gemini-2.5-flash  # ή gemini-2.5-pro για περισσότερες δυνατότητες
AGENT_NAME=Yukine
```

**Παράδειγμα `.env` για OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # από openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # προαιρετικό: καθόρισε μοντέλο
AGENT_NAME=Yukine
```

> **Σημείωση:** Για να απενεργοποιήσεις τα τοπικά/NVIDIA μοντέλα, απλώς μην ορίσεις το `BASE_URL` σε ένα τοπικό endpoint όπως `http://localhost:11434/v1`. Χρησιμοποίησε παρόχους cloud αντί αυτού.

**Παράδειγμα CLI εργαλείου `.env`:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — χωρίς {}, το prompt περνάει μέσω stdin
```

---

## MCP Servers

familiar-ai μπορεί να συνδεθεί σε οποιοδήποτε [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Αυτό σου επιτρέπει να συνδέσεις εξωτερική μνήμη, πρόσβαση στο filesystem, διαδικτυακή αναζήτηση ή οποιοδήποτε άλλο εργαλείο.

Ρύθμισε τους servers στο `~/.familiar-ai.json` (ίδιο format με το Claude Code):

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

Υποστηρίζονται δύο τύποι μεταφοράς:
- **`stdio`**: ξεκινά έναν τοπικό subprocess (`command` + `args`)
- **`sse`**: συνδέεται σε έναν HTTP+SSE server (`url`)

Αντικατέστησε την τοποθεσία αρχείου ρυθμίσεων με `MCP_CONFIG=/path/to/config.json`.

---

## Υλικό

familiar-ai λειτουργεί με όποιο υλικό έχεις — είτε καθόλου.

| Μέρος | Τι κάνει | Παράδειγμα | Απαραίτητο; |
|------|-------------|---------|-----------|
| Κάμερα Wi-Fi PTZ | Μάτια + λαιμός | Tapo C220 (~$30) | **Συνιστάται** |
| USB webcam | Μάτια (σταθερά) | Οποιαδήποτε κάμερα UVC | **Συνιστάται** |
| Ρομποτική σκούπα | Πόδια | Οποιοδήποτε μοντέλο συμβατό με Tuya | Όχι |
| PC / Raspberry Pi | Εγκέφαλος | Οτιδήποτε τρέχει Python | **Ναι** |

> **Μια κάμερα συνιστάται έντονα.** Χωρίς μία, το familiar-ai μπορεί να μιλήσει — αλλά δεν μπορεί να δει τον κόσμο, που είναι λίγο πολύ το θέμα.

### Ελάχιστη ρύθμιση (χωρίς υλικό)

Απλά θέλεις να το δοκιμάσεις; Χρειάζεσαι μόνο ένα API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Εκτέλεσε `./run.sh` (macOS/Linux/WSL2) ή `run.bat` (Windows) και άρχισε την συνομιλία. Πρόσθεσε υλικό καθώς προχωράς.

### Κάμερα Wi-Fi PTZ (Tapo C220)

1. Στην εφαρμογή Tapo: **Ρυθμίσεις → Ανάπτυξη → Λογαριασμός Κάμερας** — δημιούργησε έναν τοπικό λογαριασμό (όχι λογαριασμό TP-Link)
2. Βρες τη διεύθυνση IP της κάμερας στη λίστα συσκευών του router σου
3. Ρύθμισε στο `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Φωνή (ElevenLabs)

1. Απόκτησε ένα API key στο [elevenlabs.io](https://elevenlabs.io/)
2. Ρύθμισε στο `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # προαιρετικό, χρησιμοποιεί την προεπιλεγμένη φωνή αν παραληφθεί
   ```

Υπάρχουν δύο προορισμοί αναπαραγωγής, ελεγχόμενοι από το `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Ηχείο υπολογιστή (προεπιλογή)
TTS_OUTPUT=remote   # Μόνο ηχείο κάμερας
TTS_OUTPUT=both     # Ηχείο κάμερας + Ηχείο υπολογιστή ταυτόχρονα
```

#### A) Ηχείο κάμερας (μέσω go2rtc)

Ρύθμισε το `TTS_OUTPUT=remote` (ή `both`). Απαιτεί [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Κατέβασε το εκτελέσιμο από την [σελίδα κυκλοφορίας](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Τοποθέτησέ το και μετονομάσέ το:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # απαιτείται chmod +x

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Δημιούργησε το `go2rtc.yaml` στην ίδια τοποθεσία:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Χρησιμοποίησε τα διαπιστευτήρια του τοπικού λογαριασμού κάμερας (όχι το λογαριασμό σου στο cloud της TP-Link).

4. Το familiar-ai ξεκινά αυτόματα το go2rtc κατά την εκκίνηση. Αν η κάμερα υποστηρίζει αμφίδρομη ήχο (backchannel), η φωνή αναπαράγεται από το ηχείο της κάμερας.

#### B) Τοπικό ηχείο υπολογιστή

Η προεπιλογή (`TTS_OUTPUT=local`). Δοκιμάζει παίκτες κατά σειρά: **paplay** → **mpv** → **ffplay**. Χρησιμοποιείται επίσης ως εναλλακτική όταν το `TTS_OUTPUT=remote` και το go2rtc δεν είναι διαθέσιμο.

| OS | Εγκατάσταση |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ή `paplay` μέσω `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — ρύθμισε `PULSE_SERVER=unix:/mnt/wslg/PulseServer` στο `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — κατέβασε και πρόσθεσέ το στο PATH, **ή** `winget install ffmpeg` |

> Αν δεν είναι διαθέσιμος κανένας παίκτης ήχου, η ομιλία εξακολουθεί να παράγεται — απλά δεν θα αναπαράγεται.

### Φωνητική είσοδος (Realtime STT)

Ρύθμισε το `REALTIME_STT=true` στο `.env` για πάντα ενεργή, hands-free φωνητική είσοδο:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # το ίδιο key με το TTS
```

Το familiar-ai ρέει ήχο μικροφώνου προς ElevenLabs Scribe v2 και αυτόματα καταγράφει τις μεταγραφές όταν σταματήσεις να μιλάς. Δεν απαιτείται πίεση κουμπιού. Συμβαδίζει με την λειτουργία push-to-talk (Ctrl+T).

---

## TUI

familiar-ai περιλαμβάνει ένα τερματικό UI που έχει δημιουργηθεί με το [Textual](https://textual.textualize.io/):

- Ικανότητα κύλισης ιστορικού συνομιλίας με ζωντανό ρεύμα κειμένου
- Αυτόματη ολοκλήρωση για `/quit`, `/clear`
- Διακοπή του πράκτορα κατά τη διάρκεια της σκέψης πληκτρολογώντας ενώ σκέφτεται
- **Καταγραφή συνομιλιών** αυτόματα αποθηκευόμενη στο `~/.cache/familiar-ai/chat.log`

Για να παρακολουθήσεις την καταγραφή σε άλλο τερματικό (χρήσιμο για αντιγραφή-επικόλληση):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Προσωπικότητα (ME.md)

Η προσωπικότητα του φιλικού σου βρίσκεται στο `ME.md`. Αυτό το αρχείο είναι gitignored — είναι μόνο δικό σου.

Δες το [`persona-template/en.md`](./persona-template/en.md) για ένα παράδειγμα, ή το [`persona-template/ja.md`](./persona-template/ja.md) για μια Ιαπωνική έκδοση.

---

## Συχνές Ερωτήσεις

**Q: Λειτουργεί χωρίς GPU;**
Ναι. Το μοντέλο embeddings (multilingual-e5-small) λειτουργεί καλά σε CPU. Μια GPU το κάνει πιο γρήγορο αλλά δεν είναι απαραίτητη.

**Q: Μπορώ να χρησιμοποιήσω κάμερα εκτός από την Tapo;**
Οποιαδήποτε κάμερα που υποστηρίζει ONVIF + RTSP θα πρέπει να λειτουργεί. Η Tapo C220 είναι αυτή που δοκιμάσαμε.

**Q: Στέλνονται τα δεδομένα μου οπουδήποτε;**
Οι εικόνες και το κείμενο αποστέλλονται στο API για το επιλεγμένο LLM για επεξεργασία. Οι μνήμες αποθηκεύονται τοπικά στο `~/.familiar_ai/`.

**Q: Γιατί γράφει ο πράκτορας `（...）` αντί να μιλά;**
Βεβαιώσου ότι το `ELEVENLABS_API_KEY` έχει οριστεί. Χωρίς αυτό, η φωνητική έξοδος είναι απενεργοποιημένη και ο πράκτορας επιστρέφει σε κείμενο.

## Τεχνικό Υπόβαθρο

Είσαι περίεργος για το πώς λειτουργεί; Δες το [docs/technical.md](./docs/technical.md) για την έρευνα και τις σχεδιαστικές αποφάσεις πίσω από το familiar-ai — ReAct, SayCan, Reflexion, Voyager, το σύστημα επιθυμιών, και περισσότερα.

---

## Συμμετοχή

Το familiar-ai είναι μια ανοικτή πειραματική πρωτοβουλία. Αν οποιοδήποτε από αυτά αντηχεί μαζί σου — τεχνικά ή φιλοσοφικά — οι συνεισφορές είναι πολύ ευπρόσδεκτες.

**Καλοί τομείς για να ξεκινήσεις:**

| Τομέας | Τι χρειάζεται |
|------|---------------|
| Νέο υλικό | Υποστήριξη για περισσότερες κάμερες (RTSP, IP Webcam), μικρόφωνα, ενεργοποιητές |
| Νέα εργαλεία | Διαδικτυακή αναζήτηση, αυτοματοποίηση σπιτιού, ημερολόγιο, οτιδήποτε μέσω MCP |
| Νέοι backend | Οποιοδήποτε LLM ή τοπικό μοντέλο που ταιριάζει στη διεπαφή `stream_turn` |
| Πρότυπα προσωπικότητας | Πρότυπα ME.md για διαφορετικές γλώσσες και προσωπικότητες |
| Έρευνα | Καλύτερα μοντέλα επιθυμίας, ανάκτηση μνημών, προτροπή θεωρίας του νου |
| Τεκμηρίωση | Μαθήματα, περιγραφές, μεταφράσεις |

Δες το [CONTRIBUTING.md](./CONTRIBUTING.md) για ρυθμίσεις ανάπτυξης, στυλ κώδικα και κατευθυντήριες γραμμές PR.

Αν δεν είσαι σίγουρος πού να ξεκινήσεις, [άνοιξε ένα ζήτημα](https://github.com/lifemate-ai/familiar-ai/issues) — χαρούμενος να σε καθοδηγήσω στην σωστή κατεύθυνση.

---

## Άδεια

[MIT](./LICENSE)
