"""Tests for the GuideTree data types and format_text."""

from tracealign.multi.guide_tree import GuideTree, GuideTreeNode


def _leaf(wid: str) -> GuideTreeNode:
    return GuideTreeNode(is_leaf=True, witness_id=wid, children=[], height=0.0)


def test_guide_tree_leaf():
    leaf = _leaf("W1")
    assert leaf.is_leaf is True
    assert leaf.witness_id == "W1"
    assert leaf.children == []
    assert leaf.height == 0.0


def test_guide_tree_internal_node():
    node = GuideTreeNode(
        is_leaf=False,
        witness_id=None,
        children=[_leaf("W1"), _leaf("W2")],
        height=0.5,
    )
    assert node.is_leaf is False
    assert node.witness_id is None
    assert len(node.children) == 2
    assert node.height == 0.5


def test_guide_tree_with_distance_matrix():
    tree = GuideTree(
        root=GuideTreeNode(
            is_leaf=False,
            witness_id=None,
            children=[_leaf("W1"), _leaf("W2")],
            height=0.25,
        ),
        method="upgma",
        distance_matrix=[[0.0, 0.5], [0.5, 0.0]],
        witness_ids=["W1", "W2"],
    )
    assert tree.method == "upgma"
    assert tree.distance_matrix == [[0.0, 0.5], [0.5, 0.0]]
    assert tree.witness_ids == ["W1", "W2"]


def test_format_text_renders_indented_tree():
    tree = GuideTree(
        root=GuideTreeNode(
            is_leaf=False,
            witness_id=None,
            children=[_leaf("W1"), _leaf("W2")],
            height=0.25,
        ),
        method="upgma",
        distance_matrix=[[0.0, 0.5], [0.5, 0.0]],
        witness_ids=["W1", "W2"],
    )
    rendered = tree.format_text()
    assert "W1" in rendered
    assert "W2" in rendered
    # Some indication of structure (height or indentation)
    assert "0.25" in rendered or "0.5" in rendered
