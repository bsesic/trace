from tracealign.lang.arabic.tokenize import split_proclitics
from tracealign.tokenize.base import RawToken


def _raw(text, start=0):
    return RawToken(raw=text, span=(start, start + len(text)), flags=set())


def _texts(raws):
    return [r.raw for r in raws]


def test_splits_definite_article():
    out = split_proclitics([_raw("الكتاب")])
    assert _texts(out) == ["ال", "كتاب"]
    assert "proclitic" in out[0].flags
    assert "compound_part" in out[1].flags


def test_splits_waw_before_article():
    out = split_proclitics([_raw("والكتاب")])
    assert _texts(out) == ["و", "الكتاب"]


def test_splits_baa_before_article():
    out = split_proclitics([_raw("بالبيت")])
    assert _texts(out) == ["ب", "البيت"]


def test_splits_lam_lam_special_case():
    # للكتاب = li- + al-kitab, alif elided -> strip first lam, host keeps reduced article
    out = split_proclitics([_raw("للكتاب")])
    assert _texts(out) == ["ل", "لكتاب"]


def test_does_not_split_bare_waw_plus_radical():
    out = split_proclitics([_raw("وكتاب")])
    assert _texts(out) == ["وكتاب"]


def test_does_not_split_radical_initial_words():
    for word in ("وزير", "باب", "كتاب"):
        out = split_proclitics([_raw(word)])
        assert _texts(out) == [word], word


def test_does_not_split_short_article_like_token():
    # "ال" alone (length 2) must not split into ["ال", ""]
    out = split_proclitics([_raw("ال")])
    assert _texts(out) == ["ال"]


def test_does_not_split_short_lam_lam_token():
    # "لل" alone (length 2) must not split into ["ل", "ل"]
    out = split_proclitics([_raw("لل")])
    assert _texts(out) == ["لل"]


def test_splits_kaf_before_article():
    out = split_proclitics([_raw("كالكتاب")])
    assert _texts(out) == ["ك", "الكتاب"]
    assert "proclitic" in out[0].flags
    assert "compound_part" in out[1].flags


def test_spans_are_contiguous_after_split():
    out = split_proclitics([_raw("الكتاب", start=10)])
    assert out[0].span == (10, 12)   # ال
    assert out[1].span == (12, 16)   # كتاب


def test_unrelated_token_passes_through():
    out = split_proclitics([_raw("محمد")])
    assert _texts(out) == ["محمد"]
