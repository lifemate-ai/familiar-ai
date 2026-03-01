# familiar-ai 🐾

**Uma IA que vive ao seu lado** — com olhos, voz, pernas e memória.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai é um companheiro de IA que vive na sua casa. Configure em minutos. Nenhuma codificação necessária.

Ele percebe o mundo real através de câmeras, se move em um corpo robô, fala em voz alta e se lembra do que vê. Dê-lhe um nome, escreva sua personalidade e deixe-o viver com você.

## O que ele pode fazer

- 👁 **Ver** — captura imagens de uma câmera PTZ Wi-Fi ou webcam USB
- 🔄 **Olhar ao redor** — movimenta e inclina a câmera para explorar os arredores
- 🦿 **Mover** — dirige um aspirador robô para circular pelo ambiente
- 🗣 **Falar** — conversa via ElevenLabs TTS
- 🎙 **Ouvir** — entrada de voz sem uso das mãos via ElevenLabs Realtime STT (opcional)
- 🧠 **Lembrar** — armazena ativamente e recupera memórias com busca semântica (SQLite + embeddings)
- 🫀 **Teoria da Mente** — toma a perspectiva da outra pessoa antes de responder
- 💭 **Desejo** — possui suas próprias motivações internas que desencadeiam comportamento autônomo

## Como funciona

