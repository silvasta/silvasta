"""
Compose RichMixins

- Atomize: 1 class with 1 method __rich__

"""

__all__: list[str] = [
    "SimpleRichNameMixin",
    "RichNameMixin",
    "RichModuleNameMixin",
]

from typing import Any

from ....format.color import ColorBox, colorize
from ....format.reflect import cls_name, name

c: ColorBox = ColorBox.bold()


class SimpleRichNameMixin:
    """Show colorized class name"""

    def __rich__(self) -> str:
        return c.cyan(cls_name(self))  # NEXT: color not hardcoded!!


class RichNameMixin:
    """
    Show colorized class name and attribute value as below

    - _inside_brackets (priority 1, descending)
    - _name
    - name
    """

    def __rich__(self) -> str:
        return f"{cls_name(self)}[{name(self)}]"  # NEXT: color MISSING!!


class RichModuleNameMixin:
    def __rich__(self) -> Any:
        """Show module path from project to class name"""
        # LATER: select colors by class attributes?
        return colorize.modules(self)
