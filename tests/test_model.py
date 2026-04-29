"""Tests for Pydantic data model in trace.model."""

import pytest
from dataclasses import is_dataclass
from pydantic import ValidationError

from trace.model import AlignmentResult, Lexica, Match, Reason, Token


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


def test_alignment_result_basic():
    a = Token(id="A:0", position=0, raw="x", text="x")
    b = Token(id="B:0", position=0, raw="x", text="x")
    m = Match(token_a=a, token_b=b, score=1.0, reason=Reason.EXACT)
    r = AlignmentResult(
        matches=[m],
        total_score=1.0,
        summary={Reason.EXACT: 1},
        params={"trace_version": "0.1.0", "language_pack_version": "hbo-0.1.0"},
    )
    assert r.seq_a_meta == {}
    assert r.seq_b_meta == {}
    assert r.summary[Reason.EXACT] == 1


def test_alignment_result_round_trip():
    a = Token(id="A:0", position=0, raw="x", text="x")
    b = Token(id="B:0", position=0, raw="x", text="x")
    m = Match(token_a=a, token_b=b, score=1.0, reason=Reason.EXACT)
    r = AlignmentResult(
        matches=[m],
        seq_a_meta={"witness_id": "W1"},
        total_score=1.0,
        summary={Reason.EXACT: 1},
        params={"lang": "hbo"},
    )
    payload = r.model_dump_json()
    restored = AlignmentResult.model_validate_json(payload)
    assert restored.matches[0].score == 1.0
    assert restored.seq_a_meta == {"witness_id": "W1"}


def test_lexica_is_dataclass_with_defaults():
    assert is_dataclass(Lexica)
    lex = Lexica()
    assert lex.abbreviations == {}
    assert lex.plene_defective_pairs == []


def test_lexica_merge():
    a = Lexica(
        abbreviations={"ר\"י": ["רבי ישמעאל"]},
        plene_defective_pairs=[("דויד", "דוד")],
    )
    b = Lexica(
        abbreviations={"רשב\"י": ["רבי שמעון בן יוחאי"]},
        plene_defective_pairs=[("משיח", "מאשיח")],
    )
    merged = a.merge(b)
    assert "ר\"י" in merged.abbreviations
    assert "רשב\"י" in merged.abbreviations
    assert ("דויד", "דוד") in merged.plene_defective_pairs
    assert ("משיח", "מאשיח") in merged.plene_defective_pairs


def test_lexica_merge_does_not_mutate_inputs():
    a = Lexica(abbreviations={"x": ["X"]})
    b = Lexica(abbreviations={"y": ["Y"]})
    a.merge(b)
    assert "y" not in a.abbreviations
    assert "x" not in b.abbreviations


def test_lexica_merge_combines_overlapping_abbreviation_keys():
    a = Lexica(abbreviations={"ר\"י": ["רבי ישמעאל", "רבי יהודה"]})
    b = Lexica(abbreviations={"ר\"י": ["רבי יוסי"]})
    merged = a.merge(b)
    assert merged.abbreviations["ר\"י"] == ["רבי ישמעאל", "רבי יהודה", "רבי יוסי"]


def test_lexica_merge_dedupes_overlapping_expansions():
    a = Lexica(abbreviations={"ר\"י": ["רבי ישמעאל"]})
    b = Lexica(abbreviations={"ר\"י": ["רבי ישמעאל", "רבי יוסי"]})
    merged = a.merge(b)
    assert merged.abbreviations["ר\"י"] == ["רבי ישמעאל", "רבי יוסי"]
