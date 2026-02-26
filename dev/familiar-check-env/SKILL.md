---
name: familiar-check-env
description: Validate the .env configuration for familiar-ai. Detects common misconfigurations like wrong ports, missing MODEL, or TOOLS_MODE issues that cause silent failures or timeouts.
---

# familiar-check-env

Validate the `.env` (or environment) for familiar-ai and surface likely misconfigurations before they cause cryptic errors.

## When to Use

- "It's not responding" / "Request timed out" with a local LLM
- Setting up familiar-ai for the first time
- Switching between platforms (Anthropic → LM Studio → Ollama, etc.)
- After upgrading familiar-ai when new env vars were added

---

## What to Check

Read the current `.env` (or `os.environ`) and validate each section:

---

### Section 1: Core LLM

| Var | Expected | Common Mistake |
|-----|----------|----------------|
| `PLATFORM` | `anthropic` / `openai` / `gemini` / `kimi` | Typo, or not set (defaults to `anthropic`) |
| `API_KEY` | Non-empty | Forgotten, wrong key for the platform |
| `MODEL` | Platform-appropriate model ID | Not set → defaults to `claude-haiku-4-5-20251001` or `gpt-4o-mini`, which LM Studio won't serve |
| `BASE_URL` | Valid URL | Wrong port (LM Studio=1234, Ollama=11434), HTTP vs HTTPS |
| `TOOLS_MODE` | `prompt` for local models, `native` for real OpenAI | Missing → now defaults to `prompt` for non-OpenAI (was `native` before v0.x) |

**Platform-specific checks:**

- `PLATFORM=anthropic` → `API_KEY` should start with `sk-ant-`; `BASE_URL` and `TOOLS_MODE` are ignored
- `PLATFORM=openai` + `BASE_URL` not set → falls back to `https://api.openai.com/v1` (real OpenAI)
- `PLATFORM=openai` + `BASE_URL` set to local → warn if `TOOLS_MODE=native` (may cause timeout on models that don't support function calling)
- `PLATFORM=gemini` → `API_KEY` should be a Google AI Studio key; `BASE_URL` is ignored
- `PLATFORM=kimi` → `API_KEY` is a Moonshot AI key

**LM Studio specific:**
- Default port is **1234**, not 11434
- LM Studio only binds to `localhost` by default; cross-machine access requires enabling "Allow connections from network" in LM Studio settings
- `MODEL` must exactly match the identifier shown in LM Studio's loaded model list

**Ollama specific:**
- Default port is **11434**
- Ollama binds to `0.0.0.0` by default, so cross-machine access usually works without extra config

---

### Section 2: Camera (optional)

| Var | Notes |
|-----|-------|
| `CAMERA_HOST` | IP of the camera on the local network |
| `CAMERA_USERNAME` | Usually `admin` |
| `CAMERA_PASSWORD` | Required if `CAMERA_HOST` is set |
| `CAMERA_ONVIF_PORT` | Default `2020` for Tapo; check your camera's spec |

Warn if `CAMERA_HOST` is set but `CAMERA_PASSWORD` is empty — camera tool will silently skip init.

---

### Section 3: TTS / Voice (optional)

| Var | Notes |
|-----|-------|
| `ELEVENLABS_API_KEY` | Required for TTS |
| `ELEVENLABS_VOICE_ID` | Defaults to a built-in voice; override for custom voices |
| `GO2RTC_URL` | Default `http://localhost:1984`; only needed for camera speaker |
| `GO2RTC_STREAM` | Default `tapo_cam` |

Check that `mpv` or `ffplay` is available in PATH for local speaker playback:
```bash
which mpv || which ffplay
```

---

### Section 4: Mobility / Robot Vacuum (optional)

| Var | Notes |
|-----|-------|
| `TUYA_API_KEY` | From Tuya IoT Platform |
| `TUYA_API_SECRET` | From Tuya IoT Platform |
| `TUYA_DEVICE_ID` | The vacuum's device ID in Tuya |
| `TUYA_REGION` | `us` / `eu` / `cn` / `in` |

Mobility tool silently skips init if any of these are missing.

---

## Output Format

Report findings grouped by severity:

```
[PLATFORM: openai]
  ✅ API_KEY is set
  ✅ BASE_URL = http://192.168.10.6:1234/v1  (LM Studio)
  ⚠️  TOOLS_MODE not set → defaulting to "prompt" (correct for local models)
  ❌ MODEL not set → will request "gpt-4o-mini" which LM Studio may not serve
     Fix: set MODEL=<your-loaded-model-identifier>

[CAMERA]
  ✅ CAMERA_HOST = 192.168.10.5
  ❌ CAMERA_PASSWORD is empty → camera tool will not initialize

[TTS]
  ⚠️  ELEVENLABS_API_KEY not set → TTS disabled
  ⚠️  mpv not found in PATH, ffplay not found → no local audio playback

[MOBILITY]
  ℹ️  TUYA_* not set → mobility disabled (OK if no robot vacuum)
```

Always end with a summary:
```
Summary: 1 error, 2 warnings. Fix errors before starting the agent.
```
