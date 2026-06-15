"""Sefaria public API importer.

Loads texts from the Sefaria API (https://www.sefaria.org/api/v3/texts/...)
and returns lists of TRACE Tokens. Tests inject mock HTTP responses by
patching the module-level `_http_get` function.
"""

from __future__ import annotations

import json
from urllib.request import Request, urlopen


def _http_get(url: str) -> bytes:
    """Fetch a URL and return the raw response body.

    Tests patch this function to return canned bytes instead of hitting
    the network.
    """
    req = Request(url, headers={"User-Agent": "tracealign/0.3.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read()


def _fetch_json(url: str) -> dict:
    """Fetch a URL and parse the response body as JSON (UTF-8)."""
    body = _http_get(url)
    return json.loads(body.decode("utf-8"))
