"""
Compose RichMixins

- Atomize: 1 class with 1 method __rich__

"""

__all__: list[str] = [
    "SimpleRichNameMixin",
    "RichNameMixin",
    "RichModuleNameMixin",
]


from ...port.color import ColorBox
from ...port.view import Renderable
from ..color import colorize
from ..color.box import Colors
from ..labor import reflect

colors: ColorBox = Colors()


class SimpleRichNameMixin:
    """Show colorized class name"""

    def __rich__(self) -> Renderable:
        return colors(reflect.clsname(self), 3)


class RichNameMixin:
    """
    Show colorized class name and attribute value as below

    - _inside_brackets (priority 1, descending)
    - _name
    - name
    """

    def __rich__(self) -> str:
        return f"{reflect.clsname(self)}[{reflect.name(self)}]"


class RichModuleNameMixin:
    def __rich__(self) -> Renderable:
        """Show module path from project to class name"""
        # LATER: select colors by class attributes?
        return colorize.modules(self)
