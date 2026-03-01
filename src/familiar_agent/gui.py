"""PySide6 GUI for familiar-ai.

Provides a native desktop window with:
- Scrollable conversation log (ActionLog)
- Live streaming text display (StreamLabel)
- Camera image viewer (CameraView)
- Desire level bars (DesirePanel)
- Text input with Send button

Launch via:
    uv run familiar --gui

or via run.bat --gui / run.sh --gui
"""

from __future__ import annotations

import asyncio
import base64
import logging
from typing import TYPE_CHECKING

import qasync
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QFont, QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ._i18n import _t
from ._ui_helpers import (
    DESIRE_COOLDOWN,
    IDLE_CHECK_INTERVAL,
    desire_tick_prompt,
    format_action,
)

if TYPE_CHECKING:
    from familiar_agent.agent import EmbodiedAgent
    from familiar_agent.desires import DesireSystem

logger = logging.getLogger(__name__)

# Desires to show in the panel (must exist in DesireSystem)
_DESIRE_NAMES: list[str] = [
    "look_around",
    "look_outside",
    "miss_companion",
    "browse_curiosity",
]

# Flush streamed text at most this often (ms)
_STREAM_FLUSH_INTERVAL_MS = 50


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------


class ActionLog(QPlainTextEdit):
    """Append-only log for completed agent turns and tool actions."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Courier New", 11))
        self.setPlaceholderText("Conversation will appear here…")

    def append_line(self, text: str) -> None:
        self.appendPlainText(text)
        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())

    def append_action(self, name: str, tool_input: dict) -> None:
        """Format a tool call and append it to the log."""
        self.append_line(format_action(name, tool_input))


class StreamLabel(QLabel):
    """Displays streaming LLM text tokens in real time."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setFont(QFont("Segoe UI", 12))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._chunks: list[str] = []

        # Flush accumulated chunks to label every _STREAM_FLUSH_INTERVAL_MS
        self._timer = QTimer(self)
        self._timer.setInterval(_STREAM_FLUSH_INTERVAL_MS)
        self._timer.timeout.connect(self._flush)
        self._timer.start()

    def append_chunk(self, chunk: str) -> None:
        """Accumulate a streamed token (called from on_text callback)."""
        self._chunks.append(chunk)

    def _flush(self) -> None:
        if self._chunks:
            self.setText(self.text() + "".join(self._chunks))
            self._chunks.clear()

    def commit_and_clear(self) -> str:
        """Flush pending chunks and return the full accumulated text, then clear."""
        self._flush()
        text = self.text()
        self.setText("")
        return text


class CameraView(QLabel):
    """Displays the latest camera image (base64-encoded JPEG/PNG)."""

    _PLACEHOLDER_SIZE = QSize(320, 240)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(self._PLACEHOLDER_SIZE)
        self.setStyleSheet("background: #111; border-radius: 4px;")
        self.setText("No camera image yet")
        self.setWordWrap(True)

    def update_image(self, b64_data: str) -> None:
        """Decode a base64 image and display it."""
        try:
            raw = base64.b64decode(b64_data)
            qimage = QImage.fromData(raw)
            if qimage.isNull():
                logger.warning("CameraView: could not decode image data")
                return
            pixmap = QPixmap.fromImage(qimage)
            scaled = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.setPixmap(scaled)
        except Exception:
            logger.exception("CameraView.update_image failed")


