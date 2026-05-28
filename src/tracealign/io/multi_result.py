"""JSON persistence for MultiAlignmentResult."""

from __future__ import annotations

from pathlib import Path

from tracealign.multi.api import MultiAlignmentResult


def dumps(result: MultiAlignmentResult) -> str:
    return result.model_dump_json()


def loads(payload: str) -> MultiAlignmentResult:
    return MultiAlignmentResult.model_validate_json(payload)


def dump(result: MultiAlignmentResult, path: Path | str) -> None:
    Path(path).write_text(dumps(result), encoding="utf-8")


def load(path: Path | str) -> MultiAlignmentResult:
    return loads(Path(path).read_text(encoding="utf-8"))
