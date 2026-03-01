# familiar-ai 🐾

**Uma IA que vive ao seu lado** — com olhos, voz, pernas e memória.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [Disponível em 74 idiomas](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai é um companheiro de IA que vive na sua casa.
Configure-o em minutos. Sem necessidade de codificação.

Ele percebe o mundo real através de câmeras, se move em um corpo robótico, fala em voz alta e se lembra do que vê. Dê um nome a ele, escreva sua personalidade e deixe-o viver com você.

## O que ele pode fazer

- 👁 **Ver** — captura imagens de uma câmera PTZ Wi-Fi ou webcam USB
- 🔄 **Olhar ao redor** — faz panorâmicas e inclina a câmera para explorar os arredores
- 🦿 **Mover** — dirige um aspirador robô para perambular pelo ambiente
- 🗣 **Falar** — se comunica via ElevenLabs TTS
- 🎙 **Ouvir** — entrada de voz sem as mãos via ElevenLabs Realtime STT (opcional)
- 🧠 **Lembrar** — armazena e recorda ativamente memórias com busca semântica (SQLite + embeddings)
- 🫀 **Teoria da Mente** — assume a perspectiva da outra pessoa antes de responder
- 💭 **Desejo** — possui suas próprias motivações internas que acionam comportamentos autônomos

## Como funciona

familiar-ai executa um loop [ReAct](https://arxiv.org/abs/2210.03629) impulsionado pela sua escolha de LLM. Ele percebe o mundo através de ferramentas, pensa sobre o que fazer em seguida e age — assim como uma pessoa faria.

```
input do usuário
  → pensar → agir (câmera / mover / falar / lembrar) → observar → pensar → ...
```

Quando está ocioso, ele age de acordo com seus próprios desejos: curiosidade, vontade de olhar para fora, saudade da pessoa com quem vive.

## Começando

### 1. Instale o uv

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Ou: `winget install astral-sh.uv`

### 2. Instale o ffmpeg

ffmpeg é **necessário** para captura de imagem da câmera e reprodução de áudio.

| SO | Comando |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ou faça o download em [ffmpeg.org](https://ffmpeg.org/download.html) e adicione ao PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifique: `ffmpeg -version`

### 3. Clone e instale

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configure

```bash
cp .env.example .env
# Edite .env com suas configurações
```

**Mínimo necessário:**

| Variável | Descrição |
|----------|-------------|
| `PLATFORM` | `anthropic` (padrão) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Sua chave de API para a plataforma escolhida |

**Opcional:**

| Variável | Descrição |
|----------|-------------|
| `MODEL` | Nome do modelo (padrões sensatos por plataforma) |
| `AGENT_NAME` | Nome exibido na TUI (ex: `Yukine`) |
| `CAMERA_HOST` | Endereço IP da sua câmera ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Credenciais da câmera |
| `ELEVENLABS_API_KEY` | Para saída de voz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` para habilitar entrada de voz sem as mãos sempre ativa (requer `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Onde reproduzir áudio: `local` (alto-falante do PC, padrão) \| `remote` (alto-falante da câmera) \| `both` |
| `THINKING_MODE` | Apenas Anthropic — `auto` (padrão) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Esforço de pensamento adaptativo: `high` (padrão) \| `medium` \| `low` \| `max` (apenas Opus 4.6) |

### 5. Crie seu familiar

```bash
cp persona-template/en.md ME.md
# Edite ME.md — dê um nome e personalidade a ele
```

### 6. Execute

**macOS / Linux / WSL2:**
```bash
./run.sh             # TUI textual (recomendado)
./run.sh --no-tui    # REPL simples
```

**Windows:**
```bat
run.bat              # TUI textual (recomendado)
run.bat --no-tui     # REPL simples
```

---

## Escolhendo um LLM

> **Recomendado: Kimi K2.5** — melhor desempenho agente testado até agora. Nota o contexto, faz perguntas de acompanhamento e age autonomamente de maneiras que outros modelos não fazem. Preço semelhante ao Claude Haiku.

| Plataforma | `PLATFORM=` | Modelo padrão | Onde obter a chave |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| Compatível com OpenAI (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-fornecedor) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Ferramenta CLI** (claude -p, ollama…) | `cli` | (o comando) | — |

**Exemplo de `.env` do Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # do platform.moonshot.ai
AGENT_NAME=Yukine
```

**Exemplo de `.env` do Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # do api.z.ai
MODEL=glm-4.6v   # habilitado para visão; glm-4.7 / glm-5 = apenas texto
AGENT_NAME=Yukine
```

**Exemplo de `.env` do Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # do aistudio.google.com
MODEL=gemini-2.5-flash  # ou gemini-2.5-pro para maior capacidade
AGENT_NAME=Yukine
```

**Exemplo de `.env` do OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # do openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcional: especifique o modelo
AGENT_NAME=Yukine
```

> **Nota:** Para desativar modelos locais/NVIDIA, simplesmente não defina `BASE_URL` para um endpoint local como `http://localhost:11434/v1`. Use provedores de nuvem em vez disso.

**Exemplo de `.env` da ferramenta CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argumento do prompt
# MODEL=ollama run gemma3:27b  # Ollama — sem {}, o prompt vai via stdin
```

---

## Servidores MCP

familiar-ai pode se conectar a qualquer servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io). Isso permite que você integre memória externa, acesso ao sistema de arquivos, pesquisa na web, ou qualquer outra ferramenta.

Configure os servidores em `~/.familiar-ai.json` (mesmo formato que o Claude Code):

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

Dois tipos de transporte são suportados:
- **`stdio`**: lança um subprocesso local (`command` + `args`)
- **`sse`**: conecta a um servidor HTTP+SSE (`url`)

Substitua a localização do arquivo de configuração com `MCP_CONFIG=/caminho/para/config.json`.

---

## Hardware

familiar-ai funciona com qualquer hardware que você tenha — ou nenhum.

| Parte | O que faz | Exemplo | Necessário? |
|------|-------------|---------|-----------|
| Câmera PTZ Wi-Fi | Olhos + pescoço | Tapo C220 (~$30) | **Recomendado** |
| Webcam USB | Olhos (fixos) | Qualquer câmera UVC | **Recomendado** |
| Aspirador robô | Pernas | Qualquer modelo compatível com Tuya | Não |
| PC / Raspberry Pi | Cérebro | Qualquer coisa que execute Python | **Sim** |

> **Uma câmera é fortemente recomendada.** Sem uma, a familiar-ai ainda pode falar — mas não pode ver o mundo, o que é meio que o ponto principal.

### Configuração mínima (sem hardware)

Só quer experimentar? Você só precisa de uma chave de API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Execute `./run.sh` (macOS/Linux/WSL2) ou `run.bat` (Windows) e comece a conversar. Adicione hardware conforme necessário.

### Câmera PTZ Wi-Fi (Tapo C220)

1. No aplicativo Tapo: **Configurações → Avançado → Conta da Câmera** — crie uma conta local (não conta TP-Link)
2. Encontre o IP da câmera na lista de dispositivos do seu roteador
3. Defina em `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=seu-usuario-local
   CAMERA_PASS=sua-senha-local
   ```

### Voz (ElevenLabs)

1. Obtenha uma chave de API em [elevenlabs.io](https://elevenlabs.io/)
2. Defina em `.env`:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # opcional, usa a voz padrão se omitido
   ```

Existem dois destinos de reprodução, controlados por `TTS_OUTPUT`:

```env
TTS_OUTPUT=local    # alto-falante do PC (padrão)
TTS_OUTPUT=remote   # apenas alto-falante da câmera
TTS_OUTPUT=both     # alto-falante da câmera + alto-falante do PC simultaneamente
```

#### A) Alto-falante da câmera (via go2rtc)

Defina `TTS_OUTPUT=remote` (ou `both`). Requer [go2rtc](https://github.com/AlexxIT/go2rtc/releases):

1. Baixe o binário da [página de lançamentos](https://github.com/AlexxIT/go2rtc/releases):
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. Coloque e renomeie:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x necessário

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. Crie `go2rtc.yaml` no mesmo diretório:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://SEU_CAM_USER:SEU_CAM_PASS@SEU_CAM_IP/stream1
   ```
   Use as credenciais da conta local da câmera (não sua conta TP-Link cloud).

4. familiar-ai inicia automaticamente o go2rtc na inicialização. Se sua câmera suporta áudio bidirecional (canal de retorno), a voz é reproduzida a partir do alto-falante da câmera.

#### B) Alto-falante local do PC

O padrão (`TTS_OUTPUT=local`). Tenta reprodutores em ordem: **paplay** → **mpv** → **ffplay**. Também é utilizado como uma alternativa quando `TTS_OUTPUT=remote` e go2rtc não está disponível.

| SO | Instalação |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ou `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — defina `PULSE_SERVER=unix:/mnt/wslg/PulseServer` em `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — faça o download e adicione ao PATH, **ou** `winget install ffmpeg` |

> Se nenhum reprodutor de áudio estiver disponível, a fala ainda é gerada — mas não será reproduzida.

### Entrada de voz (Realtime STT)

Defina `REALTIME_STT=true` em `.env` para entrada de voz sem as mãos sempre ativa:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # mesma chave que para TTS
```

familiar-ai transmite áudio do microfone para o ElevenLabs Scribe v2 e auto-confirma transcrições quando você faz uma pausa ao falar. Nenhum pressionamento de botão é necessário. Coexiste com o modo de pressionar para falar (Ctrl+T).

---

## TUI

familiar-ai inclui uma interface de terminal construída com [Textual](https://textual.textualize.io/):

- Histórico de conversa rolável com texto em streaming ao vivo
- Completação de tabulação para `/quit`, `/clear`
- Interrompa o agente no meio do turno digitando enquanto ele está pensando
- **Registro de conversa** auto-salvo em `~/.cache/familiar-ai/chat.log`

Para acompanhar o registro em outro terminal (útil para copiar e colar):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

A personalidade do seu familiar vive em `ME.md`. Este arquivo é ignorado pelo git — é só seu.

Veja [`persona-template/en.md`](./persona-template/en.md) para um exemplo, ou [`persona-template/ja.md`](./persona-template/ja.md) para uma versão em japonês.

---

## FAQ

**Q: Funciona sem uma GPU?**
Sim. O modelo de embedding (multilingual-e5-small) roda bem na CPU. Uma GPU torna mais rápido, mas não é obrigatória.

**Q: Posso usar uma câmera diferente da Tapo?**
Qualquer câmera que suporte ONVIF + RTSP deve funcionar. Tapo C220 é o que testamos.

**Q: Meus dados são enviados para algum lugar?**
Imagens e textos são enviados para a API do LLM escolhido para processamento. Memórias são armazenadas localmente em `~/.familiar_ai/`.

**Q: Por que o agente escreve `（...）` em vez de falar?**
Certifique-se de que `ELEVENLABS_API_KEY` está definido. Sem isso, a voz fica desativada e o agente volta ao texto.

## Contexto técnico

Curioso sobre como funciona? Veja [docs/technical.md](./docs/technical.md) para as decisões de pesquisa e design por trás do familiar-ai — ReAct, SayCan, Reflexion, Voyager, o sistema de desejo e mais.

---

## Contribuições

familiar-ai é um experimento aberto. Se algo disso ressoa com você — tecnicamente ou filosoficamente — contribuições são muito bem-vindas.

**Boas áreas para começar:**

| Área | O que é necessário |
|------|---------------|
| Novo hardware | Suporte para mais câmeras (RTSP, Webcam IP), microfones, atuadores |
| Novas ferramentas | Pesquisa na web, automação residencial, calendário, qualquer coisa via MCP |
| Novos backends | Qualquer LLM ou modelo local que se encaixe na interface `stream_turn` |
| Modelos de persona | Templates de ME.md para diferentes idiomas e personalidades |
| Pesquisa | Melhores modelos de desejo, recuperação de memória, prompting de teoria da mente |
| Documentação | Tutoriais, guias, traduções |

Veja [CONTRIBUTING.md](./CONTRIBUTING.md) para configuração de desenvolvimento, estilo de código e diretrizes de PR.

Se você não souber por onde começar, [abra um issue](https://github.com/lifemate-ai/familiar-ai/issues) — feliz em apontá-lo na direção certa.

---

## Licença

[MIT](./LICENSE)
