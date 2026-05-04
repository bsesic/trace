"""Tests for Hebrew scoring-tier predicates."""

import pytest

from tracealign.lang.hebrew.pack import HebrewLanguagePack
from tracealign.lang.hebrew.scoring import (
    abbreviation_predicate,
    exact_predicate,
    niqqud_stripped_predicate,
    orthographic_predicate,
    plene_defective_predicate,
)
from tracealign.lang.hebrew.normalize import skeleton
from tracealign.model import Reason, Token


def _tok(text: str, raw: str | None = None, **extra) -> Token:
    return Token(
        id=f"x:{0:06d}",
        position=0,
        raw=raw if raw is not None else text,
        text=text,
        representations={"skeleton": skeleton(text)},
        **extra,
    )


def test_exact_predicate_hits_on_raw_equality():
    a = _tok("רבי", raw="רַבִּי")
    b = _tok("רבי", raw="רַבִּי")
    res = exact_predicate(a, b, HebrewLanguagePack())
    assert res is not None
    assert res.score == 1.0


def test_exact_predicate_misses_on_raw_diff():
    a = _tok("רבי", raw="רַבִּי")
    b = _tok("רבי", raw="רבי")
    assert exact_predicate(a, b, HebrewLanguagePack()) is None


def test_niqqud_stripped_predicate():
    a = _tok("רבי", raw="רַבִּי")
    b = _tok("רבי", raw="רבי")
    res = niqqud_stripped_predicate(a, b, HebrewLanguagePack())
    assert res is not None
    assert res.score == pytest.approx(0.95)


def test_plene_defective_predicate_hits_on_yod_difference():
    a = _tok("דויד")
    b = _tok("דוד")
    res = plene_defective_predicate(a, b, HebrewLanguagePack())
    assert res is not None
    assert res.score == pytest.approx(0.85)


def test_plene_defective_predicate_misses_on_other_difference():
    a = _tok("דדה")
    b = _tok("דדי")
    assert plene_defective_predicate(a, b, HebrewLanguagePack()) is None


def test_abbreviation_predicate_1to1():
    a = _tok("ר\"י", flags={"abbreviation"}, metadata={"abbrev_candidates": ["רבי"]})
    b = _tok("רבי")
    res = abbreviation_predicate(a, b, HebrewLanguagePack())
    assert res is not None
    assert res.score == pytest.approx(0.85)


def test_abbreviation_predicate_misses_when_no_candidate_matches():
    a = _tok("ר\"י", flags={"abbreviation"}, metadata={"abbrev_candidates": ["רבי ישמעאל"]})
    b = _tok("רבי")
    assert abbreviation_predicate(a, b, HebrewLanguagePack()) is None


def test_orthographic_predicate_high_similarity():
    a = _tok("שלום")
    b = _tok("שלים")
    res = orthographic_predicate(a, b, HebrewLanguagePack())
    assert res is not None
    assert 0.0 < res.score <= 0.9


def test_orthographic_predicate_low_similarity_misses():
    a = _tok("שלום")
    b = _tok("xyz")
    assert orthographic_predicate(a, b, HebrewLanguagePack()) is None


def test_pack_scoring_tiers_in_order():
    tiers = HebrewLanguagePack().scoring_tiers()
    reasons = [t.reason for t in tiers]
    assert reasons == [
        Reason.EXACT,
        Reason.NIQQUD_STRIPPED,
        Reason.PLENE_DEFECTIVE,
        Reason.ABBREVIATION,
        Reason.ORTHOGRAPHIC,
    ]
