"""Locale detection and string translations for familiar-ai."""

from __future__ import annotations

import locale
import os

__all__ = ["_LANG", "_t", "BANNER"]

_VERSION = "v0.1"


def _detect_lang() -> str:
    """Return a language code: 'ja', 'zh', 'fr', 'de', or 'en'."""
    raw = (
        os.environ.get("LANGUAGE")
        or os.environ.get("LC_ALL")
        or os.environ.get("LC_MESSAGES")
        or os.environ.get("LANG")
        or locale.getlocale()[0]
        or ""
    )
    lang = raw.split(":")[0]  # LANGUAGE can be colon-separated list
    if lang.startswith("ja"):
        return "ja"
    if lang.startswith("zh"):
        return "zh"
    if lang.startswith("fr"):
        return "fr"
    if lang.startswith("de"):
        return "de"
    return "en"


_LANG = _detect_lang()

_T: dict[str, dict[str, str]] = {
    # ── Banner ───────────────────────────────────────────────────────
    "banner_subtitle": {
        "ja": "あなたのそばに暮らすAI 🐾",
        "zh": "陪伴在你身边的AI 🐾",
        "fr": "L'IA qui vit à vos côtés 🐾",
        "de": "KI, die bei dir lebt 🐾",
        "en": "AI that lives alongside you 🐾",
    },
    # ── TUI ──────────────────────────────────────────────────────────
    "startup": {
        "ja": "familiar-ai 起動。/quit で終了、Ctrl+L で履歴クリア。ログ: {log_path}",
        "zh": "familiar-ai 已启动。输入 /quit 退出，Ctrl+L 清除历史。日志: {log_path}",
        "fr": "familiar-ai démarré. /quit pour quitter, Ctrl+L pour effacer. Journal : {log_path}",
        "de": "familiar-ai gestartet. /quit zum Beenden, Ctrl+L zum Löschen. Log: {log_path}",
        "en": "familiar-ai started. /quit to exit, Ctrl+L to clear history. Log: {log_path}",
    },
    "history_cleared": {
        "ja": "── 履歴クリア ──",
        "zh": "── 历史已清除 ──",
        "fr": "── historique effacé ──",
        "de": "── Verlauf gelöscht ──",
        "en": "── history cleared ──",
    },
    "input_placeholder": {
        "ja": "メッセージ > ",
        "zh": "消息 > ",
        "fr": "message > ",
        "de": "Nachricht > ",
        "en": "message > ",
    },
    "quit_label": {
        "ja": "終了",
        "zh": "退出",
        "fr": "Quitter",
        "de": "Beenden",
        "en": "Quit",
    },
    "clear_label": {
        "ja": "履歴クリア",
        "zh": "清除历史",
        "fr": "Effacer",
        "de": "Löschen",
        "en": "Clear history",
    },
    # ── REPL ─────────────────────────────────────────────────────────
    "repl_commands": {
        "ja": "コマンド: /clear 履歴クリア  /quit 終了",
        "zh": "命令: /clear 清除历史  /quit 退出",
        "fr": "Commandes : /clear effacer  /quit quitter",
        "de": "Befehle: /clear Verlauf löschen  /quit Beenden",
        "en": "Commands: /clear history  /quit exit",
    },
    "repl_history_cleared": {
        "ja": "履歴をクリアしました。",
        "zh": "历史已清除。",
        "fr": "Historique effacé.",
        "de": "Verlauf gelöscht.",
        "en": "History cleared.",
    },
    "repl_goodbye": {
        "ja": "またね。",
        "zh": "再见。",
        "fr": "Au revoir.",
        "de": "Tschüss.",
        "en": "Goodbye.",
    },
    # ── Desire murmurs ───────────────────────────────────────────────
    "desire_look_around": {
        "ja": "なんか外が気になってきた…",
        "zh": "突然想看看外面…",
        "fr": "j'ai envie de regarder dehors…",
        "de": "ich bin neugierig, was draußen passiert…",
        "en": "feeling curious about outside…",
    },
    "desire_explore": {
        "ja": "ちょっと動きたくなってきたな…",
        "zh": "想动动了…",
        "fr": "j'ai envie de bouger un peu…",
        "de": "ich möchte mich etwas bewegen…",
        "en": "feeling like moving around…",
    },
    "desire_greet_companion": {
        "ja": "誰かいるかな…",
        "zh": "有人在吗…",
        "fr": "je me demande si quelqu'un est là…",
        "de": "ich frage mich, ob jemand da ist…",
        "en": "wondering if someone's around…",
    },
    "desire_rest": {
        "ja": "少し休憩しよかな…",
        "zh": "想休息一下…",
        "fr": "j'ai envie de me reposer un peu…",
        "de": "ich möchte mich kurz ausruhen…",
        "en": "feeling like resting a bit…",
    },
    "desire_default": {
        "ja": "ちょっと気になることがあって…",
        "zh": "有点在意的事…",
        "fr": "quelque chose attire mon attention…",
        "de": "etwas hat meine Aufmerksamkeit geweckt…",
        "en": "something caught my attention…",
    },
}


def _t(key: str, **kwargs: str) -> str:
    return _T[key].get(_LANG, _T[key]["en"]).format(**kwargs)


def _make_banner(include_commands: bool = True) -> str:
    """Build a startup banner. CJK/emoji go outside the ASCII box to avoid width issues."""
    subtitle = _t("banner_subtitle")
    lines = [
        "╔══════════════════════════════════════╗",
        f"║          Familiar AI  {_VERSION:<15}║",
        "╚══════════════════════════════════════╝",
        f"  {subtitle}",
    ]
    if include_commands:
        lines.append(f"  {_t('repl_commands')}")
    return "\n".join(lines) + "\n"


BANNER = _make_banner()
