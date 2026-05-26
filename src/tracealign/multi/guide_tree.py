"""Guide tree types built from a pairwise distance matrix."""

from __future__ import annotations

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
