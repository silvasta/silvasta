"""
Interactive PrintFunctors mounted on PrinterLayouts.

-
"""  # TODO:

__all__: list[str] = [
    "PrintFunctor",
    "LinePrintFunctor",
    "BoxPrintFunctor",
    "TablePrintFunctor",
    "HeaderPrintFunctor",
    "DipPrintFunctor",
]

from collections.abc import Mapping, Sequence
from typing import Any, Literal, Self
from typing import Unpack as _U  # noqa:N814

from ...forge.func import SafeFunctor
from ...forge.view.factory._table import TableViewDTO
from ...port import functorial
from ...port._types import EventTypes as _ET  # noqa: N814
from ...port.color import Color, ColorArg
from ...port.event import _param as _p
from ...port.event.dto import (
    EventDTO,
    LineDTO,
    PanelDTO,
)
from ...port.link import portlink
from ._boxes import Boxes


@portlink(functorial.MountableFunctor)
class PrintFunctor[DTO: EventDTO = EventDTO](SafeFunctor[..., DTO]):
    """Base Functor bound to the Printer instance."""

    def __init__(self, host: Any, **kwargs: Any) -> None:
        self.host: Any = host
        super().__init__(**kwargs)

    @classmethod
    def __mount__(cls, host: Any, /, *, name: str = "", **kwargs: Any) -> Self:
        return cls(host=host, name=name, **kwargs)


@portlink(functorial.MountableFunctor)
class LinePrintFunctor(PrintFunctor[LineDTO]):
    """
    Handle single separator lines, sequential lines, and counted line blocks.

    Examples:
        printer.line()                            # Empty line with bg color
        printer.lines("a", "b", title="Items")    # Sequential lines with header
        printer.lines.len("Files", file_list)     # Header "Files: 12" + lines
    """

    def __call__(
        self, *content: _ET.CliSpec, **kw: _U[_p.LineInput]
    ) -> LineDTO:
        return self.host(self.host._p.line(*content, **kw))

    def len(
        self,
        name: str,
        *content: _ET.CliSpec | Sequence[_ET.CliSpec],
        **kw: _U[_p.LinePresetInput],
    ) -> LineDTO:
        if (
            len(content) == 1
            and isinstance(content[0], Sequence)
            and not isinstance(content[0], (str, bytes))
        ):
            items: tuple[_ET.CliSpec, ...] = tuple(content[0])
        else:
            items: tuple[_ET.CliSpec, ...] = tuple(
                c
                for c in content
                if not isinstance(c, Sequence) or isinstance(c, str)
            )

        header_title = f"{name}: {len(items)}"
        merged: dict[str, Any] = dict(kw)
        merged.setdefault("header_topic", name)
        return self(
            *items,
            title=header_title,
            stat=lambda vec: f"{name}: {len(vec)}",
            **merged,
        )


@portlink(functorial.MountableFunctor)
class BoxPrintFunctor(PrintFunctor[PanelDTO]):
    """Mid-level structural functor for Box variations."""

    def __call__(
        self,
        *content: _ET.CliSpec,
        box: Boxes = Boxes.OPEN,
        **kw: _U[_p.BoxInput],
    ) -> PanelDTO:
        return self.host.panel(*content, box=box, **kw)

    def open(self, *content: _ET.CliSpec, **kw: _U[_p.BoxInput]) -> PanelDTO:
        return self(*content, box=Boxes.OPEN, **kw)

    def round(self, *content: _ET.CliSpec, **kw: _U[_p.BoxInput]) -> PanelDTO:
        return self(*content, box=Boxes.ROUND, **kw)

    def corner(self, *content: _ET.CliSpec, **kw: _U[_p.BoxInput]) -> PanelDTO:
        return self(*content, box=Boxes.CORNER, **kw)

    def up(self, *content: _ET.CliSpec, **kw: _U[_p.BoxInput]) -> PanelDTO:
        return self(*content, box=Boxes.UP, **kw)

    def down(self, *content: _ET.CliSpec, **kw: _U[_p.BoxInput]) -> PanelDTO:
        return self(*content, box=Boxes.DOWN, **kw)

    def mini(
        self,
        *content: _ET.CliSpec,
        mode: Literal["up", "down", "both"] = "both",
        **kw: _U[_p.BoxInput],
    ) -> PanelDTO:
        box_map: dict[str, Boxes] = {
            "up": Boxes.MINI_UP,
            "down": Boxes.MINI_DOWN,
            "both": Boxes.MINI,
        }
        return self(*content, box=box_map[mode], **kw)

    def mini_up(self, *content: _ET.CliSpec, **kw: _U[_p.BoxInput]) -> PanelDTO:
        return self(*content, box=Boxes.MINI_UP, **kw)

    def mini_down(
        self, *content: _ET.CliSpec, **kw: _U[_p.BoxInput]
    ) -> PanelDTO:
        return self(*content, box=Boxes.MINI_DOWN, **kw)


