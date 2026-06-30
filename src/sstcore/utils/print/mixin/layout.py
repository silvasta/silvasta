from typing import Any, Literal

from rich.box import Box
from rich.markdown import Markdown
from rich.rule import Rule

from ..base import BasePrinter


class LayoutMixin(BasePrinter):
    """Provide Design Blocks for Core Layout"""

    def md(self, text, *args, header: int = 0, **kwargs):
        """Render Markdown in Terminal, optional with desired Header-Level"""
        kwargs.setdefault("style", "info")

        if not (0 <= header <= 6):  # Generate Header if argument is set
            fallback_header = 0
            self(
                f"Markdown Header {header=} invalid (H1 to H6),"
                " using {fallback_header=}",
                style="danger",
            )
            header: int = fallback_header
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
        # TASK: refactor this, use template but inside other apps
        self.header(f"{self._prepare(head, color)} {text}", frame=color)

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def title(self, text, title="", title_align="right", **kwargs):
        """Provide default Frame with Title"""
        title: str = title or self.name_and_version
        self.header(text, title=title, title_align=title_align, **kwargs)

    def success(self, text):
        """Provide header for default action"""
        self.header(text, frame="green")  # LATER: check default apply

    def danger(self, text):
        """Provide header for default action"""
        self.header(text, frame="red")  # LATER: check default apply

    def warn(self, text):
        """Provide header for default action"""
        self.header(text, frame="yellow")  # LATER: check default apply

    def special(self, text):
        """Provide header for special action"""
        self.header(text, frame="purple")  # LATER: check default apply

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def lines(self, lines: list, style="title", title=None, header=None):
        """Provide Lines optional with header in inverted style"""
        if header and (role := getattr(self._cb._palette, style, None)):  # ty:ignore
            invert: str = role.inverted if hasattr(role, "inverted") else style
            self.header(text=header, frame=invert, title=title)
        self.panel(lines, title=title, frame=style, title_align="right")

    def lines_with_len(self, name, lines: list, style: str = "title"):
        """Provide Lines with Statistics"""
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

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Latest Test of new Box layouts! (Promising!)
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def line(self, style: str = ""):
        """Print Horizontal Line"""
        self(Rule(style=style or "cyan"))

    def box_mini(
        self, target, frame="", mode: Literal["up", "down", "all"] = "all"
    ):
        """Print Partial underlined Target and open a Scroll"""
        match mode:
            case "up":
                box = self.BOX_MINI_UP
            case "down":
                box = self.BOX_MINI_DOWN
            case "all":
                box = self.BOX_MINI

        return self.box(target, frame, box=box)

    def box_full(self, target, frame=""):
        """Print Partial underlined Target and open a Scroll"""
        return self.box(target, frame, box=self.BOX_FULL)

    def box_top(self, target, frame=""):
        """Print Overlined Target and open a Scroll"""
        return self.box(target, frame, box=self.BOX_TOP)

    def box_bottom(self, target, frame=""):
        """Print Underlined Target and close a Scroll"""
        return self.box(target, frame, box=self.BOX_BOTTOM)

    def box(self, target, frame: str = "", box: Box | None = None):
        """Print Target inside  Custom Layout Box"""
        self.panel(
            target=target,
            box=box or self.BOX_OPEN,
            border_style=frame or "cyan",
            expand=True,
        )

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    # -- Box Layout Definitions --
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    BOX_TOP = Box(
        ""
        "────\n"  # 1. Top border
        "    \n"  # 2. Header walls
        "    \n"  # 3. Header divider
        "    \n"  # 4. Body walls
        "    \n"  # 5. Body row divider
        "    \n"  # 6. Footer divider
        "    \n"  # 7. Footer walls
        "    \n"  # 8. Bottom border
    )

    BOX_BOTTOM = Box(
        ""
        "    \n"  # 1. Top border
        "    \n"  # 2. Header walls
        "    \n"  # 3. Header divider
        "    \n"  # 4. Body walls
        "    \n"  # 5. Body row divider
        "    \n"  # 6. Footer divider
        "    \n"  # 7. Footer walls
        "────\n"  # 8. Bottom border
    )

    BOX_OPEN = Box(
        ""
        "────\n"  # 1. Top border
        "    \n"  # 2. Header walls
        "    \n"  # 3. Header divider
        "    \n"  # 4. Body walls
        "    \n"  # 5. Body row divider
        "    \n"  # 6. Footer divider
        "    \n"  # 7. Footer walls
        "────\n"  # 8. Bottom border
    )
    BOX_FULL = Box(  # TODO: copy, rename fix
        ""
        "╋╸╸╋\n"  # 1. Top border
        "╹  ╹\n"  # 2. Header walls
        "╹  ╹\n"  # 3. Header divider
        "╹  ╹\n"  # 4. Body walls
        "╹  ╹\n"  # 5. Body row divide
        "╹  ╹\n"  # 6. Footer divider
        "╹  ╹\n"  # 7. Footer walls
        "╋╸╸╋\n"  # 8. Bottom border
    )

    BOX_MINI_UP = Box(
        ""
        " ─  \n"  # 1. Top border
        "    \n"  # 2. Header walls
        "    \n"  # 3. Header divider
        "    \n"  # 4. Body walls
        "    \n"  # 5. Body row divide
        "    \n"  # 6. Footer divider
        "    \n"  # 7. Footer walls
        "    \n"  # 8. Bottom border
    )
    BOX_MINI = Box(
        ""
        " ─  \n"  # 1. Top border
        "    \n"  # 2. Header walls
        "    \n"  # 3. Header divider
        "    \n"  # 4. Body walls
        "    \n"  # 5. Body row divide
        "    \n"  # 6. Footer divider
        "    \n"  # 7. Footer walls
        " ─  \n"  # 8. Bottom border
    )
    BOX_MINI_DOWN = Box(
        ""
        "    \n"  # 1. Top border
        "    \n"  # 2. Header walls
        "    \n"  # 3. Header divider
        "    \n"  # 4. Body walls
        "    \n"  # 5. Body row divide
        "    \n"  # 6. Footer divider
        "    \n"  # 7. Footer walls
        " ─  \n"  # 8. Bottom border
    )
