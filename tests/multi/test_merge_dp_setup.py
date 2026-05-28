"""Tests for the DP setup phase of align_sequence_to_graph."""

import tracealign
from tracealign.multi.graph import VariantGraph
from tracealign.multi.merge import _topological_node_ids


def test_topological_order_starts_with_start_ends_with_end():
    seq = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1")
    g = VariantGraph.from_sequence("W1", seq)
    order = _topological_node_ids(g)
    assert order[0] == "START"
    assert order[-1] == "END"
    # All node ids must appear exactly once
    assert sorted(order) == sorted(n.id for n in g.nodes)


def test_topological_order_respects_edges():
    seq = tracealign.tokenize("a b c", lang="hbo", seq_label="W1")
    g = VariantGraph.from_sequence("W1", seq)
    order = _topological_node_ids(g)
    idx = {nid: i for i, nid in enumerate(order)}
    for edge in g.edges:
        assert idx[edge.source_id] < idx[edge.target_id]
