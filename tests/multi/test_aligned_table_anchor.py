"""Tests for AlignedTable.re_anchor and format_text."""

from tracealign.model import Token
from tracealign.multi.table import AlignedTable, TableCell, TableColumn


def _tok(text: str, position: int = 0) -> Token:
    return Token(
        id=f"x:{position:06d}",
        position=position,
        raw=text,
        text=text,
    )


def _make_table() -> AlignedTable:
    return AlignedTable(
        witnesses=["W1", "W2"],
        columns=[
            TableColumn(
                cells={
                    "W1": TableCell(token=_tok("a"), node_id="n:0"),
                    "W2": TableCell(token=_tok("a"), node_id="n:0"),
                }
            ),
            TableColumn(
                cells={
                    "W1": TableCell(token=_tok("b"), node_id="n:1"),
                    "W2": TableCell(token=None, node_id=None),
                }
            ),
        ],
    )


def test_re_anchor_moves_base_witness_to_front():
    table = _make_table()
    re = table.re_anchor("W2")
    assert re.witnesses[0] == "W2"
    assert set(re.witnesses) == {"W1", "W2"}


def test_re_anchor_preserves_alignment_relationships():
    table = _make_table()
    re = table.re_anchor("W2")
    # The cells per (witness, column) must remain consistent; re_anchor only
    # changes display order, not which token belongs to which witness at
    # which column.
    for original, anchored in zip(table.columns, re.columns):
        for wid in ("W1", "W2"):
            orig = original.cells[wid]
            new = anchored.cells[wid]
            assert orig.token == new.token
            assert orig.node_id == new.node_id


def test_re_anchor_to_unknown_witness_raises():
    table = _make_table()
    try:
        table.re_anchor("W99")
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_format_text_renders_columns_with_witnesses():
    table = _make_table()
    rendered = table.format_text()
    # Witness labels appear as row prefixes
    assert "W1" in rendered
    assert "W2" in rendered
    # Gap is shown as a placeholder
    assert "—" in rendered or "-" in rendered or "·" in rendered
