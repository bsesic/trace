"""AlignmentResult JSON serialization."""

from __future__ import annotations

from pathlib import Path

from tracealign.model import AlignmentResult


def dumps(result: AlignmentResult) -> str:
    return result.model_dump_json()


def loads(payload: str) -> AlignmentResult:
    return AlignmentResult.model_validate_json(payload)


def dump(result: AlignmentResult, path: Path | str) -> None:
    Path(path).write_text(dumps(result), encoding="utf-8")


def load(path: Path | str) -> AlignmentResult:
    return loads(Path(path).read_text(encoding="utf-8"))
