"""Tests for VariantGraph.from_sequence and witness_path."""

from tracealign.model import Token
from tracealign.multi.graph import VariantGraph


def _tok(text: str, position: int = 0) -> Token:
    return Token(
        id=f"x:{position:06d}",
        position=position,
        raw=text,
        text=text,
    )


def test_from_sequence_produces_linear_chain():
    seq = [_tok("a", 0), _tok("b", 1), _tok("c", 2)]
    g = VariantGraph.from_sequence("W1", seq)

    # Three content nodes plus START and END = 5 total
    assert len(g.nodes) == 5
    assert g.nodes[0].id == "START"
    assert g.nodes[-1].id == "END"
    assert g.witness_ids == ["W1"]

    # Edges: START -> n0 -> n1 -> n2 -> END, all carrying {"W1"}
    assert len(g.edges) == 4
    for edge in g.edges:
        assert edge.witnesses == {"W1"}


def test_witness_path_excludes_sentinels_and_reconstructs_input():
    seq = [_tok("a", 0), _tok("b", 1), _tok("c", 2)]
    g = VariantGraph.from_sequence("W1", seq)
    path = g.witness_path("W1")

    assert len(path) == 3
    assert [n.tokens["W1"].text for n in path] == ["a", "b", "c"]
    assert all(n.id not in ("START", "END") for n in path)


def test_from_sequence_empty_sequence_gives_start_then_end():
    g = VariantGraph.from_sequence("W1", [])
    assert [n.id for n in g.nodes] == ["START", "END"]
    assert g.witness_path("W1") == []
