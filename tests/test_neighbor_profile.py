"""Tests for the neighbor profile compatibility boundary."""

from familiar_neighbor import NeighborProfile
from familiar_neighbor.mind import DesireSystem, GlobalWorkspace


def test_neighbor_profile_defaults_to_neighbor_tool_tag() -> None:
    profile = NeighborProfile()

    assert profile.name == "neighbor"
    assert profile.tool_tags == {"neighbor"}


def test_neighbor_mind_reexports_existing_cognition_modules() -> None:
    assert DesireSystem.__name__ == "DesireSystem"
    assert GlobalWorkspace.__name__ == "GlobalWorkspace"
