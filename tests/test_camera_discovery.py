from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_discover_network_cameras_merges_sources_and_dedupes_hosts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import familiar_agent.camera_discovery as mod

    monkeypatch.setattr(
        mod,
        "_discover_ws_discovery_cameras",
        AsyncMock(
            return_value=[
                {
                    "host": "192.168.1.10",
                    "address": "http://192.168.1.10:2020/onvif/device_service",
                    "source": "ws-discovery",
                    "port": "2020",
                }
            ]
        ),
    )
    monkeypatch.setattr(
        mod,
        "_discover_mdns_cameras",
        AsyncMock(
            return_value=[
                {
                    "host": "192.168.1.10",
                    "address": "rtsp://192.168.1.10:554/stream1",
                    "source": "mdns",
                    "name": "Tapo Cam",
                    "port": "554",
                }
            ]
        ),
    )
    monkeypatch.setattr(
        mod,
        "_discover_ssdp_cameras",
        AsyncMock(
            return_value=[
                {
                    "host": "192.168.1.22",
                    "address": "http://192.168.1.22:80/device.xml",
                    "source": "ssdp",
                    "port": "80",
                }
            ]
        ),
    )
    port_scan = AsyncMock(return_value=[])
    monkeypatch.setattr(mod, "_discover_port_scan_cameras", port_scan)

    results = await mod.discover_network_cameras(timeout=1.0)

    assert [item["host"] for item in results] == ["192.168.1.10", "192.168.1.22"]
    assert results[0]["name"] == "Tapo Cam"
    assert results[0]["sources"] == "mdns,ws-discovery"
    assert results[0]["address"] == "http://192.168.1.10:2020/onvif/device_service"
    port_scan.assert_not_called()


@pytest.mark.asyncio
async def test_discover_network_cameras_can_include_port_scan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import familiar_agent.camera_discovery as mod

    monkeypatch.setattr(mod, "_discover_ws_discovery_cameras", AsyncMock(return_value=[]))
    monkeypatch.setattr(mod, "_discover_mdns_cameras", AsyncMock(return_value=[]))
    monkeypatch.setattr(mod, "_discover_ssdp_cameras", AsyncMock(return_value=[]))
    port_scan = AsyncMock(
        return_value=[
            {
                "host": "192.168.1.77",
                "address": "rtsp://192.168.1.77:554/stream1",
                "source": "port-scan",
                "port": "554",
            }
        ]
    )
    monkeypatch.setattr(mod, "_discover_port_scan_cameras", port_scan)

    results = await mod.discover_network_cameras(timeout=1.0, include_port_scan=True)

    assert results == [
        {
            "host": "192.168.1.77",
            "address": "rtsp://192.168.1.77:554/stream1",
            "source": "port-scan",
            "sources": "port-scan",
            "port": "554",
            "name": "",
        }
    ]
    port_scan.assert_awaited_once_with(timeout=1.0)


def test_main_prints_json_results(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import familiar_agent.camera_discovery as mod

    monkeypatch.setattr(
        mod,
        "discover_network_cameras",
        AsyncMock(
            return_value=[
                {
                    "host": "192.168.1.50",
                    "address": "http://192.168.1.50:2020/onvif/device_service",
                    "source": "ws-discovery",
                    "sources": "ws-discovery",
                    "port": "2020",
                    "name": "",
                }
            ]
        ),
    )
    monkeypatch.setattr(mod.sys, "argv", ["camera-discovery", "--json"])

    rc = mod.main()

    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload[0]["host"] == "192.168.1.50"
