from functools import singledispatchmethod

from sstcore.exceptions import NotImplementedDispatchError

from ..base import BasePrinter
from ..stylebox import Attribute, ColorBox


class ColorMixin(BasePrinter):
    """Encapsulate core layout building design blocks"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color_box = ColorBox()

    def panel(self, target, **kwargs):
        text_style: str = kwargs.pop("text_style", "")
        super().panel(
            self._colorize(target, text_style=text_style, **kwargs), **kwargs
        )

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- -
    ### Colorizing  strings
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- -

    @singledispatchmethod
    def _colorize[T: str | list](self, text: T, style: str, **kwargs) -> T:
        # TASK: check if try colorize instead of direct raise
        raise NotImplementedDispatchError(text, style, kwargs)

    @_colorize.register
    def _[T: str](self, text: str, style: str = "", **kwargs) -> str:
        style: str = style or kwargs.get("text_style", "white")
        return self._color_box._colorize(text, color=str(style))

    @_colorize.register
    def _[T: list[str]](self, text: list, style: str, **kwargs) -> list[str]:
        style: str = style or kwargs.get("text_style", "white")
        return [self._colorize(i, style) for i in text] or []

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- -
    ### Box
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- -

    @property
    def colors(self) -> ColorBox:
        """Provide reference to attached ColoBox"""
        return self._color_box

    def colorbox(self, mode: Attribute = "normal") -> ColorBox:
        """Export new ColorBox with desired attribute"""
        return ColorBox.with_mode(attribute=mode)

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- -
    ### Prints
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- -

    def white(self, text: str) -> None:
        self(self.colors.white(text))

    def blue(self, text: str) -> None:
        self(self.colors.blue(text))

    def red(self, text: str) -> None:
        self(self.colors.red(text))

    def green(self, text: str) -> None:
        self(self.colors.green(text))

    def cyan(self, text: str) -> None:
        self(self.colors.cyan(text))

    def magenta(self, text: str) -> None:
        self(self.colors.magenta(text))

    def yellow(self, text: str) -> None:
        self(self.colors.yellow(text))

    def black(self, text: str) -> None:
        self(self.colors.black(text))

    # def white(self, text: str) -> None:
    #     super().__call__(self.colors.white(text))
    #
    # def blue(self, text: str) -> None:
    #     super().__call__(self.colors.blue(text))
    #
    # def red(self, text: str) -> None:
    #     super().__call__(self.colors.red(text))
    #
    # def green(self, text: str) -> None:
    #     super().__call__(self.colors.green(text))
    #
    # def cyan(self, text: str) -> None:
    #     super().__call__(self.colors.cyan(text))
    #
    # def magenta(self, text: str) -> None:
    #     super().__call__(self.colors.magenta(text))
    #
    # def yellow(self, text: str) -> None:
    #     super().__call__(self.colors.yellow(text))
    #
    # def black(self, text: str) -> None:
    #     super().__call__(self.colors.black(text))
