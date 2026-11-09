"""
View Assembly

- Don't use from ..view as Functor might export there

"""

__all__: list[str] = [
    "FunctorMetaInput",
    #
    # NEXT:
    # "BaseParamSpec",
    # "DataClassSpec",
    #
    "FunctorView",
]

from collections.abc import Callable
from typing import TypedDict

from sstcore.port.color import Color

from ...brick import reflect
from ...brick.color import colorize
from ...brick.color.box import Colors
from ...brick.format import norm
from ...port.functorial import Catch, ErrorPolicy
from ...port.represent import Richable
from ...port.structures import ParamSpec
from ..engine import FunctorMetaData

colors = Colors()

FunctorMetaInput = FunctorMetaData(color=Color.GREEN)


# AI: everything fine here with the implementations?


class FunctorInput[**A, R](TypedDict, total=False):
    call: Callable[A, R]
    name: str


class FunctorSpec[**A, R](ParamSpec):
    call: Callable[A, R] | None = None
    name: str = ""


class SafeFunctorInput[**A, R](FunctorInput, total=False):
    catch: Catch[A, R]
    policy: ErrorPolicy
    exit_code: int


class SafeFunctorSpec[**A, R](ParamSpec):
    catch: Catch[A, R] | None = None
    policy: ErrorPolicy | None = None
    exit_code: int | None = None


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class FunctorView:
    _data: FunctorMetaData

    def __str__(self) -> str:
        return f"[({reflect.clsname(self)})][{reflect.name(self)}]"

    def __repr__(self) -> str:
        return f"{self}({norm.dict_to_str(vars(self))})"

    #  LINE: -- Select, later on -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __rich__(self) -> str:
        return f"{reflect.clsname(self)}[{reflect.name(self)}]"

    def __rich1__(self) -> Richable:
        return colors(reflect.clsname(self), self._data.color)

    def __rich2__(self) -> Richable:
        return colorize.modules(self)
