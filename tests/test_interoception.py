from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from familiar_agent.interoception import MCPInteroceptionProvider, semantic_pressure


def test_mcp_interoception_provider_uses_latest_jsonl_payload(tmp_path: Path) -> None:
    path = tmp_path / "interoception.jsonl"
    old_payload = {
        "observed_at": (datetime.utcnow() - timedelta(seconds=5)).isoformat(),
        "energy": 0.2,
        "cognitive_load": 0.9,
    }
    new_payload = {
        "signal": {
            "observed_at": datetime.utcnow().isoformat(),
            "energy": 0.8,
            "cognitive_load": 0.1,
            "body_stress": 0.2,
            "social_openness": 0.7,
        }
    }
    path.write_text(
        "\n".join(json.dumps(item) for item in (old_payload, new_payload)),
        encoding="utf-8",
    )

    signal = MCPInteroceptionProvider(path).collect()
    pressure = semantic_pressure(signal)

    assert signal.provider == "mcp"
    assert signal.energy == 0.8
    assert pressure.need_rest < 0.4


def test_mcp_interoception_provider_ignores_stale_payload(tmp_path: Path) -> None:
    path = tmp_path / "interoception.json"
    payload = {
        "observed_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
        "energy": 0.1,
        "cognitive_load": 0.95,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    signal = MCPInteroceptionProvider(path, max_staleness_seconds=10).collect()

    assert signal.provider == "noop"
