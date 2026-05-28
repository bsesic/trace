"""Tests for the traceback of align_sequence_to_graph."""

import tracealign
from tracealign.align import AlignerConfig
from tracealign.multi.graph import VariantGraph
from tracealign.multi.merge import _run_poa_dp, _traceback_ops


def test_traceback_for_identical_sequence_yields_only_matches():
    pack = tracealign.get_language("hbo")
    seq = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W2")
    base = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1")
    g = VariantGraph.from_sequence("W1", base)
    dpr = _run_poa_dp(seq, g, pack, AlignerConfig(), "max", -2.0)
    ops = _traceback_ops(dpr)
    # All operations should be matches (one per seq token)
    assert len([op for op in ops if op[0] == "match"]) == len(seq)
    assert all(op[0] in ("match", "insert", "delete") for op in ops)


def test_traceback_for_inserted_token_yields_insert():
    pack = tracealign.get_language("hbo")
    # Sequence has one extra token
    base = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1")
    extended = tracealign.tokenize("שלום חדש עולם", lang="hbo", seq_label="W2")
    g = VariantGraph.from_sequence("W1", base)
    dpr = _run_poa_dp(extended, g, pack, AlignerConfig(), "max", -2.0)
    ops = _traceback_ops(dpr)
    # At least one insert op for the extra token
    assert any(op[0] == "insert" for op in ops)
