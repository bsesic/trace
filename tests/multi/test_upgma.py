"""Tests for UPGMA construction."""

import numpy as np

from tracealign.multi.guide_tree import GuideTree, build_upgma


def test_upgma_two_witnesses_single_merge():
    D = np.array([[0.0, 0.5], [0.5, 0.0]])
    tree = build_upgma(D, ["W1", "W2"])
    assert isinstance(tree, GuideTree)
    assert tree.method == "upgma"
    assert tree.root.is_leaf is False
    assert len(tree.root.children) == 2
    # Height at root is half the merge distance
    assert abs(tree.root.height - 0.25) < 1e-9
    # Both witnesses are present as leaves
    leaves = {c.witness_id for c in tree.root.children}
    assert leaves == {"W1", "W2"}


def test_upgma_three_witnesses_closest_pair_merges_first():
    D = np.array([
        [0.0, 0.1, 0.5],
        [0.1, 0.0, 0.5],
        [0.5, 0.5, 0.0],
    ])
    tree = build_upgma(D, ["A", "B", "C"])
    # Closest pair (A, B) merges first, then C joins.
    # The root's children are the (AB) subtree and the C leaf.
    root = tree.root
    assert root.is_leaf is False
    assert len(root.children) == 2
    leaf_children = [c for c in root.children if c.is_leaf]
    inner_children = [c for c in root.children if not c.is_leaf]
    assert len(leaf_children) == 1
    assert leaf_children[0].witness_id == "C"
    assert len(inner_children) == 1
    inner = inner_children[0]
    inner_leaves = {c.witness_id for c in inner.children}
    assert inner_leaves == {"A", "B"}


def test_upgma_tie_breaking_uses_sorted_witness_ids():
    # D(A, B) == D(A, C), both 0.2. Tie-breaking should pick (A, B) because
    # (min, max) lexicographic order favours it over (A, C).
    D = np.array([
        [0.0, 0.2, 0.2],
        [0.2, 0.0, 0.4],
        [0.2, 0.4, 0.0],
    ])
    tree = build_upgma(D, ["A", "B", "C"])
    # The first merge must combine A and B (lexicographic tie-break)
    root = tree.root
    inner = [c for c in root.children if not c.is_leaf]
    assert len(inner) == 1
    inner_leaves = {c.witness_id for c in inner[0].children}
    assert inner_leaves == {"A", "B"}


def test_upgma_preserves_distance_matrix_on_tree():
    D = np.array([[0.0, 0.5], [0.5, 0.0]])
    tree = build_upgma(D, ["W1", "W2"])
    assert tree.distance_matrix == [[0.0, 0.5], [0.5, 0.0]]
    assert tree.witness_ids == ["W1", "W2"]
