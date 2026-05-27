from __future__ import annotations

import json
import sys
from types import SimpleNamespace
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


@pytest.mark.asyncio
async def test_discover_mdns_cameras_includes_onvif_and_rtsp_txt_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import familiar_agent.camera_discovery as mod

    service_infos = {
        ("_onvif._tcp.local.", "Tapo._onvif._tcp.local."): SimpleNamespace(
            port=2020,
            server="tapo-c220.local.",
            properties={b"model": b"Tapo C220"},
            parsed_addresses=lambda: ["192.168.1.44"],
        ),
        ("_rtsp._tcp.local.", "Tapo._rtsp._tcp.local."): SimpleNamespace(
            port=554,
            server="tapo-c220.local.",
            properties={b"path": b"/stream1"},
            parsed_addresses=lambda: ["192.168.1.44"],
        ),
    }
    discovered_types: list[str] = []

    class _FakeBrowser:
        def __init__(self, zc, service_type, listener):
            discovered_types.append(service_type)
            if service_type == "_onvif._tcp.local.":
                listener.add_service(zc, service_type, "Tapo._onvif._tcp.local.")
            if service_type == "_rtsp._tcp.local.":
                listener.add_service(zc, service_type, "Tapo._rtsp._tcp.local.")

        def cancel(self) -> None:
            return

    class _FakeZeroconf:
        def get_service_info(self, service_type, name, timeout=None):
            return service_infos[(service_type, name)]

        def close(self) -> None:
            return

    monkeypatch.setitem(
        sys.modules,
        "zeroconf",
        SimpleNamespace(ServiceBrowser=_FakeBrowser, Zeroconf=_FakeZeroconf),
    )
    monkeypatch.setattr(mod.time, "sleep", lambda _timeout: None)

    results = await mod._discover_mdns_cameras(timeout=1.0)

    assert "_onvif._tcp.local." in discovered_types
    assert "_rtsp._tcp.local." in discovered_types
    assert {
        "host": "192.168.1.44",
        "address": "http://192.168.1.44:2020/onvif/device_service",
        "source": "mdns",
        "port": "2020",
        "name": "tapo-c220.local",
        "service_type": "_onvif._tcp.local.",
    } in results
    assert {
        "host": "192.168.1.44",
        "address": "rtsp://192.168.1.44:554/stream1",
        "source": "mdns",
        "port": "554",
        "name": "tapo-c220.local",
        "service_type": "_rtsp._tcp.local.",
    } in results


def test_get_local_network_prefix_parses_default_gateway_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import familiar_agent.camera_discovery as mod

    monkeypatch.delenv("FAMILIAR_CAMERA_DISCOVERY_PREFIX", raising=False)

    def _fake_check_output(cmd, text=True, stderr=None):
        if cmd == ["ip", "route", "get", "1.1.1.1"]:
            raise RuntimeError("route get unavailable")
        return "default via 172.28.48.1 dev eth0\n"

    monkeypatch.setattr(mod.subprocess, "check_output", _fake_check_output)

    assert mod.get_local_network_prefix() == "172.28.48"


def test_get_local_network_prefix_falls_back_to_socket_probe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import familiar_agent.camera_discovery as mod

    monkeypatch.delenv("FAMILIAR_CAMERA_DISCOVERY_PREFIX", raising=False)
    monkeypatch.setattr(
        mod.subprocess,
        "check_output",
        lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError("ip not found")),
    )

    class _FakeSocket:
        def connect(self, addr) -> None:
            assert addr == ("8.8.8.8", 80)

        def getsockname(self):
            return ("10.0.0.42", 54321)

        def close(self) -> None:
            return

    monkeypatch.setattr(mod.socket, "socket", lambda *args, **kwargs: _FakeSocket())

    assert mod.get_local_network_prefix() == "10.0.0"
