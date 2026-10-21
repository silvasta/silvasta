"""
Define the Shape of the Arg Casting Pipeline

- Mount on functions and cast args

                             DependencyLevel.sstcore.port.empty[10] 🙂
"""

__all__: list[str] = [
    # "",
]

from collections.abc import Callable
from typing import Any, Concatenate, Literal, Protocol, reveal_type

from rich import print

from sstcore.brick.color.box import Colors
from sstcore.port.color import Color, Painter
from sstcore.port.empty import VOID, Maybe

#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

colors = Colors()
type ColorArg = Color | str | int


type ColorName = Literal["azure", "teal", "carbon"]  # EXTRACT: AUTO-COMPLETE
type ColorArg = Color | ColorName | int | str


def castcolor1[**P, R](
    func: Callable[Concatenate[str, Color, P], R],  # EXTRACT: colorcast medium
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
    return colors(text, color)


test1 = my_colorizer1("hello", "azure")

print(test1)


class _Colorized1[T1, R](Protocol):
    def __call__(self, target: T1, color: ColorArg = Color.AZURE) -> R: ...


def castcolor2(_func: Callable[..., Any]) -> Callable[..., Any]:
    raise NotImplementedError


class ArgCastIntersecting[SuperSet, Result](Protocol):
    def __call__(
        self,
        target: SuperSet | Result,
        /,
        *,
        default: Maybe[Result] = VOID,
    ) -> SuperSet & Result: ...  # ty:ignore


def paint(color: ColorArg, /) -> Painter:
    color: Color = Color.resolve(color)
    return colors.paint(color)


blue = paint(3)
md = blue("data/response.md")

print(blue)
print(md)
print()


def color_intersect1(text: str, color: Color) -> str:
    return colors(text, color)


# FAIL: bla_purple = color_intersect1("bla", 4)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def intersector(  # STRATEGY: this is valuable!
    func: Callable[[str, Color], str],
) -> Callable[[str, Color], str] & Callable[[str, ColorArg], str]:
    def wrapper(
        text: str,
        color: ColorArg,
    ) -> str:

        print("\nintersector::color:", end=" ")
        reveal_type(color)
        resolved: Color = Color.resolve(color)
        print("\nintersector::resolved:", end=" ")
        reveal_type(resolved)
        return func(text, resolved)

    reveal_type(wrapper)
    return wrapper


@intersector
def color_intersect2(text: str, color: Color) -> str:
    print("color_intersect2::color:", end=" ")
    reveal_type(color)
    return colors(text, color)


bla_purple = color_intersect2("hello", 5)
bla_green = color_intersect2("bye", "green")
x = color_intersect2("final", 4)

print(bla_green)
print(bla_purple)
print(x)

reveal_type(color_intersect2)


def intersector_generic[F: Callable[[str, Color], str]](
    func: F,
) -> F & Callable[[str, ColorArg], str]:
    def wrapper(  # FIX: maybe comehow reparable?
        text: str,
        color: ColorArg,
    ) -> str:
        resolved: Color = Color.resolve(color)
        return func(text, resolved)

    reveal_type(wrapper)
    return wrapper  # ty:ignore


@intersector_generic
def color_generic(text: str, color: Color) -> str:
    print("color_intersect2::color:", end=" ")
    reveal_type(color)
    return colors(text, color)


reveal_type(color_generic)

bla_purple = color_generic("xx", 3)
bla_green = color_generic("bye", "green")
x = color_generic("final", 4)

print(bla_green)
print(bla_purple)
print(x)
