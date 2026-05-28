"""End-to-end tests for align_multi."""

import pytest

import tracealign
from tracealign.multi.api import MultiAlignmentResult, align_multi


def test_align_multi_single_witness():
    seqs = {"W1": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1")}
    result = align_multi(seqs, lang="hbo")
    assert isinstance(result, MultiAlignmentResult)
    assert result.witness_ids == ["W1"]
    assert len(result.graph.nodes) >= 2  # at least START and END


def test_align_multi_two_identical_witnesses():
    seqs = {
        "W1": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1"),
        "W2": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W2"),
    }
    result = align_multi(seqs, lang="hbo")
    assert set(result.witness_ids) == {"W1", "W2"}
    # Every content node carries both witnesses
    for n in result.graph.nodes:
        if n.id in ("START", "END"):
            continue
        assert set(n.tokens.keys()) == {"W1", "W2"}


def test_align_multi_params_carry_version_metadata():
    seqs = {"W1": tracealign.tokenize("שלום", lang="hbo", seq_label="W1")}
    result = align_multi(seqs, lang="hbo")
    assert "trace_version" in result.params
    assert "language_pack_version" in result.params
    assert "guide_tree_method" in result.params
    assert result.params["lang"] == "hbo"


def test_align_multi_rejects_unknown_node_match():
    from tracealign.multi.api import MultiAlignerConfig

    seqs = {
        "W1": tracealign.tokenize("שלום", lang="hbo", seq_label="W1"),
        "W2": tracealign.tokenize("שלום", lang="hbo", seq_label="W2"),
    }
    bad = MultiAlignerConfig(node_match="median")
    with pytest.raises(ValueError):
        align_multi(seqs, lang="hbo", config=bad)
