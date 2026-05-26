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

    def re_anchor(self, base_witness: str) -> "AlignedTable":
        """Return a new AlignedTable where `base_witness` is rendered first.

        Only the row order changes; cells per (witness, column) are preserved
        unchanged. This is purely a presentation transform.
        """
        if base_witness not in self.witnesses:
            raise ValueError(f"unknown witness: {base_witness}")

        new_witnesses = [base_witness] + [w for w in self.witnesses if w != base_witness]
        return AlignedTable(witnesses=new_witnesses, columns=self.columns)

    def format_text(self, max_columns: int = 80) -> str:
        """ASCII rendering of the aligned table.

        Each row is one witness; gaps are shown as a centred dash. The
        rendering truncates each column to fit `max_columns` total width.
        """
        gap_marker = "—"
        col_widths: list[int] = []
        for col in self.columns:
            widest = max(
                (len(c.token.text) if c.token is not None else len(gap_marker))
                for c in col.cells.values()
            )
            col_widths.append(max(widest, len(gap_marker)))

        # Truncate to fit max_columns; total width = sum(col_widths) + len(cols)
        rows: list[str] = []
        label_width = max(len(w) for w in self.witnesses)
        for w in self.witnesses:
            parts = [f"{w:<{label_width}}"]
            running = label_width + 1
            for col, width in zip(self.columns, col_widths):
                cell = col.cells.get(w)
                if cell is None or cell.token is None:
                    text = gap_marker
                else:
                    text = cell.token.text
                if running + width + 1 > max_columns:
                    parts.append("…")
                    break
                parts.append(f"{text:<{width}}")
                running += width + 1
            rows.append(" ".join(parts))
        return "\n".join(rows)
