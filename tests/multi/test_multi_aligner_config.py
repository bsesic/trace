"""Tests for MultiAlignerConfig."""

import pytest

from tracealign.align import AlignerConfig
from tracealign.multi.api import MultiAlignerConfig


def test_default_multi_config():
    cfg = MultiAlignerConfig()
    assert isinstance(cfg.pairwise, AlignerConfig)
    assert cfg.node_match == "max"
    assert cfg.guide_tree_method == "upgma"
    assert cfg.gap_penalty_multi == -2.0


def test_override_node_match():
    cfg = MultiAlignerConfig(node_match="mean")
    assert cfg.node_match == "mean"


def test_pairwise_config_is_distinct_per_instance():
    c1 = MultiAlignerConfig()
    c2 = MultiAlignerConfig()
    assert c1.pairwise is not c2.pairwise


def test_validate_known_node_match_values_only():
    # Direct field assignment to an unknown value is not validated at
    # dataclass-construction time; validation happens at align_multi entry.
    # But we provide a helper that does the check.
    from tracealign.multi.api import _validate_config

    _validate_config(MultiAlignerConfig(node_match="max"))
    _validate_config(MultiAlignerConfig(node_match="mean"))
    _validate_config(MultiAlignerConfig(node_match="min"))
    with pytest.raises(ValueError):
        _validate_config(MultiAlignerConfig(node_match="median"))
    with pytest.raises(ValueError):
        _validate_config(MultiAlignerConfig(guide_tree_method="neighbor_joining"))
