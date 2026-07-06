from ...color import ColorBox
from ..base import BasePrinter


class ColorMixin(BasePrinter):
    """Encapsulate core layout building design blocks"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # LATER: this in protocoll, avaliable for other mixins
        self.color_box = ColorBox()

    @property
    def name_and_version(self) -> str:
        """Style the top right title of printer.title Panel"""
        name: str = self._cb.cyan(self.project_name)
        # LATER: MAYBE this in protocoll, avaliable for other mixins
        return f"{name} v{self.project_version}"

    @property
    def _cb(self) -> ColorBox:
        """Provide Short access to attached ColorBox"""
        # LATER: FOR SURE this in protocol, used mostly internally
        return self.color_box

    def color(self, text: str, color: str | None = None) -> str:
        """Apply color and in ColorBox predefined style attribute (bold,...)"""
        # LATER: this in protocoll, if deleting in base
        return self.color_box(text, color) if text else ""

    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --
    ### Print with named color
    ### -- -- -  -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def white(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self.color_box.white(text))

    def blue(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self.color_box.blue(text))

    def red(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self.color_box.red(text))

    def green(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self.color_box.green(text))

    def cyan(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self.color_box.cyan(text))

    def magenta(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self.color_box.magenta(text))

    def yellow(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self.color_box.yellow(text))

    def black(self, target) -> None:
        """Apply Color to text and just print"""
        text: str = self.format(target)
        self(self.color_box.black(text))
