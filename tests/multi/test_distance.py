"""Tests for the pairwise distance matrix."""

import numpy as np

import tracealign
from tracealign.align import AlignerConfig
from tracealign.multi.distance import pairwise_distances


def test_pairwise_distances_identical_witnesses_distance_zero():
    a = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1")
    b = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W2")
    pack = tracealign.get_language("hbo")
    matrix, wids = pairwise_distances({"W1": a, "W2": b}, pack, AlignerConfig())

    assert wids == ["W1", "W2"]
    assert matrix.shape == (2, 2)
    assert matrix[0, 0] == 0.0
    assert matrix[1, 1] == 0.0
    assert abs(matrix[0, 1] - 0.0) < 1e-9
    assert matrix[0, 1] == matrix[1, 0]


def test_pairwise_distances_disjoint_witnesses_distance_near_one():
    a = tracealign.tokenize("aaa bbb ccc", lang="hbo", seq_label="W1")
    b = tracealign.tokenize("xxx yyy zzz", lang="hbo", seq_label="W2")
    pack = tracealign.get_language("hbo")
    matrix, _ = pairwise_distances({"W1": a, "W2": b}, pack, AlignerConfig())
    assert matrix[0, 1] > 0.5


def test_pairwise_distances_sorts_witness_ids_canonically():
    # dict insertion order is preserved by Python, but pairwise_distances
    # must sort to guarantee deterministic output regardless of input order.
    a = tracealign.tokenize("שלום", lang="hbo", seq_label="W1")
    b = tracealign.tokenize("שלום", lang="hbo", seq_label="W2")
    pack = tracealign.get_language("hbo")
    _, wids_ab = pairwise_distances({"W2": b, "W1": a}, pack, AlignerConfig())
    _, wids_ba = pairwise_distances({"W1": a, "W2": b}, pack, AlignerConfig())
    assert wids_ab == wids_ba == ["W1", "W2"]


def test_pairwise_distances_symmetric():
    a = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1")
    b = tracealign.tokenize("שלום אחר", lang="hbo", seq_label="W2")
    pack = tracealign.get_language("hbo")
    matrix, _ = pairwise_distances({"W1": a, "W2": b}, pack, AlignerConfig())
    assert matrix[0, 1] == matrix[1, 0]
    np.testing.assert_array_equal(np.diag(matrix), np.zeros(2))
