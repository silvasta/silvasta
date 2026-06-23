from functools import singledispatchmethod
from pathlib import Path

from rich.box import Box
from rich.rule import Rule

from ....exceptions import NotImplementedDispatchError
from ...log.inspect import debug_log_or_print
from ...paint.stylebox import Attribute, ColorBox
from ..base import BasePrinter


class ColorMixin(BasePrinter):
    """Encapsulate core layout building design blocks"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color_box = ColorBox()

    @debug_log_or_print(anyway=False)
    def panel(self, target, **kwargs):
        text_style: str = kwargs.pop("text_style", "")
        title: str = kwargs.pop("title", "")  # MOVE:
        super().panel(  # TODO: dispatch kwargs
            self._colorize(target, text_style=text_style, **kwargs),
            title=self._colorize(title, "white"),  # MOVE:
            **kwargs,
        )

    LINE_COLOR = "cyan"  # MOVE: later to colorbox

    # -- Box Layout Definitions --
    # Inline comments prevent Ruff/Black from collapsing the strings into one line

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
    BOX_FULL = Box(
        ""
        "────\n"  # 1. Top border
        "│ ││\n"  # 2. Header walls
        "│ ││\n"  # 3. Header divider
        "│ ││\n"  # 4. Body walls
        "│ ││\n"  # 5. Body row divide
        "│ ││\n"  # 6. Footer divider
        "│ ││\n"  # 7. Footer walls
        "╰─╯┴\n"  # 8. Bottom border
    )
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def line(self, style: str = ""):
        """Print a full-width horizontal rule"""
        target_style = style or self.LINE_COLOR
        self(Rule(style=target_style))

    def paths(self, paths: list[Path], frame: str = "cyan"):
        """Print a list of paths within an open box"""
        self.box(self._format(paths), frame=frame)

    def box_top(self, target, frame=""):
        return self.box(target, frame, box=self.BOX_TOP)

    def box_bottom(self, target, frame=""):
        return self.box(target, frame, box=self.BOX_BOTTOM)

    def box(self, target, frame: str = "", box: Box | None = None):
        """Print target inside a customizable layout box (defaults to OPEN_BOX)"""
        self.panel(
            target=target,
            box=box or self.BOX_OPEN,
            border_style=frame or self.LINE_COLOR,
            expand=True,
        )

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### Colorizing  strings
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    # TASK: Fix pipeline trough Format
    @singledispatchmethod
    def _colorize[T: str | list](self, text: T, **kwargs) -> T:
        self(exc := NotImplementedDispatchError(text, kwargs=kwargs))
        self._raise_or_not(exc)
        return text

    @_colorize.register
    def _[T: str](self, target: str, style: str = "", **kwargs) -> str:
        style: str = style or kwargs.get("text_style", "white")
        if text := self._format(target):
            return self._color_box._colorize(text, color=str(style))
        return ""  # TEST: avoid stuff like: kwargs={'title': '[white][/]',...}

    @_colorize.register
    def _[T: list[str]](self, target: list, style: str, **kwargs) -> list[str]:
        style: str = style or kwargs.get("text_style", "white")
        return [self._colorize(i, style) for i in target] or []

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### Box
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    @property
    def colors(self) -> ColorBox:
        """Provide reference to attached ColoBox"""
        return self._color_box

    def colorbox(self, mode: Attribute = "normal") -> ColorBox:
        """Export new ColorBox with desired attribute"""
        return ColorBox.with_mode(attribute=mode)

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### Print in the named color or alias
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def white(self, target) -> None:
        text: str = self._format(target)
        self(self.colors.white(text))

    def blue(self, target) -> None:
        text: str = self._format(target)
        self(self.colors.blue(text))

    def red(self, target) -> None:
        text: str = self._format(target)
        self(self.colors.red(text))

    def r(self, target) -> None:
        text: str = self._format(target)
        self(self.colors.red(text))

    def green(self, target) -> None:
        text: str = self._format(target)
        self(self.colors.green(text))

    def g(self, target) -> None:
        text: str = self._format(target)
        self(self.colors.green(text))

    def cyan(self, target) -> None:
        text: str = self._format(target)
        self(self.colors.cyan(text))

    def c(self, target) -> None:
        text: str = self._format(target)
        self(self.colors.cyan(text))

    def magenta(self, target) -> None:
        text: str = self._format(target)
        self(self.colors.magenta(text))

    def yellow(self, target) -> None:
        text: str = self._format(target)
        self(self.colors.yellow(text))

    def black(self, target) -> None:
        text: str = self._format(target)
        self(self.colors.black(text))
