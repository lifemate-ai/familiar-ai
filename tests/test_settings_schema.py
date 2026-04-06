from __future__ import annotations

from familiar_agent.settings_schema import (
    sections_for_mode,
    setup_config_to_env_values,
    validate_setup_config,
    SetupConfig,
    iter_setting_fields,
)


def test_setup_mode_schema_is_subset_and_includes_api_key() -> None:
    full = {field.attr for field in iter_setting_fields(setup_mode=False)}
    setup = {field.attr for field in iter_setting_fields(setup_mode=True)}

    assert "api_key" in setup
    assert setup < full
    assert "utility_api_key" not in setup
    assert "camera_host" not in setup
    assert sections_for_mode(setup_mode=True) == ("agent", "voice")


def test_setup_config_to_env_values_serializes_auto_flags() -> None:
    values = setup_config_to_env_values(SetupConfig(auto_desire=True, auto_say=False))

    assert values["FAMILIAR_AUTO_DESIRE"] == "true"
    assert values["FAMILIAR_AUTO_SAY"] == "false"


def test_validate_setup_config_requires_api_key_only_in_setup_mode() -> None:
    config = SetupConfig(api_key="", camera_onvif_port="not-a-port")

    setup_errors = validate_setup_config(config, setup_mode=True)
    full_errors = validate_setup_config(config, setup_mode=False)

    assert any("API_KEY is required" in error for error in setup_errors)
    assert any("Port must be an integer" in error for error in full_errors)
