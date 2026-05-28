"""Tests for MultiAlignmentResult JSON persistence."""

import json
from pathlib import Path

import tracealign
from tracealign.io import multi_result as mr_io


def _build_result():
    seqs = {
        "W1": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W1"),
        "W2": tracealign.tokenize("שלום עולם", lang="hbo", seq_label="W2"),
    }
    return tracealign.align_multi(seqs, lang="hbo")


def test_dumps_loads_round_trip():
    r = _build_result()
    s = mr_io.dumps(r)
    restored = mr_io.loads(s)
    assert set(restored.witness_ids) == set(r.witness_ids)
    assert restored.params["lang"] == "hbo"


def test_dumps_is_valid_json():
    r = _build_result()
    s = mr_io.dumps(r)
    parsed = json.loads(s)
    assert "graph" in parsed
    assert "table" in parsed
    assert "guide_tree" in parsed


def test_dump_load_file_round_trip(tmp_path: Path):
    r = _build_result()
    f = tmp_path / "multi.json"
    mr_io.dump(r, f)
    restored = mr_io.load(f)
    assert restored.witness_ids == r.witness_ids


def test_round_trip_preserves_distance_matrix():
    r = _build_result()
    s = mr_io.dumps(r)
    restored = mr_io.loads(s)
    assert restored.guide_tree.distance_matrix == r.guide_tree.distance_matrix
