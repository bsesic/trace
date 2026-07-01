"""ArabicLanguagePack."""

from __future__ import annotations

from tracealign.lang.arabic.normalize import skeleton, strip_tashkil
from tracealign.lang.arabic.tokenize import split_proclitics
from tracealign.lang.base import LanguagePack, ScoringTier
from tracealign.model import Lexica, Token
from tracealign.tokenize.base import RawToken


class ArabicLanguagePack(LanguagePack):
    code = "ara"
    aliases = ("arabic",)
    version = "ara-0.1.0"
    word_chars = ""
    mid_word_chars = ""

    def __init__(self, lexica: Lexica | None = None) -> None:
        # Conservative splitting needs no guard lexicon; an empty Lexica is
        # intentional (see design spec).
        self.lexica = lexica if lexica is not None else Lexica()

    def post_tokenize(self, raws: list[RawToken]) -> list[RawToken]:
        return split_proclitics(raws)

    def normalize(self, raw: RawToken) -> Token:
        # `id` and `position` are pack-local placeholders derived from the raw
        # character span; the public `tokenize()` overrides both with
        # sequence-index values keyed by `seq_label`.
        text = strip_tashkil(raw.raw)
        return Token(
            id=f"ara:{raw.span[0]:06d}",
            position=raw.span[0],
            raw=raw.raw,
            text=text,
            representations={"skeleton": skeleton(text)},
            flags=set(raw.flags),
            source_span=raw.span,
            metadata={},
        )

    def scoring_tiers(self) -> list[ScoringTier]:
        from tracealign.lang.arabic.scoring import arabic_scoring_tiers
        return arabic_scoring_tiers()
