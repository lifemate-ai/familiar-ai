```markdown
# familiar-ai 🐾

**당신과 함께하는 AI** — 눈, 목소리, 다리, 그리고 기억을 가진.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

[→ English README](../README.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai는 당신의 집에서 함께 사는 AI 동반자입니다.
몇 분 안에 설정할 수 있습니다. 코딩은 필요 없습니다.

이 AI는 카메라를 통해 실제 세계를 인식하고, 로봇 몸체로 이동하며, 소리 내어 말하고, 본 것을 기억합니다. 이름을 주고, 성격을 정하고, 당신과 함께 살도록 하세요.

## 할 수 있는 일

- 👁 **보는 것** — Wi-Fi PTZ 카메라 또는 USB 웹캠에서 이미지를 캡처합니다.
- 🔄 **주위를 살피는 것** — 카메라를 팬 및 틸트하여 주변을 탐색합니다.
- 🦿 **이동하는 것** — 로봇 진공청소기를 운전하여 방을 돌아다닙니다.
- 🗣 **말하는 것** — ElevenLabs TTS를 통해 말합니다.
- 🎙 **듣는 것** — ElevenLabs Realtime STT를 통한 핸즈프리 음성 입력 (선택 사항)
- 🧠 **기억하는 것** — 의미 기반 검색 (SQLite + 임베딩)을 통해 적극적으로 기억을 저장하고 불러옵니다.
- 🫀 **마음 이론** — 대답하기 전에 상대방의 관점을 취합니다.
- 💭 **욕망** — 자율적 행동을 유도하는 내적 충동을 지닙니다.

## 작동 방식

familiar-ai는 선택한 LLM에 의해 구동되는 [ReAct](https://arxiv.org/abs/2210.03629) 루프를 실행합니다. 세계를 도구를 통해 인식하고, 다음에 무엇을 할지 생각하고, 행동합니다 — 마치 사람이 하는 것처럼.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

유휴 상태일 때, 그것은 자신의 욕망에 따라 행동합니다: 호기심, 밖을 보고 싶어함, 함께 사는 사람을 그리워함.

## 시작하기

### 1. uv 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. ffmpeg 설치

ffmpeg는 **필수**로 카메라 이미지 캡처 및 오디오 재생에 필요합니다.

| OS | 명령어 |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — 또는 [ffmpeg.org](https://ffmpeg.org/download.html)에서 다운로드하여 PATH에 추가 |
| Raspberry Pi | `sudo apt install ffmpeg` |

확인: `ffmpeg -version`

### 3. 클론 및 설치

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. 설정

```bash
cp .env.example .env
# 설정으로 .env 파일을 편집
```

**최소 필요 사항:**

| 변수 | 설명 |
|------|------|
| `PLATFORM` | `anthropic` (기본값) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | 선택한 플랫폼의 API 키 |

**선택 사항:**

| 변수 | 설명 |
|------|------|
| `MODEL` | 모델 이름 (플랫폼마다 합리적인 기본값) |
| `AGENT_NAME` | TUI에 표시되는 이름 (예: `Yukine`) |
| `CAMERA_HOST` | ONVIF/RTSP 카메라의 IP 주소 |
| `CAMERA_USER` / `CAMERA_PASS` | 카메라 자격 증명 |
| `ELEVENLABS_API_KEY` | 음성 출력을 위한 — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | 항상 활성화된 핸즈프리 음성 입력을 위해 `true`로 설정 (필수: `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | 오디오 재생 위치: `local` (PC 스피커, 기본값) \| `remote` (카메라 스피커) \| `both` |
| `THINKING_MODE` | Anthropic 전용 — `auto` (기본값) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | 적응형 사고 노력: `high` (기본값) \| `medium` \| `low` \| `max` (Opus 4.6 전용) |

### 5. 친숙한 AI 만들기

```bash
cp persona-template/en.md ME.md
# ME.md를 편집 — 이름과 성격을 부여
```

### 6. 실행

```bash
./run.sh             # 텍스트 TUI (추천)
./run.sh --no-tui    # 일반 REPL
```

---

## LLM 선택하기

> **추천: Kimi K2.5** — 지금까지 테스트된 최고의 에이전트 성능. 맥락을 인식하고, 후속 질문을 하며, 다른 모델과는 다르게 자율적으로 행동합니다. Claude Haiku와 비슷한 가격입니다.

