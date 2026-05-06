"""Importer for eScriptorium-style JSON exports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import tracealign
from tracealign.lang.base import LanguagePack
from tracealign.lang.registry import get_language
from tracealign.model import Token


def _coerce_payload(source: Path | str | dict) -> dict:
    if isinstance(source, dict):
        return source
    return json.loads(Path(source).read_text(encoding="utf-8"))


def load(
    source: Path | str | dict,
    lang: str | LanguagePack = "hbo",
) -> list[Token]:
    payload = _coerce_payload(source)
    pack = get_language(lang)
    witness_id: str = payload.get("witness_id", "W?")
    seq_label = witness_id
    out: list[Token] = []
    position = 0
    for region in payload.get("regions", []):
        surface_label = region.get("label")
        for line in region.get("lines", []):
            line_pk = line.get("line_pk")
            bbox = line.get("bbox")
            content: str = line.get("content", "")
            line_tokens = tracealign.tokenize(
                content, lang=pack, seq_label=seq_label
            )
            extra: dict[str, Any] = {
                "witness_id": witness_id,
                "surface_label": surface_label,
                "line_pk": line_pk,
            }
            if bbox is not None:
                extra["bbox"] = list(bbox)
            for tok in line_tokens:
                merged_metadata = dict(tok.metadata)
                merged_metadata.update(extra)
                out.append(
                    tok.model_copy(
                        update={
                            "id": f"{seq_label}:{position:06d}",
                            "position": position,
                            "metadata": merged_metadata,
                        }
                    )
                )
                position += 1
    return out
