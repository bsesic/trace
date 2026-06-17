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


def test_build_url_uses_hebrew_language_token():
    """Pin: Sefaria API requires 'hebrew|' not 'he|' for the version language."""
    url = sefaria._build_url("Pirkei Avot 1", version="Vilna Edition")
    assert "version=hebrew%7CVilna" in url or "version=hebrew|Vilna" in url
    # Negative: the ISO-code form must not slip back in
    assert "version=he|" not in url
    assert "version=he%7C" not in url


def test_build_url_without_version_has_no_query():
    url = sefaria._build_url("Pirkei Avot 1", version=None)
    assert "?" not in url
    assert url.startswith("https://www.sefaria.org/api/v3/texts/")
    # The reference must be URL-safe: no raw whitespace ends up in the URL.
    assert " " not in url
