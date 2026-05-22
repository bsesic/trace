"""Tests for GraphNode and GraphEdge."""

import pytest
from pydantic import ValidationError

from tracealign.model import Token
from tracealign.multi.graph import GraphNode, GraphEdge


def _tok(text: str, position: int = 0) -> Token:
    return Token(
        id=f"x:{position:06d}",
        position=position,
        raw=text,
        text=text,
    )


def test_graph_node_with_two_witnesses():
    node = GraphNode(
        id="n:000001",
        tokens={"W1": _tok("רבי"), "W2": _tok("רבי")},
    )
    assert node.id == "n:000001"
    assert set(node.tokens.keys()) == {"W1", "W2"}


def test_graph_node_empty_tokens_for_sentinel():
    # START / END sentinels carry no tokens
    node = GraphNode(id="START", tokens={})
    assert node.tokens == {}


def test_graph_edge_with_witness_set():
    edge = GraphEdge(source_id="n:0", target_id="n:1", witnesses={"W1", "W2"})
    assert edge.source_id == "n:0"
    assert edge.target_id == "n:1"
    assert edge.witnesses == {"W1", "W2"}


def test_graph_node_rejects_extra_fields():
    with pytest.raises(ValidationError):
        GraphNode(id="n:0", tokens={}, extra_field="nope")


def test_graph_edge_rejects_extra_fields():
    with pytest.raises(ValidationError):
        GraphEdge(source_id="a", target_id="b", witnesses=set(), extra="nope")
