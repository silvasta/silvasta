"""
Compose RichMixins

- Atomize: 1 class with 1 method __rich__

"""

from sstcore.port.view import Renderable

__all__: list[str] = [
    "SimpleRichNameMixin",
    "RichNameMixin",
    "RichModuleNameMixin",
]


from ....brick.color import colorize
from ....brick.color.box import Colors
from ....brick.format import reflect
from ....port.color import ColorBox

colors: ColorBox = Colors()  # ty:ignore


class SimpleRichNameMixin:
    """Show colorized class name"""

    def __rich__(self) -> Renderable:
        return colors(reflect.cls_name(self), 3)  # NEXT: color not hardcoded!!


class RichNameMixin:
    """
    Show colorized class name and attribute value as below

    - _inside_brackets (priority 1, descending)
    - _name
    - name
    """

    def __rich__(self) -> str:
        return f"{reflect.cls_name(self)}[{reflect.name(self)}]"  # NEXT: color MISSING!!


class RichModuleNameMixin:
    def __rich__(self) -> Renderable:
        """Show module path from project to class name"""
        # LATER: select colors by class attributes?
        return colorize.modules(self)
