"""Tests for AlignmentResult JSON serialization."""

import json
from pathlib import Path

import tracealign
from tracealign.io import result as result_io


def _build_result() -> "tracealign.AlignmentResult":
    a = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="A")
    b = tracealign.tokenize("שלום עולם", lang="hbo", seq_label="B")
    return tracealign.align(a, b, lang="hbo", seq_a_meta={"witness_id": "W1"})


def test_dumps_loads_round_trip():
    r = _build_result()
    s = result_io.dumps(r)
    restored = result_io.loads(s)
    assert restored.total_score == r.total_score
    assert restored.summary == r.summary
    assert len(restored.matches) == len(r.matches)
    assert restored.seq_a_meta == {"witness_id": "W1"}


def test_dumps_is_valid_json():
    r = _build_result()
    s = result_io.dumps(r)
    parsed = json.loads(s)
    assert "matches" in parsed
    assert "summary" in parsed
    assert parsed["params"]["lang"] == "hbo"


def test_dump_load_file_round_trip(tmp_path: Path):
    r = _build_result()
    f = tmp_path / "result.json"
    result_io.dump(r, f)
    restored = result_io.load(f)
    assert restored.summary == r.summary
