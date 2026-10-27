"""
Interactive PrintFunctors mounted on PrinterLayouts.

Replaces _old_layout_todos.py by turning layout methods into rich Functors
with sub-commands and multi-level presets.
"""

__all__: list[str] = [
    "PrintFunctor",
    "PanelPrintFunctor",
    "LinePrintFunctor",
    "BoxPrintFunctor",
    "TablePrintFunctor",
    "HeaderPrintFunctor",
    "DipPrintFunctor",
]

from collections.abc import Mapping, Sequence
from typing import Any, Literal, Self, Unpack

from ...forge.func import SafeFunctor
from ...forge.view.factory._table import TableViewDTO
from ...port import functorial
from ...port.color import Color, ColorArg
from ...port.event import dto
from ...port.event._param import FrameInput, HeaderFrameInput, HeaderInput
from ...port.event.dto import CliInput
from ...port.link import portlink
from ...port.printer import Print
from ._boxes import Boxes


# MOVE: to final input design assembly
class UntitledPanelInput(CliInput, HeaderFrameInput, FrameInput, total=False):
    """PanelInput without 'title' (for presets taking title positionally)."""


# MOVE: to final input design assembly
class ColoredHeaderInput(HeaderFrameInput, FrameInput, total=False):
    """PanelInput without 'title' and 'color' (for semantic presets like success/warn/danger)."""

    infos: Mapping


# MOVE: to final input design assembly
class BoxlessPanelInput(CliInput, HeaderInput, total=False):
    """PanelInput without 'box' (for box presets where box is pre-selected)."""

    topic: str
    topic_color: ColorArg


@portlink(functorial.MountableFunctor)
class PrintFunctor[DTO: dto.EventDTO = dto.EventDTO](SafeFunctor[..., DTO]):
    """Base Functor bound to the Printer instance."""

    def __init__(
        self,
        host: Print,  # WARN: annotate with :Print might be a bad idea here...
        **kwargs: Any,
    ) -> None:
        self.host: Print = host
        super().__init__(**kwargs)

    @classmethod
    def __mount__(cls, host: Any, /, *, name: str = "", **kwargs: Any) -> Self:
        return cls(host=host, name=name, **kwargs)


# ---------------------------------------------------------------------------
# 1. PANEL FUNCTOR (Level 1 & Invert-Header support)
# ---------------------------------------------------------------------------


