"""Tests for align_sequence_to_graph as a complete operation."""

import tracealign
from tracealign.align import AlignerConfig
from tracealign.multi.graph import VariantGraph
from tracealign.multi.merge import align_sequence_to_graph


def test_align_identical_sequence_merges_all_tokens():
    pack = tracealign.get_language("hbo")
    a = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1")
    b = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W2")
    g = VariantGraph.from_sequence("W1", a)
    g2 = align_sequence_to_graph(b, "W2", g, pack, AlignerConfig(), "max", -2.0)

    # Both witnesses present
    assert set(g2.witness_ids) == {"W1", "W2"}
    # All non-sentinel nodes carry both witnesses
    for node in g2.nodes:
        if node.id in ("START", "END"):
            continue
        assert set(node.tokens.keys()) == {"W1", "W2"}
    # No new nodes introduced beyond the original (graph still has same content nodes)
    assert len([n for n in g2.nodes if n.id not in ("START", "END")]) == len(a)


def test_align_with_insertion_creates_new_node():
    pack = tracealign.get_language("hbo")
    base = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1")
    extended = tracealign.tokenize("שלום חדש עולם", lang="hbo", seq_label="W2")
    g = VariantGraph.from_sequence("W1", base)
    g2 = align_sequence_to_graph(extended, "W2", g, pack, AlignerConfig(), "max", -2.0)

    # Now there are 3 content nodes (the new "חדש" added)
    content_nodes = [n for n in g2.nodes if n.id not in ("START", "END")]
    assert len(content_nodes) == 3
    # The new node carries only W2
    inserted = [n for n in content_nodes if set(n.tokens.keys()) == {"W2"}]
    assert len(inserted) == 1
    assert inserted[0].tokens["W2"].text == "חדש"
