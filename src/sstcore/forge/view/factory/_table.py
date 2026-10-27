"""
Develop the DtoFamily to the next Level

-
"""

__all__: list[str] = [
    "TableViewDTO",
]

from collections.abc import Mapping, Sequence
from typing import Any, Self, Unpack

from ....port.event.dto import CliSpec, TableDTO, TablePresetInput


class TableViewDTO(TableDTO, name="table"):
    @classmethod
    def from_matrix(
        cls,
        matrix: Sequence[Sequence[CliSpec]],
        **kwargs: Unpack[TablePresetInput],
    ) -> Self:
        return cls.create(
            content=tuple(tuple(row) for row in matrix),
            **kwargs,
        )

    @classmethod
    def from_rows(
        cls,
        rows: Mapping[str, CliSpec | Sequence[CliSpec]],
        **kwargs: Unpack[TablePresetInput],
    ) -> Self:
        return cls.create(
            content=tuple(
                tuple(v)
                if isinstance(v, Sequence) and not isinstance(v, (str, bytes))
                else (v,)
                for v in rows.values()
            ),
            row_names=tuple(rows.keys()),
            **kwargs,
        )

    @classmethod
    def from_cols(
        cls,
        cols: Mapping[str, Sequence[Any]],
        *,
        corner: str = "",
        **kwargs: Unpack[TablePresetInput],
    ) -> Self:
        """Transform mapping of {col_name: column_values} into a transposed table."""
        return cls.create(
            content=tuple(
                tuple(val for val in row)
                for row in zip(*cols.values(), strict=True)
            ),
            col_names=tuple(cols.keys()),
            corner=corner,
            **kwargs,
        )

    @classmethod
    def from_records(
        cls,
        records: Sequence[Mapping[str, Any]],
        headers: Sequence[str] | None = None,
        **kwargs: Unpack[TablePresetInput],
    ) -> Self:
        """Transform sequence of row dicts [{'ColA': 1, 'ColB': 2}] into a table."""
        if not records:
            return cls.create(((),), **kwargs)

        resolved_headers: tuple[str, ...] = (
            tuple(headers)
            if headers
            else tuple(dict.fromkeys(k for row in records for k in row.keys()))
        )
        return cls.create(
            content=tuple(
                tuple(str(row.get(h, "")) for h in resolved_headers)
                for row in records
            ),
            col_names=resolved_headers,
            **kwargs,
        )

    @classmethod
    def from_kv(
        cls,
        mapping: Mapping[str, Any],
        *,
        key_col: str = "Key",
        val_col: str = "Value",
        **kwargs: Unpack[TablePresetInput],
    ) -> Self:
        """Create a 2-column inspection table from any key-value mapping."""
        return cls.create(
            content=tuple((str(k), v) for k, v in mapping.items()),
            col_names=(key_col, val_col),
            **kwargs,
        )
