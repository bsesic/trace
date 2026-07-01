"""Arabic-specific tokenizer hooks: conservative proclitic splitting."""

from __future__ import annotations

from tracealign.tokenize.base import RawToken

ALEF = "ا"
LAM = "ل"
ARTICLE = ALEF + LAM  # ال
# Single-letter proclitics that we split only when they precede the article.
_PROCLITIC_LETTERS = ("و", "ف", "ب", "ك")  # و ف ب ك


def _emit_split(r: RawToken, cut: int) -> list[RawToken]:
    """Split RawToken `r` at character offset `cut` into proclitic + host.

    Spans are contiguous (no separator character between Arabic proclitic
    and host).
    """
    start = r.span[0]
    proclitic = RawToken(
        raw=r.raw[:cut],
        span=(start, start + cut),
        flags=set(r.flags) | {"proclitic"},
    )
    host = RawToken(
        raw=r.raw[cut:],
        span=(start + cut, r.span[1]),
        flags=set(r.flags) | {"compound_part"},
    )
    return [proclitic, host]


def _split_one(r: RawToken) -> list[RawToken]:
    text = r.raw
    # Rule 2: single-letter proclitic + article (e.g. والـ, بالـ).
    # len > 3: proclitic + article (ال) + at least one host char
    if (
        len(text) > 3
        and text[0] in _PROCLITIC_LETTERS
        and text[1:3] == ARTICLE
    ):
        return _emit_split(r, 1)
    # Rule 3: li- + article with elided alif (للـ).
    if len(text) > 2 and text[0] == LAM and text[1] == LAM:
        return _emit_split(r, 1)
    # Rule 1: bare definite article.
    # len > 2: article (ال) + at least one host char
    if len(text) > 2 and text[:2] == ARTICLE:
        return _emit_split(r, 2)
    return [r]


def split_proclitics(raws: list[RawToken]) -> list[RawToken]:
    """Conservatively split Arabic proclitics off host words.

    Splits only on unambiguous signals: the definite article, single-letter
    proclitics that precede the article, and the li-+article (لل) contraction.
    Bare proclitic letters before a non-article host are left attached to
    avoid amputating word-initial radicals.
    """
    out: list[RawToken] = []
    for r in raws:
        out.extend(_split_one(r))
    return out
