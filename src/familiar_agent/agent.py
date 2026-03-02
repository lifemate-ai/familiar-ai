"""Core agent loop - ReAct pattern with real-world tools."""

from __future__ import annotations
import asyncio
import logging
import os
import time
from collections.abc import Callable
from datetime import datetime

from .backend import create_backend, create_utility_backend
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
from ._i18n import _t

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 50

SYSTEM_PROMPT = """
(agent :type embodied
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

# Companion mood prompt — classify companion's emotional state from their message
_COMPANION_MOOD_PROMPT = """\
Read this message and pick the single best label for the sender's mood:
engaged / tired / frustrated / absent / happy

Message: {text}

Reply with the label only (one English word)."""


# Day summary prompt — condense a day's observations into a diary-like entry
_DAY_SUMMARY_PROMPT = """\
You are writing a diary entry about this day from your own first-person memory.
Recall the flow of the day: what happened in the morning, then afternoon, then evening.
Capture how your feelings changed as events unfolded — what made you happy, 
what frustrated you, what surprised you, what lingered in your mind.

Rules:
- Write in first person, as someone remembering their own lived day
- Follow the chronological arc: morning → afternoon → evening
- Include specific details: what you saw, who you talked to, what was said
- Show emotional shifts: how one event changed how you felt about the next
- Do NOT list events — weave them into a flowing narrative
- Do NOT include titles, headers, or markdown formatting
- Start directly with the first sentence of the entry
- 5-8 sentences. Write in {lang}.

{observations}

Write just the diary entry."""

# Compaction summary prompt — condense old messages into a short recap
_COMPACT_PROMPT = """\
Summarize the following conversation into a short paragraph (3-6 sentences).
Capture: what was discussed, any decisions or discoveries, and the emotional tone.
Write in third person. Be concise.

{history}

