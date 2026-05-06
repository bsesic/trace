"""Tokenizer protocol types and default editorial-marker rules."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RawToken:
    raw: str
    span: tuple[int, int]
    flags: set[str] = field(default_factory=set)


@dataclass
class EditorialBracketRules:
    pairs: list[tuple[str, str, str]]
    lacuna_markers: list[str]


DEFAULT_EDITORIAL_RULES = EditorialBracketRules(
    pairs=[
        ("[", "]", "reconstructed"),
        ("⟦", "⟧", "deletion"),
        ("〈", "〉", "insertion"),
        ("(", ")", "abbreviation_expanded"),
    ],
    lacuna_markers=["…", "[…]"],
)
