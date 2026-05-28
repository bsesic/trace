"""Tests for AlignedTable basic structure."""

from tracealign.model import Token
from tracealign.multi.table import AlignedTable, TableCell, TableColumn


def _tok(text: str, position: int = 0) -> Token:
    return Token(
        id=f"x:{position:06d}",
        position=position,
        raw=text,
        text=text,
    )


def test_table_cell_carries_token_and_node_id():
    cell = TableCell(token=_tok("a"), node_id="n:0")
    assert cell.token is not None
    assert cell.token.text == "a"
    assert cell.node_id == "n:0"


def test_table_cell_gap_has_none_token():
    cell = TableCell(token=None, node_id=None)
    assert cell.token is None
    assert cell.node_id is None


def test_table_column_holds_cells_per_witness():
    col = TableColumn(
        cells={
            "W1": TableCell(token=_tok("a"), node_id="n:0"),
            "W2": TableCell(token=None, node_id=None),
        }
    )
    assert col.cells["W1"].token.text == "a"
    assert col.cells["W2"].token is None


def test_aligned_table_has_witnesses_and_columns():
    table = AlignedTable(
        witnesses=["W1", "W2"],
        columns=[
            TableColumn(
                cells={
                    "W1": TableCell(token=_tok("a"), node_id="n:0"),
                    "W2": TableCell(token=_tok("a"), node_id="n:0"),
                }
            )
        ],
    )
    assert table.witnesses == ["W1", "W2"]
    assert len(table.columns) == 1
