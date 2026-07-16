from typing import Any, Literal

from rich.box import Box
from rich.markdown import Markdown

from sstcore.contract.cli import LineDTO, PanelDTO, RuleDTO

from ..blueprint import Printer
from ..boxes import Boxes


class PanelMixin:
    def panel(self: Printer, target: Any, **kwargs) -> None:
        """Provide General Panel Interface by pushing a PanelDTO to the core."""

        self(PanelDTO.from_call(target=target, **kwargs))


class LineMixin(PanelMixin):
    def line(self: Printer, style: str = ""):
        """Print Horizontal Line"""
        dto = LineDTO.from_call(style=style or "cyan")
        self(dto)

    def lines(
        self: Printer, lines: list, style="cyan", title=None, header=None
    ):
        """Provide Lines optional with inverted style header"""

        # LATER: check for better access to ColorBox.palette themes

        if header and (role := getattr(self._cb.palette, style, None)):
            invert: str = role.inverted if hasattr(role, "inverted") else style
            self.header(text=header, frame=invert, title=title)

        self.panel(lines, title=title, frame=style, title_align="right")

    def lines_with_len(self: Printer, name, lines: list, style: str = "cyan"):
        """Provide Lines with Statistic"""
        header = f"{name}: {len(lines)}"
        self.lines(header=header, title=name, lines=lines, style=style)

    def rule(self: Printer, title: str = "", **kwargs):
        """Print a horizontal rule with optional title."""
        self(RuleDTO.from_call(title=title, **kwargs))


class BoxMixin(PanelMixin):
    def box(
        self: Printer, target, frame: str = "", box: Box = Boxes.OPEN.value
    ):
        """Print Target inside Custom Layout Box"""
        self.panel(target=target, box=box, border_style=frame or "cyan")

    def box_top(self: Printer, target, frame=""):
        """Print Overlined Target and open a Scroll"""
        return self.box(target, frame, box=Boxes.UP.value)

    def box_bottom(self: Printer, target, frame=""):
        """Print Underlined Target and close a Scroll"""
        return self.box(target, frame, box=Boxes.DOWN.value)

    def mini_box(
        self: Printer,
        target,
        frame="",
        mode: Literal["up", "down", "both"] = "both",
    ):
        match mode:  # MOVE: dispatch in BoxesBox, most likely by Enum
            case "up":
                box = Boxes.MINI_UP.value
            case "down":
                box = Boxes.MINI_DOWN.value
            case "both":
                box = Boxes.MINI.value

        return self.box(target, frame, box=box)

    def corner(
        self: Printer, target, frame: str = "", box: Box = Boxes.CORNER.value
    ):
        self.panel(target=target, box=box, border_style=frame or "cyan")


class HeaderMixin:
    def header(
        self: Printer, text: Any, frame: str = "cyan", **kwargs
    ) -> None:
        """Provide simple access to title bar via PanelDTO."""

        text_style: str = kwargs.pop("text_style", "bold white")

        self.panel(text, color=text_style, frame=frame, **kwargs)

    def title(self: Printer, text, title="", title_align="right", **kwargs):
        """Provide default Frame with Title"""

        frame: str = kwargs.pop("frame", "cyan")

        title: str = title or self.project_info
        self.header(
            text, title=title, title_align=title_align, frame=frame, **kwargs
        )

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    # LATER: connect named colors with header and default palette

    def success(self: Printer, text):
        """Provide header for default action"""
        self.header(text, frame="green")

    def danger(self: Printer, text):
        """Provide header for default action"""
        self.header(text, frame="red")

    def warn(self: Printer, text):
        """Provide header for default action"""
        self.header(text, frame="yellow")

    def special(self: Printer, text):
        """Provide header for special action"""
        self.header(text, frame="purple")

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def dip(self: Printer, head, text, color):
        """Colorize first expressions same as Frame"""
        self.header(f"{self.color(head, color)} {text}", frame=color)


class MarkdownMixin:
    def md(self: Printer, text, *args, header: int = 0, **kwargs):
        """Render Markdown in Terminal, optional with desired Header-Level"""

        prefix: str = f"{'#' * header} " if header > 0 else ""

        self(Markdown(f"{prefix}{text}"), *args, **kwargs)


class TableMixin:
    pass
