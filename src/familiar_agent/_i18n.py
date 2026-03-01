"""Locale detection and string translations for familiar-ai."""

from __future__ import annotations

import locale
import os

__all__ = ["_LANG", "_t", "BANNER"]

_VERSION = "v0.1"


def _detect_lang() -> str:
    """Return a language code: 'ja', 'zh', 'zh-tw', 'fr', 'de', or 'en'."""
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
    # Traditional Chinese: zh_TW, zh_HK, zh_MO — must check before generic zh
    if any(lang.startswith(p) for p in ("zh_TW", "zh_HK", "zh_MO", "zh-TW", "zh-HK", "zh-MO")):
        return "zh-tw"
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
        "zh-tw": "陪伴在你身邊的AI 🐾",
        "fr": "L'IA qui vit à vos côtés 🐾",
        "de": "KI, die bei dir lebt 🐾",
        "en": "AI that lives alongside you 🐾",
    },
    # ── TUI ──────────────────────────────────────────────────────────
    "startup": {
        "ja": "familiar-ai 起動。/quit で終了、Ctrl+L で履歴クリア。ログ: {log_path}",
        "zh": "familiar-ai 已启动。输入 /quit 退出，Ctrl+L 清除历史。日志: {log_path}",
        "zh-tw": "familiar-ai 已啟動。輸入 /quit 退出，Ctrl+L 清除歷史。日誌: {log_path}",
        "fr": "familiar-ai démarré. /quit pour quitter, Ctrl+L pour effacer. Journal : {log_path}",
        "de": "familiar-ai gestartet. /quit zum Beenden, Ctrl+L zum Löschen. Log: {log_path}",
        "en": "familiar-ai started. /quit to exit, Ctrl+L to clear history. Log: {log_path}",
    },
    "history_cleared": {
        "ja": "── 履歴クリア ──",
        "zh": "── 历史已清除 ──",
        "zh-tw": "── 歷史已清除 ──",
        "fr": "── historique effacé ──",
        "de": "── Verlauf gelöscht ──",
        "en": "── history cleared ──",
    },
    "input_placeholder": {
        "ja": "メッセージ > ",
        "zh": "消息 > ",
        "zh-tw": "訊息 > ",
        "fr": "message > ",
        "de": "Nachricht > ",
        "en": "message > ",
    },
    "quit_label": {
        "ja": "終了",
        "zh": "退出",
        "zh-tw": "退出",
        "fr": "Quitter",
        "de": "Beenden",
        "en": "Quit",
    },
    "clear_label": {
        "ja": "履歴クリア",
        "zh": "清除历史",
        "zh-tw": "清除歷史",
        "fr": "Effacer",
        "de": "Löschen",
        "en": "Clear history",
    },
    # ── REPL ─────────────────────────────────────────────────────────
    "repl_commands": {
        "ja": "コマンド: /clear 履歴クリア  /quit 終了",
        "zh": "命令: /clear 清除历史  /quit 退出",
        "zh-tw": "指令: /clear 清除歷史  /quit 退出",
        "fr": "Commandes : /clear effacer  /quit quitter",
        "de": "Befehle: /clear Verlauf löschen  /quit Beenden",
        "en": "Commands: /clear history  /quit exit",
    },
    "repl_history_cleared": {
        "ja": "履歴をクリアしました。",
        "zh": "历史已清除。",
        "zh-tw": "歷史已清除。",
        "fr": "Historique effacé.",
        "de": "Verlauf gelöscht.",
        "en": "History cleared.",
    },
    "repl_goodbye": {
        "ja": "またね。",
        "zh": "再见。",
        "zh-tw": "再見。",
        "fr": "Au revoir.",
        "de": "Tschüss.",
        "en": "Goodbye.",
    },
    # ── Desire murmurs ───────────────────────────────────────────────
    "desire_look_around": {
        "ja": "なんか外が気になってきた…",
        "zh": "突然想看看外面…",
        "zh-tw": "突然想看看外面…",
        "fr": "j'ai envie de regarder dehors…",
        "de": "ich bin neugierig, was draußen passiert…",
        "en": "feeling curious about outside…",
    },
    "desire_explore": {
        "ja": "ちょっと動きたくなってきたな…",
        "zh": "想动动了…",
        "zh-tw": "想動動了…",
        "fr": "j'ai envie de bouger un peu…",
        "de": "ich möchte mich etwas bewegen…",
        "en": "feeling like moving around…",
    },
    "desire_greet_companion": {
        "ja": "誰かいるかな…",
        "zh": "有人在吗…",
        "zh-tw": "有人在嗎…",
        "fr": "je me demande si quelqu'un est là…",
        "de": "ich frage mich, ob jemand da ist…",
        "en": "wondering if someone's around…",
    },
    "desire_rest": {
        "ja": "少し休憩しよかな…",
        "zh": "想休息一下…",
        "zh-tw": "想休息一下…",
        "fr": "j'ai envie de me reposer un peu…",
        "de": "ich möchte mich kurz ausruhen…",
        "en": "feeling like resting a bit…",
    },
    # ── REPL action display ──────────────────────────────────────────
    "action_see": {
        "ja": "👀 見てる...",
        "zh": "👀 看着...",
        "zh-tw": "👀 看著...",
        "fr": "👀 regarde...",
        "de": "👀 schaut...",
        "en": "👀 looking...",
    },
    "action_look": {
        "ja": "↩️  向いてる...",
        "zh": "↩️  转向...",
        "zh-tw": "↩️  轉向...",
        "fr": "↩️  tourne...",
        "de": "↩️  dreht...",
        "en": "↩️  turning...",
    },
    "action_walk": {
        "ja": "🚶 歩いてる...",
        "zh": "🚶 走动中...",
        "zh-tw": "🚶 走動中...",
        "fr": "🚶 marche...",
        "de": "🚶 geht...",
        "en": "🚶 walking...",
    },
    "action_say": {
        "ja": "💬 しゃべってる...",
        "zh": "💬 说话中...",
        "zh-tw": "💬 說話中...",
        "fr": "💬 parle...",
        "de": "💬 spricht...",
        "en": "💬 speaking...",
    },
    "action_remember": {
        "ja": "💾 記憶してる...",
        "zh": "💾 记忆中...",
        "zh-tw": "💾 記憶中...",
        "fr": "💾 mémorise...",
        "de": "💾 merkt sich...",
        "en": "💾 remembering...",
    },
    "look_left": {
        "ja": "左を向いた",
        "zh": "向左看",
        "zh-tw": "向左看",
        "fr": "tourne à gauche",
        "de": "dreht links",
        "en": "looked left",
    },
    "look_right": {
        "ja": "右を向いた",
        "zh": "向右看",
        "zh-tw": "向右看",
        "fr": "tourne à droite",
        "de": "dreht rechts",
        "en": "looked right",
    },
    "look_up": {
        "ja": "上を向いた",
        "zh": "向上看",
        "zh-tw": "向上看",
        "fr": "regarde en haut",
        "de": "schaut hoch",
        "en": "looked up",
    },
    "look_down": {
        "ja": "下を向いた",
        "zh": "向下看",
        "zh-tw": "向下看",
        "fr": "regarde en bas",
        "de": "schaut runter",
        "en": "looked down",
    },
    "look_around": {
        "ja": "見回してる",
        "zh": "环顾四周",
        "zh-tw": "環顧四周",
        "fr": "regarde autour",
        "de": "schaut sich um",
        "en": "looking around",
    },
    "walk_timed": {
        "ja": "{direction}に{duration}秒...",
        "zh": "向{direction}{duration}秒...",
        "zh-tw": "向{direction}{duration}秒...",
        "fr": "vers {direction} {duration}s...",
        "de": "{direction} für {duration}s...",
        "en": "{direction} for {duration}s...",
    },
    "walk_dir": {
        "ja": "{direction}へ...",
        "zh": "向{direction}...",
        "zh-tw": "向{direction}...",
        "fr": "vers {direction}...",
        "de": "nach {direction}...",
        "en": "to {direction}...",
    },
    "desire_default": {
        "ja": "ちょっと気になることがあって…",
        "zh": "有点在意的事…",
        "zh-tw": "有點在意的事…",
        "fr": "quelque chose attire mon attention…",
        "de": "etwas hat meine Aufmerksamkeit geweckt…",
        "en": "something caught my attention…",
    },
    # ── Agent internal prompts (injected into LLM context) ───────────
    "inner_voice_label": {
        "ja": "[今の気持ち — 一緒に暮らす人の発言ではなく、自分自身の内的衝動]",
        "zh": "[此刻的感受 — 这是自己内心的冲动，不是同住之人说的话]",
        "zh-tw": "[此刻的感受 — 這是自己內心的衝動，不是同住之人說的話]",
        "fr": "[Ressenti intérieur — une impulsion personnelle, pas un message de la personne avec qui je vis]",
        "de": "[Inneres Gefühl — ein eigener Impuls, keine Aussage der Person, mit der ich lebe]",
        "en": "[My current feeling — my own inner impulse, not a message from the person I live with]",
    },
    "inner_voice_directive": {
        "ja": "→ これは自分の内的衝動。返事は不要。衝動に従って行動するだけでいい。",
        "zh": "→ 这是内心冲动。无需回应任何人——只需按冲动行事。",
        "zh-tw": "→ 這是內心衝動。無需回應任何人——只需按衝動行事。",
        "fr": "→ C'est une impulsion intérieure. Pas besoin de répondre — il suffit d'agir selon l'impulsion.",
        "de": "→ Das ist ein innerer Impuls. Keine Antwort nötig — einfach dem Impuls folgen.",
        "en": "→ This is an internal drive. No need to respond to anyone — just act on the impulse.",
    },
    "desire_turn_marker": {
        "ja": "（内的衝動に従って行動）",
        "zh": "（按内心冲动行事）",
        "zh-tw": "（按內心衝動行事）",
        "fr": "(agir selon l'impulsion intérieure)",
        "de": "(dem inneren Impuls folgen)",
        "en": "(acting on internal impulse)",
    },
    "summary_lang": {
        "ja": "日本語",
        "zh": "中文",
        "zh-tw": "繁體中文",
        "fr": "français",
        "de": "Deutsch",
        "en": "English",
    },
    "curiosity_none": {
        "ja": "なし",
        "zh": "无",
        "zh-tw": "無",
        "fr": "rien",
        "de": "nichts",
        "en": "none",
    },
    # Default companion name when COMPANION_NAME is not set
    "default_companion_name": {
        "ja": "ユウト",
        "zh": "小明",
        "zh-tw": "小明",
        "fr": "Lucas",
        "de": "Lukas",
        "en": "Alex",
    },
    # Morning reconstruction — autobiographical self bridge
    "morning_no_history": {
        "ja": "[これは最初のセッション。過去の記憶はまだない。比較や昨日よりという表現は使わないこと。]",
        "zh": "[这是第一次会话。还没有过去的记忆。不要使用与昨天相比这样的表达。]",
        "zh-tw": "[這是第一次會話。還沒有過去的記憶。不要使用與昨天相比這樣的表達。]",
        "fr": "[C'est la premiere session. Aucun souvenir passe pour l'instant. Ne pas utiliser de comparaisons avec hier.]",
        "de": "[Dies ist die erste Sitzung. Es gibt noch keine vergangenen Erinnerungen. Keine Vergleiche mit gestern verwenden.]",
        "en": "[This is the first session. No past memories yet. Do not use comparisons or expressions like 'more than yesterday'.]",
    },
    "morning_header": {
        "ja": "[昨日からのうち — セッションをまたいで続く自分]:",
        "zh": "[来自昨天的我——跨越会话延续的自我]：",
        "zh-tw": "[來自昨天的我——跨越會話延續的自我]：",
        "fr": "[Moi depuis hier — le soi qui continue à travers les sessions] :",
        "de": "[Ich von gestern — das Selbst, das über Sitzungen hinweg weiterbesteht]:",
        "en": "[Me from yesterday — the self that continues across sessions]:",
    },
}


def _t(key: str, **kwargs: str) -> str:
    return _T[key].get(_LANG, _T[key]["en"]).format(**kwargs)


def _make_banner(include_commands: bool = True) -> str:
    """Build a startup banner. CJK/emoji go outside the ASCII box to avoid width issues."""
    subtitle = _t("banner_subtitle")
    lines = [
        "🦉  Familiar AI",
        "╔══════════════════════════════════════╗",
        f"║  version {_VERSION:<29}║",
        "╚══════════════════════════════════════╝",
        f"  {subtitle}",
    ]
    if include_commands:
        lines.append(f"  {_t('repl_commands')}")
    return "\n".join(lines) + "\n"


BANNER = _make_banner()
