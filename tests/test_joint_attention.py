"""joint_attention tool: present in the registry, steers to see()."""

from __future__ import annotations

import pytest

from familiar_agent.tools.joint_attention import JointAttentionTool
from familiar_capabilities import JointAttentionCapability


@pytest.mark.asyncio
async def test_joint_attention_acknowledges_target_and_points_to_see() -> None:
    cap = JointAttentionCapability(JointAttentionTool())
    assert [s.name for s in cap.specs()] == ["joint_attention"]
    res = await cap.call("joint_attention", {"target": "窓の光"})
    assert res.success and "窓の光" in res.text and "see()" in res.text
    empty = await cap.call("joint_attention", {})
    assert "what they pointed at" in empty.text


def test_tom_description_carries_pragmatic_cues() -> None:
    from familiar_agent.tools.tom import ToMTool

    desc = ToMTool.__new__(ToMTool)
    desc._default_person = "Kota"
    spec = desc.get_tool_definitions()[0]
    assert spec["name"] == "perspective_taking"
    text = spec["description"]
    for cue in ("trailing sentence", "non-sequitur", "'it's fine'"):
        assert cue in text
