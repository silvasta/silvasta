"""
Develop the DtoFamily to the next Level

-
"""

__all__: list[str] = [
    "TableViewDTO",
]

from collections.abc import Mapping, Sequence
from typing import Any, Self, Unpack

from ....port.event._param import HeaderSpec
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
        rows: dict[str, CliSpec | list[CliSpec] | tuple[CliSpec]],
        **kwargs: Unpack[TablePresetInput],
    ) -> Self:
        return cls.create(
            content=tuple(
                tuple(v) if isinstance(v, (list, tuple)) else (v,)
                for v in rows.values()
            ),
            row_names=tuple(rows.keys()),
            **kwargs,
        )

    @classmethod
    def from_cols(
        cls,
        cols: dict[str, Sequence[Any]],
        *,
        corner: str = "",
        **kwargs: Unpack[TablePresetInput],
    ) -> Self:
        """Transform dict of {col_name: column_values} into a cls (transposed)."""

        return cls.create(
            header=HeaderSpec(title="Table From Cols"),
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
        records: Sequence[dict[str, Any]],
        headers: list[str] | None = None,
        **kwargs: Unpack[TablePresetInput],
    ) -> Self:
        """Transform list of row dicts [{'ColA': 1, 'ColB': 2}] into a cls."""
        if not records:
            return cls.create(((),), **kwargs)

        resolved_headers: tuple[str, ...] = (
            tuple(headers)
            if headers
            else tuple(dict.fromkeys(k for row in records for k in row.keys()))
        )
        return cls.create(
            header=HeaderSpec(title="Table from Records"),
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
