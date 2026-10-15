"""
Develop the DtoFamily to the next Level

-
"""

__all__: list[str] = [
    "TableViewDTO",
]

from collections.abc import Sequence
from typing import Any, Self

from ....port.event.dto import CliData, HeaderData, TableDTO


class TableViewDTO(TableDTO, name="table"):
    @classmethod
    def table_from_matrix(
        cls, matrix: list[list[CliData]], title: str | None = None
    ) -> Self:
        return cls(
            content=tuple(tuple(row) for row in matrix),
            header=HeaderData(title=title),
        )

    @classmethod
    def table_from_rows(cls, rows: dict[str, CliData | list[CliData]]) -> Self:
        return cls(
            content=tuple(
                tuple(v) if isinstance(v, (list, tuple)) else (v,)
                for v in rows.values()
            ),
            row_names=tuple(rows.keys()),
            header=HeaderData(title="Table From Dicts"),
        )

    @classmethod
    def table_from_cols(
        cls, cols: dict[str, Sequence[Any]], *, corner: str = ""
    ) -> Self:
        """Transform dict of {col_name: column_values} into a cls (transposed)."""

        return cls(
            header=HeaderData(title="Table From Cols"),
            content=tuple(
                tuple(val for val in row)
                for row in zip(*cols.values(), strict=True)
            ),
            col_names=tuple(cols.keys()),
            corner=corner,
        )

    @classmethod
    def table_from_records(
        cls,
        records: Sequence[dict[str, Any]],
        headers: list[str] | None = None,
    ) -> Self:
        """Transform list of row dicts [{'ColA': 1, 'ColB': 2}] into a cls."""
        if not records:
            return cls(
                content=(()),
                header=HeaderData(title="Table from no Records"),
            )

        headers: tuple[str, ...] = (
            tuple(headers)
            if headers
            else tuple(dict.fromkeys(k for row in records for k in row.keys()))
        )
        return cls(
            header=HeaderData(title="Table from Records"),
            content=tuple(
                tuple(row.get(h, "") for h in headers) for row in records
            ),
            col_names=headers,
        )

    @classmethod
    def table_from_col_dicts(
        cls, cols: dict[str, list[Any]], **kwargs
    ) -> Self:
        return cls(
            content=tuple(
                tuple(row) for row in zip(*cols.values(), strict=True)
            ),
            col_names=tuple(cols.keys()),
            **kwargs,
        )
