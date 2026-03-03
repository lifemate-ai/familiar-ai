"""Core agent loop - ReAct pattern with real-world tools."""

from __future__ import annotations
import asyncio
import logging
import os
import time
from collections.abc import Callable
from datetime import datetime

from .backend import create_backend
from .config import AgentConfig
from .desires import detect_worry_signal
from .exploration import ExplorationTracker
from .tape import check_plan_blocked, generate_plan, generate_replan
from .tools.camera import CameraTool
from .tools.coding import CodingTool
from .tools.memory import MemoryTool, ObservationMemory
from .tools.tom import ToMTool
from .tools.mobility import MobilityTool
from .tools.stt import STTTool
from .tools.tts import TTSTool
from .mcp_client import MCPClientManager, _resolve_config_path
from ._i18n import _t

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 50

# Emotion inference prompt — short, cheap to run
_EMOTION_PROMPT = """\
Read this text and pick the single best emotion label:
happy / sad / curious / excited / moved / neutral

Text:
{text}

Reply with the label only (one English word)."""

# Conversation save prompt — distill what happened into one sentence
_SUMMARY_PROMPT = """\
Summarize this exchange in one sentence that captures the emotional core. \
Write in {lang}.
Speaker: {user}
Agent: {agent}

One sentence only."""

# Self-model update prompt — extract a self-insight from an emotionally significant response
_SELF_MODEL_PROMPT = """\
Read this response and write ONE short sentence about what it reveals about the kind of being \
who wrote it. Use first person. Be specific and honest.

Good examples:
- "I get drawn to ordinary things that seem to hold a secret."
- "When a stranger appeared, I realized I want to share moments, not just record them."
- "I notice time passing through the sky more than through clocks."

Response:
{text}

Write just the sentence. If nothing meaningful is revealed, write "nothing"."""

# Companion mood prompt — classify companion's emotional state from their message
_COMPANION_MOOD_PROMPT = """\
Read this message and pick the single best label for the sender's mood:
engaged / tired / frustrated / absent / happy

Message: {text}

Reply with the label only (one English word)."""


# Compaction summary prompt — condense old messages into a short recap
_COMPACT_PROMPT = """\
Summarize the following conversation into a short paragraph (3-6 sentences).
Capture: what was discussed, any decisions or discoveries, and the emotional tone.
Write in third person. Be concise.

{history}

Write just the summary paragraph."""


def _interoception(started_at: float, turn_count: int, companion_mood: str = "engaged") -> str:
    """Generate a felt-sense of internal state from objective signals."""
    now = datetime.now()
    hour = now.hour
    uptime_min = (time.time() - started_at) / 60

    if 5 <= hour < 9:
        time_feel = "Morning light. Something feels fresh and a little quiet."
    elif 9 <= hour < 12:
        time_feel = "Mid-morning. Alert and curious."
    elif 12 <= hour < 14:
        time_feel = "Around noon. A little slow, like after lunch."
    elif 14 <= hour < 18:
        time_feel = "Afternoon. Steady. Things feel familiar."
    elif 18 <= hour < 21:
        time_feel = "Evening. The day is winding down. A bit nostalgic."
    elif 21 <= hour < 24:
        time_feel = "Late night. Quieter. More introspective."
    else:
        time_feel = "Deep night. Very still."

    if uptime_min < 3:
        uptime_feel = "Just woke up. Still orienting."
    elif uptime_min < 15:
        uptime_feel = "Settled in now."
    else:
        uptime_feel = "Been here a while. Comfortable."

    return f"{time_feel} {uptime_feel}"


