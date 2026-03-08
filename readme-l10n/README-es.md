# familiar-ai 🐾

**Una IA que vive a tu lado** — con ojos, voz, patas y memoria.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Disponible en 74 idiomas](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai es un compañero de IA que vive en tu hogar. Configúralo en minutos. No se requiere programación.

Percibe el mundo real a través de cámaras, se mueve en un cuerpo robótico, habla en voz alta y recuerda lo que ve. Dale un nombre, escribe su personalidad y déjalo vivir contigo.

## Lo que puede hacer

- 👁 **Ver** — captura imágenes de una cámara PTZ Wi-Fi o webcam USB
- 🔄 **Mirar alrededor** — gira y inclina la cámara para explorar su entorno
- 🦿 **Moverse** — conduce una aspiradora robótica para recorrer la habitación
- 🗣 **Hablar** — habla a través de ElevenLabs TTS
- 🎙 **Escuchar** — entrada de voz manos libres a través de ElevenLabs Realtime STT (opcional)
- 🧠 **Recordar** — almacena y recuerda activamente recuerdos con búsqueda semántica (SQLite + embeddings)
- 🫀 **Teoría de la Mente** — adopta la perspectiva de la otra persona antes de responder
- 💭 **Deseo** — tiene sus propios impulsos internos que desencadenan un comportamiento autónomo

## Cómo funciona

familiar-ai ejecuta un bucle [ReAct](https://arxiv.org/abs/2210.03629) impulsado por tu elección de LLM. Percibe el mundo a través de herramientas, piensa en qué hacer a continuación y actúa, como lo haría una persona.

```
entrada del usuario
  → pensar → actuar (cámara / mover / hablar / recordar) → observar → pensar → ...
```

Cuando está inactivo, actúa según sus propios deseos: curiosidad, querer mirar afuera, extrañar a la persona con la que vive.

## Comenzando

### 1. Instala uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
O: `winget install astral-sh.uv`

### 2. Instala ffmpeg

ffmpeg es **requerido** para la captura de imágenes de la cámara y la reproducción de audio.

| OS | Comando |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — o descarga desde [ffmpeg.org](https://ffmpeg.org/download.html) y añade a PATH |
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
| `PLATFORM` | `anthropic` (predeterminado) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Tu clave API para la plataforma elegida |

**Opcional:**

| Variable | Descripción |
|----------|-------------|
| `MODEL` | Nombre del modelo (valores predeterminados sensatos por plataforma) |
| `AGENT_NAME` | Nombre de visualización en el TUI (ej. `Yukine`) |
| `CAMERA_HOST` | Dirección IP de tu cámara ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Credenciales de la cámara |
| `ELEVENLABS_API_KEY` | Para salida de voz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` para habilitar la entrada de voz manos libres siempre activa (requiere `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Donde reproducir audio: `local` (altavoz del PC, predeterminado) \| `remote` (altavoz de la cámara) \| `both` |
| `THINKING_MODE` | Solo Anthropic — `auto` (predeterminado) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Esfuerzo de pensamiento adaptativo: `high` (predeterminado) \| `medium` \| `low` \| `max` (solo Opus 4.6) |

### 5. Crea tu familiar

```bash
cp persona-template/en.md ME.md
# Edita ME.md — dale un nombre y personalidad
```

### 6. Ejecuta

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI textual (recomendado)
./run.sh --no-tui    # REPL simple
```

**Windows:**
```bat
run.bat              # TUI textual (recomendado)
run.bat --no-tui     # REPL simple
```

---

## Elegir un LLM

> **Recomendado: Kimi K2.5** — mejor rendimiento agentico probado hasta ahora. Nota contexto, hace preguntas de seguimiento y actúa de manera autónoma en formas que otros modelos no lo hacen. Precios similares a Claude Haiku.

| Plataforma | `PLATFORM=` | Modelo predeterminado | Dónde obtener la clave |
|------------|-------------|-----------------------|------------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
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

> **Nota:** Para deshabilitar modelos locales/NVIDIA, simplemente no establezcas `BASE_URL` en un punto final local como `http://localhost:11434/v1`. Utiliza proveedores en la nube en su lugar.

**Ejemplo de `.env` de herramienta CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argumento de prompt
# MODEL=ollama run gemma3:27b  # Ollama — sin {}, el prompt pasa por stdin
```

---

## Servidores MCP

familiar-ai puede conectarse a cualquier servidor [MCP (Modelo Contexto Protocolo)](https://modelcontextprotocol.io). Esto te permite conectar memoria externa, acceso a sistemas de archivos, búsqueda en la web o cualquier otra herramienta.

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
- **`stdio`**: lanza un subprocesso local (`command` + `args`)
- **`sse`**: conecta a un servidor HTTP+SSE (`url`)

Sobrescribe la ubicación del archivo de configuración con `MCP_CONFIG=/ruta/a/config.json`.

---

## Hardware

familiar-ai funciona con el hardware que tengas, o incluso sin ninguno.

| Parte | Lo que hace | Ejemplo | ¿Requerido? |
|-------|-------------|---------|-------------|
| Cámara PTZ Wi-Fi | Ojos + cuello | Tapo C220 (~$30, Eufy C220) | **Recomendado** |
| Webcam USB | Ojos (fijos) | Cualquier cámara UVC | **Recomendado** |
| Aspiradora robótica | Patas | Cualquier modelo compatible con Tuya | No |
| PC / Raspberry Pi | Cerebro | Cualquier cosa que ejecute Python | **Sí** |

> **Se recomienda encarecidamente una cámara.** Sin una, familiar-ai aún puede hablar, pero no puede ver el mundo, que es en parte el objetivo.

### Configuración mínima (sin hardware)

¿Solo quieres intentarlo? Solo necesitas una clave API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Ejecuta `./run.sh` (macOS/Linux/WSL2) o `run.bat` (Windows) y comienza a chatear. Agrega hardware mientras avanzas.

### Cámara PTZ Wi-Fi (Tapo C220)

1. En la aplicación Tapo: **Configuración → Avanzado → Cuenta de Cámara** — crea una cuenta local (no de TP-Link)
2. Encuentra la IP de la cámara en la lista de dispositivos de tu router
3. Establece en `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=tu-usuario-local
   CAMERA_PASS=tu-contraseña-local
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


### Voz (ElevenLabs)

1. Obtén una clave API en [elevenlabs.io](https://elevenlabs.io/)
2. Establece en `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcional, utiliza la voz predeterminada si se omite
   ```

Hay dos destinos de reproducción, controlados por `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # altavoz del PC (predeterminado)
TTS_OUTPUT=remote   # solo altavoz de la cámara
TTS_OUTPUT=both     # altavoz de la cámara + altavoz del PC simultáneamente
```

#### A) Altavoz de la cámara (a través de go2rtc)

Establece `TTS_OUTPUT=remote` (o `both`). Requiere [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Descarga el binario desde la [página de lanzamientos](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Colócalo y renómbrelo:
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
       - rtsp://TU_USUARIO_CAMARA:TU_CONTRASEÑA_CAMARA@TU_IP_CAMARA/stream1
   ```
   Usa las credenciales de cuenta de cámara local (no tu cuenta TP-Link en la nube).

4. familiar-ai inicia go2rtc automáticamente al iniciar. Si tu cámara admite audio bidireccional (canal de retorno), la voz se reproduce desde el altavoz de la cámara.

#### B) Altavoz local del PC

El predeterminado (`TTS_OUTPUT=local`). Intenta reproductores en orden: **paplay** → **mpv** → **ffplay**. También se utiliza como respaldo cuando `TTS_OUTPUT=remote` y go2rtc no está disponible.

| OS | Instalación |
|----|-------------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (o `paplay` a través de `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — establece `PULSE_SERVER=unix:/mnt/wslg/PulseServer` en `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — descarga y añade a PATH, **o** `winget install ffmpeg` |

> Si no hay disponible reproductor de audio, se generará el discurso — simplemente no se reproducirá.

### Entrada de voz (Realtime STT)

Establece `REALTIME_STT=true` en `.env` para entrada de voz siempre activa y manos libres:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # misma clave que TTS
```

familiar-ai transmite audio del micrófono a ElevenLabs Scribe v2 y guarda automáticamente las transcripciones cuando dejas de hablar. No se requiere presión de botón. Coexiste con el modo de pulsar para hablar (Ctrl+T).

---

## TUI

familiar-ai incluye una interfaz de terminal construida con [Textual](https://textual.textualize.io/):

- Historial de conversación desplazable con texto en vivo
- Autocompletado para `/quit`, `/clear`
- Interrumpe al agente a mitad de turno escribiendo mientras está pensando
- **Registro de conversación** guardado automáticamente en `~/.cache/familiar-ai/chat.log`

Para seguir el registro en otra terminal (útil para copiar y pegar):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

La personalidad de tu familiar vive en `ME.md`. Este archivo está ignorado por git — es solo tuyo.

Consulta [`persona-template/en.md`](./persona-template/en.md) para un ejemplo, o [`persona-template/ja.md`](./persona-template/ja.md) para una versión en japonés.

---

## Preguntas Frecuentes

**Q: ¿Funciona sin GPU?**
Sí. El modelo de embedding (multilingual-e5-small) funciona bien en CPU. Una GPU lo hace más rápido, pero no es necesaria.

**Q: ¿Puedo usar una cámara que no sea Tapo?**
Cualquier cámara que soporte Any camera that supports RTSP works. Tested: **Tapo C220** (ONVIF+RTSP) and **Eufy C220** (RTSP only). For Eufy, pass the full RTSP URL as `CAMERA_HOST` and set authentication to **Basic** in the app.

**Q: ¿Se envían mis datos a alguna parte?**
Las imágenes y textos se envían a tu API de LLM elegida para su procesamiento. Los recuerdos se guardan localmente en `~/.familiar_ai/`.

**Q: ¿Por qué el agente escribe `（...）` en lugar de hablar?**
Asegúrate de que `ELEVENLABS_API_KEY` esté establecido. Sin ello, la voz está deshabilitada y el agente vuelve al texto.

## Antecedentes técnicos

¿Tienes curiosidad sobre cómo funciona? Consulta [docs/technical.md](./docs/technical.md) para ver la investigación y decisiones de diseño detrás de familiar-ai — ReAct, SayCan, Reflexion, Voyager, el sistema de deseos, y más.

---

## Contribuyendo

familiar-ai es un experimento abierto. Si algo de esto resuena contigo — técnica o filosóficamente — las contribuciones son muy bienvenidas.

**Buenos lugares para comenzar:**

| Área | Qué se necesita |
|------|-----------------|
| Nuevo hardware | Soporte para más cámaras (RTSP, Webcam IP), micrófonos, actuadores |
| Nuevas herramientas | Búsqueda en la web, automatización del hogar, calendario, cualquier cosa a través de MCP |
| Nuevos backends | Cualquier LLM o modelo local que se ajuste a la interfaz `stream_turn` |
| Plantillas de personalidad | Plantillas ME.md para diferentes idiomas y personalidades |
| Investigación | Mejores modelos de deseos, recuperación de recuerdos, prompts de teoría de la mente |
| Documentación | Tutoriales, guías, traducciones |

Consulta [CONTRIBUTING.md](./CONTRIBUTING.md) para configuración de desarrollo, estilo de código y pautas de PR.

Si no estás seguro de por dónde comenzar, [abre un issue](https://github.com/lifemate-ai/familiar-ai/issues) — estaré encantado de orientarte en la dirección correcta.

---

## Licencia

[MIT](./LICENSE)
