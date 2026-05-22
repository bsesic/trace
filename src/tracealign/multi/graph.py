"""Variant graph types and helpers."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from tracealign.model import Token


class GraphNode(BaseModel):
    """A position in the multi-witness alignment.

    A node carries the tokens from witnesses that are considered aligned at
    this position. Nodes with zero tokens are the START and END sentinels.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    tokens: dict[str, Token]


class GraphEdge(BaseModel):
    """A directed edge in the variant DAG carrying the witnesses that traverse it."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    target_id: str
    witnesses: set[str]


class VariantGraph(BaseModel):
    """A directed acyclic graph representing a multi-witness alignment.

    Nodes are topologically sorted with the START sentinel first and the END
    sentinel last. Every witness path runs from START to END along edges
    whose `witnesses` set contains the witness id.
    """

    model_config = ConfigDict(extra="forbid")

    nodes: list[GraphNode]
    edges: list[GraphEdge]
    witness_ids: list[str]

    @classmethod
    def from_sequence(cls, witness_id: str, tokens: list[Token]) -> "VariantGraph":
        """Build a linear graph for a single witness."""
        nodes: list[GraphNode] = [GraphNode(id="START", tokens={})]
        for i, tok in enumerate(tokens):
            nodes.append(GraphNode(id=f"n:{i:06d}", tokens={witness_id: tok}))
        nodes.append(GraphNode(id="END", tokens={}))

        edges: list[GraphEdge] = []
        for i in range(len(nodes) - 1):
            edges.append(
                GraphEdge(
                    source_id=nodes[i].id,
                    target_id=nodes[i + 1].id,
                    witnesses={witness_id},
                )
            )

        return cls(nodes=nodes, edges=edges, witness_ids=[witness_id])

    def witness_path(self, witness_id: str) -> list[GraphNode]:
        """Return the non-sentinel nodes traversed by `witness_id` in order."""
        # Build adjacency: source_id -> list[(target_id, witnesses)]
        adj: dict[str, list[tuple[str, set[str]]]] = {}
        for edge in self.edges:
            adj.setdefault(edge.source_id, []).append((edge.target_id, edge.witnesses))

        nodes_by_id = {n.id: n for n in self.nodes}
        path: list[GraphNode] = []
        cur = "START"
        while cur != "END":
            next_id = None
            for target_id, witnesses in adj.get(cur, []):
                if witness_id in witnesses:
                    next_id = target_id
                    break
            if next_id is None:
                # No outgoing edge for this witness — should never happen for a
                # consistent graph; treat as end of path.
                break
            if next_id != "END":
                path.append(nodes_by_id[next_id])
            cur = next_id
        return path
