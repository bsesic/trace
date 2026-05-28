"""Multi-witness POA merge: sequence-vs-graph alignment + graph update."""

from __future__ import annotations

import statistics

from tracealign.align import AlignerConfig
from tracealign.align.needleman_wunsch import _dp_score
from tracealign.lang.base import LanguagePack
from tracealign.model import Token
from tracealign.multi.graph import GraphNode
from tracealign.score.tiered import tiered_score


NEG_INF = float("-inf")


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


def _run_poa_dp(
    seq,
    graph,
    pack: LanguagePack,
    pairwise_cfg: AlignerConfig,
    node_match_mode: str,
    gap_penalty: float,
) -> dict:
    """Forward DP for sequence-vs-graph alignment.

    Implements the three POA transitions over a topologically ordered DAG:

      * match  — consume ``seq[i]`` and advance from a predecessor of ``nid``
        to ``nid``; scored by :func:`node_match_score`.
      * insert — consume ``seq[i]`` but stay at ``nid``; cost ``gap_penalty``.
      * delete — advance from a predecessor of ``nid`` to ``nid`` without
        consuming a sequence token; cost ``gap_penalty`` for real nodes,
        free when either endpoint is the START or END sentinel.

    Sentinel transitions are free so that reaching END after exactly ``m``
    consumed sequence tokens does not pay an extra penalty.

    Returns a dict with:
      * ``dp``         — ``dp[i][node_id]`` = best score reaching ``node_id``
        after consuming ``i`` sequence tokens.
      * ``bp``         — ``bp[i][node_id]`` = ``(op, prev_i, prev_node_id)``
        backpointer or ``None``.
      * ``best_score`` — the score at the END sentinel at ``i = len(seq)``.
      * ``topo``       — topological list of node ids.
    """
    topo = _topological_node_ids(graph)
    nodes_by_id = {n.id: n for n in graph.nodes}

    incoming: dict[str, list[str]] = {nid: [] for nid in topo}
    for edge in graph.edges:
        incoming[edge.target_id].append(edge.source_id)
    # Sort predecessors for determinism
    for nid in incoming:
        incoming[nid].sort()

    m = len(seq)
    dp: dict[int, dict[str, float]] = {
        i: {nid: NEG_INF for nid in topo} for i in range(m + 1)
    }
    bp: dict[int, dict[str, tuple[str, int, str] | None]] = {
        i: {nid: None for nid in topo} for i in range(m + 1)
    }

    # Start: dp[0][START] = 0
    dp[0]["START"] = 0.0

    def _is_sentinel(nid: str) -> bool:
        return nid in ("START", "END")

    for i in range(m + 1):
        for nid in topo:
            node = nodes_by_id[nid]

            # Delete (skip this node): advance from prev_nid to nid without
            # consuming a sequence token. Free at sentinels, otherwise
            # gap_penalty. Processed first so match/insert at the same i can
            # read the updated dp[i][nid].
            for prev_nid in incoming[nid]:
                if dp[i][prev_nid] == NEG_INF:
                    continue
                step = 0.0 if (_is_sentinel(nid) or _is_sentinel(prev_nid)) else gap_penalty
                cand = dp[i][prev_nid] + step
                if cand > dp[i][nid]:
                    dp[i][nid] = cand
                    bp[i][nid] = ("delete", i, prev_nid)

            # Match: consume seq[i] AND advance from prev_nid to nid.
            # Not allowed at START (no node before it) or END (no real tokens).
            if i < m and nid not in ("START", "END"):
                token = seq[i]
                match_s = node_match_score(token, node, pack, mode=node_match_mode)
                if match_s != NEG_INF:
                    for prev_nid in incoming[nid]:
                        if dp[i][prev_nid] == NEG_INF:
                            continue
                        cand = dp[i][prev_nid] + match_s
                        if cand > dp[i + 1][nid]:
                            dp[i + 1][nid] = cand
                            bp[i + 1][nid] = ("match", i, prev_nid)

            # Insertion in seq: consume seq[i] but stay at this node.
            # Not allowed at START (we never sit on START while consuming).
            if i < m and nid != "START":
                if dp[i][nid] != NEG_INF:
                    cand = dp[i][nid] + gap_penalty
                    if cand > dp[i + 1][nid]:
                        dp[i + 1][nid] = cand
                        bp[i + 1][nid] = ("insert", i, nid)

    best_score = dp[m]["END"]
    return {"dp": dp, "bp": bp, "best_score": best_score, "topo": topo}
