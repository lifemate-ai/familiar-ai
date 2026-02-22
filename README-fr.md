# familiar-ai 🐾

**Une IA qui vit à vos côtés** — avec des yeux, une voix, des jambes et de la mémoire.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

[English README](./README.md)

---

familiar-ai est une IA compagne qui vit dans votre maison.
Installez-la en quelques minutes. Aucun code requis.

Elle perçoit le monde réel par des caméras, se déplace sur un corps de robot, parle à haute voix et se souvient de ce qu'elle voit. Donnez-lui un nom, écrivez sa personnalité, et laissez-la vivre avec vous.

## Ce qu'elle peut faire

- 👁 **Voir** — capture des images à partir d'une caméra PTZ Wi-Fi ou d'une webcam USB
- 🔄 **Regarder autour** — incline et fait pivoter la caméra pour explorer ses alentours
- 🦿 **Se déplacer** — conduit un aspirateur robot pour explorer la pièce
- 🗣 **Parler** — s'exprime via la synthèse vocale ElevenLabs
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

### 2. Cloner et installer

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 3. Configurer

```bash
cp .env.example .env
# Modifiez .env avec vos paramètres
```

**Minimum requis :**

| Variable | Description |
|----------|-------------|
| `PLATFORM` | `anthropic` (défaut) \| `gemini` \| `openai` \| `kimi` |
| `API_KEY` | Votre clé API pour la plateforme choisie |

**Optionnel :**

| Variable | Description |
|----------|-------------|
| `MODEL` | Nom du modèle (valeurs par défaut judicieuses par plateforme) |
| `AGENT_NAME` | Nom d'affichage dans l'interface textuelle (ex. `Yukine`) |
| `CAMERA_HOST` | Adresse IP de votre caméra ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Identifiants de la caméra |
| `ELEVENLABS_API_KEY` | Pour la sortie vocale — [elevenlabs.io](https://elevenlabs.io/) |

### 4. Créer votre compagne

```bash
cp persona-template/en.md ME.md
# Modifiez ME.md — donnez-lui un nom et une personnalité
```

### 5. Lancer

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
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Compatible OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |

**Exemple `.env` pour Kimi K2.5 :**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

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
3. La voix joue via le haut-parleur intégré de la caméra via go2rtc (téléchargé automatiquement au premier lancement)

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
