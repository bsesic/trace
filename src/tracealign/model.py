"""Pydantic data model for TRACE."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_PathLike = Path | Traversable | str


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

    @classmethod
    def load(cls, paths: dict[str, _PathLike]) -> "Lexica":
        import json

        def _as_readable(p: _PathLike) -> Any:
            return Path(p) if isinstance(p, str) else p

        abbreviations: dict[str, list[str]] = {}
        plene_defective_pairs: list[tuple[str, str]] = []

        ap = paths.get("abbreviations")
        if ap is not None:
            data = json.loads(_as_readable(ap).read_text(encoding="utf-8"))
            abbreviations = {k: list(v) for k, v in data.items()}

        pp = paths.get("plene_defective_pairs")
        if pp is not None:
            data = json.loads(_as_readable(pp).read_text(encoding="utf-8"))
            plene_defective_pairs = [tuple(item) for item in data]

        return cls(
            abbreviations=abbreviations,
            plene_defective_pairs=plene_defective_pairs,
        )

    def merge(self, other: "Lexica") -> "Lexica":
        merged_abbrev: dict[str, list[str]] = {
            k: list(v) for k, v in self.abbreviations.items()
        }
        for key, vals in other.abbreviations.items():
            target = merged_abbrev.setdefault(key, [])
            for v in vals:
                if v not in target:
                    target.append(v)
        merged_pairs = list(self.plene_defective_pairs)
        for pair in other.plene_defective_pairs:
            if pair not in merged_pairs:
                merged_pairs.append(pair)
        return Lexica(
            abbreviations=merged_abbrev,
            plene_defective_pairs=merged_pairs,
        )