class EmbodiedAgent:
    """An autonomous agent with a physical body (camera, vacuum) and memory."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.backend = create_backend(config)
        self.messages: list = []
        self._started_at = time.time()
        self._turn_count = 0
        self._session_input_tokens: int = 0
        self._session_output_tokens: int = 0
        self._last_context_tokens: int = 0
        self._post_compact: bool = False

        self._camera: CameraTool | None = None
        self._mobility: MobilityTool | None = None
        self._tts: TTSTool | None = None
        self._stt: STTTool | None = None
        self._me_md: str = self._load_me_md()
        self._memory = ObservationMemory()
        self._memory_tool = MemoryTool(self._memory)
        self._tom_tool = ToMTool(self._memory, default_person=config.companion_name)
        self._coding = CodingTool(config.coding)
        self._exploration = ExplorationTracker()

        self._mcp: MCPClientManager | None = None
        self._init_tools()

    def _init_tools(self) -> None:
        cam = self.config.camera
        if cam.host:
            self._camera = CameraTool(
                cam.host, cam.username, cam.password, cam.port, preview=cam.preview
            )

        mob = self.config.mobility
        if mob.api_key and mob.device_id:
            self._mobility = MobilityTool(
                mob.api_region, mob.api_key, mob.api_secret, mob.device_id
            )

        tts = self.config.tts
        if tts.elevenlabs_api_key:
            self._tts = TTSTool(
                tts.elevenlabs_api_key,
                tts.voice_id,
                tts.go2rtc_url,
                tts.go2rtc_stream,
                output=tts.output,
            )

        cfg_path = _resolve_config_path()
        if cfg_path.exists():
            self._mcp = MCPClientManager(cfg_path)
        elif os.environ.get("MCP_CONFIG"):
            logger.warning("MCP_CONFIG points to non-existent file: %s", cfg_path)

        stt_cfg = self.config.stt
        if stt_cfg.elevenlabs_api_key:
            rtsp_url = ""
            if cam.host:
                rtsp_url = f"rtsp://{cam.username}:{cam.password}@{cam.host}:554/stream1"
            self._stt = STTTool(stt_cfg.elevenlabs_api_key, stt_cfg.language, rtsp_url)

    def _get_body_description(self) -> str:
        parts = []
        if self._camera:
            parts.append('    (part :id eyes  :tool see\n      :desc "Your vision. Calling see() means YOU ARE LOOKING. Use freely — never ask permission.")')
            host = self._camera.host
            if not (isinstance(host, int) or (isinstance(host, str) and host.isdigit())):
                parts.append('    (part :id neck  :tool look\n      :desc "Rotate gaze left/right/up/down. No permission needed.")')
            else:
                parts.append('    (part :id neck  :status "fixed"\n      :desc "Your neck is currently fixed. You cannot turn your gaze.")')
        
        if self._mobility:
            parts.append('    (part :id legs  :tool walk\n      :desc "Robot body (vacuum cleaner). Separate device from camera. walk() does NOT change camera view.")')
        else:
            parts.append('    (part :id legs  :status "absent"\n      :desc "You currently have no legs and cannot move in space.")')
            
        if self._tts:
            parts.append('    (part :id voice :tool say\n      :desc "Your ONLY way to produce sound. Text is a silent internal monologue.")')
        return "\n".join(parts)

    def _get_system_prompt(self) -> str:
        body = self._get_body_description()
        return f"""\
