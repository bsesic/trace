"""Verify affine gap penalties: a single block insertion is cheaper than scattered mismatches."""

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


def test_block_insertion_treated_as_single_extended_gap():
    a = _seq(["x1", "x2", "y1", "y2", "y3", "y4", "y5", "z1", "z2"])
    b = _seq(["x1", "x2", "z1", "z2"])  # the y-block is missing
    cfg = AlignerConfig(semi_global_a=False, semi_global_b=False, abbrev_lookahead=False)
    matches = align_sequences(a, b, HebrewLanguagePack(), cfg)
    insertion_runs: list[int] = []
    run = 0
    for m in matches:
        if m.reason == Reason.INSERTION:
            run += 1
        else:
            if run > 0:
                insertion_runs.append(run)
            run = 0
    if run > 0:
        insertion_runs.append(run)
    # A clean affine model gives one contiguous run of 5 INSERTIONs covering the y-block.
    assert any(r == 5 for r in insertion_runs)
