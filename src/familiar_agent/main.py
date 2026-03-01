"""CLI REPL for familiar-ai."""

from __future__ import annotations

import asyncio
import logging
import sys
import time
from pathlib import Path

from .agent import EmbodiedAgent
from .config import AgentConfig
from .desires import DesireSystem
from ._i18n import BANNER, _t

IDLE_CHECK_INTERVAL = 10.0  # seconds between desire checks when idle
DESIRE_COOLDOWN = 90.0  # seconds after last user interaction before desires can fire


def setup_logging(debug: bool = False) -> None:
    """Setup basic logging to a file ONLY (to keep the screen clean)."""
    log_dir = Path.home() / ".cache" / "familiar-ai"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    level = logging.DEBUG if debug else logging.INFO

    # Root logger configuration - FileHandler only
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
    )
    # Reduce noise from 3rd party libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("google.genai").setLevel(logging.WARNING)

    logging.info("Logging initialized. Level: %s, File: %s", logging.getLevelName(level), log_file)


def _format_action(name: str, tool_input: dict) -> str:
    """Format a tool call for display."""
    if name == "look":
        direction = tool_input.get("direction", "")
        key = {
            "left": "look_left",
            "right": "look_right",
            "up": "look_up",
            "down": "look_down",
        }.get(direction, "look_around")
        return f"↩️  {_t(key)}..."
    if name == "walk":
        direction = tool_input.get("direction", "?")
        duration = tool_input.get("duration")
        if duration:
            return f"🚶 {_t('walk_timed', direction=direction, duration=str(duration))}"
        return f"🚶 {_t('walk_dir', direction=direction)}"
    if name == "say":
        text = tool_input.get("text", "")[:40]
        return f"💬 「{text}...」"
    action_key = f"action_{name}"
    try:
        return _t(action_key)
    except KeyError:
        return f"⚙  {name}..."


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
            queued_input: str | None
            try:
                queued_input = await asyncio.wait_for(
                    input_queue.get(), timeout=IDLE_CHECK_INTERVAL
                )
            except asyncio.TimeoutError:
                queued_input = None

            if queued_input is None and input_queue.empty():
                # Genuine idle — check desires, but respect cooldown after conversation
                if time.time() - last_interaction_time < DESIRE_COOLDOWN:
                    continue  # Still in post-conversation cooldown

                prompt = desires.dominant_as_prompt()
                if prompt:
                    dominant = desires.get_dominant()
                    if dominant is None:
                        continue
                    desire_name, _ = dominant
                    murmur = {
                        "look_around": _t("desire_look_around"),
                        "explore": _t("desire_explore"),
                        "greet_companion": _t("desire_greet_companion"),
                        "rest": _t("desire_rest"),
                    }.get(desire_name, _t("desire_default"))
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

            if queued_input:
                await _handle_user(
                    queued_input, agent, desires, on_action, on_text, debug, input_queue
                )

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        stdin_task.cancel()
        await agent.close()
        print(f"\n{_t('repl_goodbye')}")


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
        print(_t("repl_history_cleared"))
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


def _mcp_command(args: list[str]) -> None:
    """Handle 'familiar mcp <subcommand>' — manage ~/.familiar-ai.json."""
    import argparse
    import json

    from .mcp_client import _resolve_config_path

    parser = argparse.ArgumentParser(prog="familiar mcp", add_help=True)
    sub = parser.add_subparsers(dest="action", required=True)

    p_add = sub.add_parser("add", help="Add an MCP server")
    p_add.add_argument("name", help="Name for the server (e.g. filesystem)")
    p_add.add_argument("command", help="Command to launch the server (e.g. npx)")
    p_add.add_argument("server_args", nargs="*", metavar="ARG")
    p_add.add_argument(
        "-e",
        "--env",
        action="append",
        metavar="KEY=VALUE",
        default=[],
        help="Set environment variable (repeatable)",
    )

    p_rm = sub.add_parser("remove", help="Remove an MCP server")
    p_rm.add_argument("name")

    sub.add_parser("list", help="List configured MCP servers")

    parsed = parser.parse_args(args)
    cfg_path = _resolve_config_path()

    data: dict = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    servers: dict = data.setdefault("mcpServers", {})

    if parsed.action == "add":
        env: dict[str, str] = {}
        for kv in parsed.env:
            k, _, v = kv.partition("=")
            if k:
                env[k] = v
        entry: dict = {"type": "stdio", "command": parsed.command, "args": parsed.server_args}
        if env:
            entry["env"] = env
        servers[parsed.name] = entry
        cfg_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"Added MCP server '{parsed.name}' → {cfg_path}")

    elif parsed.action == "remove":
        if parsed.name not in servers:
            print(f"MCP server '{parsed.name}' not found in {cfg_path}")
            sys.exit(1)
        del servers[parsed.name]
        cfg_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"Removed MCP server '{parsed.name}'")

    elif parsed.action == "list":
        if not servers:
            print(f"No MCP servers configured.  Config: {cfg_path}")
            return
        print(f"MCP servers  ({cfg_path})\n")
        for name, cfg in servers.items():
            cmd = cfg.get("command", "")
            a = " ".join(str(x) for x in cfg.get("args", []))
            env_keys = list((cfg.get("env") or {}).keys())
            env_hint = f"  env:{','.join(env_keys)}" if env_keys else ""
            print(f"  {name:<22} {cmd} {a}{env_hint}")


def main() -> None:
    # Use uvloop for faster I/O throughput when available (Linux / WSL2)
    try:
        import uvloop

        uvloop.install()
    except ImportError:
        pass

    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        _mcp_command(sys.argv[2:])
        return

    debug = "--debug" in sys.argv
    use_tui = "--no-tui" not in sys.argv

    setup_logging(debug=debug)

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
        app.run(mouse=False)
    else:
        asyncio.run(repl(agent, desires, debug=debug))


if __name__ == "__main__":
    main()
