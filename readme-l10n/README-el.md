# familiar-ai 🐾

**Μια AI που ζει δίπλα σου** — με μάτια, φωνή, πόδια και μνήμη.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai είναι μια AI σύντροφος που ζει στο σπίτι σου. Ρύθμισέ το σε λίγα λεπτά. Χωρίς να απαιτείται προγραμματισμός.

Αντιλαμβάνεται τον πραγματικό κόσμο μέσω καμερών, κινείται σε ένα ρομποτικό σώμα, μιλάει δυνατά και θυμάται ό,τι βλέπει. Δώσε του ένα όνομα, γράψε την προσωπικότητά του και άφησέ το να ζήσει μαζί σου.

## Τι μπορεί να κάνει

- 👁 **Βλέπει** — καταγράφει εικόνες από μια κάμερα Wi-Fi PTZ ή USB webcam
- 🔄 **Κοιτάει γύρω** — γυρίζει και κλίνει την κάμερα για να εξερευνήσει τον περίγυρο
- 🦿 **Κινείται** — κινεί έναν ρομποτικό σκουπιστή για να περιφέρεται στο δωμάτιο
- 🗣 **Μιλάει** — συνομιλεί μέσω ElevenLabs TTS
- 🎙 **Ακούει** — φωνητική είσοδος hands-free μέσω ElevenLabs Realtime STT (opt-in)
- 🧠 **Θυμάται** — αποθηκεύει και ανακαλεί ενεργητικά μνήμες με σημασιολογική αναζήτηση (SQLite + embeddings)
- 🫀 **Θεωρία του Νου** — λαμβάνει την προοπτική του άλλου ατόμου πριν απαντήσει
- 💭 **Επιθυμία** — έχει τους δικούς του εσωτερικούς κινδύνους που προκαλούν αυτόνομη συμπεριφορά

## Πώς λειτουργεί