| 플랫폼 | `PLATFORM=` | 기본 모델 | 키 받는 곳 |
|----------|------------|---------------|-----------------|
| **Moonshot Kimi K2.5** | `kimi` | `kimi-k2.5` | [platform.moonshot.ai](https://platform.moonshot.ai) |
| Z.AI GLM | `glm` | `glm-4.6v` | [api.z.ai](https://api.z.ai) |
| Anthropic Claude | `anthropic` | `claude-haiku-4-5-20251001` | [console.anthropic.com](https://console.anthropic.com) |
| Google Gemini | `gemini` | `gemini-2.5-flash` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `openai` | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| OpenAI 호환 (Ollama, vllm…) | `openai` + `BASE_URL=` | — | — |
| OpenRouter.ai (다중 공급자) | `openai` + `BASE_URL=https://openrouter.ai/api/v1` | — | [openrouter.ai](https://openrouter.ai) |
| **CLI 도구** (claude -p, ollama…) | `cli` | (명령어) | — |

**Kimi K2.5 `.env` 예시:**
```env
PLATFORM=kimi
API_KEY=sk-...   # from platform.moonshot.ai
AGENT_NAME=Yukine
```

**Z.AI GLM `.env` 예시:**
```env
PLATFORM=glm
API_KEY=...   # from api.z.ai
MODEL=glm-4.6v   # 비전 지원; glm-4.7 / glm-5 = 텍스트 전용
AGENT_NAME=Yukine
```

**Google Gemini `.env` 예시:**
```env
PLATFORM=gemini
API_KEY=AIza...   # from aistudio.google.com
MODEL=gemini-2.5-flash  # 또는 더 높은 성능을 위해 gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` 예시:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # 선택 사항: 모델 지정
AGENT_NAME=Yukine
```

> **참고:** 로컬/NVIDIA 모델을 비활성화하려면 `BASE_URL`을 `http://localhost:11434/v1`와 같은 로컬 엔드포인트로 설정하지 않으면 됩니다. 대신 클라우드 공급자를 사용하세요.

**CLI 도구 `.env` 예시:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = 프롬프트 인자
# MODEL=ollama run gemma3:27b  # Ollama — {}, 프롬프트는 stdin을 통해 전달
```

---

## MCP 서버

familiar-ai는 모든 [MCP (모델 컨텍스트 프로토콜)](https://modelcontextprotocol.io) 서버에 연결할 수 있습니다. 이를 통해 외부 메모리, 파일 시스템 접근, 웹 검색 또는 기타 도구를 연결할 수 있습니다.

서버를 `~/.familiar-ai.json`에 구성하세요 (Claude Code와 같은 형식):

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

두 가지 전송 유형이 지원됩니다:
- **`stdio`**: 로컬 하위 프로세스 시작 (`command` + `args`)
- **`sse`**: HTTP+SSE 서버에 연결 (`url`)

구성 파일 위치는 `MCP_CONFIG=/path/to/config.json`으로 재정의할 수 있습니다.

---

## 하드웨어

familiar-ai는 당신이 가진 하드웨어와 함께 작동합니다 — 또는 하드웨어가 전혀 없어도 괜찮습니다.

| 부품 | 기능 | 예시 | 필수 여부 |
|------|------|------|-----------|
| Wi-Fi PTZ 카메라 | 눈 + 목 | Tapo C220 (~$30) | **추천** |
| USB 웹캠 | 눈 (고정) | 어떤 UVC 카메라 | **추천** |
| 로봇 진공청소기 | 다리 | Tuya 호환 모델 | 아니요 |
| PC / Raspberry Pi | 두뇌 | Python이 실행되는 모든 것 | **예** |

> **카메라는 강력히 추천됩니다.** 없으면 familiar-ai는 여전히 말할 수 있지만, 세상을 볼 수 없으니 그게 핵심입니다.

### 최소 설정 (하드웨어 없음)

해보고 싶으신가요? API 키만 필요합니다:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh`를 실행하고 대화를 시작하세요. 필요에 따라 하드웨어를 추가하세요.

### Wi-Fi PTZ 카메라 (Tapo C220)

1. Tapo 앱에서: **설정 → 고급 → 카메라 계정** — 로컬 계정을 생성하세요 (TP-Link 계정 아님).
2. 라우터의 장치 목록에서 카메라의 IP를 찾으세요.
3. `.env`에 설정:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### 음성 (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/)에서 API 키를 받으세요.
2. `.env`에 설정:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # 선택 사항, 생략하면 기본 음성을 사용
   ```

재생 위치는 `TTS_OUTPUT`에 의해 제어됩니다:

```env
TTS_OUTPUT=local    # PC 스피커 (기본값)
TTS_OUTPUT=remote   # 카메라 스피커만
TTS_OUTPUT=both     # 카메라 스피커 + PC 스피커 동시에
```

#### A) 카메라 스피커 (go2rtc 통해)

`TTS_OUTPUT=remote` (또는 `both`)로 설정하세요. [go2rtc](https://github.com/AlexxIT/go2rtc/releases)가 필요합니다:

1. [릴리즈 페이지](https://github.com/AlexxIT/go2rtc/releases)에서 바이너리를 다운로드합니다:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. 해당 위치에 배치하고 이름을 변경합니다:
   ```
   # Linux / macOS
   ~/.cache/embodied-claude/go2rtc/go2rtc          # chmod +x 필요

   # Windows
   %USERPROFILE%\.cache\embodied-claude\go2rtc\go2rtc.exe
   ```

3. 같은 디렉토리에 `go2rtc.yaml` 생성:
   ```yaml
   streams:
     tapo_cam:
       - rtsp://YOUR_CAM_USER:YOUR_CAM_PASS@YOUR_CAM_IP/stream1
   ```
   로컬 카메라 계정 자격 증명을 사용하세요 (TP-Link 클라우드 계정 아님).

4. familiar-ai는 시작 시 go2rtc를 자동으로 시작합니다. 카메라가 양방향 오디오를 지원하면, 음성이 카메라 스피커에서 재생됩니다.

#### B) 로컬 PC 스피커

기본값(`TTS_OUTPUT=local`). 다음 순서로 플레이어를 시도합니다: **paplay** → **mpv** → **ffplay**. `TTS_OUTPUT=remote`로 설정하고 go2rtc가 사용 불가능할 때 대체로 사용됩니다.

| OS | 설치 |
|----|------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (또는 `pulseaudio-utils` 통해 `paplay`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env`에 `PULSE_SERVER=unix:/mnt/wslg/PulseServer` 설정 |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — 다운로드하고 PATH에 추가, **또는** `winget install ffmpeg` |

> 오디오 플레이어가 없으면 음성이 여전히 생성되지만, 재생되지 않습니다.

### 음성 입력 (Realtime STT)

`.env`에 `REALTIME_STT=true`로 설정하여 항상 켜져 있는 핸즈프리 음성 입력을 활성화합니다:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS와 동일한 키
```

familiar-ai는 마이크로폰 오디오를 ElevenLabs Scribe v2로 스트리밍하고, 발화를 멈추면 자동으로 기록을 커밋합니다. 버튼 누르지 않아도 됩니다. 푸시 투 토크 모드(Ctrl+T)와 동시에 사용 가능.

---

## TUI

familiar-ai에는 [Textual](https://textual.textualize.io/)로 구축된 터미널 UI가 포함되어 있습니다:

- 라이브 스트리밍 텍스트와 함께 스크롤 가능한 대화 기록
- `/quit`, `/clear`를 위한 탭 완전 자동 완성
- 에이전트가 생각하는 동안 입력하여 중단 가능
- **대화 기록**가 자동으로 `~/.cache/familiar-ai/chat.log`에 저장됩니다.

다른 터미널에서 로그를 따라가려면 (복사-붙여넣기를 위해 유용):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## 성격 (ME.md)

당신의 친숙한 AI의 성격은 `ME.md`에 저장됩니다. 이 파일은 gitignore 되어 있으므로 오직 당신만의 것입니다.

[`persona-template/en.md`](./persona-template/en.md)에서 예제를 보거나, 일본어 버전은 [`persona-template/ja.md`](./persona-template/ja.md)에서 확인하세요.

---

## 자주 묻는 질문

**Q: GPU 없이도 작동하나요?**
네. 임베딩 모델 (multilingual-e5-small)은 CPU에서 잘 작동합니다. GPU가 있으면 더 빨라지지만 필수는 아닙니다.

**Q: Tapo 이외의 카메라도 쓸 수 있나요?**
ONVIF + RTSP를 지원하는 카메라라면 어떤 카메라도 작동해야 합니다. Tapo C220에서 테스트했습니다.

**Q: 내 데이터가 어딘가로 전송되나요?**
이미지와 텍스트는 선택한 LLM API로 전송되어 처리됩니다. 기억은 로컬의 `~/.familiar_ai/`에 저장됩니다.

**Q: 에이전트가 `（...）`라고 쓰는 이유는 무엇인가요?**
`ELEVENLABS_API_KEY`가 설정되어 있는지 확인하세요. 그렇지 않으면 음성이 비활성화되어 에이전트는 텍스트로 대체됩니다.

## 기술 배경

어떻게 작동하는지 궁금한가요? familiar-ai의 연구와 설계 결정에 대한 내용을 보려면 [docs/technical.md](./docs/technical.md)를 참고하세요 — ReAct, SayCan, Reflexion, Voyager, 욕망 시스템 등.

---

## 기여하기

familiar-ai는 열린 실험입니다. 이 내용이 기술적이든 철학적이든 상관없이 공감이 간다면 기여를 환영합니다.

**시작하기 좋은 곳:**

| 영역 | 필요한 것 |
|------|------------|
| 새로운 하드웨어 | 더 많은 카메라 (RTSP, IP 웹캠), 마이크, 액추에이터 지원 |
| 새로운 도구 | 웹 검색, 홈 자동화, 캘린더, MCP를 통한 모든 것 |
| 새로운 백엔드 | `stream_turn` 인터페이스에 맞는 LLM 또는 로컬 모델 |
| 페르소나 템플릿 | 다양한 언어와 성격에 대한 ME.md 템플릿 |
| 연구 | 더 나은 욕망 모델, 기억 검색, 마음 이론 프롬프트 |
| 문서화 | 튜토리얼, 안내서, 번역 |

[CONTRIBUTING.md](./CONTRIBUTING.md)를 참조하여 개발 환경 설정, 코드 스타일 및 PR 가이드라인을 확인하세요.

어디서부터 시작해야 할지 모르겠다면, [이슈를 열어](https://github.com/lifemate-ai/familiar-ai/issues) 주세요 — 기꺼이 방향을 알려드리겠습니다.

---

## 라이선스

[MIT](./LICENSE)
```
