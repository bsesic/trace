"""Multi-witness POA merge: sequence-vs-graph alignment + graph update."""

from __future__ import annotations

import statistics

from tracealign.align.needleman_wunsch import _dp_score
from tracealign.lang.base import LanguagePack
from tracealign.model import Token
from tracealign.multi.graph import GraphNode
from tracealign.score.tiered import tiered_score


def node_match_score(
    token: Token,
    node: GraphNode,
    pack: LanguagePack,
    mode: str = "max",
) -> float:
    """Aggregate score for matching `token` against the constituents of `node`.

    `mode` is one of "max" (default), "mean", or "min". The per-constituent
    score is the tiered pairwise score mapped to the DP scale [-1, +1] by
    the same convention as v0.1's pairwise aligner.
    """
    if not node.tokens:
        # Sentinel node — never matches a real token
        return float("-inf")

    scores = [_dp_score(tiered_score(token, t, pack).score) for t in node.tokens.values()]
    if mode == "max":
        return max(scores)
    if mode == "min":
        return min(scores)
    if mode == "mean":
        return statistics.mean(scores)
    raise ValueError(f"unknown node_match mode: {mode}")
