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
