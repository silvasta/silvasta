"""
Transform to str, be the pattern and parse the pattern

  (Experimental Setup)
                                                       DependencyLevel[2]
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
    """
    EXPERIMENTAL!

    Immutable string that knows its own pattern.

    Useful for event names, bus keys, or any place where you want
    a validated string that can still parse itself.

    Example:
        class EventName(Name):
            pattern = "{namespace}.{event}"

        ev = EventName("ui.click")
        data = ev.parse()          # → dict
    """

    def __new__(cls, value: str | Path, **kwargs: Any) -> Self:
        if isinstance(value, Path):
            value = value.name

        parser = NameParser(pattern=getattr(cls, "pattern", value), **kwargs)
        parser.extract(value)  # Validate on construction

        new_name: Self = str.__new__(cls, value)
        new_name._parser = parser  # ty:ignore
        return new_name

    def render(self, keys: dict | list | tuple) -> Name:
        new_value: str = super().render(keys)
        return type(self)(new_value)


if __name__ == "__main__":
    from rich.console import Console

    print = Console().print

    def rawreprstr(x):
        print("RAW_", end=" ")
        print(x)
        print("REPR", end=" ")
        print(repr(x))
        print("STR_", end=" ")
        print(str(x))

    names = [
        Name("Hello {user}, select {task} to {do}"),
        Name("New {input} for {Raiser}?"),
    ]
    for name in names:
        rawreprstr(name)
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

    for name, _input in zip(names, render, strict=True):
        for i in _input:
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
    for name, _input in zip(names, extract, strict=True):
        for i in _input:
            print(name(i))
