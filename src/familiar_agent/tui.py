"""Textual TUI for familiar-ai."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.suggester import SuggestFromList
from textual.widgets import Footer, Input, RichLog, Static

if TYPE_CHECKING:
    from .agent import EmbodiedAgent
    from .desires import DesireSystem

logger = logging.getLogger(__name__)

IDLE_CHECK_INTERVAL = 10.0
DESIRE_COOLDOWN = 90.0

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

#input-bar {
    dock: bottom;
    height: 3;
    border-top: solid $primary-darken-2;
    padding: 0 1;
}
"""

ACTION_ICONS = {
    "see": "👀",
    "look_left": "◀️",
    "look_right": "▶️",
    "look_up": "🔼",
    "look_down": "🔽",
    "look_around": "🔄",
    "walk": "🚶",
    "say": "💬",
}


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
    return f"{icon} {name}"


class FamiliarApp(App):
    CSS = CSS
    BINDINGS = [
        Binding("ctrl+c", "quit", "終了", show=True),
        Binding("ctrl+l", "clear_history", "履歴クリア", show=True),
    ]

    def __init__(self, agent: "EmbodiedAgent", desires: "DesireSystem") -> None:
        super().__init__()
        self.agent = agent
        self.desires = desires
        self._agent_name = agent.config.agent_name
        self._input_queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._last_interaction = time.time()
        self._agent_running = False
        self._current_text_buf = ""  # buffer for streaming text

    def compose(self) -> ComposeResult:
        yield RichLog(id="log", highlight=False, markup=True, wrap=True)
        yield Static("", id="stream")
        yield Input(
            placeholder="コウタ > ",
            id="input-bar",
            suggester=SuggestFromList(["/quit", "/clear"], case_sensitive=False),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#input-bar", Input).focus()
        self._log_system("familiar-ai 起動。/quit で終了、Ctrl+L で履歴クリア。")
        self.set_interval(IDLE_CHECK_INTERVAL, self._desire_tick)
        self.run_worker(self._process_queue(), exclusive=False)

    # ── logging helpers ────────────────────────────────────────────

    def _log(self, text: str, style: str = "") -> None:
        log = self.query_one("#log", RichLog)
        if style:
            log.write(f"[{style}]{text}[/{style}]")
        else:
            log.write(text)

    def _log_system(self, text: str) -> None:
        self._log(f"[dim]{text}[/dim]")

    def _log_user(self, text: str) -> None:
        self._log(f"[bold cyan]コウタ ▶[/bold cyan] {text}")

    def _log_action(self, name: str, tool_input: dict) -> None:
        label = _format_action(name, tool_input)
        self._log(f"[dim]{label}[/dim]")

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
            self._log_system("── 履歴クリア ──")
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

    async def _run_agent(self, user_input: str, inner_voice: str = "") -> None:
        self._agent_running = True
        self._current_text_buf = ""

        log = self.query_one("#log", RichLog)
        stream = self.query_one("#stream", Static)
        text_buf: list[str] = []

        name_tag = f"[bold magenta]{self._agent_name} ▶[/bold magenta]"

        def _flush_stream() -> None:
            """Commit streamed text to the log and clear the stream widget."""
            if text_buf:
                log.write(f"{name_tag} {''.join(text_buf)}")
                text_buf.clear()
                stream.update("")

        def on_action(name: str, tool_input: dict) -> None:
            _flush_stream()
            label = _format_action(name, tool_input)
            log.write(f"[dim]{label}[/dim]")

        def on_text(chunk: str) -> None:
            text_buf.append(chunk)
            stream.update(f"{name_tag} {''.join(text_buf)}")

        try:
            await self.agent.run(
                user_input,
                on_action=on_action,
                on_text=on_text,
                desires=self.desires,
                inner_voice=inner_voice,
                interrupt_queue=self._input_queue,
            )
            _flush_stream()
        except Exception as e:
            self._log(f"[red]エラー: {e}[/red]")
        finally:
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

        desire_name, _ = self.desires.get_dominant()
        murmur = {
            "look_around": "なんか外が気になってきた…",
            "explore": "ちょっと動きたくなってきたな…",
            "greet_companion": "誰かいるかな…",
            "rest": "少し休憩しよかな…",
        }.get(desire_name, "ちょっと気になることがあって…")

        self._log_system(murmur)

        # Check for pending user note
        pending: str | None = None
        if not self._input_queue.empty():
            item = self._input_queue.get_nowait()
            if item:
                pending = item
                prompt = f"（{pending}と言ってた）{prompt}"

        await self._run_agent("", inner_voice=prompt)
        self.desires.satisfy(desire_name)
        self.desires.curiosity_target = None

    def action_clear_history(self) -> None:
        self.agent.clear_history()
        self._log_system("── 履歴クリア ──")

    def action_quit(self) -> None:
        self.exit()
