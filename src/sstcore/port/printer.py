"""
print

                                    DependencyLevel.sstcore.port[9]
"""

__all__: list[str] = [
    "Print",
    "PrintMode",
    # "PrintCore",
    # # NEXT: Render? Normalize? Color?
    # "PrintLayouts",
    # "PrintTools",
]


# TASK: finish printer

from enum import auto
from pathlib import Path
from string.templatelib import Template
from typing import Any, TypedDict, Unpack
from typing import Protocol as Protocol

from rich.box import Box

from .color import ColorBox, ColorId
from .config import ProjectInformation
from .event.dto import CliDTO, LineDTO, MarkdownDTO, PanelDTO
from .represent import CliRenderable, Richable
from .solid import EnumMode
from .tree import SimpleTree


class StdPrintInput(TypedDict, total=False):
    sep: str
    end: str


class SstPrintInput(TypedDict, total=False):
    content: str
    color: ColorId


class PrintInput(StdPrintInput, SstPrintInput):
    """Define the Input Space of the Printers Print"""


class Print(Protocol):
    """Define the Printers Print"""

    def __call__(
        self, target: Any, /, *more: Any, **spec: Unpack[PrintInput]
    ) -> Any: ...


class TemplatePrint(Protocol):
    # TASK: TemplateEngine! Including Log/Cli,...?
    def __call__(self, target: Template, /, **kwargs) -> CliDTO: ...


class PrintMode(EnumMode):  # NEXT: - SPLIT??? Adapter and Mode?
    """Define the Execution Mode"""

    RICH_CONSOLE = auto()
    RICH_PRINT = auto()
    DEBUG = auto()
    PRINT = auto()
    NULL = auto()

    @classmethod
    def default(cls) -> PrintMode:  # LATER: this on BaseEnum??
        return cls.RICH_CONSOLE


class PrinterBase(Protocol):
    """Define the Base of the Printer"""

    def __call__(self, target: Any, **kwargs) -> Any:
        """Print the target and return the manual"""

    colors: ColorBox  # TODO: stack
    info: ProjectInformation

    @property  # TODO: __str__==info.plain, otherwise __rich__
    def project_info(self) -> str:
        """Style the top right title of printer.title Panel"""

    mode: PrintMode = PrintMode.RICH_CONSOLE

    def muted(self) -> Any: ...
    def mute(self) -> None: ...
    def unmute(self) -> None: ...
    def debug(self) -> Any: ...
    def in_mode(self, modus: PrintMode): ...


class PrintNormalizer(Protocol):
    def normalize(self, target: Any, **kwargs) -> str:
        """Ensure Input is useable to build DTOs"""


class PrintFactory(Protocol):
    def produce(self, target: Any, **kwargs) -> CliDTO:
        """Transform Input into CliDTOs"""


class PrintRender(Protocol):
    def render(self, target: CliDTO, **kwargs) -> CliRenderable:
        """Transform CliDTOs into Renderables"""


class PrintRichRender(Protocol):
    def render(self, target: CliDTO, **kwargs) -> Richable:
        """Transform CliDTOs into Rich Renderables"""


class TitleInput(TypedDict, total=False):
    title: str | None
    text_color: ColorId
    title_color: ColorId
    # title_align: _AlignMethod


class HeaderInput(TitleInput, total=False):
    color: ColorId  # frame


class PanelInput(HeaderInput, total=False):
    header: str | None


class LayoutPrint(Protocol):
    def line(self, **kwargs: Unpack[SstPrintInput]) -> CliDTO:
        """Render Single Line with or without Content"""

    # IDEA: lines as *line?
    def lines(self, lines: list, **kwargs: Unpack[PanelInput]) -> LineDTO:
        """Render Multiple Lines from Iterable"""

    def lines_with_len(  # IDEA: this as additional hit
        self, lines: list, name: str, **kwargs: Unpack[PanelInput]
    ) -> None:
        """Simple Helper - Check usage! still useful?"""

    def panel(self, content: Any, **kwargs) -> CliDTO:
        """Render Multiple Lines from Iterable"""

    def box(self, content: Any, frame: str = "", box: Box = ...) -> PanelDTO:
        """Check Difference to Panel"""

    # TODO:
    # def box_top(self, target: Any, frame: str = "") -> None: ...
    # def box_bottom(self, target: Any, frame: str = "") -> None: ...
    # TODO: box.top
    # TODO: box.bottom
    # TODO: box.mini
    # TODO: box.mini.up
    # TODO: box.mini.down
    # TODO: box.mini.both
    # TODO: box.corner
    # def mini_box( self, target: Any, frame: str = "",
    #     mode: Literal["up", "down", "both"] = "both",) -> None: ...
    # def corner( self, target: Any, # frame: str = "", # box: Box = ...,) -> None: ...

    def header(self, content: Any, **kwargs: Unpack[HeaderInput]) -> PanelDTO:
        """Define Single Slim Panel"""

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

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

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def dip(self, head: str, text: str, color: str) -> PanelDTO:
        """Special Title with Nose of Text in Frame Color"""

    def md(self, text: str, *args, header: int = 0, **kwargs) -> MarkdownDTO:
        """Render Markdown"""


type TableInput = dict | list[list] | list[dict]  # NEXT: finish this!


# TODO: unwrap this functions, attach only function
class SpecialPrint(Protocol):
    def path_exists_table(  # IDEA: PathDTO? definitely multiple path prints!
        self, paths: list[Path], **kwargs: Unpack[PanelInput]
    ) -> PanelDTO:
        """Render Path overview with information about Existence"""

    def debug_table(
        self,
        target: TableInput,
        header="Dict Inspection",
        show_type: bool | tuple[bool, bool] = (True, True),
        style="green",
    ):
        """Print colored Dict with Type Information of Key and Value"""

    def tree(  # IDEA: TreeDTO? or just SimpleTree(Node)?
        self,
        tree: SimpleTree,
        max_depth: int | None = None,
        root: str = "bold magenta",
        node: str = "by_level",
        guide: str = "bold white",
        hide_root=False,
    ) -> None:
        """Visual Representation of the SimpleTreeNode"""


class BasePrinter(PrintRender, PrintFactory, PrintNormalizer, PrinterBase):
    """Define Minimal functionality to Operate"""


class RichPrinter(PrintRichRender, BasePrinter):
    """Define Minimal functionality to handle Rich"""


class Printer(LayoutPrint, RichPrinter):
    """Define Minimal functionality for Optimal Workflow"""


class DataPrinter(SpecialPrint, Printer):
    """Define Minimal functionality for Optimal Workflow"""


class TuiPrinter(Printer):
    """Future Development..."""
