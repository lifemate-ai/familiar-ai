"""PySide6 GUI for familiar-ai — Airy Pastel theme.

Provides a native desktop window with:
- Scrollable conversation log with styled HTML-like bubbles (ChatLog)
- Live streaming text display with blinking cursor (StreamLabel)
- Camera image viewer (CameraView)
- Animated desire level bars (DesirePanel)
- Pill-shaped text input with circular send button
- Settings dialog (⚙) for .env configuration

Launch via:
    uv run familiar --gui

or via run.bat --gui / run.sh --gui
"""

from __future__ import annotations

import asyncio
import base64
import html as _html
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import qasync
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QTimer
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTabWidget,
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
from .realtime_stt_session import RealtimeSttSession, create_realtime_stt_session

if TYPE_CHECKING:
    from familiar_agent.agent import EmbodiedAgent
    from familiar_agent.config import AgentConfig
    from familiar_agent.desires import DesireSystem

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gear icon (SVG)
# ---------------------------------------------------------------------------

_GEAR_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
    ' stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="12" r="3"/>'
    '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06'
    "a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09"
    "A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83"
    "l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09"
    "A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83"
    "l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09"
    "a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83"
    "l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09"
    'a1.65 1.65 0 0 0-1.51 1z"/>'
    "</svg>"
)


def _gear_icon(color: str, size: int = 24) -> QIcon:
    """Render the gear SVG at *size*px with the given stroke *color*."""
    from PySide6.QtCore import QByteArray  # noqa: PLC0415
    from PySide6.QtGui import QPainter  # noqa: PLC0415

    svg_bytes = QByteArray(_GEAR_SVG.format(color=color).encode())
    renderer = QSvgRenderer(svg_bytes)
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(0)
    painter = QPainter(img)
    renderer.render(painter)
    painter.end()
    return QIcon(QPixmap.fromImage(img))


# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

_BG_BASE = "#F8F7FF"
_BG_SURFACE = "#F0EEFA"
_BG_CARD = "#EDE9FE"
_BG_ELEVATED = "#E8E3FC"
_BG_HOVER = "rgba(124,58,237,0.06)"
_ACCENT = "#7C3AED"
_ACCENT_DEEP = "#6D28D9"
_ACCENT_DIM = "#8B5CF6"
_TEXT_PRIMARY = "#1E1B3A"
_TEXT_SECONDARY = "#7C7A94"
_BORDER = "rgba(124,58,237,0.12)"
_BUBBLE_USER_BG = "rgba(124,58,237,0.10)"
_BUBBLE_AGENT_BG = "#FFFFFF"
_BUBBLE_TOOL_BG = "rgba(124,58,237,0.05)"

_DESIRE_COLORS: dict[str, str] = {
    "look_around": "#0891B2",
    "look_outside": "#2563EB",
    "miss_companion": "#DB2777",
    "browse_curiosity": "#7C3AED",
    "explore": "#4F46E5",
    "greet_companion": "#D97706",
    "worry_companion": "#DC2626",
}

# Flush streamed text at most this often (ms)
_STREAM_FLUSH_INTERVAL_MS = 50

# Resolve .env path: project root, then cwd fallback
_ENV_PATH: Path = Path(__file__).resolve().parents[2] / ".env"
if not _ENV_PATH.exists():
    _ENV_PATH = Path.cwd() / ".env"


# ---------------------------------------------------------------------------
# Global stylesheet
# ---------------------------------------------------------------------------


