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


from enum import auto
from string.templatelib import Template
from typing import Any, TypedDict, Unpack
from typing import Protocol as Protocol

from rich.box import Box

from .color import ColorBox, ColorId
from .config import ProjectInformation
from .event.dto import CliDTO, LineDTO, MarkdownDTO, PanelDTO
from .solid import EnumMode


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


class PrintMode(EnumMode):
    """Define the Execution Mode"""

    RICH = auto()
    DEBUG = auto()
    PRINT = auto()
    NULL = auto()

    @classmethod
    def default(cls) -> PrintMode:  # LATER: this on BaseEnum?
        return cls.RICH


class Printing(Protocol):
    """Define the Printers Print"""

    def __call__(  # TODO: work out, together with Inputs and Specs
        self, target: Any, /, *more: Any, **spec: Unpack[PrintInput]
    ) -> Any: ...


class StdPrintInput(TypedDict, total=False):
    sep: str
    end: str


class SstPrintInput(TypedDict, total=False):
    content: str
    color: ColorId


class PrintInput(StdPrintInput, SstPrintInput):
    """Define the Input Space of the Printers Print"""


class TemplatePrint(Protocol):  # TASK: TemplateEngine!
    def __call__(self, target: Template, /, **kwargs) -> CliDTO: ...


class TitleInput(TypedDict, total=False):
    title: str | None
    text_color: ColorId
    title_color: ColorId


class HeaderInput(TitleInput, total=False):
    color: ColorId


class PanelInput(HeaderInput, total=False):
    header: str | None


class PrintLayouts(Protocol):
    def lines(self, *lines, **kwargs: Unpack[PanelInput]) -> LineDTO:
        """Render Single, Zero or Multiple Lines from Iterable"""

    # # NEXT: this as additional hit: lines.len(...) on functor
    # def lines_with_len(
    #     self, lines: list, name: str, **kwargs: Unpack[PanelInput]
    # ) -> None:
    #     """Simple Helper - Check usage! still useful?"""

    def md(self, text: str, *args, header: int = 0, **kwargs) -> MarkdownDTO:
        """Render Markdown"""

    def panel(self, content: Any, **kwargs) -> CliDTO:
        """Render Multiple Lines from Iterable"""

    def box(self, content: Any, frame: str = "", box: Box = ...) -> PanelDTO:
        """Check Difference to Panel"""

    def dip(self, head: str, text: str, color: str) -> PanelDTO:
        """Special Title with Nose of Text in Frame Color"""

    def header(self, content: Any, **kwargs: Unpack[HeaderInput]) -> PanelDTO:
        """Define Single Slim Panel"""

    #  LINE: -- Below with StackingCore? SemanticColorNames -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def title(self, text: Any, **kwargs: Unpack[TitleInput]) -> PanelDTO:
        """Single Slim Panel with Semantic Coloring"""

    def success(self, text: Any, **kwargs: Unpack[TitleInput]) -> PanelDTO:
        """Single Slim Panel with Semantic Coloring"""

    def danger(self, text: Any, **kwargs: Unpack[TitleInput]) -> PanelDTO:
        """Single Slim Panel with Semantic Coloring"""

    def warn(self, text: Any, **kwargs: Unpack[TitleInput]) -> PanelDTO:
        """Single Slim Panel with Semantic Coloring"""

    def special(self, text: Any, **kwargs: Unpack[TitleInput]) -> PanelDTO:
        """Single Slim Panel with Semantic Coloring"""


class Print(PrintLayouts, PrintBase):
    """Define Minimal functionality for Optimal Workflow"""


class TuiPrinter(Print):
    """Future Development..."""
