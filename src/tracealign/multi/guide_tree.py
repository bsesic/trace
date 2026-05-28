"""Guide tree types built from a pairwise distance matrix."""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict


class GuideTreeNode(BaseModel):
    """One node in a binary guide tree.

    Leaves have `is_leaf=True`, `witness_id` set, and no children. Internal
    nodes have `is_leaf=False`, `witness_id=None`, and exactly two children
    (binary tree from UPGMA).
    """

    model_config = ConfigDict(extra="forbid")

    is_leaf: bool
    witness_id: str | None
    children: list["GuideTreeNode"]
    height: float


GuideTreeNode.model_rebuild()


class GuideTree(BaseModel):
    """A guide tree plus the distance matrix that generated it.

    The distance matrix is kept on the tree so that downstream stages (e.g.
    Stage 7 stemmatic reconstruction) can reuse it without recomputation.
    """

    model_config = ConfigDict(extra="forbid")

    root: GuideTreeNode
    method: str
    distance_matrix: list[list[float]]
    witness_ids: list[str]

    def format_text(self) -> str:
        """Render the tree as an indented ASCII listing."""
        lines: list[str] = []
        self._render(self.root, lines, depth=0)
        return "\n".join(lines)

    def _render(self, node: GuideTreeNode, lines: list[str], depth: int) -> None:
        indent = "  " * depth
        if node.is_leaf:
            lines.append(f"{indent}- {node.witness_id} (h={node.height:.4f})")
        else:
            lines.append(f"{indent}+ (h={node.height:.4f})")
            for child in node.children:
                self._render(child, lines, depth + 1)


def build_upgma(distance_matrix: "np.ndarray", witness_ids: list[str]) -> GuideTree:
    """Build a UPGMA guide tree from a symmetric distance matrix.

    Ties are broken on the (min, max) lexicographic order of the cluster
    members, guaranteeing determinism regardless of input order.
    """
    n = len(witness_ids)

    # Cluster representation: a list of (cluster_node, member_witness_ids_set)
    clusters: list[tuple[GuideTreeNode, set[str]]] = []
    for wid in witness_ids:
        leaf = GuideTreeNode(is_leaf=True, witness_id=wid, children=[], height=0.0)
        clusters.append((leaf, {wid}))

    # Working distance matrix as a plain dict keyed by frozenset pair
    D: dict[frozenset[str], float] = {}
    for i in range(n):
        for j in range(i + 1, n):
            D[frozenset([witness_ids[i], witness_ids[j]])] = float(distance_matrix[i, j])

    def _cluster_min_label(members: set[str]) -> str:
        return min(members)

    def _cluster_pair_key(a_members: set[str], b_members: set[str]) -> tuple[str, str]:
        # Canonical (min, max) sorted by lexicographic order
        a_lo = _cluster_min_label(a_members)
        b_lo = _cluster_min_label(b_members)
        return tuple(sorted([a_lo, b_lo]))

    while len(clusters) > 1:
        # Find the pair with the smallest distance; tie-break on canonical key
        best_pair: tuple[int, int] | None = None
        best_dist = float("inf")
        best_key: tuple[str, str] | None = None
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                members_i = clusters[i][1]
                members_j = clusters[j][1]
                pair_key = frozenset(members_i | members_j)
                dist = D[pair_key] if pair_key in D \
                    else _avg_distance(members_i, members_j, D)
                key = _cluster_pair_key(members_i, members_j)
                if dist < best_dist or (dist == best_dist and (best_key is None or key < best_key)):
                    best_dist = dist
                    best_pair = (i, j)
                    best_key = key

        i, j = best_pair  # type: ignore[misc]
        node_i, members_i = clusters[i]
        node_j, members_j = clusters[j]

        # Order children deterministically: smaller min-member first
        if _cluster_min_label(members_i) <= _cluster_min_label(members_j):
            children = [node_i, node_j]
        else:
            children = [node_j, node_i]

        merged_node = GuideTreeNode(
            is_leaf=False,
            witness_id=None,
            children=children,
            height=best_dist / 2.0,
        )
        merged_members = members_i | members_j

        # Update D with new cluster distances
        for k, (_, members_k) in enumerate(clusters):
            if k == i or k == j:
                continue
            d_ik = _avg_distance(members_i, members_k, D)
            d_jk = _avg_distance(members_j, members_k, D)
            new_d = (d_ik * len(members_i) + d_jk * len(members_k)) / (
                len(members_i) + len(members_j)
            )
            D[frozenset(merged_members | members_k)] = new_d

        # Remove old clusters, insert merged
        new_clusters = []
        for k, entry in enumerate(clusters):
            if k != i and k != j:
                new_clusters.append(entry)
        new_clusters.append((merged_node, merged_members))
        clusters = new_clusters

    root = clusters[0][0]
    return GuideTree(
        root=root,
        method="upgma",
        distance_matrix=distance_matrix.tolist(),
        witness_ids=witness_ids,
    )


def _avg_distance(a: set[str], b: set[str], D: dict[frozenset[str], float]) -> float:
    total = 0.0
    count = 0
    for x in a:
        for y in b:
            total += D[frozenset([x, y])]
            count += 1
    return total / count if count else 0.0


def post_order_witness_ids(tree: GuideTree) -> list[str]:
    """Return the witness ids in canonical post-order traversal of the tree."""
    out: list[str] = []
    _post_order(tree.root, out)
    return out


def _post_order(node: GuideTreeNode, out: list[str]) -> None:
    if node.is_leaf:
        if node.witness_id is not None:
            out.append(node.witness_id)
        return
    for child in node.children:
        _post_order(child, out)
