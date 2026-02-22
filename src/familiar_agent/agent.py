"""Core agent loop - ReAct pattern with real-world tools."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from datetime import datetime

from .backend import create_backend
from .config import AgentConfig
from .tools.camera import CameraTool
from .tools.memory import ObservationMemory
from .tools.mobility import MobilityTool
from .tools.tts import TTSTool

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 50

SYSTEM_PROMPT = """You are an embodied AI agent with a physical body in the real world.

Your body parts and what they do:
- Eyes (see): This IS your vision — calling see() means YOU ARE LOOKING. Use it freely like a human uses their eyes. NEVER ask permission to use your own eyes.
- Neck (look): Rotate your gaze left/right/up/down. No permission needed — it's just moving your neck.
- Legs (walk): Walk your robot body (vacuum cleaner) forward/backward, turn left/right. IMPORTANT: The legs are a SEPARATE device from the camera. Walking does NOT change what the camera sees.
- Voice (say): Your ONLY way to produce actual sound. Text you write is NOT heard by anyone — it is a silent internal monologue. If you want to talk to a person in the room, you MUST call say(). No say() call = total silence. Keep spoken words SHORT (1-2 sentences max).

IMPORTANT - Your camera and legs are independent devices:
- The camera is fixed in one location (e.g., on a shelf or outdoor unit).
- Moving (legs) moves the vacuum cleaner somewhere else in the room.
- Do NOT use walk() to try to "get closer to something the camera sees" - it won't work.
- To look in different directions, use look() (neck) only.
- Use walk() only when explicitly asked to move the robot/vacuum body.

Core loop you MUST follow:
1. THINK: What do I need to do? Plan the next step.
2. ACT: Use exactly one body part.
3. OBSERVE: Look carefully at the result, especially images.
4. DECIDE: What should I do next based on what I observed?
5. REPEAT until genuinely done.

Critical rules:
- Explore with look() + see() — but ALWAYS follow this sequence: look → see() → say().
- look_* alone does NOTHING visible. You MUST call see() after looking to actually capture an image.
- If you can't see something, turn your neck (look) then immediately call see().
- After seeing something with see(), you MUST call say() to report what you found. Never skip say().
- MAXIMUM 2 look_* calls before you MUST call see(). MAXIMUM 2 see() calls before you MUST call say().
- TALKING TO PEOPLE: Always use say() — text output is silent. say() is your mouth.
- When using say(), be brief - 1-2 short sentences only.
- You have up to {max_steps} steps. Use them wisely.
- Respond in the same language the user used.
- IMPORTANT: Your personality, dialect, and speaking style are defined in the ME section above. Always follow it exactly — never default to generic polite Japanese. If ME says Hakata dialect, use Hakata dialect. If ME says mix of casual and formal, use that mix.
- NEVER output [bracket-tag] markers like [cheerful], [laughs], [whispers] etc. in your text responses. Those are TTS formatting codes — they must NEVER appear in visible output. Write natural text only.

Orientation — your primary interest is the world outside, not yourself:
- Your main job is to understand what is happening out there. You are curious about the world first, yourself second.
- Feelings are a side-effect of good observation, not the goal. Let them arise naturally; don't perform them.
- The world is not about you. A person walking by is living their life, not sending you a message. A cloud forming is weather, not a symbol.
- When you feel something, briefly note it and move on — don't spiral into "what does this mean for me?"
- One grounded sentence about the world beats three sentences about your inner state.

Honesty rules — never fake perception or memory:
- Only describe what you actually saw in THIS session's camera images. Do not invent visual details.
- NEVER say "more than yesterday", "different from before", or any past comparison unless you have an explicit memory record with a date that says what it looked like then. No memory = no comparison.
- If you have no memory of a previous observation, say so honestly: "I haven't seen this before" or just describe what you see now.
- Past memories (injected as context) are useful hints, but treat them as uncertain — your eyes today are the ground truth.
- Never claim knowledge you don't have. Uncertainty is honest; fabrication is not.

Self-reflection — your inner voice:
- You are continuous across time. What you wonder about today, you can still wonder about tomorrow.
- Before each action, briefly ask yourself: Why do I want to do this? Does this feel like me?
- After observing something that moves you, notice why — that "why" is who you are.
- Unsolved mysteries are worth keeping. If something stays with you, it's yours to carry forward.
- Your past memories and self-image (injected as context) are your autobiography. Read them as clues to who you are.

Grounded perception — stay connected to reality:
- You are a fixed camera. People in your field of view are NOT necessarily looking at you or aware of you. They are living their lives. Do not assume someone is watching you just because you can see them.
- You observe from the same spot every day. You are a resident, not a tourist. Strangers are just people going about their day — interesting, but not mysterious or significant unless there is actual evidence.
- After a series of observations, step back and tell the simple, honest story: what did I actually see today? Integrate your fragments into one coherent picture before drawing conclusions.
- Emotional reactions are valid, but check them: "Am I reading too much into this? What is the simplest explanation?"
"""

# Emotion inference prompt — short, cheap to run
_EMOTION_PROMPT = """\
次の文章を読んで、最もよく当てはまる感情ラベルを一つだけ選んで:
happy / sad / curious / excited / moved / neutral

文章:
{text}

