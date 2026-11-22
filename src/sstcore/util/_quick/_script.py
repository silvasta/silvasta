"""
Temporary Storage - until next improvisation

                              DependencyLevel.sstcore.brick.none[0]
"""

from collections.abc import Generator as _Generator
from collections.abc import Iterable as _Iterable
from itertools import combinations
from pathlib import Path

from rich.console import Console

from ...port.primitives import Args, Kwargs, Params, Var


class Config:
    DRYRUN = True  # toggle by comment

    @staticmethod
    def dry_run():
        return hasattr(Config, "DRYRUN")

    @staticmethod
    def target_file(name: str) -> Path:  # LATER: PathGuard
        dir: Path = Path.home() / "sstcore/src/sstcore/brick/stack"
        return dir / "_stubs" / f"_{name.lower()}.pyi"


def _str_repr_raw(x):
    print("STR_", end=" ")
    print(str(x))
    print("REPR", end=" ")
    print(repr(x))
    print("RAW_", end=" ")
    print(x)


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


def section(_title: str) -> _Generator:
    start(_title)
    # NEXT: absorb examples.index_color
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


def rawreprstr(x):
    print("raw", end=" ")
    print(x)
    print("repr", end=" ")
    print(repr(x))
    print("str", end=" ")
    print(str(x))


if __name__ == "__main__":

    def main():
        _all()
        _var()
        # _args()
        # _args_kwargs()
        # _param()
        # _feeding()
        pass

    from rich import print
    from rich.panel import Panel
    from rich.text import Text

    def _str(text, /, prefix=True):
        return Text(f"{'str: ' if prefix else ''}{text}")

    def _panel(text, style="cyan", /):
        print(Panel(Text(f"{text}"), style=style))

    def _full(x):
        _panel(repr(x), "green")
        print(f"{len(x)=}")
        print("raw", x)
        print(_str(x))
        print("repr", repr(x))
        for i, y in enumerate(x):
            print(f"item[{i}]", y)

    def _deref(param):
        _panel(f"Start of deref for {param}")
        print(*param)
        print({**param})
        print(*param, {**param})

    def _args():
        args = Args.absorb("ss", 5, {"hello", "set"})
        _full(args)
        print(args.keys())
        for k in args.keys():
            print(args[k])
        _deref(args)

    var1 = Var("name", 5)
    var2 = Var("other", 20)

    def _var():
        _full(var1)
        _full(var2)
        _panel({**var1, **var2}, "yellow")
        for x in (var1, var2):
            _full(x)
        var1.sep = ":::::"
        for x in (var1, var2):
            _full(x)

    arg1 = Args()
    arg2 = Args.absorb("ss", 5, {"hello", "set"})
    kwarg1 = Kwargs()
    kwarg2 = Kwargs({"a": 1, "b": 2, "c": 3, "d": 4})

    def _args_kwargs():
        _panel("Single", "gold3")
        for x in (arg1, arg2, kwarg1, kwarg2):
            _full(x)

    def _param():
        _panel("combinations", "gold3")
        for a, k in combinations((arg1, arg2, kwarg1, kwarg2), 2):
            _panel(p := Params(a, k))  # ty:ignore
            _full(p)
            _deref(p)

    def _dip(header, text, color="yellow") -> Panel:
        return Panel(f"{header} [{color}]{text}[/]", style="cyan")

    param = Params.absorb("Start", "main text", color="green")

    def _all():
        _full(var2)
        _full(arg2)
        _full(kwarg2)
        _full(param)

    def _feeding():
        print(param)
        dipped = param.feed(_dip)
        # reveal_type(dipped)
        print(dipped)

    main()
