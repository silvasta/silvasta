"""
Visual inspection of Loader generic type extraction and spectrum resolution.

Run via: python examples/loader_spectrum.py
"""

from typing import Any

from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from sstcore.brick.call.___loader import ReflectiveLoader as Loader
from sstcore.brick.reflect import ___typearg as _typearg
from sstcore.brick.reflect.___typearg import extract_type_args, format_type_arg
from sstcore.port.empty import VOID


def main():
    # NEXT: compare port::typeargs with brick::typeargs
    # test_1()
    test_2()


def test_1() -> None:
    def _inspect(name: str, loader: Loader[Any, Any]) -> None:
        lines = [
            f"str:   {loader}",
            f"repr:  {loader!r}",
            f"type:  {loader.target_type!r} (via {loader.type_args.value_source})",
            f"specs: {[str(s) for s in loader.type_args.specs]}",
        ]
        print(Panel(Text("\n".join(lines)), title=name, border_style="cyan"))

    l_empty = Loader()
    l_default = Loader(default=42)
    l_none = Loader(default=None)

    l_explicit = Loader[[str, int], float]()
    l_ellipsis = Loader[..., list[str]]()

    def fetch(host: str, port: int) -> dict[str, Any]:
        return {"host": host, "port": port}

    l_func = Loader(fetch)
    l_func_loaded = Loader(fetch)
    l_func_loaded("localhost", 8080)

    class IntLoader[**P](Loader[P, int]): ...

    class ZeroArgIntLoader(IntLoader[[]]): ...

    class GenericBoxLoader[T](Loader[[T], list[T]]): ...

    class StrBoxLoader(GenericBoxLoader[str]): ...

    class UnboundLoader[T](Loader[[int], T]): ...

    examples: list[tuple[str, Loader[Any, Any]]] = [
        ("Empty", l_empty),
        ("Default int", l_default),
        ("Default None", l_none),
        ("Explicit [[str, int], float]", l_explicit),
        ("Explicit [..., list[str]]", l_ellipsis),
        ("Typed func (unloaded)", l_func),
        ("Typed func (loaded)", l_func_loaded),
        ("Subclass IntLoader", IntLoader()),
        ("Subclass ZeroArgIntLoader", ZeroArgIntLoader()),
        ("Multi-level StrBoxLoader", StrBoxLoader()),
        ("Unbound GenericBoxLoader", GenericBoxLoader()),
        ("UnboundLoader[T]", UnboundLoader()),
    ]

    for label, ldr in examples:
        _inspect(label, ldr)


def test_2() -> None:
    def _str(text: object, /, prefix: bool = True) -> Text:
        return Text(f"{'str: ' if prefix else ''}{text}")

    def _panel(text: object, style: str = "cyan", /) -> None:
        print(Panel(Text(str(text)), style=style))

    def _full(items: tuple[object, ...], /) -> None:
        _panel(repr(items), "green")
        print(f"{len(items)=}")
        print(_str(items))
        for index, item in enumerate(items):
            print(f"item[{index}]", item)

    def load_str() -> str:
        return "loaded"

    def load_int(n: int) -> int:
        return n

    def load_union() -> int | str:
        return 1

    class IntLoader(Loader[..., int]): ...

    class SubIntLoader(IntLoader): ...

    class OpenLoader[X](Loader[..., X]): ...

    class ListLoader[X](Loader[..., list[X]]): ...

    class IntListLoader(ListLoader[int]): ...

    class PairLoader(Loader[[int, str], bool]): ...

    ready = Loader(load_str)
    ready()
    held = Loader(load_int, default=0, prefer="default")
    held(4)

    samples = (
        ("bare", Loader()),
        ("subscript", Loader[..., int]()),
        ("int subclass", IntLoader()),
        ("deep subclass", SubIntLoader()),
        ("open", OpenLoader()),
        ("open + default", OpenLoader(default=5)),
        ("substituted", IntListLoader()),
        ("param list", PairLoader()),
        ("default", Loader(default=5)),
        ("default none", Loader(default=None)),
        ("default bool", Loader(default=True)),
        ("func", Loader(load_str)),
        ("func args", Loader(load_int)),
        ("union func", Loader(load_union)),
        ("func beats default", Loader(load_str, default=5)),
        ("explicit beats both", IntLoader(load_str, default="nope")),
        ("loaded", ready),
        ("prefer default", held),
    )

    _panel("loader spectrum")
    table = Table(show_lines=True)
    for column in ("case", "str", "T", "T from", "P", "P from", "also"):
        table.add_column(column)
    for case, loader in samples:
        found = loader.type_args
        extra = []
        if found.func_return is not VOID:
            extra.append(f"func={format_type_arg(found.func_return)}")
        if found.default_type is not VOID:
            extra.append(f"default={format_type_arg(found.default_type)}")
        table.add_row(
            case,
            str(loader),
            format_type_arg(found.value),
            found.value_source,
            _typearg.format_parameters(found.parameters),
            found.parameters_source,
            ", ".join(extra) or "-",
        )
    print(table)

    _panel("IntListLoader bases, after substitution")
    _full(extract_type_args(IntListLoader()))

    _panel("OpenLoader, X stays open")
    _full(extract_type_args(OpenLoader()))


if __name__ == "__main__":
    main()
