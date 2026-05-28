"""Public entry point for multi-witness alignment."""

from __future__ import annotations

from dataclasses import dataclass, field

from tracealign.align import AlignerConfig


@dataclass
class MultiAlignerConfig:
    """Configuration for align_multi.

    Follows the @dataclass style of v0.1's AlignerConfig; snapshotted into
    MultiAlignmentResult.params for persistence.
    """

    pairwise: AlignerConfig = field(default_factory=AlignerConfig)
    node_match: str = "max"
    guide_tree_method: str = "upgma"
    gap_penalty_multi: float = -2.0


_VALID_NODE_MATCH = {"max", "mean", "min"}
_VALID_GUIDE_TREE = {"upgma"}


def _validate_config(cfg: MultiAlignerConfig) -> None:
    if cfg.node_match not in _VALID_NODE_MATCH:
        raise ValueError(
            f"unknown node_match mode: {cfg.node_match!r}; "
            f"expected one of {sorted(_VALID_NODE_MATCH)}"
        )
    if cfg.guide_tree_method not in _VALID_GUIDE_TREE:
        raise ValueError(
            f"unknown guide_tree_method: {cfg.guide_tree_method!r}; "
            f"expected one of {sorted(_VALID_GUIDE_TREE)}"
        )
