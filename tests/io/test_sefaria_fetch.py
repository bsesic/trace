"""Tests for tracealign.io.sefaria._fetch_json mocking surface."""

import json
from pathlib import Path
from unittest.mock import patch

from tracealign.io import sefaria


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_fetch_json_returns_parsed_json():
    payload = {"ref": "Pirkei Avot 1", "versions": []}
    with patch.object(sefaria, "_http_get", return_value=json.dumps(payload).encode("utf-8")):
        result = sefaria._fetch_json("https://example.invalid/")
    assert result == payload


def test_fetch_json_decodes_utf8():
    payload = {"text": "שלום"}
    with patch.object(sefaria, "_http_get", return_value=json.dumps(payload).encode("utf-8")):
        result = sefaria._fetch_json("https://example.invalid/")
    assert result["text"] == "שלום"


def test_fetch_json_uses_fixture():
    body = (FIXTURE_DIR / "sefaria_avot_1_davidson.json").read_bytes()
    with patch.object(sefaria, "_http_get", return_value=body):
        result = sefaria._fetch_json("https://example.invalid/")
    assert result["ref"] == "Pirkei Avot 1"
    assert result["versions"][0]["versionTitle"].startswith("William Davidson")