def _apply_global_style(app: QApplication) -> None:
    """Apply the Airy Pastel stylesheet to the whole application."""
    app.setStyleSheet(
        f"""
        QMainWindow {{ background: {_BG_BASE}; }}
        QDialog {{ background: {_BG_SURFACE}; }}

        /* Scrollbar — slim pastel */
        QScrollBar:vertical {{
            background: transparent; width: 6px; border-radius: 3px;
        }}
        QScrollBar::handle:vertical {{
            background: rgba(124,58,237,0.15); border-radius: 3px; min-height: 24px;
        }}
        QScrollBar::handle:vertical:hover {{ background: rgba(124,58,237,0.30); }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

        /* Inputs */
        QLineEdit {{
            background: #FFFFFF; color: {_TEXT_PRIMARY};
            border: 1px solid {_BORDER}; border-radius: 10px; padding: 8px 14px;
            font-size: 14px;
            selection-background-color: {_ACCENT_DIM};
        }}
        QLineEdit:focus {{ border-color: {_ACCENT}; background: #FDFCFF; }}

        /* Buttons */
        QPushButton {{
            background: {_BG_CARD}; color: {_TEXT_PRIMARY};
            border: 1px solid {_BORDER}; border-radius: 8px; padding: 7px 18px;
            font-size: 14px;
        }}
        QPushButton:hover {{ background: {_BG_ELEVATED}; border-color: {_ACCENT_DIM}; }}
        QPushButton:pressed {{ background: {_BG_SURFACE}; }}
        QPushButton:disabled {{
            background: {_BG_SURFACE}; color: {_TEXT_SECONDARY};
            border-color: rgba(124,58,237,0.06);
        }}

        /* ComboBox */
        QComboBox {{
            background: #FFFFFF; color: {_TEXT_PRIMARY};
            border: 1px solid {_BORDER}; border-radius: 10px; padding: 8px 14px;
            font-size: 14px;
        }}
        QComboBox::drop-down {{ border: none; padding-right: 8px; }}
        QComboBox QAbstractItemView {{
            background: #FFFFFF; color: {_TEXT_PRIMARY};
            selection-background-color: rgba(124,58,237,0.12);
            border: 1px solid {_BORDER};
        }}

        /* Tabs — pill style */
        QTabWidget::pane {{
            border: 1px solid {_BORDER}; background: {_BG_SURFACE}; top: -1px;
            border-radius: 12px;
        }}
        QTabBar::tab {{
            background: transparent; color: {_TEXT_SECONDARY};
            padding: 7px 22px; border-radius: 20px; margin-right: 4px;
            font-size: 13px;
        }}
        QTabBar::tab:selected {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {_ACCENT_DEEP}, stop:1 {_ACCENT_DIM});
            color: white;
        }}
        QTabBar::tab:hover:!selected {{ background: {_BG_CARD}; color: {_TEXT_PRIMARY}; }}

        """
    )


# ---------------------------------------------------------------------------
# ChatLog — bubble-based conversation log
# ---------------------------------------------------------------------------