@portlink(functorial.MountableFunctor)
class PanelPrintFunctor(PrintFunctor[dto.PanelDTO]):
    """Direct Panel printing + quick variations."""

    def __call__(
        self, *content: dto.CliSpec, **kw: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO:
        return self.host(self.host.dto.panel(*content, **kw))


# ---------------------------------------------------------------------------
# 2. LINE FUNCTOR (Unboxed lines, rules, and counted line blocks)
# ---------------------------------------------------------------------------


@portlink(functorial.MountableFunctor)
class LinePrintFunctor(PrintFunctor[dto.LineDTO]):
    """
    Handle single separator lines, sequential lines, and counted blocks.

    Examples:
        printer.lines()                           # Prints horizontal rule
        printer.lines("a", "b", title="Items")    # Sequential lines with header
        printer.lines.len("Files", file_list)     # Header "Files: 12" + lines
    """

    def __call__(
        self, *content: dto.CliSpec, **kw: Unpack[dto.LineInput]
    ) -> dto.LineDTO:
        return self.host(self.host.dto.line(*content, **kw))

    def rule(self, color: ColorArg = Color.AZURE) -> dto.LineDTO:
        """Print a clean horizontal divider line."""
        return self(color=color)

    def len(
        self,
        name: str,
        lines: Sequence[dto.CliSpec],
        **kw: Unpack[UntitledPanelInput],
    ) -> dto.PanelDTO:
        """Renders a panel with 'name: <count>' as header and 'name' as frame topic."""

        header_title = f"{name}: {len(lines)}"
        kw.setdefault("topic", name)
        return self.host.panel(*lines, title=header_title, **kw)


# ---------------------------------------------------------------------------
# 3. BOX FUNCTOR (Open, Top, Bottom, Mini variations)
# ---------------------------------------------------------------------------


@portlink(functorial.MountableFunctor)
class BoxPrintFunctor(PrintFunctor[dto.PanelDTO]):
    def __call__(
        self,
        *content: dto.CliSpec,
        box: Boxes = Boxes.OPEN,
        **kw: Unpack[BoxlessPanelInput],
    ) -> dto.PanelDTO:
        return self.host.panel(*content, box=box, **kw)

    def top(
        self, *content: dto.CliSpec, **kw: Unpack[BoxlessPanelInput]
    ) -> dto.PanelDTO:
        """Box with top border focus (Boxes.UP)."""
        return self(*content, box=Boxes.UP, **kw)

    def bottom(
        self, *content: dto.CliSpec, **kw: Unpack[BoxlessPanelInput]
    ) -> dto.PanelDTO:
        """Box with bottom border focus (Boxes.DOWN)."""
        return self(*content, box=Boxes.DOWN, **kw)

    def round(
        self, *content: dto.CliSpec, **kw: Unpack[BoxlessPanelInput]
    ) -> dto.PanelDTO:
        """Box with rounded corners (Boxes.ROUND)."""
        return self(*content, box=Boxes.ROUND, **kw)

    def mini(
        self,
        *content: dto.CliSpec,
        mode: Literal["up", "down", "both"] = "both",
        **kw: Unpack[BoxlessPanelInput],
    ) -> dto.PanelDTO:
        """Minimalist box borders (up, down, or both)."""
        box_map: dict[str, Boxes] = {
            "up": Boxes.MINI_UP,
            "down": Boxes.MINI_DOWN,
            "both": Boxes.MINI,
        }
        return self(*content, box=box_map[mode], **kw)


# ---------------------------------------------------------------------------
# 4. TABLE FUNCTOR (Direct Grid + Ergonomic Builders from _table.py)
# ---------------------------------------------------------------------------


@portlink(functorial.MountableFunctor)
class TablePrintFunctor(PrintFunctor[TableViewDTO]):
    def __call__(
        self, content: dto._Grid, /, **kw: Unpack[dto.TableInput]
    ) -> TableViewDTO:
        return self.host(self.host.dto.table(content, **kw))

    def cols(
        self,
        cols: dict[str, Sequence[Any]],
        *,
        corner: str = "",
        title: str | None = None,
        color: ColorArg = Color.AZURE,
    ) -> TableViewDTO:
        """Create and print a table from a dictionary of columns {col_name: values}."""
        table_dto = TableViewDTO.from_cols(cols, corner=corner)
        if title is not None:
            table_dto.header.title = title
        table_dto.color = Color(color)
        return self.host(table_dto)

    def rows(
        self,
        rows: dict[str, dto.CliSpec | list[dto.CliSpec]],
        *,
        title: str | None = None,
        color: ColorArg = Color.AZURE,
    ) -> TableViewDTO:
        """Create and print a table from a dictionary of rows {row_name: cells}."""
        table_dto = TableViewDTO.from_rows(rows)
        if title is not None:
            table_dto.header.title = title
        table_dto.color = Color(color)
        return self.host(table_dto)

    def records(
        self,
        records: Sequence[dict[str, Any]],
        headers: list[str] | None = None,
        *,
        title: str | None = None,
        color: ColorArg = Color.AZURE,
    ) -> TableViewDTO:
        """Create and print a table from a list of row dicts."""
        table_dto = TableViewDTO.from_records(records, headers=headers)
        if title is not None:
            table_dto.header.title = title
        table_dto.color = Color(color)
        return self.host(table_dto)

    def matrix(
        self,
        matrix: list[list[dto.CliSpec]],
        *,
        title: str | None = None,
        color: ColorArg = Color.AZURE,
    ) -> TableViewDTO:
        """Create and print a table from a 2D list."""
        table_dto = TableViewDTO.from_matrix(matrix, title=title)
        table_dto.color = Color(color)
        return self.host(table_dto)


# ---------------------------------------------------------------------------
# 5. HEADER & DIP FUNCTORS (Standalone Banner vs Titled Panel + Color Dip)
# ---------------------------------------------------------------------------


@portlink(functorial.MountableFunctor)
class HeaderPrintFunctor(PrintFunctor[dto.PanelDTO]):
    def __call__(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[UntitledPanelInput],
    ) -> dto.PanelDTO:
        if not content:
            styled_title = self.host.colors(title, Color.WHITE)
            return self.host.panel(styled_title, **kw)
        return self.host.panel(*content, title=title, **kw)


@portlink(functorial.MountableFunctor)
class DipPrintFunctor(PrintFunctor[dto.PanelDTO]):
    def __call__(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        color: ColorArg = Color.AZURE,
        **kw: Unpack[ColoredHeaderInput],
    ) -> dto.PanelDTO:
        colored_head = self.host.colors(head, color)
        white_text = self.host.colors(text, Color.WHITE)
        banner = f"{colored_head} {white_text}"
        if not content:
            return self.host.panel(banner, color=color, **kw)
        return self.host.panel(*content, title=banner, color=color, **kw)

    # LATER: make them below accessable by StackingCore
    def azure(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        **kw: Unpack[ColoredHeaderInput],
    ) -> dto.PanelDTO:
        return self(head, text, *content, color=Color.AZURE, **kw)

    def green(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        **kw: Unpack[ColoredHeaderInput],
    ) -> dto.PanelDTO:
        return self(head, text, *content, color=Color.GREEN, **kw)

    def yellow(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        **kw: Unpack[ColoredHeaderInput],
    ) -> dto.PanelDTO:
        return self(head, text, *content, color=Color.YELLOW, **kw)

    def red(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        **kw: Unpack[ColoredHeaderInput],
    ) -> dto.PanelDTO:
        return self(head, text, *content, color=Color.RED, **kw)

    def purple(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        **kw: Unpack[ColoredHeaderInput],
    ) -> dto.PanelDTO:
        return self(head, text, *content, color=Color.PURPLE, **kw)
