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


def test_load_segments_returns_one_list_per_mishna():
    payload = _load_fixture("sefaria_avot_1_davidson.json")
    with patch.object(sefaria, "_fetch_json", return_value=payload):
        segments = sefaria.load_segments(
            "Pirkei Avot 1",
            version="William Davidson Edition - Hebrew",
            seq_label="Davidson",
        )
    assert len(segments) == 3
    assert all(isinstance(seg, list) for seg in segments)
    assert all(seg for seg in segments)


def test_load_segments_assigns_distinct_seq_labels_per_segment():
    payload = _load_fixture("sefaria_avot_1_davidson.json")
    with patch.object(sefaria, "_fetch_json", return_value=payload):
        segments = sefaria.load_segments(
            "Pirkei Avot 1",
            version="William Davidson Edition - Hebrew",
            seq_label="Davidson",
        )
    for i, seg in enumerate(segments):
        assert all(t.id.startswith(f"Davidson:{i + 1}:") for t in seg)


def test_load_strips_html_tags():
    payload = {
        "ref": "Pirkei Avot 1:1",
        "versions": [
            {
                "versionTitle": "Test",
                "language": "he",
                "text": "<b>שלום</b> <i>עולם</i><sup>1</sup>",
            }
        ],
    }
    with patch.object(sefaria, "_fetch_json", return_value=payload):
        tokens = sefaria.load("Pirkei Avot 1:1", version="Test", seq_label="T")
    texts = [t.text for t in tokens]
    assert "שלום" in texts
    assert "עולם" in texts
    assert "1" not in texts
    assert all("<" not in t.raw and ">" not in t.raw for t in tokens)


def test_load_versions_returns_dict_of_segments_per_version():
    davidson = _load_fixture("sefaria_avot_1_davidson.json")
    vilna = _load_fixture("sefaria_avot_1_vilna.json")
    kaufmann = _load_fixture("sefaria_avot_1_kaufmann.json")

    def fake_fetch(url):
        if "William%20Davidson" in url:
            return davidson
        if "Vilna" in url:
            return vilna
        if "Kaufmann" in url:
            return kaufmann
        raise AssertionError(f"unexpected URL: {url}")

    with patch.object(sefaria, "_fetch_json", side_effect=fake_fetch):
        out = sefaria.load_versions(
            "Pirkei Avot 1",
            versions=[
                "William Davidson Edition - Hebrew",
                "Vilna Edition",
                "Kaufmann Manuscript",
            ],
        )

    assert set(out.keys()) == {
        "William Davidson Edition - Hebrew",
        "Vilna Edition",
        "Kaufmann Manuscript",
    }
    for segments in out.values():
        assert len(segments) == 3
