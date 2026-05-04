"""Tests for the generic tiered scoring loop."""

from tracealign.lang.hebrew.pack import HebrewLanguagePack
from tracealign.model import Reason, Token
from tracealign.score.tiered import tiered_score


def _tok(text: str, raw: str | None = None, **extra) -> Token:
    from tracealign.lang.hebrew.normalize import skeleton

    return Token(
        id=f"x:{0:06d}",
        position=0,
        raw=raw if raw is not None else text,
        text=text,
        representations={"skeleton": skeleton(text)},
        **extra,
    )


def test_tiered_score_exact():
    a = _tok("רבי")
    b = _tok("רבי")
    m = tiered_score(a, b, HebrewLanguagePack())
    assert m.reason == Reason.EXACT
    assert m.score == 1.0


def test_tiered_score_niqqud_stripped():
    a = _tok("רבי", raw="רַבִּי")
    b = _tok("רבי", raw="רבי")
    m = tiered_score(a, b, HebrewLanguagePack())
    assert m.reason == Reason.NIQQUD_STRIPPED


def test_tiered_score_plene_defective():
    a = _tok("דויד")
    b = _tok("דוד")
    m = tiered_score(a, b, HebrewLanguagePack())
    assert m.reason == Reason.PLENE_DEFECTIVE


def test_tiered_score_orthographic():
    a = _tok("שלום")
    b = _tok("שלים")
    m = tiered_score(a, b, HebrewLanguagePack())
    assert m.reason == Reason.ORTHOGRAPHIC


def test_tiered_score_no_match():
    a = _tok("שלום")
    b = _tok("xyz")
    m = tiered_score(a, b, HebrewLanguagePack())
    assert m.reason == Reason.NO_MATCH
    assert m.score == 0.0


def test_tiered_score_attaches_details_when_predicate_provides_them():
    a = _tok("דויד")
    b = _tok("דוד")
    m = tiered_score(a, b, HebrewLanguagePack())
    assert m.details is not None
    assert m.details["layer"] == "skeleton"