class DesirePanel(QWidget):
    """Shows desire levels as progress bars, refreshed every 2 seconds."""

    def __init__(self, desires: DesireSystem, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._desires = desires
        self._bars: dict[str, QProgressBar] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        title = QLabel("Desires")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        for name in _DESIRE_NAMES:
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setTextVisible(True)
            bar.setFormat(f"{name}  %p%")
            bar.setFixedHeight(20)
            self._bars[name] = bar
            layout.addWidget(bar)

        layout.addStretch()

        timer = QTimer(self)
        timer.timeout.connect(self._refresh)
        timer.start(2000)
        self._refresh()

    def _refresh(self) -> None:
        for name, bar in self._bars.items():
            try:
                level = self._desires.level(name)
                bar.setValue(int(level * 100))
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------


class FamiliarWindow(QMainWindow):
    """Main application window."""

    def __init__(self, agent: EmbodiedAgent, desires: DesireSystem) -> None:
        super().__init__()
        self._agent = agent
        self._desires = desires
        self._input_queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._agent_running = False

        self.setWindowTitle("familiar-ai")
        self.resize(900, 650)
        self._build_ui()

        # Start the agent processing loop
        asyncio.ensure_future(self._process_queue())
        # Show initializing status until embedding model is ready
        if not self._agent.is_embedding_ready:
            asyncio.ensure_future(self._show_init_status())

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # Left panel: log + stream + input
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        self._log = ActionLog()
        left_layout.addWidget(self._log, stretch=5)

        self._stream = StreamLabel()
        self._stream.setMinimumHeight(60)
        self._stream.setStyleSheet(
            "background: #1a1a2e; color: #e0e0ff; padding: 6px; border-radius: 4px;"
        )
        left_layout.addWidget(self._stream, stretch=1)

        # Input row
        input_row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a message and press Enter…")
        self._input.setFont(QFont("Segoe UI", 12))
        self._input.returnPressed.connect(self._on_send)
        input_row.addWidget(self._input)

        send_btn = QPushButton("Send")
        send_btn.setFixedWidth(70)
        send_btn.clicked.connect(self._on_send)
        input_row.addWidget(send_btn)

        left_layout.addLayout(input_row)

        # Right panel: camera + desires
        right = QWidget()
        right.setFixedWidth(340)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        self._camera = CameraView()
        right_layout.addWidget(self._camera, stretch=3)

        self._desire_panel = DesirePanel(self._desires)
        right_layout.addWidget(self._desire_panel, stretch=1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter)

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------

    def _on_send(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._log.append_line(f"\n[You] {text}")
        if self._agent_running:
            # Interrupt: inject into running agent
            self._input_queue.put_nowait(text)
        else:
            self._input_queue.put_nowait(text)

    # ------------------------------------------------------------------
    # Agent loop
    # ------------------------------------------------------------------

    async def _process_queue(self) -> None:
        """Dequeue user messages and run the agent; fire desires when idle."""
        import time

        last_interaction = time.time()
        while True:
            try:
                text = await asyncio.wait_for(self._input_queue.get(), timeout=IDLE_CHECK_INTERVAL)
            except asyncio.TimeoutError:
                # Idle — check desires if cooldown has passed
                if not self._agent_running and time.time() - last_interaction >= DESIRE_COOLDOWN:
                    pending: list[str] = []
                    if not self._input_queue.empty():
                        item = self._input_queue.get_nowait()
                        if item and item is not None:
                            pending.append(item)
                    tick = desire_tick_prompt(self._desires, pending)
                    if tick:
                        desire_name, prompt, _ = tick
                        self._log.append_line(f"… {desire_name}")
                        await self._run_agent("", inner_voice=prompt)
                        self._desires.satisfy(desire_name)
                        self._desires.curiosity_target = None
                        last_interaction = time.time()
                continue

            if text is None:
                break
            last_interaction = time.time()
            await self._run_agent(text)

    async def _run_agent(self, user_input: str, inner_voice: str = "") -> None:
        self._agent_running = True

        def on_text(chunk: str) -> None:
            self._stream.append_chunk(chunk)

        def on_action(name: str, tool_input: dict) -> None:
            # Commit any streamed text first, then log the action
            committed = self._stream.commit_and_clear()
            if committed.strip():
                self._log.append_line(f"[Agent] {committed.strip()}")
            self._log.append_action(name, tool_input)

        def on_image(b64: str) -> None:
            self._camera.update_image(b64)

        try:
            final_text = await self._agent.run(
                user_input,
                on_action=on_action,
                on_text=on_text,
                on_image=on_image,
                desires=self._desires,
                inner_voice=inner_voice,
                interrupt_queue=self._input_queue,
            )
            # Flush remaining streamed text
            committed = self._stream.commit_and_clear()
            display = committed.strip() or final_text.strip()
            if display:
                self._log.append_line(f"[Agent] {display}")
        except asyncio.CancelledError:
            self._stream.commit_and_clear()
            self._log.append_line("[interrupted]")
        except Exception as exc:
            logger.exception("Agent run error")
            self._log.append_line(f"[error] {exc}")
        finally:
            self._agent_running = False

    async def _show_init_status(self) -> None:
        """Update window title with elapsed time until embedding model is ready."""
        import time

        if self._agent.is_embedding_ready:
            return
        start = time.time()
        while not self._agent.is_embedding_ready:
            elapsed = int(time.time() - start)
            self.setWindowTitle(f"familiar-ai  ⏳ {_t('initializing')}... ({elapsed}s)")
            await asyncio.sleep(0.5)
        elapsed = int(time.time() - start)
        self._log.append_line(f"✅ {_t('initializing_done')} ({elapsed}s)")
        self.setWindowTitle("familiar-ai")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:  # type: ignore[override]
        asyncio.ensure_future(self._agent.close())
        self._input_queue.put_nowait(None)
        event.accept()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_gui(agent: EmbodiedAgent, desires: DesireSystem) -> None:
    """Launch the PySide6 GUI with qasync event loop."""
    import sys

    qt_app = QApplication.instance() or QApplication(sys.argv)
    loop = qasync.QEventLoop(qt_app)
    asyncio.set_event_loop(loop)

    window = FamiliarWindow(agent, desires)
    window.show()

    with loop:
        loop.run_forever()
