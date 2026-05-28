"""Public entry point for multi-witness alignment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ConfigDict

import tracealign as _tracealign_pkg
from tracealign.align import AlignerConfig
from tracealign.lang.base import LanguagePack
from tracealign.model import Reason, Token
from tracealign.multi.distance import pairwise_distances
from tracealign.multi.graph import VariantGraph
from tracealign.multi.guide_tree import GuideTree, build_upgma
from tracealign.multi.merge import progressive_merge
from tracealign.multi.table import AlignedTable, TableCell, TableColumn


@dataclass
class MultiAlignerConfig:
    """Configuration for align_multi.

    Follows the @dataclass style of v0.1's AlignerConfig; snapshotted into
    MultiAlignmentResult.params for persistence.
    """

    pairwise: AlignerConfig = field(default_factory=AlignerConfig)
    node_match: str = "max"
    guide_tree_method: str = "upgma"
    gap_penalty_multi: float = -2.0


_VALID_NODE_MATCH = {"max", "mean", "min"}
_VALID_GUIDE_TREE = {"upgma"}


def _validate_config(cfg: MultiAlignerConfig) -> None:
    if cfg.node_match not in _VALID_NODE_MATCH:
        raise ValueError(
            f"unknown node_match mode: {cfg.node_match!r}; "
            f"expected one of {sorted(_VALID_NODE_MATCH)}"
        )
    if cfg.guide_tree_method not in _VALID_GUIDE_TREE:
        raise ValueError(
            f"unknown guide_tree_method: {cfg.guide_tree_method!r}; "
            f"expected one of {sorted(_VALID_GUIDE_TREE)}"
        )


class MultiAlignmentResult(BaseModel):
    """Top-level result of align_multi()."""

    model_config = ConfigDict(extra="forbid")

    graph: VariantGraph
    table: AlignedTable
    guide_tree: GuideTree
    witness_ids: list[str]
    summary: dict[Reason, int]
    params: dict[str, Any]


def align_multi(
    witnesses: dict[str, list[Token]],
    lang: str | LanguagePack = "hbo",
    config: MultiAlignerConfig | None = None,
) -> MultiAlignmentResult:
    """Align N witnesses simultaneously, producing a variant graph + aligned table."""
    cfg = config or MultiAlignerConfig()
    _validate_config(cfg)

    pack = _tracealign_pkg.get_language(lang)

    # Phase 1: distance matrix
    D, witness_ids = pairwise_distances(witnesses, pack, cfg.pairwise)

    # Phase 2: guide tree
    if cfg.guide_tree_method == "upgma":
        tree = build_upgma(D, witness_ids)
    else:
        raise ValueError(f"unsupported guide_tree_method: {cfg.guide_tree_method}")

    # Phase 3: progressive merge
    graph = progressive_merge(
        witnesses, tree, pack, cfg.pairwise, cfg.node_match, cfg.gap_penalty_multi
    )

    # Derive table view (default-anchored to first witness in tree post-order)
    table = _build_table_from_graph(graph)

    # Aggregate per-pair summaries into a single counter.
    # In v0.2 we keep this simple: empty summary unless we want to expose it
    # later. (Acceptable per spec — summary may be empty in v0.2.0; richer
    # aggregation can come in v0.2.x without an API break.)
    summary: dict[Reason, int] = {}

    params: dict[str, Any] = {
        "lang": pack.code,
        "gap_open": cfg.pairwise.gap_open,
        "gap_extend": cfg.pairwise.gap_extend,
        "gap_penalty_multi": cfg.gap_penalty_multi,
        "node_match": cfg.node_match,
        "guide_tree_method": cfg.guide_tree_method,
        "trace_version": getattr(_tracealign_pkg, "__version__", "0.0.0"),
        "language_pack_version": getattr(pack, "version", "unknown"),
    }

    return MultiAlignmentResult(
        graph=graph,
        table=table,
        guide_tree=tree,
        witness_ids=witness_ids,
        summary=summary,
        params=params,
    )


def _build_table_from_graph(graph: VariantGraph) -> AlignedTable:
    """Derive an AlignedTable by walking the topological order of the graph."""
    columns: list[TableColumn] = []
    for node in graph.nodes:
        if node.id in ("START", "END"):
            continue
        cells: dict[str, TableCell] = {}
        for wid in graph.witness_ids:
            tok = node.tokens.get(wid)
            cells[wid] = TableCell(token=tok, node_id=node.id if tok else None)
        columns.append(TableColumn(cells=cells))
    return AlignedTable(witnesses=list(graph.witness_ids), columns=columns)
