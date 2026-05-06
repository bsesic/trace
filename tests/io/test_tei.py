"""Tests for the TEI XML importer."""

from pathlib import Path

from tracealign.io.tei import load


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_tei_with_w_tags_each_w_is_one_token():
    tokens = load(FIXTURE_DIR / "tei_with_w.xml", lang="hbo")
    assert [t.text for t in tokens] == ["שלום", "עולם"]


def test_tei_flow_text_runs_through_plaintext_tokenizer():
    tokens = load(FIXTURE_DIR / "tei_flow.xml", lang="hbo")
    assert [t.text for t in tokens] == ["שלום", "עולם"]


def test_tei_load_from_string():
    xml = (FIXTURE_DIR / "tei_with_w.xml").read_text(encoding="utf-8")
    tokens = load(xml, lang="hbo")
    assert len(tokens) == 2
