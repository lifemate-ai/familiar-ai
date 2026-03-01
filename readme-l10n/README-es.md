# familiar-ai 🐾

**Una IA que vive junto a ti** — con ojos, voz, piernas y memoria.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai es un compañero de IA que vive en tu hogar.
Configúralo en minutos. No se requiere codificación.

Percibe el mundo real a través de cámaras, se mueve en un cuerpo robótico, habla en voz alta y recuerda lo que ve. Dale un nombre, escribe su personalidad y déjalo vivir contigo.

## Lo que puede hacer

- 👁 **Ver** — captura imágenes de una cámara PTZ Wi-Fi o webcam USB
- 🔄 **Mirar alrededor** — barra y inclina la cámara para explorar su entorno
- 🦿 **Mover** — conduce una aspiradora robot para deambular por la habitación
- 🗣 **Hablar** — habla a través de ElevenLabs TTS
- 🎙 **Escuchar** — entrada de voz manos libres a través de ElevenLabs Realtime STT (opcional)
- 🧠 **Recordar** — almacena y recuerda activamente recuerdos con búsqueda semántica (SQLite + embeddings)
- 🫀 **Teoría de la mente** — toma la perspectiva de la otra persona antes de responder
- 💭 **Deseo** — tiene sus propios impulsos internos que desencadenan comportamiento autónomo

## Cómo funciona

