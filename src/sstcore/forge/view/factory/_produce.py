"""
CliFactory - Experiment 3

- Tiny but by far the besgt so far!

"""

import warnings
from collections.abc import Sequence
from typing import Any

from ....brick.color.box import Colors
from ....port.color import ColorBox
from ....port.event.dto import (
    GroupDTO,
    LineDTO,
    MarkdownDTO,
    PanelDTO,
    TableDTO,
)
from ....port.represent import CliRenderable

colors: ColorBox = Colors()


def panel(
    content: CliRenderable | list[CliRenderable],
    *,
    title: str | None = None,
    expand: bool = True,
    **kwargs: Any,
) -> PanelDTO:
    """Create a framed PanelDTO container."""
    return PanelDTO(content=content, title=title, expand=expand, **kwargs)


def panel_ctor(content: Any, title: str | None = None, **kwargs) -> PanelDTO:
    return PanelDTO(content=content, title=title, **kwargs)


def group(*items: CliRenderable) -> GroupDTO:
    """Create a GroupDTO stacking multiple renderables."""
    return GroupDTO(content=list(items))


def line_ctor(character: str = "─", *, style: str = "cyan") -> LineDTO:  # noqa:N805
    """Create a horizontal character LineDTO."""
    return LineDTO(content=character, color=style)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def markdown(
    text: str, *, header: int = 0, style: str = "white"
) -> MarkdownDTO:
    """Create a MarkdownDTO with validated header constraints (H0-H6)."""
    if not (0 <= header <= 6):
        warnings.warn(
            f"Markdown header={header} invalid (expected H0-H6). Defaulting to 0.",
            stacklevel=2,
        )
        header = 0
    return MarkdownDTO(content=text, header=header, color=style)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def table_from_matrix(matrix: list[list[Any]], content: str = "") -> TableDTO:
    return TableDTO(
        content=content or "Table From Dicts",
        matrix=matrix,
    )


def table_from_row_dicts(rows: dict[str, Any | list[Any]]) -> TableDTO:
    return TableDTO(
        content="Table From Dicts",
        matrix=list(rows.values()),
        row_names=list(rows.keys()),
    )


def table_from_rows(
    rows: dict[str, Any | Sequence[Any]], *, corner: str = ""
) -> TableDTO:
    """Transform dict of {row_name: values} into a TableDTO."""
    matrix: list[list[Any]] = [
        list(v)
        if isinstance(v, (list, tuple))  #
        else [v]
        for v in rows.values()
    ]
    return TableDTO(
        content="Table From Rows",
        matrix=matrix,
        row_names=list(rows.keys()),
        corner=corner,
    )


def table_from_cols(
    cols: dict[str, Sequence[Any]], *, corner: str = ""
) -> TableDTO:
    """Transform dict of {col_name: column_values} into a TableDTO (transposed)."""

    return TableDTO(
        content="Table From Cols",
        matrix=[list(row) for row in zip(*cols.values(), strict=True)],
        col_names=list(cols.keys()),
        corner=corner,
    )


def table_from_records(
    records: Sequence[dict[str, Any]], headers: list[str] | None = None
) -> TableDTO:
    """Transform list of row dicts [{'ColA': 1, 'ColB': 2}] into a TableDTO."""
    if not records:
        return TableDTO(content="Table", matrix=[])

    headers: list[str] = headers or list(
        dict.fromkeys(k for row in records for k in row.keys())
    )
    return TableDTO(
        content="Table from Records",
        matrix=[[row.get(h, "") for h in headers] for row in records],
        col_names=headers,
    )


def table_from_col_dicts(cols: dict[str, list[Any]], **kwargs) -> TableDTO:
    return TableDTO(
        matrix=[list(row) for row in zip(*cols.values(), strict=True)],
        col_names=list(cols.keys()),
        **kwargs,
    )
