"""Tests for Hebrew normalize: niqqud strip, skeleton, abbrev candidates."""

from tracealign.lang.hebrew.normalize import strip_niqqud, skeleton
from tracealign.lang.hebrew.pack import HebrewLanguagePack
from tracealign.model import Lexica
from tracealign.tokenize.base import RawToken


def test_strip_niqqud_removes_combining_marks():
    assert strip_niqqud("רַבִּי") == "רבי"


def test_strip_niqqud_removes_teamim():
    assert strip_niqqud("בְּרֵאשִׁ֖ית") == "בראשית"


def test_strip_niqqud_passes_plain_text():
    assert strip_niqqud("שלום") == "שלום"


def test_skeleton_removes_yod_and_waw():
    assert skeleton("דויד") == "דד"
    assert skeleton("דוד") == "דד"


def test_skeleton_keeps_other_letters():
    assert skeleton("שלום") == "שלם"


def test_normalize_basic_token():
    pack = HebrewLanguagePack()
    raw = RawToken(raw="רַבִּי", span=(0, 5), flags=set())
    tok = pack.normalize(raw)
    assert tok.raw == "רַבִּי"
    assert tok.text == "רבי"
    assert tok.representations["skeleton"] == skeleton("רבי")
    assert "abbreviation" not in tok.flags


def test_normalize_preserves_existing_flags():
    pack = HebrewLanguagePack()
    raw = RawToken(raw="רבי", span=(0, 3), flags={"reconstructed"})
    tok = pack.normalize(raw)
    assert "reconstructed" in tok.flags


def test_normalize_detects_abbreviation_via_gershayim():
    pack = HebrewLanguagePack()
    raw = RawToken(raw="ר\"י", span=(0, 3), flags=set())
    tok = pack.normalize(raw)
    assert "abbreviation" in tok.flags


def test_normalize_populates_abbrev_candidates_from_lexicon():
    lex = Lexica(abbreviations={"ר\"י": ["רבי ישמעאל", "רבי יהודה"]})
    pack = HebrewLanguagePack(lexica=lex)
    raw = RawToken(raw="ר\"י", span=(0, 3), flags=set())
    tok = pack.normalize(raw)
    assert tok.metadata["abbrev_candidates"] == ["רבי ישמעאל", "רבי יהודה"]


def test_normalize_id_includes_position():
    pack = HebrewLanguagePack()
    raw = RawToken(raw="x", span=(42, 43), flags=set())
    tok = pack.normalize(raw)
    assert tok.position == 42
