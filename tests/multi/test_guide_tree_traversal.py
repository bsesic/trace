"""Tests for post_order_witness_ids traversal."""

import numpy as np

from tracealign.multi.guide_tree import build_upgma, post_order_witness_ids


def test_post_order_two_witnesses():
    D = np.array([[0.0, 0.5], [0.5, 0.0]])
    tree = build_upgma(D, ["W1", "W2"])
    order = post_order_witness_ids(tree)
    assert sorted(order) == ["W1", "W2"]
    assert len(order) == 2


def test_post_order_three_witnesses_closest_pair_adjacent():
    D = np.array([
        [0.0, 0.1, 0.5],
        [0.1, 0.0, 0.5],
        [0.5, 0.5, 0.0],
    ])
    tree = build_upgma(D, ["A", "B", "C"])
    order = post_order_witness_ids(tree)
    assert set(order) == {"A", "B", "C"}
    assert len(order) == 3
    # A and B (closest) appear adjacent in the order
    a_idx = order.index("A")
    b_idx = order.index("B")
    assert abs(a_idx - b_idx) == 1


def test_post_order_is_deterministic():
    D = np.array([
        [0.0, 0.2, 0.2],
        [0.2, 0.0, 0.4],
        [0.2, 0.4, 0.0],
    ])
    tree1 = build_upgma(D, ["A", "B", "C"])
    tree2 = build_upgma(D, ["A", "B", "C"])
    assert post_order_witness_ids(tree1) == post_order_witness_ids(tree2)
