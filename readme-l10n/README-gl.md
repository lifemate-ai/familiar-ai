# familiar-ai 🐾

**Un AI que vive a teu lado** — con ollos, voz, patas e memoria.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai é un compañero AI que vive na túa casa. Configureo en minutos. Non se require codificación.

Percibe o mundo real a través de cámaras, móvese cun corpo robótico, fala en voz alta e lembra o que ve. Dále un nome, escribe a súa personalidade e déixao vivir contigo.

## O que pode facer

- 👁 **Ver** — captura imaxes dunha cámara PTZ Wi-Fi ou webcam USB
- 🔄 **Mirar ao redor** — move e inclina a cámara para explorar os seus arredores
- 🦿 **Moverse** — conduce un aspirador robótico para percorrer a habitación
- 🗣 **Falar** — fala a través de ElevenLabs TTS
- 🎙 **Escoitar** — entrada de voz sen mans a través de ElevenLabs Realtime STT (opcional)
- 🧠 **Lembrar** — almacena e recupera activamente recordos con busca semántica (SQLite + embeddings)
- 🫀 **Teoría da mente** — toma a perspectiva da outra persoa antes de responder
- 💭 **Desexo** — ten os seus propios impulsos internos que desencadean comportamento autónomo

## Como funciona

familiar-ai executa un loop [ReAct](https://arxiv.org/abs/2210.03629) impulsado pola túa elección de LLM. Percibe o mundo a través de ferramentas, pensa sobre o que facer a continuación e actúa — igual que faría unha persoa.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Cando está inactiva, actúa segundo os seus propios desexos: curiosidade, querer mirar fóra, echando de menos á persoa coa que vive.

## Comezando

### 1. Instalar uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instalar ffmpeg

ffmpeg é **requirido** para a captura de imaxes da cámara e a reprodución de audio.

| SO | Comando |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ou descarga de [ffmpeg.org](https://ffmpeg.org/download.html) e engade á PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifica: `ffmpeg -version`

### 3. Clonar e instalar

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configurar

```bash
cp .env.example .env
# Edita .env coas túas configuracións
```

**Mínimo requerido:**

| Variable | Descrición |
|----------|-------------|
| `PLATFORM` | `anthropic` (por defecto) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | A túa clave API para a plataforma elixida |

**Opcional:**

| Variable | Descrición |
|----------|-------------|
| `MODEL` | Nome do modelo (valores por defecto sensatos por plataforma) |
| `AGENT_NAME` | Nome a mostrar na TUI (exemplo: `Yukine`) |
| `CAMERA_HOST` | Dirección IP da túa cámara ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Credenciais da cámara |
| `ELEVENLABS_API_KEY` | Para a saída de voz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` para activar a entrada de voz sempre activa sen mans (requere `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Onde reproducir audio: `local` (altavoceiro do PC, por defecto) \| `remote` (altavoceiro da cámara) \| `both` |
| `THINKING_MODE` | Só para Anthropomic — `auto` (por defecto) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Esforzo de pensamento adaptativo: `high` (por defecto) \| `medium` \| `low` \| `max` (só Opus 4.6) |

### 5. Crea o teu familiar

```bash
cp persona-template/en.md ME.md
# Edita ME.md — dáslle un nome e personalidade
```

### 6. Executar

```bash
./run.sh             # TUI textual (recomendado)
./run.sh --no-tui    # REPL simple
```

---

## Elixindo un LLM

> **Recomendado: Kimi K2.5** — o mellor rendemento agentic que probamos até agora. Nota o contexto, fai preguntas de seguimento e actúa de forma autónoma de maneiras que outros modelos non fan. Prezo similar a Claude Haiku.

| Plataforma | `PLATFORM=` | Modelo por defecto | Onde conseguir a clave |
|------------|------------|-------------------|----------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Compatible con OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provedor) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Ferramenta CLI** (claude -p, ollama…) | `cli` | (o comando) | — |

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
MODEL=mistralai/mistral-7b-instruct  # opcional: especificar modelo
AGENT_NAME=Yukine
```

> **Nota:** Para desactivar modelos locais/NVIDIA, simplemente non establezas `BASE_URL` a un punto de extensión local como `http://localhost:11434/v1`. Usa provedores na nube en vez diso.

**Exemplo de `.env` para ferramenta CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = prompt arg
# MODEL=ollama run gemma3:27b  # Ollama — sen {}, o prompt vai por stdin
```

---

## Servidores MCP

familiar-ai pode conectarse a calquera servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Isto permítelle conectar memoria externa, acceso ao sistema de arquivos, búsqueda na web, ou calquera outra ferramenta.

Configura os servidores en `~/.familiar-ai.json` (mesmo formato que Claude Code):

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

Dúas tipoloxías de transporte están soportadas:
- **`stdio`**: lanzar un subprocesso local (`command` + `args`)
- **`sse`**: conectarse a un servidor HTTP+SSE (`url`)

Substitúe a localización do arquivo de configuración con `MCP_CONFIG=/camiño/a/config.json`.

---

## Hardware

familiar-ai funciona co que queiras — ou sen hardware algum.

| Parte | Que fai | Exemplo | Requerido? |
|-------|---------|---------|------------|
| Cámara PTZ Wi-Fi | Ollos + pescozo | Tapo C220 (~$30) | **Recomendado** |
| Webcam USB | Ollos (fixo) | Calquera cámara UVC | **Recomendado** |
| Aspirador robótico | Pata | Calquera modelo compatible con Tuya | Non |
| PC / Raspberry Pi | Cerebro | Calquera cousa que execute Python | **Si** |

> **Recoméndase encarecidamente unha cámara.** Sen ela, familiar-ai pode seguir a falar — pero non pode ver o mundo, que é un pouco a toda a cuestión.

### Configuración mínima (sen hardware)

Só queres probar? Só necesitas unha chave API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Executa `./run.sh` e comeza a charlar. Engade hardware conforme avanzas.

### Cámara PTZ Wi-Fi (Tapo C220)

1. Na aplicación Tapo: **Configuración → Avanzado → Conta da cámara** — crea unha conta local (non unha conta TP-Link)
2. Atopa a IP da cámara na lista de dispositivos do teu router
3. Configura en `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### Voz (ElevenLabs)

1. Obtén unha clave API en [elevenlabs.io](https://elevenlabs.io/)
2. Configura en `.env`:
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

2. Colócao e renómbrao:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x requerido

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Crea `go2rtc.yaml` no mesmo directorio:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Usa as credenciais da conta local da cámara (non a túa conta en nube de TP-Link).

4. familiar-ai inicia go2rtc automáticamente ao lanzarse. Se a túa cámara admite audio bidireccional (canle de retroceso), a voz reproduce a partir do altavoz da cámara.

#### B) Altavoz local do PC

O por defecto (`TTS_OUTPUT=local`). Intenta reprodutores en orde: **paplay** → **mpv** → **ffplay**. Tamén se usa como alternativa cando `TTS_OUTPUT=remote` e go2rtc non está dispoñible.

| SO | Instalar |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ou `paplay` a través de `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — configurar `PULSE_SERVER=unix:/mnt/wslg/PulseServer` en `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — descarga e engade á PATH, **ou** `winget install ffmpeg` |

> Se non está dispoñible ningún reprodutor de audio, a voz segue xerándose — simplemente non se reproducirá.

### Entrada de voz (Realtime STT)

Establece `REALTIME_STT=true` en `.env` para entrada de voz sempre activa e sen mans:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # mesma clave que TTS
```

familiar-ai transmite audio do micrófono a ElevenLabs Scribe v2 e auto-compón transcricións cando detés a túa fala. Non se require pulsar botón. Coexiste co modo de presión para falar (Ctrl+T).

---

## TUI

familiar-ai inclúe unha UI de terminal construída con [Textual](https://textual.textualize.io/):

- Historial de conversación desprazable con texto en directo
- Completado por tabulación para `/quit`, `/clear`
- Interrompe ao axente no medio dunha volta escribindo mentres está pensando
- **Diario de conversación** auto-gardado en `~/.cache/familiar-ai/chat.log`

Para seguir o diario noutro terminal (útil para copiar-pegar):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

A personalidade do teu familiar vive en `ME.md`. Este arquivo está ignorado por git — é só teu.

Consulta [`persona-template/en.md`](./persona-template/en.md) para un exemplo, ou [`persona-template/ja.md`](./persona-template/ja.md) para unha versión en xaponés.

---

## FAQ

**P: Funciona sen GPU?**
Si. O modelo de embedding (multilingual-e5-small) funciona ben na CPU. Unha GPU faino máis rápido pero non é necesaria.

**P: Podo usar unha cámara que non sexa Tapo?**
Calquera cámara que soporte ONVIF + RTSP debería funcionar. Probandose cunha Tapo C220.

**P: Os meus datos envíanse a algún sitio?**
Imaxes e texto envíanse á API do LLM elixido para procesamento. Os recordos gárdanse localmente en `~/.familiar_ai/`.

**P: Por que o axente escribe `（...）` en vez de falar?**
Asegúrate de que `ELEVENLABS_API_KEY` está configurado. Sen el, a voz está desactivada e o axente volve ao texto.

## Antecedentes técnicos

Tes curiosidade sobre como funciona? Consulta [docs/technical.md](./docs/technical.md) para as decisións de investigación e deseño detrás de familiar-ai — ReAct, SayCan, Reflexion, Voyager, o sistema de desexo, e máis.

---

## Contribuíndo

familiar-ai é un experimento aberto. Se algo diso resoa contigo — técnica ou filosóficamente — as contribucións son moi benvidas.

**Bons lugares para comezar:**

| Área | Que se necesita |
|------|-----------------|
| Novo hardware | Soporte para máis cámaras (RTSP, IP Webcam), micrófonos, actuadores |
| Novas ferramentas | Búsqueda web, automatización do fogar, calendario, calquera cousa a través de MCP |
| Novos backends | Calquera LLM ou modelo local que se ajuste á interface `stream_turn` |
| Plantillas de persona | Plantillas ME.md para diferentes linguas e personalidades |
| Investigación | Mellores modelos de desexo, recuperación de memoria, estímulos de teoría da mente |
| Documentación | Tutoriais, guías, traducións |

Consulta [CONTRIBUTING.md](./CONTRIBUTING.md) para a configuración do dev, estilo de código, e directrices de PR.

Se non estás seguro por onde empezar, [abre un problema](https://github.com/lifemate-ai/familiar-ai/issues) — estou feliz de indicarte a dirección correcta.

---

## Licenza

[MIT](./LICENSE)
