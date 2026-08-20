"""
print

.
"""

from sstcore.port.color import ColorBox

__all__: list[str] = [
    "Print",
    "PrintMode",
    "PrintCore",
    # NEXT: Render? Normalize? Color?
    "PrintLayouts",
    "PrintTools",
]


from enum import Enum, auto
from typing import Any, Literal
from typing import Protocol as Protocol

from .config import ProjectInformation
from .event.dto import (
    CliDTO,
    LineDTO,
    LogDTO,
    MarkdownDTO,
    PanelDTO,
    RuleDTO,
    TableDTO,
)
from .view import RichRenderable


class PrintMode(Enum):
    RICH = auto()
    DEBUG = auto()
    NULL = auto()


class Print(Protocol):
    """Define the Base of the Printer"""

    def __call__(self, target: Any, **kwargs) -> CliDTO:
        """Print the target and return the manual"""

    @property
    def info(self) -> ProjectInformation: ...
    def project_info(self) -> str: ...
    def set_info(self, info: ProjectInformation) -> None:
        """Attach Project specific information for Printer layouts"""

    modus: PrintMode = PrintMode.RICH

    def muted(self) -> Any: ...
    def mute(self) -> None: ...
    def unmute(self) -> None: ...
    def debug(self) -> Any: ...
    def in_mode(self, modus: PrintMode): ...


class PrintCore(Protocol):
    color_box: ColorBox

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


class PrintLayouts(Protocol):
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


class PrintTools(Protocol):
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
