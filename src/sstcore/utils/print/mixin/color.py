from functools import singledispatchmethod

from ....exceptions import NotImplementedDispatchError
from ..base import BasePrinter
from ..stylebox import Attribute, ColorBox


class ColorMixin(BasePrinter):
    """Encapsulate core layout building design blocks"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color_box = ColorBox()

    def panel(self, target, **kwargs):
        self._debug_log_if_active(target, **kwargs)
        text_style: str = kwargs.pop("text_style", "")
        title: str = kwargs.pop("title", "")  # MOVE:
        super().panel(  # TODO: dispatch kwargs
            self._colorize(target, text_style=text_style, **kwargs),
            title=self._colorize(title, "white"),  # MOVE:
            **kwargs,
        )

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### Colorizing  strings
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    # TASK: Fix pipeline trough Format
    @singledispatchmethod
    def _colorize[T: str | list](self, text: T, **kwargs) -> T:
        raise NotImplementedDispatchError(text, kwargs=kwargs)

    @_colorize.register
    def _[T: str](self, target: str, style: str = "", **kwargs) -> str:
        style: str = style or kwargs.get("text_style", "white")
        text: str = self._format(target)
        return self._color_box._colorize(text, color=str(style))

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
    ### Prints
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
