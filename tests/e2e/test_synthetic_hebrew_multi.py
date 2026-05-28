"""End-to-end multi-witness golden test on synthetic Hebrew."""

import tracealign


WITNESS_TEXTS = {
    "W1": "שלום עולם רַבִּי דויד אמר מחר",
    "W2": "שלום עולם רבי דוד אמר מחר",
    "W3": "שלום עולם ר\"י אמר מחר",
    "W4": "שלום עולם רבי דוד אמר טוב מחר",
}


def _align_witnesses():
    return tracealign.align_multi(
        {
            wid: tracealign.tokenize(text, lang="hbo", seq_label=wid)
            for wid, text in WITNESS_TEXTS.items()
        },
        lang="hbo",
    )


def test_synthetic_multi_all_witnesses_present():
    result = _align_witnesses()
    assert set(result.witness_ids) == {"W1", "W2", "W3", "W4"}


def test_synthetic_multi_lossless_reconstruction():
    result = _align_witnesses()
    expected = {
        wid: [t.text for t in tracealign.tokenize(text, lang="hbo", seq_label=wid)]
        for wid, text in WITNESS_TEXTS.items()
    }
    for wid, expected_texts in expected.items():
        path_texts = [n.tokens[wid].text for n in result.graph.witness_path(wid)]
        assert path_texts == expected_texts


def test_synthetic_multi_has_at_least_one_variant_locus():
    result = _align_witnesses()
    variants = list(result.graph.variants())
    assert len(variants) >= 1


def test_synthetic_multi_w4_insertion_appears_in_table():
    result = _align_witnesses()
    re = result.table.re_anchor("W4")
    # Some column shows token "טוב" for W4 and a gap for the others
    found_tov = False
    for col in re.columns:
        cell_w4 = col.cells.get("W4")
        if cell_w4 and cell_w4.token and cell_w4.token.text == "טוב":
            others_gap = all(
                col.cells[wid].token is None
                for wid in ("W1", "W2", "W3")
                if wid in col.cells
            )
            if others_gap:
                found_tov = True
                break
    assert found_tov
