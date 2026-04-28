"""Pydantic data model for TRACE."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Reason(str, Enum):
    EXACT = "exact"
    NIQQUD_STRIPPED = "niqqud_stripped"
    PLENE_DEFECTIVE = "plene_defective"
    ABBREVIATION = "abbreviation"
    ORTHOGRAPHIC = "orthographic"
    SCRIPT_VARIANT = "script_variant"
    INSERTION = "insertion"
    OMISSION = "omission"
    NO_MATCH = "no_match"


class Token(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    position: int
    raw: str
    text: str
    representations: dict[str, str] = Field(default_factory=dict)
    flags: set[str] = Field(default_factory=set)
    source_span: tuple[int, int] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Match(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token_a: Token | None
    token_b: Token | None
    score: float
    reason: Reason
    details: dict[str, Any] | None = None


class AlignmentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    matches: list[Match]
    seq_a_meta: dict[str, Any] = Field(default_factory=dict)
    seq_b_meta: dict[str, Any] = Field(default_factory=dict)
    total_score: float
    summary: dict[Reason, int]
    params: dict[str, Any]


@dataclass
class Lexica:
    abbreviations: dict[str, list[str]] = field(default_factory=dict)
    plene_defective_pairs: list[tuple[str, str]] = field(default_factory=list)

    def merge(self, other: "Lexica") -> "Lexica":
        merged_abbrev = dict(self.abbreviations)
        for key, vals in other.abbreviations.items():
            merged_abbrev.setdefault(key, list(vals))
        merged_pairs = list(self.plene_defective_pairs)
        for pair in other.plene_defective_pairs:
            if pair not in merged_pairs:
                merged_pairs.append(pair)
        return Lexica(
            abbreviations=merged_abbrev,
            plene_defective_pairs=merged_pairs,
        )
