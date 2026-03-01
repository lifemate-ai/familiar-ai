```markdown
# familiar-ai 🐾

**당신 곁에 사는 AI** — 눈, 목소리, 다리, 기억을 가진.

[![Lint](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml/badge.svg)](https://github.com/kmizu/familiar-ai/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/kmizu?style=flat&logo=github&color=ea4aaa)](https://github.com/sponsors/kmizu)

🌍 [74개 언어로 제공](./SUPPORTED_LANGUAGES.md)

---

[![Demo video](https://img.youtube.com/vi/hiR9uWRnjt4/0.jpg)](https://youtube.com/shorts/hiR9uWRnjt4)

familiar-ai는 당신의 집에 사는 AI 동반자입니다.
몇 분 안에 설정할 수 있습니다. 코딩은 필요 없어요.

이 AI는 카메라를 통해 실제 세계를 인식하고, 로봇 몸체로 돌아다니며, 외치고, 보는 것을 기억합니다. 이름을 지어주고, 성격을 써주고, 함께 살게 해보세요.

## 할 수 있는 것들

- 👁 **보기** — Wi-Fi PTZ 카메라 또는 USB 웹캠으로부터 이미지를 캡처
- 🔄 **주위 둘러보기** — 카메라를 팬과 틸트하여 주변을 탐색
- 🦿 **이동하기** — 로봇 청소기를 몰아 방을 돌아다님
- 🗣 **말하기** — ElevenLabs TTS를 통해 이야기함
- 🎙 **듣기** — ElevenLabs Realtime STT를 통한 핸즈프리 음성 입력 (옵트인)
- 🧠 **기억하기** — 의미 검색(SQLite + 임베딩)을 통해 기억을 능동적으로 저장하고 호출
- 🫀 **마음 이론** — 응답하기 전에 상대방의 관점을 고려
- 💭 **욕망** — 자율적인 행동을 촉발하는 내부 동기

## 작동 방식

familiar-ai는 당신이 선택한 LLM으로 구동되는 [ReAct](https://arxiv.org/abs/2210.03629) 루프를 실행합니다. 세상을 도구를 통해 인식하고, 다음에 무엇을 할지 생각하고, 행동합니다 — 마치 사람처럼.

```
user input
  → think → act (camera / move / speak / remember) → observe → think → ...
