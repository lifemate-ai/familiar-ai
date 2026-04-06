from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from familiar_agent.tools.mic import describe_sounddevice_input_failure, probe_sounddevice_input


def test_describe_sounddevice_input_failure_adds_wsl_hint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WSL_INTEROP", "/run/WSL/1")
    monkeypatch.delenv("PULSE_SERVER", raising=False)

    message = describe_sounddevice_input_failure(RuntimeError("Error querying device -1"))

    assert "Error querying device -1" in message
    assert "WSL2/WSLg" in message
    assert "PULSE_SERVER=unix:/mnt/wslg/PulseServer" in message


def test_probe_sounddevice_input_reports_missing_devices(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WSL_INTEROP", "/run/WSL/1")
    monkeypatch.setenv("PULSE_SERVER", "unix:/mnt/wslg/PulseServer")

    mock_sd = MagicMock()
    mock_sd.query_devices.side_effect = [[], RuntimeError("Error querying device -1")]

    with patch.dict("sys.modules", {"sounddevice": mock_sd}):
        ok, detail = probe_sounddevice_input()

    assert ok is False
    assert "WSL2/WSLg" in detail
    assert "python -m sounddevice" in detail


def test_probe_sounddevice_input_reports_device_name() -> None:
    mock_sd = MagicMock()
    mock_sd.query_devices.side_effect = [
        [{"name": "Mic", "default_samplerate": 48000}],
        {"name": "Mic", "default_samplerate": 48000},
    ]

    with patch.dict("sys.modules", {"sounddevice": mock_sd}):
        ok, detail = probe_sounddevice_input()

    assert ok is True
    assert detail == "Mic @ 48000 Hz"
