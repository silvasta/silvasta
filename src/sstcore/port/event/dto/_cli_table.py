"""
Provide typed Data Transfer Objects for the EventBus

- CliDTO: Intended for __cli__ and processed by printer
"""

# LATER: move function implementation out of the port

__all__: list[str] = [
    "TableDTO",
    "MarkdownDTO",
]

import warnings
from dataclasses import dataclass, field
from typing import Any, Self

from ._cli import CliDTO


@dataclass(kw_only=True)
class MarkdownDTO(CliDTO):
    # REMOVE: text: str
    header: int = 0
    style = "white"

    def _validate(self):  # LATER: which **kwargs?
        if not (0 <= (header := self.header) <= 6):
            self.header = 0
            message = f"Markdown {header=}, invalid! (H1-H6) using default=0"
            warnings.warn(message, stacklevel=2)


@dataclass(kw_only=True)
class TableDTO(CliDTO):
    """Store Table data as lists of rows containing lists of values"""

    # AI_QUESTION: how to define the content here? as the matrix?
    matrix: list[list[Any]]  # The Content [1:][1:]

    col_names: list[str] = field(default_factory=list)  # [0][1:] (header)
    row_names: list[str] = field(default_factory=list)  # [1:][0]
    corner: str = ""  # [0][0] element: used if Row and Col names Defined

    def _validate(self):
        if not self.matrix:  # LATER: confirm that empty is valid
            return
        if self.col_names:
            if (n_col := len(self.col_names)) != (w := len(self.matrix[0])):
                raise ValueError(f"{n_col} row_names but matrix width ({w})")
        if self.row_names:
            if (n_row := len(self.row_names)) != (h := len(self.matrix)):
                raise ValueError(f"{n_row} row_names but matrix height ({h})")

    @property
    def header(self) -> list[str]:
        """Yields the complete header row, including the corner if needed."""
        return (
            []
            if not self.col_names
            else self.col_names
            if not self.row_names
            else [self.corner] + self.col_names
        )

    @property
    def rows(self):
        """Yield aligned rows and inject side-titles if needed"""
        for i, row in enumerate(self.matrix):
            if self.row_names and i < len(self.row_names):
                # LATER: colorize, zip(strict=True)
                yield [self.row_names[i]] + row
            else:
                yield row

    @classmethod
    def from_row_dicts(cls, rows: dict[str, Any | list[Any]]) -> Self:
        """Transform dict of {row_name: value(s)} to internal structure."""
        return cls(
            matrix=list(rows.values()),
            row_names=list(rows.keys()),
        )

    @classmethod
    def from_col_dicts(cls, cols: dict[str, list[Any]]) -> Self:
        """Transform dict of {col_name: values} to internal structure."""
        return cls(  # Transpose columns into rows using zip
            matrix=[list(row) for row in zip(*cols.values(), strict=True)],
            col_names=list(cols.keys()),
        )

    @classmethod
    def from_col_list(cls, cols: list[list[Any]]) -> Self:
        """Transform list of columns to internal row structure."""
        return cls(matrix=[list(row) for row in zip(*cols, strict=True)])

    @classmethod
    def from_value_dicts(
        cls, rows: list[dict[str, Any]], headers: list[str] | None = None
    ) -> Self:
        """Transform list of dicts [{"Header A": 1, "Header B": 2}]"""
        if not rows:
            return cls(matrix=[])
        if headers is None:
            headers: list[str] = list(
                # dict.fromkeys acts as ordered set
                dict.fromkeys(k for row in rows for k in row.keys())
            )
        filtered_matrix: list[list[Any]] = [
            # Build, filter and sort the matrix by header
            [row.get(header, "") for header in headers]
            for row in rows
        ]
        return cls(matrix=filtered_matrix, col_names=headers)