```

가만히 있을 때, 그 자체의 욕망에 따라 행동합니다: 호기심, 바깥을 보고 싶어하는 것, 함께 사는 사람을 그리워하는 것.

## 시작하기

### 1. uv 설치

**macOS / Linux / WSL2:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
또는: `winget install astral-sh.uv`

### 2. ffmpeg 설치

ffmpeg는 **카메라 이미지 캡처 및 오디오 재생**에 필요합니다.

| OS | 명령어 |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora / RHEL | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| Windows | `winget install ffmpeg` — 또는 [ffmpeg.org](https://ffmpeg.org/download.html)에서 다운로드하여 PATH에 추가 |
| Raspberry Pi | `sudo apt install ffmpeg` |

검증하기: `ffmpeg -version`

### 3. 클론하고 설치하기

```bash
git clone https://github.com/lifemate-ai/familiar-ai
cd familiar-ai
uv sync
```

### 4. 설정하기

```bash
cp .env.example .env
# .env를 여러분의 설정으로 수정
```

**최소 요구 사항:**

| 변수 | 설명 |
|----------|-------------|
| `PLATFORM` | `anthropic` (기본값) \| `gemini` \| `openai` \| `kimi` \| `glm` |
| `API_KEY` | 선택한 플랫폼의 API 키 |

**옵션:**

| 변수 | 설명 |
|----------|-------------|
| `MODEL` | 모델 이름 (플랫폼별 합리적인 기본값) |
| `AGENT_NAME` | TUI에 표시되는 이름 (예: `Yukine`) |
| `CAMERA_HOST` | ONVIF/RTSP 카메라의 IP 주소 |
| `CAMERA_USER` / `CAMERA_PASS` | 카메라 자격증명 |
| `ELEVENLABS_API_KEY` | 음성 출력을 위해 — [elevenlabs.io](https://elevenlabs.io/) |
| `REALTIME_STT` | 항상 켜진 핸즈프리 음성 입력을 활성화하려면 `true` (requires `ELEVENLABS_API_KEY`) |
| `TTS_OUTPUT` | 오디오 재생 위치: `local` (PC 스피커, 기본값) \| `remote` (카메라 스피커) \| `both` |
| `THINKING_MODE` | Anthropic 전용 — `auto` (기본값) \| `adaptive` \| `extended` \| `disabled` |
| `THINKING_EFFORT` | 적응형 사고 노력: `high` (기본값) \| `medium` \| `low` \| `max` (Opus 4.6 전용) |

### 5. 당신의 familiar 만들기

```bash
cp persona-template/en.md ME.md
# ME.md를 수정하여 이름과 성격을 부여
```

### 6. 실행하기

**macOS / Linux / WSL2:**
```bash
./run.sh             # 텍스트 TUI (추천)
./run.sh --no-tui    # 일반 REPL
```

**Windows:**
```bat
run.bat              # 텍스트 TUI (추천)
run.bat --no-tui     # 일반 REPL
```

---

## LLM 선택하기

> **추천: Kimi K2.5** — 지금까지 테스트된 최고 성능의 에이전트입니다. 문맥을 인지하고 후속 질문을 하며 다른 모델과는 다르게 자율적으로 행동합니다. Claude Haiku와 비슷한 가격입니다.

| 플랫폼 | `PLATFORM=` | 기본 모델 | 키를 받을 곳 |
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
MODEL=gemini-2.5-flash  # 또는 더 높은 기능의 gemini-2.5-pro
AGENT_NAME=Yukine
```

**OpenRouter.ai `.env` 예시:**
```env
PLATFORM=openai
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-...   # from openrouter.ai
MODEL=mistralai/mistral-7b-instruct  # 선택적: 모델 지정
AGENT_NAME=Yukine
```

> **참고:** 로컬/NVIDIA 모델을 비활성화하려면 단순히 `BASE_URL`을 `http://localhost:11434/v1`과 같은 로컬 엔드포인트로 설정하지 마세요. 클라우드 제공업체를 대신 사용하세요.

**CLI 도구 `.env` 예시:**
```env
PLATFORM=cli
MODEL=llm -m gemma3 {}        # llm CLI (https://llm.datasette.io) — {} = 프롬프트 인자
# MODEL=ollama run gemma3:27b  # Ollama — {}, 프롬프트는 stdin을 통해 전달
```

---

## MCP 서버

