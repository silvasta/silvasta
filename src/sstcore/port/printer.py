"""
Sketch the Structure of the Printer

                                    DependencyLevel.sstcore.port[9]
"""

__all__: list[str] = [
    "PrintBase",
    "PrintMode",
    "PrintLayouts",
    "Printing",
    "Print",
]


from collections.abc import Callable, Sequence
from enum import auto
from string.templatelib import Template
from typing import Any, Literal, Protocol, TypedDict, Unpack

from ._types import _Stringable
from .color import ColorArg, ColorBox, ColorId
from .config import ProjectInformation
from .event import dto
from .event._param import _Boxes
from .event.dto import CliDTO, EventDTO
from .event.factory import EventDtoFactory, TableDelivering
from .solid import EnumMode


class PrintMode(EnumMode):
    """Define the Execution Mode"""

    RICH = auto()
    DEBUG = auto()
    PRINT = auto()
    NULL = auto()

    @classmethod
    def default(cls) -> PrintMode:  # LATER: this on BaseEnum?
        return cls.RICH


class PrintBase(Protocol):
    """Define the Base of the Printer"""

    info: ProjectInformation
    mode: PrintMode

    @property
    def colors(self) -> ColorBox: ...
    @property
    def project_info(self) -> str:
        """Style the top right title of printer.title Panel"""

    def __call__(self, target: Any, /, **kwargs) -> Any:
        """Print the target and return the manual"""

    def muted(self) -> Any: ...
    def mute(self) -> None: ...
    def unmute(self) -> None: ...
    def debug(self) -> Any: ...
    def in_mode(self, modus: PrintMode): ...


class LinePrinting(Protocol):
    def __call__(
        self, *content: dto.CliSpec, **kw: Unpack[dto.LineInput]
    ) -> dto.LineDTO: ...

    def len(
        self,
        name: str,
        *content: dto.CliSpec | Sequence[dto.CliSpec],
        **kw: Unpack[dto.LinePresetInput],
    ) -> dto.LineDTO: ...


class BoxPrinting(Protocol):
    def __call__(
        self,
        *content: dto.CliSpec,
        box: _Boxes = _Boxes.OPEN,
        **kw: Unpack[dto.BoxInput],
    ) -> dto.PanelDTO: ...

    def open(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def round(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def corner(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def up(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def down(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def mini(
        self,
        *content: dto.CliSpec,
        mode: Literal["up", "down", "both"] = "both",
        **kw: Unpack[dto.BoxInput],
    ) -> dto.PanelDTO: ...
    def mini_up(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def mini_down(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...


class HeaderPrinting(Protocol):
    def __call__(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.HeaderPresetInput],
    ) -> dto.PanelDTO: ...


class DipPrinting(Protocol):
    def __call__(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        color: ColorArg = ...,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO: ...

    def azure(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO: ...
    def green(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO: ...
    def yellow(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO: ...
    def red(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO: ...
    def purple(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO: ...


class PrintLayouts(Protocol):
    @property
    def lines(self) -> LinePrinting: ...
    @property
    def box(self) -> BoxPrinting: ...
    @property
    def table(self) -> TableDelivering: ...
    @property
    def header(self) -> HeaderPrinting: ...
    @property
    def dip(self) -> DipPrinting: ...

    def panel(
        self, *content: dto.CliSpec, **kw: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO:
        """Render Panel with full configuration."""

    def md(
        self, content: _Stringable, /, **kw: Unpack[dto.MarkdownInput]
    ) -> dto.MarkdownDTO:
        """Render Markdown."""

    def title(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.HeaderPresetInput],
    ) -> dto.PanelDTO:
        """Single Slim Panel with Semantic Coloring"""

    def success(
        self, title: str, *content: dto.CliSpec, **kw: Unpack[dto.StatusInput]
    ) -> dto.PanelDTO: ...

    def warn(
        self, title: str, *content: dto.CliSpec, **kw: Unpack[dto.StatusInput]
    ) -> dto.PanelDTO: ...

    def danger(
        self, title: str, *content: dto.CliSpec, **kw: Unpack[dto.StatusInput]
    ) -> dto.PanelDTO: ...

    def special(
        self, title: str, *content: dto.CliSpec, **kw: Unpack[dto.StatusInput]
    ) -> dto.PanelDTO: ...


class Print(PrintLayouts, PrintBase, Protocol):
    """Define Minimal functionality for Optimal Workflow"""

    @property
    def dto(self) -> EventDtoFactory:
        """DtoFactory with Producer for all DTOs"""

    @property
    def render(self) -> Callable[[EventDTO], Any]:
        """DtoRenderHub with Visualizer for all DTOs"""


# LATER:
class TuiPrinter(Print):
    """Future Development..."""


class Printing(Protocol):
    """Define the Printers Print"""

    def __call__(  # LATER: work out, together with Inputs and Specs
        self, target: Any, /, *more: Any, **spec: Unpack[PrintInput]
    ) -> Any: ...


# LATER:
class StdPrintInput(TypedDict, total=False):
    sep: str
    end: str


# LATER:
class SstPrintInput(TypedDict, total=False):
    content: str
    color: ColorId


# LATER:
class PrintInput(StdPrintInput, SstPrintInput):
    """Define the Input Space of the Printers Print"""


# LATER:
class TemplatePrint(Protocol):  # TASK: TemplateEngine!
    def __call__(self, target: Template, /, **kwargs) -> CliDTO: ...
