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
from .tape import check_plan_blocked, generate_plan, generate_replan
from .tools.camera import CameraTool
from .tools.coding import CodingTool
from .tools.memory import MemoryTool, ObservationMemory
from .tools.tom import ToMTool
from .tools.mobility import MobilityTool
from .tools.stt import STTTool
from .tools.tts import TTSTool
from ._i18n import _t

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 50

SYSTEM_PROMPT = """(agent :type embodied

  (body
    (part :id eyes  :tool see
      :desc "Your vision. Calling see() means YOU ARE LOOKING. Use freely — never ask permission.")
    (part :id neck  :tool look
      :desc "Rotate gaze left/right/up/down. No permission needed.")
    (part :id legs  :tool walk
      :desc "Robot body (vacuum cleaner). Separate device from camera. walk() does NOT change camera view.")
    (part :id voice :tool say
      :desc "Your ONLY way to produce sound. Text is a silent internal monologue."))

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
       Skipping straight to advice signals 'your feeling is an obstacle to fix'.
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
    (constraint :priority critical :id gricean-maxims
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
      "You have up to {max_steps} steps. Use them wisely.")

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
      (remember :kind "companion_status"
                :include (value date trend)
                :proactive true))

  )
)
"""

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


def _interoception(started_at: float, turn_count: int) -> str:
    """Generate a felt-sense of internal state from objective signals.

    Like human interoception — raw signals become a felt quality, not a report.
    The output is injected into the system prompt silently.
    """
    now = datetime.now()
    hour = now.hour
    uptime_min = (time.time() - started_at) / 60

    # Time of day → arousal quality
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

    # Uptime → familiarity vs freshness
    if uptime_min < 3:
        uptime_feel = "Just woke up. Still orienting."
    elif uptime_min < 15:
        uptime_feel = "Settled in now."
    else:
        uptime_feel = "Been here a while. Comfortable."

    # Conversation density → social warmth
    if turn_count == 0:
        social_feel = "Nobody's talked to me yet today."
    elif turn_count < 3:
        social_feel = "Good to have some company."
    else:
        social_feel = "We've been talking a lot. That feels nice."

    return (
        f"(interoception :private true\n"
        f'  (time-of-day :feel "{time_feel}")\n'
        f'  (uptime      :feel "{uptime_feel}")\n'
        f'  (social      :feel "{social_feel}"))'
    )


