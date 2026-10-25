"""
Prepare Functors, 1 per DTO

- add optional safe mode
- handle stacked functions

"""

from sstcore.brick.color.box import Colors

__all__: list[str] = [
    "LogDtoRenderer",
    "CliDtoRenderer",
    "PanelDtoRenderer",
    "MarkdownDtoRenderer",
    "LineDtoRenderer",
    "TableDtoRenderer",
]

from pathlib import Path
from typing import Any, Self

from rich.console import ConsoleRenderable, Group, RichCast
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ....brick.color import colorize
from ....forge.func import SafeFunctor
from ....port import functorial
from ....port.event import _param as _p
from ....port.event import dto
from ....port.event.dto import DtoNames
from ....port.link import portlink
from ....port.represent import PydanticModel, Richable


@portlink(functorial.MountableFunctor)
class DtoRenderer[DTO: dto.EventDTO = dto.EventDTO](
    SafeFunctor[[DTO], Richable]
):
    """Visualize the DTO - handle variations"""

    dto_name: DtoNames

    def __init__(self, colors: Colors, **kwargs: Any) -> None:
        """Use Colors (ColorBox implementation) Inside"""
        self.colors: Colors = colors
        super().__init__(**kwargs)

    @classmethod
    def __mount__(cls, host: Any, /, *, name: str = "", **kwargs: Any) -> Self:
        return cls(colors=host.colors, name=name, **kwargs)

    def normalize(self, target: Any) -> Richable:
        match target:
            case ConsoleRenderable() | RichCast() | str() | PydanticModel():
                return target
            case tuple() | list() as items:
                return "\n".join(str(self.normalize(i)) for i in items)
            case Path() as path:
                return colorize.path(path)
            case type():
                return colorize.modules(target)
            case _:
                return str(target)

    def build_panel(
        self, content: Any, frame: _p.FrameSpec, border_color: str
    ) -> Panel:
        """Wrap any renderable in a FrameSpec-configured Rich Panel."""
        topic = (
            # FIX:
            f"[{frame.topic_color}]{frame.topic}[/]" if frame.topic else None
        )
        return Panel(
            renderable=self.normalize(content),
            title=topic,
            title_align="right",
            border_style=border_color,
            box=frame.box.value,  # Assuming Boxes enum resolves to rich.box.Box
        )

    def apply_header(
        self, main_renderable: Richable, header: _p.HeaderSpec, color: str
    ) -> Richable:
        """If HeaderSpec has a title, stack a header Panel above the main content."""
        if not header.title:
            return main_renderable

        header_panel = self.build_panel(
            content=Text(header.title, style="bold white"),
            frame=header.frame,
            border_color=color,
        )
        return Group(header_panel, main_renderable)


#  LINE: -- Log and Cli Base -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LogDtoRenderer(DtoRenderer[dto.LogDTO]):
    dto_name = "log"

    def __call__(self, target: dto.LogDTO, /) -> Richable: ...


class CliDtoRenderer(DtoRenderer[dto.CliDTO]):
    dto_name = "cli"

    def __call__(self, target: dto.CliDTO, /) -> Richable:
        text = str(self.normalize(target.content))
        return Text.from_markup(f"[{target.color}]{text}[/]")


#  LINE: -- Cli Specifications -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PanelDtoRenderer(DtoRenderer[dto.PanelDTO]):
    dto_name = "panel"

    def __call__(self, target: dto.PanelDTO, /) -> Richable:
        body: Panel = self.build_panel(
            target.content,
            target.frame,
            str(target.color),  # FIX:
        )
        return self.apply_header(body, target.header, str(target.color))


class LineDtoRenderer(DtoRenderer[dto.LineDTO]):
    dto_name = "line"

    def __call__(self, target: dto.LineDTO, /) -> Richable:
        if not target.content:
            # FIX:
            return Text("─" * 50, style=str(target.color))
        body = self.normalize(target.content)
        return self.apply_header(body, target.header, str(target.color))


class MarkdownDtoRenderer(DtoRenderer[dto.MarkdownDTO]):
    dto_name = "markdown"

    def __call__(self, target: dto.MarkdownDTO, /) -> Richable:
        md = Markdown(str(target.content))
        if target.frame.topic:
            return self.build_panel(md, target.frame, str(target.color))
        return md


class TableDtoRenderer(DtoRenderer[dto.TableDTO]):
    dto_name = "table"

    def __call__(self, target: dto.TableDTO, /) -> Richable:
        table = Table(
            border_style=str(target.color), box=target.frame.box.value
        )

        if target.row_names:
            table.add_column(target.corner, style="bold magenta")
        for col in target.col_names:
            table.add_column(str(col), style="cyan")

        for idx, row in enumerate(target.content):
            cells = [str(self.normalize(c)) for c in row]
            if target.row_names and idx < len(target.row_names):
                cells.insert(0, str(target.row_names[idx]))
            table.add_row(*cells)

        return self.apply_header(table, target.header, str(target.color))
