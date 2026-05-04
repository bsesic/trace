"""HebrewLanguagePack."""

from __future__ import annotations

from importlib import resources

from tracealign.lang.base import LanguagePack, ScoringTier
from tracealign.lang.hebrew.normalize import has_gershayim, skeleton, strip_niqqud
from tracealign.lang.hebrew.tokenize import HEB_MID_WORD_CHARS, split_maqqef_compounds
from tracealign.model import Lexica, Token
from tracealign.tokenize.base import RawToken


def default_hebrew_lexica() -> Lexica:
    data_pkg = resources.files("tracealign.lang.hebrew.data")
    return Lexica.load(
        {
            "abbreviations": data_pkg.joinpath("abbreviations.json"),
            "plene_defective_pairs": data_pkg.joinpath("plene_defective.json"),
        }
    )


class HebrewLanguagePack(LanguagePack):
    code = "hbo"
    aliases = ("hebrew", "he-anc")
    version = "hbo-0.1.0"
    word_chars = ""
    mid_word_chars = HEB_MID_WORD_CHARS

    def __init__(self, lexica: Lexica | None = None) -> None:
        self.lexica = lexica if lexica is not None else default_hebrew_lexica()

    def post_tokenize(self, raws: list[RawToken]) -> list[RawToken]:
        return split_maqqef_compounds(raws)

    def normalize(self, raw: RawToken) -> Token:
        text = strip_niqqud(raw.raw)
        flags = set(raw.flags)
        metadata: dict = {}
        if has_gershayim(raw.raw):
            flags.add("abbreviation")
        candidates = self.lexica.abbreviations.get(text)
        if candidates:
            flags.add("abbreviation")
            metadata["abbrev_candidates"] = list(candidates)
        return Token(
            id=f"hbo:{raw.span[0]:06d}",
            position=raw.span[0],
            raw=raw.raw,
            text=text,
            representations={"skeleton": skeleton(text)},
            flags=flags,
            source_span=raw.span,
            metadata=metadata,
        )

    def scoring_tiers(self) -> list[ScoringTier]:
        from tracealign.lang.hebrew.scoring import hebrew_scoring_tiers
        return hebrew_scoring_tiers()
