"""TEI XML importer."""

from __future__ import annotations

from pathlib import Path

from lxml import etree

import tracealign
from tracealign.lang.base import LanguagePack
from tracealign.lang.registry import get_language
from tracealign.model import Token

TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def _parse(source: Path | str) -> etree._Element:
    if isinstance(source, Path):
        return etree.parse(str(source)).getroot()
    text = source
    if text.lstrip().startswith("<"):
        return etree.fromstring(text.encode("utf-8"))
    return etree.parse(text).getroot()


def load(
    source: Path | str,
    lang: str | LanguagePack = "hbo",
    text_xpath: str | None = None,
    seq_label: str = "tei",
) -> list[Token]:
    pack = get_language(lang)
    root = _parse(source)
    body_elements = root.xpath(".//tei:body", namespaces=TEI_NS)
    if not body_elements:
        return []
    body = body_elements[0]
    w_elements = body.xpath(".//tei:w", namespaces=TEI_NS)
    if w_elements:
        out: list[Token] = []
        position = 0
        for w in w_elements:
            content = "".join(w.itertext()).strip()
            if not content:
                continue
            sub = tracealign.tokenize(content, lang=pack, seq_label=seq_label)
            for tok in sub:
                out.append(
                    tok.model_copy(
                        update={
                            "id": f"{seq_label}:{position:06d}",
                            "position": position,
                        }
                    )
                )
                position += 1
        return out
    body_text = " ".join(t.strip() for t in body.itertext() if t and t.strip())
    return tracealign.tokenize(body_text, lang=pack, seq_label=seq_label)
