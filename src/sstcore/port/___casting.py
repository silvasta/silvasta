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
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    Literal,
    Protocol,
    reveal_type,
)
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


type ColorName = Literal["azure", "teal", "carbon"]  # EXTRACT: AUTO-COMPLETE
type ColorArg = Color | ColorName | int | str


def castcolor[**P, R](
    func: Callable[Concatenate[Color, P], R],  # EXTRACT: colorcast low
) -> Callable[Concatenate[ColorArg, P], R]:
    def wrapper(
        color: ColorArg = Color.AZURE, *args: P.args, **kwargs: P.kwargs
    ) -> R:
        resolved: Color = Color.resolve(color)
        return func(resolved, *args, **kwargs)

    return wrapper


if TYPE_CHECKING:
    from sstcore.brick.color.box import Colors


class ArgCastIntersecting[SuperSet, Result](Protocol):
    def __call__(
        self,
        target: SuperSet | Result,
        /,
        *,
        default: Maybe[Result] = VOID,
    ) -> SuperSet & Result: ...  # ty:ignore


colors = Colors()
type ColorArg = Color | str | int


def intersector(
    func: Callable[[str, Color], str],
) -> Callable[[str, Color], str] & Callable[[str, ColorArg], str]:
    def wrapper(
        text: str,
        color: ColorArg,
    ) -> str:
        reveal_type(color)
        resolved: Color = Color.resolve(color)
        reveal_type(resolved)
        return func(text, resolved)

    reveal_type(wrapper)
    return wrapper


@intersector
def color_intersect2(text: str, color: Color) -> str:
    return colors(text, color)


bla_purple = color_intersect2("hello", 5)
bla_green = color_intersect2("bye", "green")


def intersector_generic[F: Callable[[str, Color], str]](
    func: F,
) -> F & Callable[[str, ColorArg], str]:
    def wrapper(
        text: str,
        color: ColorArg,
    ) -> str:
        resolved: Color = Color.resolve(color)
        return func(text, resolved)

    reveal_type(wrapper)
    return wrapper  # ty:ignore
