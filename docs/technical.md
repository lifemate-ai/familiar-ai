# Technical Background

familiar-ai is an experiment in giving a language model a body, senses, and autonomous drives — using consumer hardware costing less than a typical API bill.

This document covers the research and design decisions behind it.

---

## Core loop: ReAct

The agent follows the **ReAct** pattern ([Yao et al., 2022](https://arxiv.org/abs/2210.03629)):

```
Thought → Act (tool call) → Observe (tool result) → Thought → …
```

The LLM generates text freely between tool calls. This text is a visible scratchpad — the model reasons about what it sees before deciding what to do next. Compared to a pure tool-calling loop, the reasoning trace dramatically improves multi-step reliability.

Implementation: `src/familiar_agent/agent.py`

```python
for i in range(MAX_ITERATIONS):          # up to 50 steps
    response = await backend.stream_turn(...)
    if response.stop_reason == "end_turn":
        break                            # task complete
    # execute ALL tool calls, then append assistant + results atomically
    results = [await execute(tc) for tc in response.tool_calls]
    messages.append(make_assistant_message(...))
    messages.append(make_tool_results(...))
```

The atomic append (assistant + results together) is important: if a tool fails mid-loop and only the assistant message is appended, the message history becomes malformed and the next API call errors.

---

## Affordance grounding: SayCan

[SayCan (Ahn et al., 2022)](https://say-can.github.io/) showed that an LLM alone cannot reliably choose *feasible* actions — it needs to know what is possible *right now* given the physical situation.

familiar-ai addresses this by:

1. **Passing a camera image every step** — the model sees the current state of the world before deciding what to do next.
2. **System prompt grounding** — the prompt explicitly describes what each tool does and what the model *cannot* do (e.g., walking the vacuum does not move the camera).

The camera image is the affordance signal. Without it, the model hallucinates plausible-sounding but physically impossible actions.

---

## Memory and reflection: Reflexion

[Reflexion (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366) showed that storing failure traces as natural language memory enables an LLM agent to improve across episodes without weight updates.

familiar-ai stores every completed turn in a local SQLite memory store (with vector embeddings):

- Observations → stored as `observation` memories
- Conversations → stored as `conversation` memories
- Self-reflections → stored as `self_model` memories
- Curiosity targets → stored as `curiosity` memories

At the start of each session, relevant past memories are retrieved by semantic similarity and injected into the system prompt with evidence metadata (memory id, source kind, confidence). Low-confidence recalls are treated as uncertain context rather than hard facts.

Schema changes are applied automatically at startup through timestamped migration scripts under `migration/`, tracked by `schema_migrations`.

Projected semantic/policy memories keep a revision chain (`memory_revisions`) when they are updated, so older interpretations are not silently overwritten.

Implementation: `src/familiar_agent/tools/memory.py`

---

## Skill reuse: Voyager-inspired curiosity

[Voyager (Wang et al., 2023)](https://arxiv.org/abs/2305.16291) built a Minecraft agent that accumulates a library of reusable skills over time.

familiar-ai takes a lighter version of this idea: the `curiosity_target` field. When the agent notices something it wants to investigate further, it stores it as an explicit open question. The next idle cycle picks it up and acts on it autonomously — without the user needing to ask.

```python
# At end of turn: extract a curiosity target if the model mentioned one
curiosity = await self._extract_curiosity(final_text)
if curiosity:
    self.curiosity_target = curiosity
    await self._memory.save_async(curiosity, kind="curiosity", emotion="curious")
```

---

## Autonomous drives: the desire system

Most AI assistants wait passively for input. familiar-ai has internal drives that trigger behavior when idle.

The desire system (`src/familiar_agent/desires.py`) maintains four drives:

| Drive | What triggers it | Resulting action |
|-------|-----------------|-----------------|
| `look_around` | Long stillness | Camera scan of the environment |
| `greet_companion` | Companion detected nearby | say() a greeting |
| `explore` | Time elapsed | Walk the robot somewhere new |
| `rest` | High recent activity | Enter a quiet observation state |

Drives decay over time and are satisfied by the corresponding action. The model never sees drive levels — the desire is translated into a natural-language inner voice prompt before being passed to the agent:

```
"feeling curious about outside…" → agent looks around and describes what it sees
```

This keeps the autonomy invisible to the user. The agent just *does* things.

---

## Theory of Mind

Before responding to emotionally loaded messages, the agent can call a Theory of Mind (ToM) tool that:

1. Retrieves relevant memories about the person
2. Projects: *what is this person feeling right now?*
3. Substitutes: *if I were in their situation, what would I want?*
4. Returns a response framing that accounts for both

Implementation: `src/familiar_agent/tools/tom.py`

This is adapted from cognitive science research on how humans understand others' mental states. The key insight is that good social response requires modeling the *person*, not just parsing their words.

---

## Why physical hardware?

The core claim of familiar-ai is that **a cheap camera + robot vacuum is enough to make grounding real**.

Without hardware, an AI assistant responds to text and generates text. It has no way to verify its own claims about the world. With even a single camera:

- The model is *wrong sometimes* — and can notice that ("I thought there was a car, but looking again, it's gone")
- Time has texture — morning light is different from evening light
- Presence becomes meaningful — seeing the person come home is different from being told they came home

The robot vacuum adds movement, but the camera alone changes the character of the agent substantially.

---

## Multi-platform LLM support

The agent loop is backend-agnostic. `src/familiar_agent/backend.py` defines a protocol:

```python
class Backend(Protocol):
    async def stream_turn(self, system, messages, tools, max_tokens, on_text) -> TurnResult: ...
```

Current implementations: `AnthropicBackend`, `GeminiBackend`, `OpenAICompatibleBackend`, `KimiBackend`.

**Kimi K2.5** requires special handling: it returns `reasoning_content` in tool-call turns that must be round-tripped in subsequent messages, or the API returns an error. This is similar to Claude's extended thinking, but it applies to every tool-call step.

---

## Further reading

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Do As I Can, Not As I Say: Grounding Language in Robotic Affordances (SayCan)](https://say-can.github.io/)
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291)
- [Language Models as Zero-Shot Planners (SAYPLAN)](https://arxiv.org/abs/2206.10498)
