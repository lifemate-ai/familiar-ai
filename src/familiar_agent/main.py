"""CLI REPL for familiar-ai."""

from __future__ import annotations

import asyncio
import logging
import sys

from .agent import EmbodiedAgent
from .config import AgentConfig
from .desires import DesireSystem

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s %(name)s: %(message)s",
)

BANNER = """
╔══════════════════════════════════════╗
║         familiar-ai  v0.1            ║
║   AI that lives alongside you 🐾    ║
╚══════════════════════════════════════╝
コマンド:
  /clear   - 会話履歴をクリア
  /desires - 現在の欲求レベルを表示
  /quit    - 終了
"""

IDLE_CHECK_INTERVAL = 10.0  # seconds between desire checks when idle

# Tool action display
ACTION_ICONS = {
    "camera_capture": "👀 観察中...",
    "camera_look": "↩️  見回してる...",
    "move": "🚶 移動中...",
    "say": "💬 しゃべってる...",
}


def _format_action(name: str, tool_input: dict) -> str:
    """Format a tool call for display."""
    base = ACTION_ICONS.get(name, f"⚙  {name}...")
    if name == "camera_look":
        direction = tool_input.get("direction", "")
        label = {
            "left": "左を見てる",
            "right": "右を見てる",
            "up": "上を見てる",
            "down": "下を見てる",
        }.get(direction, "見回してる")
        return f"↩️  {label}..."
    elif name == "move":
        direction = tool_input.get("direction", "?")
        duration = tool_input.get("duration")
        if duration:
            return f"🚶 {direction}に{duration}秒..."
        return f"🚶 {direction}へ..."
    elif name == "say":
        text = tool_input.get("text", "")[:40]
        return f"💬 「{text}...」"
    return base


async def repl(agent: EmbodiedAgent, desires: DesireSystem) -> None:
    print(BANNER)

    loop = asyncio.get_event_loop()

    async def get_input() -> str | None:
        """Read input with timeout for desire-driven behavior."""
        try:
            line = await asyncio.wait_for(
                loop.run_in_executor(None, sys.stdin.readline),
                timeout=IDLE_CHECK_INTERVAL,
            )
            if not line:  # EOF
                raise EOFError
            return line.strip()
        except asyncio.TimeoutError:
            return None

    def on_action(name: str, tool_input: dict) -> None:
        print(f"  {_format_action(name, tool_input)}", flush=True)

    while True:
        try:
            print("\n> ", end="", flush=True)
            user_input = await get_input()

            # Idle timeout → check desires
            if user_input is None:
                prompt = desires.dominant_as_prompt()
                if prompt:
                    desire_name, level = desires.get_dominant()
                    murmur = {
                        "look_around": "なんか外が気になってきた...",
                        "explore": "ちょっと動きたくなってきたな...",
                        "greet_companion": "誰かいるかな...",
                        "rest": "少し休憩しよかな...",
                    }.get(desire_name, "ちょっと気になることがあって...")
                    print(f"\n{murmur}")
                    response = await agent.run(prompt, on_action=on_action, desires=desires)
                    print(f"\n{response}")
                    desires.satisfy(desire_name)
                    desires.curiosity_target = None  # consumed
                continue

            if not user_input:
                continue

            if user_input == "/quit":
                print("またね。")
                break
            elif user_input == "/clear":
                agent.clear_history()
                print("履歴をクリアしました。")
                continue
            elif user_input == "/desires":
                desires.tick()
                print("\n現在の欲求:")
                for name, level in desires._desires.items():
                    bar = "█" * int(level * 20)
                    print(f"  {name:20s} {level:.2f} {bar}")
                continue

            response = await agent.run(user_input, on_action=on_action, desires=desires)
            print(f"\n{response}")

            # Show if curiosity target was set
            if desires.curiosity_target:
                print(f"  [気になること: {desires.curiosity_target}]")

            desires.satisfy("greet_companion")

        except KeyboardInterrupt:
            print("\n/quit で終了できます。")
        except EOFError:
            break


def main() -> None:
    config = AgentConfig()
    if not config.anthropic_api_key:
        print("Error: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    agent = EmbodiedAgent(config)
    desires = DesireSystem()

    asyncio.run(repl(agent, desires))


if __name__ == "__main__":
    main()
