"""End-to-end synthetic Hebrew alignment exercising every Reason."""

from pathlib import Path

import tracealign
from tracealign.model import Reason


FIX = Path(__file__).parent / "fixtures"


def _align():
    w1 = (FIX / "synthetic_w1.txt").read_text(encoding="utf-8").strip()
    w2 = (FIX / "synthetic_w2.txt").read_text(encoding="utf-8").strip()
    a = tracealign.tokenize(w1, lang="hbo", seq_label="W1")
    b = tracealign.tokenize(w2, lang="hbo", seq_label="W2")
    return tracealign.align(a, b, lang="hbo")


def test_synthetic_alignment_hits_all_expected_reasons():
    result = _align()
    seen = set(result.summary.keys())
    assert Reason.EXACT in seen
    assert Reason.NIQQUD_STRIPPED in seen
    assert Reason.PLENE_DEFECTIVE in seen
    assert Reason.ABBREVIATION in seen


def test_synthetic_alignment_abbreviation_has_primary_and_continuation():
    result = _align()
    primaries = [
        m for m in result.matches
        if m.reason == Reason.ABBREVIATION
        and m.details and m.details.get("role") == "primary"
    ]
    continuations = [
        m for m in result.matches
        if m.reason == Reason.ABBREVIATION
        and m.details and m.details.get("role") == "continuation"
    ]
    assert len(primaries) == 1
    assert len(continuations) == 1


def test_synthetic_alignment_total_score_in_unit_interval():
    result = _align()
    assert 0.0 <= result.total_score <= 1.0


def test_synthetic_alignment_summary_excludes_continuation_count():
    # The single continuation must NOT inflate summary[ABBREVIATION].
    result = _align()
    assert result.summary.get(Reason.ABBREVIATION, 0) == 1
