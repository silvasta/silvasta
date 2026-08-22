"""
Run Quick Tests

-
"""

from collections.abc import Generator as _Generator
from collections.abc import Iterable as _Iterable
from contextlib import contextmanager

from colorprint.helper import full_repr
from colorprint.port.collections import Stringable
from rich.console import Console

_console = Console()


def rich_markup(text: Stringable, style: Stringable = "bold"):
    return f"[{style}]{text}[/]" if style else text


_r = rich_markup


def start(_title):
    start = f"{_r('Start', 'steel_blue1')}"
    _console.print(f"{start} {_title}", style="cyan")


def separator():
    print("\n---\n")


@contextmanager
def section(_title: str) -> _Generator:
    start(_title)
    try:
        yield
    except Exception as error:
        print(f"FAIL for {_title}:", error)
    finally:
        separator()


def get_items(_target: _Iterable, _title: str) -> _Generator:
    start(_title)
    try:
        yield from _target
    finally:
        separator()


def color_test(_color):
    console(_color, end=": ")
    console(f"{_color!r}", end=" ")
    console(_color("The formatted text!"))


def console(_target, *args, **kwargs):
    _console.print(_target, *args, **kwargs)


def double_print(_target, *args, **kwargs):
    _console.print(_target, *args, **kwargs)
    print(_target, *args, **kwargs)


def print_full_repr(_target, *args, **kwargs):
    print(full_repr(_target, *args, **kwargs))


def console_full_repr(_target, *args, **kwargs):
    _console.print(full_repr(_target, *args, **kwargs))
