"""Generic tiered-similarity scoring loop."""

from __future__ import annotations

from tracealign.lang.base import LanguagePack
from tracealign.model import Match, Reason, Token


def tiered_score(a: Token, b: Token, pack: LanguagePack) -> Match:
    for tier in pack.scoring_tiers():
        result = tier.predicate(a, b, pack)
        if result is not None:
            return Match(
                token_a=a,
                token_b=b,
                score=result.score,
                reason=tier.reason,
                details=result.details,
            )
    return Match(token_a=a, token_b=b, score=0.0, reason=Reason.NO_MATCH)
