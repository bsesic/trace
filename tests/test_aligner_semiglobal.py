"""Tests for semi-global alignment (free terminal gaps)."""

from tracealign.align.needleman_wunsch import AlignerConfig, align_sequences
from tracealign.lang.hebrew.normalize import skeleton
from tracealign.lang.hebrew.pack import HebrewLanguagePack
from tracealign.model import Reason, Token


def _tok(text: str, position: int) -> Token:
    return Token(
        id=f"x:{position:06d}",
        position=position,
        raw=text,
        text=text,
        representations={"skeleton": skeleton(text)},
    )


def _seq(words: list[str]) -> list[Token]:
    return [_tok(w, i) for i, w in enumerate(words)]


def test_fragment_in_middle_no_terminal_penalty():
    full = _seq(["pre1", "pre2", "core1", "core2", "post1", "post2"])
    fragment = _seq(["core1", "core2"])
    cfg = AlignerConfig(semi_global_a=True, semi_global_b=True, abbrev_lookahead=False)
    matches = align_sequences(fragment, full, HebrewLanguagePack(), cfg)
    exact = [m for m in matches if m.reason == Reason.EXACT]
    assert len(exact) == 2
    # The fragment is fully consumed by core matches; INSERTION (gap-in-full)
    # for the fragment's tokens should not appear.
    insertion_count = sum(1 for m in matches if m.reason == Reason.INSERTION)
    assert insertion_count == 0


def test_global_aligns_have_rim_gaps():
    full = _seq(["pre", "core", "post"])
    fragment = _seq(["core"])
    cfg_global = AlignerConfig(semi_global_a=False, semi_global_b=False, abbrev_lookahead=False)
    matches_global = align_sequences(fragment, full, HebrewLanguagePack(), cfg_global)
    # In global mode, the rim non-matches still cost; we expect OMISSIONs at start AND end.
    omission_count = sum(1 for m in matches_global if m.reason == Reason.OMISSION)
    assert omission_count == 2