Write just the summary paragraph."""


def _interoception(started_at: float, turn_count: int, companion_mood: str = "engaged") -> str:
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

    mood_feel_map = {
        "engaged": "They're here with me.",
        "tired": "They seem tired tonight.",
        "frustrated": "Something's bothering them.",
        "absent": "It's quiet. Not sure if they're really here.",
        "happy": "They're in a good mood today.",
    }
    companion_feel = mood_feel_map.get(companion_mood, "They're here with me.")

    return (
        f"(interoception :private true\n"
        f'  (time-of-day :feel "{time_feel}")\n'
        f'  (uptime      :feel "{uptime_feel}")\n'
        f'  (social      :feel "{social_feel}")\n'
        f'  (companion   :feel "{companion_feel}"))'
    )


class EmbodiedAgent:
    """Real-world exploration agent using a pluggable LLM backend."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.backend = create_backend(config)
        self._utility_backend = create_utility_backend(config) or self.backend
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
        self._me_md: str = self._load_me_md()  # loaded once; restart to pick up changes
        self._memory = ObservationMemory()
        self._memory_tool = MemoryTool(self._memory)
        self._tom_tool = ToMTool(self._memory, default_person=config.companion_name)
        self._coding = CodingTool(config.coding)
        self._exploration = ExplorationTracker()

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
                tts.elevenlabs_api_key,
                tts.voice_id,
                tts.go2rtc_url,
                tts.go2rtc_stream,
                output=tts.output,
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
        companion_mood: str = "engaged",
    ) -> tuple[str, str]:
        """Return (stable, variable) system prompt parts for prompt caching.

        stable  — ME.md + core rules; never changes within a session.
                  AnthropicBackend marks this block with cache_control.
        variable — interoception, feelings, inner voice, plan; changes every turn.
        """
        base = SYSTEM_PROMPT.format(max_steps=MAX_ITERATIONS)
        stable_parts = [p for p in [self._me_md, base] if p]
        stable = "\n\n---\n\n".join(stable_parts)

        intero = _interoception(self._started_at, self._turn_count, companion_mood)
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

        exploration_ctx = self._exploration_context()
        if exploration_ctx:
            variable_parts.append(exploration_ctx)

        variable = "\n\n---\n\n".join(variable_parts)
        return stable, variable

    def _exploration_context(self) -> str:
        """Return exploration history for ICL-based direction steering."""
        return self._exploration.context_for_prompt(n=5)

    async def _infer_emotion(self, text: str) -> str:
        """Ask the LLM to label the emotion of a response. Returns label string."""
        label = await self._utility_backend.complete(
            _EMOTION_PROMPT.format(text=text[:400]), max_tokens=10
        )
        label = label.lower()
        valid = {"happy", "sad", "curious", "excited", "moved", "neutral"}
        return label if label in valid else "neutral"

    async def _infer_companion_mood(self, text: str) -> str:
        """Classify companion's emotional state from their message. Returns mood label."""
        if not text or len(text.strip()) < 3:
            return "absent"
        label = await self._utility_backend.complete(
            _COMPANION_MOOD_PROMPT.format(text=text[:300]), max_tokens=10
        )
        label = label.strip().lower()
        valid = {"engaged", "tired", "frustrated", "absent", "happy"}
        return label if label in valid else "engaged"

    async def _summarize_exchange(self, user_input: str, agent_response: str) -> str:
        """Distill an exchange into one sentence for memory storage."""
        result = await self._utility_backend.complete(
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
        logger.info("Morning reconstruction started")
        self_model, curiosities, feelings, day_summaries = await asyncio.gather(
            self._memory.recall_self_model_async(n=5),
            self._memory.recall_curiosities_async(n=3),
            self._memory.recent_feelings_async(n=3),
            self._memory.recall_day_summaries_async(n=5),
        )
        logger.info(
            "Morning data: self_model=%d, curiosities=%d, feelings=%d, day_summaries=%d",
            len(self_model),
            len(curiosities),
            len(feelings),
            len(day_summaries),
        )

        # Generate day summaries for past dates that don't have one yet.
        # Run in background so it never delays the first-turn greeting response.
        asyncio.ensure_future(self._backfill_day_summaries())

        # Re-fetch if backfill created new summaries
        if not day_summaries:
            day_summaries = await self._memory.recall_day_summaries_async(n=5)

        # Surface the most recent curiosity into the desire system
        if desires is not None and curiosities and desires.curiosity_target is None:
            desires.curiosity_target = curiosities[0]["summary"]

        parts = []
        if day_summaries:
            parts.append(self._memory.format_day_summaries_for_context(day_summaries))
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

    async def _backfill_day_summaries(self) -> None:
        """Generate day summaries for past dates that don't have one yet.

        Skips today (summary is generated at shutdown). Only processes
        the most recent 5 days to keep startup time reasonable.

        Skipped when no separate utility backend is configured: the main
        conversation backend may not handle bulk observations well (e.g.
        Kimi K2.5 input-size limits), and we don't want to stall startup.
        """
        if self._utility_backend is self.backend:
            logger.debug("Backfill skipped: no separate utility backend configured")
            return
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            all_dates = await asyncio.to_thread(self._memory.get_dates_with_observations, 7)
            existing = await asyncio.to_thread(self._memory.get_dates_with_summaries)
            logger.info(
                "Backfill check: today=%s, all_dates=%s, existing=%s",
                today,
                all_dates,
                existing,
            )

            missing = [d for d in all_dates if d != today and d not in existing][:5]
            if missing:
                logger.info("Backfill: generating day summaries for %s", missing)
            else:
                logger.info("Backfill: no missing day summaries")
            for date in missing:
                await self._generate_day_summary(date)
        except Exception as e:
            logger.warning("Day summary backfill failed: %s", e)

    async def _generate_day_summary(self, date: str) -> None:
        """Generate and save a day summary for the given date."""
        try:
            observations = await asyncio.to_thread(self._memory.get_observations_for_date, date, 50)
            if not observations:
                logger.info("No observations for %s, skipping day summary", date)
                return

            # Build a concise transcript for the LLM — keep it short
            lines = []
            for obs in observations:
                emotion = f" [{obs['emotion']}]" if obs["emotion"] != "neutral" else ""
                lines.append(f"  {obs['time']} ({obs['kind']}){emotion}: {obs['content'][:150]}")
            transcript = "\n".join(lines)
            logger.info("Generating day summary for %s (%d observations)", date, len(observations))

            summary = await asyncio.wait_for(
                self._utility_backend.complete(
                    _DAY_SUMMARY_PROMPT.format(
                        lang=_t("summary_lang"),
                        observations=transcript,
                    ),
                    max_tokens=400,
                ),
                timeout=30.0,
            )
            if summary:
                await self._memory.save_async(
                    summary,
                    direction="記憶",
                    kind="day_summary",
                    emotion="neutral",
                    override_date=date,
                )
                logger.info("Day summary generated for %s: %s", date, summary[:80])
            else:
                logger.warning("Day summary for %s: LLM returned empty response", date)
        except asyncio.TimeoutError:
            logger.warning("Day summary for %s timed out (30s)", date)
        except Exception as e:
            logger.warning("Failed to generate day summary for %s: %s", date, e)

    async def _update_self_model(self, final_text: str, emotion: str) -> None:
        """Extract a self-insight and store it as self_model memory.

        Conway's working self: what this response reveals about who I am.
        Only runs when something actually moved us (non-neutral emotion).
        """
        if emotion == "neutral":
            return
        try:
            insight = await self._utility_backend.complete(
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
            text = await self._utility_backend.complete(
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

    def _should_compact(self, threshold_tokens: int = 60_000) -> bool:
        """Return True when context is large enough to warrant compaction.

        A threshold of 0 acts as a disabled sentinel — never compact.
        In normal use _last_context_tokens is 0 until after the first turn,
        so an empty conversation naturally returns False.
        """
        return threshold_tokens > 0 and self._last_context_tokens > threshold_tokens

    async def _compact_messages(self, keep_last: int = 6) -> None:
        """Summarise old messages and trim the history.

        Keeps the last `keep_last` messages verbatim, replaces the rest with a
        single summary marker, and sets `_post_compact = True` so the next
        `run()` call does a boosted memory recall to compensate.
        """
        if len(self.messages) <= keep_last:
            return

        to_summarise = self.messages[:-keep_last]
        recent = self.messages[-keep_last:]

        # Build a plain-text transcript for the summary LLM call
        lines = []
        for msg in to_summarise:
            role = msg.get("role", "?")
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    p.get("text", "")
                    for p in content
                    if isinstance(p, dict) and p.get("type") == "text"
                )
            lines.append(f"{role}: {content[:300]}")
        history_text = "\n".join(lines)

        summary = await self._utility_backend.complete(
            _COMPACT_PROMPT.format(history=history_text),
            max_tokens=200,
        )
        summary_marker = self.backend.make_user_message(
            f"[Conversation summary — earlier turns compacted]\n{summary}"
        )

        self.messages = [summary_marker] + list(recent)
        self._post_compact = True

    @property
    def is_embedding_ready(self) -> bool:
        """Return True once the embedding model has finished loading."""
        return self._memory.is_embedding_ready()

    async def close(self) -> None:
        """Clean up resources. Bounded by timeouts to avoid hanging on exit."""
        # Generate (or refresh) today's day summary before shutting down.
        # Skipped when no separate utility backend is configured.
        if self._utility_backend is not self.backend:
            try:
                today = datetime.now().strftime("%Y-%m-%d")
                await asyncio.to_thread(self._memory.delete_day_summaries_for_date, today)
                await self._generate_day_summary(today)
            except Exception as e:
                logger.warning("Failed to generate today's day summary on shutdown: %s", e)
        if self._mcp:
            try:
                await asyncio.wait_for(self._mcp.stop(), timeout=2.0)
            except (asyncio.TimeoutError, Exception):
                pass
        try:
            await asyncio.wait_for(asyncio.to_thread(self._memory.close), timeout=1.0)
        except (asyncio.TimeoutError, Exception):
            pass

    async def run(
        self,
        user_input: str,
        on_action: Callable[[str, dict], None] | None = None,
        on_text: Callable[[str], None] | None = None,
        on_image: Callable[[str], None] | None = None,
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

        # Compact context if it has grown too large (GC-like: compress old turns)
        if self._should_compact():
            await self._compact_messages()

        # Inject relevant past memories + emotional context (skip for desire-driven turns)
        recall_n = 5 if self._post_compact else 3
        self._post_compact = False  # consume the flag regardless
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
            if memory_parts:
                user_input_with_ctx = user_input + "\n\n" + "\n\n".join(memory_parts)
            else:
                user_input_with_ctx = user_input
            feelings_ctx = self._memory.format_feelings_for_context(feelings) if feelings else ""
        else:
            # Desire turn: no user context needed; feelings injected via interoception
            feelings = []
            feelings_ctx = ""
            companion_mood = "engaged"
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
                    feelings_ctx,
                    morning_ctx,
                    inner_voice=inner_voice,
                    plan_ctx=plan_ctx,
                    companion_mood=companion_mood,
                ),
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

                # Auto-say: if the model wrote text but never called say(), speak it aloud.
                if self._tts and not say_used and final_text and final_text != "(no response)":
                    spoken = final_text[:150]
                    if on_action:
                        on_action("say", {"text": spoken})
                    await self._tts.call("say", {"text": spoken})

                if final_text and final_text != "(no response)":
                    # Save observation and compute novelty for ICL exploration
                    if camera_used:
                        await self._memory.save_async(
                            final_text[:500], direction="観察", kind="observation"
                        )
                        # Novelty = how different this observation is from recent ones.
                        # recall_async returns records sorted by cosine similarity (highest first).
                        # The most similar past observation's score ≈ redundancy; invert it.
                        recent_obs = await self._memory.recall_async(
                            final_text[:200], n=6, kind="observation"
                        )
                        # Skip the just-saved record (index 0 is itself); use next ones
                        past_scores = [m.get("score", 0.5) for m in recent_obs[1:4]]
                        if past_scores:
                            avg_similarity = sum(past_scores) / len(past_scores)
                            novelty = 1.0 - avg_similarity  # low similarity → high novelty
                        else:
                            novelty = 0.8  # first observation is always novel
                        novelty = max(0.0, min(1.0, novelty))
                        self._exploration.record_novelty(novelty)
                        if desires is not None:
                            desires.boost("look_around", novelty * 0.3)

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
                        # Companion mood: frustrated → boost worry_companion (LLM-based check)
                        if companion_mood == "frustrated":
                            desires.boost("worry_companion", 0.3)
                            logger.debug("Companion mood frustrated: boosting worry_companion")

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
                    if image and on_image is not None:
                        on_image(image)
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