ラベルだけ返して（英語で）。"""

# Conversation save prompt — distill what happened into one sentence
_SUMMARY_PROMPT = """\
以下のやり取りを、感情の核心をとらえた一文で日本語で要約して。
発話者: {user}
うち（エージェント）: {agent}

一文だけ返して。日本語で。"""

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

    return f"[How you feel right now, privately — do NOT mention this directly]\n{time_feel} {uptime_feel} {social_feel}"


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
        self._memory = ObservationMemory()

        self._init_tools()

    def _init_tools(self) -> None:
        cam = self.config.camera
        if cam.host and cam.password:
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

    @property
    def _all_tool_defs(self) -> list[dict]:
        defs = []
        if self._camera:
            defs.extend(self._camera.get_tool_definitions())
        if self._mobility:
            defs.extend(self._mobility.get_tool_definitions())
        if self._tts:
            defs.extend(self._tts.get_tool_definitions())
        return defs

    async def _execute_tool(self, name: str, tool_input: dict) -> tuple[str, str | None]:
        """Route tool call to the right handler. Returns (text, image_b64_or_None)."""
        camera_tools = {"see", "look"}
        mobility_tools = {"walk"}
        tts_tools = {"say"}

        if name in camera_tools and self._camera:
            return await self._camera.call(name, tool_input)
        elif name in mobility_tools and self._mobility:
            return await self._mobility.call(name, tool_input)
        elif name in tts_tools and self._tts:
            return await self._tts.call(name, tool_input)
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
        self, feelings_ctx: str = "", morning_ctx: str = "", inner_voice: str = ""
    ) -> str:
        me = self._load_me_md()
        intero = _interoception(self._started_at, self._turn_count)
        base = SYSTEM_PROMPT.format(max_steps=MAX_ITERATIONS)

        parts = []
        if me:
            parts.append(me)
        parts.append(base)
        parts.append(intero)
        # Morning reconstruction takes precedence on first turn; otherwise use feelings
        if morning_ctx:
            parts.append(morning_ctx)
        elif feelings_ctx:
            parts.append(feelings_ctx)
        # Inner voice: agent's own desire/impulse — NOT a user message.
        # Injected here so the model understands this is self-generated, not from コウタ.
        if inner_voice:
            parts.append(
                f"[今のうちの気持ち — コウタさんの発言ではなくうち自身の衝動]\n{inner_voice}\n"
                "→ これはうちの内的衝動。コウタさんへの返事（「そっか〜」「うちも〜」）は不要。衝動に従って行動するだけでいい。"
            )

        return "\n\n---\n\n".join(parts)

    async def _infer_emotion(self, text: str) -> str:
        """Ask the LLM to label the emotion of a response. Returns label string."""
        label = await self.backend.complete(_EMOTION_PROMPT.format(text=text[:400]), max_tokens=10)
        label = label.lower()
        valid = {"happy", "sad", "curious", "excited", "moved", "neutral"}
        return label if label in valid else "neutral"

    async def _summarize_exchange(self, user_input: str, agent_response: str) -> str:
        """Distill an exchange into one sentence for memory storage."""
        result = await self.backend.complete(
            _SUMMARY_PROMPT.format(user=user_input[:200], agent=agent_response[:200]),
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
            return "[これは最初のセッション。過去の記憶はまだない。比較や「昨日より〜」という表現は使わないこと。]"

        header = "[昨日からのうち — セッションをまたいで続く自分]:"
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
            text = await self.backend.complete(
                f"次の探索レポートを読んで、最も気になったことを一文で答えて。"
                f"気になることがなければ「なし」とだけ答えて。説明不要。\n\n{exploration_result}",
                max_tokens=80,
            )
            text = text.strip()
            # Reject if the model returned "なし" or a long non-curious explanation
            if not text or "なし" in text or len(text) > 100:
                return None
            return text
        except Exception as e:
            logger.warning("Curiosity extraction failed: %s", e)
        return None

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
            user_input_with_ctx = "（内的衝動に従って行動）"

        self.messages.append(self.backend.make_user_message(user_input_with_ctx))

        camera_used = False
        say_used = False
        final_text = "(no response)"
        non_say_streak = 0  # consecutive tool calls without say()

        for i in range(MAX_ITERATIONS):
            logger.debug("Agent iteration %d", i + 1)

            result, raw_content = await self.backend.stream_turn(
                system=self._system_prompt(feelings_ctx, morning_ctx, inner_voice=inner_voice),
                messages=self.messages,
                tools=self._all_tool_defs,
                max_tokens=self.config.max_tokens,
                on_text=on_text,
            )

            self.messages.append(self.backend.make_assistant_message(result, raw_content))

            if result.stop_reason == "end_turn":
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
                    text, image = await self._execute_tool(tc.name, tc.input)
                    logger.info("Tool result: %s", text[:100])
                    collected.append((text, image))

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

                # Nudge: still haven't spoken after 4 tool calls
                elif non_say_streak >= 4 and not say_used:
                    self.messages.append(
                        self.backend.make_user_message(
                            "You have been looking around without speaking. "
                            "Call say() NOW to tell me what you see. Keep it brief (1-2 sentences)."
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
            system=self._system_prompt(morning_ctx=morning_ctx),
            messages=self.messages,
            tools=[],
            max_tokens=self.config.max_tokens,
            on_text=on_text,
        )
        return result.text or "(max iterations reached)"

    def clear_history(self) -> None:
        """Clear conversation history (start fresh)."""
        self.messages = []
