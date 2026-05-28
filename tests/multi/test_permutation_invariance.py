"""Property test: align_multi result must not depend on input dict insertion order."""

import tracealign


def _witness_paths(result):
    return {
        wid: [n.tokens[wid].text for n in result.graph.witness_path(wid)]
        for wid in result.witness_ids
    }


def _variant_loci(result):
    return frozenset(
        frozenset((wid, t.text) for wid, t in n.tokens.items())
        for n in result.graph.variants()
    )


def test_permutation_invariance_two_orderings():
    seqs_a = {
        "W1": tracealign.tokenize("שלום עולם רַבִּי דויד", lang="hbo", seq_label="W1"),
        "W2": tracealign.tokenize("שלום עולם רבי דוד", lang="hbo", seq_label="W2"),
        "W3": tracealign.tokenize("שלום עולם ר\"י", lang="hbo", seq_label="W3"),
    }
    # Different insertion order, same data
    seqs_b = {
        "W3": seqs_a["W3"],
        "W1": seqs_a["W1"],
        "W2": seqs_a["W2"],
    }

    r_a = tracealign.align_multi(seqs_a, lang="hbo")
    r_b = tracealign.align_multi(seqs_b, lang="hbo")

    assert _witness_paths(r_a) == _witness_paths(r_b)
    assert _variant_loci(r_a) == _variant_loci(r_b)


def test_permutation_invariance_with_insertion():
    seqs_a = {
        "A": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="A"),
        "B": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="B"),
        "C": tracealign.tokenize("שלום חדש עולם", lang="hbo", seq_label="C"),
    }
    seqs_b = {"C": seqs_a["C"], "A": seqs_a["A"], "B": seqs_a["B"]}

    r_a = tracealign.align_multi(seqs_a, lang="hbo")
    r_b = tracealign.align_multi(seqs_b, lang="hbo")

    assert _witness_paths(r_a) == _witness_paths(r_b)
    assert _variant_loci(r_a) == _variant_loci(r_b)
