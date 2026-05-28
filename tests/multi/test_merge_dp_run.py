"""Tests for the forward DP of align_sequence_to_graph."""

import tracealign
from tracealign.align import AlignerConfig
from tracealign.multi.graph import VariantGraph
from tracealign.multi.merge import _run_poa_dp


def test_dp_score_for_identical_sequence_against_linear_graph():
    pack = tracealign.get_language("hbo")
    seq = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W2")
    w1 = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1")
    g = VariantGraph.from_sequence("W1", w1)
    score = _run_poa_dp(
        seq, g, pack,
        pairwise_cfg=AlignerConfig(),
        node_match_mode="max",
        gap_penalty=-2.0,
    )["best_score"]
    # Two exact matches at +1.0 each, plus zero from sentinels.
    assert score >= 2.0


def test_dp_higher_score_when_sequence_matches_existing_graph_path():
    pack = tracealign.get_language("hbo")
    aligned = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1")
    unrelated = tracealign.tokenize("aaa bbb", lang="hbo", seq_label="W2")
    g = VariantGraph.from_sequence("W1", aligned)
    s_match = _run_poa_dp(
        aligned, g, pack,
        pairwise_cfg=AlignerConfig(),
        node_match_mode="max",
        gap_penalty=-2.0,
    )["best_score"]
    s_unrelated = _run_poa_dp(
        unrelated, g, pack,
        pairwise_cfg=AlignerConfig(),
        node_match_mode="max",
        gap_penalty=-2.0,
    )["best_score"]
    assert s_match > s_unrelated
