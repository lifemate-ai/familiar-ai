# familiar-ai 🐾

**Une IA qui vit à vos côtés** — avec des yeux, une voix, des jambes et de la mémoire.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

[English README](./README.md)

---

[![Vidéo de démo](https://img.youtube.com/vi/kakc5jUBFjM/0.jpg)](https://youtube.com/shorts/kakc5jUBFjM)

familiar-ai est une IA compagne qui vit dans votre maison.
Installez-la en quelques minutes. Aucun code requis.

Elle perçoit le monde réel par des caméras, se déplace sur un corps de robot, parle à haute voix et se souvient de ce qu'elle voit. Donnez-lui un nom, écrivez sa personnalité, et laissez-la vivre avec vous.

## Ce qu'elle peut faire

- 👁 **Voir** — capture des images à partir d'une caméra PTZ Wi-Fi ou d'une webcam USB
- 🔄 **Regarder autour** — incline et fait pivoter la caméra pour explorer ses alentours
- 🦿 **Se déplacer** — conduit un aspirateur robot pour explorer la pièce
- 🗣 **Parler** — s'exprime via la synthèse vocale ElevenLabs
- 🎙 **Écouter** — saisie vocale mains libres via ElevenLabs STT temps réel (optionnel)
- 🧠 **Se souvenir** — enregistre et rappelle activement les souvenirs avec recherche sémantique (SQLite + embeddings)
- 🫀 **Théorie de l'esprit** — adopte la perspective d'autrui avant de répondre
- 💭 **Désirs** — possède ses propres motivations internes qui déclenchent un comportement autonome

## Comment ça fonctionne

familiar-ai exécute une boucle [ReAct](https://arxiv.org/abs/2210.03629) alimentée par votre LLM de choix. Elle perçoit le monde par des outils, réfléchit à la prochaine action à faire et agit — comme une personne le ferait.

```
entrée utilisateur
  → penser → agir (caméra / bouger / parler / mémoriser) → observer → penser → ...
```

Quand elle est inactive, elle agit selon ses propres désirs : la curiosité, l'envie de regarder dehors, le manque de la personne avec qui elle vit.

## Premiers pas

### 1. Installer uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Installer ffmpeg

ffmpeg est **requis** pour la capture d'images de la caméra et la lecture audio.

| OS | Commande |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ou télécharger depuis [ffmpeg.org](https://ffmpeg.org/download.html) et ajouter au PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Vérifier : `ffmpeg -version`

### 3. Cloner et installer

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configurer

```bash
cp .env.example .env
# Modifiez .env avec vos paramètres
```

**Minimum requis :**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (défaut) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Votre clé API pour la plateforme choisie |

**Optionnel :**

| Variable | Description |
|----------|-------------|
| `MODEL` | Nom du modèle (valeurs par défaut judicieuses par plateforme) |
| `AGENT_NAME` | Nom d'affichage dans l'interface textuelle (ex. `Yukine`) |
| `CAMERA_HOST` | Adresse IP de votre caméra ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Identifiants de la caméra |
| `ELEVENLABS_API_KEY` | Pour la sortie vocale — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` pour activer la saisie vocale mains libres en temps réel (nécessite `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Destination audio : `local` (haut-parleur PC, défaut) \| `remote` (haut-parleur caméra) \| `both` (les deux simultanément) |
| `THINKING_MODE` | Anthropic uniquement — `auto` (défaut) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Profondeur de la réflexion adaptative : `high` (défaut) \| `medium` \| `low` \| `max` (Opus 4.6 uniquement) |

### 5. Créer votre compagne

```bash
cp persona-template/en.md ME.md
# Modifiez ME.md — donnez-lui un nom et une personnalité
```

### 6. Lancer

```bash
./run.sh             # Interface textuelle (recommandé)
./run.sh --no-tui    # REPL simple
```

---

## Choisir un LLM

> **Recommandé : Kimi K2.5** — meilleure performance agentic testée jusqu'à présent. Comprend le contexte, pose des questions de suivi et agit de manière autonome d'une façon que d'autres modèles ne font pas. Prix comparable à Claude Haiku.

| Plateforme | `PLATFORM=` | Modèle par défaut | Où obtenir la clé |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Compatible OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-fournisseurs) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Outil CLI** (llm, ollama…) | `cli` | (la commande) | — |

**Exemple `.env` pour Kimi K2.5 :**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Exemple `.env` Z.AI GLM :**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # vision-enabled; glm-4.7 / glm-5 = text-only
AGENT_NAME=Yukine
```

**Exemple `.env` pour Google Gemini :**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # or gemini-2.5-pro
AGENT_NAME=Yukine
```

**Exemple `.env` pour OpenRouter.ai :**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # optional
AGENT_NAME=Yukine
```

> **Note :** Pour désactiver les modèles locaux/NVIDIA, ne définissez pas `BASE_URL` sur un endpoint local comme `http://localhost:11434/v1`. Utilisez plutôt des fournisseurs cloud.

**Exemple `.env` pour outil CLI :**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = arg du prompt
# MODEL=ollama run gemma3:27b  # Ollama — sans {}, prompt via stdin
```

---

## Serveurs MCP

familiar-ai peut se connecter à n'importe quel serveur [MCP (Model Context Protocol)](https://modelcontextprotocol.io) pour accéder à la mémoire externe, aux fichiers, à la recherche web, etc.

Configurez les serveurs dans `~/.familiar-ai.json` (même format que Claude Code) :

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

Deux types de transport sont supportés :
- **`stdio`** : lance un sous-processus local (`command` + `args`)
- **`sse`** : se connecte à un serveur HTTP+SSE (`url`)

Remplacez le chemin du fichier de config avec `MCP_CONFIG=/path/to/config.json`.

---

## Matériel

familiar-ai fonctionne avec le matériel que vous avez — ou rien du tout.

| Composant | Rôle | Exemple | Requis ? |
|------|-------------|---------|-----------|
| Caméra PTZ Wi-Fi | Yeux + cou | Tapo C220 (~$30) | **Recommandé** |
| Webcam USB | Yeux (fixes) | Toute caméra UVC | **Recommandé** |
| Aspirateur robot | Jambes | Tout modèle compatible Tuya | Non |
| PC / Raspberry Pi | Cerveau | Tout ce qui exécute Python | **Oui** |

> **Une caméra est fortement recommandée.** Sans elle, familiar-ai peut toujours parler — mais elle ne peut pas voir le monde, ce qui est un peu tout l'intérêt.

### Configuration minimale (sans matériel)

Vous voulez juste l'essayer ? Vous n'avez besoin que d'une clé API :

```env
PLATFORM=kimi
API_KEY=sk-...
```

Lancez `./run.sh` et commencez à discuter. Ajoutez du matériel au fur et à mesure.

### Caméra PTZ Wi-Fi (Tapo C220)

1. Dans l'app Tapo : **Paramètres → Avancé → Compte caméra** — créez un compte local (pas de compte TP-Link)
2. Trouvez l'IP de la caméra dans la liste des appareils de votre routeur
3. Définissez dans `.env` :
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Voix (ElevenLabs)

1. Obtenez une clé API sur [elevenlabs.io](https://elevenlabs.io/)
2. Définissez dans `.env` :
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # optionnel, utilise la voix par défaut si omis
   ```
La destination audio est contrôlée par `TTS_OUTPUT` :

```env
TTS_OUTPUT=local    # Haut-parleur PC (défaut)
TTS_OUTPUT=remote   # Haut-parleur caméra uniquement
TTS_OUTPUT=both     # Haut-parleur caméra + haut-parleur PC simultanément
```

#### A) Haut-parleur de la caméra (via go2rtc)

Utilisez `TTS_OUTPUT=remote` (ou `both`). Installez [go2rtc](https://github.com/AlexxIT/go2rtc/releases) manuellement :

1. Téléchargez le binaire depuis la [page des releases](https://github.com/AlexxIT/go2rtc/releases) :
   - Linux/macOS : `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows : `go2rtc_win64.exe`**

2. Placez et renommez-le :
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x requis

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Créez `go2rtc.yaml` dans le même répertoire :
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```

4. familiar-ai démarre go2rtc automatiquement. Si la caméra supporte l'audio bidirectionnel, la voix sort du haut-parleur de la caméra.

#### B) Haut-parleur PC local

Mode par défaut (`TTS_OUTPUT=local`). Essaie dans l'ordre : **paplay** → **mpv** → **ffplay**. Également utilisé en repli quand `TTS_OUTPUT=remote` et que go2rtc est indisponible.

| OS | Installation |
|----|-------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ou `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — définir `PULSE_SERVER=unix:/mnt/wslg/PulseServer` dans `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — télécharger et ajouter au PATH, **ou** `winget install ffmpeg` |

> Sans go2rtc ni lecteur local, la génération vocale (appel API ElevenLabs) fonctionne toujours — la lecture est simplement ignorée.

### Saisie vocale (STT temps réel)

Définissez `REALTIME_STT=true` dans `.env` pour une saisie vocale mains libres en continu :

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # même clé que pour TTS
```

familiar-ai diffuse l'audio du microphone vers ElevenLabs Scribe v2 et valide les transcriptions automatiquement lorsque vous faites une pause. Aucune pression de touche requise. Compatible avec le mode push-to-talk (Ctrl+T).

---

## Interface textuelle

familiar-ai inclut une interface textuelle créée avec [Textual](https://textual.textualize.io/) :

- Historique de conversation scrollable avec diffusion de texte en direct
- Complément de tabulation pour `/quit`, `/clear`
- Interrompez l'agent en cours d'exécution en tapant pendant qu'il réfléchit
- **Journal de conversation** sauvegardé automatiquement dans `~/.cache/familiar-ai/chat.log`

Pour suivre le journal dans un autre terminal (utile pour copier-coller) :
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

La personnalité de votre compagne vit dans `ME.md`. Ce fichier est ignoré par git — il vous appartient seul.

Consultez [`persona-template/en.md`](./persona-template/en.md) pour un exemple, ou [`persona-template/ja.md`](./persona-template/ja.md) pour une version japonaise.

---

## FAQ

**Q : Ça fonctionne sans GPU ?**
Oui. Le modèle d'embedding (multilingual-e5-small) s'exécute bien sur CPU. Un GPU le rend plus rapide mais n'est pas requis.

**Q : Puis-je utiliser une caméra autre que Tapo ?**
Toute caméra supportant ONVIF + RTSP devrait fonctionner. Tapo C220 est ce que nous avons testé.

**Q : Mes données sont-elles envoyées quelque part ?**
Les images et le texte sont envoyés à l'API LLM de votre choix pour traitement. Les souvenirs sont stockés localement dans `~/.familiar_ai/`.

**Q : Pourquoi l'agent écrit-il `（...）` au lieu de parler ?**
Assurez-vous que `ELEVENLABS_API_KEY` est défini. Sans lui, la voix est désactivée et l'agent revient au texte.

## Licence

[MIT](./LICENSE)
