from tracealign.model import Reason
from tracealign.lang.arabic.scoring import arabic_scoring_tiers
from tracealign.model import Token


def test_arabic_reason_values_exist():
    assert Reason.DIACRITICS_STRIPPED.value == "diacritics_stripped"
    assert Reason.ORTHOGRAPHIC_VARIANT.value == "orthographic_variant"


def _tok(raw, text=None, skel=None):
    text = raw if text is None else text
    reps = {} if skel is None else {"skeleton": skel}
    return Token(id="t", position=0, raw=raw, text=text, representations=reps)


def _score(a, b):
    """Return (reason, TierResult) for the first matching tier, else None."""
    pack = object()
    for tier in arabic_scoring_tiers():
        result = tier.predicate(a, b, pack)
        if result is not None:
            return tier.reason, result
    return None


def test_exact_tier():
    reason, res = _score(_tok("كتاب"), _tok("كتاب"))
    assert reason == Reason.EXACT
    assert res.score == 1.0


def test_diacritics_stripped_tier():
    # same consonantal text, different raw (one vocalized)
    a = _tok("كَتَبَ", text="كتب")
    b = _tok("كتب", text="كتب")
    reason, res = _score(a, b)
    assert reason == Reason.DIACRITICS_STRIPPED
    assert res.score == 0.95


def test_orthographic_variant_tier():
    # different text, same skeleton (alif-hamza folding)
    a = _tok("أحمد", text="أحمد", skel="احمد")
    b = _tok("احمد", text="احمد", skel="احمد")
    reason, res = _score(a, b)
    assert reason == Reason.ORTHOGRAPHIC_VARIANT
    assert res.score == 0.90
    assert res.details["layer"] == "skeleton"


def test_orthographic_fuzzy_tier():
    a = _tok("كتاب", text="كتاب", skel="كتاب")
    b = _tok("كتيب", text="كتيب", skel="كتيب")
    reason, res = _score(a, b)
    assert reason == Reason.ORTHOGRAPHIC
    assert res.details["layer"] == "fuzzy"
    assert 0.0 < res.score < 0.9


def test_no_match_below_threshold():
    a = _tok("كتاب", text="كتاب", skel="كتاب")
    b = _tok("شمس", text="شمس", skel="شمس")
    assert _score(a, b) is None


def test_tier_order_and_reasons():
    tiers = arabic_scoring_tiers()
    assert [t.reason for t in tiers] == [
        Reason.EXACT,
        Reason.DIACRITICS_STRIPPED,
        Reason.ORTHOGRAPHIC_VARIANT,
        Reason.ORTHOGRAPHIC,
    ]
