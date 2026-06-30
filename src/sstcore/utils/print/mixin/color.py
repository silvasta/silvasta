from ...color import ColorBox
from ..base import BasePrinter


class ColorMixin(BasePrinter):
    """Encapsulate core layout building design blocks"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color_box = ColorBox()

    @property
    def name_and_version(self) -> str:
        name = self._cb.cyan(self.project_name)
        return f"{name} v{self.project_version}"

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### Colorizing  strings
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def color(self, text: str, color: str) -> str:
        return self._color_box(text, color) if text else ""

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### Box
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    @property
    def color_box(self) -> ColorBox:
        """Provide access to attached ColorBox"""
        return self._color_box

    @property
    def _cb(self) -> ColorBox:
        """Provide Short access to attached ColorBox"""
        return self._color_box

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### Print with named color
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def white(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self._color_box.white(text))

    def blue(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self._color_box.blue(text))

    def red(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self._color_box.red(text))

    def green(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self._color_box.green(text))

    def cyan(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self._color_box.cyan(text))

    def magenta(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self._color_box.magenta(text))

    def yellow(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self._color_box.yellow(text))

    def black(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self._color_box.black(text))
