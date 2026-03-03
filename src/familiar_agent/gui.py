"""PySide6 GUI for familiar-ai — Soft Daylight theme.

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
import contextlib
import html as _html
import logging
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

import qasync
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
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
    QPlainTextEdit,
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
    should_fire_idle_desire,
)
from .realtime_stt_session import create_realtime_stt_session

if TYPE_CHECKING:
    from familiar_agent.agent import EmbodiedAgent
    from familiar_agent.config import AgentConfig
    from familiar_agent.desires import DesireSystem
    from familiar_agent.realtime_stt_session import RealtimeSttSession

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

_BG_BASE = "#f8fbff"
_BG_SURFACE = "#ffffff"
_BG_CARD = "#ffffff"
_BG_ELEVATED = "#fff8fc"
_BG_HOVER = "rgba(255, 167, 190, 0.16)"
_ACCENT = "#ff8db1"
_ACCENT_DEEP = "#ff6e9d"
_ACCENT_DIM = "#ffd7e7"
_TEXT_PRIMARY = "#342c44"
_TEXT_SECONDARY = "#7f7394"
_BORDER = "rgba(255, 169, 192, 0.42)"
_BUBBLE_USER_BG = "#ffe9f3"
_BUBBLE_AGENT_BG = "#ffffff"
_BUBBLE_TOOL_BG = "#eef6ff"
_UI_FONT_STACK = (
    "'Noto Sans CJK JP', 'Yu Gothic UI', 'Hiragino Sans', 'Meiryo', 'Segoe UI', sans-serif"
)
_MONO_FONT_STACK = "'Cascadia Mono', 'Consolas', 'Courier New', monospace"
_FONT_SCALE = 1.9

_DESIRE_COLORS: dict[str, str] = {
    "look_around": "#57b8ff",
    "look_outside": "#4f8cff",
    "miss_companion": "#ff7ea3",
    "browse_curiosity": "#58c5b7",
    "explore": "#5ea1ff",
    "greet_companion": "#ffb35f",
    "worry_companion": "#ff6b73",
}

# Flush streamed text at most this often (ms)
_STREAM_FLUSH_INTERVAL_MS = 50
_GUI_LOOP_LAG_CHECK_SEC = 1.0
_GUI_LOOP_LAG_WARN_SEC = 0.35
_GUI_QUEUE_WARN_SIZE = 20
_GUI_LOOK_PREVIEW_FPS = 8
_GUI_LOOK_PREVIEW_MIN_SEC = 0.8
_GUI_LOOK_PREVIEW_MAX_SEC = 2.0
_GUI_LOOK_PREVIEW_GRACE_SEC = 0.3
_GUI_LOOK_PREVIEW_READ_TIMEOUT_SEC = 0.35


def _px(size: int) -> int:
    """Scale font-size in px for large readable UI."""
    return max(1, int(round(size * _FONT_SCALE)))


# Resolve .env path: project root, then cwd fallback
_ENV_PATH: Path = Path(__file__).resolve().parents[2] / ".env"
if not _ENV_PATH.exists():
    _ENV_PATH = Path.cwd() / ".env"

_TESTFLIGHT_SETUP_FLAG = "TESTFLIGHT_SETUP_DONE"
_TESTFLIGHT_PERSONA_PATH = Path.home() / ".familiar_ai" / "ME.md"


# ---------------------------------------------------------------------------
# Global stylesheet
# ---------------------------------------------------------------------------


def _apply_global_style(app: QApplication) -> None:
    """Apply the Soft Daylight stylesheet to the whole application."""
    app.setStyleSheet(
        f"""
        QWidget {{
            color: {_TEXT_PRIMARY};
            font-family: {_UI_FONT_STACK};
            font-size: {_px(13)}px;
        }}
        QMainWindow {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #fefeff, stop:1 {_BG_BASE});
        }}
        QDialog {{
            background: {_BG_SURFACE};
            border: 1px solid {_BORDER};
            border-radius: 20px;
        }}
        QLabel {{ color: {_TEXT_PRIMARY}; }}

        /* Scrollbar — soft rounded */
        QScrollBar:vertical {{
            background: transparent; width: 6px; border-radius: 3px;
        }}
        QScrollBar::handle:vertical {{
            background: rgba(127,115,148,0.34); border-radius: 3px; min-height: 24px;
        }}
        QScrollBar::handle:vertical:hover {{ background: rgba(255,141,177,0.72); }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

        /* Inputs */
        QLineEdit {{
            background: {_BG_SURFACE}; color: {_TEXT_PRIMARY};
            border: 1px solid {_BORDER}; border-radius: 15px; padding: 10px 14px;
            selection-background-color: {_ACCENT_DIM};
        }}
        QPlainTextEdit {{
            background: {_BG_SURFACE}; color: {_TEXT_PRIMARY};
            border: 1px solid {_BORDER}; border-radius: 15px; padding: 10px 14px;
            selection-background-color: {_ACCENT_DIM};
        }}
        QLineEdit:focus {{
            border-color: {_ACCENT};
            background: #fffaff;
        }}
        QPlainTextEdit:focus {{
            border-color: {_ACCENT};
            background: #fffaff;
        }}

        /* Buttons */
        QPushButton {{
            background: #fff4fa; color: {_TEXT_PRIMARY};
            border: 1px solid {_BORDER}; border-radius: 16px; padding: 10px 18px;
        }}
        QPushButton:hover {{ background: #ffe8f2; border-color: rgba(255,141,177,0.75); }}
        QPushButton:pressed {{ background: #ffdfea; }}
        QPushButton:disabled {{
            background: #f7f3f8; color: {_TEXT_SECONDARY};
            border-color: rgba(127,115,148,0.20);
        }}

        /* ComboBox */
        QComboBox {{
            background: {_BG_SURFACE}; color: {_TEXT_PRIMARY};
            border: 1px solid {_BORDER}; border-radius: 15px; padding: 10px 14px;
        }}
        QComboBox::drop-down {{ border: none; padding-right: 8px; }}
        QComboBox QAbstractItemView {{
            background: {_BG_CARD}; color: {_TEXT_PRIMARY};
            selection-background-color: #ffe1ee;
            border: 1px solid {_BORDER};
        }}

        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {_BORDER}; background: {_BG_SURFACE}; top: -1px;
            border-radius: 16px;
        }}
        QTabBar::tab {{
            background: #fff7fc; color: {_TEXT_SECONDARY};
            padding: 10px 22px; border-radius: 18px; margin-right: 6px;
            border: 1px solid rgba(255,169,192,0.28);
        }}
        QTabBar::tab:selected {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {_ACCENT_DEEP}, stop:1 {_ACCENT});
            color: white;
            border-color: rgba(255,110,157,0.8);
        }}
        QTabBar::tab:hover:!selected {{ background: #ffeef6; color: {_TEXT_PRIMARY}; }}
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
        *,
        agent_label: str = "Agent",
        companion_label: str = "You",
    ) -> None:
        super().__init__(parent)
        self._agent_label = (agent_label or "Agent").strip() or "Agent"
        self._companion_label = (companion_label or "You").strip() or "You"
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

    @staticmethod
    def _extract_prefixed_text(text: str, label: str) -> str | None:
        marker = f"[{label}]"
        if text.startswith(marker):
            return text[len(marker) :].strip()
        return None

    def append_line(self, text: str) -> None:
        """Add a styled bubble. Prefix determines bubble style."""
        text = text.strip()
        if not text:
            return

        user_text = self._extract_prefixed_text(text, self._companion_label)
        if user_text is None and self._companion_label != "You":
            user_text = self._extract_prefixed_text(text, "You")
        if user_text is not None:
            self._add_bubble(
                user_text,
                prefix=self._companion_label,
                prefix_color=_TEXT_SECONDARY,
                bg=_BUBBLE_USER_BG,
                ml=60,
                mr=4,
            )
            return

        agent_text = self._extract_prefixed_text(text, self._agent_label)
        if agent_text is None and self._agent_label != "Agent":
            agent_text = self._extract_prefixed_text(text, "Agent")
        if agent_text is not None:
            self._add_bubble(
                agent_text,
                prefix=self._agent_label,
                prefix_color=_ACCENT,
                bg=_BUBBLE_AGENT_BG,
                ml=4,
                mr=60,
                accent_left=True,
            )
            return

        if text.startswith("[error]"):
            self._add_bubble(
                f"⚠ {text[7:].strip()}",
                bg="#ffe9ee",
                text_color="#d83d58",
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
        fs = f"{_px(11) if small else _px(13)}px"
        ff = _MONO_FONT_STACK if monospace else _UI_FONT_STACK

        if prefix:
            inner_html = (
                f'<span style="color:{prefix_color};font-size:{_px(10)}px;font-weight:600;'
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
        self._status_text = ""
        self._cursor_on = False

        self._label = QLabel("")
        self._label.setWordWrap(True)
        self._label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._label.setStyleSheet(
            f"background: {_BG_SURFACE}; color: {_TEXT_PRIMARY};"
            f" padding: 10px 16px; border-radius: 14px;"
            f" border: 1px solid {_BORDER}; border-left: 3px solid {_ACCENT};"
            f" font-family: {_UI_FONT_STACK}; font-size: {_px(13)}px;"
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
        self._status_text = ""
        if not self._blink_timer.isActive():
            self._blink_timer.start()

    def set_status(self, text: str) -> None:
        """Display non-streaming status text (e.g., thinking elapsed time)."""
        self._status_text = text
        if not self._text and not self._chunks:
            self._label.setText(self._status_text)

    def clear_status(self) -> None:
        """Clear the status text if no streaming text is currently shown."""
        self._status_text = ""
        if not self._text and not self._chunks:
            self._label.setText("")

    def has_content(self) -> bool:
        """Whether streamed assistant text is currently visible/pending."""
        return bool(self._text or self._chunks)

    def _flush(self) -> None:
        if self._chunks:
            self._text += "".join(self._chunks)
            self._chunks.clear()
            self._update_label()

    def _blink(self) -> None:
        self._cursor_on = not self._cursor_on
        self._update_label()

    def _update_label(self) -> None:
        if self._text:
            cursor = "▊" if self._cursor_on else " "
            self._label.setText(self._text + cursor)
        elif self._status_text:
            self._label.setText(self._status_text)
        else:
            self._label.setText("")

    def commit_and_clear(self) -> str:
        """Flush pending chunks, return full accumulated text, then clear."""
        self._flush()
        text = self._text
        self._text = ""
        self._chunks.clear()
        self._status_text = ""
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
        try:
            display_name = _t(f"desire_label_{name}")
        except KeyError:
            display_name = name.replace("_", " ").title()
        name_lbl = QLabel(display_name)
        name_lbl.setStyleSheet(
            f"color: {color}; font-size: {_px(10)}px; font-weight: 600; background: transparent;"
            f" letter-spacing: 0.03em;"
        )
        header.addWidget(name_lbl)
        header.addStretch()
        self._pct_label = QLabel("0%")
        self._pct_label.setStyleSheet(
            f"color: {_TEXT_SECONDARY}; font-size: {_px(10)}px; background: transparent;"
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
            f"QProgressBar {{ background: rgba(127,115,148,0.16); border-radius: 3px; border: none; }}"
            f"QProgressBar::chunk {{"
            f" background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 rgba(0,0,0,0), stop:0.3 {color}55, stop:1 {color});"
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

        title = QLabel(_t("desire_panel_title"))
        title.setStyleSheet(
            f"color: {_TEXT_SECONDARY}; font-size: {_px(10)}px; font-weight: 600;"
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
# Testflight Setup
# ---------------------------------------------------------------------------


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def build_testflight_persona(
    *,
    agent_name: str,
    companion_name: str,
    companion_profile: str,
    agent_profile: str,
    relationship: str,
) -> str:
    """Build ME.md content from structured first-run setup fields."""
    a_name = (agent_name or "AI").strip() or "AI"
    c_name = (companion_name or "あなた").strip() or "あなた"
    c_profile = companion_profile.strip()
    a_profile = agent_profile.strip()
    relation = relationship.strip()
    return (
        "# 私について\n\n"
        f"名前：{a_name}\n\n"
        f"{a_profile}\n\n"
        "## 一緒に暮らす人\n\n"
        f"- 名前：{c_name}\n"
        f"- 設定：{c_profile}\n\n"
        "## 二人の関係性\n\n"
        f"{relation}\n"
    )


def needs_testflight_setup(
    config: "AgentConfig",
    *,
    setup_flag: str | None = None,
    persona_path: Path | None = None,
) -> bool:
    """Return True when testflight first-run setup should be shown."""
    if not getattr(config, "testflight_mode", False):
        return False

    done = _is_truthy(
        setup_flag if setup_flag is not None else os.environ.get(_TESTFLIGHT_SETUP_FLAG)
    )
    cam = config.camera
    has_camera = bool(cam.host.strip() and cam.username.strip() and cam.password.strip())
    persona_target = persona_path or _TESTFLIGHT_PERSONA_PATH
    try:
        has_persona = persona_target.exists() and bool(
            persona_target.read_text(encoding="utf-8").strip()
        )
    except Exception:
        has_persona = False
    return not (done and has_camera and has_persona)


class TestflightSetupDialog(QDialog):
    """Minimal first-run setup for external testflight users."""

    def __init__(
        self,
        config: "AgentConfig",
        env_path: Path,
        persona_path: Path = _TESTFLIGHT_PERSONA_PATH,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._env_path = env_path
        self._persona_path = persona_path

        self.setWindowTitle("テスト版 初回セットアップ")
        self.setModal(True)
        self.setMinimumWidth(880)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 14)
        root.setSpacing(12)

        intro = QLabel(
            "今晩のテスト向けに、最初に必要な項目だけ入力してね。\n入力後は自動で設定保存されます。"
        )
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {_TEXT_SECONDARY}; background: transparent;")
        root.addWidget(intro)

        def _label(text: str) -> QLabel:
            lbl = QLabel(text)
            lbl.setMinimumWidth(210)
            lbl.setStyleSheet(
                f"color: {_TEXT_PRIMARY}; font-size: {_px(13)}px; font-weight: 600; background: transparent;"
            )
            return lbl

        tabs = QTabWidget()
        root.addWidget(tabs)

        persona_tab = QWidget()
        persona_form = QFormLayout(persona_tab)
        persona_form.setHorizontalSpacing(16)
        persona_form.setVerticalSpacing(10)
        persona_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._agent_name = QLineEdit((config.agent_name or "AI").strip() or "AI")
        self._companion_name = QLineEdit((config.companion_name or "").strip())
        self._companion_profile = QPlainTextEdit()
        self._companion_profile.setPlaceholderText("例: 眼鏡をかけてる、夜型、コーヒー好き など")
        self._companion_profile.setFixedHeight(110)
        self._agent_profile = QPlainTextEdit()
        self._agent_profile.setPlaceholderText("例: 明るい関西弁、観察好き、短く率直に話す など")
        self._agent_profile.setFixedHeight(110)
        self._relationship = QPlainTextEdit()
        self._relationship.setPlaceholderText("例: 幼馴染。深夜によく一緒に作業する相棒。")
        self._relationship.setFixedHeight(110)

        persona_form.addRow(_label("エージェント名"), self._agent_name)
        persona_form.addRow(_label("ユーザー名"), self._companion_name)
        persona_form.addRow(_label("ユーザー設定"), self._companion_profile)
        persona_form.addRow(_label("エージェント設定"), self._agent_profile)
        persona_form.addRow(_label("二人の関係性"), self._relationship)
        tabs.addTab(persona_tab, "1. ペルソナ")

        other_tab = QWidget()
        other_form = QFormLayout(other_tab)
        other_form.setHorizontalSpacing(16)
        other_form.setVerticalSpacing(10)
        other_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._cam_host = QLineEdit(config.camera.host)
        self._cam_host.setPlaceholderText("例: 192.168.0.100")
        self._cam_user = QLineEdit((config.camera.username or "admin").strip() or "admin")
        self._cam_pass = QLineEdit(config.camera.password)
        self._cam_pass.setEchoMode(QLineEdit.EchoMode.Password)

        other_form.addRow(_label("カメラIP"), self._cam_host)
        other_form.addRow(_label("カメラアカウント"), self._cam_user)
        other_form.addRow(_label("カメラパスワード"), self._cam_pass)
        tabs.addTab(other_tab, "2. カメラ")

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _save(self) -> None:
        from dotenv import set_key

        agent_name = self._agent_name.text().strip()
        companion_name = self._companion_name.text().strip()
        companion_profile = self._companion_profile.toPlainText().strip()
        agent_profile = self._agent_profile.toPlainText().strip()
        relationship = self._relationship.toPlainText().strip()
        cam_host = self._cam_host.text().strip()
        cam_user = self._cam_user.text().strip() or "admin"
        cam_pass = self._cam_pass.text().strip()

        missing = []
        if not agent_name:
            missing.append("エージェント名")
        if not companion_name:
            missing.append("ユーザー名")
        if not companion_profile:
            missing.append("ユーザー設定")
        if not agent_profile:
            missing.append("エージェント設定")
        if not relationship:
            missing.append("二人の関係性")
        if not cam_host:
            missing.append("カメラIP")
        if not cam_user:
            missing.append("カメラアカウント")
        if not cam_pass:
            missing.append("カメラパスワード")
        if missing:
            QMessageBox.warning(
                self, "入力不足", "次の項目を埋めてください:\n- " + "\n- ".join(missing)
            )
            return

        persona_text = build_testflight_persona(
            agent_name=agent_name,
            companion_name=companion_name,
            companion_profile=companion_profile,
            agent_profile=agent_profile,
            relationship=relationship,
        )

        try:
            self._persona_path.parent.mkdir(parents=True, exist_ok=True)
            self._persona_path.write_text(persona_text, encoding="utf-8")

            env_str = str(self._env_path)
            self._env_path.touch(exist_ok=True)
            pairs = [
                ("AGENT_NAME", agent_name),
                ("COMPANION_NAME", companion_name),
                ("CAMERA_HOST", cam_host),
                ("CAMERA_USERNAME", cam_user),
                ("CAMERA_PASSWORD", cam_pass),
                ("CAMERA_ONVIF_PORT", "2020"),
                ("MOBILITY_ENABLED", "false"),
                (_TESTFLIGHT_SETUP_FLAG, "true"),
            ]
            for key, value in pairs:
                set_key(env_str, key, value)
        except Exception as exc:
            QMessageBox.warning(self, "保存失敗", str(exc))
            return

        QMessageBox.information(self, "保存完了", "セットアップ完了。アプリを起動します。")
        self.accept()


def run_testflight_setup_if_needed(config: "AgentConfig", env_path: Path = _ENV_PATH) -> bool:
    """Run first-run setup dialog in testflight mode when needed."""
    if not needs_testflight_setup(config):
        return True

    import sys

    existing = QApplication.instance()
    qt_app = existing if isinstance(existing, QApplication) else QApplication(sys.argv)
    _apply_global_style(qt_app)
    dlg = TestflightSetupDialog(config, env_path)
    return dlg.exec() == int(QDialog.DialogCode.Accepted)


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
        self.setWindowTitle(_t("settings_window_title"))
        self.setMinimumWidth(760)
        self.setModal(True)

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(16, 16, 16, 12)
        vbox.setSpacing(12)

        tabs = QTabWidget()
        vbox.addWidget(tabs)

        def _style_form(form: QFormLayout) -> None:
            form.setHorizontalSpacing(16)
            form.setVerticalSpacing(11)
            form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
            form.setFormAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        def _form_label(key: str) -> QLabel:
            label = QLabel(_t(key))
            # Keep enough width so short JP labels like 「名」 never get clipped.
            label.setMinimumWidth(180)
            label.setStyleSheet(
                f"color: {_TEXT_PRIMARY}; font-size: {_px(13)}px; font-weight: 600;"
                f"padding-right: 6px; background: transparent;"
            )
            return label

        # ── Tab 1: Agent ──────────────────────────────────────────
        agent_tab = QWidget()
        agent_tab.setStyleSheet("background: transparent;")
        af = QFormLayout(agent_tab)
        _style_form(af)

        self._agent_name = QLineEdit(config.agent_name)
        self._companion_name = QLineEdit(config.companion_name)
        self._platform = QComboBox()
        self._platform.addItems(["anthropic", "google", "openai", "kimi", "glm"])
        _set_combo(self._platform, config.platform)
        self._api_key = QLineEdit(config.api_key)
        self._api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key.setPlaceholderText(_t("settings_placeholder_unchanged"))
        self._model = QLineEdit(config.model)

        af.addRow(_form_label("settings_field_agent_name"), self._agent_name)
        af.addRow(_form_label("settings_field_companion_name"), self._companion_name)
        af.addRow(_form_label("settings_field_platform"), self._platform)
        af.addRow(_form_label("settings_field_api_key"), self._api_key)
        af.addRow(_form_label("settings_field_model"), self._model)
        tabs.addTab(agent_tab, _t("settings_tab_agent"))

        # ── Tab 2: Voice ──────────────────────────────────────────
        voice_tab = QWidget()
        voice_tab.setStyleSheet("background: transparent;")
        vf = QFormLayout(voice_tab)
        _style_form(vf)

        self._el_api_key = QLineEdit(config.tts.elevenlabs_api_key)
        self._el_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._el_api_key.setPlaceholderText(_t("settings_placeholder_unchanged"))
        self._voice_id = QLineEdit(config.tts.voice_id)
        self._tts_output = QComboBox()
        self._tts_output.addItems(["local", "remote", "both"])
        _set_combo(self._tts_output, config.tts.output)
        self._stt_language = QLineEdit(config.stt.language)

        vf.addRow(_form_label("settings_field_elevenlabs_api_key"), self._el_api_key)
        vf.addRow(_form_label("settings_field_voice_id"), self._voice_id)
        vf.addRow(_form_label("settings_field_tts_output"), self._tts_output)
        vf.addRow(_form_label("settings_field_stt_language"), self._stt_language)
        tabs.addTab(voice_tab, _t("settings_tab_voice"))

        # ── Tab 3: Camera ─────────────────────────────────────────
        cam_tab = QWidget()
        cam_tab.setStyleSheet("background: transparent;")
        cf = QFormLayout(cam_tab)
        _style_form(cf)

        self._cam_host = QLineEdit(config.camera.host)
        self._cam_user = QLineEdit(config.camera.username)
        self._cam_pass = QLineEdit(config.camera.password)
        self._cam_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self._cam_pass.setPlaceholderText(_t("settings_placeholder_unchanged"))
        self._cam_port = QLineEdit(str(config.camera.port))

        cf.addRow(_form_label("settings_field_camera_host"), self._cam_host)
        cf.addRow(_form_label("settings_field_camera_username"), self._cam_user)
        cf.addRow(_form_label("settings_field_camera_password"), self._cam_pass)
        cf.addRow(_form_label("settings_field_camera_onvif_port"), self._cam_port)
        tabs.addTab(cam_tab, _t("settings_tab_camera"))

        # ── Tab 4: Advanced ───────────────────────────────────────
        adv_tab = QWidget()
        adv_tab.setStyleSheet("background: transparent;")
        advf = QFormLayout(adv_tab)
        _style_form(advf)

        self._thinking_mode = QComboBox()
        self._thinking_mode.addItems(["auto", "adaptive", "extended", "disabled"])
        _set_combo(self._thinking_mode, config.thinking_mode)
        self._thinking_effort = QComboBox()
        self._thinking_effort.addItems(["low", "medium", "high", "max"])
        _set_combo(self._thinking_effort, config.thinking_effort)
        self._memory_path = QLineEdit(config.memory.db_path)

        advf.addRow(_form_label("settings_field_thinking_mode"), self._thinking_mode)
        advf.addRow(_form_label("settings_field_thinking_effort"), self._thinking_effort)
        advf.addRow(_form_label("settings_field_memory_db_path"), self._memory_path)
        tabs.addTab(adv_tab, _t("settings_tab_advanced"))

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
            QMessageBox.warning(self, _t("settings_save_failed_title"), str(exc))
            return

        QMessageBox.information(
            self,
            _t("settings_saved_title"),
            _t("settings_saved_message"),
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
        self._agent_display_name = (self._agent.config.agent_name or "Agent").strip() or "Agent"
        self._companion_display_name = (self._agent.config.companion_name or "You").strip() or "You"
        self._input_queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._agent_running = False
        self._closing = False
        self._shutdown_requested = False
        self._shutdown_done = False
        self._shutdown_task: asyncio.Task[None] | None = None
        self._cancel_requested = False
        self._agent_task: asyncio.Task[str] | None = None
        self._queue_task: asyncio.Task[None] | None = None
        self._init_task: asyncio.Task[None] | None = None
        self._look_preview_task: asyncio.Task[None] | None = None
        self._look_preview_until: float = 0.0
        self._look_preview_disabled = False
        self._realtime_stt: RealtimeSttSession | None = create_realtime_stt_session()
        self._realtime_stt_task: asyncio.Task[None] | None = None
        self._last_lag_tick = time.perf_counter()
        self._lag_timer = QTimer(self)
        self._lag_timer.setInterval(int(_GUI_LOOP_LAG_CHECK_SEC * 1000))
        self._lag_timer.timeout.connect(self._report_event_loop_lag)
        self._lag_timer.start()

        self.setWindowTitle("familiar-ai")
        self.resize(1020, 720)
        self.setStyleSheet(f"background: {_BG_BASE};")
        self._build_ui()

        self._queue_task = self._create_task(self._process_queue())
        if not self._agent.is_embedding_ready:
            self._init_task = self._create_task(self._show_init_status())
        if self._realtime_stt:
            self._realtime_stt_task = self._create_task(self._start_realtime_stt())

    def _create_task(self, coro) -> asyncio.Task[Any]:
        """Create an asyncio task from GUI sync callbacks safely.

        `asyncio.create_task()` requires a running loop and fails during
        early window construction on some platforms (notably Windows).
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        return loop.create_task(coro)

    @staticmethod
    def _build_rtsp_url(host: str, username: str, password: str) -> str | None:
        """Build RTSP URL from camera config, preserving explicit URI hosts."""
        host = (host or "").strip()
        if not host:
            return None
        if "://" in host:
            return host
        user = quote((username or "").strip(), safe="")
        pw = quote((password or "").strip(), safe="")
        auth = ""
        if user and pw:
            auth = f"{user}:{pw}@"
        elif user:
            auth = f"{user}@"
        return f"rtsp://{auth}{host}:554/stream1"

    def _camera_rtsp_url(self) -> str | None:
        cam = self._agent.config.camera
        return self._build_rtsp_url(cam.host, cam.username, cam.password)

    @staticmethod
    def _look_preview_seconds_for_degrees(degrees: int | None) -> float:
        """Map look degrees to preview duration (short look -> shorter preview)."""
        raw = 30 if degrees is None else degrees
        clamped = max(1, min(90, int(raw)))
        sec = clamped / 45.0
        return max(_GUI_LOOK_PREVIEW_MIN_SEC, min(_GUI_LOOK_PREVIEW_MAX_SEC, sec))

    @staticmethod
    def _extract_jpeg_frames(buffer: bytearray, max_frames: int = 2) -> list[bytes]:
        """Extract complete JPEG frames from a byte buffer and consume them."""
        frames: list[bytes] = []
        while len(frames) < max_frames:
            start = buffer.find(b"\xff\xd8")
            if start < 0:
                if len(buffer) > 1_000_000:
                    buffer.clear()
                break
            if start > 0:
                del buffer[:start]
            end = buffer.find(b"\xff\xd9", 2)
            if end < 0:
                break
            frame = bytes(buffer[: end + 2])
            del buffer[: end + 2]
            frames.append(frame)
        return frames

    def _request_look_preview(self, degrees: int | None = None) -> None:
        """Start/extend a short live preview window for look() actions."""
        if self._look_preview_disabled:
            return
        stream_url = self._camera_rtsp_url()
        if not stream_url:
            return
        duration = self._look_preview_seconds_for_degrees(degrees) + _GUI_LOOK_PREVIEW_GRACE_SEC
        self._look_preview_until = max(self._look_preview_until, time.perf_counter() + duration)
        if self._look_preview_task and not self._look_preview_task.done():
            return
        self._look_preview_task = self._create_task(self._run_look_preview(stream_url))

    async def _run_look_preview(self, stream_url: str) -> None:
        """Render low-FPS RTSP frames while look() is in progress."""
        cmd = [
            "ffmpeg",
            "-loglevel",
            "error",
            "-rtsp_transport",
            "tcp",
            "-fflags",
            "nobuffer",
            "-flags",
            "low_delay",
            "-probesize",
            "32",
            "-analyzeduration",
            "0",
            "-i",
            stream_url,
            "-an",
            "-sn",
            "-vf",
            "scale=640:-1",
            "-r",
            str(_GUI_LOOK_PREVIEW_FPS),
            "-f",
            "image2pipe",
            "-vcodec",
            "mjpeg",
            "-q:v",
            "7",
            "-",
        ]

        proc: asyncio.subprocess.Process | None = None
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            logger.warning("Live look preview disabled: ffmpeg not found")
            self._look_preview_disabled = True
            return
        except Exception as exc:
            logger.debug("Live look preview unavailable: %s", exc)
            return

        assert proc.stdout is not None
        buf = bytearray()
        last_emit = 0.0
        min_interval = 1.0 / max(1, _GUI_LOOK_PREVIEW_FPS)

        try:
            while not self._closing and time.perf_counter() < self._look_preview_until:
                try:
                    chunk = await asyncio.wait_for(
                        proc.stdout.read(4096),
                        timeout=_GUI_LOOK_PREVIEW_READ_TIMEOUT_SEC,
                    )
                except asyncio.TimeoutError:
                    continue
                if not chunk:
                    if proc.returncode is not None:
                        break
                    await asyncio.sleep(0.01)
                    continue

                buf.extend(chunk)
                for frame in self._extract_jpeg_frames(buf, max_frames=2):
                    now = time.perf_counter()
                    if now - last_emit < min_interval:
                        continue
                    self._camera.update_image(base64.b64encode(frame).decode("ascii"))
                    last_emit = now
        finally:
            if proc.returncode is None:
                proc.kill()
                with contextlib.suppress(Exception):
                    await proc.wait()
            self._look_preview_task = None

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
            f"background: {_BG_SURFACE}; border-radius: 16px; border: 1px solid {_BORDER};"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 10, 10, 10)
        header_layout.setSpacing(8)

        title_lbl = QLabel("✦ familiar-ai")
        title_lbl.setStyleSheet(
            f"color: {_ACCENT_DEEP}; font-size: {_px(15)}px; font-weight: 700; background: transparent;"
            f" letter-spacing: -0.02em;"
        )
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        settings_btn = QPushButton(_t("settings_button"))
        settings_btn.setToolTip(_t("settings_button_tooltip"))
        settings_btn.setFixedHeight(48)
        settings_btn.setMinimumWidth(160)
        settings_btn.setStyleSheet(
            f"QPushButton {{ background: #fff2f8; border-radius: 16px;"
            f" border: 1px solid {_BORDER};"
            f" padding: 0 16px; font-size: {_px(12)}px; color: {_TEXT_SECONDARY}; }}"
            f"QPushButton:hover {{ background: #ffe7f2; color: {_TEXT_PRIMARY}; }}"
        )
        settings_btn.clicked.connect(self._open_settings)
        header_layout.addWidget(settings_btn)
        left_layout.addWidget(header)

        # Chat log
        self._log = ChatLog(
            agent_label=self._agent_display_name,
            companion_label=self._companion_display_name,
        )
        left_layout.addWidget(self._log, stretch=5)

        # Stream label
        self._stream = StreamLabel()
        self._stream.setMinimumHeight(110)
        left_layout.addWidget(self._stream, stretch=1)

        # Input row — pill QLineEdit + circular send button
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText(_t("gui_input_placeholder"))
        self._input.setObjectName("msgInput")
        self._input.setStyleSheet(
            f"QLineEdit#msgInput {{"
            f" border-radius: 999px; padding: 10px 20px;"
            f" background: {_BG_SURFACE}; border: 1px solid {_BORDER};"
            f" color: {_TEXT_PRIMARY}; font-size: {_px(13)}px;"
            f" font-family: {_UI_FONT_STACK};"
            f"}}"
            f"QLineEdit#msgInput:focus {{"
            f" border-color: {_ACCENT}; background: #fff8fc;"
            f"}}"
        )
        self._input.returnPressed.connect(self._on_send)
        input_row.addWidget(self._input)

        self._send_btn = QPushButton("⬆")
        self._send_btn.setFixedSize(60, 60)
        self._send_btn.setObjectName("sendBtn")
        self._send_btn.setStyleSheet(
            f"QPushButton#sendBtn {{"
            f" background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f" stop:0 {_ACCENT_DEEP}, stop:1 {_ACCENT});"
            f" border-radius: 30px; border: none;"
            f" font-size: {_px(18)}px; color: white;"
            f"}}"
            f"QPushButton#sendBtn:hover {{"
            f" background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f" stop:0 #ff5f96, stop:1 #ff9fbc);"
            f"}}"
            f"QPushButton#sendBtn:disabled {{"
            f" background: rgba(127,115,148,0.15); color: {_TEXT_SECONDARY};"
            f"}}"
        )
        self._send_btn.clicked.connect(self._on_send)
        input_row.addWidget(self._send_btn)

        self._stop_btn = QPushButton("■")
        self._stop_btn.setFixedSize(60, 60)
        self._stop_btn.setObjectName("stopBtn")
        self._stop_btn.setToolTip(_t("gui_cancel_turn_tooltip"))
        self._stop_btn.setStyleSheet(
            f"QPushButton#stopBtn {{"
            f" background: rgba(255,107,115,0.20);"
            f" border-radius: 30px; border: 1px solid rgba(255,107,115,0.52);"
            f" font-size: {_px(14)}px; color: #e34f5d;"
            f"}}"
            f"QPushButton#stopBtn:hover {{"
            f" background: rgba(255,107,115,0.30); color: #c13f4d;"
            f"}}"
            f"QPushButton#stopBtn:disabled {{"
            f" background: rgba(127,115,148,0.12); color: {_TEXT_SECONDARY};"
            f" border-color: rgba(127,115,148,0.20);"
            f"}}"
        )
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._on_cancel_clicked)
        input_row.addWidget(self._stop_btn)
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
            f"background: {_BG_ELEVATED}; border-radius: 18px; border: 1px solid {_BORDER};"
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
        splitter.setStyleSheet(
            "QSplitter::handle { background: rgba(255,169,192,0.42); width: 2px; }"
        )
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
        self._stream.clear_status()
        self._log.append_line(f"[{self._companion_display_name}] {text}")
        self._input_queue.put_nowait(text)
        qsize = self._input_queue.qsize()
        if qsize >= _GUI_QUEUE_WARN_SIZE:
            logger.warning("GUI input queue backlog: %d", qsize)
        else:
            logger.debug("GUI input queued (size=%d)", qsize)

    def _on_realtime_stt_partial(self, text: str) -> None:
        """Display partial STT transcript while idle."""
        if self._closing:
            return
        partial = text.strip()
        if not partial:
            return
        if self._agent_running or self._stream.has_content():
            return
        self._stream.set_status(f"🎤 {partial}")

    def _on_realtime_stt_committed(self, text: str) -> None:
        """Display committed STT transcript as a user message bubble."""
        if self._closing:
            return
        spoken = text.strip()
        if not spoken:
            return
        self._stream.clear_status()
        self._log.append_line(f"[{self._companion_display_name}] {spoken}")

    async def _start_realtime_stt(self) -> None:
        """Initialize realtime STT and feed transcripts into the GUI input queue."""
        assert self._realtime_stt is not None
        try:
            loop = asyncio.get_event_loop()
            self._realtime_stt.on_partial = self._on_realtime_stt_partial
            self._realtime_stt.on_committed = self._on_realtime_stt_committed
            await self._realtime_stt.start(loop, self._input_queue)
            self._log.append_line("🎤 Realtime STT ON (ElevenLabs)")
        except Exception as exc:
            logger.warning("Realtime STT init failed: %s", exc)
            self._log.append_line(f"[error] Realtime STT init failed: {exc}")
            self._realtime_stt = None

    def _on_cancel_clicked(self) -> None:
        self._cancel_turn(reason="user")

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.key() == Qt.Key.Key_Escape:
            self._cancel_turn(reason="user")
            event.accept()
            return
        super().keyPressEvent(event)

    def _cancel_turn(self, reason: str = "user") -> None:
        """Cancel current turn if running.

        reason: "user" (explicit cancel) or "shutdown" (window/app exit).
        """
        if not self._agent_running:
            return
        self._cancel_requested = True
        if self._agent_task and not self._agent_task.done():
            self._agent_task.cancel()
        if reason == "user":
            self._log.append_line("[interrupted]")
        logger.info("GUI turn cancel requested (%s), queue=%d", reason, self._input_queue.qsize())

    def _set_turn_ui_state(self, running: bool) -> None:
        self._stop_btn.setEnabled(running)

    def _thinking_status_text(self, elapsed_sec: int) -> str:
        """Status line shown while waiting for the first response chunk."""
        return _t(
            "thinking_status",
            name=self._agent_display_name,
            seconds=str(elapsed_sec),
        )

    @staticmethod
    def _startup_status_text(elapsed_sec: int) -> str:
        """Status line shown while first-turn startup work is in progress."""
        return f"{_t('initializing')}... ({elapsed_sec}s)"

    # ------------------------------------------------------------------
    # Agent loop
    # ------------------------------------------------------------------

    async def _process_queue(self) -> None:
        """Dequeue user messages and run the agent; fire desires when idle."""
        last_interaction = time.time()
        while True:
            try:
                text = await asyncio.wait_for(self._input_queue.get(), timeout=IDLE_CHECK_INTERVAL)
            except asyncio.TimeoutError:
                now = time.time()
                if self._closing:
                    continue
                if not should_fire_idle_desire(
                    agent_running=self._agent_running,
                    has_pending_input=not self._input_queue.empty(),
                    last_interaction=last_interaction,
                    now=now,
                    cooldown=DESIRE_COOLDOWN,
                ):
                    continue

                tick = desire_tick_prompt(self._desires, [])
                if tick:
                    # If user input arrived meanwhile, prioritize that over autonomous desire.
                    if not self._input_queue.empty():
                        continue
                    desire_name, prompt, _ = tick
                    try:
                        murmur = _t(f"desire_{desire_name}")
                    except KeyError:
                        murmur = _t("desire_default")
                    self._log.append_line(murmur)
                    await self._run_agent("", inner_voice=prompt)
                    self._desires.satisfy(desire_name)
                    self._desires.curiosity_target = None
                    last_interaction = time.time()
                continue

            if text is None:
                break
            last_interaction = time.time()
            logger.debug(
                "GUI dequeued input (remaining queue=%d, running=%s)",
                self._input_queue.qsize(),
                self._agent_running,
            )
            await self._run_agent(text)

    async def _run_agent(self, user_input: str, inner_voice: str = "") -> None:
        turn_started = time.perf_counter()
        self._agent_running = True
        self._cancel_requested = False
        self._set_turn_ui_state(True)
        logger.info(
            "GUI turn start (user_input=%d chars, inner_voice=%s, queue=%d)",
            len(user_input),
            bool(inner_voice),
            self._input_queue.qsize(),
        )

        phase = (
            "startup"
            if (getattr(self._agent, "_turn_count", 0) == 0 or not self._agent.is_embedding_ready)
            else "thinking"
        )
        phase_started = time.perf_counter()
        thinking_timer = QTimer(self)
        thinking_timer.setInterval(200)

        def _update_thinking_status() -> None:
            nonlocal phase_started
            if self._stream.has_content():
                return
            elapsed = int(time.perf_counter() - phase_started)
            if phase == "startup":
                self._stream.set_status(self._startup_status_text(elapsed))
            else:
                self._stream.set_status(self._thinking_status_text(elapsed))

        thinking_timer.timeout.connect(_update_thinking_status)
        _update_thinking_status()
        thinking_timer.start()

        def on_phase(new_phase: str) -> None:
            nonlocal phase, phase_started
            if new_phase not in {"startup", "thinking"}:
                return
            if phase == new_phase:
                return
            phase = new_phase
            phase_started = time.perf_counter()
            if not self._stream.has_content():
                _update_thinking_status()

        def on_text(chunk: str) -> None:
            self._stream.clear_status()
            self._stream.append_chunk(chunk)

        def on_action(name: str, tool_input: dict) -> None:
            committed = self._stream.commit_and_clear()
            if committed.strip():
                self._log.append_line(f"[{self._agent_display_name}] {committed.strip()}")
            self._log.append_action(name, tool_input)
            if name == "look":
                self._request_look_preview(tool_input.get("degrees"))

        def on_image(b64: str) -> None:
            self._camera.update_image(b64)

        try:
            self._agent_task = self._create_task(
                self._agent.run(
                    user_input,
                    on_action=on_action,
                    on_text=on_text,
                    on_image=on_image,
                    on_phase=on_phase,
                    desires=self._desires,
                    inner_voice=inner_voice,
                    interrupt_queue=self._input_queue,
                )
            )
            final_text = await self._agent_task
            committed = self._stream.commit_and_clear()
            display = committed.strip() or final_text.strip()
            if display:
                self._log.append_line(f"[{self._agent_display_name}] {display}")
        except asyncio.CancelledError:
            self._stream.commit_and_clear()
            if not self._cancel_requested:
                self._log.append_line("[interrupted]")
        except Exception as exc:
            logger.exception("Agent run error")
            self._log.append_line(f"[error] {exc}")
        finally:
            thinking_timer.stop()
            self._stream.clear_status()
            self._agent_task = None
            self._agent_running = False
            self._set_turn_ui_state(False)
            logger.info(
                "GUI turn end (duration=%.2fs, cancelled=%s, queue=%d)",
                time.perf_counter() - turn_started,
                self._cancel_requested,
                self._input_queue.qsize(),
            )
            self._cancel_requested = False

    async def _show_init_status(self) -> None:
        """Update window title with elapsed time until embedding model is ready."""
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
        if self._shutdown_done:
            event.accept()
            return
        if self._shutdown_requested:
            event.ignore()
            return
        self._shutdown_requested = True
        self._closing = True
        self.setEnabled(False)
        self.setWindowTitle("familiar-ai  ⏳ shutting down...")
        self._ensure_shutdown_task()
        event.ignore()

    def _ensure_shutdown_task(self) -> asyncio.Task[None]:
        if self._shutdown_task and not self._shutdown_task.done():
            return self._shutdown_task
        self._shutdown_task = self._create_task(self._shutdown())
        self._shutdown_task.add_done_callback(lambda _task: self._finalize_close())
        return self._shutdown_task

    def _finalize_close(self) -> None:
        if not self._shutdown_done:
            return
        self.close()

    def _report_event_loop_lag(self) -> None:
        now = time.perf_counter()
        elapsed = now - self._last_lag_tick
        self._last_lag_tick = now
        lag = elapsed - _GUI_LOOP_LAG_CHECK_SEC
        if lag > _GUI_LOOP_LAG_WARN_SEC:
            logger.warning(
                "GUI event-loop lag detected: %.3fs (queue=%d running=%s)",
                lag,
                self._input_queue.qsize(),
                self._agent_running,
            )

    async def _shutdown(self) -> None:
        """Best-effort async cleanup on window close."""
        self._lag_timer.stop()
        self._cancel_turn(reason="shutdown")
        if self._realtime_stt_task and not self._realtime_stt_task.done():
            self._realtime_stt_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._realtime_stt_task
        self._realtime_stt_task = None
        if self._realtime_stt:
            with contextlib.suppress(asyncio.TimeoutError, Exception):
                await asyncio.wait_for(self._realtime_stt.stop(), timeout=2.0)
            self._realtime_stt = None
        if self._look_preview_task and not self._look_preview_task.done():
            self._look_preview_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._look_preview_task
        self._input_queue.put_nowait(None)
        if self._queue_task and not self._queue_task.done():
            self._queue_task.cancel()
        if self._init_task and not self._init_task.done():
            self._init_task.cancel()
        try:
            if self._agent_task and not self._agent_task.done():
                try:
                    await asyncio.wait_for(asyncio.shield(self._agent_task), timeout=1.0)
                except (asyncio.TimeoutError, asyncio.CancelledError, Exception):
                    pass
            await asyncio.wait_for(self._agent.close(), timeout=3.0)
        except (asyncio.TimeoutError, Exception):
            pass
        self._shutdown_done = True


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
    qt_app.aboutToQuit.connect(window._ensure_shutdown_task)

    with loop:
        loop.run_forever()
