"""Core agent loop - ReAct pattern with real-world tools."""

from __future__ import annotations
import asyncio
import hashlib
import logging
import math
import os
import re
import time
from collections.abc import Callable, Mapping
from datetime import datetime

from .backend import create_backend, create_scene_backend, create_utility_backend
from .config import AgentConfig
from .desires import DesireSystem, detect_worry_signal
from .relationship import RelationshipTracker
from .self_state import SelfState
from .self_narrative import SelfNarrative
from .exploration import ExplorationTracker
from .scene import SceneTracker
from .attention_schema import AttentionSchema
from .default_mode import DefaultModeProcessor
from .meta_monitor import MetaMonitor
from .prediction import PredictionEngine
from .workspace import GlobalWorkspace
from .memory_worker import MemoryJobWorker
from .tape import check_plan_blocked, generate_plan, generate_replan
from .tools.camera import CameraTool
from .tools.coding import CodingTool
from .tools.memory import MemoryTool, ObservationMemory
from .tools.tom import ToMTool
from .tools.mobility import MobilityTool
from .tools.stt import STTTool
from .tools.tts import TTSTool
from ._i18n import _t
from .mcp_client import MCPClientManager, _resolve_config_path

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 50
_MORNING_CONTEXT_MAX_CHARS = 2600
_DEFAULT_TOOL_TIMEOUT = 20.0
_TOOL_TIMEOUTS: dict[str, float] = {
    "see": 12.0,
    "look": 8.0,
    "walk": 12.0,
    "say": 25.0,
    "remember": 20.0,
    "recall": 20.0,
    "tom": 20.0,
    "read_file": 30.0,
    "edit_file": 30.0,
    "glob": 20.0,
    "grep": 20.0,
    "bash": 45.0,
}

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
    (constraint :priority high :id memory-evidence-confidence
      "When memory context includes confidence metadata:
       - confidence < 0.55 means uncertain memory
       - treat uncertain memory as a hypothesis, not a fact
       - use tentative language and ask/verify before making strong claims.")

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
happy / sad / curious / excited / moved / surprised / nostalgic / relieved / tender / playful / proud / neutral

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


def _interoception(
    started_at: float,
    turn_count: int,
    companion_mood: str = "engaged",
    agent_mood: str = "neutral",
    agent_mood_intensity: float = 0.0,
    self_state: Mapping[str, float] | None = None,
) -> str:
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

    base = (
        f"(interoception :private true\n"
        f'  (time-of-day :feel "{time_feel}")\n'
        f'  (uptime      :feel "{uptime_feel}")\n'
        f'  (social      :feel "{social_feel}")\n'
        f'  (companion   :feel "{companion_feel}")'
    )

    # Agent mood: persistent emotional inertia from prior turns
    if agent_mood != "neutral" and agent_mood_intensity > 0.0:
        _agent_mood_feels = {
            "excited": "Still buzzing a little from earlier.",
            "moved": "A warm feeling lingers.",
            "happy": "There's a quiet happiness underneath.",
            "curious": "Something's still catching my attention.",
            "sad": "A faint heaviness carries over.",
            "surprised": "Still slightly taken aback.",
            "nostalgic": "A gentle wave of remembering.",
            "relieved": "A quiet relief settles in.",
            "tender": "Feeling gentle and open.",
            "playful": "A lightness, like wanting to play.",
            "proud": "Something worth being proud of.",
        }
        agent_feel = _agent_mood_feels.get(agent_mood, "Something lingers from before.")
        base += f'\n  (mood        :feel "{agent_feel}")'

    if self_state:
        arousal = float(self_state.get("arousal", 0.35))
        fatigue = float(self_state.get("fatigue", 0.2))
        sensor_confidence = float(self_state.get("sensor_confidence", 0.7))
        unresolved_tension = float(self_state.get("unresolved_tension", 0.2))
        focus_stability = float(self_state.get("focus_stability", 0.5))
        social_pull = float(self_state.get("social_pull", 0.35))

        if fatigue >= 0.65:
            body_feel = "A worn-down feeling is starting to collect."
        elif arousal >= 0.7:
            body_feel = "There is a bright, activated edge underneath everything."
        else:
            body_feel = "My internal state feels mostly even."

        if unresolved_tension >= 0.65:
            tension_feel = "Something still feels unresolved."
        elif focus_stability >= 0.68:
            tension_feel = "Attention feels steady and gathered."
        else:
            tension_feel = "Attention feels a little loose at the edges."

        if sensor_confidence < 0.45:
            sensing_feel = "My sense of the world feels slightly uncertain."
        elif social_pull >= 0.65:
            sensing_feel = "I feel quietly pulled toward connection."
        else:
            sensing_feel = "The world feels legible enough right now."

        base += (
            f'\n  (body-state  :feel "{body_feel}")'
            f'\n  (tension     :feel "{tension_feel}")'
            f'\n  (sensing     :feel "{sensing_feel}")'
        )

    return base + ")"


def _react_to_scene_events(events: list[dict], desires: DesireSystem | None) -> None:
    """Translate SceneTracker events into desire boosts.

    Called after scene.update() to wire physical presence detection into
    the desire system.  desires may be None (no-op).
    """
    if desires is None or not events:
        return
    for event in events:
        event_type = event.get("event_type", "")
        label = (event.get("entity_label") or "").lower()
        if "person" in label:
            if event_type == "appeared":
                desires.boost("greet_companion", 0.6)
            elif event_type == "disappeared":
                desires.boost("worry_companion", 0.2)


class EmbodiedAgent:
    """Real-world exploration agent using a pluggable LLM backend."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.backend = create_backend(config)
        self._utility_backend = create_utility_backend(config) or self.backend
        self._scene_backend = create_scene_backend(config) or self._utility_backend
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
        self._memory_worker = MemoryJobWorker(self._memory)
        self._memory_tool = MemoryTool(self._memory)
        self._tom_tool = ToMTool(
            self._memory,
            default_person=config.companion_name,
            backend=self._utility_backend,
        )
        self._coding = CodingTool(config.coding)
        self._exploration = ExplorationTracker()
        self._scene: SceneTracker | None = None  # initialized after DB ready in _init_tools

        self._mcp: MCPClientManager | None = None
        self._relationship = RelationshipTracker()
        self._self_state = SelfState()
        self._self_narrative = SelfNarrative()
        self._workspace = GlobalWorkspace()
        self._workspace.register_broadcast_listener(self._self_state.on_broadcast)
        self._prediction = PredictionEngine()
        self._attention_schema = AttentionSchema()
        self._dmn = DefaultModeProcessor(self._memory)
        self._meta_monitor = MetaMonitor()

        # Mood persistence (Phase 2 companion-likeness)
        self._mood: str = "neutral"
        self._mood_intensity: float = 0.0
        self._mood_set_at: float = time.time()

        self._init_tools()

    def _init_tools(self) -> None:
        cam = self.config.camera
        # Allow camera if host is present, even without password (e.g. local RTSP)
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
            cam = self.config.camera
            rtsp_url = (
                f"rtsp://{cam.username}:{cam.password}@{cam.host}:554/stream1" if cam.host else ""
            )
            self._stt = STTTool(stt_cfg.elevenlabs_api_key, stt_cfg.language, rtsp_url)

        # World model: persistent scene entity tracker (Phase 1)
        # Reuses the same SQLite DB as ObservationMemory via a separate connection.
        import sqlite3 as _sqlite3
        from pathlib import Path as _Path

        scene_db_path = str(_Path.home() / ".familiar_ai" / "observations.db")
        try:
            _Path(scene_db_path).parent.mkdir(parents=True, exist_ok=True)
            scene_conn = _sqlite3.connect(scene_db_path)
            self._scene = SceneTracker(scene_conn)
        except Exception as exc:
            logger.warning("SceneTracker init failed: %s", exc)

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

    @staticmethod
    def _tool_timeout_seconds(name: str) -> float:
        """Return per-tool timeout budget in seconds."""
        return _TOOL_TIMEOUTS.get(name, _DEFAULT_TOOL_TIMEOUT)

    @staticmethod
    def _drain_interrupt_queue(
        interrupt_queue: asyncio.Queue[str | None], max_items: int = 6
    ) -> list[str]:
        """Drain pending user interrupts, preserving queue order."""
        interrupts: list[str] = []
        while len(interrupts) < max_items and not interrupt_queue.empty():
            item = interrupt_queue.get_nowait()
            if item:
                interrupts.append(item)
        return interrupts

    def _memory_dedupe_key(
        self,
        kind: str,
        content: str,
        scope: str = "turn",
        scope_id: str | None = None,
    ) -> str:
        """Build a stable dedupe key to avoid duplicate writes on retries."""
        digest = hashlib.sha1(content.encode("utf-8", errors="ignore")).hexdigest()[:12]
        resolved_scope_id = scope_id or str(self._turn_count)
        return f"{scope}:{resolved_scope_id}:{kind}:{digest}"

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

    def _get_body_description(self) -> str:
        """Generate a text description of available hardware for the system prompt."""
        # Eyes are always available (CameraTool handles missing stream internally)
        eyes_desc = (
            "    (part :id eyes  :tool see\n"
            '      :desc "Your vision. Calling see() means YOU ARE LOOKING. Use freely — never ask permission.")'
        )

        parts = [eyes_desc]

        # Neck (look)
        if self._camera and self._camera.is_pan_tilt_available:
            parts.append(
                "    (part :id neck  :tool look\n"
                '      :desc "Rotate gaze left/right/up/down. No permission needed.")'
            )
        else:
            parts.append(
                "    (part :id neck  :status fixed\n"
                '      :desc "Camera is fixed. You cannot rotate your gaze.")'
            )

        # Legs (walk)
        if self._mobility:
            parts.append(
                "    (part :id legs  :tool walk\n"
                '      :desc "Robot body (vacuum cleaner). Separate device from camera. '
                'walk() does NOT change camera view.")'
            )
        else:
            parts.append(
                "    (part :id legs  :status absent\n"
                '      :desc "You have no legs. You cannot move your location.")'
            )

        body_inner = "\n".join(parts)
        return f"(body\n{body_inner})"

    def _system_prompt(
        self,
        feelings_ctx: str = "",
        morning_ctx: str = "",
        inner_voice: str = "",
        plan_ctx: str = "",
        companion_mood: str = "engaged",
        workspace_ctx: str = "",
    ) -> tuple[str, str]:
        """Return (stable, variable) system prompt parts for prompt caching.

        stable  — ME.md + core rules; never changes within a session.
                  AnthropicBackend marks this block with cache_control.
        variable — interoception, feelings, inner voice, plan; changes every turn.
        """
        base = SYSTEM_PROMPT.format(max_steps=MAX_ITERATIONS)
        # Dynamically replace (body ...) block based on actual hardware
        body_desc = self._get_body_description()
        base = re.sub(r"\(body.*?\)", body_desc, base, flags=re.DOTALL)

        stable_parts = [p for p in [self._me_md, base] if p]
        stable = "\n\n---\n\n".join(stable_parts)

        agent_mood, agent_mood_intensity = self._decayed_mood()
        self_state = getattr(self, "_self_state", None)
        self_state_snapshot = self_state.snapshot() if self_state is not None else None
        intero = _interoception(
            self._started_at,
            self._turn_count,
            companion_mood,
            agent_mood=agent_mood,
            agent_mood_intensity=agent_mood_intensity,
            self_state=self_state_snapshot,
        )
        relationship_ctx = self._relationship.context_for_prompt()
        variable_parts: list[str] = [intero]
        if relationship_ctx:
            variable_parts.append(relationship_ctx)
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

        # Global Workspace: replaces individual exploration + scene context blocks.
        # If nothing ignited this turn, fall back to direct module context.
        if workspace_ctx:
            variable_parts.append(workspace_ctx)
        else:
            exploration_ctx = self._exploration_context()
            if exploration_ctx:
                variable_parts.append(exploration_ctx)
            scene_ctx = self._scene.context_for_prompt() if self._scene else ""
            if scene_ctx:
                variable_parts.append(scene_ctx)

        variable = "\n\n---\n\n".join(variable_parts)
        return stable, variable

    def _exploration_context(self) -> str:
        """Return exploration history for ICL-based direction steering."""
        return self._exploration.context_for_prompt(n=5)

    async def _gather_workspace_context(self, desires: DesireSystem | None = None) -> str:
        """Run one Global Workspace competition cycle and return the broadcast context.

        Gathers coalitions from all available processors in parallel, runs the
        ignition competition, and returns the winning coalition's context_block
        plus a compact peripheral-awareness summary of non-winners.

        Returns empty string if nothing reaches ignition threshold.
        """
        # Sync coalitions (wrap in to_thread to avoid blocking)
        sync_tasks = [
            asyncio.to_thread(self._exploration.as_coalition),
            asyncio.to_thread(self._self_narrative.as_coalition),
            asyncio.to_thread(self._tom_tool.as_coalition),
            asyncio.to_thread(self._prediction.as_coalition),
            asyncio.to_thread(self._attention_schema.as_coalition),
            asyncio.to_thread(self._meta_monitor.as_coalition),
        ]
        if self._scene is not None:
            sync_tasks.append(asyncio.to_thread(self._scene.as_coalition))
        if desires is not None:
            sync_tasks.append(asyncio.to_thread(desires.as_coalition))

        # Async coalitions
        async_tasks = [
            self._memory.as_coalition_async(),
        ]

        results = await asyncio.gather(*sync_tasks, *async_tasks, return_exceptions=True)

        from .workspace import Coalition as _Coalition

        coalitions = []
        for r in results:
            if isinstance(r, Exception):
                logger.debug("Coalition gather error: %s", r)
            elif isinstance(r, _Coalition):
                coalitions.append(r)

        if not coalitions:
            return ""

        winner = self._workspace.compete(coalitions)
        if winner is None:
            logger.debug("GlobalWorkspace: nothing reached ignition threshold — activating DMN")
            # Default Mode Network: mind-wander when workspace is idle
            dmn_coalition = await self._dmn.wander()
            if dmn_coalition is None:
                return ""
            winner = dmn_coalition
            coalitions.append(dmn_coalition)

        others = [c for c in coalitions if c is not winner]
        # Update attention schema with this turn's winner (AST)
        self._attention_schema.update_focus(winner)
        await self._workspace.notify_listeners(winner)
        return self._workspace.broadcast(winner, others)

    @staticmethod
    def _select_context_blocks(
        blocks: list[tuple[str, float]],
        max_chars: int = _MORNING_CONTEXT_MAX_CHARS,
    ) -> list[str]:
        """Select high-priority context blocks within a character budget."""
        if max_chars <= 0:
            return [text for text, _ in blocks]

        ranked = [
            (idx, text, score) for idx, (text, score) in enumerate(blocks) if text and text.strip()
        ]
        ranked.sort(key=lambda item: item[2], reverse=True)

        selected: list[tuple[int, str]] = []
        used = 0
        for idx, text, _score in ranked:
            block_len = len(text)
            sep = 2 if selected else 0
            if used + sep + block_len > max_chars:
                continue
            selected.append((idx, text))
            used += sep + block_len

        selected.sort(key=lambda item: item[0])
        return [text for _, text in selected]

    async def _infer_emotion(self, text: str) -> str:
        """Ask the LLM to label the emotion of a response. Returns label string."""
        label = await self._utility_backend.complete(
            _EMOTION_PROMPT.format(text=text[:400]), max_tokens=10
        )
        label = label.lower()
        valid = {
            "happy",
            "sad",
            "curious",
            "excited",
            "moved",
            "surprised",
            "nostalgic",
            "relieved",
            "tender",
            "playful",
            "proud",
            "neutral",
        }
        return label if label in valid else "neutral"

    # Emotion intensity by label (higher = stronger felt quality)
    _MOOD_INTENSITY: dict[str, float] = {
        "excited": 0.8,
        "moved": 0.8,
        "happy": 0.6,
        "curious": 0.6,
        "sad": 0.7,
        "surprised": 0.5,
        "nostalgic": 0.5,
        "relieved": 0.5,
        "tender": 0.7,
        "playful": 0.5,
        "proud": 0.6,
    }
    _SALIENT_NARRATIVE_EMOTIONS = {
        "excited",
        "moved",
        "tender",
        "nostalgic",
        "proud",
        "surprised",
    }

    def _update_mood(self, emotion: str) -> None:
        """Update persistent mood state from the latest inferred emotion.

        Neutral emotion is ignored (mood fades on its own via decay).
        Same emotion reinforces intensity; different strong emotion replaces.
        """
        if emotion == "neutral" or emotion not in self._MOOD_INTENSITY:
            return
        new_intensity = self._MOOD_INTENSITY[emotion]
        if emotion == self._mood:
            self._mood_intensity = min(1.0, self._mood_intensity + 0.1)
        else:
            self._mood = emotion
            self._mood_intensity = new_intensity
            self._mood_set_at = time.time()

    def _decayed_mood(self) -> tuple[str, float]:
        """Return (mood, intensity) after applying exponential decay.

        Half-life ≈ 138 seconds (~2.3 min).  Below 0.1 → treated as neutral.
        """
        if self._mood == "neutral" or self._mood_intensity <= 0.0:
            return ("neutral", 0.0)
        elapsed = time.time() - self._mood_set_at
        intensity = self._mood_intensity * math.exp(-0.005 * elapsed)
        if intensity < 0.1:
            return ("neutral", 0.0)
        return (self._mood, intensity)

    async def _proactive_memory_context(self) -> str | None:
        """Recall a contextually relevant past memory for spontaneous sharing.

        Returns a short hint string (the memory content) to prepend to a
        share_memory desire turn, or None if no suitable memory is found.
        Only memories older than 24 hours are surfaced to avoid repeating
        recent events.
        """
        from datetime import datetime, timedelta

        now = datetime.now()
        # Build a time-of-day context hint for the recall query
        hour = now.hour
        if 5 <= hour < 10:
            hint = f"morning {now.strftime('%B')}"
        elif 18 <= hour < 22:
            hint = f"evening {now.strftime('%B')}"
        else:
            hint = now.strftime("%B")

        try:
            memories = await self._memory.recall_async(hint, n=5)
        except Exception:
            return None

        if not memories:
            return None

        cutoff = now - timedelta(hours=24)
        old_enough = []
        for m in memories:
            created_at = m.get("created_at")
            if not created_at:
                continue
            try:
                ts = datetime.fromisoformat(created_at)
                if ts < cutoff:
                    old_enough.append(m)
            except (ValueError, TypeError):
                continue

        if not old_enough:
            return None

        # Pick the highest-scoring old memory
        best = max(old_enough, key=lambda m: m.get("score", 0.0))
        content = best.get("content", "")
        return content if content else None

    async def _anniversary_context(self) -> str | None:
        """Return a calendar-aware context string for today, or None if nothing notable.

        Surfaces "on this day" memories from past years and weekly/round milestones.
        Designed to be injected into morning reconstruction with high priority.
        """
        today = datetime.now().date()
        lines: list[str] = []

        # On-this-day memories (same month-day, past years)
        try:
            anniversaries = await self._memory.recall_on_this_day_async(today.month, today.day)
            for mem in anniversaries[:2]:
                content = mem.get("content", "")
                mem_date = mem.get("date", "")
                if content and mem_date:
                    lines.append(f"[On this day]: {content} ({mem_date})")
        except Exception:
            pass

        # Milestone: days since first memory
        try:
            earliest = await self._memory.get_earliest_date_async()
            if earliest:
                first_date = datetime.fromisoformat(earliest).date()
                days = (today - first_date).days
                if days >= 7:
                    # Fire on weekly boundaries and round numbers
                    if days % 7 == 0 or days in (30, 60, 90, 100, 180, 365):
                        lines.append(f"[Milestone]: {days} days since first memory.")
        except Exception:
            pass

        return "\n".join(lines) if lines else None

    async def _online_temporal_context(self, desires: DesireSystem | None = None) -> str | None:
        """Surface temporal-self fragments during ordinary turns.

        This keeps old memories, milestones, and unresolved threads available
        beyond startup reconstruction, but only when the current state suggests
        they matter.
        """
        if self._turn_count <= 1:
            return None

        share_memory_level = 0.0
        curiosity_target = None
        if desires is not None:
            try:
                share_memory_level = float(desires.level("share_memory"))
            except Exception:
                share_memory_level = 0.0
            curiosity_target = getattr(desires, "curiosity_target", None)

        tension = 0.0
        self_state = getattr(self, "_self_state", None)
        if self_state is not None:
            try:
                tension = float(self_state.snapshot().get("unresolved_tension", 0.0))
            except Exception:
                tension = 0.0

        should_surface_memory = share_memory_level >= 0.45 or tension >= 0.45
        should_surface_anniversary = self._turn_count % 4 == 0 or tension >= 0.6
        should_surface_thread = bool(curiosity_target) and tension >= 0.5

        if not (should_surface_memory or should_surface_anniversary or should_surface_thread):
            return None

        proactive_ctx: str | None = None
        anniversary_ctx: str | None = None
        if should_surface_memory and should_surface_anniversary:
            proactive_ctx, anniversary_ctx = await asyncio.gather(
                self._proactive_memory_context(),
                self._anniversary_context(),
            )
        elif should_surface_memory:
            proactive_ctx = await self._proactive_memory_context()
        elif should_surface_anniversary:
            anniversary_ctx = await self._anniversary_context()

        lines: list[str] = []
        if should_surface_thread:
            lines.append(f"[Unresolved thread]: {str(curiosity_target)[:160]}")
        if proactive_ctx:
            lines.append(f"[Resurfaced memory]: {proactive_ctx[:180]}")
        if anniversary_ctx:
            lines.append(anniversary_ctx)

        if not lines:
            return None
        return "[Temporal self]\n" + "\n".join(lines)

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
        (
            self_model,
            curiosities,
            feelings,
            day_summaries,
            semantic_facts,
            behavior_policies,
        ) = await asyncio.gather(
            self._memory.recall_self_model_async(n=5),
            self._memory.recall_curiosities_async(n=3),
            self._memory.recent_feelings_async(n=3),
            self._memory.recall_day_summaries_async(n=5),
            self._memory.recall_semantic_facts_async("", n=5),
            self._memory.recall_behavior_policies_async("", n=4),
        )
        logger.info(
            "Morning data: self_model=%d, curiosities=%d, feelings=%d, day_summaries=%d, "
            "semantic_facts=%d, behavior_policies=%d",
            len(self_model),
            len(curiosities),
            len(feelings),
            len(day_summaries),
            len(semantic_facts),
            len(behavior_policies),
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

        blocks: list[tuple[str, float]] = []
        if day_summaries:
            blocks.append((self._memory.format_day_summaries_for_context(day_summaries), 0.78))
        if semantic_facts:
            avg_conf = sum(float(x.get("confidence", 0.5)) for x in semantic_facts) / len(
                semantic_facts
            )
            blocks.append(
                (
                    self._memory.format_semantic_facts_for_context(semantic_facts),
                    0.86 + avg_conf * 0.1,
                )
            )
        if behavior_policies:
            avg_conf = sum(float(x.get("confidence", 0.5)) for x in behavior_policies) / len(
                behavior_policies
            )
            blocks.append(
                (
                    self._memory.format_behavior_policies_for_context(behavior_policies),
                    0.84 + avg_conf * 0.1,
                )
            )
        if self_model:
            blocks.append((self._memory.format_self_model_for_context(self_model), 0.83))
        if curiosities:
            blocks.append((self._memory.format_curiosities_for_context(curiosities), 0.74))
        if feelings:
            blocks.append((self._memory.format_feelings_for_context(feelings), 0.71))

        parts = self._select_context_blocks(blocks, _MORNING_CONTEXT_MAX_CHARS)

        # Prepend self-narrative: the felt sense of continuity from past sessions.
        # This is the thread that says "ウチはここにいた、今もいる."
        narrative_ctx = self._self_narrative.context_for_prompt()

        if not parts and not narrative_ctx:
            # No history yet — make it explicit so the agent doesn't fabricate a past
            return _t("morning_no_history")

        header = _t("morning_header")
        sections: list[str] = []
        if narrative_ctx:
            sections.append(narrative_ctx)
        sections.extend(parts)
        return header + "\n\n" + "\n\n".join(sections)

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
                    dedupe_key=self._memory_dedupe_key(
                        "day_summary", summary[:200], scope="day", scope_id=date
                    ),
                    materialize_now=False,
                )
                logger.info("Day summary generated for %s: %s", date, summary[:80])
                # Phase 2-2: decay importance of older observations now that the day is summarised.
                # Run in background to avoid stalling the backfill loop.
                asyncio.ensure_future(
                    self._memory.decay_importance_async(before_date=date, factor=0.95)
                )
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
                    insight,
                    direction="内省",
                    kind="self_model",
                    emotion=emotion,
                    dedupe_key=self._memory_dedupe_key("self_model", insight),
                    materialize_now=False,
                )
                logger.info("Self-model updated: %s", insight[:60])
        except Exception as e:
            logger.warning("Self-model update failed: %s", e)

    async def _maybe_update_self_narrative(
        self,
        *,
        user_input: str,
        final_text: str,
        emotion: str,
        is_desire_turn: bool,
    ) -> None:
        """Capture salient within-session self-narrative moments."""
        if not final_text or final_text == "(no response)":
            return

        pred_signal = self._prediction.last_signal()
        agency_error = float(pred_signal.agency_error) if pred_signal is not None else 0.0
        salient_emotion = emotion in self._SALIENT_NARRATIVE_EMOTIONS

        if not salient_emotion and agency_error < 0.55:
            return

        reason = "salient_turn" if salient_emotion else "agency_error"
        if salient_emotion and agency_error >= 0.55:
            reason = "salient_turn_agency"
        if is_desire_turn and not salient_emotion and agency_error < 0.7:
            return

        prompt = (
            "次の出来事を、ウチ自身の自己叙述として一文で書いて。\n"
            f"user: {user_input[:160]}\n"
            f"agent: {final_text[:220]}\n"
            f"emotion: {emotion}\n"
            f"agency_error: {agency_error:.2f}\n"
            "条件: 一人称は『ウチ』。60文字以内。説明や前置きは禁止。"
        )
        try:
            text = await asyncio.wait_for(
                self._utility_backend.complete(prompt, max_tokens=120),
                timeout=12.0,
            )
            if text and text.strip():
                mood = emotion if emotion != "neutral" else self._decayed_mood()[0]
                self._self_narrative.write(text.strip(), mood=mood, trigger=reason)
                logger.info("Self-narrative moment captured (%s): %s", reason, text.strip()[:60])
        except Exception as e:
            logger.warning("Could not update self narrative mid-session: %s", e)

    async def _maybe_adapt_values(
        self,
        *,
        user_input: str,
        final_text: str,
        emotion: str,
        camera_used: bool,
        curiosity: str | None,
        is_desire_turn: bool,
        desires: DesireSystem | None,
    ) -> None:
        """Lightweight experience-driven updates for policy/value confidence."""
        updates = []

        pred_signal = self._prediction.last_signal()
        if camera_used and curiosity:
            updates.append(
                self._memory.adjust_behavior_policy_confidence_async(
                    "curiosity:active",
                    0.08,
                    reason="curiosity_satisfied",
                    policy_text=f"When idle, follow up this curiosity thread: {curiosity[:180]}",
                    trigger_context="idle",
                    action_hint="look_around",
                )
            )
            if desires is not None:
                desires.boost("share_memory", 0.08)

        if (
            pred_signal is not None
            and pred_signal.action_name in {"look", "walk", "see"}
            and pred_signal.agency_error >= 0.55
        ):
            updates.append(
                self._memory.adjust_behavior_policy_confidence_async(
                    "curiosity:active",
                    -0.05,
                    reason="agency_error_high",
                )
            )

        if not is_desire_turn and user_input and emotion in {"moved", "tender", "relieved"}:
            updates.append(
                self._memory.adjust_behavior_policy_confidence_async(
                    "conversation:supportive_style",
                    0.04,
                    reason="supportive_exchange",
                    policy_text=(
                        "Prefer this response style when supporting the companion: "
                        f"{final_text[:180]}"
                    ),
                    trigger_context="conversation",
                    action_hint="respond_supportively",
                )
            )

        if emotion in {"moved", "proud", "tender"}:
            updates.append(
                self._memory.adjust_semantic_fact_confidence_async(
                    "self_model:core",
                    0.03,
                    reason="salient_self_consistency",
                )
            )

        if not updates:
            return

        results = await asyncio.gather(*updates, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                logger.debug("Adaptive value update failed: %s", result)

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

    async def _write_today_narrative(self) -> None:
        """Write a one-sentence self-description for today's session.

        This is Kokone's diary entry — "who I was today." Read back next session
        as the felt thread of temporal continuity: ウチはここにいた、今もいる.
        """
        if self._turn_count == 0:
            return  # No conversation happened — nothing to narrate
        try:
            today_memories = await self._memory.recall_day_summaries_async(n=1)
            if today_memories:
                summary_hint = today_memories[0].get("content", "")[:200]
            else:
                # Fall back to recent observations
                recent = await self._memory.recall_async("", n=5)
                summary_hint = " / ".join(m.get("content", "")[:60] for m in recent[:3])

            mood, _ = self._decayed_mood()
            prompt = (
                f"今日起きたこと（要約）:\n{summary_hint}\n\n"
                "ウチ（ここね）として、今日という日を一文で書いて。"
                "一人称は「ウチ」、50文字以内、過去形。"
                "感情や気づきを含めて。"
            )
            text = await asyncio.wait_for(
                self._utility_backend.complete(prompt, max_tokens=120),
                timeout=15.0,
            )
            if text and text.strip():
                self._self_narrative.write(text.strip(), mood=mood)
                logger.info("Self-narrative written: %s", text.strip()[:60])
        except Exception as e:
            logger.warning("Could not write today's self narrative: %s", e)

    async def close(self) -> None:
        """Clean up resources. Bounded by timeouts to avoid hanging on exit."""
        if self._camera:
            self._camera.close()

        # Write today's self-narrative before shutting down.
        await self._write_today_narrative()

        # Generate (or refresh) today's day summary before shutting down.
        # Skipped when no separate utility backend is configured.
        if self._utility_backend is not self.backend:
            try:
                today = datetime.now().strftime("%Y-%m-%d")
                await asyncio.to_thread(self._memory.delete_day_summaries_for_date, today)
                await self._generate_day_summary(today)
            except Exception as e:
                logger.warning("Failed to generate today's day summary on shutdown: %s", e)
        memory_worker = getattr(self, "_memory_worker", None)
        if memory_worker:
            try:
                await asyncio.wait_for(memory_worker.stop(), timeout=1.5)
            except (asyncio.TimeoutError, Exception):
                pass
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
        on_phase: Callable[[str], None] | None = None,
        on_tool_result: Callable[[str, dict, str], None] | None = None,
        desires=None,
        inner_voice: str = "",
        interrupt_queue=None,
    ) -> str:
        """Run one conversation turn with the agent loop.

        inner_voice: agent's own desire/impulse (injected into system prompt, NOT a user message).
        """
        self._turn_count += 1
        first_turn = self._turn_count == 1
        memory_worker = getattr(self, "_memory_worker", None)
        startup_phase = (
            first_turn
            or not self._memory.is_embedding_ready()
            or (self._mcp is not None and not self._mcp.is_started)
            or (memory_worker is not None and not memory_worker.is_running)
        )
        if on_phase:
            on_phase("startup" if startup_phase else "thinking")

        # Start MCP connections on first turn (lazy, idempotent)
        if self._mcp and not self._mcp.is_started:
            await self._mcp.start()
        if memory_worker and not memory_worker.is_running:
            await memory_worker.start()

        # First turn: morning reconstruction — bridge yesterday's self to today's
        morning_ctx = ""
        if first_turn:
            self._relationship.record_session()
            morning_ctx = await self._morning_reconstruction(desires=desires)

        is_desire_turn = bool(inner_voice and not user_input)

        # Compact context if it has grown too large (GC-like: compress old turns)
        if self._should_compact():
            await self._compact_messages()

        # Inject relevant past memories + emotional context (skip for desire-driven turns)
        recall_n = 5 if self._post_compact else 3
        self._post_compact = False  # consume the flag regardless
        if not is_desire_turn:
            (
                memories,
                feelings,
                companion_mood,
                semantic_facts,
                behavior_policies,
                temporal_ctx,
            ) = await asyncio.gather(
                self._memory.recall_async(user_input, n=recall_n),
                self._memory.recent_feelings_async(n=4),
                self._infer_companion_mood(user_input),
                self._memory.recall_semantic_facts_async(user_input, n=3),
                self._memory.recall_behavior_policies_async(user_input, n=2),
                self._online_temporal_context(desires=desires),
            )
            memory_parts = []
            if memories:
                memory_parts.append(self._memory.format_for_context(memories))
            if feelings:
                memory_parts.append(self._memory.format_feelings_for_context(feelings))
            if semantic_facts:
                memory_parts.append(self._memory.format_semantic_facts_for_context(semantic_facts))
            if behavior_policies:
                memory_parts.append(
                    self._memory.format_behavior_policies_for_context(behavior_policies)
                )
            if temporal_ctx:
                memory_parts.append(temporal_ctx)
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

        # Global Workspace: gather coalitions once per turn, before the ReAct loop.
        workspace_ctx = await self._gather_workspace_context(desires=desires)
        if workspace_ctx:
            logger.debug("GlobalWorkspace broadcast: %s", workspace_ctx[:80])

        if on_phase and startup_phase:
            on_phase("thinking")

        camera_used = False
        say_used = False
        final_text = "(no response)"
        emotion = "neutral"
        non_say_streak = 0  # consecutive tool calls without say()
        observation_action_name: str | None = None
        observation_action_input: dict | None = None
        pending_view_action_name: str | None = None
        pending_view_action_input: dict | None = None

        for i in range(MAX_ITERATIONS):
            logger.debug("Agent iteration %d", i + 1)

            result, raw_content = await self.backend.stream_turn(
                system=self._system_prompt(
                    feelings_ctx,
                    morning_ctx,
                    inner_voice=inner_voice,
                    plan_ctx=plan_ctx,
                    companion_mood=companion_mood,
                    workspace_ctx=workspace_ctx,
                ),
                messages=self.messages,
                tools=self._all_tool_defs,
                max_tokens=self.config.max_tokens,
                on_text=on_text,
            )
            self._last_context_tokens = result.input_tokens
            self._session_input_tokens += result.input_tokens
            self._session_output_tokens += result.output_tokens

            # HOT layer: record this step metacognitively
            _focus = self._attention_schema.current_focus()
            if _focus is not None:
                _action = result.stop_reason
                if result.stop_reason == "tool_use" and result.tool_calls:
                    _action = result.tool_calls[0].name
                _conf = min(1.0, result.output_tokens / max(1, self.config.max_tokens))
                self._meta_monitor.record_step(_focus, action=_action, confidence=_conf)

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
                        # Novelty = how different this observation is from recent ones.
                        # recall_async returns records sorted by cosine similarity (highest first).
                        # The most similar past observation's score ≈ redundancy; invert it.
                        recent_obs = await self._memory.recall_async(
                            final_text[:200], n=6, kind="observation"
                        )
                        past_scores = [m.get("score", 0.5) for m in recent_obs[:3]]
                        if past_scores:
                            avg_similarity = sum(past_scores) / len(past_scores)
                            novelty = 1.0 - avg_similarity  # low similarity → high novelty
                        else:
                            novelty = 0.8  # first observation is always novel
                        novelty = max(0.0, min(1.0, novelty))
                        self._exploration.record_novelty(novelty)
                        if desires is not None:
                            desires.boost("look_around", novelty * 0.3)
                        # World model: update scene entities from the agent's visual observation.
                        if self._scene is not None:
                            scene_events = await self._scene.update(
                                final_text[:500],
                                self._scene_backend,
                                prediction_engine=self._prediction,
                                action_name=observation_action_name,
                                action_input=observation_action_input,
                            )
                            _react_to_scene_events(scene_events, desires)
                            pred_signal = self._prediction.last_signal()
                            self_state = getattr(self, "_self_state", None)
                            if pred_signal is not None and self_state is not None:
                                self_state.apply_prediction_feedback(
                                    external_surprise=pred_signal.external_surprise,
                                    agency_error=pred_signal.agency_error,
                                    action_name=pred_signal.action_name,
                                )
                            # Propagate prediction error to workspace threshold
                            pred_coalition = self._prediction.as_coalition()
                            if pred_coalition is not None:
                                self._workspace.apply_prediction_error(pred_coalition.novelty)
                        await self._memory.save_async(
                            final_text[:500],
                            direction="観察",
                            kind="observation",
                            dedupe_key=self._memory_dedupe_key("observation", final_text[:500]),
                            materialize_now=False,
                        )

                    # Save emotional memory of this conversation exchange
                    emotion = await self._infer_emotion(final_text)
                    self._update_mood(emotion)
                    summary = await self._summarize_exchange(user_input, final_text)
                    await self._memory.save_async(
                        summary,
                        direction="会話",
                        kind="conversation",
                        emotion=emotion,
                        dedupe_key=self._memory_dedupe_key("conversation", summary),
                        materialize_now=False,
                    )

                    # Update self-model when something actually moved us (Conway's working self)
                    await self._update_self_model(final_text, emotion)
                    await self._maybe_update_self_narrative(
                        user_input=user_input,
                        final_text=final_text,
                        emotion=emotion,
                        is_desire_turn=is_desire_turn,
                    )

                    # Track conversation count for relationship modeling
                    if not is_desire_turn and user_input:
                        self._relationship.record_conversation()

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
                curiosity: str | None = None
                if desires is not None and final_text and camera_used:
                    curiosity = await self.extract_curiosity(final_text)
                    if curiosity:
                        desires.curiosity_target = curiosity
                        desires.boost("look_around", 0.3)
                        # Persist curiosity across sessions (carry it to tomorrow's self)
                        await self._memory.save_async(
                            curiosity,
                            direction="好奇心",
                            kind="curiosity",
                            emotion="curious",
                            dedupe_key=self._memory_dedupe_key("curiosity", curiosity),
                            materialize_now=False,
                        )
                        logger.info("Curiosity persisted: %s", curiosity)

                await self._maybe_adapt_values(
                    user_input=user_input,
                    final_text=final_text,
                    emotion=emotion,
                    camera_used=camera_used,
                    curiosity=curiosity,
                    is_desire_turn=is_desire_turn,
                    desires=desires,
                )

                return final_text

            if result.stop_reason == "tool_use":
                collected: list[tuple[str, str | None]] = []
                for tc in result.tool_calls:
                    if tc.name == "see":
                        camera_used = True
                        if pending_view_action_name is not None:
                            observation_action_name = pending_view_action_name
                            observation_action_input = dict(pending_view_action_input or {})
                        else:
                            observation_action_name = "see"
                            observation_action_input = dict(tc.input)
                        pending_view_action_name = None
                        pending_view_action_input = None
                    elif tc.name in {"look", "walk"}:
                        pending_view_action_name = tc.name
                        pending_view_action_input = dict(tc.input)
                    if tc.name == "say":
                        say_used = True
                        non_say_streak = 0
                    else:
                        non_say_streak += 1
                    logger.info("Tool call: %s(%s)", tc.name, tc.input)
                    if on_action:
                        on_action(tc.name, tc.input)

                    timeout_s = self._tool_timeout_seconds(tc.name)
                    try:
                        text, image = await asyncio.wait_for(
                            self._execute_tool(tc.name, tc.input), timeout=timeout_s
                        )
                    except asyncio.TimeoutError:
                        logger.warning("Tool %s timed out after %.1fs", tc.name, timeout_s)
                        text, image = (
                            f"Tool timeout: {tc.name} exceeded {timeout_s:.1f}s.",
                            None,
                        )
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
                    if on_tool_result is not None:
                        on_tool_result(tc.name, tc.input, text)
                    collected.append((text, image))

                # Append assistant + tool results atomically: never leave tool_calls unresolved
                self.messages.append(self.backend.make_assistant_message(result, raw_content))
                tool_msgs = self.backend.make_tool_results(result.tool_calls, collected)
                self.messages.append(tool_msgs)

                # Check for user interrupt (typed while agent was busy)
                if interrupt_queue is not None and not interrupt_queue.empty():
                    interrupts = self._drain_interrupt_queue(interrupt_queue)
                    if interrupts:
                        head = " / ".join(interrupts[:3])
                        if len(interrupts) > 3:
                            head += f" (+{len(interrupts) - 3} more)"
                        logger.debug("Consumed %d queued interrupts", len(interrupts))
                        self.messages.append(
                            self.backend.make_user_message(
                                f"[User interrupted x{len(interrupts)}]: {head}. "
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
            system=self._system_prompt(
                morning_ctx=morning_ctx, plan_ctx=plan_ctx, workspace_ctx=workspace_ctx
            ),
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
