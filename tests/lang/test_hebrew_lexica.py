"""Tests for Hebrew seed lexica and Lexica.load."""

from pathlib import Path

from tracealign.lang.hebrew.pack import HebrewLanguagePack, default_hebrew_lexica
from tracealign.model import Lexica


def test_default_hebrew_lexica_loaded_with_some_entries():
    lex = default_hebrew_lexica()
    assert isinstance(lex, Lexica)
    assert len(lex.abbreviations) >= 5
    assert len(lex.plene_defective_pairs) >= 1


def test_lexica_load_from_json_files(tmp_path: Path):
    abbrev_path = tmp_path / "abbrev.json"
    abbrev_path.write_text('{"x": ["X expansion"]}', encoding="utf-8")
    pleen_path = tmp_path / "plene.json"
    pleen_path.write_text('[["a", "b"], ["c", "d"]]', encoding="utf-8")
    lex = Lexica.load({"abbreviations": abbrev_path, "plene_defective_pairs": pleen_path})
    assert lex.abbreviations == {"x": ["X expansion"]}
    assert ("a", "b") in lex.plene_defective_pairs
    assert ("c", "d") in lex.plene_defective_pairs


def test_lexica_load_with_missing_keys_is_empty():
    lex = Lexica.load({})
    assert lex.abbreviations == {}
    assert lex.plene_defective_pairs == []


def test_lexica_load_accepts_string_paths(tmp_path: Path):
    abbrev_path = tmp_path / "abbrev.json"
    abbrev_path.write_text('{"y": ["Y expansion"]}', encoding="utf-8")
    lex = Lexica.load({"abbreviations": str(abbrev_path)})
    assert lex.abbreviations == {"y": ["Y expansion"]}


def test_pack_uses_default_lexica_when_none_provided():
    pack = HebrewLanguagePack()
    assert pack.lexica.abbreviations  # non-empty
