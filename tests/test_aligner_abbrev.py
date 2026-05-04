"""Tests for abbreviation-span lookahead in the aligner."""

from tracealign.align.needleman_wunsch import AlignerConfig, align_sequences
from tracealign.lang.hebrew.normalize import skeleton
from tracealign.lang.hebrew.pack import HebrewLanguagePack
from tracealign.model import Reason, Token


def _abbrev(position: int) -> Token:
    return Token(
        id=f"a:{position:06d}",
        position=position,
        raw="ר\"י",
        text="ר\"י",
        representations={"skeleton": skeleton("ר\"י")},
        flags={"abbreviation"},
        metadata={"abbrev_candidates": ["רבי ישמעאל"]},
    )


def _word(text: str, position: int) -> Token:
    return Token(
        id=f"b:{position:06d}",
        position=position,
        raw=text,
        text=text,
        representations={"skeleton": skeleton(text)},
    )


def test_abbreviation_resolves_to_two_token_span():
    a = [_abbrev(0)]
    b = [_word("רבי", 0), _word("ישמעאל", 1)]
    cfg = AlignerConfig(semi_global_a=False, semi_global_b=False, abbrev_lookahead=True)
    matches = align_sequences(a, b, HebrewLanguagePack(), cfg)
    # Expect: 1 primary ABBREVIATION + 1 continuation = 2 matches total.
    assert len(matches) == 2
    primary = [m for m in matches if m.details and m.details.get("role") == "primary"]
    cont = [m for m in matches if m.details and m.details.get("role") == "continuation"]
    assert len(primary) == 1
    assert len(cont) == 1
    assert primary[0].reason == Reason.ABBREVIATION
    assert primary[0].details["expansion"] == "רבי ישמעאל"
    assert primary[0].details["span_size"] == 2
    assert cont[0].reason == Reason.ABBREVIATION
    assert cont[0].score == 0.0


def test_abbreviation_lookahead_disabled_falls_back_to_orthographic_or_no_match():
    a = [_abbrev(0)]
    b = [_word("רבי", 0), _word("ישמעאל", 1)]
    cfg = AlignerConfig(semi_global_a=False, semi_global_b=False, abbrev_lookahead=False)
    matches = align_sequences(a, b, HebrewLanguagePack(), cfg)
    primary = [m for m in matches if m.details and m.details.get("role") == "primary"]
    assert primary == []  # no abbreviation primary when lookahead is off


def test_abbreviation_lookahead_no_match_when_candidates_dont_match():
    a = [_abbrev(0)]
    b = [_word("רבי", 0), _word("יהודה", 1)]
    cfg = AlignerConfig(semi_global_a=False, semi_global_b=False, abbrev_lookahead=True)
    matches = align_sequences(a, b, HebrewLanguagePack(), cfg)
    primary = [m for m in matches if m.details and m.details.get("role") == "primary"]
    assert primary == []
