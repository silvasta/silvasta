"""
Final TODOs

- Save the remaing highly usable settings for access and application

"""

from typing import Any, Literal

from rich.box import Box

from ._boxes import Boxes


class LineMixin:
    def line(self, style: str = ""):
        """TODO: include in lines but very simple, or just reuse"""

    def lines(self, lines: list, style="cyan", title=None, header=None):
        """TODO: check if everything collected"""

        if header and (role := getattr(self._cb.palette, style, None)):
            invert: str = role.inverted if hasattr(role, "inverted") else style
            self.header(text=header, frame=invert, title=title)

        self.panel(lines, title=title, frame=style, title_align="right")

    def lines_with_len(self, name, lines: list, style: str = "cyan"):
        """TODO: make exactly this with dot-access on functor: lines.len(...)"""
        header = f"{name}: {len(lines)}"
        self.lines(header=header, title=name, lines=lines, style=style)


class BoxMixin:
    def box(self, target, frame: str, box: Box):
        """Print Target inside Custom Layout Box"""
        self.panel(target=target, box=box, border_style=frame or "cyan")

    def box_top(self, target, frame=""):
        """LATER: make with dot-access, wait fro __getattr__ stack"""
        return self.box(target, frame, box=Boxes.UP.option())

    def box_bottom(self, target, frame=""):
        """LATER: make with dot-access, wait fro __getattr__ stack"""
        return self.box(target, frame, box=Boxes.DOWN.option())

    def mini_box(
        self,
        target,
        frame="",
        mode: Literal["up", "down", "both"] = "both",
    ):
        """LATER: make with (double?) dot-access, wait fro __getattr__ stack"""
        match mode:
            case "up":
                box: Box = Boxes.MINI_UP.option()
            case "down":
                box: Box = Boxes.MINI_DOWN.option()
            case "both":
                box: Box = Boxes.MINI.option()
        return self.box(target, frame, box)


class HeaderMixin:
    def header(self, text: Any, frame: str = "cyan", **kwargs) -> None:
        """TODO: Extract param"""
        text_style: str = kwargs.pop("text_style", "bold white")
        self.panel(text, color=text_style, frame=frame, **kwargs)

    def dip(self, head, text, color):
        """IMPORTANT: create first color dispatched version now, later __getattr__"""
        self.header(f"{self.color(head, color)} {text}", frame=color)

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    # NEXT: exactly as simple as here (only 1, rest is generated)
    def success(self, text): ...
    def danger(self, text): ...
    def warn(self, text): ...
    def special(self, text):
        """Provide header for special action"""
        self.header(text, frame="purple")
