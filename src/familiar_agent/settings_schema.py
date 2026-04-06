"""Single source of truth for familiar-ai setup/settings fields."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .config import AgentConfig


@dataclass
class SetupConfig:
    """Unified settings shared by setup wizard and GUI settings."""

    platform: str = "anthropic"
    api_key: str = ""
    model: str = ""
    base_url: str = ""
    tools_mode: str = ""

    agent_name: str = ""
    companion_name: str = ""
    thinking_mode: str = ""
    thinking_effort: str = ""
    memory_db_path: str = ""

    utility_platform: str = ""
    utility_api_key: str = ""
    utility_model: str = ""

    scene_platform: str = ""
    scene_api_key: str = ""
    scene_model: str = ""

    camera_host: str = ""
    camera_username: str = ""
    camera_password: str = ""
    camera_onvif_port: str = "2020"
    camera_ptz_host: str = ""
    camera_ptz_username: str = ""
    camera_ptz_password: str = ""
    camera_ptz_port: str = ""

    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    tts_output: str = "local"
    realtime_stt: bool = False
    stt_language: str = "ja"

    auto_desire: bool = False
    auto_say: bool = True


Validator = Callable[[Any], str | None]
RuntimeGetter = Callable[["AgentConfig"], Any]


def _validate_optional_port(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        port = int(text)
    except ValueError:
        return "Port must be an integer."
    if port < 1 or port > 65535:
        return "Port must be between 1 and 65535."
    return None


@dataclass(frozen=True)
class SettingField:
    """Metadata for one editable setting field."""

    env_key: str
    attr: str
    section: str
    label: str
    widget: str
    default: str | bool
    options: tuple[str, ...] = ()
    secret: bool = False
    placeholder_key: str | None = None
    validator: Validator | None = None
    setup_visible: bool = True
    runtime_getter: RuntimeGetter | None = None


SECTION_ORDER = ("agent", "voice", "camera", "advanced")
SECTION_LABELS = {
    "agent": "settings_tab_agent",
    "voice": "settings_tab_voice",
    "camera": "settings_tab_camera",
    "advanced": "settings_tab_advanced",
}


SETTINGS_FIELDS: tuple[SettingField, ...] = (
    SettingField(
        env_key="AGENT_NAME",
        attr="agent_name",
        section="agent",
        label="settings_field_agent_name",
        widget="text",
        default="",
        runtime_getter=lambda config: config.agent_name,
    ),
    SettingField(
        env_key="COMPANION_NAME",
        attr="companion_name",
        section="agent",
        label="settings_field_companion_name",
        widget="text",
        default="",
        runtime_getter=lambda config: config.companion_name,
    ),
    SettingField(
        env_key="PLATFORM",
        attr="platform",
        section="agent",
        label="settings_field_platform",
        widget="combo",
        default="anthropic",
        options=("anthropic", "gemini", "openai", "kimi", "glm", "cli"),
        runtime_getter=lambda config: config.platform,
    ),
    SettingField(
        env_key="API_KEY",
        attr="api_key",
        section="agent",
        label="settings_field_api_key",
        widget="password",
        default="",
        secret=True,
        placeholder_key="settings_placeholder_unchanged",
        runtime_getter=lambda config: config.api_key,
    ),
    SettingField(
        env_key="MODEL",
        attr="model",
        section="agent",
        label="settings_field_model",
        widget="text",
        default="",
        runtime_getter=lambda config: config.model,
    ),
    SettingField(
        env_key="BASE_URL",
        attr="base_url",
        section="agent",
        label="Base URL:",
        widget="text",
        default="",
        runtime_getter=lambda config: config.base_url,
    ),
    SettingField(
        env_key="TOOLS_MODE",
        attr="tools_mode",
        section="agent",
        label="Tools mode:",
        widget="combo",
        default="",
        options=("", "prompt", "native"),
        runtime_getter=lambda config: config.tools_mode,
    ),
    SettingField(
        env_key="ELEVENLABS_API_KEY",
        attr="elevenlabs_api_key",
        section="voice",
        label="settings_field_elevenlabs_api_key",
        widget="password",
        default="",
        secret=True,
        placeholder_key="settings_placeholder_unchanged",
        runtime_getter=lambda config: config.tts.elevenlabs_api_key,
    ),
    SettingField(
        env_key="ELEVENLABS_VOICE_ID",
        attr="elevenlabs_voice_id",
        section="voice",
        label="settings_field_voice_id",
        widget="text",
        default="",
        runtime_getter=lambda config: config.tts.voice_id,
    ),
    SettingField(
        env_key="TTS_OUTPUT",
        attr="tts_output",
        section="voice",
        label="settings_field_tts_output",
        widget="combo",
        default="local",
        options=("local", "remote", "both"),
        runtime_getter=lambda config: config.tts.output,
    ),
    SettingField(
        env_key="REALTIME_STT",
        attr="realtime_stt",
        section="voice",
        label="Realtime STT:",
        widget="bool",
        default=False,
        runtime_getter=lambda config: bool(getattr(config, "realtime_stt", False)),
    ),
    SettingField(
        env_key="STT_LANGUAGE",
        attr="stt_language",
        section="voice",
        label="settings_field_stt_language",
        widget="text",
        default="ja",
        runtime_getter=lambda config: config.stt.language,
    ),
    SettingField(
        env_key="CAMERA_HOST",
        attr="camera_host",
        section="camera",
        label="settings_field_camera_host",
        widget="text",
        default="",
        setup_visible=False,
        runtime_getter=lambda config: config.camera.host,
    ),
    SettingField(
        env_key="CAMERA_USERNAME",
        attr="camera_username",
        section="camera",
        label="settings_field_camera_username",
        widget="text",
        default="",
        setup_visible=False,
        runtime_getter=lambda config: config.camera.username,
    ),
    SettingField(
        env_key="CAMERA_PASSWORD",
        attr="camera_password",
        section="camera",
        label="settings_field_camera_password",
        widget="password",
        default="",
        secret=True,
        placeholder_key="settings_placeholder_unchanged",
        setup_visible=False,
        runtime_getter=lambda config: config.camera.password,
    ),
    SettingField(
        env_key="CAMERA_ONVIF_PORT",
        attr="camera_onvif_port",
        section="camera",
        label="settings_field_camera_onvif_port",
        widget="text",
        default="2020",
        validator=_validate_optional_port,
        setup_visible=False,
        runtime_getter=lambda config: str(config.camera.port),
    ),
    SettingField(
        env_key="CAMERA_PTZ_HOST",
        attr="camera_ptz_host",
        section="camera",
        label="PTZ host override:",
        widget="text",
        default="",
        setup_visible=False,
        runtime_getter=lambda config: config.camera.ptz_host_override,
    ),
    SettingField(
        env_key="CAMERA_PTZ_USERNAME",
        attr="camera_ptz_username",
        section="camera",
        label="PTZ username override:",
        widget="text",
        default="",
        setup_visible=False,
        runtime_getter=lambda config: config.camera.ptz_username_override,
    ),
    SettingField(
        env_key="CAMERA_PTZ_PASSWORD",
        attr="camera_ptz_password",
        section="camera",
        label="PTZ password override:",
        widget="password",
        default="",
        secret=True,
        placeholder_key="settings_placeholder_unchanged",
        setup_visible=False,
        runtime_getter=lambda config: config.camera.ptz_password_override,
    ),
    SettingField(
        env_key="CAMERA_PTZ_PORT",
        attr="camera_ptz_port",
        section="camera",
        label="PTZ port override:",
        widget="text",
        default="",
        validator=_validate_optional_port,
        setup_visible=False,
        runtime_getter=lambda config: (
            str(config.camera.ptz_port_override)
            if config.camera.ptz_port_override is not None
            else ""
        ),
    ),
    SettingField(
        env_key="THINKING_MODE",
        attr="thinking_mode",
        section="advanced",
        label="settings_field_thinking_mode",
        widget="combo",
        default="auto",
        options=("auto", "adaptive", "extended", "disabled"),
        setup_visible=False,
        runtime_getter=lambda config: config.thinking_mode,
    ),
    SettingField(
        env_key="THINKING_EFFORT",
        attr="thinking_effort",
        section="advanced",
        label="settings_field_thinking_effort",
        widget="combo",
        default="high",
        options=("low", "medium", "high", "max"),
        setup_visible=False,
        runtime_getter=lambda config: config.thinking_effort,
    ),
    SettingField(
        env_key="UTILITY_PLATFORM",
        attr="utility_platform",
        section="advanced",
        label="Utility platform:",
        widget="combo",
        default="",
        options=("", "anthropic", "gemini", "openai", "kimi", "glm"),
        setup_visible=False,
        runtime_getter=lambda config: config.utility_platform,
    ),
    SettingField(
        env_key="UTILITY_API_KEY",
        attr="utility_api_key",
        section="advanced",
        label="Utility API key:",
        widget="password",
        default="",
        secret=True,
        placeholder_key="settings_placeholder_unchanged",
        setup_visible=False,
        runtime_getter=lambda config: config.utility_api_key,
    ),
    SettingField(
        env_key="UTILITY_MODEL",
        attr="utility_model",
        section="advanced",
        label="Utility model:",
        widget="text",
        default="",
        setup_visible=False,
        runtime_getter=lambda config: config.utility_model,
    ),
    SettingField(
        env_key="SCENE_PLATFORM",
        attr="scene_platform",
        section="advanced",
        label="Scene platform:",
        widget="combo",
        default="",
        options=("", "anthropic", "gemini", "openai", "kimi", "glm"),
        setup_visible=False,
        runtime_getter=lambda config: config.scene_platform,
    ),
    SettingField(
        env_key="SCENE_API_KEY",
        attr="scene_api_key",
        section="advanced",
        label="Scene API key:",
        widget="password",
        default="",
        secret=True,
        placeholder_key="settings_placeholder_unchanged",
        setup_visible=False,
        runtime_getter=lambda config: config.scene_api_key,
    ),
    SettingField(
        env_key="SCENE_MODEL",
        attr="scene_model",
        section="advanced",
        label="Scene model:",
        widget="text",
        default="",
        setup_visible=False,
        runtime_getter=lambda config: config.scene_model,
    ),
    SettingField(
        env_key="MEMORY_DB_PATH",
        attr="memory_db_path",
        section="advanced",
        label="settings_field_memory_db_path",
        widget="text",
        default="",
        setup_visible=False,
        runtime_getter=lambda config: config.memory.db_path,
    ),
    SettingField(
        env_key="FAMILIAR_AUTO_DESIRE",
        attr="auto_desire",
        section="advanced",
        label="Auto desire turns:",
        widget="bool",
        default=False,
        setup_visible=False,
        runtime_getter=lambda config: config.auto_desire,
    ),
    SettingField(
        env_key="FAMILIAR_AUTO_SAY",
        attr="auto_say",
        section="advanced",
        label="Auto-say text:",
        widget="bool",
        default=True,
        setup_visible=False,
        runtime_getter=lambda config: config.auto_say,
    ),
)


def iter_setting_fields(
    *, section: str | None = None, setup_mode: bool = False
) -> Iterable[SettingField]:
    """Yield setting fields for the requested section/mode."""
    for field in SETTINGS_FIELDS:
        if section is not None and field.section != section:
            continue
        if setup_mode and not field.setup_visible:
            continue
        yield field


def get_setting_field(attr: str) -> SettingField:
    """Return schema metadata by SetupConfig attribute name."""
    for field in SETTINGS_FIELDS:
        if field.attr == attr:
            return field
    raise KeyError(attr)


def sections_for_mode(*, setup_mode: bool = False) -> tuple[str, ...]:
    """Return section ids that have visible fields for the requested mode."""
    visible: list[str] = []
    for section in SECTION_ORDER:
        if any(True for _ in iter_setting_fields(section=section, setup_mode=setup_mode)):
            visible.append(section)
    return tuple(visible)


def setup_config_from_agent_config(config: "AgentConfig") -> SetupConfig:
    """Project a runtime AgentConfig into the shared setup schema."""
    values: dict[str, Any] = {}
    for field in SETTINGS_FIELDS:
        if field.runtime_getter is None:
            continue
        values[field.attr] = field.runtime_getter(config)
    return SetupConfig(**values)


def setup_config_to_env_values(config: SetupConfig) -> dict[str, str]:
    """Convert SetupConfig into the unified env key/value mapping."""
    values: dict[str, str] = {}
    for field in SETTINGS_FIELDS:
        raw = getattr(config, field.attr)
        if field.widget == "bool":
            values[field.env_key] = "true" if bool(raw) else "false"
        else:
            values[field.env_key] = str(raw).strip()
    return values


def validate_setup_config(config: SetupConfig, *, setup_mode: bool = False) -> list[str]:
    """Return validation errors for schema-managed fields."""
    errors: list[str] = []
    if setup_mode and not config.api_key.strip():
        errors.append("API_KEY is required to continue.")
    for field in SETTINGS_FIELDS:
        if setup_mode and not field.setup_visible:
            continue
        if field.validator is None:
            continue
        message = field.validator(getattr(config, field.attr))
        if message:
            errors.append(f"{field.label} {message}")
    return errors
