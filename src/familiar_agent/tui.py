"""Textual TUI for familiar-ai."""

from __future__ import annotations

import asyncio
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from collections.abc import Callable
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Input, RichLog, Static
from textual_autocomplete import AutoComplete, DropdownItem, TargetState

from ._i18n import _make_banner, _t

if TYPE_CHECKING:
    from .agent import EmbodiedAgent
    from .desires import DesireSystem

logger = logging.getLogger(__name__)

IDLE_CHECK_INTERVAL = 10.0
DESIRE_COOLDOWN = 90.0

_RICH_TAG_RE = re.compile(r"\[/?[^\[\]]*\]")

CSS = """
#log {
    height: 1fr;
    border: none;
    padding: 0 1;
    scrollbar-size: 1 1;
}

#stream {
    height: auto;
    min-height: 1;
    padding: 0 1;
    color: $text;
}

#stream.thinking {
    color: $text-muted;
}

#stream.recording {
    color: $error;
}

#input-bar {
    dock: bottom;
    height: 3;
    border-top: solid $primary-darken-2;
    padding: 0 1;
}
"""

_SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

# CC-style interrupt message constants
INTERRUPT_MSG = "[Request interrupted by user]"
INTERRUPT_TOOL_MSG = "[Request interrupted by user for tool use]"


def _format_elapsed(seconds: float) -> str:
    """Human-readable elapsed time: '45s' or '7m 43s'."""
    total = int(seconds)
    if total < 60:
        return f"{total}s"
    m, s = divmod(total, 60)
    return f"{m}m {s:02d}s"


def _format_tokens(n: int) -> str:
    """Compact token count: '' for zero, '500' under 1k, '6.5k' above."""
    if n == 0:
        return ""
    if n < 1000:
        return str(n)
    return f"{n / 1000:.1f}k"


# Slash commands shown in the autocomplete dropdown
_SLASH_COMMANDS: list[tuple[str, str]] = [
    ("/btw", "💬  Quick one-shot question (no memory / tools)"),
    ("/transcribe", "🎙  Start / stop voice input (STT)"),
    ("/cost", "💰  Show token usage and cost for this session"),
    ("/clear", "🗑   Clear conversation history"),
    ("/quit", "✕   Quit"),
]


def _parse_btw(text: str) -> str:
    """Extract the question from '/btw <question>'."""
    after = text[len("/btw") :].strip()
    return after


async def handle_btw_command(question: str, backend) -> str:
    """Run a single lightweight LLM completion — no tools, no memory.

    Like CC's /btw: a quick side-question that doesn't pollute conversation history.
    """
    question = question.strip()
    if not question:
        return ""
    return await backend.complete(question, max_tokens=300)


def _format_cost(
    input_tokens: int,
    output_tokens: int,
    *,
    input_price_per_m: float = 3.0,
    output_price_per_m: float = 15.0,
) -> str:
    """Format token usage and estimated USD cost for display.

    Default prices match Sonnet 4.6 ($/1M tokens).
    """
    input_cost = input_tokens / 1_000_000 * input_price_per_m
    output_cost = output_tokens / 1_000_000 * output_price_per_m
    total = input_cost + output_cost
    return (
        f"📊 Tokens — in: {input_tokens:,}  out: {output_tokens:,}\n"
        f"💰 Cost   — ${total:.4f} (in ${input_cost:.4f} + out ${output_cost:.4f})"
    )


def _slash_candidates(state: TargetState) -> list[DropdownItem]:
    """Return matching commands only when input starts with '/'.

    Uses text up to cursor position so that the library's search_string and
    our own prefix-filter stay in sync.  Each item's .value is the bare
    command string so that selecting from the dropdown inserts only the
    command, not the description.
    """
    text = state.text[: state.cursor_position]
    if not text.startswith("/"):
        return []
    return [DropdownItem(main=cmd) for cmd, _desc in _SLASH_COMMANDS if cmd.startswith(text)]


ACTION_ICONS = {
    "see": "👀",
    "look_left": "◀️",
    "look_right": "▶️",
    "look_up": "🔼",
    "look_down": "🔽",
    "look_around": "🔄",
    "walk": "🚶",
    "say": "🗣️",
    "remember": "💾",
}

# Tool names that have dedicated i18n labels (key: "action_{name}")
_I18N_ACTION_NAMES = {"see", "look", "walk", "say", "remember"}


