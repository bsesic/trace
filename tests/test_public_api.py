"""Tests for the public API in tracealign.__init__."""

import tracealign
from tracealign.model import AlignmentResult, Reason


def test_tokenize_plaintext_hebrew():
    tokens = tracealign.tokenize("שלום עולם", lang="hbo")
    assert len(tokens) == 2
    assert tokens[0].text == "שלום"
    assert tokens[1].text == "עולם"
    assert tokens[0].position == 0
    assert tokens[1].position == 1


def test_tokenize_hebrew_handles_gershayim():
    tokens = tracealign.tokenize("ר\"י", lang="hbo")
    assert len(tokens) == 1
    assert "abbreviation" in tokens[0].flags


def test_tokenize_hebrew_splits_maqqef():
    tokens = tracealign.tokenize("אֶל־בֵּית", lang="hbo")
    assert len(tokens) == 2
    assert all("compound_part" in t.flags for t in tokens)


def test_tokenize_assigns_sequential_positions():
    tokens = tracealign.tokenize("a b c d", lang="hbo")
    assert [t.position for t in tokens] == [0, 1, 2, 3]


def test_tokenize_uses_seq_label_in_id():
    tokens = tracealign.tokenize("a b", lang="hbo", seq_label="W42")
    assert tokens[0].id.startswith("W42:")
    assert tokens[1].id.startswith("W42:")


def test_align_end_to_end():
    a = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="A")
    b = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="B")
    result = tracealign.align(a, b, lang="hbo")
    assert isinstance(result, AlignmentResult)
    assert result.summary[Reason.EXACT] == 2
    assert result.total_score == 1.0


def test_list_languages_includes_hebrew():
    assert "hbo" in tracealign.list_languages()
