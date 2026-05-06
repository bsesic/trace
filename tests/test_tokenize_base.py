"""Tests for the tokenizer base types and default rules."""

from dataclasses import is_dataclass

from tracealign.tokenize.base import (
    DEFAULT_EDITORIAL_RULES,
    EditorialBracketRules,
    RawToken,
)


def test_rawtoken_is_dataclass():
    assert is_dataclass(RawToken)
    rt = RawToken(raw="abc", span=(0, 3), flags=set())
    assert rt.raw == "abc"
    assert rt.span == (0, 3)
    assert rt.flags == set()


def test_editorial_bracket_rules_is_dataclass():
    assert is_dataclass(EditorialBracketRules)
    rules = EditorialBracketRules(pairs=[], lacuna_markers=[])
    assert rules.pairs == []


def test_default_editorial_rules_have_expected_pairs():
    flags = {flag for _open, _close, flag in DEFAULT_EDITORIAL_RULES.pairs}
    assert "reconstructed" in flags
    assert "deletion" in flags
    assert "insertion" in flags
    assert "abbreviation_expanded" in flags


def test_default_editorial_rules_have_lacuna_markers():
    assert "…" in DEFAULT_EDITORIAL_RULES.lacuna_markers
