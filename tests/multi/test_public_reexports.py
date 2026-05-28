"""Tests that align_multi and the multi types are reachable at the top level."""


def test_top_level_align_multi():
    import tracealign

    assert hasattr(tracealign, "align_multi")
    assert hasattr(tracealign, "MultiAlignerConfig")
    assert hasattr(tracealign, "MultiAlignmentResult")


def test_top_level_graph_types():
    import tracealign

    assert hasattr(tracealign, "VariantGraph")
    assert hasattr(tracealign, "GraphNode")
    assert hasattr(tracealign, "GraphEdge")


def test_top_level_table_and_guide_tree():
    import tracealign

    assert hasattr(tracealign, "AlignedTable")
    assert hasattr(tracealign, "TableColumn")
    assert hasattr(tracealign, "TableCell")
    assert hasattr(tracealign, "GuideTree")
    assert hasattr(tracealign, "GuideTreeNode")