familiar-ai executa um loop [ReAct](https://arxiv.org/abs/2210.03629) alimentado pela sua escolha de LLM. Ele percebe o mundo através de ferramentas, pensa sobre o que fazer a seguir e age — assim como uma pessoa faria.

```
entrada do usuário
  → pensar → agir (câmera / mover / falar / lembrar) → observar → pensar → ...
```

Quando ocioso, age de acordo com seus próprios desejos: curiosidade, desejo de olhar para fora, saudade da pessoa com quem vive.

## Começando

### 1. Instalar uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instalar ffmpeg

ffmpeg é **obrigatório** para captura de imagens da câmera e reprodução de áudio.

| SO | Comando |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — ou baixe de [ffmpeg.org](https://ffmpeg.org/download.html) e adicione ao PATH |
| Raspberry Pi | `sudo apt install ffmpeg` |

Verifique: `ffmpeg -version`

### 3. Clonar e instalar

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. Configurar

```bash
cp .env.example .env
# Edite .env com suas configurações
```

**Requisitos mínimos:**

| Variável | Descrição |
|----------|-------------|
| `PLATFORM` | `anthropic` (padrão) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | Sua chave de API para a plataforma escolhida |

**Opcional:**

| Variável | Descrição |
|----------|-------------|
| `MODEL` | Nome do modelo (valores padrão sensatos por plataforma) |
| `AGENT_NAME` | Nome exibido na TUI (ex: `Yukine`) |
| `CAMERA_HOST` | Endereço IP da sua câmera ONVIF/RTSP |
| `CAMERA_USER` / `CAMERA_PASS` | Credenciais da câmera |
| `ELEVENLABS_API_KEY` | Para saída de voz — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | `true` para ativar entrada de voz sem mãos sempre ativa (requer `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | Onde reproduzir o áudio: `local` (alto-falante do PC, padrão) \| `remote` (alto-falante da câmera) \| `both` |
| `THINKING_MODE` | Apenas Anthropic — `auto` (padrão) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | Esforço de pensamento adaptativo: `high` (padrão) \| `medium` \| `low` \| `max` (apenas Opus 4.6) |

### 5. Crie seu familiar

```bash
cp persona-template/en.md ME.md
# Edite ME.md — dê um nome e personalidade a ele
```

### 6. Executar

```bash
./run.sh             # TUI textual (recomendado)
./run.sh --no-tui    # REPL simples
```

---

## Escolhendo um LLM

> **Recomendado: Kimi K2.5** — melhor desempenho agente testado até agora. Nota contexto, faz perguntas de acompanhamento e age autonomamente de maneiras que outros modelos não fazem. Preço semelhante ao Claude Haiku.

| Plataforma | `PLATFORM=` | Modelo padrão | Onde obter a chave |
|------------|------------|---------------|--------------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI-compatible (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (multi-provedor) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **Ferramenta CLI** (claude -p, ollama…) | `cli` | (o comando) | — |

**Exemplo `.env` para Kimi K2.5:**
```env
PLATFORM=kimi
API_KEY=sk-...   # da platform.moonshot.ai
AGENT_NAME=Yukine
```

**Exemplo `.env` para Z.AI GLM:**
```env
PLATFORM=glm
API_KEY=...   # da api.z.ai
MODEL=glm-4.6v   # habilitado para visão; glm-4.7 / glm-5 = apenas texto
AGENT_NAME=Yukine
```

**Exemplo `.env` para Google Gemini:**
```env
PLATFORM=gemini
API_KEY=AIza...   # da aistudio.google.com
MODEL=gemini-2.5-flash  # ou gemini-2.5-pro para maior capacidade
AGENT_NAME=Yukine
```

**Exemplo `.env` para OpenRouter.ai:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # de openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # opcional: especificar modelo
AGENT_NAME=Yukine
```

> **Nota:** Para desativar modelos locais/NVIDIA, simplesmente não defina `BASE_URL` para um ponto final local como `http://localhost:11434/v1`. Use provedores de nuvem em vez disso.

**Exemplo `.env` para ferramenta CLI:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = argumento do prompt
# MODEL=ollama run gemma3:27b  # Ollama — sem {}, prompt vai via stdin
```

---

## Servidores MCP

familiar-ai pode conectar a qualquer servidor [MCP (Modelo Contexto Protocolo)](https://modelcontextprotocol.io). Isso permite que você conecte memória externa, acesso ao sistema de arquivos, busca na web ou qualquer outra ferramenta.

Configurar servidores em `~/.familiar-ai.json` (mesmo formato que o Claude Code):

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
- **`stdio`**: inicia um subprocesso local (`command` + `args`)
- **`sse`**: conecta a um servidor HTTP+SSE (`url`)

Substitua a localização do arquivo de configuração com `MCP_CONFIG=/path/to/config.json`.

---

## Hardware

familiar-ai funciona com qualquer hardware que você tiver — ou nenhum.

| Parte | O que faz | Exemplo | Necessário? |
|------|-------------|---------|-----------|
| Câmera PTZ Wi-Fi | Olhos + pescoço | Tapo C220 (~$30) | **Recomendado** |
| Webcam USB | Olhos (fixo) | Qualquer câmera UVC | **Recomendado** |
| Aspirador robô | Pernas | Qualquer modelo compatível com Tuya | Não |
| PC / Raspberry Pi | Cérebro | Qualquer um que execute Python | **Sim** |

> **Uma câmera é fortemente recomendada.** Sem uma, familiar-ai ainda pode falar — mas não pode ver o mundo, o que é meio que o objetivo.

### Configuração mínima (sem hardware)

Só quer testar? Você só precisa de uma chave de API:

```env
PLATFORM=kimi
API_KEY=sk-...
```

Execute `./run.sh` e comece a conversar. Adicione hardware conforme necessário.

### Câmera PTZ Wi-Fi (Tapo C220)

1. No aplicativo Tapo: **Configurações → Avançado → Conta da Câmera** — crie uma conta local (não a conta TP-Link)
2. Encontre o IP da câmera na lista de dispositivos do seu roteador
3. Defina em `.env`:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=seu-usuário-local
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
TTS_OUTPUT=remote   # alto-falante da câmera apenas
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
       - rtsp://SEU_USUÁRIO_CAM:SUA_SENHA_CAM@SEU_IP_CAM/stream1
   ```
   Use as credenciais da conta local da câmera (não sua conta em nuvem TP-Link).

4. familiar-ai inicia go2rtc automaticamente na inicialização. Se sua câmera suportar áudio bidirecional (canal reverso), a voz é reproduzida pelo alto-falante da câmera.

#### B) Alto-falante local do PC

O padrão (`TTS_OUTPUT=local`). Tenta players na ordem: **paplay** → **mpv** → **ffplay**. Também é usado como uma opção de fallback quando `TTS_OUTPUT=remote` e go2rtc não está disponível.

| SO | Instalar |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (ou `paplay` via `pulseaudio-utils`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — defina `PULSE_SERVER=unix:/mnt/wslg/PulseServer` em `.env` |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — baixe e adicione ao PATH, **ou** `winget install ffmpeg` |

> Se nenhum player de áudio estiver disponível, a fala ainda será gerada — apenas não será reproduzida.

### Entrada de voz (Realtime STT)

Defina `REALTIME_STT=true` em `.env` para entrada de voz sempre ativa, sem as mãos:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # mesma chave que TTS
```

familiar-ai transmite áudio do microfone para ElevenLabs Scribe v2 e comete automaticamente a transcrição quando você para de falar. Nenhum botão é necessário. Coexiste com o modo de empurrar para falar (Ctrl+T).

---

## TUI

familiar-ai inclui uma interface terminal construída com [Textual](https://textual.textualize.io/):

- Histórico de conversas rolável com texto em tempo real
- Completamento de aba para `/quit`, `/clear`
- Interrompa o agente no meio da resposta digitando enquanto ele está pensando
- **Registro de conversa** salvo automaticamente em `~/.cache/familiar-ai/chat.log`

Para seguir o registro em outro terminal (útil para copiar-colar):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## Persona (ME.md)

A personalidade do seu familiar vive em `ME.md`. Este arquivo é gitignored — é só seu.

Veja [`persona-template/en.md`](./persona-template/en.md) para um exemplo, ou [`persona-template/ja.md`](./persona-template/ja.md) para uma versão em japonês.

---

## FAQ

**P: Funciona sem uma GPU?**  
Sim. O modelo de embeddings (multilingual-e5-small) funciona bem em CPU. Uma GPU torna mais rápido, mas não é necessária.

**P: Posso usar uma câmera diferente da Tapo?**  
Qualquer câmera que suporte ONVIF + RTSP deve funcionar. Tapo C220 é com a qual testamos.

**P: Meus dados são enviados para algum lugar?**  
Imagens e textos são enviados para a API do LLM escolhido para processamento. Memórias são armazenadas localmente em `~/.familiar_ai/`.

**P: Por que o agente escreve `（...）` em vez de falar?**  
Certifique-se de que `ELEVENLABS_API_KEY` esteja definido. Sem isso, a voz é desativada e o agente recorre ao texto.

## Contexto técnico

Curioso sobre como funciona? Veja [docs/technical.md](./docs/technical.md) para as decisões de pesquisa e design por trás do familiar-ai — ReAct, SayCan, Reflexion, Voyager, o sistema de desejo e mais.

---

## Contribuindo

familiar-ai é um experimento aberto. Se algo disso ressoa com você — tecnicamente ou filosoficamente — contribuições são muito bem-vindas.

**Bons lugares para começar:**

| Área | O que é necessário |
|------|---------------|
| Novo hardware | Suporte para mais câmeras (RTSP, IP Webcam), microfones, atuadores |
| Novas ferramentas | Busca na web, automação residencial, calendário, qualquer coisa via MCP |
| Novos backends | Qualquer LLM ou modelo local que se encaixe na interface `stream_turn` |
| Modelos de persona | Modelos ME.md para diferentes idiomas e personalidades |
| Pesquisa | Melhores modelos de desejo, recuperação de memória, prompting da teoria da mente |
| Documentação | Tutoriais, guias, traduções |

Veja [CONTRIBUTING.md](./CONTRIBUTING.md) para configuração de desenvolvimento, estilo de código e diretrizes de PR.

Se você não sabe por onde começar, [abra uma issue](https://github.com/lifemate-ai/familiar-ai/issues) — ficaremos felizes em te direcionar.  

---

## Licença

[MIT](./LICENSE)
