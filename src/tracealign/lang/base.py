"""LanguagePack ABC and scoring tier types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

from tracealign.model import Lexica, Reason, Token
from tracealign.tokenize.base import (
    DEFAULT_EDITORIAL_RULES,
    EditorialBracketRules,
    RawToken,
)


@dataclass
class TierResult:
    score: float
    details: dict[str, Any] | None = None


@dataclass
class ScoringTier:
    reason: Reason
    predicate: Callable[[Token, Token, "LanguagePack"], TierResult | None]


class LanguagePack(ABC):
    code: str
    aliases: tuple[str, ...] = ()
    version: str
    word_chars: str = ""
    mid_word_chars: str = ""
    editorial_rules: EditorialBracketRules = DEFAULT_EDITORIAL_RULES
    lexica: Lexica  # subclasses must set this in __init__

    def post_tokenize(self, raws: list[RawToken]) -> list[RawToken]:
        return raws

    @abstractmethod
    def normalize(self, raw: RawToken) -> Token:
        ...

    @abstractmethod
    def scoring_tiers(self) -> list[ScoringTier]:
        ...
