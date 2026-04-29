"""HebrewLanguagePack — wires hooks together. Normalize and scoring come later."""

from __future__ import annotations

from tracealign.lang.base import LanguagePack, ScoringTier
from tracealign.lang.hebrew.tokenize import HEB_MID_WORD_CHARS, split_maqqef_compounds
from tracealign.model import Lexica, Token
from tracealign.tokenize.base import RawToken


class HebrewLanguagePack(LanguagePack):
    code = "hbo"
    aliases = ("hebrew", "he-anc")
    version = "hbo-0.1.0"
    word_chars = ""
    mid_word_chars = HEB_MID_WORD_CHARS

    def __init__(self, lexica: Lexica | None = None) -> None:
        self.lexica = lexica or Lexica()

    def post_tokenize(self, raws: list[RawToken]) -> list[RawToken]:
        return split_maqqef_compounds(raws)

    def normalize(self, raw: RawToken) -> Token:
        # Placeholder until Task 7. Returns a minimal Token so the ABC is satisfied.
        return Token(
            id=f"hbo:{raw.span[0]:06d}",
            position=raw.span[0],
            raw=raw.raw,
            text=raw.raw,
            flags=set(raw.flags),
        )

    def scoring_tiers(self) -> list[ScoringTier]:
        # Placeholder until Task 9.
        return []