class ChatLog(QScrollArea):
    """Scrollable chat log that renders messages as styled bubbles.

    Public API (backward-compatible with ActionLog):
        append_line(text: str) -> None
        append_action(name: str, tool_input: dict) -> None
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        agent_name: str = "Agent",
        companion_name: str = "You",
    ) -> None:
        super().__init__(parent)
        self._agent_display = agent_name
        self._companion_display = companion_name
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet(f"QScrollArea {{ background: {_BG_BASE}; border: none; }}")

        self._container = QWidget()
        self._container.setStyleSheet(f"background: {_BG_BASE}; border: none;")
        self._vbox = QVBoxLayout(self._container)
        self._vbox.setContentsMargins(10, 10, 10, 10)
        self._vbox.setSpacing(4)
        self._vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setWidget(self._container)

    def _scroll_to_bottom(self) -> None:
        QTimer.singleShot(
            20, lambda: self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        )

    def append_line(self, text: str) -> None:
        """Add a styled bubble. Prefix determines bubble style."""
        text = text.strip()
        if not text:
            return

        if text.startswith("[You]"):
            self._add_bubble(
                text[5:].strip(),
                prefix=self._companion_display,
                prefix_color=_TEXT_SECONDARY,
                bg=_BUBBLE_USER_BG,
                ml=60,
                mr=4,
            )
        elif text.startswith("[Agent]"):
            self._add_bubble(
                text[7:].strip(),
                prefix=self._agent_display,
                prefix_color=_ACCENT,
                bg=_BUBBLE_AGENT_BG,
                ml=4,
                mr=60,
                accent_left=True,
            )
        elif text.startswith("[error]"):
            self._add_bubble(
                f"⚠ {text[7:].strip()}",
                bg="#FEF2F2",
                text_color="#DC2626",
                ml=20,
                mr=20,
                small=True,
            )
        else:
            self._add_bubble(
                text,
                bg=_BUBBLE_TOOL_BG,
                text_color=_TEXT_SECONDARY,
                ml=20,
                mr=20,
                small=True,
                monospace=True,
            )

    def append_action(self, name: str, tool_input: dict) -> None:
        """Format a tool call and append it as a bubble."""
        self.append_line(format_action(name, tool_input))

    def _add_bubble(
        self,
        text: str,
        bg: str,
        ml: int = 0,
        mr: int = 0,
        prefix: str = "",
        prefix_color: str = _TEXT_SECONDARY,
        text_color: str = _TEXT_PRIMARY,
        small: bool = False,
        monospace: bool = False,
        accent_left: bool = False,
    ) -> None:
        escaped = _html.escape(text).replace("\n", "<br>")
        fs = "13px" if small else "15px"
        ff = "'Courier New', monospace" if monospace else "system-ui, -apple-system, sans-serif"

        if prefix:
            inner_html = (
                f'<span style="color:{prefix_color};font-size:12px;font-weight:600;'
                f'letter-spacing:0.04em;text-transform:uppercase;">'
                f"{_html.escape(prefix)}</span><br>"
                f'<span style="color:{text_color};font-size:{fs};font-family:{ff};">'
                f"{escaped}</span>"
            )
        else:
            inner_html = (
                f'<span style="color:{text_color};font-size:{fs};font-family:{ff};">'
                f"{escaped}</span>"
            )

        label = QLabel(inner_html)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        if accent_left:
            label.setStyleSheet(
                f"background: {bg}; border-radius: 16px; padding: 10px 16px;"
                f" border: 1px solid {_BORDER};"
                f" border-left: 3px solid {_ACCENT};"
            )
        else:
            label.setStyleSheet(
                f"background: {bg}; border-radius: 16px; padding: 10px 16px;"
                f" border: 1px solid {_BORDER};"
            )
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        row = QWidget()
        row.setStyleSheet("background: transparent;")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(ml, 2, mr, 2)
        rl.setSpacing(0)
        rl.addWidget(label)

        self._vbox.addWidget(row)
        self._scroll_to_bottom()


# ---------------------------------------------------------------------------
# StreamLabel — live LLM token display with blinking cursor
# ---------------------------------------------------------------------------


class StreamLabel(QWidget):
    """Displays streaming LLM text tokens in real time.

    Public API:
        append_chunk(chunk: str) -> None
        commit_and_clear() -> str
    """

    _BLINK_MS = 500

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._chunks: list[str] = []
        self._text = ""
        self._cursor_on = False

        self._label = QLabel("")
        self._label.setWordWrap(True)
        self._label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._label.setStyleSheet(
            f"background: #FFFFFF; color: {_TEXT_PRIMARY};"
            f" padding: 12px 18px; border-radius: 14px;"
            f" border: 1px solid {_BORDER}; border-left: 3px solid {_ACCENT};"
            f" font-family: system-ui, -apple-system, sans-serif; font-size: 15px;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)

        self._flush_timer = QTimer(self)
        self._flush_timer.setInterval(_STREAM_FLUSH_INTERVAL_MS)
        self._flush_timer.timeout.connect(self._flush)
        self._flush_timer.start()

        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(self._BLINK_MS)
        self._blink_timer.timeout.connect(self._blink)

    def append_chunk(self, chunk: str) -> None:
        self._chunks.append(chunk)
        if not self._blink_timer.isActive():
            self._blink_timer.start()

    def _flush(self) -> None:
        if self._chunks:
            self._text += "".join(self._chunks)
            self._chunks.clear()
            self._update_label()

    def _blink(self) -> None:
        self._cursor_on = not self._cursor_on
        self._update_label()

    def _update_label(self) -> None:
        cursor = "▊" if self._cursor_on else " "
        self._label.setText(self._text + cursor)

    def commit_and_clear(self) -> str:
        """Flush pending chunks, return full accumulated text, then clear."""
        self._flush()
        text = self._text
        self._text = ""
        self._chunks.clear()
        self._cursor_on = False
        self._blink_timer.stop()
        self._label.setText("")
        return text


# ---------------------------------------------------------------------------
# CameraView
# ---------------------------------------------------------------------------


class CameraView(QLabel):
    """Displays the latest camera image (base64-encoded JPEG/PNG)."""

    _PLACEHOLDER_SIZE = QSize(320, 240)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(self._PLACEHOLDER_SIZE)
        self.setStyleSheet(
            f"background: {_BG_CARD}; border-radius: 18px;"
            f" border: 1px solid {_BORDER}; color: {_TEXT_SECONDARY};"
            f" font-size: 14px;"
        )
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


# ---------------------------------------------------------------------------
# DesireBar — single desire with animated progress bar
# ---------------------------------------------------------------------------


class DesireBar(QWidget):
    """A labeled progress bar with smooth animation for one desire."""

    def __init__(self, name: str, color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 2, 0, 2)
        vbox.setSpacing(2)

        # Header: desire name + percentage
        header = QHBoxLayout()
        display_name = name.replace("_", " ").title()
        name_lbl = QLabel(display_name)
        name_lbl.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: 600; background: transparent;"
            f" letter-spacing: 0.03em;"
        )
        header.addWidget(name_lbl)
        header.addStretch()
        self._pct_label = QLabel("0%")
        self._pct_label.setStyleSheet(
            f"color: {_TEXT_SECONDARY}; font-size: 11px; background: transparent;"
        )
        header.addWidget(self._pct_label)
        vbox.addLayout(header)

        # Gradient progress bar
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(6)
        self._bar.setStyleSheet(
            f"QProgressBar {{ background: rgba(124,58,237,0.08); border-radius: 3px; border: none; }}"
            f"QProgressBar::chunk {{"
            f" background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 rgba(0,0,0,0), stop:0.3 {color}66, stop:1 {color});"
            f" border-radius: 3px;"
            f"}}"
        )
        vbox.addWidget(self._bar)

        # Smooth animation
        self._anim = QPropertyAnimation(self._bar, b"value")
        self._anim.setDuration(500)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def set_level(self, level: float) -> None:
        target = int(level * 100)
        self._anim.stop()
        self._anim.setStartValue(self._bar.value())
        self._anim.setEndValue(target)
        self._anim.start()
        self._pct_label.setText(f"{target}%")


# ---------------------------------------------------------------------------
# DesirePanel
# ---------------------------------------------------------------------------


class DesirePanel(QWidget):
    """Shows desire levels as animated bars, refreshed every 2 seconds."""

    def __init__(self, desires: "DesireSystem", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._desires = desires
        self._bars: dict[str, DesireBar] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("✦ DESIRES")
        title.setStyleSheet(
            f"color: {_TEXT_SECONDARY}; font-size: 12px; font-weight: 600;"
            f" background: transparent; letter-spacing: 0.1em;"
        )
        layout.addWidget(title)

        for name, color in _DESIRE_COLORS.items():
            bar = DesireBar(name, color)
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
                bar.set_level(level)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# SettingsDialog
# ---------------------------------------------------------------------------


class SettingsDialog(QDialog):
    """Settings dialog with 4 tabs: Agent, Voice, Camera, Advanced."""

    def __init__(
        self,
        config: "AgentConfig",
        env_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._env_path = env_path
        self.setWindowTitle("Settings — familiar-ai")
        self.setMinimumWidth(500)
        self.setModal(True)

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(16, 16, 16, 12)
        vbox.setSpacing(12)

        tabs = QTabWidget()
        vbox.addWidget(tabs)

        # ── Tab 1: Agent ──────────────────────────────────────────
        agent_tab = QWidget()
        agent_tab.setStyleSheet("background: transparent; font-size: 14px;")
        af = QFormLayout(agent_tab)
        af.setSpacing(10)

        self._agent_name = QLineEdit(config.agent_name)
        self._companion_name = QLineEdit(config.companion_name)
        self._platform = QComboBox()
        self._platform.addItems(["anthropic", "google", "openai", "kimi", "glm"])
        _set_combo(self._platform, config.platform)
        self._api_key = QLineEdit(config.api_key)
        self._api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key.setPlaceholderText("(unchanged)")
        self._model = QLineEdit(config.model)

        af.addRow("Agent name:", self._agent_name)
        af.addRow("Companion name:", self._companion_name)
        af.addRow("Platform:", self._platform)
        af.addRow("API key:", self._api_key)
        af.addRow("Model:", self._model)
        tabs.addTab(agent_tab, "Agent")

        # ── Tab 2: Voice ──────────────────────────────────────────
        voice_tab = QWidget()
        voice_tab.setStyleSheet("background: transparent; font-size: 14px;")
        vf = QFormLayout(voice_tab)
        vf.setSpacing(10)

        self._el_api_key = QLineEdit(config.tts.elevenlabs_api_key)
        self._el_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._el_api_key.setPlaceholderText("(unchanged)")
        self._voice_id = QLineEdit(config.tts.voice_id)
        self._tts_output = QComboBox()
        self._tts_output.addItems(["local", "remote", "both"])
        _set_combo(self._tts_output, config.tts.output)
        self._stt_language = QLineEdit(config.stt.language)

        vf.addRow("ElevenLabs API key:", self._el_api_key)
        vf.addRow("Voice ID:", self._voice_id)
        vf.addRow("TTS output:", self._tts_output)
        vf.addRow("STT language:", self._stt_language)
        tabs.addTab(voice_tab, "Voice")

        # ── Tab 3: Camera ─────────────────────────────────────────
        cam_tab = QWidget()
        cam_tab.setStyleSheet("background: transparent; font-size: 14px;")
        cf = QFormLayout(cam_tab)
        cf.setSpacing(10)

        self._cam_host = QLineEdit(config.camera.host)
        self._cam_user = QLineEdit(config.camera.username)
        self._cam_pass = QLineEdit(config.camera.password)
        self._cam_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self._cam_pass.setPlaceholderText("(unchanged)")
        self._cam_port = QLineEdit(str(config.camera.port))

        cf.addRow("Camera host:", self._cam_host)
        cf.addRow("Username:", self._cam_user)
        cf.addRow("Password:", self._cam_pass)
        cf.addRow("ONVIF port:", self._cam_port)
        tabs.addTab(cam_tab, "Camera")

        # ── Tab 4: Advanced ───────────────────────────────────────
        adv_tab = QWidget()
        adv_tab.setStyleSheet("background: transparent; font-size: 14px;")
        advf = QFormLayout(adv_tab)
        advf.setSpacing(10)

        self._thinking_mode = QComboBox()
        self._thinking_mode.addItems(["auto", "adaptive", "extended", "disabled"])
        _set_combo(self._thinking_mode, config.thinking_mode)
        self._thinking_effort = QComboBox()
        self._thinking_effort.addItems(["low", "medium", "high", "max"])
        _set_combo(self._thinking_effort, config.thinking_effort)
        self._memory_path = QLineEdit(config.memory.db_path)

        advf.addRow("Thinking mode:", self._thinking_mode)
        advf.addRow("Thinking effort:", self._thinking_effort)
        advf.addRow("Memory DB path:", self._memory_path)
        tabs.addTab(adv_tab, "Advanced")

        # Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self._save)
        btn_box.rejected.connect(self.reject)
        vbox.addWidget(btn_box)

    def _save(self) -> None:
        from dotenv import set_key

        env_str = str(self._env_path)

        # Non-sensitive fields: always write
        plain_pairs = [
            ("AGENT_NAME", self._agent_name.text()),
            ("COMPANION_NAME", self._companion_name.text()),
            ("PLATFORM", self._platform.currentText()),
            ("MODEL", self._model.text()),
            ("ELEVENLABS_VOICE_ID", self._voice_id.text()),
            ("TTS_OUTPUT", self._tts_output.currentText()),
            ("STT_LANGUAGE", self._stt_language.text()),
            ("CAMERA_HOST", self._cam_host.text()),
            ("CAMERA_USERNAME", self._cam_user.text()),
            ("CAMERA_ONVIF_PORT", self._cam_port.text()),
            ("THINKING_MODE", self._thinking_mode.currentText()),
            ("THINKING_EFFORT", self._thinking_effort.currentText()),
            ("MEMORY_DB_PATH", self._memory_path.text()),
        ]
        # Sensitive fields: skip if empty (placeholder shown)
        masked_pairs = [
            ("API_KEY", self._api_key.text()),
            ("ELEVENLABS_API_KEY", self._el_api_key.text()),
            ("CAMERA_PASSWORD", self._cam_pass.text()),
        ]

        try:
            self._env_path.touch(exist_ok=True)
            for key, value in plain_pairs:
                if value:
                    set_key(env_str, key, value)
            for key, value in masked_pairs:
                if value:
                    set_key(env_str, key, value)
        except Exception as exc:
            QMessageBox.warning(self, "Save failed", str(exc))
            return

        QMessageBox.information(
            self,
            "Settings saved",
            "Settings saved.\nRestart familiar-ai to apply all changes.",
        )
        self.accept()


def _set_combo(combo: QComboBox, value: str) -> None:
    """Select a combo box item by value, ignoring if not found."""
    idx = combo.findText(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------


class FamiliarWindow(QMainWindow):
    """Main application window."""

    def __init__(self, agent: "EmbodiedAgent", desires: "DesireSystem") -> None:
        super().__init__()
        self._agent = agent
        self._desires = desires
        self._input_queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._agent_running = False
        self._realtime_stt: RealtimeSttSession | None = create_realtime_stt_session()

        self.setWindowTitle("familiar-ai")
        self.resize(1020, 720)
        self.setStyleSheet(f"background: {_BG_BASE};")
        self._build_ui()

        asyncio.ensure_future(self._process_queue())
        if not self._agent.is_embedding_ready:
            asyncio.ensure_future(self._show_init_status())
        if self._realtime_stt:
            asyncio.ensure_future(self._start_realtime_stt())

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        central.setStyleSheet(f"background: {_BG_BASE};")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # ── Left panel ──────────────────────────────────────────
        left = QWidget()
        left.setStyleSheet(f"background: {_BG_BASE};")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # Header bar
        header = QWidget()
        header.setStyleSheet(
            f"background: #FFFFFF; border-radius: 14px; border: 1px solid {_BORDER};"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 10, 10, 10)
        header_layout.setSpacing(8)

        title_lbl = QLabel("✦ familiar-ai")
        title_lbl.setStyleSheet(
            f"color: {_ACCENT}; font-size: 18px; font-weight: 700; background: transparent;"
            f" letter-spacing: -0.02em;"
        )
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        settings_btn = QPushButton()
        settings_btn.setFixedSize(36, 36)
        settings_btn.setIcon(_gear_icon(_TEXT_SECONDARY, 20))
        settings_btn.setIconSize(QSize(20, 20))
        settings_btn.setStyleSheet(
            f"QPushButton {{ background: {_BG_CARD}; border-radius: 18px;"
            f" border: 1px solid {_BORDER}; }}"
            f"QPushButton:hover {{ background: {_BG_ELEVATED}; }}"
        )
        settings_btn.clicked.connect(self._open_settings)
        header_layout.addWidget(settings_btn)
        left_layout.addWidget(header)

        # Chat log
        self._log = ChatLog(
            agent_name=self._agent.config.agent_name,
            companion_name=self._agent.config.companion_name,
        )
        left_layout.addWidget(self._log, stretch=5)

        # Stream label
        self._stream = StreamLabel()
        self._stream.setMinimumHeight(64)
        left_layout.addWidget(self._stream, stretch=1)

        # Input row — pill QLineEdit + circular send button
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a message and press Enter…")
        self._input.setObjectName("msgInput")
        self._input.setStyleSheet(
            f"QLineEdit#msgInput {{"
            f" border-radius: 999px; padding: 12px 22px;"
            f" background: #FFFFFF; border: 1px solid {_BORDER};"
            f" color: {_TEXT_PRIMARY}; font-size: 15px;"
            f" font-family: system-ui, -apple-system, sans-serif;"
            f"}}"
            f"QLineEdit#msgInput:focus {{"
            f" border-color: {_ACCENT}; background: #FDFCFF;"
            f"}}"
        )
        self._input.returnPressed.connect(self._on_send)
        input_row.addWidget(self._input)

        self._send_btn = QPushButton("⬆")
        self._send_btn.setFixedSize(44, 44)
        self._send_btn.setObjectName("sendBtn")
        self._send_btn.setStyleSheet(
            f"QPushButton#sendBtn {{"
            f" background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f" stop:0 {_ACCENT_DEEP}, stop:1 {_ACCENT_DIM});"
            f" border-radius: 22px; border: none;"
            f" font-size: 20px; color: white;"
            f"}}"
            f"QPushButton#sendBtn:hover {{"
            f" background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f" stop:0 #5B21B6, stop:1 #A78BFA);"
            f"}}"
            f"QPushButton#sendBtn:disabled {{"
            f" background: {_BG_CARD}; color: {_TEXT_SECONDARY};"
            f"}}"
        )
        self._send_btn.clicked.connect(self._on_send)
        input_row.addWidget(self._send_btn)
        left_layout.addLayout(input_row)

        # ── Right panel ─────────────────────────────────────────
        right = QWidget()
        right.setFixedWidth(340)
        right.setStyleSheet(f"background: {_BG_BASE};")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self._camera = CameraView()
        right_layout.addWidget(self._camera, stretch=3)

        desire_card = QWidget()
        desire_card.setStyleSheet(
            f"background: #FFFFFF; border-radius: 18px; border: 1px solid {_BORDER};"
        )
        desire_card_vbox = QVBoxLayout(desire_card)
        desire_card_vbox.setContentsMargins(0, 0, 0, 0)
        self._desire_panel = DesirePanel(self._desires)
        self._desire_panel.setStyleSheet("background: transparent;")
        desire_card_vbox.addWidget(self._desire_panel)
        right_layout.addWidget(desire_card, stretch=2)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setStyleSheet(f"QSplitter::handle {{ background: {_BG_ELEVATED}; width: 1px; }}")
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter)

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self._agent.config, _ENV_PATH, self)
        dlg.exec()

    def _on_send(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._log.append_line(f"[You] {text}")
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
                if not self._agent_running and time.time() - last_interaction >= DESIRE_COOLDOWN:
                    pending: list[str] = []
                    if not self._input_queue.empty():
                        item = self._input_queue.get_nowait()
                        if item is not None:
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
        self._send_btn.setEnabled(False)

        def on_text(chunk: str) -> None:
            self._stream.append_chunk(chunk)

        def on_action(name: str, tool_input: dict) -> None:
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
            self._send_btn.setEnabled(True)

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
    # Realtime STT
    # ------------------------------------------------------------------

    async def _start_realtime_stt(self) -> None:
        """Initialize and run realtime STT in the background."""
        assert self._realtime_stt is not None
        try:
            loop = asyncio.get_running_loop()

            def _on_partial(text: str) -> None:
                self._stream._label.setText(f"\U0001f3a4 {text}")

            def _on_committed(text: str) -> None:
                self._log.append_line(f"[You] \U0001f3a4 {text}")

            self._realtime_stt.on_partial = _on_partial
            self._realtime_stt.on_committed = _on_committed
            await self._realtime_stt.start(loop, self._input_queue)
            self._log.append_line("\U0001f3a4 Realtime STT ON (ElevenLabs)")
        except Exception as e:
            logger.warning("Realtime STT init failed: %s", e)
            self._log.append_line(f"[error] Realtime STT init failed: {e}")
            self._realtime_stt = None

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._realtime_stt:
            asyncio.ensure_future(self._realtime_stt.stop())
        asyncio.ensure_future(self._agent.close())
        self._input_queue.put_nowait(None)
        event.accept()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_gui(agent: "EmbodiedAgent", desires: "DesireSystem") -> None:
    """Launch the PySide6 GUI with qasync event loop."""
    import sys

    existing = QApplication.instance()
    qt_app = existing if isinstance(existing, QApplication) else QApplication(sys.argv)
    _apply_global_style(qt_app)

    loop = qasync.QEventLoop(qt_app)
    asyncio.set_event_loop(loop)

    window = FamiliarWindow(agent, desires)
    window.show()

    with loop:
        loop.run_forever()
