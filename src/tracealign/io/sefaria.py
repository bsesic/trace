"""Sefaria public API importer.

Loads texts from the Sefaria API (https://www.sefaria.org/api/v3/texts/...)
and returns lists of TRACE Tokens. Tests inject mock HTTP responses by
patching the module-level `_http_get` function.
"""

from __future__ import annotations

import json
from urllib.parse import quote
from urllib.request import Request, urlopen

import tracealign
from tracealign.lang.base import LanguagePack
from tracealign.model import Token


SEFARIA_API_BASE = "https://www.sefaria.org/api/v3/texts"


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


def _build_url(ref: str, version: str | None) -> str:
    """Build the v3 API URL for a reference, optionally pinning a version."""
    encoded_ref = quote(ref.replace(" ", "_"), safe="._")
    url = f"{SEFARIA_API_BASE}/{encoded_ref}"
    if version is not None:
        url += f"?version=he|{quote(version, safe='')}"
    return url


def _select_version(payload: dict, version: str | None) -> dict:
    """Pick the right version block from the payload."""
    versions = payload.get("versions", [])
    if not versions:
        raise ValueError(
            f"Sefaria response has no versions: ref={payload.get('ref')!r}"
        )
    if version is None:
        return versions[0]
    for v in versions:
        if v.get("versionTitle") == version:
            return v
    available = [v.get("versionTitle") for v in versions]
    raise ValueError(
        f"version {version!r} not found in Sefaria response; "
        f"available: {available}"
    )


def load(
    ref: str,
    version: str | None = None,
    lang: str | LanguagePack = "hbo",
    seq_label: str | None = None,
) -> list[Token]:
    """Load one Sefaria reference and return its tokens.

    For chapter-level references that resolve to multiple segments the
    function concatenates all segments with single spaces. See
    `load_segments` to get a list of token-lists per segment.
    """
    url = _build_url(ref, version)
    payload = _fetch_json(url)
    version_block = _select_version(payload, version)
    text_field = version_block.get("text")
    if isinstance(text_field, list):
        text = " ".join(s for s in text_field if isinstance(s, str))
    elif isinstance(text_field, str):
        text = text_field
    else:
        raise ValueError(f"Sefaria version {version!r} has no text field")

    label = seq_label or version or ref
    return tracealign.tokenize(text, lang=lang, seq_label=label)
