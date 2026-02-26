---
name: familiar-debug-loop
description: Debug a stuck or misbehaving familiar-ai ReAct loop. Diagnoses tool-call failures, model output issues, prompt-mode parsing errors, and silent tool skips.
---

# familiar-debug-loop

Diagnose why the familiar-ai agent loop is stuck, looping, or behaving unexpectedly.

## When to Use

- Agent responds but never calls any tools
- Agent keeps calling the same tool in a loop
- "Tool not available" errors despite the tool being configured
- TTS / camera / mobility silently does nothing
- Agent finishes immediately without doing anything useful
- Weird JSON parse errors in prompt-mode tool calling

---

## Diagnostic Flow

Work through these checks in order. Stop at the first confirmed cause.

---

### Check 1: Tool Availability

The agent skips tool init silently if env vars are missing. Verify each tool actually initialized:

```python
# In a Python REPL or quick script:
from familiar_agent.config import AgentConfig
from familiar_agent.agent import FamiliarAgent

cfg = AgentConfig()
agent = FamiliarAgent(cfg)

print("Camera:", agent._camera)     # None = not initialized
print("Mobility:", agent._mobility) # None = not initialized
print("TTS:", agent._tts)           # None = not initialized
print("Tools:", [t["name"] for t in agent._all_tool_defs])
```

If a tool is `None`, run **familiar-check-env** to find the missing config.

---

### Check 2: Model is Generating Tool Calls

In `TOOLS_MODE=prompt`, the model must output `<tool_call>{...}</tool_call>` blocks.
In `TOOLS_MODE=native`, the model must return `finish_reason="tool_calls"`.

**Enable debug logging** to see raw model output:

```bash
# .env
LOG_LEVEL=DEBUG
```

Or in Python:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Look for lines like:
```
DEBUG familiar_agent.backend - ...
```

**Prompt-mode symptoms:**
- Model outputs `<tool_call>` but nothing happens → check `_TOOL_CALL_RE` regex parse
- Model outputs plain text instead of `<tool_call>` → model isn't following the tools prompt; try a different/larger model
- Model outputs `<tool_call>` then keeps talking → model ignored the "STOP after tool_call" instruction; try `TOOLS_MODE=prompt` with a stronger system prompt hint

**Native-mode symptoms:**
- `finish_reason` is `"stop"` instead of `"tool_calls"` → model doesn't support native function calling; switch to `TOOLS_MODE=prompt`
- Request timeout → model hangs on `tools` parameter; switch to `TOOLS_MODE=prompt`

---

### Check 3: Tool Call Routing

In `agent.py → _execute_tool()`, tool calls are routed by name string matching.

If you added a new tool but it's returning `"Tool 'xyz' not available"`:

1. Check the tool name in `get_tool_definitions()` matches exactly the string being routed in `_execute_tool()`
2. Check the tool's set is included in `_execute_tool()`:
   ```python
   <name>_tools = {"<verb1>", "<verb2>"}
   if name in <name>_tools and self._<name>:
       return await self._<name>.call(name, tool_input)
   ```
3. Check `self._<name>` is not `None` (see Check 1)

---

### Check 4: Camera Issues

**"see() returns no image"**
- RTSP stream URL is wrong → check `CAMERA_HOST`, `CAMERA_ONVIF_PORT`
- Camera is offline → try pinging `CAMERA_HOST`
- ffmpeg not in PATH → `which ffmpeg`

**"look() does nothing"**
- ONVIF PTZ not supported by camera model → check camera spec
- Wrong ONVIF port → default for Tapo is `2020`, other brands vary

**"Connection refused"**
- ONVIF port not open → check firewall, camera settings

---

### Check 5: TTS Issues

**"say() returns success but no sound"**
- go2rtc not running → check `~/.cache/embodied-claude/go2rtc/go2rtc` exists and is executable
- Camera doesn't support backchannel audio → go2rtc fallback should kick in and play locally
- `mpv` / `ffplay` not in PATH → no local playback fallback; install one

**"TTS API failed (401)"**
- `ELEVENLABS_API_KEY` is wrong or expired

**"TTS API failed (422)"**
- Text too long → truncated at 200 chars automatically; if still failing, check for special characters

---

### Check 6: Agent Loop Logic

**Agent loops on the same action:**
- Check `MAX_ITERATIONS` (default 50) in `agent.py`
- Likely the model isn't getting a useful result back from the tool and keeps retrying
- Look at what the tool is returning — is it a meaningful observation or an error message?

**Agent ends turn immediately after one action:**
- System prompt says "speak after every see()" — if `say()` is the last required step, the loop ends naturally
- Check if `stop_reason == "end_turn"` is coming too early — model may be concluding the task prematurely

**Agent never enters tool-calling mode (just talks):**
- `_all_tool_defs` returns empty list → all tools are `None`; run Check 1
- Model ignoring tools prompt → try a VLM with stronger instruction following (qwen3-vl, llava-next, etc.)

---

### Check 7: Memory Issues

**"recall() returns nothing"**
- DB file not created yet → first run
- Embedding model not downloaded → check `~/.cache/huggingface/`
- DB path wrong → check `MEMORY_DB_PATH` or default `~/.familiar_ai/observations.db`

**"remember() hangs"**
- Embedding model loading for the first time (downloads ~117MB) → wait
- Torch not installed → `uv add torch --extra-index-url https://download.pytorch.org/whl/cpu`

---

## Quick Reference: Log Levels

```bash
LOG_LEVEL=DEBUG    # Full backend request/response, tool routing
LOG_LEVEL=INFO     # Tool init, backend selection, key events (default)
LOG_LEVEL=WARNING  # Only problems
```

Log file location: `~/.cache/familiar-ai/familiar-ai.log`

---

## Useful One-Liners

```bash
# Check what tools are available given current .env
uv run python -c "
from familiar_agent.config import AgentConfig
from familiar_agent.agent import FamiliarAgent
a = FamiliarAgent(AgentConfig())
print([t['name'] for t in a._all_tool_defs])
"

# Tail the log
tail -f ~/.cache/familiar-ai/familiar-ai.log

# Check DB exists and has records
sqlite3 ~/.familiar_ai/observations.db "SELECT count(*) FROM observations;"
```
