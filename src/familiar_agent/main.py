"""CLI REPL for familiar-ai."""

from __future__ import annotations

import asyncio
import logging
import sys
import time

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
  /clear - 会話履歴をクリア
  /quit  - 終了
"""

IDLE_CHECK_INTERVAL = 10.0  # seconds between desire checks when idle
DESIRE_COOLDOWN = 90.0  # seconds after last user interaction before desires can fire

ACTION_ICONS = {
    "see": "👀 見てる...",
    "look": "↩️  向いてる...",
    "walk": "🚶 歩いてる...",
    "say": "💬 しゃべってる...",
}


def _format_action(name: str, tool_input: dict) -> str:
    """Format a tool call for display."""
    base = ACTION_ICONS.get(name, f"⚙  {name}...")
    if name == "look":
        direction = tool_input.get("direction", "")
        label = {
            "left": "左を向いた",
            "right": "右を向いた",
            "up": "上を向いた",
            "down": "下を向いた",
        }.get(direction, "見回してる")
        return f"↩️  {label}..."
    elif name == "walk":
        direction = tool_input.get("direction", "?")
        duration = tool_input.get("duration")
        if duration:
            return f"🚶 {direction}に{duration}秒..."
        return f"🚶 {direction}へ..."
    elif name == "say":
        text = tool_input.get("text", "")[:40]
        return f"💬 「{text}...」"
    return base


async def repl(agent: EmbodiedAgent, desires: DesireSystem, debug: bool = False) -> None:
    print(BANNER)

    loop = asyncio.get_event_loop()

    # Persistent input queue — stdin reader runs as a background task
    # so user input is captured even while the agent is busy.
    input_queue: asyncio.Queue[str | None] = asyncio.Queue()
    last_interaction_time: float = time.time()

    async def _stdin_reader() -> None:
        """Read stdin continuously into the queue."""
        while True:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:  # EOF
                await input_queue.put(None)
                return
            await input_queue.put(line.strip())

    stdin_task = asyncio.create_task(_stdin_reader())

    def on_action(name: str, tool_input: dict) -> None:
        print(f"  {_format_action(name, tool_input)}", flush=True)

    def on_text(chunk: str) -> None:
        print(chunk, end="", flush=True)

    try:
        while True:
            # Drain any pending user input first (user spoke while agent was busy)
            pending: list[str] = []
            while not input_queue.empty():
                item = input_queue.get_nowait()
                if item is None:
                    raise EOFError
                if item:
                    pending.append(item)

            if pending:
                # Process all buffered user messages before doing anything autonomous
                for user_input in pending:
                    last_interaction_time = time.time()
                    await _handle_user(
                        user_input, agent, desires, on_action, on_text, debug, input_queue
                    )
                continue

            # No pending input — show prompt and wait briefly
            print("\n> ", end="", flush=True)
            try:
                user_input = await asyncio.wait_for(input_queue.get(), timeout=IDLE_CHECK_INTERVAL)
            except asyncio.TimeoutError:
                user_input = None

            if user_input is None and input_queue.empty():
                # Genuine idle — check desires, but respect cooldown after conversation
                if time.time() - last_interaction_time < DESIRE_COOLDOWN:
                    continue  # Still in post-conversation cooldown

                prompt = desires.dominant_as_prompt()
                if prompt:
                    desire_name, _ = desires.get_dominant()
                    murmur = {
                        "look_around": "なんか外が気になってきた...",
                        "explore": "ちょっと動きたくなってきたな...",
                        "greet_companion": "誰かいるかな...",
                        "rest": "少し休憩しよかな...",
                    }.get(desire_name, "ちょっと気になることがあって...")
                    print(f"\n{murmur}")

                    # Check once more — user may have typed while we were deciding.
                    # If they did, weave their words INTO the desire prompt so the agent
                    # knows who they're talking to (e.g. "コウタだよ" while being watched).
                    pending_note: str | None = None
                    if not input_queue.empty():
                        item = input_queue.get_nowait()
                        if item is None:
                            break
                        if item:
                            pending_note = item

                    if pending_note:
                        # Fold the user's note into the desire prompt instead of a separate turn
                        prompt = f"（{pending_note}と言ってた）{prompt}"

                    print()
                    await agent.run(
                        "",
                        on_action=on_action,
                        on_text=on_text,
                        desires=desires,
                        inner_voice=prompt,
                        interrupt_queue=input_queue,
                    )
                    desires.satisfy(desire_name)
                    desires.curiosity_target = None

                    # Flush any input that arrived during agent.run()
                    buffered: list[str] = []
                    while not input_queue.empty():
                        item = input_queue.get_nowait()
                        if item is None:
                            raise EOFError
                        if item:
                            buffered.append(item)
                    for msg in buffered:
                        await _handle_user(
                            msg, agent, desires, on_action, on_text, debug, input_queue
                        )
                continue

            if user_input:
                await _handle_user(
                    user_input, agent, desires, on_action, on_text, debug, input_queue
                )

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        stdin_task.cancel()
        print("\nまたね。")


async def _handle_user(
    user_input: str,
    agent: EmbodiedAgent,
    desires: DesireSystem,
    on_action,
    on_text,
    debug: bool,
    interrupt_queue=None,
) -> None:
    """Process a single user message."""
    if user_input == "/quit":
        raise EOFError
    elif user_input == "/clear":
        agent.clear_history()
        print("履歴をクリアしました。")
    elif user_input == "/desires":
        if debug:
            desires.tick()
            print("\n[debug] desires:")
            for name, level in desires._desires.items():
                bar = "█" * int(level * 20)
                print(f"  {name:20s} {level:.2f} {bar}")
    else:
        print()
        await agent.run(
            user_input,
            on_action=on_action,
            on_text=on_text,
            desires=desires,
            interrupt_queue=interrupt_queue,
        )
        if desires.curiosity_target:
            print(f"\n  [気になること: {desires.curiosity_target}]")
        desires.satisfy("greet_companion")


def main() -> None:
    debug = "--debug" in sys.argv
    use_tui = "--no-tui" not in sys.argv

    config = AgentConfig()
    if not config.api_key:
        print("Error: API_KEY not set.")
        print("  Set PLATFORM=gemini|anthropic|openai and API_KEY=<your key>.")
        sys.exit(1)

    agent = EmbodiedAgent(config)
    desires = DesireSystem()

    if use_tui:
        from .tui import FamiliarApp

        app = FamiliarApp(agent, desires)
        app.run()
    else:
        asyncio.run(repl(agent, desires, debug=debug))


if __name__ == "__main__":
    main()
