"""
print

.
"""

__all__: list[str] = [
    "Print",
    "PrintMode",
    "PrintCore",
    # NEXT: Render? Normalize? Color?
    "PrintLayouts",
    "PrintTools",
]


from enum import Enum, auto
from string import Template
from typing import Any, Literal, Required, TypedDict, Unpack
from typing import Protocol as Protocol

from ..port.color import ColorBox, ColorIdentifier
from .config import ProjectInformation
from .event.dto import CliDTO
from .view import Renderable, RichRenderable


class PrintSpec(TypedDict, total=False):
    """Define the Input Space of the Printers Print"""

    # AI: this is like the base set for the kwargs
    color: str
    sep: str
    end: str


class Print(Protocol):
    """Define the Printers Print"""

    # AI: this is like the main gate, but there are many others
    def __call__(
        self, target: Any, /, *more: Any, **spec: Unpack[PrintSpec]
    ) -> CliDTO: ...


class _NewIntermediateTemplateProcess(Protocol):
    """Define the Printers Print"""

    # AI:
    def __call__(self, target: Template, /, **kwargs) -> Renderable: ...


class _PrintReadyForEngine(Protocol):
    """Define the Normalized Call to the Printer Engine"""

    # AI: this is what the printer engine throws into the adapter like rich.Console
    def __call__(
        self,
        target: Renderable,
        /,
        *more: Renderable,
        **spec: Unpack[PrintSpec],
    ) -> CliDTO: ...


class DontForget(TypedDict, total=False):  # REMOVE: when memorized
    maybe1: int
    maybe2: int
    needed: Required[int]


class PrintMode(Enum):
    """
    Define the Execution Mode

    - SPLIT??? Adapter and Mode?
      - e.g. rich as adapter maybe even as a mixin dependant setup
      - but DEBUG,PRINT and NULL always?
    """

    RCONSOLE = auto()
    RPRINT = auto()
    DEBUG = auto()
    PRINT = auto()
    NULL = auto()


class PrinterBase(Protocol):
    """Define the Base of the Printer"""

    def __call__(self, target: Any, **kwargs) -> CliDTO:
        """Print the target and return the manual"""

    info: ProjectInformation
    # @property
    # def info(self) -> ProjectInformation: ...

    @property
    def project_info(self) -> str:
        """Style the top right title of printer.title Panel"""

    modus: PrintMode = PrintMode.RCONSOLE

    def muted(self) -> Any: ...
    def mute(self) -> None: ...
    def unmute(self) -> None: ...
    def debug(self) -> Any: ...
    def in_modus(self, modus: PrintMode): ...


class ColorPrint(Protocol):
    colors: ColorBox  # TODO: stack

    def colorize(self, text: str, color: ColorIdentifier | None) -> str: ...
    def normalize(self, target: Any, **kwargs) -> str: ...


class CorePrint(Protocol):
    def render(self, target: CliDTO, **kwargs) -> RichRenderable: ...
    def display(self, target: CliDTO, **kwargs) -> RichRenderable: ...


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

    def set_info(self, info: ProjectInformation) -> None:
        """Attach Project specific information for Printer layouts"""
