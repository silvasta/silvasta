"""
Compose RichMixins

- Atomize: 1 class with 1 method __rich__

"""

from typing import Any

from ...color import ColorBox, colorize

c: ColorBox = ColorBox.bold()


class SimpleRichNameMixin:  # TODO: synchronize with str, use StyledName
    def __rich__(self) -> str:
        # IDEA: maybe getattr _name_color with some default
        return c.cyan(type(self).__name__)


class ModuleNameMixin:
    def __rich__(self) -> Any:  # TODO: synchronize with str
        """Show location of module and name of class"""
        return colorize.modules(self)
