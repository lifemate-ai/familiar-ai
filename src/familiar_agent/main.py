"""CLI REPL for familiar-ai."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

from .agent import EmbodiedAgent
from .config import AgentConfig
from .desires import DesireSystem
from .realtime_stt_session import create_realtime_stt_session
from ._i18n import BANNER, _t
from ._ui_helpers import (
    DESIRE_COOLDOWN,
    IDLE_CHECK_INTERVAL,
    desire_tick_prompt,
    format_action as _format_action,
)


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
    logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
    logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
    try:
        import transformers as _transformers

        _transformers.logging.set_verbosity_error()
    except ImportError:
        pass

    logging.info("Logging initialized. Level: %s, File: %s", logging.getLevelName(level), log_file)


async def repl(agent: EmbodiedAgent, desires: DesireSystem, debug: bool = False) -> None:
    print(BANNER)

    if not agent.is_embedding_ready:
        start_init = time.time()
        while not agent.is_embedding_ready:
            elapsed = int(time.time() - start_init)
            print(f"\r  {_t('initializing')}... ({elapsed}s)", end="", flush=True)
            await asyncio.sleep(0.5)
        print(f"\r  {_t('initializing_done')} ({int(time.time() - start_init)}s)          ")

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

    # ── Realtime STT (hands-free voice input) ────────────────────────
    stt_session = create_realtime_stt_session()
    if stt_session:
        try:
            stt_session.on_partial = lambda t: print(
                f"\r  \U0001f3a4 (\u805e\u304d\u53d6\u308a\u4e2d) {t}    ", end="", flush=True
            )
            stt_session.on_committed = lambda t: print(f"\n  \U0001f3a4 {t}")
            await stt_session.start(loop, input_queue)
            print("  \U0001f3a4 Realtime STT ON (ElevenLabs)")
        except Exception as e:
            logging.getLogger(__name__).warning("Realtime STT init failed: %s", e)
            print(f"  \u26a0 Realtime STT init failed: {e}")
            stt_session = None

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

                # Peek at any pending input before firing desire
                pending_items: list[str] = []
                if not input_queue.empty():
                    item = input_queue.get_nowait()
                    if item is None:
                        break
                    if item:
                        pending_items.append(item)

                tick = desire_tick_prompt(desires, pending_items)
                if tick:
                    desire_name, prompt, _pending = tick
                    try:
                        murmur = _t(f"desire_{desire_name}")
                    except KeyError:
                        murmur = _t("desire_default")
                    print(f"\n{murmur}\n")

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
                elif pending_items:
                    # Had pending input but no desire — process it as user message
                    for msg in pending_items:
                        await _handle_user(
                            msg, agent, desires, on_action, on_text, debug, input_queue
                        )
                    continue

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
        if stt_session:
            try:
                await asyncio.wait_for(stt_session.stop(), timeout=3.0)
            except (asyncio.TimeoutError, Exception):
                pass
        try:
            await asyncio.wait_for(agent.close(), timeout=5.0)
        except (asyncio.TimeoutError, Exception):
            pass
        print(f"\n{_t('repl_goodbye')}")
        # sys.stdin.readline runs in a non-daemon thread that cannot be
        # cancelled. Force exit so it doesn't prevent process termination.
        os._exit(0)


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
    # Suppress noisy HuggingFace Hub / transformers output before any imports
    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

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
    use_gui = "--gui" in sys.argv
    use_tui = "--no-tui" not in sys.argv and not use_gui

    setup_logging(debug=debug)

    config = AgentConfig()
    if not config.api_key:
        print("Error: API_KEY not set.")
        print("  Set PLATFORM=gemini|anthropic|openai and API_KEY=<your key>.")
        sys.exit(1)

    agent = EmbodiedAgent(config)
    desires = DesireSystem()

    if use_gui:
        from .gui import run_gui

        run_gui(agent, desires)
    elif use_tui:
        from .tui import FamiliarApp

        app = FamiliarApp(agent, desires)
        app.run(mouse=False)
    else:
        asyncio.run(repl(agent, desires, debug=debug))


if __name__ == "__main__":
    main()