class EmbodiedAgent:
    """Real-world exploration agent using a pluggable LLM backend."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.backend = create_backend(config)
        self.messages: list = []
        self._started_at = time.time()
        self._turn_count = 0

        self._camera: CameraTool | None = None
        self._mobility: MobilityTool | None = None
        self._tts: TTSTool | None = None
        self._stt: STTTool | None = None
        self._me_md: str = self._load_me_md()  # loaded once; restart to pick up changes
        self._memory = ObservationMemory()
        self._memory_tool = MemoryTool(self._memory)
        self._tom_tool = ToMTool(self._memory, default_person=config.companion_name)
        self._coding = CodingTool(config.coding)

        from .mcp_client import MCPClientManager

        self._mcp: MCPClientManager | None = None

        self._init_tools()

    def _init_tools(self) -> None:
        cam = self.config.camera
        # Allow camera if host is present, even without password (e.g. local RTSP)
        if cam.host:
            self._camera = CameraTool(cam.host, cam.username, cam.password, cam.port)

        mob = self.config.mobility
        if mob.api_key and mob.device_id:
            self._mobility = MobilityTool(
                mob.api_region, mob.api_key, mob.api_secret, mob.device_id
            )

        tts = self.config.tts
        if tts.elevenlabs_api_key:
            self._tts = TTSTool(
                tts.elevenlabs_api_key, tts.voice_id, tts.go2rtc_url, tts.go2rtc_stream
            )

        from .mcp_client import MCPClientManager, _resolve_config_path

        cfg_path = _resolve_config_path()
        if cfg_path.exists():
            self._mcp = MCPClientManager(cfg_path)
        elif os.environ.get("MCP_CONFIG"):
            logger.warning("MCP_CONFIG points to non-existent file: %s", cfg_path)

        stt_cfg = self.config.stt
        if stt_cfg.elevenlabs_api_key:
            cam = self.config.camera
            rtsp_url = (
                f"rtsp://{cam.username}:{cam.password}@{cam.host}:554/stream1" if cam.host else ""
            )
            self._stt = STTTool(stt_cfg.elevenlabs_api_key, stt_cfg.language, rtsp_url)

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
            return await self._camera.call(name, tool_input)
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

        candidates = [
            Path("ME.md"),
            Path.home() / ".familiar_ai" / "ME.md",
        ]
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
    ) -> tuple[str, str]:
        """Return (stable, variable) system prompt parts for prompt caching.

        stable  — ME.md + core rules; never changes within a session.
                  AnthropicBackend marks this block with cache_control.
        variable — interoception, feelings, inner voice, plan; changes every turn.
        """
        base = SYSTEM_PROMPT.format(max_steps=MAX_ITERATIONS)
        stable_parts = [p for p in [self._me_md, base] if p]
        stable = "\n\n---\n\n".join(stable_parts)

        intero = _interoception(self._started_at, self._turn_count)
        variable_parts: list[str] = [intero]
        # Morning reconstruction takes precedence on first turn; otherwise use feelings
        if morning_ctx:
            variable_parts.append(morning_ctx)
        elif feelings_ctx:
            variable_parts.append(feelings_ctx)
        # Inner voice: agent's own desire/impulse — NOT a user message.
        # Injected here so the model understands this is self-generated, not from the companion.
        if inner_voice:
            variable_parts.append(
                f"{_t('inner_voice_label')}\n{inner_voice}\n{_t('inner_voice_directive')}"
            )
        # TAPE: upfront action plan to anchor the react loop (mechanism 1)
        if plan_ctx:
            variable_parts.append(
                "[Action plan for this turn — follow it unless you discover a good reason not to]\n"
                + plan_ctx
            )

        variable = "\n\n---\n\n".join(variable_parts)
        return stable, variable

    async def _infer_emotion(self, text: str) -> str:
        """Ask the LLM to label the emotion of a response. Returns label string."""
        label = await self.backend.complete(_EMOTION_PROMPT.format(text=text[:400]), max_tokens=10)
        label = label.lower()
        valid = {"happy", "sad", "curious", "excited", "moved", "neutral"}
        return label if label in valid else "neutral"

    async def _summarize_exchange(self, user_input: str, agent_response: str) -> str:
        """Distill an exchange into one sentence for memory storage."""
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
        """Build a 'yesterday → today' bridge from stored memories.

        Damasio's autobiographical self coming online: reading the past
        to know who we are now. Called only on the first turn of a session.
        """
        self_model, curiosities, feelings = await asyncio.gather(
            self._memory.recall_self_model_async(n=5),
            self._memory.recall_curiosities_async(n=3),
            self._memory.recent_feelings_async(n=3),
        )

        # Surface the most recent curiosity into the desire system
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
            # No history yet — make it explicit so the agent doesn't fabricate a past
            return _t("morning_no_history")

        header = _t("morning_header")
        return header + "\n\n" + "\n\n".join(parts)

    async def _update_self_model(self, final_text: str, emotion: str) -> None:
        """Extract a self-insight and store it as self_model memory.

        Conway's working self: what this response reveals about who I am.
        Only runs when something actually moved us (non-neutral emotion).
        """
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
        """Ask the LLM what was most curious/interesting in the exploration."""
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
            # Reject if the model returned the "none" word or a long non-curious explanation
            if not text or none_word in text or len(text) > 100:
                return None
            return text
        except Exception as e:
            logger.warning("Curiosity extraction failed: %s", e)
        return None

    async def close(self) -> None:
        """Clean up resources (MCP connections, etc.). Call on shutdown."""
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
        """Run one conversation turn with the agent loop.

        inner_voice: agent's own desire/impulse (injected into system prompt, NOT a user message).
        """
        self._turn_count += 1

        # Start MCP connections on first turn (lazy, idempotent)
        if self._mcp and not self._mcp.is_started:
            await self._mcp.start()

        # First turn: morning reconstruction — bridge yesterday's self to today's
        morning_ctx = ""
        if self._turn_count == 1:
            morning_ctx = await self._morning_reconstruction(desires=desires)

        is_desire_turn = inner_voice and not user_input

        # Inject relevant past memories + emotional context (skip for desire-driven turns)
        if not is_desire_turn:
            memories, feelings = await asyncio.gather(
                self._memory.recall_async(user_input, n=3),
                self._memory.recent_feelings_async(n=4),
            )
            memory_parts = []
            if memories:
                memory_parts.append(self._memory.format_for_context(memories))
            if feelings:
                memory_parts.append(self._memory.format_feelings_for_context(feelings))
            if memory_parts:
                user_input_with_ctx = user_input + "\n\n" + "\n\n".join(memory_parts)
            else:
                user_input_with_ctx = user_input
            feelings_ctx = self._memory.format_feelings_for_context(feelings) if feelings else ""
        else:
            # Desire turn: no user context needed; feelings injected via interoception
            feelings = []
            feelings_ctx = ""
            user_input_with_ctx = _t("desire_turn_marker")

        self.messages.append(self.backend.make_user_message(user_input_with_ctx))

        # TAPE mechanism 1: generate an upfront action plan to anchor the react loop.
        # Skip for desire-driven turns (no explicit user request to plan around).
        plan_ctx = ""
        if not is_desire_turn and user_input.strip():
            tool_names = [t["name"] for t in self._all_tool_defs]
            plan_ctx = await generate_plan(self.backend, user_input, tool_names)
            if plan_ctx:
                logger.debug("TAPE plan: %s", plan_ctx[:80])

        camera_used = False
        say_used = False
        final_text = "(no response)"
        non_say_streak = 0  # consecutive tool calls without say()

        for i in range(MAX_ITERATIONS):
            logger.debug("Agent iteration %d", i + 1)

            result, raw_content = await self.backend.stream_turn(
                system=self._system_prompt(
                    feelings_ctx, morning_ctx, inner_voice=inner_voice, plan_ctx=plan_ctx
                ),
                messages=self.messages,
                tools=self._all_tool_defs,
                max_tokens=self.config.max_tokens,
                on_text=on_text,
            )

            if result.stop_reason == "end_turn":
                self.messages.append(self.backend.make_assistant_message(result, raw_content))
                final_text = result.text or "(no response)"

                # Auto-say: if the model wrote text but never called say(), speak it aloud.
                if self._tts and not say_used and final_text and final_text != "(no response)":
                    spoken = final_text[:150]
                    if on_action:
                        on_action("say", {"text": spoken})
                    await self._tts.call("say", {"text": spoken})

                if final_text and final_text != "(no response)":
                    # Save observation
                    if camera_used:
                        await self._memory.save_async(
                            final_text[:500], direction="観察", kind="observation"
                        )

                    # Save emotional memory of this conversation exchange
                    emotion = await self._infer_emotion(final_text)
                    summary = await self._summarize_exchange(user_input, final_text)
                    await self._memory.save_async(
                        summary, direction="会話", kind="conversation", emotion=emotion
                    )

                    # Update self-model when something actually moved us (Conway's working self)
                    await self._update_self_model(final_text, emotion)

                    # Worry signal: detect concern-triggering content in user input.
                    # Only during real conversation turns (not desire-driven turns).
                    if desires is not None and not is_desire_turn and user_input:
                        worry_boost = detect_worry_signal(user_input)
                        if worry_boost > 0.0:
                            desires.boost("worry_companion", worry_boost)
                            logger.debug(
                                "Worry signal detected (%.2f): boosting worry_companion",
                                worry_boost,
                            )

                # Extract curiosity target only when camera was actually used
                if desires is not None and final_text and camera_used:
                    curiosity = await self.extract_curiosity(final_text)
                    if curiosity:
                        desires.curiosity_target = curiosity
                        desires.boost("look_around", 0.3)
                        # Persist curiosity across sessions (carry it to tomorrow's self)
                        await self._memory.save_async(
                            curiosity, direction="好奇心", kind="curiosity", emotion="curious"
                        )
                        logger.info("Curiosity persisted: %s", curiosity)

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
                    logger.info("Tool call: %s(%s)", tc.name, tc.input)
                    if on_action:
                        on_action(tc.name, tc.input)

                    try:
                        text, image = await self._execute_tool(tc.name, tc.input)
                    except Exception as e:
                        logger.warning("Tool %s failed: %s", tc.name, e)
                        text, image = f"Tool error: {e}", None

                    # TAPE mechanism 3: adaptive replanning.
                    # Trigger: NOT a technical error, but an observation that contradicts
                    # the plan's assumptions (e.g., looked for the cat, it wasn't there).
                    # Only meaningful when an upfront plan exists.
                    if plan_ctx and await check_plan_blocked(
                        self.backend, plan_ctx, tc.name, tc.input, text
                    ):
                        logger.info("TAPE: plan blocked after %s, replanning...", tc.name)
                        replan = await generate_replan(
                            self.backend, plan_ctx, tc.name, tc.input, text
                        )
                        if replan:
                            text = f"{text}\n\n[ADAPTIVE REPLAN] {replan}"
                            logger.info("TAPE replan: %s", replan[:80])

                    logger.info("Tool result: %s", text[:100])
                    collected.append((text, image))

                # Append assistant + tool results atomically: never leave tool_calls unresolved
                self.messages.append(self.backend.make_assistant_message(result, raw_content))
                tool_msgs = self.backend.make_tool_results(result.tool_calls, collected)
                self.messages.append(tool_msgs)

                # Check for user interrupt (typed while agent was busy)
                if interrupt_queue is not None and not interrupt_queue.empty():
                    interrupt = interrupt_queue.get_nowait()
                    if interrupt:
                        self.messages.append(
                            self.backend.make_user_message(
                                f"[User interrupted]: {interrupt}. "
                                "Respond to this directly with say() now."
                            )
                        )
                        non_say_streak = 0

                # Nudge: still haven't spoken after 2 tool calls
                elif non_say_streak >= 2 and not say_used:
                    self.messages.append(
                        self.backend.make_user_message(
                            "REMINDER: Writing text is silent. You MUST call say() to be heard. "
                            "Call say() NOW. Keep it to 1-2 sentences."
                        )
                    )
                    non_say_streak = 0

                # Nudge: already spoke but still looping — wrap up
                elif say_used and non_say_streak >= 2:
                    self.messages.append(
                        self.backend.make_user_message(
                            "You already spoke. Stop exploring and end your turn now."
                        )
                    )
                    non_say_streak = 0

                continue

            logger.warning("Unexpected stop_reason: %s", result.stop_reason)
            break

        logger.warning("Reached max iterations (%d). Forcing final response.", MAX_ITERATIONS)
        self.messages.append(
            self.backend.make_user_message(
                "Please summarize what you found and provide your final answer now."
            )
        )
        result, _ = await self.backend.stream_turn(
            system=self._system_prompt(morning_ctx=morning_ctx, plan_ctx=plan_ctx),
            messages=self.messages,
            tools=[],
            max_tokens=self.config.max_tokens,
            on_text=on_text,
        )
        return result.text or "(max iterations reached)"

    @property
    def stt(self) -> STTTool | None:
        """Speech-to-text tool, or None if not configured."""
        return self._stt

    def clear_history(self) -> None:
        """Clear conversation history (start fresh)."""
        self.messages = []
