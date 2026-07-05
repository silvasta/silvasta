from typing import Any, Literal

from rich.box import Box
from rich.markdown import Markdown
from rich.rule import Rule

from ..base import BasePrinter
from ._boxes import BoxLibrary


class LayoutMixin(BasePrinter):
    """Provide Design Blocks for Core Layout"""

    _boxes = BoxLibrary()

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Latest Test of new Box layouts! (Promising!)
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def line(self, style: str = ""):
        """Print Horizontal Line"""
        self(Rule(style=style or "cyan"))

    # REFACTOR: keep nice boxes, reduce rest
    # IDEA: something like dot accessed boxes?
    # -> printer.box.full|top|dash... ?

    def box_full(self, target, frame=""):
        """Print Partial underlined Target and open a Scroll"""
        return self.box(target, frame, box=self._boxes.EDGE)

    def box_top(self, target, frame=""):
        """Print Overlined Target and open a Scroll"""
        return self.box(target, frame, box=self._boxes.UP)

    def box_bottom(self, target, frame=""):
        """Print Underlined Target and close a Scroll"""
        return self.box(target, frame, box=self._boxes.DOWN)

    def mini_box(
        self, target, frame="", mode: Literal["up", "down", "both"] = "both"
    ):
        match mode:  # MOVE: dispatch in BoxesBox, most likely by Enum
            case "up":
                box = self._boxes.MINI_UP
            case "down":
                box = self._boxes.MINI_DOWN
            case "both":
                box = self._boxes.MINI

        return self.box(target, frame, box=box)

    def box(self, target, frame: str = "", box: Box | None = None):
        """Print Target inside Custom Layout Box"""
        self.panel(
            target=target,
            box=box or self._boxes.OPEN,
            border_style=frame or "cyan",
            expand=True,
        )

    def dash(self, target, frame: str = "", box: Box | None = None):
        """Print Target inside Custom Layout Box"""
        self.panel(  # MERGE: after decision for boxes
            target=target,
            box=box or self._boxes.DASH,
            border_style=frame or "cyan",
            expand=True,
        )

    def edge(self, target, frame: str = "", box: Box | None = None):
        """Print Target inside Custom Layout Box"""
        self.panel(  # MERGE: after decision for boxes
            target=target,
            box=box or self._boxes.EDGE,
            border_style=frame or "cyan",
            expand=True,
        )

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### Layouts
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def md(self, text, *args, header: int = 0, **kwargs):
        """Render Markdown in Terminal, optional with desired Header-Level"""

        kwargs.setdefault("style", "white")  # LATER: default from ... ?

        if not (0 <= header <= 6):
            warn = (f"Markdown {header=} invalid! (H1 to H6) using default=0",)
            self.danger(warn)
            header = 0

        prefix: str = f"{'#' * header} " if header > 0 else ""

        self(Markdown(f"{prefix}{text}"), *args, **kwargs)

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def header(
        self, text, text_style: str = "bold white", frame="cyan", **kwargs
    ):
        """Provide simple access to title bar"""
        # NOTE: the white text_style inside colored frame looks amazing
        self.panel(text, text_style=text_style, frame=frame, **kwargs)

    def dip(self, head, text, color):
        """Colorize first expressions same as Frame"""
        # IDEA: extract pattern below and use as template for other layouts
        # - instead of 5 other dips, create easy arg access down to panel
        self.header(f"{self.color(head, color)} {text}", frame=color)

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def title(self, text, title="", title_align="right", **kwargs):
        """Provide default Frame with Title"""

        # LATER: check as well the title.inverted, how to provide arg for that?
        frame: str | None = kwargs.pop("frame", "cyan")

        title: str = title or self.name_and_version
        self.header(
            text, title=title, title_align=title_align, frame=frame, **kwargs
        )

    # LATER: connect named colors with header and default palette

    def success(self, text):
        """Provide header for default action"""
        self.header(text, frame="green")

    def danger(self, text):
        """Provide header for default action"""
        self.header(text, frame="red")

    def warn(self, text):
        """Provide header for default action"""
        self.header(text, frame="yellow")

    def special(self, text):
        """Provide header for special action"""
        self.header(text, frame="purple")

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def lines(
        self, lines: list, style="cyan", title=None, header=None
    ):  # LATER: default from ... ?
        """Provide Lines optional with inverted style header"""

        # LATER: check for better access to ColorBox.palette themes

        if header and (role := getattr(self._cb.palette, style, None)):
            invert: str = role.inverted if hasattr(role, "inverted") else style
            self.header(text=header, frame=invert, title=title)

        self.panel(lines, title=title, frame=style, title_align="right")

    def lines_with_len(
        self, name, lines: list, style: str = "cyan"
    ):  # LATER: default from ... ?
        """Provide Lines with Statistic"""
        header = f"{name}: {len(lines)}"
        self.lines(header=header, title=name, lines=lines, style=style)

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def banner(
        self, target: Any | list[Any], style="cyan", padding=(1, 1), **kwargs
    ):
        """Provide fat block that is hard to miss in CLI"""
        self.panel(
            target,
            border_style=f"white on {style}",
            style=style,
            padding=padding,
            **kwargs,
        )