@portlink(functorial.MountableFunctor)
class TablePrintFunctor(PrintFunctor[TableViewDTO]):
    """Exposes all TableDtoProducer builders directly on `printer.table.*`."""

    def __call__(
        self, content: _ET.Grid, /, **kw: _U[_p.TableInput]
    ) -> TableViewDTO:
        return self.host(self.host._p.table(content, **kw))

    def matrix(
        self,
        matrix: Sequence[Sequence[_ET.CliSpec]],
        /,
        **kw: _U[_p.TablePresetInput],
    ) -> TableViewDTO:
        return self.host(self.host._p.table.matrix(matrix, **kw))

    def rows(
        self,
        rows: Mapping[str, _ET.CliSpec | Sequence[_ET.CliSpec]],
        /,
        **kw: _U[_p.TablePresetInput],
    ) -> TableViewDTO:
        return self.host(self.host._p.table.rows(rows, **kw))

    def cols(
        self,
        cols: Mapping[str, Sequence[Any]],
        /,
        *,
        corner: str = "",
        **kw: _U[_p.TablePresetInput],
    ) -> TableViewDTO:
        return self.host(self.host._p.table.cols(cols, corner=corner, **kw))

    def records(
        self,
        records: Sequence[Mapping[str, Any]],
        /,
        *,
        headers: Sequence[str] | None = None,
        **kw: _U[_p.TablePresetInput],
    ) -> TableViewDTO:
        return self.host(
            self.host._p.table.records(records, headers=headers, **kw)
        )

    def kv(
        self,
        mapping: Mapping[str, Any],
        /,
        *,
        key_col: str = "Key",
        val_col: str = "Value",
        **kw: _U[_p.TablePresetInput],
    ) -> TableViewDTO:
        return self.host(
            self.host._p.table.kv(
                mapping, key_col=key_col, val_col=val_col, **kw
            )
        )


@portlink(functorial.MountableFunctor)
class HeaderPrintFunctor(PrintFunctor[PanelDTO]):
    def __call__(
        self,
        title: str,
        *content: _ET.CliSpec,
        **kw: _U[_p.HeaderPresetInput],
    ) -> PanelDTO:
        if not content:
            styled_title = self.host.colors(title, Color.WHITE)
            return self.host.panel(styled_title, **kw)
        return self.host.panel(*content, title=title, **kw)


@portlink(functorial.MountableFunctor)
class DipPrintFunctor(PrintFunctor[PanelDTO]):
    def __call__(
        self,
        head: str,
        text: str,
        *content: _ET.CliSpec,
        color: ColorArg = Color.AZURE,
        **kw: _U[_p.StatusInput],
    ) -> PanelDTO:
        colored_head = self.host.colors(head, color)
        white_text = self.host.colors(text, Color.WHITE)
        banner = f"{colored_head} {white_text}"
        if not content:
            return self.host.panel(banner, color=color, **kw)
        return self.host.panel(*content, title=banner, color=color, **kw)

    def azure(
        self,
        head: str,
        text: str,
        *content: _ET.CliSpec,
        **kw: _U[_p.StatusInput],
    ) -> PanelDTO:
        return self(head, text, *content, color=Color.AZURE, **kw)

    def green(
        self,
        head: str,
        text: str,
        *content: _ET.CliSpec,
        **kw: _U[_p.StatusInput],
    ) -> PanelDTO:
        return self(head, text, *content, color=Color.GREEN, **kw)

    def yellow(
        self,
        head: str,
        text: str,
        *content: _ET.CliSpec,
        **kw: _U[_p.StatusInput],
    ) -> PanelDTO:
        return self(head, text, *content, color=Color.YELLOW, **kw)

    def red(
        self,
        head: str,
        text: str,
        *content: _ET.CliSpec,
        **kw: _U[_p.StatusInput],
    ) -> PanelDTO:
        return self(head, text, *content, color=Color.RED, **kw)

    def purple(
        self,
        head: str,
        text: str,
        *content: _ET.CliSpec,
        **kw: _U[_p.StatusInput],
    ) -> PanelDTO:
        return self(head, text, *content, color=Color.PURPLE, **kw)
