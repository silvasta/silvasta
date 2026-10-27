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
from .event.factory import EventDtoFactory
from .solid import EnumMode

# AI: ignore everything marked with # LATER: ...


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


# TODO: resolve
class TitleInput(TypedDict, total=False):
    title: str | None
    text_color: ColorId
    title_color: ColorId


# TODO: resolve
class HeaderInput(TitleInput, total=False):
    color: ColorId


# TODO: resolve
class PanelInput(HeaderInput, total=False):
    header: str | None


# AI: this must show the most important methods and inputs
class PrintLayouts(Protocol):
    def lines(self, *lines, **kwargs: Unpack[PanelInput]) -> LineDTO:
        """Render Single, Zero or Multiple Lines from Iterable"""

    def md(self, text: str, *args, header: int = 0, **kwargs) -> MarkdownDTO:
        """Render Markdown"""

    def panel(self, content: Any, **kwargs) -> PanelDTO:
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


# IMPORTANT: this must hold, used in System and many other annotations for printer
class Print(PrintLayouts, PrintBase):
    """Define Minimal functionality for Optimal Workflow"""

    dto: EventDtoFactory
    render: EventDtoFactory


# LATER:
class TuiPrinter(Print):
    """Future Development..."""
