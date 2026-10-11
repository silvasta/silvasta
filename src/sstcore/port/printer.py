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
from string.templatelib import Template
from typing import Any, Literal, TypedDict, Unpack
from typing import Protocol as Protocol

from .calling import Richable
from .color import Color, ColorBox, ColorId
from .config import ProjectInformation
from .event.dto import CliDTO  # 7
from .represent import CliRenderable  # 8
from .solid import EnumMode


class StdPrintInput(TypedDict, total=False):
    sep: str
    end: str


class SstPrintInput(TypedDict, total=False):
    color: ColorId


class PrintInput(StdPrintInput, SstPrintInput):
    """Define the Input Space of the Printers Print"""


x = PrintInput(color=Color.AZURE)


class Print(Protocol):
    """Define the Printers Print"""

    def __call__(
        self, target: Any, /, *more: Any, **spec: Unpack[PrintInput]
    ) -> Any: ...


# NEXT: TemplateEngine! Including Log/Cli,...?
class TemplatePrint(Protocol):
    def __call__(self, target: Template, /, **kwargs) -> CliDTO: ...


# NEXT: specify steps to mouth
class _PrintReadyForEngine(Protocol):
    """Define the Normalized Call to the Printer Engine"""

    def __call__(
        self,
        target: CliRenderable,
        /,
        *more: CliRenderable,
        **spec: Unpack[PrintInput],
    ) -> CliDTO: ...


class PrintMode(EnumMode):
    """
    Define the Execution Mode

    NEXT:
    NEXT:
    NEXT:
    - SPLIT??? Adapter and Mode?
      - e.g. rich as adapter maybe even as a mixin dependant setup
      - but DEBUG,PRINT and NULL always?
    """

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

    info: ProjectInformation

    @property
    def project_info(self) -> str:
        """Style the top right title of printer.title Panel"""

    mode: PrintMode = PrintMode.RICH_CONSOLE

    def muted(self) -> Any: ...
    def mute(self) -> None: ...
    def unmute(self) -> None: ...
    def debug(self) -> Any: ...
    def in_mode(self, modus: PrintMode): ...


# NEXT: resolve this below
class ColorPrint(Protocol):
    colors: ColorBox  # TODO: stack

    def colorize(self, text: str, color: ColorId | None) -> str: ...
    def normalize(self, target: Any, **kwargs) -> str: ...


# REMOVE:??
class CorePrint(Protocol):
    def render(self, target: CliDTO, **kwargs) -> Richable: ...
    def display(self, target: CliDTO, **kwargs) -> Richable: ...


# TASK: Stacking and attach?
class LayoutPrint(Protocol):
    def panel(self, target: Any, **kwargs) -> None: ...
    def line(self, style: str = "", title: str | None = None) -> None: ...
    def lines(
        self,
        # lines: list,
        # style: str = "cyan",
        # title: str | None = None,
        # header: str | None = None,
    ) -> None: ...
    def lines_with_len(
        # self, name: str, lines: list, style: str = "cyan"
    ) -> None: ...
    # box
    def box(
        self,
        target: Any,
        # frame: str = "",
        # box: Box = ...,
    ) -> None: ...
    # def box_top(self, target: Any, frame: str = "") -> None: ...
    # def box_bottom(self, target: Any, frame: str = "") -> None: ...
    def mini_box(
        self,
        target: Any,
        frame: str = "",
        mode: Literal["up", "down", "both"] = "both",
    ) -> None: ...
    def corner(
        self,
        target: Any,
        # frame: str = "",
        # box: Box = ...,
    ) -> None: ...
    def header(
        # self,
        # text: Any,
        # frame: str = "cyan",
        # **kwargs,
    ) -> None: ...
    def title(
        self,
        text: Any,
        # title: str = "",
        # title_align: AlignMethod = "right",
        **kwargs,
    ) -> None: ...
    # def success(self, text: Any) -> None: ...
    # def danger(self, text: Any) -> None: ...
    # def warn(self, text: Any) -> None: ...
    # def special(self, text: Any) -> None: ...
    def dip(self, head: str, text: str, color: str) -> None: ...

    def md(self, text: str, *args, header: int = 0, **kwargs) -> None: ...


# TODO: unwrap this functions, attach only function
class SpecialPrint(Protocol):
    def path_exists_table(
        # self, paths: list[Path], title=None, header="Path"
    ) -> None: ...
    def dict_table(
        self,
        # target: dict,
        # header="Dict Inspection",
        # show_type: bool | tuple[bool, bool] = (True, True),
        # style="green",
    ): ...
    def tree_graph(
        self,
        # simple_tree: SimpleTreeNode,
        # max_depth: int | None = None,
        # root: str = "bold magenta",
        # node: str = "by_level",
        # guide: str = "bold white",
        # hide_root=False,
    ) -> None: ...


class Printer(Protocol):
    """TEMP"""

    __call__: Print
    info: ProjectInformation

    # def set_info(self, info: ProjectInformation) -> None:
    #     """Attach Project specific information for Printer layouts"""
