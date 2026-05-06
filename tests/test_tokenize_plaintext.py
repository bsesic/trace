"""Tests for the language-agnostic plaintext pretokenizer."""

from tracealign.tokenize.base import DEFAULT_EDITORIAL_RULES
from tracealign.tokenize.plaintext import pretokenize


def test_simple_whitespace_split():
    raws = pretokenize("hello world")
    assert [r.raw for r in raws] == ["hello", "world"]
    assert raws[0].span == (0, 5)
    assert raws[1].span == (6, 11)


def test_unicode_nfc_applied():
    # combining acute on "e" -> precomposed é
    raws = pretokenize("café")
    assert raws[0].raw == "café"


def test_punctuation_splits_words():
    raws = pretokenize("hello, world.")
    assert [r.raw for r in raws] == ["hello", "world"]


def test_mid_word_chars_keep_token_intact():
    # a quote in the middle of a Hebrew-shaped abbreviation must stay attached
    raws = pretokenize("ר\"י", mid_word_chars="\"'")
    assert [r.raw for r in raws] == ["ר\"י"]


def test_reconstructed_brackets_become_flag():
    raws = pretokenize("[שלום]")
    assert len(raws) == 1
    assert raws[0].raw == "שלום"
    assert "reconstructed" in raws[0].flags


def test_lacuna_marker_yields_lacuna_token():
    raws = pretokenize("alpha … beta")
    raw_strings = [r.raw for r in raws]
    assert "alpha" in raw_strings
    assert "beta" in raw_strings
    lacuna_tokens = [r for r in raws if "lacuna" in r.flags]
    assert len(lacuna_tokens) == 1
    assert lacuna_tokens[0].raw == ""


def test_deletion_brackets_become_flag():
    raws = pretokenize("⟦abc⟧")
    assert raws[0].raw == "abc"
    assert "deletion" in raws[0].flags


def test_custom_rules_override_defaults():
    custom = DEFAULT_EDITORIAL_RULES
    raws = pretokenize("hello", rules=custom)
    assert raws[0].raw == "hello"
