"""Tests for Pydantic data model in trace.model."""

import pytest
from pydantic import ValidationError

from trace.model import Match, Reason, Token


def test_token_minimal_fields():
    t = Token(id="W1:000000", position=0, raw="שלום", text="שלום")
    assert t.representations == {}
    assert t.flags == set()
    assert t.metadata == {}
    assert t.source_span is None


def test_token_full_fields():
    t = Token(
        id="W1:000042",
        position=42,
        raw="רַבִּי",
        text="רבי",
        representations={"skeleton": "רב"},
        flags={"abbreviation"},
        source_span=(156, 161),
        metadata={"witness_id": "W1", "line_pk": 7},
    )
    assert t.flags == {"abbreviation"}
    assert t.representations["skeleton"] == "רב"


def test_token_id_required():
    with pytest.raises(ValidationError):
        Token(position=0, raw="x", text="x")


def test_reason_enum_values():
    assert Reason.EXACT.value == "exact"
    assert Reason.NIQQUD_STRIPPED.value == "niqqud_stripped"
    assert Reason.PLENE_DEFECTIVE.value == "plene_defective"
    assert Reason.ABBREVIATION.value == "abbreviation"
    assert Reason.ORTHOGRAPHIC.value == "orthographic"
    assert Reason.SCRIPT_VARIANT.value == "script_variant"
    assert Reason.INSERTION.value == "insertion"
    assert Reason.OMISSION.value == "omission"
    assert Reason.NO_MATCH.value == "no_match"


def test_match_basic():
    a = Token(id="A:0", position=0, raw="שלום", text="שלום")
    b = Token(id="B:0", position=0, raw="שלום", text="שלום")
    m = Match(token_a=a, token_b=b, score=1.0, reason=Reason.EXACT)
    assert m.score == 1.0
    assert m.reason == Reason.EXACT
    assert m.details is None


def test_match_gap_in_b():
    a = Token(id="A:0", position=0, raw="x", text="x")
    m = Match(token_a=a, token_b=None, score=0.0, reason=Reason.INSERTION)
    assert m.token_b is None


def test_match_with_details():
    a = Token(id="A:0", position=0, raw="ר\"י", text="ר\"י", flags={"abbreviation"})
    b = Token(id="B:0", position=0, raw="רבי", text="רבי")
    m = Match(
        token_a=a,
        token_b=b,
        score=0.85,
        reason=Reason.ABBREVIATION,
        details={"role": "primary", "expansion": "רבי ישמעאל", "span_size": 2},
    )
    assert m.details["role"] == "primary"
