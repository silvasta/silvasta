"""
Transform to str, be the pattern and parse the pattern

                        DependencyLevel.sstcore.brick.format[1.0:0]
"""

from pathlib import Path
from typing import Any, Self

from ....port.link import portlink
from ....port.normalize import NameParsing
from ....port.primitives import NameParser

__all__: list[str] = [
    "Name",
]


@portlink(NameParsing)
class Name(NameParser, str):
    """Integrate the NameParser and Pattern directly into str"""

    def __new__(cls, pattern: str | Path, /, **kwargs: Any) -> Self:
        """Create str from prepared Pattern and attach NameParser"""
        if isinstance(pattern, Path):
            pattern = pattern.name

        parser = NameParser(pattern=getattr(cls, "pattern", pattern), **kwargs)
        parser.extract(pattern)  # Validate on construction

        new_name: Self = str.__new__(cls, pattern)
        new_name._parser = parser  # ty:ignore
        return new_name

    def render(self, keys: dict | list | tuple) -> Name:
        # CHECK: is this even helpful? the parsed string contains probably no {keys}
        new_pattern: str = super().render(keys)
        return type(self)(new_pattern)


if __name__ == "__main__":
    from rich.console import Console

    print = Console().print

    def _str_repr_raw(x):
        print("STR_", end=" ")
        print(str(x))
        print("REPR", end=" ")
        print(repr(x))
        print(x)
        print()
        print("RAW_", end=" ")
        print(x)

    names = [
        name1 := Name("Hello {user}, select {task} to {do}"),
        name2 := Name("New {input} for {Raiser}?"),
    ]

    print("\n", "--- basic", "\n")
    for name in names:
        _str_repr_raw(name)
        print(name.keys)
        print(name.__rich__())

    render = [
        [
            ("silvan", "refactor", "delay"),
            ("silvan", "refactor", "complete"),
        ],
        [
            ("Parser", "RAISER"),
            ("Input", "Error"),
        ],
    ]

    print("\n", "--- render")
    for name, task in zip(names, render, strict=True):
        print("\n", name, "\n", f"{task=}", "\n")
        for i in task:
            print(name(i))

    extract = [
        [
            "Hello Raiser, select failure to raise",
            "Hello Silvan, select beer to drink",
        ],
        [
            "New color for paint?",
            "New target for RAISE?",
        ],
    ]

    print("\n", "--- extract")
    for name, task in zip(names, extract, strict=True):
        print("\n", name, "\n", f"{task=}", "\n")
        for i in task:
            print(name(i))

    print("\n", "ColorFlip", "\n")

    class NewName(Name): ...

    name3 = NewName("My {new} Pattern")

    print(f"{name1.color=}")
    print(name1)
    print(name2)
    print(name3)
    print()

    name1.color = "red"

    print(f"{name1.color=}")
    print(name1)
    print(name2)
    print(name3)
    print()

    name3.color = "purple3"
    print(name1)
    print(name2)
    print(name3)

    name2.color = "gold3"
    print(name1)
    print(name2)
    print(name3)
