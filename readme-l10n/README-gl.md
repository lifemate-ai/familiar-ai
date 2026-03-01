# familiar-ai 🐾

**Unha IA que vive xunto a ti** — con ollos, voz, pernas e memoria.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Disponíbel en 74 linguas](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai é un compañeiro de IA que vive na túa casa. 
Configúrao en minutos. Non se require programación.

Percibe o mundo real a través de cámaras, móvese nun corpo robot, fala en voz alta e lembra o que ve. Dále un nome, escribe a súa personalidade e déixao vivir contigo.

## O que pode facer

- 👁 **Ver** — captura imaxes dende unha cámara PTZ Wi-Fi ou webcam USB
- 🔄 **Mirar arredor** — panorámica e inclina a cámara para explorar o seu arredor
- 🦿 **Mover** — xira un aspirador robot para percorrer a habitación
- 🗣 **Falar** — conversa a través de ElevenLabs TTS
- 🎙 **Escoitar** — entrada de voz sen mans a través de ElevenLabs Realtime STT (optativo)
- 🧠 **Lembrar** — almacena e recupera activamente recordos cunha busca semántica (SQLite + embeddings)
- 🫀 **Teoría da mente** — toma a perspectiva da outra persoa antes de responder
- 💭 **Desexo** — ten os seus propios impulsos internos que desencadenan comportamento autónomo

## Como funciona

familiar-ai executa un loop [ReAct](https://arxiv.org/abs/2210.03629) impulsado pola túa escolha de LLM. Percibe o mundo a través de ferramentas, pensa en que facer a continuación e actúa — como faría unha persoa.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Cando está inactivo, actúa segundo os seus propios desexos: curiosidade, desexo de mirar fóra, a echo da persoa coa que vive.

## Comezando

### 1. Instala uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Ou: `winget install astral-sh.uv`

### 2. Instala ffmpeg

ffmpeg é **requirido** para capturar imaxes da cámara e reprodución de audio.

| OS | Comando |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ou descarga dende [ffmpeg.org](https://ffmpeg.org/download.html) e engádeo ao PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifica: `ffmpeg -version`

### 3. Clona e instala

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configura

```bash
cp .env.example .env
# Edita .env cos teus parámetros
```

**Mínimo requirido:**

| Variable | Descrición |
|----------|-------------|
| `PLATFORM` | `anthropic` (por defecto) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | A tua clave de API para a plataforma escollida |

**Opcional:**

| Variable | Descrición |
|----------|-------------|
| `MODEL` | Nome do modelo (valores por defecto para cada plataforma) |
| `AGENT_NAME` | Nome que se amosa na TUI (por exemplo `Yukine`) |
| `CAMERA_HOST` | Dirección IP da túa cámara ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Credenciais da cámara |
| `ELEVENLABS_API_KEY` | Para a saída de voz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` para habilitar a entrada de voz sen mans (requiere `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Onde reproducir audio: `local` (altofalante do PC, por defecto) \| `remote` (altofalante da cámara) \| `both` |
| `THINKING_MODE` | Só Anthropic — `auto` (por defecto) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Esforzo de pensamento adaptativo: `high` (por defecto) \| `medium` \| `low` \| `max` (só Opus 4.6) |

### 5. Crea o teu familiar

```bash
cp persona-template/en.md ME.md
# Edita ME.md — dáselle un nome e personalidade
```

### 6. Executa

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI textual (recomendado)
./run.sh --no-tui    # REPL plano
```

**Windows:**
```bat
run.bat              # TUI textual (recomendado)
run.bat --no-tui     # REPL plano
```

---

## Escollendo un LLM

> **Recomendado: Kimi K2.5** — a mellor rendibilidade de axente probada ata agora. Nota o contexto, fai preguntas de seguimento e actúa de maneira autónoma onde outros modelos non o fan. Prezo similar a Claude Haiku.

| Plataforma | `PLATFORM=` | Modelo por defecto | Onde conseguir a clave |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provider) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI tool** (claude -p, ollama…) | `cli` | (o comando) | — |

**Exemplo de `.env` para Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # de platform.moonshot.ai
AGENT_NAME=Yukine
```

**Exemplo de `.env` para Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # de api.z.ai
MODEL=glm-4.6v   # habilitado para visión; glm-4.7 / glm-5 = só texto
AGENT_NAME=Yukine
```

**Exemplo de `.env` para Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # de aistudio.google.com
MODEL=gemini-2.5-flash  # ou gemini-2.5-pro para maior capacidade
AGENT_NAME=Yukine
```

**Exemplo de `.env` para OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # de openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcional: especifica o modelo
AGENT_NAME=Yukine
```

> **Nota:** Para desactivar modelos locais/NVIDIA, simplemente non configures `BASE_URL` para un punto final local como `http://localhost:11434/v1`. Usa provedores en nube en lugar diso.

**Exemplo de `.env` para CLI tool:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argumento de prompt
# MODEL=ollama run gemma3:27b  # Ollama — sen {}, o prompt vai por stdin
```

---

## Servidores MCP

familiar-ai pode conectarse a calquera servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Isto permítelle conectar memoria externa, acceso a sistema de ficheiros, busca en web, ou calquera outra ferramenta.

Configura servidores en `~/.familiar-ai.json` (mesmo formato que Claude Code):

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

Dúas tipos de transporte son soportados:
- **`stdio`**: lanza un subprocesso local (`command` + `args`)
- **`sse`**: conéctase a un servidor HTTP+SSE (`url`)

Override a ubicación do ficheiro de configuración con `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai funciona co que queiras — ou sen nada.

| Parte | O que fai | Exemplo | Necesario? |
|------|-------------|---------|-----------|
| Cámara PTZ Wi-Fi | Ollos + pescozo | Tapo C220 (~$30) | **Recomendado** |
| Webcam USB | Ollos (fixo) | Calquera cámara UVC | **Recomendado** |
| Aspirador robot | pernas | Calquera modelo compatible con Tuya | Non |
| PC / Raspberry Pi | Cerebro | Calquera que execute Python | **Si** |

> **Recoméndase fortemente unha cámara.** Sen unha, familiar-ai pode falar — pero non pode ver o mundo, que é un pouco o bote da cuestión.

### Configuración mínima (sen hardware)

Queres só probalo? Só necesitas unha clave de API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Executa `./run.sh` (macOS/Linux/WSL2) ou `run.bat` (Windows) e comeza a charlar. Engade hardware conforme avanzas.

### Cámara PTZ Wi-Fi (Tapo C220)

1. Na app de Tapo: **Configuración → Avanzada → Conta da Cámara** — crea unha conta local (non a conta de TP-Link)
2. Atopa a IP da cámara na lista de dispositivos do teu router
3. Establece en `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Voz (ElevenLabs)

1. Obtén unha clave de API en [elevenlabs.io](https://elevenlabs.io/)
2. Establece en `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcional, usa a voz por defecto se se omite
   ```

Hai dous destinos de reprodución, controlados por `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # Altavoz do PC (por defecto)
TTS_OUTPUT=remote   # só altavoz da cámara
TTS_OUTPUT=both     # altavoz da cámara + altavoz do PC simultaneamente
```

#### A) Altavoz da cámara (a través de go2rtc)

Establece `TTS_OUTPUT=remote` (ou `both`). Require [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Descarga o binario da [páxina de lanzamentos](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Colócao e renómrao:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x necesario

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Crea `go2rtc.yaml` na mesma carpeta:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Usa as credenciais da conta local da cámara (non a túa conta en nube de TP-Link).

4. familiar-ai inicia go2rtc automaticamente ao lanzarse. Se a túa cámara soporta audio bidireccional (canle de volta), a voz reproduce dende o altavoz da cámara.

#### B) Altavoz do PC local

O por defecto (`TTS_OUTPUT=local`). Intenta reprodutores en orde: **paplay** → **mpv** → **ffplay**. Tamén se usa como un fallback cando `TTS_OUTPUT=remote` e go2rtc non está dispoñible.

| OS | Instala |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ou `paplay` a través de `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — establece `PULSE_SERVER=unix:/mnt/wslg/PulseServer` en `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — descarga e engádeo ao PATH, **ou** `winget install ffmpeg` |

> Se non hai ningún reprodutor de audio dispoñible, a fala aínda se xera — simplemente non se reproducirá.

### Entrada de voz (Realtime STT)

Establece `REALTIME_STT=true` en `.env` para entrada de voz sempre activa e sen mans:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # mesma clave que TTS
```

familiar-ai transmite audio do micrófono a ElevenLabs Scribe v2 e auto-confirma transcricións cando pares de falar. Non se require presión de botón. Coexiste co modo de pulsar para falar (Ctrl+T).

---

## TUI

familiar-ai inclúe unha interface de terminal construida con [Textual](https://textual.textualize.io/):

- Historial de conversación desprazable con texto en streaming en vivo
- Completado de tabulación para `/quit`, `/clear`
- Interrompe ao axente a medio pensamento escribindo mentres está pensando
- **Log de conversación** auto-desgravado en `~/.cache/familiar-ai/chat.log`

Para seguir o log en outra terminal (útil para copiar e pegar):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

A personalidade do teu familiar vive en `ME.md`. Este ficheiro está ignorado por git — é só teu.

Véxase [`persona-template/en.md`](./persona-template/en.md) para un exemplo, ou [`persona-template/ja.md`](./persona-template/ja.md) para unha versión en xaponés.

---

## FAQ

**Q: Funciona sen GPU?**
Si. O modelo de embedding (multilingual-e5-small) funciona ben en CPU. Unha GPU faina máis rápida pero non é necesaria.

**Q: Podo usar unha cámara que non sexa Tapo?**
Calquera cámara que soporte ONVIF + RTSP debería funcionar. Tapo C220 é o que probamos.

**Q: Se envían os meus datos a algún lugar?**
As imaxes e o texto envíase á API do LLM escollido para procesamento. Os recordos almacénanse localmente en `~/.familiar_ai/`.

**Q: Por que o axente escribe `（...）` en lugar de falar?**
Asegúrate de que `ELEVENLABS_API_KEY` está configurado. Sen el, a voz está desactivada e o axente recorre ao texto.

## Antecedentes técnicos

Curioso sobre como funciona? Vexa [docs/technical.md](./docs/technical.md) para as investigacións e decisións de deseño detrás de familiar-ai — ReAct, SayCan, Reflexion, Voyager, o sistema de desexo, e máis.

---

## Contribuíndo

familiar-ai é un experimento aberto. Se algo diso resoa contigo — técnica ou filosóficamente — as contribucións son moi benvidas.

**Boas formas de comezar:**

| Área | O que se necesita |
|------|---------------|
| Novo hardware | Soporte para máis cámaras (RTSP, IP Webcam), micrófonos, actuadores |
| Novas ferramentas | Busca en web, automatización do fogar, calendario, calquera cousa a través de MCP |
| Novos backends | Calquera LLM ou modelo local que se axuste á interface `stream_turn` |
| Plantillas de persona | Plantillas de ME.md para diferentes linguas e personalidades |
| Investigación | Mellores modelos de desexo, recuperación de memoria, incitación á teoría da mente |
| Documentación | Tutoriais, guías, traducións |

Véxase [CONTRIBUTING.md](./CONTRIBUTING.md) para a configuración do dev, estilo de código, e guías de PR.

Se non estás seguro por onde comezar, [abre un problema](https://github.com/lifemate-ai/familiar-ai/issues) — encantado de sinalarche na dirección correcta.

---

## Licenza

[MIT](./LICENSE)
