"""Pydantic data model for TRACE."""

from __future__ import annotations

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
