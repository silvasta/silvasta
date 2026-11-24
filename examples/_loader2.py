"""Loader type spectrum. Outside the library."""

from rich import print
from rich.panel import Panel
from rich.table import Table

from sstcore.port.structures import Loader


def main() -> None:
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
        ("func", Loader(load_str)),
        ("func args", Loader(load_int)),
        ("union func", Loader(load_union)),
        ("func beats default", Loader(load_str, default=5)),
        ("explicit beats both", IntLoader(load_str, default="nope")),  # ty:ignore FIX:
        ("loaded", ready),
        ("prefer default", held),
    )

    table = Table(title="loader spectrum", show_lines=True)
    for column in ("case", "str", "T", "T from", "P", "P from", "also"):
        table.add_column(column)
    for case, loader in samples:
        found = loader._type_args
        table.add_row(
            case,
            str(loader),
            found.render().split(", ", 1)[-1],
            found.value_source,
            found.render().split(", ", 1)[0],
            found.parameters_source,
            found.extras(),
        )
    print(table)
    print(Panel(repr(ready), title="loaded repr"))


if __name__ == "__main__":
    main()
