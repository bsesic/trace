"""Language-agnostic plaintext pretokenizer.

Performs stages 1-4 of the tokenizer pipeline:
1. NFC normalization
2. Editorial-marker scan (bracket pairs + lacuna markers)
3. Whitespace + punctuation split
4. Marker reattach as flags on the resulting RawTokens
"""

from __future__ import annotations

import unicodedata

from tracealign.tokenize.base import (
    DEFAULT_EDITORIAL_RULES,
    EditorialBracketRules,
    RawToken,
)

_DEFAULT_PUNCT = ",.;:!?،؛"


def _scan_markers(
    text: str,
    rules: EditorialBracketRules,
) -> tuple[list[tuple[int, int, str]], list[tuple[int, int]]]:
    """Return (bracket_spans, lacuna_spans) over the raw text.

    bracket_spans: list of (content_start, content_end, flag) covering the
    text *inside* the brackets.
    lacuna_spans: list of (start, end) covering the lacuna marker itself.
    """
    bracket_spans: list[tuple[int, int, str]] = []
    lacuna_spans: list[tuple[int, int]] = []
    i = 0
    while i < len(text):
        matched = False
        for marker in rules.lacuna_markers:
            if text.startswith(marker, i):
                lacuna_spans.append((i, i + len(marker)))
                i += len(marker)
                matched = True
                break
        if matched:
            continue
        for open_b, close_b, flag in rules.pairs:
            if text.startswith(open_b, i):
                close_idx = text.find(close_b, i + len(open_b))
                if close_idx != -1:
                    content_start = i + len(open_b)
                    content_end = close_idx
                    bracket_spans.append((content_start, content_end, flag))
                    i = close_idx + len(close_b)
                    matched = True
                    break
        if matched:
            continue
        i += 1
    return bracket_spans, lacuna_spans


def _is_word_char(ch: str, mid_word_chars: str, punct: str) -> bool:
    if ch.isspace():
        return False
    if ch in punct:
        return False
    if ch in mid_word_chars:
        return True
    cat = unicodedata.category(ch)
    return cat[0] in {"L", "N", "M"}


def pretokenize(
    text: str,
    *,
    mid_word_chars: str = "",
    punct: str = _DEFAULT_PUNCT,
    rules: EditorialBracketRules = DEFAULT_EDITORIAL_RULES,
) -> list[RawToken]:
    """Stages 1-4 of the tokenizer pipeline.

    Returns a list of RawTokens with editorial-marker flags attached.
    Language-pack hooks (post_tokenize, normalize) run on the output.
    """
    text = unicodedata.normalize("NFC", text)
    bracket_spans, lacuna_spans = _scan_markers(text, rules)

    bracket_lookup: dict[int, str] = {}
    for cs, ce, flag in bracket_spans:
        for k in range(cs, ce):
            bracket_lookup[k] = flag
    bracket_skip: set[int] = set()
    for cs, ce, _flag in bracket_spans:
        bracket_skip.add(cs - 1)
        bracket_skip.add(ce)

    lacuna_skip: set[int] = set()
    lacuna_starts: dict[int, tuple[int, int]] = {}
    for ls, le in lacuna_spans:
        lacuna_starts[ls] = (ls, le)
        for k in range(ls, le):
            lacuna_skip.add(k)

    tokens: list[RawToken] = []
    i = 0
    n = len(text)
    while i < n:
        if i in lacuna_starts:
            ls, le = lacuna_starts[i]
            tokens.append(RawToken(raw="", span=(ls, le), flags={"lacuna"}))
            i = le
            continue
        if i in bracket_skip:
            i += 1
            continue
        ch = text[i]
        if not _is_word_char(ch, mid_word_chars, punct):
            i += 1
            continue
        start = i
        while i < n and i not in bracket_skip and i not in lacuna_skip and _is_word_char(
            text[i], mid_word_chars, punct
        ):
            i += 1
        end = i
        flags: set[str] = set()
        for k in range(start, end):
            flag = bracket_lookup.get(k)
            if flag is not None:
                flags.add(flag)
        tokens.append(RawToken(raw=text[start:end], span=(start, end), flags=flags))
    return tokens
