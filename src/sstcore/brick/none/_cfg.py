"""
Temporary Storage - until next improvisation

                              DependencyLevel.sstcore.brick.none[0]
"""

from collections.abc import Generator as _Generator
from collections.abc import Iterable as _Iterable
from contextlib import contextmanager
from pathlib import Path

from rich.console import Console


class Config:
    DRYRUN = True  # toggle by comment

    @staticmethod
    def dry_run():
        return hasattr(Config, "DRYRUN")

    @staticmethod
    def target_file(name: str) -> Path:  # LATER: PathGuard
        dir: Path = Path.home() / "sstcore/src/sstcore/brick/stack"
        return dir / "_stubs" / f"_{name.lower()}.pyi"


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

"""
Run Quick Tests

-
"""

_console = Console()


def rich_markup(text: str, style: str = "bold"):
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
