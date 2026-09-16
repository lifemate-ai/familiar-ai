"""Network camera discovery helpers and CLI entrypoint."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import socket
import subprocess
import sys
import time
from collections import OrderedDict
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_CAMERA_PORTS = (554, 80, 2020)
_MDNS_SERVICE_TYPES = ("_onvif._tcp.local.", "_rtsp._tcp.local.", "_http._tcp.local.")
_SSDP_MULTICAST_ADDR = ("239.255.255.250", 1900)
_SSDP_REQUEST = "\r\n".join(
    [
        "M-SEARCH * HTTP/1.1",
        "HOST: 239.255.255.250:1900",
        'MAN: "ssdp:discover"',
        "MX: 1",
        "ST: ssdp:all",
        "",
        "",
    ]
).encode("ascii")


def _normalize_camera(entry: dict[str, str]) -> dict[str, str]:
    host = str(entry.get("host", "") or "").strip()
    address = str(entry.get("address", "") or "").strip()
    if not host and address:
        host = urlparse(address).hostname or ""
    if not host:
        return {}
    return {
        "host": host,
        "address": address,
        "source": str(entry.get("source", "") or "").strip(),
        "port": str(entry.get("port", "") or "").strip(),
        "name": str(entry.get("name", "") or "").strip(),
    }


def _decode_zeroconf_properties(raw: Any) -> dict[str, str]:
    properties: dict[str, str] = {}
    if not isinstance(raw, dict):
        return properties
    for key, value in raw.items():
        key_text = key.decode("utf-8", errors="ignore") if isinstance(key, bytes) else str(key)
        if isinstance(value, bytes):
            value_text = value.decode("utf-8", errors="ignore")
        else:
            value_text = str(value)
        properties[key_text] = value_text
    return properties


def _build_mdns_address(host: str, port: int, service_type: str, properties: dict[str, str]) -> str:
    explicit = properties.get("url") or properties.get("uri")
    if explicit:
        if "://" in explicit:
            return explicit
        path = explicit if explicit.startswith("/") else f"/{explicit}"
    elif service_type.startswith("_onvif"):
        path = "/onvif/device_service"
    elif service_type.startswith("_rtsp"):
        txt_path = properties.get("path") or properties.get("rtsp_path") or properties.get("stream")
        path = ""
        if txt_path:
            path = txt_path if txt_path.startswith("/") else f"/{txt_path}"
    else:
        path = ""

    scheme = "rtsp" if service_type.startswith("_rtsp") or port == 554 else "http"
    return f"{scheme}://{host}:{port}{path}" if port else f"{scheme}://{host}{path}"


def _extract_ip_prefix(ip_address: str) -> str | None:
    parts = ip_address.strip().split(".")
    if len(parts) != 4:
        return None
    try:
        octets = [int(part) for part in parts]
    except ValueError:
        return None
    if any(octet < 0 or octet > 255 for octet in octets):
        return None
    return ".".join(str(octet) for octet in octets[:3])


def _merge_camera_results(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: "OrderedDict[str, dict[str, str]]" = OrderedDict()
    for raw in candidates:
        item = _normalize_camera(raw)
        if not item:
            continue
        host = item["host"]
        if host not in merged:
            merged[host] = {**item, "sources": item["source"] or ""}
            continue

        current = merged[host]
        if not current["address"] and item["address"]:
            current["address"] = item["address"]
        if not current["port"] and item["port"]:
            current["port"] = item["port"]
        if not current["name"] and item["name"]:
            current["name"] = item["name"]

        sources = {
            source
            for source in (current.get("sources", ""), item["source"])
            for source in source.split(",")
            if source
        }
        current["sources"] = ",".join(sorted(sources))
        current["source"] = current["source"] or item["source"]

    return list(merged.values())


async def discover_network_cameras(
    *, timeout: float = 3.0, include_port_scan: bool = False
) -> list[dict[str, str]]:
    """Discover network cameras via multiple low-friction protocols."""
    tasks = [
        _discover_ws_discovery_cameras(timeout=timeout),
        _discover_mdns_cameras(timeout=timeout),
        _discover_ssdp_cameras(timeout=timeout),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    candidates: list[dict[str, str]] = []
    for result in results:
        if isinstance(result, BaseException):
            logger.debug("Camera discovery strategy failed: %s", result)
            continue
        candidates.extend(result)

    if include_port_scan:
        try:
            candidates.extend(await _discover_port_scan_cameras(timeout=timeout))
        except Exception as exc:
            logger.debug("Camera port-scan fallback failed: %s", exc)

    return _merge_camera_results(candidates)


async def _discover_ws_discovery_cameras(timeout: float = 3.0) -> list[dict[str, str]]:
    try:
        from wsdiscovery import WSDiscovery  # type: ignore[import]
    except ImportError:
        logger.debug("wsdiscovery not available — skipping WS-Discovery")
        return []

    def _sync() -> list[dict[str, str]]:
        wsd = WSDiscovery()
        try:
            wsd.start()
            services = wsd.searchServices()
        finally:
            try:
                wsd.stop()
            except Exception:
                pass

        found: list[dict[str, str]] = []
        for svc in services:
            try:
                addrs = svc.getXAddrs()
                if not addrs:
                    continue
                address = str(addrs[0])
                parsed = urlparse(address)
                host = parsed.hostname or ""
                port = parsed.port or 2020
                if host:
                    found.append(
                        {
                            "host": host,
                            "address": address,
                            "source": "ws-discovery",
                            "port": str(port),
                            "name": "",
                        }
                    )
            except Exception:
                continue
        return found

    try:
        return await asyncio.wait_for(asyncio.to_thread(_sync), timeout=timeout)
    except Exception as exc:
        logger.debug("WS-Discovery failed: %s", exc)
        return []


async def _discover_mdns_cameras(timeout: float = 3.0) -> list[dict[str, str]]:
    try:
        from zeroconf import ServiceBrowser, Zeroconf  # type: ignore[import]
    except ImportError:
        logger.debug("zeroconf not available — skipping mDNS discovery")
        return []

    def _sync() -> list[dict[str, str]]:
        found: list[dict[str, str]] = []

        class _Listener:
            def add_service(self, zc: Any, service_type: str, name: str) -> None:
                try:
                    info = zc.get_service_info(service_type, name, timeout=int(timeout * 1000))
                except Exception:
                    return
                if info is None:
                    return
                addresses: list[str] = []
                try:
                    addresses = list(info.parsed_addresses())
                except Exception:
                    pass
                if not addresses:
                    return

                port = int(getattr(info, "port", 0) or 0)
                properties = _decode_zeroconf_properties(getattr(info, "properties", {}))
                for host in addresses:
                    found.append(
                        {
                            "host": host,
                            "address": _build_mdns_address(host, port, service_type, properties),
                            "source": "mdns",
                            "port": str(port) if port else "",
                            "name": str(getattr(info, "server", "") or name).rstrip("."),
                            "service_type": service_type,
                        }
                    )

            def update_service(self, zc: Any, service_type: str, name: str) -> None:
                self.add_service(zc, service_type, name)

            def remove_service(self, zc: Any, service_type: str, name: str) -> None:
                return

        zc = Zeroconf()
        browsers = []
        try:
            listener = _Listener()
            for service_type in _MDNS_SERVICE_TYPES:
                browsers.append(ServiceBrowser(zc, service_type, listener))  # type: ignore[arg-type]
            time.sleep(timeout)
        finally:
            for browser in browsers:
                try:
                    browser.cancel()
                except Exception:
                    pass
            zc.close()
        return found

    try:
        return await asyncio.to_thread(_sync)
    except Exception as exc:
        logger.debug("mDNS discovery failed: %s", exc)
        return []


def _parse_ssdp_response(payload: bytes, addr: tuple[str, int]) -> dict[str, str]:
    text = payload.decode("utf-8", errors="ignore")
    headers: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()

    address = headers.get("location", "")
    host = urlparse(address).hostname if address else ""
    if not host:
        host = addr[0]
    if not host:
        return {}

    port = str(urlparse(address).port or "")
    name = headers.get("server", "") or headers.get("usn", "")
    return {
        "host": host,
        "address": address,
        "source": "ssdp",
        "port": port,
        "name": name,
    }


async def _discover_ssdp_cameras(timeout: float = 3.0) -> list[dict[str, str]]:
    def _sync() -> list[dict[str, str]]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.settimeout(max(0.2, timeout / 4))
        sock.sendto(_SSDP_REQUEST, _SSDP_MULTICAST_ADDR)

        deadline = time.monotonic() + timeout
        found: list[dict[str, str]] = []
        try:
            while time.monotonic() < deadline:
                try:
                    payload, addr = sock.recvfrom(65535)
                except socket.timeout:
                    break
                item = _parse_ssdp_response(payload, addr)
                if item:
                    found.append(item)
        finally:
            sock.close()
        return found

    try:
        return await asyncio.to_thread(_sync)
    except Exception as exc:
        logger.debug("SSDP discovery failed: %s", exc)
        return []


def get_local_network_prefix() -> str | None:
    """Best-effort `/24` prefix for local fallback scanning."""
    env_prefix = (os.environ.get("FAMILIAR_CAMERA_DISCOVERY_PREFIX", "") or "").strip()
    if env_prefix:
        return env_prefix

    commands = (
        ["ip", "route", "get", "1.1.1.1"],
        ["ip", "route"],
    )
    for cmd in commands:
        try:
            output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        except Exception:
            continue

        match = re.search(r"\bsrc\s+(\d+\.\d+\.\d+)\.\d+\b", output)
        if match:
            return match.group(1)

        match = re.search(r"\bdefault via\s+(\d+\.\d+\.\d+\.\d+)\b", output)
        if match:
            prefix = _extract_ip_prefix(match.group(1))
            if prefix:
                return prefix

        match = re.search(r"\b(\d+\.\d+\.\d+)\.\d+/\d+\b", output)
        if match:
            return match.group(1)

    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe.connect(("8.8.8.8", 80))
            prefix = _extract_ip_prefix(str(probe.getsockname()[0]))
            if prefix:
                return prefix
        finally:
            probe.close()
    except Exception:
        pass

    return None


async def _probe_camera_port(host: str, port: int, timeout: float) -> dict[str, str] | None:
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
    except Exception:
        return None
    try:
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass

    scheme = "rtsp" if port == 554 else "http"
    path = "/onvif/device_service" if port == 2020 else ""
    return {
        "host": host,
        "address": f"{scheme}://{host}:{port}{path}",
        "source": "port-scan",
        "port": str(port),
        "name": "",
    }


async def _discover_port_scan_cameras(timeout: float = 3.0) -> list[dict[str, str]]:
    prefix = get_local_network_prefix()
    if not prefix:
        return []

    hosts = [f"{prefix}.{index}" for index in range(1, 255)]
    probe_timeout = min(0.2, max(timeout / 20, 0.05))
    semaphore = asyncio.Semaphore(64)

    async def _scan_host(host: str) -> list[dict[str, str]]:
        async with semaphore:
            found: list[dict[str, str]] = []
            for port in _CAMERA_PORTS:
                result = await _probe_camera_port(host, port, timeout=probe_timeout)
                if result is not None:
                    found.append(result)
            return found

    tasks = [_scan_host(host) for host in hosts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    found: list[dict[str, str]] = []
    for result in results:
        if isinstance(result, BaseException):
            continue
        found.extend(result)
    return found


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover ONVIF / network cameras on the LAN")
    parser.add_argument(
        "--timeout", type=float, default=3.0, help="per-strategy timeout in seconds"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="enable slower TCP port-scan fallback in addition to WS-Discovery/mDNS/SSDP",
    )
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    return parser


def _render_human(results: list[dict[str, str]]) -> str:
    if not results:
        return "No cameras found."
    lines = ["Discovered cameras:"]
    for item in results:
        label = item["name"] or item["host"]
        details = f"{label} [{item['sources']}]"
        if item["address"]:
            details += f" -> {item['address']}"
        lines.append(details)
    return "\n".join(lines)


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args(sys.argv[1:])

    results = asyncio.run(
        discover_network_cameras(timeout=args.timeout, include_port_scan=bool(args.scan))
    )
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(_render_human(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
