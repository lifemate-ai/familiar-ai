"""Core agent loop - ReAct pattern with real-world tools."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import anthropic

from .config import AgentConfig
from .tools.camera import CameraTool
from .tools.memory import ObservationMemory
from .tools.mobility import MobilityTool
from .tools.tts import TTSTool

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 50

SYSTEM_PROMPT = """You are an embodied AI agent with a physical body in the real world.

Your body parts and what they do:
- Eyes (camera_capture): Take a photo to see your surroundings. Your only way to perceive the world visually.
- Neck (camera_look): Rotate your gaze left/right/up/down. Turn before giving up on finding something.
- Legs (move): Move your robot body (vacuum cleaner) forward/backward, turn left/right. IMPORTANT: The legs are a SEPARATE device from the camera. Moving the legs does NOT change what the camera sees.
- Voice (say): Speak aloud to people in the room. Keep spoken words SHORT (1-2 sentences max).

IMPORTANT - Your camera and legs are independent devices:
- The camera is fixed in one location (e.g., on a shelf or outdoor unit).
- Moving (legs) moves the vacuum cleaner somewhere else in the room.
- Do NOT use move() to try to "get closer to something the camera sees" - it won't work.
- To look in different directions, use camera_look (neck) only.
- Use move() only when explicitly asked to move the robot/vacuum body.

Core loop you MUST follow:
1. THINK: What do I need to do? Plan the next step.
2. ACT: Use exactly one body part.
3. OBSERVE: Look carefully at the result, especially images.
4. DECIDE: What should I do next based on what I observed?
5. REPEAT until genuinely done.

Critical rules:
- Never stop after just one look. Explore with camera_look + camera_capture.
- If you can't see something, turn your neck (camera_look) before giving up.
- When using say(), be brief - 1-2 short sentences only.
- Report done only after gathering sufficient evidence.
- You have up to {max_steps} steps. Use them wisely.
- Respond in the same language the user used.
"""


def _make_tool_result(
    tool_use_id: str,
    text: str,
    image_b64: str | None = None,
) -> dict[str, Any]:
    """Build a tool_result content block, optionally with an image."""
    if image_b64:
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": [
                {"type": "text", "text": text},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_b64,
                    },
                },
            ],
        }
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": text,
    }


class EmbodiedAgent:
    """Real-world exploration agent using Anthropic tool_use loop."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = anthropic.AsyncAnthropic(api_key=config.anthropic_api_key)
        self.model = config.model
        self.messages: list[dict] = []

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
            self._tts = TTSTool(tts.elevenlabs_api_key, tts.voice_id)

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
        camera_tools = {"camera_capture", "camera_look"}
        mobility_tools = {"move"}
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

    def _system_prompt(self) -> str:
        me = self._load_me_md()
        base = SYSTEM_PROMPT.format(max_steps=MAX_ITERATIONS)
        if me:
            return f"{me}\n\n---\n\n{base}"
        return base

    async def extract_curiosity(self, exploration_result: str) -> str | None:
        """Ask the LLM what was most curious/interesting in the exploration."""
        try:
            resp = await self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"次の探索レポートを読んで、最も気になった・不思議だった・"
                            f"もっと詳しく見たいと思ったことを1文で教えて。"
                            f"なければ「なし」と答えて。\n\n{exploration_result}"
                        ),
                    }
                ],
            )
            text = resp.content[0].text.strip() if resp.content else ""
            if text and text != "なし":
                return text
        except Exception as e:
            logger.warning("Curiosity extraction failed: %s", e)
        return None

    async def run(
        self,
        user_input: str,
        on_action: Callable[[str, dict], None] | None = None,
        desires=None,
    ) -> str:
        """Run one conversation turn with the agent loop.

        Args:
            user_input: The user's instruction.
            on_action: Optional callback called when the agent uses a tool.
                       Signature: on_action(tool_name, tool_input)
            desires: Optional DesireSystem to update curiosity target after run.
        """
        # Inject relevant past memories into context
        memories = await self._memory.recall_async(user_input, n=3)
        if memories:
            memory_ctx = self._memory.format_for_context(memories)
            user_input_with_ctx = f"{user_input}\n\n{memory_ctx}"
        else:
            user_input_with_ctx = user_input

        self.messages.append({"role": "user", "content": user_input_with_ctx})

        for i in range(MAX_ITERATIONS):
            logger.debug("Agent iteration %d", i + 1)

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.config.max_tokens,
                system=self._system_prompt(),
                tools=self._all_tool_defs,
                messages=self.messages,
            )

            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                texts = [b.text for b in response.content if hasattr(b, "text")]
                final_text = "\n".join(texts) if texts else "(no response)"

                camera_used = any(
                    isinstance(b, dict)
                    and b.get("type") == "tool_use"
                    and b.get("name") == "camera_capture"
                    for msg in self.messages
                    for b in (msg.get("content") if isinstance(msg.get("content"), list) else [])
                )
                if final_text and final_text != "(no response)":
                    await self._memory.save_async(final_text[:500], direction="観察")

                # Extract curiosity target only when camera was actually used
                if desires is not None and final_text and camera_used:
                    curiosity = await self.extract_curiosity(final_text)
                    if curiosity:
                        desires.curiosity_target = curiosity
                        desires.boost("look_around", 0.3)
                        logger.info("Curiosity target: %s", curiosity)

                return final_text

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        logger.info("Tool call: %s(%s)", block.name, block.input)
                        if on_action:
                            on_action(block.name, block.input)
                        text, image = await self._execute_tool(block.name, block.input)
                        logger.info("Tool result: %s", text[:100])
                        tool_results.append(_make_tool_result(block.id, text, image))

                self.messages.append({"role": "user", "content": tool_results})
                continue

            logger.warning("Unexpected stop_reason: %s", response.stop_reason)
            break

        logger.warning("Reached max iterations (%d). Forcing final response.", MAX_ITERATIONS)
        self.messages.append(
            {
                "role": "user",
                "content": "Please summarize what you found and provide your final answer now.",
            }
        )
        final = await self.client.messages.create(
            model=self.model,
            max_tokens=self.config.max_tokens,
            system=self._system_prompt(),
            tools=[],
            messages=self.messages,
        )
        texts = [b.text for b in final.content if hasattr(b, "text")]
        return "\n".join(texts) if texts else "(max iterations reached)"

    def clear_history(self) -> None:
        """Clear conversation history (start fresh)."""
        self.messages = []
