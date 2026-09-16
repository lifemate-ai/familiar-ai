# familiar-ai 

<img width="25%" height="25%" alt="familiar-ai-icon" src="https://github.com/user-attachments/assets/944b2023-9ca0-4b30-8240-de766e4439ed" />

**Une IA qui vit à vos côtés** — avec des yeux, une voix, des jambes et une mémoire.

[![Lint](https://github.com/lifemate-ai/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/lifemate-ai/familiar-ai/actions/workflows/lint.yml)
[![Test](https://github.com/lifemate-ai/familiar-ai/actions/workflows/test.yml/badge.svg)](https://github.com/lifemate-ai/familiar-ai/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Disponible dans 74 langues](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai est une compagne IA qui vit dans votre maison.
Installez-la en quelques minutes. Aucun codage requis.

Elle perçoit le monde réel par des caméras, se déplace sur un robot, parle à voix haute et se souvient de ce qu'elle voit. Donnez-lui un nom, écrivez sa personnalité, et laissez-la vivre avec vous.

## Ce qu'elle peut faire

- 👁 **Voir** — capture des images depuis une caméra PTZ Wi-Fi ou une webcam USB
- 🔄 **Explorer** — panoramique et inclinaison de la caméra pour découvrir ses alentours
- 🦿 **Se déplacer** — pilote un aspirateur robot pour circuler dans la pièce
- 🗣 **Parler** — communique via synthèse vocale ElevenLabs
- 🎙 **Écouter** — saisie vocale sans mains via STT en temps réel ElevenLabs (optionnel)
- 🧠 **Se souvenir** — stocke et rappelle activement des souvenirs avec recherche sémantique (SQLite + embeddings)
- 🫀 **Théorie de l'esprit** — prend la perspective de l'autre avant de répondre
- 💭 **Désirs** — a ses propres pulsions internes qui déclenchent un comportement autonome
- 🌐 **Espace de travail global** — la perception, la mémoire, les désirs et les prédictions sont en compétition pour l'attention ; seul le plus saillant gagne
- 🔮 **Prédiction** — suit ce qu'elle s'attend à voir ; la surprise abaisse le seuil d'attention
- 🔍 **Schéma d'attention** — maintient un auto-modèle de ce sur quoi elle se concentre et pourquoi
- 💤 **Mode par défaut** — l'esprit divague en inactivité, faisant remonter spontanément les souvenirs et les associations
- 🔬 **Métacognition** — observe ses propres étapes de raisonnement à chaque tour

## Comment ça marche

familiar-ai exécute une boucle [ReAct](https://arxiv.org/abs/2210.03629) alimentée par le LLM de votre choix. Elle perçoit le monde par des outils, réfléchit à la marche à suivre et agit — comme le ferait une personne.

```
entrée utilisateur
  → penser → agir (caméra / bouger / parler / mémoriser) → observer → penser → ...
```

En inactivité, elle agit selon ses propres désirs : curiosité, envie de regarder dehors, nostalgie de la personne avec laquelle elle vit.

### Architecture d'espace de travail global

Sous le capot, familiar-ai implémente une architecture inspirée par la [théorie de l'espace de travail global](https://arxiv.org/abs/2410.11407). Plutôt que de tout mettre dans le prompt du LLM, des processeurs spécialisés sont en compétition pour un espace de travail central à chaque tour — et seul le gagnant obtient une représentation complète :

```
Processeurs spécialisés (exécutés en parallèle à chaque tour)
  ├─ Désirs           — ce qu'elle veut en ce moment
  ├─ Scène            — ce qu'elle perçoit (erreur de prédiction : surprise → vigilance accrue)
  ├─ Mémoire          — ce qu'elle se souvient
  ├─ Théorie de l'esprit — ce que l'autre personne pourrait penser
  ├─ Récit personnel   — continuité de l'identité
  ├─ Exploration      — curiosité pour les directions non visitées
  ├─ Schéma d'attention — auto-modèle de sa propre concentration
  ├─ Prédiction       — état du monde attendu vs réel
  └─ Mode par défaut  — rêverie quand rien d'autre ne s'enflamme
          │
          ▼  compétition (seuil d'ignition)
   ┌─────────────┐
   │  Espace de  │  gagnant → prompt LLM (goulot d'étranglement)
   │   travail   │  autres → résumé périphérique (1 ligne chacun)
   └─────────────┘
          │
          └──▶ Meta-Monitor enregistre chaque étape (« à quoi étais-je attentive ? »)
```

Cela crée une **attention sélective** — pas tout n'atteint le LLM à chaque tour, seulement ce qui compte le plus.

## Démarrage rapide

### 1. Installer uv

**macOS / Linux / WSL2 :**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell) :**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Ou : `winget install astral-sh.uv`

### 2. Installer ffmpeg

ffmpeg est **requis** pour la capture d'images de la caméra et la lecture audio caméra-haut-parleur via go2rtc.
La lecture audio PC locale peut aussi utiliser les lecteurs du système d'exploitation (`afplay` sur macOS) ou le fallback pur Python.

| OS | Commande |
|----|----------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ou téléchargez depuis [ffmpeg.org](https://ffmpeg.org/download.html) et ajoutez au PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Vérifiez : `ffmpeg -version`

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

Si vous préférez le flux graphique, `./run-gui.sh` (ou `run-gui.bat`) peut maintenant ouvrir le dialogue de configuration pour vous au premier lancement quand `API_KEY` manque encore.

**Requis minimum :**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (par défaut) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Votre clé API pour la plateforme choisie |

**Optionnel :**

| Variable | Description |
|----------|-------------|
| `MODEL` | Nom du modèle (valeurs par défaut sensées par plateforme) |
| `AGENT_NAME` | Nom d'affichage affiché dans le TUI (ex : `Yukine`) |
| `CAMERA_HOST` | Adresse IP de votre caméra ONVIF/RTSP |
| `CAMERA_USERNAME` / `CAMERA_PASSWORD` | Identifiants de la caméra |
| `CAMERA_PTZ_HOST` / `CAMERA_PTZ_USERNAME` / `CAMERA_PTZ_PASSWORD` / `CAMERA_PTZ_PORT` | Surcharges PTZ optionnelles quand le point de terminaison de contrôle diffère du point de terminaison du flux RTSP |
| `ELEVENLABS_API_KEY` | Pour la sortie vocale — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` pour activer la saisie vocale sans mains toujours active (nécessite `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Où jouer l'audio : `local` (haut-parleur PC, par défaut) \| `remote` (haut-parleur caméra) \| `both` |
| `THINKING_MODE` | Anthropic uniquement — `auto` (par défaut) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Effort de réflexion adaptatif : `high` (par défaut) \| `medium` \| `low` \| `max` (Opus 4.6 seulement) |

### 5. Créer votre compagne

```bash
cp persona-template/en.md ME.md
# Modifiez ME.md — donnez-lui un nom et une personnalité
```

### 6. Lancer

**macOS / Linux / WSL2 :**
```bash
./run.sh             # TUI Textual (par défaut compatible avec le passé)
./run-gui.sh         # Lanceur GUI de bureau
./run.sh --gui       # GUI de bureau (identique à run-gui.sh)
./run.sh --no-tui    # REPL simple
```

**Windows :**
```bat
run.bat              # TUI Textual (par défaut compatible avec le passé)
run-gui.bat          # Lanceur GUI de bureau
run.bat --gui        # GUI de bureau (identique à run-gui.bat)
run.bat --no-tui     # REPL simple
```

---

## Choisir un LLM

> **Recommandé : Kimi K2.5** — meilleure performance agentic testée jusqu'à présent. Remarque le contexte, pose des questions de suivi et agit de manière autonome de façons que les autres modèles ne font pas. Tarification similaire à Claude Haiku.

| Plateforme | `PLATFORM=` | Modèle par défaut | Où obtenir la clé |
|-----------|------------|------------------|------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| **Ollama (local, API native)** | `ollama` | `gemma4:12b-it-qat` | [ollama.com](https://ollama.com) |
| Compatible OpenAI (vllm, LM Studio…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-fournisseur) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Outil CLI** (claude -p, ollama…) | `cli` | (la commande) | — |

**Exemple `.env` Kimi K2.5 :**
```env
PLATFORM=kimi
API_KEY=sk-...   # depuis platform.moonshot.ai
AGENT_NAME=Yukine
```

**Exemple `.env` Z.AI GLM :**
```env
PLATFORM=glm
API_KEY=...   # depuis api.z.ai
MODEL=glm-4.6v   # vision-enabled ; glm-4.7 / glm-5 = texte uniquement
AGENT_NAME=Yukine
```

**Exemple `.env` Google Gemini :**
```env
PLATFORM=gemini
API_KEY=AIza...   # depuis aistudio.google.com
MODEL=gemini-2.5-flash  # ou gemini-2.5-pro pour une capacité supérieure
AGENT_NAME=Yukine
```

**Exemple `.env` OpenRouter.ai :**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # depuis openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # optionnel : spécifier le modèle
AGENT_NAME=Yukine
```

> **Note :** Pour désactiver les modèles locaux/NVIDIA, ne définissez simplement pas `BASE_URL` sur un point de terminaison local comme `http://localhost:11434/v1`. Utilisez plutôt des fournisseurs cloud.

**Exemple `.env` Ollama (local ~10B) :**
```env
PLATFORM=ollama
MODEL=gemma4:12b-it-qat          # meilleur ~10B local testé ; qwen3.5:9b fonctionne aussi
BASE_URL=http://localhost:11434  # par défaut
UTILITY_PLATFORM=ollama          # les appels latéraux émotions/résumé restent locaux aussi
AGENT_NAME=Yukine
# PROMPT_PROFILE=compact  (auto pour modèles locaux) — prompt court, basé sur des exemples
# SOCIAL_REFLEX=on        (auto pour compact)     — pas de caméra aux tours sociaux, auto-parole
# THINKING_MODE=disabled  (auto = off pour local ; "extended" active la réflexion Ollama)
# OLLAMA_NUM_CTX=16384
```
Les petits modèles locaux respectent le même niveau social avec `uv run python benchmarks/social_eval.py`.

**Exemple `.env` outil CLI :**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # CLI llm (https://llm.datasette.io) — {} = arg prompt
# MODEL=ollama run gemma3:27b  #