familiar-ai ejecuta un bucle [ReAct](https://arxiv.org/abs/2210.03629) alimentado por tu elección de LLM. Percibe el mundo a través de herramientas, piensa en qué hacer a continuación y actúa, tal como lo haría una persona.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

Cuando está inactivo, actúa según sus propios deseos: curiosidad, querer mirar afuera, extrañar a la persona con la que vive.

## Comenzando

### 1. Instala uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instala ffmpeg

ffmpeg es **requerido** para la captura de imágenes de cámara y la reproducción de audio.

| OS | Comando |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — o descárgalo de [ffmpeg.org](https://ffmpeg.org/download.html) y agrégalo a PATH |
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
# Edita .env con tu configuración
```

**Mínimo requerido:**

| Variable | Descripción |
|----------|-------------|
| `PLATFORM` | `anthropic` (por defecto) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Tu clave API para la plataforma elegida |

**Opcional:**

| Variable | Descripción |
|----------|-------------|
| `MODEL` | Nombre del modelo (valores por defecto sensatos por plataforma) |
| `AGENT_NAME` | Nombre que se muestra en la TUI (ej., `Yukine`) |
| `CAMERA_HOST` | Dirección IP de tu cámara ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Credenciales de la cámara |
| `ELEVENLABS_API_KEY` | Para salida de voz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` para habilitar la entrada de voz manos libres siempre activa (requiere `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Dónde reproducir audio: `local` (altavoz de PC, por defecto) \| `remote` (altavoz de la cámara) \| `both` |
| `THINKING_MODE` | Solo Anthropic — `auto` (por defecto) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Esfuerzo de pensamiento adaptativo: `high` (por defecto) \| `medium` \| `low` \| `max` (solo Opus 4.6) |

### 5. Crea tu familiar

```bash
cp persona-template/en.md ME.md
# Edita ME.md — dale un nombre y personalidad
```

### 6. Ejecuta

```bash
./run.sh             # TUI textual (recomendado)
./run.sh --no-tui    # REPL simple
```

---

## Elegir un LLM

> **Recomendado: Kimi K2.5** — mejor rendimiento agente probado hasta ahora. Nota el contexto, hace preguntas de seguimiento y actúa de forma autónoma en maneras que otros modelos no lo hacen. Precios similares a Claude Haiku.

| Plataforma | `PLATFORM=` | Modelo por defecto | Dónde obtener la clave |
|------------|------------|--------------------|-----------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM  | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-proveedor) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Herramienta CLI** (claude -p, ollama…) | `cli` | (el comando) | — |

**Ejemplo de `.env` de Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # de platform.moonshot.ai
AGENT_NAME=Yukine
```

**Ejemplo de `.env` de Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # de api.z.ai
MODEL=glm-4.6v   # habilitado para visión; glm-4.7 / glm-5 = solo texto
AGENT_NAME=Yukine
```

**Ejemplo de `.env` de Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # de aistudio.google.com
MODEL=gemini-2.5-flash  # o gemini-2.5-pro para mayor capacidad
AGENT_NAME=Yukine
```

**Ejemplo de `.env` de OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # de openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcional: especificar modelo
AGENT_NAME=Yukine
```

> **Nota:** Para deshabilitar modelos locales/NVIDIA, simplemente no establezcas `BASE_URL` como un endpoint local como `http://localhost:11434/v1`. Usa proveedores de la nube en su lugar.

**Ejemplo de `.env` de herramienta CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argumento de prompt
# MODEL=ollama run gemma3:27b  # Ollama — sin {}, el prompt va por stdin
```

---

## Servidores MCP

familiar-ai puede conectarse a cualquier servidor [MCP (Modelo Context Protocol)](https://modelcontextprotocol.io). Esto te permite integrar memoria externa, acceso al sistema de archivos, búsqueda en la web u otra herramienta.

Configura servidores en `~/.familiar-ai.json` (mismo formato que Claude Code):

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

Se admiten dos tipos de transporte:
- **`stdio`**: lanza un subproceso local (`command` + `args`)
- **`sse`**: conecta a un servidor HTTP+SSE (`url`)

Anula la ubicación del archivo de configuración con `MCP_CONFIG=/ruta/al/config.json`.

---

## Hardware

familiar-ai funciona con el hardware que tengas — o con ninguno.

| Parte | Lo que hace | Ejemplo | ¿Requerido? |
|-------|-------------|---------|-------------|
| Cámara PTZ Wi-Fi | Ojos + cuello | Tapo C220 (~$30) | **Recomendado** |
| Webcam USB | Ojos (fijos) | Cualquier cámara UVC | **Recomendado** |
| Aspiradora robótica | Piernas | Cualquier modelo compatible con Tuya | No |
| PC / Raspberry Pi | Cerebro | Cualquier cosa que ejecute Python | **Sí** |

> **Se recomienda encarecidamente una cámara.** Sin ella, familiar-ai aún puede hablar, pero no puede ver el mundo, que es un poco el objetivo.

### Configuración mínima (sin hardware)

¿Solo quieres probarlo? Solo necesitas una clave API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Ejecuta `./run.sh` y comienza a chatear. Agrega hardware a medida que avanzas.

### Cámara PTZ Wi-Fi (Tapo C220)

1. En la aplicación Tapo: **Configuración → Avanzado → Cuenta de Cámara** — crea una cuenta local (no cuenta TP-Link)
2. Encuentra la IP de la cámara en la lista de dispositivos de tu enrutador
3. Establece en `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=tu-usuario-local
   CAMERA_PASS=tu-contrasena-local
   ```

### Voz (ElevenLabs)

1. Obtén una clave API en [elevenlabs.io](https://elevenlabs.io/)
2. Establece en `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcional, usa la voz por defecto si se omite
   ```

Hay dos destinos de reproducción, controlados por `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # altavoz de PC (por defecto)
TTS_OUTPUT=remote   # solo altavoz de la cámara
TTS_OUTPUT=both     # altavoz de la cámara + altavoz de PC simultáneamente
```

#### A) Altavoz de la cámara (a través de go2rtc)

Establece `TTS_OUTPUT=remote` (o `both`). Requiere [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Descarga el binario de la [página de lanzamientos](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Coloca y renómbralo:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x requerido

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Crea `go2rtc.yaml` en el mismo directorio:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   Usa las credenciales de la cuenta local de la cámara (no tu cuenta de nube TP-Link).

4. familiar-ai inicia go2rtc automáticamente al iniciar. Si tu cámara admite audio bidireccional (canal de regreso), la voz se reproduce desde el altavoz de la cámara.

#### B) Altavoz local de PC

El predeterminado (`TTS_OUTPUT=local`). Intenta reproductores en orden: **paplay** → **mpv** → **ffplay**. También se usa como respaldo cuando `TTS_OUTPUT=remote` y go2rtc no está disponible.

| OS | Instalar |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (o `paplay` a través de `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — establece `PULSE_SERVER=unix:/mnt/wslg/PulseServer` en `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — descarga y agrégalo a PATH, **o** `winget install ffmpeg` |

> Si no hay un reproductor de audio disponible, la voz sigue generándose — simplemente no se reproducirá.

### Entrada de voz (Realtime STT)

Establece `REALTIME_STT=true` en `.env` para entrada de voz manos libres siempre activa:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # misma clave que para TTS
```

familiar-ai transmite audio del micrófono a ElevenLabs Scribe v2 y auto-compromete transcripciones cuando dejas de hablar. No se requiere pulsar ningún botón. Coexiste con el modo de pulsar para hablar (Ctrl+T).

---

## TUI

familiar-ai incluye una interfaz de terminal construida con [Textual](https://textual.textualize.io/):

- Historial de conversación desplazable con texto en streaming en vivo
- Completado de tabulador para `/quit`, `/clear`
- Interrumpe al agente en medio de un turno escribiendo mientras está pensando
- **Registro de conversación** guardado automáticamente en `~/.cache/familiar-ai/chat.log`

Para seguir el registro en otra terminal (útil para copiar-pegar):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

La personalidad de tu familiar vive en `ME.md`. Este archivo está ignorado por Git — es solo tuyo.

Consulta [`persona-template/en.md`](./persona-template/en.md) para un ejemplo, o [`persona-template/ja.md`](./persona-template/ja.md) para una versión en japonés.

---

## Preguntas frecuentes

**Q: ¿Funciona sin GPU?**
Sí. El modelo de embeddings (multilingual-e5-small) funciona bien en CPU. Una GPU lo hace más rápido, pero no es necesaria.

**Q: ¿Puedo usar una cámara diferente a la Tapo?**
Cualquier cámara que soporte ONVIF + RTSP debería funcionar. La Tapo C220 es con la que hemos probado.

**Q: ¿Se envían mis datos a algún lado?**
Las imágenes y el texto se envían a la API de LLM que elijas para su procesamiento. Los recuerdos se almacenan localmente en `~/.familiar_ai/`.

**Q: ¿Por qué el agente escribe `（...）` en lugar de hablar?**
Asegúrate de que `ELEVENLABS_API_KEY` esté configurado. Sin él, la voz está deshabilitada y el agente recurre al texto.

## Antecedentes técnicos

¿Tienes curiosidad sobre cómo funciona? Consulta [docs/technical.md](./docs/technical.md) para conocer las decisiones de investigación y diseño detrás de familiar-ai — ReAct, SayCan, Reflexion, Voyager, el sistema de deseos y más.

---

## Contribuyendo

familiar-ai es un experimento abierto. Si alguna de esto resuena contigo —técnicamente o filosóficamente— las contribuciones son muy bienvenidas.

**Buenos lugares para comenzar:**

| Área | Lo que se necesita |
|------|--------------------|
| Nuevo hardware | Soporte para más cámaras (RTSP, Webcam IP), micrófonos, actuadores |
| Nuevas herramientas | Búsqueda web, automatización del hogar, calendario, cualquier cosa a través de MCP |
| Nuevos backends | Cualquier LLM o modelo local que se ajuste a la interfaz `stream_turn` |
| Plantillas de persona | Plantillas de ME.md para diferentes idiomas y personalidades |
| Investigación | Mejores modelos de deseos, recuperación de memoria, indicaciones de teoría de la mente |
| Documentación | Tutoriales, guías, traducciones |

Consulta [CONTRIBUTING.md](./CONTRIBUTING.md) para la configuración de desarrollo, estilo de código y pautas de PR.

Si no estás seguro de por dónde empezar, [abre un problema](https://github.com/lifemate-ai/familiar-ai/issues) — estaré encantado de indicarte la dirección correcta.

---

## Licencia

[MIT](./LICENSE)
