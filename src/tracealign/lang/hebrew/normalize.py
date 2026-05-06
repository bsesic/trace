"""Hebrew normalization: niqqud strip and skeleton computation."""

from __future__ import annotations

import unicodedata

YOD = "י"
WAW = "ו"
GERSHAYIM = "\""
GERESH = "'"


def strip_niqqud(text: str) -> str:
    """Remove all combining marks (niqqud, te'amim) from `text`."""
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def skeleton(text_no_niqqud: str) -> str:
    """Remove yod and waw from a niqqud-free string."""
    return "".join(ch for ch in text_no_niqqud if ch not in (YOD, WAW))


def has_gershayim(text: str) -> bool:
    return GERSHAYIM in text or GERESH in text
