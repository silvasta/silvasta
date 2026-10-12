"""
CliFactory - Experiment 1

- Static meta toolkit and missing args/kwargs

"""

__all__: list[str] = [
    "CliDtoFactory",
]

import warnings
from collections.abc import Sequence
from typing import Any

from ....brick.color.box import Colors
from ....brick.labor import clsname
from ....forge.engine.blueprint import StaticFuncMeta, StaticFuncMetaData
from ....port.color import ColorBox
from ....port.event.dto import (
    GroupDTO,
    LineDTO,
    MarkdownDTO,
    PanelDTO,
    TableDTO,
)
from ....port.view import Renderable

colors: ColorBox = Colors()

CliDtoFactoryMetaInput = StaticFuncMetaData(
    name=lambda cls: f"󰕧 {clsname(cls)} 󰕧",
    rich=f"{colors.azure('CliDto')}{colors.teal('Factory')}",
    # TODO: attach CliDTO, I mean this is the CliFactory...
    cli="Standard factory for constructing normalized CliDTO renderables",
    color=4,
)


class CliDtoFactory(metaclass=StaticFuncMeta, data=CliDtoFactoryMetaInput):
    """Toolkit for constructing normalized CliDTO items."""

    def panel(
        content: Renderable | list[Renderable],  # noqa:N805
        *,
        title: str | None = None,
        expand: bool = True,
        **kwargs: Any,
    ) -> PanelDTO:
        """Create a framed PanelDTO container."""
        return PanelDTO(content=content, title=title, expand=expand, **kwargs)

    def group(*items: Renderable) -> GroupDTO:
        """Create a GroupDTO stacking multiple renderables."""
        return GroupDTO(content=list(items))

    def line(character: str = "─", *, style: str = "cyan") -> LineDTO:  # noqa:N805
        """Create a horizontal character LineDTO."""
        return LineDTO(content=character, color=style)

    def markdown(
        text: str,  # noqa:N805
        *,
        header: int = 0,
        style: str = "white",  # noqa:N805
    ) -> MarkdownDTO:
        """Create a MarkdownDTO with validated header constraints (H0-H6)."""
        if not (0 <= header <= 6):
            warnings.warn(
                f"Markdown header={header} invalid (expected H0-H6). Defaulting to 0.",
                stacklevel=2,
            )
            header = 0
        return MarkdownDTO(content=text, header=header, color=style)

    def table_from_rows(
        rows: dict[str, Any | Sequence[Any]],  # noqa:N805
        *,
        corner: str = "",
    ) -> TableDTO:
        """Transform dict of {row_name: values} into a TableDTO."""
        content = [
            list(v) if isinstance(v, (list, tuple)) else [v]
            for v in rows.values()
        ]
        return TableDTO(
            content=content,
            row_names=list(rows.keys()),
            corner=corner,
        )

    def table_from_cols(
        cols: dict[str, Sequence[Any]],  # noqa:N805
        *,
        corner: str = "",
    ) -> TableDTO:
        """Transform dict of {col_name: column_values} into a TableDTO (transposed)."""
        content = [list(row) for row in zip(*cols.values(), strict=True)]
        return TableDTO(
            content=content,
            col_names=list(cols.keys()),
            corner=corner,
        )

    def table_from_records(
        records: Sequence[dict[str, Any]],  # noqa:N805
        headers: list[str] | None = None,
    ) -> TableDTO:
        """Transform list of row dicts [{'ColA': 1, 'ColB': 2}] into a TableDTO."""
        if not records:
            return TableDTO(content=[])

        if headers is None:
            headers = list(
                dict.fromkeys(k for row in records for k in row.keys())
            )

        content = [[row.get(h, "") for h in headers] for row in records]
        return TableDTO(content=content, col_names=headers)
