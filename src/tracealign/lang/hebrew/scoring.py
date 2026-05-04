"""Hebrew scoring-tier predicates."""

from __future__ import annotations

from rapidfuzz.fuzz import ratio

from tracealign.lang.base import LanguagePack, ScoringTier, TierResult
from tracealign.lang.hebrew.normalize import WAW, YOD
from tracealign.model import Reason, Token


def exact_predicate(a: Token, b: Token, pack: LanguagePack) -> TierResult | None:
    if a.raw == b.raw:
        return TierResult(score=1.0)
    return None


def niqqud_stripped_predicate(a: Token, b: Token, pack: LanguagePack) -> TierResult | None:
    if a.text == b.text and a.raw != b.raw:
        return TierResult(score=0.95)
    return None


def _is_yod_or_waw_only_diff(text_a: str, text_b: str) -> bool:
    if abs(len(text_a) - len(text_b)) != 1:
        return False
    longer, shorter = (text_a, text_b) if len(text_a) > len(text_b) else (text_b, text_a)
    for i, ch in enumerate(longer):
        if ch in (YOD, WAW) and longer[:i] + longer[i + 1:] == shorter:
            return True
    return False


def plene_defective_predicate(a: Token, b: Token, pack: LanguagePack) -> TierResult | None:
    sk_a = a.representations.get("skeleton")
    sk_b = b.representations.get("skeleton")
    if sk_a is None or sk_b is None:
        return None
    if sk_a != sk_b:
        return None
    if a.text == b.text:
        return None
    if _is_yod_or_waw_only_diff(a.text, b.text):
        return TierResult(score=0.85, details={"layer": "skeleton"})
    return None


def abbreviation_predicate(a: Token, b: Token, pack: LanguagePack) -> TierResult | None:
    """1:1 case only. 1:n span matches are handled by the aligner's lookahead."""
    for candidate_token, other in ((a, b), (b, a)):
        if "abbreviation" not in candidate_token.flags:
            continue
        candidates = candidate_token.metadata.get("abbrev_candidates", [])
        for cand in candidates:
            if cand == other.text:
                return TierResult(
                    score=0.85,
                    details={"layer": "abbreviation", "resolution": cand},
                )
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
    return TierResult(
        score=r * 0.9,
        details={"layer": "orthographic", "ratio": r},
    )


def hebrew_scoring_tiers() -> list[ScoringTier]:
    return [
        ScoringTier(reason=Reason.EXACT, predicate=exact_predicate),
        ScoringTier(reason=Reason.NIQQUD_STRIPPED, predicate=niqqud_stripped_predicate),
        ScoringTier(reason=Reason.PLENE_DEFECTIVE, predicate=plene_defective_predicate),
        ScoringTier(reason=Reason.ABBREVIATION, predicate=abbreviation_predicate),
        ScoringTier(reason=Reason.ORTHOGRAPHIC, predicate=orthographic_predicate),
    ]
