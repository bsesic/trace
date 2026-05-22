"""Tests for VariantGraph.variants — yields variant loci."""

from tracealign.model import Token
from tracealign.multi.graph import GraphEdge, GraphNode, VariantGraph


def _tok(text: str, position: int = 0) -> Token:
    return Token(
        id=f"x:{position:06d}",
        position=position,
        raw=text,
        text=text,
    )


def test_variants_yields_nodes_with_distinct_token_texts():
    nodes = [
        GraphNode(id="START", tokens={}),
        GraphNode(id="n:0", tokens={"W1": _tok("a"), "W2": _tok("a")}),
        GraphNode(id="n:1", tokens={"W1": _tok("b"), "W2": _tok("c")}),
        GraphNode(id="END", tokens={}),
    ]
    edges = [
        GraphEdge(source_id="START", target_id="n:0", witnesses={"W1", "W2"}),
        GraphEdge(source_id="n:0", target_id="n:1", witnesses={"W1", "W2"}),
        GraphEdge(source_id="n:1", target_id="END", witnesses={"W1", "W2"}),
    ]
    g = VariantGraph(nodes=nodes, edges=edges, witness_ids=["W1", "W2"])

    variants = list(g.variants())
    assert len(variants) == 1
    assert variants[0].id == "n:1"


def test_variants_ignores_single_witness_nodes():
    nodes = [
        GraphNode(id="START", tokens={}),
        GraphNode(id="n:0", tokens={"W1": _tok("a")}),  # unique reading
        GraphNode(id="END", tokens={}),
    ]
    edges = [
        GraphEdge(source_id="START", target_id="n:0", witnesses={"W1"}),
        GraphEdge(source_id="n:0", target_id="END", witnesses={"W1"}),
    ]
    g = VariantGraph(nodes=nodes, edges=edges, witness_ids=["W1"])
    assert list(g.variants()) == []


def test_variants_treats_identical_texts_as_agreement():
    # Same text from two witnesses is agreement, not a variant
    node = GraphNode(id="n:0", tokens={"W1": _tok("שלום"), "W2": _tok("שלום")})
    g = VariantGraph(
        nodes=[GraphNode(id="START", tokens={}), node, GraphNode(id="END", tokens={})],
        edges=[
            GraphEdge(source_id="START", target_id="n:0", witnesses={"W1", "W2"}),
            GraphEdge(source_id="n:0", target_id="END", witnesses={"W1", "W2"}),
        ],
        witness_ids=["W1", "W2"],
    )
    assert list(g.variants()) == []
