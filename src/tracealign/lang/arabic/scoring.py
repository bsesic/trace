"""Arabic scoring-tier predicates."""

from __future__ import annotations

from rapidfuzz.fuzz import ratio

from tracealign.lang.base import LanguagePack, ScoringTier, TierResult
from tracealign.model import Reason, Token


def exact_predicate(a: Token, b: Token, pack: LanguagePack) -> TierResult | None:
    if a.raw == b.raw:
        return TierResult(score=1.0)
    return None


def diacritics_stripped_predicate(
    a: Token, b: Token, pack: LanguagePack
) -> TierResult | None:
    if a.text == b.text and a.raw != b.raw:
        return TierResult(score=0.95)
    return None


def orthographic_variant_predicate(
    a: Token, b: Token, pack: LanguagePack
) -> TierResult | None:
    sk_a = a.representations.get("skeleton")
    sk_b = b.representations.get("skeleton")
    if sk_a is None or sk_b is None:
        return None
    if sk_a == sk_b and a.text != b.text:
        return TierResult(score=0.90, details={"layer": "skeleton"})
    return None


def orthographic_predicate(
    a: Token,
    b: Token,
    pack: LanguagePack,
    *,
    threshold: float = 0.6,
) -> TierResult | None:
    r = ratio(a.text, b.text) / 100.0
    if r < threshold:
        return None
    return TierResult(score=r * 0.9, details={"layer": "fuzzy", "ratio": r})


def arabic_scoring_tiers() -> list[ScoringTier]:
    return [
        ScoringTier(reason=Reason.EXACT, predicate=exact_predicate),
        ScoringTier(
            reason=Reason.DIACRITICS_STRIPPED,
            predicate=diacritics_stripped_predicate,
        ),
        ScoringTier(
            reason=Reason.ORTHOGRAPHIC_VARIANT,
            predicate=orthographic_variant_predicate,
        ),
        ScoringTier(reason=Reason.ORTHOGRAPHIC, predicate=orthographic_predicate),
    ]
