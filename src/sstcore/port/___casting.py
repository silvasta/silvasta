"""
Define the Shape of the Arg Casting Pipeline

- Mount on functions and cast args

                             DependencyLevel.sstcore.port.empty[10] 🙂
"""

__all__: list[str] = [
    "ArgCasting0",
    "ArgCasting",
    "CastInput",
    # types
    "CastPlan",
    "TypeRegistry",
]

import typing as _t
from collections.abc import Callable
from pathlib import Path
from typing import Any, Concatenate, Literal, Protocol, overload
from typing import Protocol as _Protocol

from .color import Color
from .empty import VOID, May, MayBe, Maybe

type CastPlan = dict[str, ArgCasting]
type TypeRegistry[T: type] = dict[T, ArgCasting]


class CastInput[Some](_t.TypedDict, total=False):
    """Configuration flags for ArgCasting"""

    default: Some | VOID


@_t.runtime_checkable
class ArgCasting0(_Protocol):
    """Check if target can be used for ArgCast pipeline"""

    def __call__[Some](
        self, target, /, *, default: MayBe[Some] = VOID
    ) -> Some:
        """Cast, Coerce, Resolve and or Validate the Function Input"""


@_t.runtime_checkable
class _ArgCasting(_Protocol):
    """Check if target can be used for ArgCast pipeline"""

    def __call__[T](self, target, /, *, default: May[T] = VOID) -> T:
        """Cast, Coerce, Resolve and or Validate the Function Input"""


@_t.runtime_checkable
class ArgCasting[SuperSet: Any = Path, Result: Path = Path](_Protocol):
    """Check if target can be used for ArgCast pipeline"""

    def __call__(
        self, target: SuperSet, /, *, default: Maybe[Result] = VOID
    ) -> Result:
        """Cast, Coerce, Resolve and or Validate the Function Input"""


@_t.runtime_checkable
class _SuperArgCasting[Result = Any, Raw = Any](_Protocol):
    """Cast, Coerce, Resolve and/or Validate Function Input."""

    def __call__(
        self,
        target: Result | Raw,
        /,
        *,
        default: Maybe[Result] = VOID,
    ) -> Result: ...


type ColorName = Literal["azure", "teal", "carbon"]
type ColorArg = Color | ColorName | int | str


def castcolor[**P, R](
    func: Callable[Concatenate[Color, P], R],
) -> Callable[Concatenate[ColorArg, P], R]:
    def wrapper(
        color: ColorArg = Color.AZURE, *args: P.args, **kwargs: P.kwargs
    ) -> R:
        resolved: Color = Color.resolve(color)
        return func(resolved, *args, **kwargs)

    return wrapper


@castcolor
def my_colorizer(color: Color, target: str) -> str:
    pass


test = my_colorizer("teal", "mytext")


def castcolor1[**P, R](
    func: Callable[Concatenate[str, Color, P], R],
) -> Callable[Concatenate[str, ColorArg, P], R]:
    def wrapper(
        text: str,
        color: ColorArg = Color.AZURE,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        resolved: Color = Color.resolve(color)
        return func(text, resolved, *args, **kwargs)

    return wrapper


@castcolor1
def my_colorizer1(text: str, color: Color) -> str:
    return text


test1 = my_colorizer1("hello")


class _Colorized1[T1, R](Protocol):
    def __call__(self, target: T1, color: ColorArg = Color.AZURE) -> R: ...


class _ColorizedKw[**P, R](Protocol):
    def __call__(
        self, *args: P.args, color: ColorArg = Color.AZURE, **kwargs: P.kwargs
    ) -> R: ...


@overload
def castcolor2[T1, R](
    func: Callable[[T1, Color], R],
) -> _Colorized1[T1, R]: ...


@overload
def castcolor2[**P, R](func: Callable[P, R]) -> _ColorizedKw[P, R]: ...


def castcolor2(func: Callable[..., Any]) -> Callable[..., Any]:
    # Runtime inspection via inspect.signature to cast `color`
    ...
