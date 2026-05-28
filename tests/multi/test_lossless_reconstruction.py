"""Property test: every input witness can be exactly reconstructed from the result graph."""

import tracealign


def _reconstruct(result, wid: str):
    """Walk the witness's path through the graph and return its tokens."""
    return [n.tokens[wid] for n in result.graph.witness_path(wid)]


def test_lossless_reconstruction_two_witnesses():
    seqs = {
        "W1": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1"),
        "W2": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W2"),
    }
    result = tracealign.align_multi(seqs, lang="hbo")
    for wid in seqs:
        assert _reconstruct(result, wid) == seqs[wid]


def test_lossless_reconstruction_three_witnesses_with_insertion():
    seqs = {
        "W1": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1"),
        "W2": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W2"),
        "W3": tracealign.tokenize("שלום חדש עולם", lang="hbo", seq_label="W3"),
    }
    result = tracealign.align_multi(seqs, lang="hbo")
    for wid in seqs:
        assert _reconstruct(result, wid) == seqs[wid]


def test_lossless_reconstruction_diverse_witnesses():
    seqs = {
        "A": tracealign.tokenize("שלום עולם רַבִּי דויד אמר", lang="hbo", seq_label="A"),
        "B": tracealign.tokenize("שלום עולם רבי דוד אמר", lang="hbo", seq_label="B"),
        "C": tracealign.tokenize("שלום עולם ר\"י אמר", lang="hbo", seq_label="C"),
    }
    result = tracealign.align_multi(seqs, lang="hbo")
    for wid in seqs:
        assert _reconstruct(result, wid) == seqs[wid]
