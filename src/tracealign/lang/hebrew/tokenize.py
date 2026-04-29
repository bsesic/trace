"""Hebrew-specific tokenizer hooks."""

from __future__ import annotations

from tracealign.tokenize.base import RawToken

MAQQEF = "־"  # U+05BE Hebrew punctuation maqaf
HEB_GERSHAYIM = "\""
HEB_GERESH = "'"

# Hebrew mid-word characters: gershayim, geresh, and maqqef. The generic
# splitter does not break tokens at these characters; the maqqef post-pass
# below handles compound splitting after pretokenize.
HEB_MID_WORD_CHARS = HEB_GERSHAYIM + HEB_GERESH + MAQQEF


def split_maqqef_compounds(raws: list[RawToken]) -> list[RawToken]:
    """Split tokens containing U+05BE into multiple parts."""
    out: list[RawToken] = []
    for r in raws:
        if MAQQEF not in r.raw:
            out.append(r)
            continue
        cursor = r.span[0]
        parts = r.raw.split(MAQQEF)
        for part in parts:
            start = cursor
            end = cursor + len(part)
            cursor = end + 1  # skip the maqqef itself
            flags = set(r.flags)
            flags.add("compound_part")
            out.append(RawToken(raw=part, span=(start, end), flags=flags))
    return out
