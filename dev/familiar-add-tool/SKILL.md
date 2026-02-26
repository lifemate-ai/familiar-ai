---
name: familiar-add-tool
description: Scaffold a new sensor/actuator tool for familiar-ai. Generates the tool file and registers it in all required places in agent.py.
---

# familiar-add-tool

Scaffold a new tool (sensor, actuator, or service) for the familiar-ai agent.

## When to Use

- Adding a new physical sensor (microphone, temperature, GPS, …)
- Adding a new actuator (arm, LED, speaker, …)
- Wrapping a new external service (weather API, home automation, …)

## What This Skill Does

1. Creates `src/familiar_agent/tools/<name>.py` from the standard template
2. Registers the tool in `agent.py` in **all three required places**
3. Adds any new env vars to `config.py` and `.env.example`
4. Adds the tool's body description to the system prompt in `agent.py`

---

## Step 1: Gather Requirements

Ask the user (or infer from context):

- **Tool name** (snake_case, e.g. `microphone`)
- **Tool verbs** — the callable actions the agent can take (e.g. `listen`, `record`)
- **Config vars** — env vars needed (e.g. `MIC_DEVICE_INDEX`)
- **System prompt description** — how should the agent understand this body part?
- **Optional flag** — is the tool optional (guarded by config) or always available?

---

## Step 2: Create the Tool File

Create `src/familiar_agent/tools/<name>.py`:

```python
"""<Name> tool — <one-line description>."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class <Name>Tool:
    """<Description>."""

    def __init__(self, <config_params>) -> None:
        self.<param> = <param>
        # TODO: initialize hardware/client

    async def <verb>(self, <args>) -> tuple[str, str | None]:
        """<What this action does>. Returns (text_result, image_b64_or_None)."""
        # TODO: implement
        return "Not implemented yet.", None

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "<verb>",
                "description": "<What the agent does when calling this tool>.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        # "<param>": {"type": "string", "description": "..."},
                    },
                    "required": [],
                },
            },
        ]

    async def call(self, tool_name: str, tool_input: dict) -> tuple[str, str | None]:
        if tool_name == "<verb>":
            return await self.<verb>(**tool_input)
        return f"Unknown tool: {tool_name}", None
```

**Key rules for tool files:**
- `call()` always returns `tuple[str, str | None]` — text result + optional JPEG base64
- `get_tool_definitions()` uses Anthropic input_schema format
- Keep each tool in its own file, one class per file

---

## Step 3: Register in `agent.py`

Touch **three** places:

### 3a. Import (top of file)
```python
from .tools.<name> import <Name>Tool
```

### 3b. `_init_tools()` — instantiate if config is available
```python
# In Agent._init_tools():
<name>_cfg = self.config.<name>          # or read directly from config
if <name>_cfg.<required_field>:
    self._<name> = <Name>Tool(<name>_cfg.<field>, ...)
```

### 3c. `_all_tool_defs` property — expose definitions
```python
# In Agent._all_tool_defs:
if self._<name>:
    defs.extend(self._<name>.get_tool_definitions())
```

### 3d. `_execute_tool()` — route calls
```python
# In Agent._execute_tool():
<name>_tools = {"<verb1>", "<verb2>"}

if name in <name>_tools and self._<name>:
    return await self._<name>.call(name, tool_input)
```

Also add `self._<name>: <Name>Tool | None = None` to `__init__`.

---

## Step 4: Update `config.py`

If new env vars are needed, add a config dataclass:

```python
@dataclass
class <Name>Config:
    <field>: str = field(default_factory=lambda: os.environ.get("<ENV_VAR>", ""))
```

And add it to `AgentConfig`:
```python
<name>: <Name>Config = field(default_factory=<Name>Config)
```

---

## Step 5: Update System Prompt in `agent.py`

Add the tool to the body parts description in `SYSTEM_PROMPT`:

```
- <Body part name> (<verb>): <How the agent should think about and use this>.
```

Keep it grounded and concrete — e.g. "Ears (listen): Your hearing. Calling listen() records audio from the microphone and transcribes it."

---

## Step 6: Update `.env.example`

```bash
# <Name> tool
<ENV_VAR>=
```

---

## Checklist Before Finishing

- [ ] `tools/<name>.py` created with `get_tool_definitions()` and `call()`
- [ ] Import added to `agent.py`
- [ ] `_init_tools()` instantiates the tool (with optional guard)
- [ ] `_all_tool_defs` includes it
- [ ] `_execute_tool()` routes to it
- [ ] `config.py` has new config class (if needed)
- [ ] `AgentConfig` references the new config (if needed)
- [ ] `SYSTEM_PROMPT` describes the new body part
- [ ] `.env.example` documents new env vars
- [ ] Run `uv run ruff check . && uv run ruff format .` before committing
