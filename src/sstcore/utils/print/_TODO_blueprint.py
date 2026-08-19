"""
Sketch the Structure of the Printer

- Protocol with all functions

"""

from pathlib import Path

from ..tree import SimpleTreeNode

__all__: list[str] = [
    "Printer",
    "Modus",
]

from enum import Enum, auto
from typing import Any, Literal, Protocol

import rich
from rich.align import AlignMethod
from rich.box import Box
from rich.theme import Theme

from ...port.event.dto import (
    CliDTO,
    LineDTO,
    LogDTO,
    MarkdownDTO,
    PanelDTO,
    RuleDTO,
    TableDTO,
)
from ...port.view import RichRenderable
from ..color import ColorBox, Palette  # AI: this is outdated


class Modus(Enum):
    NULL = auto()
    DEBUG = auto()
    EMIT = auto()
    RICH = auto()


class Printer(Protocol):
    """
    Define the Interface of the Printer

    - Support Mixin implementation
    - Type hint dynamically built printers

    """

    # meta
    project_name: str
    project_version: str

    @property
    def project_info(self) -> str: ...
    def set_project_info(self, name: str, version: str) -> None: ...

    # base
    palette: Palette
    theme: Theme
    console: rich.Console

    def print(self, *args, **kwargs): ...

    def load_theme(self, theme: dict[str, str] | None = None) -> None: ...
    def preview_themes(self) -> None: ...

    modus: Modus = Modus.RICH

    def mute(self) -> None: ...
    def debug(self) -> None: ...
    def wire(self) -> None: ...
    def unmute(self) -> None: ...
    def in_modus(self, modus: Modus): ...
    def muted(self) -> Any: ...
    def on_debug(self) -> Any: ...
    def wired(self) -> Any: ...

    # core
    def __call__(self, target: Any, **kwargs) -> None: ...

    # essentials
    color_box: ColorBox  # AI_FOCUS: rich has still high priority but not as obly priority

    @property
    def _cb(self) -> ColorBox: ...
    def color(self, text: str, color: str | None = None) -> str: ...
    def normalize(self, target: Any, **kwargs) -> str: ...
    def render(self, target: CliDTO | LogDTO, **kwargs) -> RichRenderable: ...
    #
    def render_panel(self, dto: PanelDTO) -> RichRenderable: ...
    def render_line(self, dto: LineDTO) -> RichRenderable: ...
    def render_rule(self, dto: RuleDTO) -> RichRenderable: ...
    def render_table(self, dto: TableDTO) -> RichRenderable: ...
    def render_markdown(self, dto: MarkdownDTO) -> RichRenderable: ...
    def render_log(self, dto: LogDTO) -> RichRenderable: ...

    # color
    # AI: here a task for the ColorStack
    def white(self, target: Any) -> None: ...
    def blue(self, target: Any) -> None: ...
    def red(self, target: Any) -> None: ...
    def green(self, target: Any) -> None: ...
    def cyan(self, target: Any) -> None: ...
    def magenta(self, target: Any) -> None: ...
    def yellow(self, target: Any) -> None: ...
    def black(self, target: Any) -> None: ...

    # layout
    def panel(self, target: Any, **kwargs) -> None: ...
    # line
    def line(self, style: str = "", title: str | None = None) -> None: ...
    def lines(
        self,
        lines: list,
        style: str = "cyan",
        title: str | None = None,
        header: str | None = None,
    ) -> None: ...
    def lines_with_len(
        self, name: str, lines: list, style: str = "cyan"
    ) -> None: ...
    # box
    def box(self, target: Any, frame: str = "", box: Box = ...) -> None: ...
    def box_top(self, target: Any, frame: str = "") -> None: ...
    def box_bottom(self, target: Any, frame: str = "") -> None: ...
    def mini_box(
        self,
        target: Any,
        frame: str = "",
        mode: Literal["up", "down", "both"] = "both",
    ) -> None: ...
    def corner(self, target: Any, frame: str = "", box: Box = ...) -> None: ...
    # header
    # AI: here as well a task for the ColorStack, probably most of the functions
    def header(self, text: Any, frame: str = "cyan", **kwargs) -> None: ...
    def title(
        self,
        text: Any,
        title: str = "",
        title_align: AlignMethod = "right",
        **kwargs,
    ) -> None: ...
    # AI: here semantic roles
    def success(self, text: Any) -> None: ...
    def danger(self, text: Any) -> None: ...
    def warn(self, text: Any) -> None: ...
    def special(self, text: Any) -> None: ...
    def dip(self, head: str, text: str, color: str) -> None: ...

    def md(self, text: str, *args, header: int = 0, **kwargs) -> None: ...

    # tool
    def path_exists_table(
        self, paths: list[Path], title=None, header="Path"
    ) -> None: ...
    def dict_table(
        self,
        target: dict,
        header="Dict Inspection",
        show_type: bool | tuple[bool, bool] = (True, True),
        style="green",
    ): ...
    def tree_graph(
        self: Printer,
        simple_tree: SimpleTreeNode,
        max_depth: int | None = None,
        root: str = "bold magenta",
        node: str = "by_level",
        guide: str = "bold white",
        hide_root=False,
    ) -> None: ...