def _format_action(name: str, tool_input: dict) -> str:
    icon = ACTION_ICONS.get(name, "⚙")
    if name in ("look_left", "look_right", "look_up", "look_down"):
        deg = tool_input.get("degrees", "")
        return f"{icon} {name}({deg}°)"
    if name == "say":
        text = tool_input.get("text", "")[:50]
        return f"{icon} 「{text}…」"
    if name == "walk":
        return f"{icon} {tool_input.get('direction', '')} {tool_input.get('duration', '')}s"
    if name in _I18N_ACTION_NAMES:
        return _t(f"action_{name}")
    return f"{icon} {name}"


class FamiliarApp(App):
    CSS = CSS
    BINDINGS = [
        Binding("ctrl+c", "quit", _t("quit_label"), show=True),
        Binding("ctrl+l", "clear_history", _t("clear_label"), show=True),
        Binding("ctrl+t", "toggle_listen", "🎙 Voice", show=True),
        Binding("escape", "cancel_turn", "🛑 Cancel", show=False),
        Binding("space", "start_ptt", "🎙 PTT", show=False),
    ]

    def __init__(self, agent: "EmbodiedAgent", desires: "DesireSystem") -> None:
        super().__init__()
        self.agent = agent
        self.desires = desires
        self._agent_name = agent.config.agent_name
        self._companion_name = agent.config.companion_name
        self._input_queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._last_interaction = time.time()
        self._agent_running = False
        self._current_text_buf = ""  # buffer for streaming text
        self._log_path = self._open_log_file()
        self._recording = False
        self._stop_recording: asyncio.Event = asyncio.Event()
        self._last_toggle_listen: float = 0.0  # debounce Ctrl+T key-repeat
        # ESC cancel support
        self._cancel_event: asyncio.Event = asyncio.Event()
        self._agent_task: asyncio.Task | None = None
        # Push-to-Talk state
        self._ptt_active: bool = False

    def _open_log_file(self) -> Path:
        log_dir = Path.home() / ".cache" / "familiar-ai"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "chat.log"
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"\n{'─' * 60}\n[{datetime.now():%Y-%m-%d %H:%M:%S}] セッション開始\n")
        return log_path

    def _append_log(self, line: str) -> None:
        plain = _RICH_TAG_RE.sub("", line)
        with self._log_path.open("a", encoding="utf-8") as f:
            f.write(plain + "\n")

    def compose(self) -> ComposeResult:
        yield RichLog(id="log", highlight=False, markup=True, wrap=True)
        yield Static("", id="stream")
        input_bar = Input(
            placeholder=_t("input_placeholder"),
            id="input-bar",
        )
        yield input_bar
        yield AutoComplete(input_bar, candidates=_slash_candidates)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#input-bar", Input).focus()
        # Show startup banner
        log = self.query_one("#log", RichLog)
        for line in _make_banner(include_commands=False).splitlines():
            log.write(f"[bold]{line}[/bold]" if "familiar-ai" in line else f"[dim]{line}[/dim]")
        self._log_system(_t("startup", log_path=str(self._log_path)))
        self.set_interval(IDLE_CHECK_INTERVAL, self._desire_tick)
        self.run_worker(self._process_queue(), exclusive=False)

    # ── logging helpers ────────────────────────────────────────────

    def _write_log(self, text: str, style: str = "") -> None:
        log = self.query_one("#log", RichLog)
        if style:
            log.write(f"[{style}]{text}[/{style}]")
        else:
            log.write(text)
        self._append_log(text)

    def _log_system(self, text: str) -> None:
        self._write_log(f"[dim]{text}[/dim]")

    def _log_user(self, text: str) -> None:
        self._write_log(f"[bold cyan]{self._companion_name} ▶[/bold cyan] {text}")

    def _log_action(self, name: str, tool_input: dict) -> None:
        label = _format_action(name, tool_input)
        self._write_log(f"[dim]{label}[/dim]")

    # ── input handling ─────────────────────────────────────────────

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        event.input.clear()
        if not text:
            return

        if text == "/quit":
            self.exit()
            return
        if text == "/clear":
            self.agent.clear_history()
            self._log_system(_t("history_cleared"))
            return
        if text == "/transcribe":
            await self.action_toggle_listen()
            return
        if text == "/cost":
            in_tok = getattr(self.agent, "_session_input_tokens", 0)
            out_tok = getattr(self.agent, "_session_output_tokens", 0)
            self._log_system(_format_cost(in_tok, out_tok))
            return
        if text.startswith("/btw"):
            question = _parse_btw(text)
            if not question:
                self._log_system("Usage: /btw <question>")
                return
            answer = await handle_btw_command(question, self.agent.backend)
            name_tag = f"[bold magenta]{self._agent_name} ▶[/bold magenta]"
            self._write_log(f"{name_tag} {answer}")
            return

        self._log_user(text)
        self._last_interaction = time.time()
        await self._input_queue.put(text)

    # ── agent loop ─────────────────────────────────────────────────

    async def _process_queue(self) -> None:
        """Main loop: dequeue user messages and run agent."""
        while True:
            text = await self._input_queue.get()
            if text is None:
                break
            await self._run_agent(text)

    async def _spinner_loop(
        self,
        stream: Static,
        name_tag: str,
        stop: asyncio.Event,
        start_time: float,
        get_tokens: Callable[[], int] | None = None,
    ) -> None:
        """Animate the stream widget with a live status line.

        Shows:  ⠋ 23s · ↓ 6.5k
        The token count reflects _last_context_tokens, updated after each
        stream_turn() call in the agent loop.
        """
        stream.add_class("thinking")
        for i in range(10_000):
            if stop.is_set():
                break
            frame = _SPINNER_FRAMES[i % len(_SPINNER_FRAMES)]
            elapsed_str = _format_elapsed(time.time() - start_time)
            tokens = get_tokens() if get_tokens else 0
            tok_str = f" · ↓ {_format_tokens(tokens)}" if tokens else ""
            stream.update(f"{name_tag} {frame} [dim]{elapsed_str}{tok_str}[/dim]")
            await asyncio.sleep(0.08)
        stream.remove_class("thinking")

    async def _run_agent(self, user_input: str, inner_voice: str = "") -> None:
        self._agent_running = True
        self._cancel_event.clear()
        self._current_text_buf = ""
        start_time = time.time()

        log = self.query_one("#log", RichLog)
        stream = self.query_one("#stream", Static)
        text_buf: list[str] = []
        action_counts: dict[str, int] = {}

        name_tag = f"[bold magenta]{self._agent_name} ▶[/bold magenta]"

        # Spinner state — restarted after each tool call
        get_tokens = lambda: self.agent._last_context_tokens  # noqa: E731
        stop_spinner = asyncio.Event()
        spinner_task: asyncio.Task = asyncio.create_task(
            self._spinner_loop(stream, name_tag, stop_spinner, start_time, get_tokens)
        )

        def _stop_spinner() -> None:
            stop_spinner.set()

        def _restart_spinner() -> None:
            nonlocal spinner_task, stop_spinner
            stop_spinner.set()
            stop_spinner = asyncio.Event()
            spinner_task = asyncio.create_task(
                self._spinner_loop(stream, name_tag, stop_spinner, start_time, get_tokens)
            )

        def _flush_stream() -> None:
            """Commit streamed text to the log and clear the stream widget."""
            if text_buf:
                content = "".join(text_buf)
                log.write(f"{name_tag} {content}")
                self._append_log(f"{self._agent_name} ▶ {content}")
                text_buf.clear()
                stream.update("")

        def _log_turn_summary() -> None:
            elapsed = time.time() - start_time
            parts = [f"[dim]{elapsed:.1f}s[/dim]"]
            for tool_name, icon in ACTION_ICONS.items():
                count = action_counts.get(tool_name, 0)
                if count:
                    parts.append(f"[dim]{icon} ×{count}[/dim]")
            summary = "  [dim]──[/dim] " + "  ".join(parts) + "  [dim]" + "─" * 20 + "[/dim]"
            log.write(summary)
            self._append_log(f"── {elapsed:.1f}s ──")

        def on_action(name: str, tool_input: dict) -> None:
            action_counts[name] = action_counts.get(name, 0) + 1
            _stop_spinner()
            _flush_stream()
            label = _format_action(name, tool_input)
            log.write(f"[dim]{label}[/dim]")
            # Restart spinner while waiting for the next LLM response
            _restart_spinner()

        def on_text(chunk: str) -> None:
            _stop_spinner()
            text_buf.append(chunk)
            stream.update(f"{name_tag} {''.join(text_buf)}")

        async def _cancel_watcher() -> None:
            await self._cancel_event.wait()
            if self._agent_task and not self._agent_task.done():
                self._agent_task.cancel()

        watcher = asyncio.create_task(_cancel_watcher())
        try:
            self._agent_task = asyncio.create_task(
                self.agent.run(
                    user_input,
                    on_action=on_action,
                    on_text=on_text,
                    desires=self.desires,
                    inner_voice=inner_voice,
                    interrupt_queue=self._input_queue,
                )
            )
            await self._agent_task
            _flush_stream()
            _log_turn_summary()
        except asyncio.CancelledError:
            _flush_stream()
            self._write_log(f"[dim]{INTERRUPT_TOOL_MSG}[/dim]")
        except Exception as e:
            self._write_log(f"[red]エラー: {e}[/red]")
        finally:
            watcher.cancel()
            self._agent_task = None
            _stop_spinner()
            stream.update("")
            self._agent_running = False

    async def _desire_tick(self) -> None:
        """Check desires and fire autonomous actions when idle."""
        if self._agent_running:
            return
        if not self._input_queue.empty():
            return
        if time.time() - self._last_interaction < DESIRE_COOLDOWN:
            return

        prompt = self.desires.dominant_as_prompt()
        if not prompt:
            return

        dominant = self.desires.get_dominant()
        if dominant is None:
            return
        desire_name, _ = dominant
        murmur = {
            "look_around": _t("desire_look_around"),
            "explore": _t("desire_explore"),
            "greet_companion": _t("desire_greet_companion"),
            "rest": _t("desire_rest"),
        }.get(desire_name, _t("desire_default"))

        self._log_system(murmur)

        # Check for pending user note
        pending: str | None = None
        if not self._input_queue.empty():
            item = self._input_queue.get_nowait()
            if item:
                pending = item
                prompt = f"（{pending}と言ってた）{prompt}"

        self._last_interaction = (
            time.time()
        )  # reset cooldown so desire doesn't fire again immediately
        await self._run_agent("", inner_voice=prompt)
        self.desires.satisfy(desire_name)
        self.desires.curiosity_target = None

    async def action_toggle_listen(self) -> None:
        """Toggle microphone recording for voice input."""
        if not self.agent.stt:
            self._log_system("STT not configured (set ELEVENLABS_API_KEY)")
            return
        # Debounce: ignore key-repeat events within 0.5 s of the last toggle
        now = time.time()
        if now - self._last_toggle_listen < 0.5:
            return
        self._last_toggle_listen = now

        stream = self.query_one("#stream", Static)

        if not self._recording:
            self._recording = True
            self._stop_recording.clear()
            stream.add_class("recording")
            stream.update("🎙 Recording… (Ctrl+T to stop)")
            self.run_worker(self._do_record(), exclusive=False)
        else:
            self._stop_recording.set()

    async def _do_record(self) -> None:
        """Worker: record until stop_event, transcribe, then submit as user input."""
        stream = self.query_one("#stream", Static)
        try:
            # Kick off recording as a background task so we can update the UI mid-way
            record_task = asyncio.create_task(
                self.agent.stt.record_and_transcribe(self._stop_recording)  # type: ignore[union-attr]
            )
            # Wait until the user presses Ctrl+M again (stop_event is set)
            await self._stop_recording.wait()
            # Recording has stopped — now transcribing
            stream.remove_class("recording")
            stream.update("🔄 Transcribing…")
            text = await record_task
            if text.strip():
                self._log_user(text)
                self._last_interaction = time.time()
                await self._input_queue.put(text)
        except Exception as e:
            self._log_system(f"STT error: {e}")
        finally:
            self._recording = False
            stream.remove_class("recording")
            stream.update("")

    def action_clear_history(self) -> None:
        self.agent.clear_history()
        self._log_system(_t("history_cleared"))

    def action_cancel_turn(self) -> None:
        """ESC — cancel the running agent turn."""
        if not self._agent_running:
            return
        self._cancel_event.set()
        # Directly cancel the task on every ESC press — the watcher only fires once,
        # so repeated ESC presses must hit the task directly.
        if self._agent_task and not self._agent_task.done():
            self._agent_task.cancel()
        self._log_system(f"[dim]{INTERRUPT_MSG}[/dim]")

    def action_start_ptt(self) -> None:
        """Space — start Push-to-Talk recording (if STT configured)."""
        if not self.agent.stt:
            return
        if self._recording or self._ptt_active:
            return
        self._ptt_active = True
        self._recording = True
        self._stop_recording.clear()
        stream = self.query_one("#stream", Static)
        stream.add_class("recording")
        stream.update("🎙 PTT… (release Space to send)")
        self.run_worker(self._do_record(), exclusive=False)

    def action_stop_ptt(self) -> None:
        """Space released — stop Push-to-Talk recording."""
        if not self._ptt_active:
            return
        self._ptt_active = False
        self._stop_recording.set()

    async def action_quit(self) -> None:
        await self.agent.close()
        self.exit()
