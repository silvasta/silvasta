"""
CliFactory - Experiment 3

- Tiny but by far the besgt so far!

"""

from typing import Any

from ...brick.color.box import Colors
from ...port.color import ColorBox
from ...port.event.dto import LineDTO, PanelDTO, TableDTO

colors: ColorBox = Colors()  # ty:ignore


class TableProducer:
    """Counterpart to RenderMixin.render_table"""

    def from_row_dicts(
        self, rows: dict[str, Any | list[Any]], **kwargs
    ) -> TableDTO:
        return TableDTO(
            content=list(rows.values()), row_names=list(rows.keys()), **kwargs
        )

    def from_col_dicts(self, cols: dict[str, list[Any]], **kwargs) -> TableDTO:
        return TableDTO(
            content=[list(row) for row in zip(*cols.values(), strict=True)],
            col_names=list(cols.keys()),
            **kwargs,
        )


class LayoutProducer:
    """Counterpart to RenderMixin.render_panel and render_line"""

    def panel(
        self, content: Any, title: str | None = None, **kwargs
    ) -> PanelDTO:
        return PanelDTO(content=content, title=title, **kwargs)

    def line(
        self, style: str = "cyan", character: str = "─", **kwargs
    ) -> LineDTO:
        return LineDTO(style=style, character=character, **kwargs)


class CliDtoFactory:
    """Unified entry point for CLI Layout generation."""

    def __init__(self):
        self.table = TableProducer()
        self.layout = LayoutProducer()


# Provide a ready-to-use instance
cli_factory = CliDtoFactory()
