"""Tests for Hebrew tokenizer hooks."""

from tracealign.lang.hebrew.tokenize import split_maqqef_compounds
from tracealign.tokenize.base import RawToken
from tracealign.tokenize.plaintext import pretokenize


def test_gershayim_keeps_token_intact_via_pretokenize_with_mid_word_chars():
    raws = pretokenize("ר\"י", mid_word_chars="\"'")
    assert [r.raw for r in raws] == ["ר\"י"]


def test_maqqef_split_two_parts():
    raws = [RawToken(raw="אֶל־בֵּית", span=(0, 9), flags=set())]
    out = split_maqqef_compounds(raws)
    assert len(out) == 2
    assert out[0].raw == "אֶל"
    assert out[1].raw == "בֵּית"
    assert "compound_part" in out[0].flags
    assert "compound_part" in out[1].flags


def test_maqqef_split_three_parts():
    raws = [RawToken(raw="a־b־c", span=(0, 5), flags=set())]
    out = split_maqqef_compounds(raws)
    assert [r.raw for r in out] == ["a", "b", "c"]
    assert all("compound_part" in r.flags for r in out)


def test_maqqef_split_preserves_other_flags():
    raws = [RawToken(raw="a־b", span=(0, 3), flags={"reconstructed"})]
    out = split_maqqef_compounds(raws)
    for part in out:
        assert "reconstructed" in part.flags
        assert "compound_part" in part.flags


def test_maqqef_split_passes_through_non_compound():
    raws = [RawToken(raw="hello", span=(0, 5), flags=set())]
    out = split_maqqef_compounds(raws)
    assert out == raws


def test_maqqef_split_preserves_spans():
    raws = [RawToken(raw="ab־cd", span=(10, 15), flags=set())]
    out = split_maqqef_compounds(raws)
    assert out[0].span == (10, 12)
    assert out[1].span == (13, 15)
