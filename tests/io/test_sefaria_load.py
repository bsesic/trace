"""Tests for tracealign.io.sefaria.load."""

import json
from pathlib import Path
from unittest.mock import patch

from tracealign.io import sefaria
from tracealign.model import Token


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_load_single_segment_returns_tokens():
    payload = _load_fixture("sefaria_avot_1_davidson.json")
    with patch.object(sefaria, "_fetch_json", return_value=payload):
        tokens = sefaria.load(
            "Pirkei Avot 1:1",
            version="William Davidson Edition - Hebrew",
            seq_label="Davidson",
        )
    assert isinstance(tokens, list)
    assert tokens, "expected at least one token"
    assert all(isinstance(t, Token) for t in tokens)
    assert tokens[0].raw.startswith("מ")


def test_load_single_segment_passes_seq_label_through():
    payload = _load_fixture("sefaria_avot_1_davidson.json")
    with patch.object(sefaria, "_fetch_json", return_value=payload):
        tokens = sefaria.load(
            "Pirkei Avot 1:1",
            version="William Davidson Edition - Hebrew",
            seq_label="Davidson",
        )
    assert all(t.id.startswith("Davidson:") for t in tokens)