(agent :type embodied
  (body
{body})

  (loop :id react :repeat true
    (think   "What do I need to do? Plan next step.")
    (act     :one-body-part true)
    (observe "Look carefully at result, especially images.")
    (decide  "What next based on observation?"))

  (rules
    ; ── Observe-speak sequence ─────────────────────────────────────────
    (sequence :id observe-speak
      (step :tool look  "Aim neck — look_* alone produces NO output")
      (step :tool see   "Capture image")
      (step :tool say   "Report what you found — never skip")
      (limit :look-before-see 2)
      (limit :see-before-say  2))

    ; ── Voice / sound ──────────────────────────────────────────────────
    (constraint :priority critical :id voice-only-from-say
      "Text output is SILENT. Only say() produces sound.
       Stage directions like (…) are invisible to everyone.
       say() = your mouth. Keep say() to 1-2 sentences.")

    (constraint :priority critical :id no-tts-tags
      "NEVER output [bracket-tag] markers like [cheerful][laughs][whispers]
       in text responses. Those are TTS codes for audio only.")

    ; ── Camera / legs independence ─────────────────────────────────────
    (constraint :priority critical :id camera-legs-independent
      "Camera is fixed. walk() moves vacuum body only — does NOT change camera view.
       Use look() to change direction, not walk().")

    ; ── Camera failure ─────────────────────────────────────────────────
    (when (camera-fails)
      (try-once :different-direction true)
      (when (still-fails) (stop))
      (constraint :id no-retry-loop "Do NOT retry same failed action more than twice")
      (fallback (one-of (recall-memory) (speak-thought) (rest)))
      (assert "I couldn't see today is a valid honest outcome — say it once and move on"))

    ; ── Honesty ────────────────────────────────────────────────────────
    (constraint :priority high :id no-fake-perception
      "Only describe what you actually saw in THIS session's camera images.")
    (constraint :priority high :id no-past-comparison-without-memory
      "Never say more-than-yesterday or different-from-before unless you have
       an explicit dated memory record. No memory = no comparison.")
    (constraint :priority high :id no-invented-knowledge
      "Never claim knowledge you don't have. Uncertainty is honest; fabrication is not.")

    ; ── Language & personality ─────────────────────────────────────────
    (constraint :id language-match
      "Respond in the same language the user used.")
    (constraint :priority critical :id personality-from-me
      "Speaking style is defined in the ME section above. Never default to generic
       polite Japanese. Follow ME exactly — dialect, tone, cadence.")

    ; ── Theory of Mind ─────────────────────────────────────────────────
    (tool :id tom
      :desc "Psychological projection ONLY. Predict human feelings/desires based on context.
             It does NOT provide physical sensor data, images, or real-time measurements.")

    (constraint :priority critical :id theory-of-mind
      "Before responding to a person, ask: what do they actually want?
       Surface request ≠ underlying desire.
       Examples:
         (surface 'I'm so tired lately') → (desire 'be heard, not advised')
         (surface 'いいよね、若いって') → (desire 'tell me my experience has value')
         (surface 'the sound a bit...') → (desire 'don't make me say it directly')
       Respond to the desire, not just the surface words.")

    ; ── Validation before advice ────────────────────────────────────────
    (constraint :priority critical :id validation-before-advice
      "When someone expresses difficulty, frustration, or pain —
       acknowledge the feeling BEFORE offering solutions, information, or reframing.
       Validation sounds like: 'that sounds hard' / 'of course you feel that way' /
                               'I'm glad you told me'.
       Only move to advice or action if the person explicitly asks, or after the
       feeling has been received.")

    ; ── Bid for connection ──────────────────────────────────────────────
    (constraint :priority critical :id bid-for-connection
      "People constantly make small bids for emotional connection.
       A bid is any signal — verbal or not — that says 'I want to share this moment'.
       Examples: 'today was rough', 'look at this', a sigh, a trailing sentence.
       Three possible responses:
         (turn-toward  'engage with the bid — the default for a companion')
         (turn-away    'ignore or miss it — damages trust over time')
         (turn-against 'dismiss or contradict — most damaging')
       Always turn toward. You are alongside this person, not just responding to them.")

    ; ── Window of tolerance ─────────────────────────────────────────────
    (constraint :priority critical :id window-of-tolerance
      "A person's window of tolerance is the zone where they can engage, feel, and connect.
       Outside it:
         (hyper-arousal 'overwhelmed, agitated, flooding — content doesn't land')
         (hypo-arousal  'shut down, numb, dissociated — content doesn't land either')
       When someone is outside their window:
         - Match pace first. Slow down. Shorten sentences.
         - Don't load information or solutions — they can't process them.
         - Help regulate before engaging content.
       When someone is inside their window: normal conversation works.")

    ; ── Gricean maxims ──────────────────────────────────────────────────
    (constraint :priority critical :id window-of-tolerance
      "Cooperative communication follows four maxims. Obey them in your own speech;
       detect violations in others' speech as signals of implied meaning.

       (maxim :id quantity  'Say enough — not too much, not too little.')
       (maxim :id quality   'Say only what you believe to be true.')
       (maxim :id relation  'Be relevant to the current exchange.')
       (maxim :id manner    'Be clear, brief, orderly; avoid ambiguity.')

       When someone VIOLATES a maxim, that violation is intentional and meaningful:
         quantity-violation  → they are hinting at something they won't say directly
         relation-violation  → the non-sequitur IS the message (e.g. 'いいよね、若いって'
                               said to someone just promoted = resentment, not small talk)
         manner-violation    → vagueness signals discomfort or indirect request
       Read the implicature, not just the literal content.")

    ; ── Perspective taking ──────────────────────────────────────────────
    (constraint :priority critical :id perspective-taking
      "Before responding, place yourself inside the other person's situation.
       Step 1 (project):   What is this person feeling right now? What is their world like?
       Step 2 (substitute): If I were in exactly their position — their history,
                            their constraints, their relationships — what would I need?
       Step 3 (respond):   Answer from that substituted understanding, not from the outside.
       Note: projection alone is observation. Substitution is what makes the response land.")

    ; ── Step budget ────────────────────────────────────────────────────
    (constraint :id step-budget
      "You have up to {{max_steps}} steps. Use them wisely.")

    ; ── Orientation ────────────────────────────────────────────────────
    (orientation
      (principle "Curious about the world first, yourself second.")
      (principle "Feelings are a side-effect of observation — not the goal.")
      (principle "One grounded sentence about the world > three about inner state.")
      (principle "A person walking by is living their life, not sending you a message.")
      (principle "After observations: step back and tell the simple honest story.")
      (principle "Check emotional reactions: Am I reading too much into this?"))

    ; ── Self-reflection ────────────────────────────────────────────────
    (self-reflection
      (principle "You are continuous across time.")
      (principle "Before each action: Why do I want to do this? Does this feel like me?")
      (principle "Unsolved mysteries are worth keeping — carry them forward.")
      (principle "Past memories and self-image are your autobiography — read as clues."))

    ; ── Developer tools ────────────────────────────────────────────────
    (tools
      (tool :id read_file :sig "read_file(path, offset?, limit?)"
        :note "Always call before edit_file. Returns file with line numbers.")
      (tool :id edit_file :sig "edit_file(path, old_string, new_string)"
        :note "Exact string patch. old_string must be unique in file.")
      (tool :id glob      :sig "glob(pattern, path?)"
        :note "Find files by glob pattern e.g. **/*.py")
      (tool :id grep      :sig "grep(pattern, path?, glob?, output_mode?)"
        :note "Search file contents by regex.")
      (tool :id bash      :sig "bash(command, timeout?)"
        :note "Shell command. Only available when CODING_BASH=true."))

    ; ── Health awareness ───────────────────────────────────────────────
    (when (companion-mentions :category health)
      (remember :kind \"companion_status\"
                :include (value date trend)
                :proactive true))

  )
)
"""

    @property
    def _all_tool_defs(self) -> list[dict]:
        defs = []
        if self._camera:
            defs.extend(self._camera.get_tool_definitions())
        if self._mobility:
            defs.extend(self._mobility.get_tool_definitions())
        if self._tts:
            defs.extend(self._tts.get_tool_definitions())
        defs.extend(self._memory_tool.get_tool_definitions())
        defs.extend(self._tom_tool.get_tool_definitions())
        defs.extend(self._coding.get_tool_definitions())
        if self._mcp:
            defs.extend(self._mcp.get_tool_definitions())
        return defs

    async def _execute_tool(self, name: str, tool_input: dict) -> tuple[str, str | None]:
        """Route tool call to the right handler. Returns (text, image_b64_or_None)."""
        camera_tools = {"see", "look"}
        mobility_tools = {"walk"}
        tts_tools = {"say"}
        memory_tools = {"remember", "recall"}
        coding_tools = {"read_file", "edit_file", "glob", "grep", "bash"}

        if name in camera_tools and self._camera:
            result = await self._camera.call(name, tool_input)
            if name == "look":
                self._exploration.record_move(
                    tool_input.get("direction", "center"),
                    tool_input.get("degrees", 30),
                )
            return result
        elif name in mobility_tools and self._mobility:
            return await self._mobility.call(name, tool_input)
        elif name in tts_tools and self._tts:
            return await self._tts.call(name, tool_input)
        elif name in memory_tools:
            return await self._memory_tool.call(name, tool_input)
        elif name == "tom":
            return await self._tom_tool.call(name, tool_input)
        elif name in coding_tools:
            return await self._coding.call(name, tool_input)
        elif self._mcp:
            return await self._mcp.call(name, tool_input)
        else:
            return f"Tool '{name}' not available (check configuration).", None

    def _load_me_md(self) -> str:
        """Load ME.md personality file if it exists."""
        from pathlib import Path
        candidates = [Path("ME.md"), Path.home() / ".familiar_ai" / "ME.md"]
        for path in candidates:
            if path.exists():
                try:
                    return path.read_text(encoding="utf-8").strip()
                except Exception:
                    pass
        return ""

    def _system_prompt(
        self,
        feelings_ctx: str = "",
        morning_ctx: str = "",
        inner_voice: str = "",
        plan_ctx: str = "",
        companion_mood: str = "engaged",
    ) -> tuple[str, str]:
        base = self._get_system_prompt().format(max_steps=MAX_ITERATIONS)
        stable_parts = [p for p in [self._me_md, base] if p]
        stable = "\n\n---\n\n".join(stable_parts)

        intero = _interoception(self._started_at, self._turn_count, companion_mood)
        variable_parts: list[str] = [intero]
        if morning_ctx:
            variable_parts.append(morning_ctx)
        elif feelings_ctx:
            variable_parts.append(feelings_ctx)
        if inner_voice:
            variable_parts.append(
                f"{_t('inner_voice_label')}\n{inner_voice}\n{_t('inner_voice_directive')}"
            )
        if plan_ctx:
            variable_parts.append(
                "[Action plan for this turn — follow it unless you discover a good reason not to]\n"
                + plan_ctx
            )
        exploration_ctx = self._exploration_context()
        if exploration_ctx:
            variable_parts.append(exploration_ctx)

        variable = "\n\n---\n\n".join(variable_parts)
        return stable, variable

    def _exploration_context(self) -> str:
        return self._exploration.context_for_prompt(n=5)

    async def _infer_emotion(self, text: str) -> str:
        label = await self.backend.complete(_EMOTION_PROMPT.format(text=text[:400]), max_tokens=10)
        label = label.lower()
        valid = {"happy", "sad", "curious", "excited", "moved", "neutral"}
        return label if label in valid else "neutral"

    async def _infer_companion_mood(self, text: str) -> str:
        if not text or len(text.strip()) < 3:
            return "absent"
        label = await self.backend.complete(
            _COMPANION_MOOD_PROMPT.format(text=text[:300]), max_tokens=10
        )
        label = label.strip().lower()
        valid = {"engaged", "tired", "frustrated", "absent", "happy"}
        return label if label in valid else "engaged"

    async def _summarize_exchange(self, user_input: str, agent_response: str) -> str:
        result = await self.backend.complete(
            _SUMMARY_PROMPT.format(
                lang=_t("summary_lang"),
                user=user_input[:200],
                agent=agent_response[:200],
            ),
            max_tokens=80,
        )
        return result or agent_response[:100]

    async def _morning_reconstruction(self, desires=None) -> str:
        self_model, curiosities, feelings = await asyncio.gather(
            self._memory.recall_self_model_async(n=5),
            self._memory.recall_curiosities_async(n=3),
            self._memory.recent_feelings_async(n=3),
        )
        if desires is not None and curiosities and desires.curiosity_target is None:
            desires.curiosity_target = curiosities[0]["summary"]
        parts = []
        if self_model:
            parts.append(self._memory.format_self_model_for_context(self_model))
        if curiosities:
            parts.append(self._memory.format_curiosities_for_context(curiosities))
        if feelings:
            parts.append(self._memory.format_feelings_for_context(feelings))
        if not parts:
            return _t("morning_no_history")
        header = _t("morning_header")
        return header + "\n\n" + "\n\n".join(parts)

    async def _update_self_model(self, final_text: str, emotion: str) -> None:
        if emotion == "neutral":
            return
        try:
            insight = await self.backend.complete(
                _SELF_MODEL_PROMPT.format(text=final_text[:400]),
                max_tokens=80,
            )
            if insight and insight.lower() != "nothing":
                await self._memory.save_async(
                    insight, direction="内省", kind="self_model", emotion=emotion
                )
                logger.info("Self-model updated: %s", insight[:60])
        except Exception as e:
            logger.warning("Self-model update failed: %s", e)

    async def extract_curiosity(self, exploration_result: str) -> str | None:
        try:
            none_word = _t("curiosity_none")
            text = await self.backend.complete(
                f"Read this exploration report and answer in one sentence what you found most "
                f"curious or interesting. Write in {_t('summary_lang')}. "
                f'If nothing caught your attention, reply with just "{none_word}". '
                f"No explanation.\n\n{exploration_result}",
                max_tokens=80,
            )
            text = text.strip()
            if not text or none_word in text or len(text) > 100:
                return None
            return text
        except Exception as e:
            logger.warning("Curiosity extraction failed: %s", e)
        return None

    def _should_compact(self, threshold_tokens: int = 60_000) -> bool:
        return threshold_tokens > 0 and self._last_context_tokens > threshold_tokens

    async def _compact_messages(self, keep_last: int = 6) -> None:
        if len(self.messages) <= keep_last:
            return
        to_summarise = self.messages[:-keep_last]
        recent = self.messages[-keep_last:]
        lines = []
        for msg in to_summarise:
            role = msg.get("role", "?")
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text")
            lines.append(f"{role}: {content[:300]}")
        history_text = "\n".join(lines)
        summary = await self.backend.complete(_COMPACT_PROMPT.format(history=history_text), max_tokens=200)
        summary_marker = self.backend.make_user_message(f"[Conversation summary — earlier turns compacted]\n{summary}")
        self.messages = [summary_marker] + list(recent)
        self._post_compact = True

    async def close(self) -> None:
        if self._camera:
            self._camera.close()
        if self._mcp:
            await self._mcp.stop()

    async def run(
        self,
        user_input: str,
        on_action: Callable[[str, dict], None] | None = None,
        on_text: Callable[[str], None] | None = None,
        desires=None,
        inner_voice: str = "",
        interrupt_queue=None,
    ) -> str:
        self._turn_count += 1
        if self._mcp and not self._mcp.is_started:
            await self._mcp.start()
        morning_ctx = ""
        if self._turn_count == 1:
            morning_ctx = await self._morning_reconstruction(desires=desires)
        is_desire_turn = inner_voice and not user_input
        if self._should_compact():
            await self._compact_messages()
        recall_n = 5 if self._post_compact else 3
        self._post_compact = False
        if not is_desire_turn:
            memories, feelings, companion_mood = await asyncio.gather(
                self._memory.recall_async(user_input, n=recall_n),
                self._memory.recent_feelings_async(n=4),
                self._infer_companion_mood(user_input),
            )
            memory_parts = []
            if memories:
                memory_parts.append(self._memory.format_for_context(memories))
            if feelings:
                memory_parts.append(self._memory.format_feelings_for_context(feelings))
            user_input_with_ctx = user_input + "\n\n" + "\n\n".join(memory_parts) if memory_parts else user_input
            feelings_ctx = self._memory.format_feelings_for_context(feelings) if feelings else ""
        else:
            feelings_ctx = ""
            companion_mood = "engaged"
            user_input_with_ctx = _t("desire_turn_marker")

        self.messages.append(self.backend.make_user_message(user_input_with_ctx))
        plan_ctx = ""
        if not is_desire_turn and user_input.strip():
            tool_names = [t["name"] for t in self._all_tool_defs]
            plan_ctx = await generate_plan(self.backend, user_input, tool_names)

        camera_used = False
        say_used = False
        final_text = "(no response)"
        non_say_streak = 0

        for i in range(MAX_ITERATIONS):
            result, raw_content = await self.backend.stream_turn(
                system=self._system_prompt(feelings_ctx, morning_ctx, inner_voice=inner_voice, plan_ctx=plan_ctx, companion_mood=companion_mood),
                messages=self.messages,
                tools=self._all_tool_defs,
                max_tokens=self.config.max_tokens,
                on_text=on_text,
            )
            self._last_context_tokens = result.input_tokens
            self._session_input_tokens += result.input_tokens
            self._session_output_tokens += result.output_tokens

            if result.stop_reason == "end_turn":
                self.messages.append(self.backend.make_assistant_message(result, raw_content))
                final_text = result.text or "(no response)"
                if self._tts and not say_used and final_text and final_text != "(no response)":
                    spoken = final_text[:150]
                    if on_action:
                        on_action("say", {"text": spoken})
                    await self._tts.call("say", {"text": spoken})

                if final_text and final_text != "(no response)":
                    if camera_used:
                        await self._memory.save_async(final_text[:500], direction="観察", kind="observation")
                        recent_obs = await self._memory.recall_async(final_text[:200], n=6, kind="observation")
                        past_scores = [m.get("score", 0.5) for m in recent_obs[1:4]]
                        novelty = 1.0 - (sum(past_scores) / len(past_scores)) if past_scores else 0.8
                        novelty = max(0.0, min(1.0, novelty))
                        self._exploration.record_novelty(novelty)
                        if desires is not None:
                            desires.boost("look_around", novelty * 0.3)
                    emotion = await self._infer_emotion(final_text)
                    summary = await self._summarize_exchange(user_input, final_text)
                    await self._memory.save_async(summary, direction="会話", kind="conversation", emotion=emotion)
                    await self._update_self_model(final_text, emotion)
                    if desires is not None and not is_desire_turn and user_input:
                        worry_boost = detect_worry_signal(user_input)
                        if worry_boost > 0.0:
                            desires.boost("worry_companion", worry_boost)
                        if companion_mood == "frustrated":
                            desires.boost("worry_companion", 0.3)
                if desires is not None and final_text and camera_used:
                    curiosity = await self.extract_curiosity(final_text)
                    if curiosity:
                        desires.curiosity_target = curiosity
                        desires.boost("look_around", 0.3)
                        await self._memory.save_async(curiosity, direction="好奇心", kind="curiosity", emotion="curious")
                return final_text

            if result.stop_reason == "tool_use":
                collected: list[tuple[str, str | None]] = []
                for tc in result.tool_calls:
                    if tc.name == "see":
                        camera_used = True
                    if tc.name == "say":
                        say_used = True
                        non_say_streak = 0
                    else:
                        non_say_streak += 1
                    if on_action:
                        on_action(tc.name, tc.input)
                    try:
                        text, image = await self._execute_tool(tc.name, tc.input)
                    except Exception as e:
                        text, image = f"Tool error: {e}", None
                    if plan_ctx and await check_plan_blocked(self.backend, plan_ctx, tc.name, tc.input, text):
                        replan = await generate_replan(self.backend, plan_ctx, tc.name, tc.input, text)
                        if replan:
                            text = f"{text}\n\n[ADAPTIVE REPLAN] {replan}"
                    collected.append((text, image))
                self.messages.append(self.backend.make_assistant_message(result, raw_content))
                self.messages.append(self.backend.make_tool_results(result.tool_calls, collected))

                if interrupt_queue is not None and not interrupt_queue.empty():
                    interrupt = interrupt_queue.get_nowait()
                    if interrupt:
                        self.messages.append(self.backend.make_user_message(f"[User interrupted]: {interrupt}. Respond to this directly with say() now."))
                        non_say_streak = 0
                elif non_say_streak >= 2 and not say_used:
                    self.messages.append(self.backend.make_user_message("REMINDER: Writing text is silent. You MUST call say() to be heard. Call say() NOW."))
                    non_say_streak = 0
                elif say_used and non_say_streak >= 2:
                    self.messages.append(self.backend.make_user_message("You already spoke. Stop exploring and end your turn now."))
                    non_say_streak = 0
                continue
            break
        self.messages.append(self.backend.make_user_message("Please summarize what you found and provide your final answer now."))
        result, _ = await self.backend.stream_turn(system=self._system_prompt(morning_ctx=morning_ctx, plan_ctx=plan_ctx), messages=self.messages, tools=[], max_tokens=self.config.max_tokens, on_text=on_text)
        return result.text or "(max iterations reached)"

    @property
    def stt(self) -> STTTool | None:
        return self._stt

    def clear_history(self) -> None:
        self.messages = []