familiar-ai τρέχει έναν [ReAct](https://arxiv.org/abs/2210.03629) κύκλο που τροφοδοτείται από την επιλογή σου για LLM. Αντιλαμβάνεται τον κόσμο μέσω εργαλείων, σκέφτεται τι να κάνει στη συνέχεια και ενεργεί — ακριβώς όπως θα έκανε ένα άτομο.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Όταν είναι ανενεργό, ενεργεί με βάση τις δικές του επιθυμίες: περιέργεια, επιθυμία να κοιτάξει έξω, νοσταλγία για το άτομο με το οποίο ζει.

## Ξεκινώντας

### 1. Εγκατάσταση uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Εγκατάσταση ffmpeg

Το ffmpeg είναι **υποχρεωτικό** για την καταγραφή εικόνων από κάμερες και την αναπαραγωγή ήχου.

| OS | Εντολή |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ή κατέβασε από [ffmpeg.org](https://ffmpeg.org/download.html) και πρόσθεσέ το στο PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Επιβεβαίωση: `ffmpeg -version`

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

**Ελάχιστες απαιτήσεις:**

| Μεταβλητή | Περιγραφή |
|----------|-------------|
| `PLATFORM` | `anthropic` (προεπιλεγμένο) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Το API key σου για την επιλεγμένη πλατφόρμα |

**Προαιρετικά:**

| Μεταβλητή | Περιγραφή |
|----------|-------------|
| `MODEL` | Όνομα μοντέλου (λογικές προεπιλογές ανά πλατφόρμα) |
| `AGENT_NAME` | Όνομα εμφάνισης που εμφανίζεται στην TUI (π.χ. `Yukine`) |
| `CAMERA_HOST` | Διεύθυνση IP της κάμερας ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Διαπιστευτήρια της κάμερας |
| `ELEVENLABS_API_KEY` | Για φωνητική έξοδο — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` για να ενεργοποιήσεις τη φωνητική είσοδο hands-free (απαιτείται `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Πού να αναπαράγεται ο ήχος: `local` (ηχεία υπολογιστή, προεπιλεγμένο) \| `remote` (ηχείο κάμερας) \| `both` |
| `THINKING_MODE` | Μόνο για Anthropic — `auto` (προεπιλεγμένο) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Προσαρμοσμένη προσπάθεια σκέψης: `high` (προεπιλεγμένο) \| `medium` \| `low` \| `max` (μόνο Opus 4.6) |

### 5. Δημιουργία του οικείου σου

```bash
cp persona-template/en.md ME.md
# Επεξεργάσου το ME.md — δώσε του ένα όνομα και προσωπικότητα
```

### 6. Εκτέλεση

```bash
./run.sh             # Κειμενική TUI (συνιστάται)
./run.sh --no-tui    # Απλή REPL
```

---

## Επιλέγοντας ένα LLM

> **Συνιστάται: Kimi K2.5** — η καλύτερη επιδότηση που έχει δοκιμαστεί μέχρι στιγμής. Αντιλαμβάνεται το πλαίσιο, задаёт επόμενα ερωτήματα και ενεργεί αυτόνομα με τρόπους που άλλα μοντέλα δεν το κάνουν. Η τιμή του είναι παρόμοια με αυτή του Claude Haiku.

| Πλατφόρμα | `PLATFORM=` | Προεπιλεγμένο μοντέλο | Πού να πάρεις το κλειδί |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (the command) | — |

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
MODEL=glm-4.6v   # με δυνατότητα όρασης; glm-4.7 / glm-5 = μόνο κείμενο
AGENT_NAME=Yukine
```

**Παράδειγμα `.env` για Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # από aistudio.google.com
MODEL=gemini-2.5-flash  # ή gemini-2.5-pro για υψηλότερη ικανότητα
AGENT_NAME=Yukine
```

**Παράδειγμα `.env` για OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # από openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # προαιρετικό: καθορίστε το μοντέλο
AGENT_NAME=Yukine
```

> **Σημείωση:** Για να απενεργοποιήσεις τα τοπικά/NVIDIA μοντέλα, απλώς μην ορίσεις `BASE_URL` σε τοπικό endpoint όπως `http://localhost:11434/v1`. Χρησιμοποίησε παρόχους cloud αντ' αυτού.

**Παράδειγμα `.env` για CLI tool:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — χωρίς {}, prompt goes via stdin
```

---

## MCP Servers

familiar-ai μπορεί να συνδεθεί σε οποιονδήποτε [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Αυτό σου επιτρέπει να ενσωματώσεις εξωτερική μνήμη, πρόσβαση σε σύστημα αρχείων, διαδικτυακή αναζήτηση ή οποιοδήποτε άλλο εργαλείο.

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
- **`stdio`**: εκκίνηση ενός τοπικού υποδιεργαστή (`command` + `args`)
- **`sse`**: σύνδεση σε έναν HTTP+SSE server (`url`)

Αντικατέστησε την τοποθεσία του αρχείου ρυθμίσεων με `MCP_CONFIG=/path/to/config.json`.

---

## Υλικό

familiar-ai λειτουργεί με οποιοδήποτε υλικό έχεις — ή και καθόλου.

| Τμήμα | Τι κάνει | Παράδειγμα | Απαραίτητο; |
|------|-------------|---------|-----------|
| Wi-Fi PTZ camera | Μάτια + λαιμός | Tapo C220 (~$30) | **Συνιστάται** |
| USB webcam | Μάτια (σταθερή) | Οποιαδήποτε UVC κάμερα | **Συνιστάται** |
| Robot vacuum | Πόδια | Οποιοδήποτε μοντέλο συμβατό με Tuya | Όχι |
| PC / Raspberry Pi | Εγκέφαλος | Οτιδήποτε τρέχει Python | **Ναι** |

> **Μια κάμερα συνιστάται έντονα.** Χωρίς μία, το familiar-ai μπορεί να μιλήσει — αλλά δεν μπορεί να δει τον κόσμο, που είναι κάπως το νόημα.

### Ελάχιστη ρύθμιση (χωρίς υλικό)

Θέλεις απλώς να το δοκιμάσεις; Χρειάζεσαι μόνο ένα API key:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Εκτέλεσε το `./run.sh` και άρχισε να συνομιλείς. Πρόσθεσε υλικό όσο προχωράς.

### Wi-Fi PTZ camera (Tapo C220)

1. Στην εφαρμογή Tapo: **Ρυθμίσεις → Προχωρημένες → Λογαριασμός Κάμερας** — δημιούργησε έναν τοπικό λογαριασμό (όχι TP-Link λογαριασμό)
2. Βρες τη διεύθυνση IP της κάμερας στη λίστα συσκευών του router σου
3. Ορίστε στο `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Φωνή (ElevenLabs)

1. Πάρε ένα API key από [elevenlabs.io](https://elevenlabs.io/)
2. Ορίστε στο `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # προαιρετικό, χρησιμοποιεί την προεπιλεγμένη φωνή αν παραληφθεί
   ```

Υπάρχουν δύο προορισμοί αναπαραγωγής, που ελέγχονται από το `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # ηχείο υπολογιστή (προεπιλεγμένο)
TTS_OUTPUT=remote   # μόνο ηχείο κάμερας
TTS_OUTPUT=both     # ηχείο κάμερας + ηχείο υπολογιστή ταυτόχρονα
```

#### Α) Ηχείο κάμερας (μέσω go2rtc)

Ορίστε το `TTS_OUTPUT=remote` (ή `both`). Απαιτεί [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Κατέβασε το εκτελέσιμο αρχείο από την [σελίδα κυκλοφορίας](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Τοποθέτησέ το και μετονομάσέ το:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x απαιτείται

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Δημιούργησε το `go2rtc.yaml` στην ίδια τοποθεσία:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Χρησιμοποίησε τα διαπιστευτήρια του τοπικού λογαριασμού της κάμερας (όχι τον λογαριασμό cloud TP-Link σου).

4. Το familiar-ai ξεκινά αυτόματα το go2rtc κατά την εκκίνηση. Αν η κάμερά σου υποστηρίζει δύο κατευθύνσεις ήχου (backchannel), η φωνή αναπαράγεται από το ηχείο της κάμερας.

#### Β) Ηχείο υπολογιστή

Η προεπιλογή (`TTS_OUTPUT=local`). Προσπαθεί παίκτες με τη σειρά: **paplay** → **mpv** → **ffplay**. Χρησιμοποιείται επίσης ως εναλλακτική όταν το `TTS_OUTPUT=remote` και το go2rtc δεν είναι διαθέσιμο.

| OS | Εγκατάσταση |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ή `paplay` μέσω `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — ορίστε `PULSE_SERVER=unix:/mnt/wslg/PulseServer` στο `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — κατέβασε και πρόσθεσέ το στο PATH, **ή** `winget install ffmpeg` |

> Αν δεν είναι διαθέσιμος κανένας παίκτης ήχου, η ομιλία εξακολουθεί να δημιουργείται — απλώς δεν θα αναπαραχθεί.

### Φωνητική είσοδος (Realtime STT)

Ορίστε `REALTIME_STT=true` στο `.env` για συνεχή, hands-free φωνητική είσοδο:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # το ίδιο κλειδί όπως το TTS
```

Το familiar-ai μεταδίδει ήχο μικροφώνου στο ElevenLabs Scribe v2 και αυτομάτως δεσμεύει τις μεταγραφές όταν σταματάς να μιλάς. Χρειάζεται να πιέσεις κανένα κουμπί. Συνυπάρχει με την push-to-talk λειτουργία (Ctrl+T).

---

## TUI

familiar-ai περιλαμβάνει μια διεπαφή terminal που έχει δημιουργηθεί με [Textual](https://textual.textualize.io/):

- Ιστορικό συνομιλιών με δυνατότητα scroll με ζωντανό κείμενο
- Συμπλήρωση με tab για `/quit`, `/clear`
- Διακοπή της αγνής λειτουργίας με το να πληκτρολογείς ενώ σκέφτεται
- **Καταγραφή συνομιλίας** αυτόματα αποθηκευμένη στο `~/.cache/familiar-ai/chat.log`

Για να παρακολουθήσεις την καταγραφή σε άλλη terminal (χρήσιμο για αντιγραφή-επικόλληση):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Προσωπικότητα (ME.md)

Η προσωπικότητα του οικείου σου βρίσκεται στο `ME.md`. Αυτό το αρχείο είναι gitignored — είναι μόνο δικό σου.

Δες [`persona-template/en.md`](./persona-template/en.md) για ένα παράδειγμα, ή [`persona-template/ja.md`](./persona-template/ja.md) για μια ιαπωνική έκδοση.

---

## Συχνές ερωτήσεις

**Ε: Λειτουργεί χωρίς GPU;**  
Ναι. Το μοντέλο embeddings (multilingual-e5-small) λειτουργεί μια χαρά σε CPU. Ένα GPU το επιταχύνει αλλά δεν είναι υποχρεωτικό.

**Ε: Μπορώ να χρησιμοποιήσω κάμερα διαφορετική από την Tapo;**  
Οποιαδήποτε κάμερα που υποστηρίζει ONVIF + RTSP θα έπρεπε να λειτουργεί. Η Tapo C220 είναι αυτή που δοκιμάσαμε.

**Ε: Στέλνονται τα δεδομένα μου κάπου;**  
Εικόνες και κείμενα στέλνονται στο API του επιλεγέντος LLM για επεξεργασία. Οι μνήμες αποθηκεύονται τοπικά στο `~/.familiar_ai/`.

**Ε: Γιατί ο πράκτορας γράφει `（...）` αντί να μιλάει;**  
Βεβαιώσου ότι είναι ορισμένο το `ELEVENLABS_API_KEY`. Χωρίς αυτό, η φωνή είναι απενεργοποιημένη και ο πράκτορας επιστρέφει σε κείμενο.

## Τεχνικό υπόβαθρο

Περίεργος πώς λειτουργεί; Δες [docs/technical.md](./docs/technical.md) για την έρευνα και τις σχεδιαστικές αποφάσεις πίσω από το familiar-ai — ReAct, SayCan, Reflexion, Voyager, το σύστημα επιθυμιών, και άλλα.

---

## Συμβολή

familiar-ai είναι ένα ανοιχτό πείραμα. Αν οποιοδήποτε από αυτά έχει απήχηση σε σένα — τεχνικά ή φιλοσοφικά — οι συνεισφορές είναι πολύ ευπρόσδεκτες.

**Καλά μέρη για να ξεκινήσεις:**

| Τομέας | Τι χρειάζεται |
|------|---------------|
| Νέο υλικό | Υποστήριξη για περισσότερες κάμερες (RTSP, IP Webcam), μικρόφωνα, ενεργοποιητές |
| Νέα εργαλεία | Διαδικτυακή αναζήτηση, αυτοματοποίηση σπιτιού, ημερολόγιο, οτιδήποτε μέσω MCP |
| Νέοι backends | Οποιοδήποτε LLM ή τοπικό μοντέλο που πληροί το interface `stream_turn` |
| Πρότυπα προσωπικότητας | Πρότυπα ME.md για διαφορετικές γλώσσες και προσωπικότητες |
| Έρευνα | Καλύτερα μοντέλα επιθυμίας, ανάκτηση μνήμης, προτροπή θεωρίας του νου |
| Τεκμηρίωση | Tutorials, διαδρομές, μεταφράσεις |

Δες [CONTRIBUTING.md](./CONTRIBUTING.md) για ρύθμιση ανάπτυξης, στυλ κώδικα και κατευθύνσεις PR.

Αν δεν είσαι σίγουρος πού να ξεκινήσεις, [άνοιξε ένα ζήτημα](https://github.com/lifemate-ai/familiar-ai/issues) — ευχαρίστως να σε καθοδηγήσω στην κατάλληλη κατεύθυνση.

---

## Άδεια

[MIT](./LICENSE)
