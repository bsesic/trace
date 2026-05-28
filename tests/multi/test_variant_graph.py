"""Tests for VariantGraph container and topological order."""

from tracealign.model import Token
from tracealign.multi.graph import GraphEdge, GraphNode, VariantGraph


def _tok(text: str, position: int = 0) -> Token:
    return Token(
        id=f"x:{position:06d}",
        position=position,
        raw=text,
        text=text,
    )


def test_variant_graph_holds_nodes_and_edges():
    nodes = [
        GraphNode(id="START", tokens={}),
        GraphNode(id="n:0", tokens={"W1": _tok("a")}),
        GraphNode(id="END", tokens={}),
    ]
    edges = [
        GraphEdge(source_id="START", target_id="n:0", witnesses={"W1"}),
        GraphEdge(source_id="n:0", target_id="END", witnesses={"W1"}),
    ]
    g = VariantGraph(nodes=nodes, edges=edges, witness_ids=["W1"])
    assert g.witness_ids == ["W1"]
    assert len(g.nodes) == 3
    assert len(g.edges) == 2


def test_variant_graph_first_node_is_start_last_is_end():
    g = VariantGraph(
        nodes=[
            GraphNode(id="START", tokens={}),
            GraphNode(id="n:0", tokens={"W1": _tok("a")}),
            GraphNode(id="END", tokens={}),
        ],
        edges=[
            GraphEdge(source_id="START", target_id="n:0", witnesses={"W1"}),
            GraphEdge(source_id="n:0", target_id="END", witnesses={"W1"}),
        ],
        witness_ids=["W1"],
    )
    assert g.nodes[0].id == "START"
    assert g.nodes[-1].id == "END"
