"""Aligned table view derived from a VariantGraph."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from tracealign.model import Token


class TableCell(BaseModel):
    """One cell in the aligned table — a token or a gap."""

    model_config = ConfigDict(extra="forbid")

    token: Token | None
    node_id: str | None


class TableColumn(BaseModel):
    """One column of the aligned table — one cell per witness."""

    model_config = ConfigDict(extra="forbid")

    cells: dict[str, TableCell]


class AlignedTable(BaseModel):
    """Tabular view over a VariantGraph.

    Rows correspond to witnesses; columns to aligned positions. Cells whose
    token is None represent gaps relative to the column's consensus.
    """

    model_config = ConfigDict(extra="forbid")

    witnesses: list[str]
    columns: list[TableColumn]
