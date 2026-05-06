"""Tests for the eScriptorium JSON importer."""

import json
from pathlib import Path

from tracealign.io.escriptorium import load


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_load_returns_token_list():
    tokens = load(FIXTURE_DIR / "escriptorium_minimal.json", lang="hbo")
    texts = [t.text for t in tokens]
    assert "שלום" in texts
    assert "עולם" in texts
    assert "אמר" in texts


def test_load_preserves_metadata():
    tokens = load(FIXTURE_DIR / "escriptorium_minimal.json", lang="hbo")
    first = tokens[0]
    assert first.metadata["witness_id"] == "W1"
    assert first.metadata["surface_label"] == "fol. 12r"
    assert first.metadata["line_pk"] == 7


def test_load_from_dict():
    payload = json.loads(
        (FIXTURE_DIR / "escriptorium_minimal.json").read_text(encoding="utf-8")
    )
    tokens = load(payload, lang="hbo")
    assert tokens
    assert tokens[0].metadata["witness_id"] == "W1"


def test_load_handles_abbreviation():
    tokens = load(FIXTURE_DIR / "escriptorium_minimal.json", lang="hbo")
    abbreviated = [t for t in tokens if "abbreviation" in t.flags]
    assert any(t.text == "ר\"י" for t in abbreviated)
