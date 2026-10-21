"""
View Assembly

- Don't use from ..view as Functor might export there

"""

from ...brick import reflect
from ...brick.color import colorize
from ...brick.color.box import Colors
from ...brick.format import norm
from ...port.represent import Richable

colors = Colors()


class FunctorView:
    def __str__(self) -> str:
        return f"[({reflect.clsname(self)})][{reflect.name(self)}]"

    def __repr__(self) -> str:
        return f"{self}({norm.dict_to_str(vars(self))})"

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __rich__(self) -> str:
        return f"{reflect.clsname(self)}[{reflect.name(self)}]"

    def __rich1__(self) -> Richable:
        return colors(reflect.clsname(self), 3)

    def __rich2__(self) -> Richable:
        return colorize.modules(self)
