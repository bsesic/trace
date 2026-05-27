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


def _topological_node_ids(graph) -> list[str]:
    """Kahn's algorithm topological sort over the graph's nodes.

    Returns node ids in topological order, with stable ordering by node id
    among nodes with the same depth to keep the algorithm deterministic.
    """
    incoming: dict[str, set[str]] = {n.id: set() for n in graph.nodes}
    outgoing: dict[str, list[str]] = {n.id: [] for n in graph.nodes}
    for edge in graph.edges:
        incoming[edge.target_id].add(edge.source_id)
        outgoing[edge.source_id].append(edge.target_id)

    # Sources have no incoming edges
    ready = sorted([nid for nid, srcs in incoming.items() if not srcs])
    out: list[str] = []
    while ready:
        nid = ready.pop(0)
        out.append(nid)
        # Outgoing edges sorted for determinism
        for tgt in sorted(outgoing[nid]):
            incoming[tgt].discard(nid)
            if not incoming[tgt]:
                # Insert into ready in sorted order
                import bisect
                bisect.insort(ready, tgt)
    return out
