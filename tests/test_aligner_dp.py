"""Tests for the basic Gotoh DP aligner (global, no semi-global, no abbrev)."""

from tracealign.align.needleman_wunsch import AlignerConfig, align_sequences
from tracealign.lang.hebrew.normalize import skeleton
from tracealign.lang.hebrew.pack import HebrewLanguagePack
from tracealign.model import Reason, Token


def _tok(text: str, position: int, raw: str | None = None) -> Token:
    return Token(
        id=f"x:{position:06d}",
        position=position,
        raw=raw if raw is not None else text,
        text=text,
        representations={"skeleton": skeleton(text)},
    )


def _seq(words: list[str]) -> list[Token]:
    return [_tok(w, i) for i, w in enumerate(words)]


def test_identical_sequences_all_exact():
    a = _seq(["שלום", "עולם"])
    b = _seq(["שלום", "עולם"])
    cfg = AlignerConfig(semi_global_a=False, semi_global_b=False, abbrev_lookahead=False)
    matches = align_sequences(a, b, HebrewLanguagePack(), cfg)
    assert [m.reason for m in matches] == [Reason.EXACT, Reason.EXACT]


def test_single_substitution():
    a = _seq(["שלום", "עולם"])
    b = _seq(["שלים", "עולם"])
    cfg = AlignerConfig(semi_global_a=False, semi_global_b=False, abbrev_lookahead=False)
    matches = align_sequences(a, b, HebrewLanguagePack(), cfg)
    assert len(matches) == 2
    assert matches[1].reason == Reason.EXACT


def test_insertion_in_b():
    a = _seq(["שלום", "עולם"])
    b = _seq(["שלום", "ברוך", "עולם"])
    cfg = AlignerConfig(semi_global_a=False, semi_global_b=False, abbrev_lookahead=False)
    matches = align_sequences(a, b, HebrewLanguagePack(), cfg)
    reasons = [m.reason for m in matches]
    assert Reason.OMISSION in reasons


def test_deletion_from_b():
    a = _seq(["שלום", "ברוך", "עולם"])
    b = _seq(["שלום", "עולם"])
    cfg = AlignerConfig(semi_global_a=False, semi_global_b=False, abbrev_lookahead=False)
    matches = align_sequences(a, b, HebrewLanguagePack(), cfg)
    reasons = [m.reason for m in matches]
    assert Reason.INSERTION in reasons


def test_match_count_equals_path_length():
    a = _seq(["a", "b"])
    b = _seq(["a", "x", "b"])
    cfg = AlignerConfig(semi_global_a=False, semi_global_b=False, abbrev_lookahead=False)
    matches = align_sequences(a, b, HebrewLanguagePack(), cfg)
    assert 3 <= len(matches) <= 5
