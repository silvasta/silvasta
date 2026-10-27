"""
Prepare Functors, 1 per DTO

- add optional safe mode
- handle stacked functions

"""

__all__: list[str] = [
    "LogDtoVisualizer",
    "CliDtoVisualizer",
    "PanelDtoVisualizer",
    "MarkdownDtoVisualizer",
    "LineDtoVisualizer",
    "TableDtoVisualizer",
]

from pathlib import Path
from typing import Any, Literal, Self

from rich.console import Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ....brick.color import colorize
from ....brick.color.box import Colors
from ....forge.func import SafeFunctor
from ....port import functorial
from ....port.color import Color
from ....port.event import _param as _p
from ....port.event import dto
from ....port.event.dto import DtoNames
from ....port.link import portlink
from ....port.represent import PydanticModel, Richable, RichConsolable, RichView
from ._log import render_log


@portlink(functorial.MountableFunctor)
class DtoVisualizer[DTO: dto.EventDTO = dto.EventDTO](
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

    def normalize(self, target: Any, /) -> Richable:
        match target:
            case RichView() | RichConsolable() | str() | PydanticModel():
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
        self, content: Any, frame: _p.FrameSpec, color: Color
    ) -> Panel:
        """Wrap any renderable in a FrameSpec-configured Rich Panel."""
        topic: str | None = (
            self.colors(frame.topic, frame.topic_color)  #
            if frame.topic
            else None
        )
        return Panel(
            renderable=self.normalize(content),
            title=topic,
            title_align="right",
            border_style=self.colors.paint(color),
            # LATER: padding=dto.padding,
            # LATER: expand=dto.expand,
            box=frame.box.get(),
        )

    def apply_header(
        self, main_renderable: Richable, /, header: _p.HeaderSpec, color: Color
    ) -> Richable:
        """If HeaderSpec has a title, stack a header Panel above the main content."""
        if not header.title:
            return main_renderable

        header_panel: Panel = self.build_panel(
            content=Text(header.title, style="bold white"),
            frame=header.frame,
            color=color,
        )
        return Group(header_panel, main_renderable)


#  LINE: -- Log and Cli Base -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LogDtoVisualizer(DtoVisualizer[dto.LogDTO]):
    dto_name = "log"

    def __call__(
        self, target: dto.LogDTO, /, index: Literal[0, 1, 2] = 0
    ) -> Richable:
        return render_log(target, select=index)


class CliDtoVisualizer(DtoVisualizer[dto.CliDTO]):
    dto_name = "cli"

    def __call__(self, target: dto.CliDTO, /) -> Richable:
        if isinstance(target, RichView):
            # CHECK: avoids __rich__ view is flattened to text?
            # - maybe include in normalize
            text = target.__rich__()
        else:
            text = str(self.normalize(target.content))

        return Text(text, style=self.colors.paint(target.color))


#  LINE: -- Cli Specifications -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PanelDtoVisualizer(DtoVisualizer[dto.PanelDTO]):
    dto_name = "panel"

    def __call__(self, target: dto.PanelDTO, /) -> Richable:
        body: Panel = self.build_panel(
            target.content,
            target.frame,
            target.color,
        )
        return self.apply_header(body, target.header, target.color)


class LineDtoVisualizer(DtoVisualizer[dto.LineDTO]):
    dto_name = "line"

    def __call__(self, target: dto.LineDTO, /) -> Richable:
        # REMOVE: no --- line, no Rule!
        # TODO: just an empty line with nothing but background color
        # if not target.content:
        #     return Text("─" * 50, style=str(target.color))
        body = self.normalize(target.content)
        return self.apply_header(body, target.header, target.color)


class MarkdownDtoVisualizer(DtoVisualizer[dto.MarkdownDTO]):
    dto_name = "markdown"

    def __call__(self, target: dto.MarkdownDTO, /) -> Richable:
        content = Markdown(str(target.content))
        if target.frame.topic:
            return self.build_panel(content, target.frame, target.color)
        return content


class TableDtoVisualizer(DtoVisualizer[dto.TableDTO]):
    dto_name = "table"

    def __call__(self, target: dto.TableDTO, /) -> Richable:
        topic: str | None = (
            self.colors(target.frame.topic, target.frame.topic_color)
            if target.frame.topic
            else None
        )
        table = Table(
            title=topic,
            border_style=self.colors.paint(target.color),
            box=target.frame.box.get(),
        )

        if target.row_names:
            table.add_column(target.corner, style=self.colors.orange)
        for col in target.col_names:
            table.add_column(str(col), style=self.colors.azure)

        for idx, row in enumerate(target.content):
            cells: list[str] = [str(self.normalize(c)) for c in row]
            if target.row_names and idx < len(target.row_names):
                cells.insert(0, str(target.row_names[idx]))
            table.add_row(*cells)

        return self.apply_header(table, target.header, target.color)
