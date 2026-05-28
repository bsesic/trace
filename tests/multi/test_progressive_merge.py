"""Tests for progressive_merge wrapper."""

import numpy as np

import tracealign
from tracealign.align import AlignerConfig
from tracealign.multi.guide_tree import build_upgma
from tracealign.multi.merge import progressive_merge


def test_progressive_merge_three_identical_witnesses_collapses():
    pack = tracealign.get_language("hbo")
    seqs = {
        "W1": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1"),
        "W2": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W2"),
        "W3": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W3"),
    }
    D = np.zeros((3, 3))
    tree = build_upgma(D, ["W1", "W2", "W3"])
    g = progressive_merge(seqs, tree, pack, AlignerConfig(), "max", -2.0)
    # All content nodes should carry all three witnesses
    for n in g.nodes:
        if n.id in ("START", "END"):
            continue
        assert set(n.tokens.keys()) == {"W1", "W2", "W3"}


def test_progressive_merge_with_distinct_third_witness():
    pack = tracealign.get_language("hbo")
    seqs = {
        "W1": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1"),
        "W2": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W2"),
        "W3": tracealign.tokenize("שלום עולם חדש", lang="hbo", seq_label="W3"),
    }
    D = np.array([
        [0.0, 0.0, 0.3],
        [0.0, 0.0, 0.3],
        [0.3, 0.3, 0.0],
    ])
    tree = build_upgma(D, ["W1", "W2", "W3"])
    g = progressive_merge(seqs, tree, pack, AlignerConfig(), "max", -2.0)
    # All witnesses present
    assert set(g.witness_ids) == {"W1", "W2", "W3"}
    # There's at least one node holding only W3 (the inserted "חדש")
    w3_only = [n for n in g.nodes
               if n.id not in ("START", "END") and set(n.tokens.keys()) == {"W3"}]
    assert len(w3_only) >= 1