familiar-ai는 어떤 [MCP (Model Context Protocol)](https://modelcontextprotocol.io) 서버에도 연결할 수 있습니다. 이를 통해 외부 메모리, 파일 시스템 접근, 웹 검색 또는 기타 도구를 플러그인할 수 있습니다.

서버는 `~/.familiar-ai.json`에서 설정합니다 (Claude Code와 동일한 형식):

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

두 가지 전송 유형을 지원합니다:
- **`stdio`**: 로컬 하위 프로세스를 통합 (`command` + `args`)
- **`sse`**: HTTP+SSE 서버에 연결 (`url`)

구성 파일 위치는 `MCP_CONFIG=/path/to/config.json`으로 재정의할 수 있습니다.

---

## 하드웨어

familiar-ai는 당신이 가지고 있는 모든 하드웨어와 함께 작동하거나 전혀 필요하지 않습니다.

| 부품 | 기능 | 예시 | 필수 여부 |
|------|-------------|---------|-----------|
| Wi-Fi PTZ 카메라 | 눈 + 목 | Tapo C220 (~$30) | **추천** |
| USB 웹캠 | 눈 (고정) | 모든 UVC 카메라 | **추천** |
| 로봇 청소기 | 다리 | 모든 Tuya 호환 모델 | 아니오 |
| PC / Raspberry Pi | 두뇌 | Python이 실행되는 모든 것 | **예** |

> **카메라는 강력히 추천됩니다.** 카메라 없이도 familiar-ai는 대화할 수 있지만 세상을 볼 수 없으니, 그게 바로 전체 취지입니다.

### 최소 설정 (하드웨어 없음)

해보고 싶으신가요? API 키만 필요합니다:

```env
PLATFORM=kimi
API_KEY=sk-...
```

`./run.sh`(macOS/Linux/WSL2) 또는 `run.bat`(Windows)를 실행하고 대화를 시작하세요. 진행하면서 하드웨어를 추가하세요.

### Wi-Fi PTZ 카메라 (Tapo C220)

1. Tapo 앱에서: **설정 → 고급 → 카메라 계정** — 로컬 계정을 생성 (TP-Link 계정 아님)
2. 라우터의 장치 목록에서 카메라의 IP를 찾기
3. `.env`에서 설정:
   ```env
   CAMERA_HOST=192.168.1.xxx
   CAMERA_USER=your-local-user
   CAMERA_PASS=your-local-pass
   ```

### 음성 (ElevenLabs)

1. [elevenlabs.io](https://elevenlabs.io/)에서 API 키 받기
2. `.env`에서 설정:
   ```env
   ELEVENLABS_API_KEY=sk_...
   ELEVENLABS_VOICE_ID=...   # 선택적, 생략 시 기본 음성 사용
   ```

두 가지 재생 위치가 있으며, `TTS_OUTPUT`로 조절됩니다:

```env
TTS_OUTPUT=local    # PC 스피커 (기본)
TTS_OUTPUT=remote   # 카메라 스피커만
TTS_OUTPUT=both     # 카메라 스피커 + PC 스피커 동시에
```

#### A) 카메라 스피커 (go2rtc를 통해)

`TTS_OUTPUT=remote` (또는 `both`)로 설정합니다. [go2rtc](https://github.com/AlexxIT/go2rtc/releases)가 필요합니다:

1. [릴리스 페이지](https://github.com/AlexxIT/go2rtc/releases)에서 바이너리 다운로드:
   - Linux/macOS: `go2rtc_linux_amd64` / `go2rtc_darwin_amd64`
   - **Windows: `go2rtc_win64.exe`**

2. 아래와 같이 배치하고 이름 변경:
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
   TP-Link 클라우드 계정이 아닌 로컬 카메라 계정 자격증명을 사용합니다.

4. familiar-ai는 시작 시 go2rtc를 자동으로 시작합니다. 카메라에서 양방향 오디오(백채널)를 지원하는 경우, 음성은 카메라 스피커에서 재생됩니다.

#### B) 로컬 PC 스피커

기본값(`TTS_OUTPUT=local`). 다음 순서로 플레이어를 시도합니다: **paplay** → **mpv** → **ffplay**. `TTS_OUTPUT=remote`로 설정하고 go2rtc가 사용 불가능할 때 대체로 사용됩니다.

| OS | 설치 |
|----|---------|
| macOS | `brew install mpv` |
| Ubuntu / Debian | `sudo apt install mpv` (또는 `pulseaudio-utils`를 통해 `paplay`) |
| WSL2 / WSLg | `sudo apt install pulseaudio-utils` — `.env`에 `PULSE_SERVER=unix:/mnt/wslg/PulseServer` 설정 |
| Windows | [mpv.io/installation](https://mpv.io/installation/) — 다운로드하여 PATH에 추가, **또는** `winget install ffmpeg` |

> 오디오 플레이어가 없으면 음성은 여전히 생성되지만 재생되지 않습니다.

### 음성 입력 (Realtime STT)

`.env`에 `REALTIME_STT=true`를 설정하여 항상 켜진 핸즈프리 음성 입력을 활성화합니다:

```env
REALTIME_STT=true
ELEVENLABS_API_KEY=sk_...   # TTS와 동일한 키
```

familiar-ai는 마이크로폰 오디오를 ElevenLabs Scribe v2로 스트리밍하고, 말하기를 멈출 때 자동으로 기록을 커밋합니다. 버튼 누르는 것이 필요 없습니다. 푸시 투 톡 모드(Ctrl+T)와 공존합니다.

---

## TUI

familiar-ai는 [Textual](https://textual.textualize.io/)로 구축된 터미널 UI를 포함합니다:

- 실시간 스트리밍 텍스트로 스크롤 가능한 대화 이력
- `/quit`, `/clear`에 대한 탭 완성
- 에이전트가 생각할 때 중간에 입력하여 방해할 수 있음
- **대화 로그**는 자동으로 `~/.cache/familiar-ai/chat.log`에 저장됨

다른 터미널에서 로그를 추적하려면 (복사-붙여넣기에 유용):
```bash
tail -f ~/.cache/familiar-ai/chat.log
```

---

## 페르소나 (ME.md)

당신의 familiar의 성격은 `ME.md`에 담겨 있습니다. 이 파일은 gitignore에 포함되어 개인의 것만입니다.

예시로 [`persona-template/en.md`](./persona-template/en.md) 또는 일본어 버전인 [`persona-template/ja.md`](./persona-template/ja.md)를 확인하세요.

---

## FAQ

**Q: GPU 없이도 작동하나요?**
네. 임베딩 모델 (multilingual-e5-small)은 CPU에서 잘 작동합니다. GPU가 더 빠르지만 필요하지는 않습니다.

**Q: Tapo 외의 카메라도 사용할 수 있나요?**
ONVIF + RTSP를 지원하는 카메라는 모두 작동해야 합니다. Tapo C220으로 테스트했습니다.

**Q: 내 데이터가 어디론가 전송되나요?**
이미지와 텍스트는 선택한 LLM API로 전송되어 처리됩니다. 기억은 로컬의 `~/.familiar_ai/`에 저장됩니다.

**Q: 에이전트가 말을 하지 않고 `（...）`를 작성하는 이유는 무엇인가요?**
`ELEVENLABS_API_KEY`가 설정되어 있는지 확인하세요. 없는 경우, 음성이 비활성화되고 에이전트는 텍스트로 돌아갑니다.

## 기술적 배경

이 시스템이 어떻게 작동하는지 궁금한가요? familiar-ai의 연구 및 설계 결정에 대한 내용을 보려면 [docs/technical.md](./docs/technical.md)를 참조하세요 — ReAct, SayCan, Reflexion, Voyager, 욕망 시스템 등.

---

## 기여하기

familiar-ai는 열린 실험입니다. 기술적이든 철학적이든 이와 관련이 있다면 기여를 환영합니다.

**시작하기 좋은 곳:**

| 분야 | 필요한 것 |
|------|---------------|
| 새로운 하드웨어 | 더 많은 카메라 (RTSP, IP Webcam), 마이크, 액추에이터에 대한 지원 |
| 새로운 도구 | 웹 검색, 홈 자동화, 캘린더, MCP를 통한 기타 무엇이든지 |
| 새로운 백엔드 | `stream_turn` 인터페이스에 맞는 어떤 LLM이나 로컬 모델 |
| 페르소나 템플릿 | 다양한 언어와 성격의 ME.md 템플릿 |
| 연구 | 더 나은 욕망 모델, 기억 검색, 마음 이론 프롬프트 |
| 문서화 | 튜토리얼, 워크스루, 번역 |

개발 설정, 코드 스타일 및 PR 지침은 [CONTRIBUTING.md](./CONTRIBUTING.md)에서 확인하세요.

어디서부터 시작해야 할지 모른다면 [이슈 열기](https://github.com/lifemate-ai/familiar-ai/issues) — 기꺼이 방향을 알려드리겠습니다.

---

## 라이선스

[MIT](./LICENSE)
```
