"""
Transform to str, be the pattern and parse the pattern

  (Experimental Setup)
                                                       DependencyLevel[2]
"""

from pathlib import Path
from typing import Any, Self

from ._parse import NameParser

__all__: list[str] = [
    "Name",
]


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

    # IDEA: slots?

    def __new__(cls, value: str | Path, **kwargs: Any) -> Self:
        if isinstance(value, Path):
            value = value.name

        parser = NameParser(pattern=getattr(cls, "pattern", value), **kwargs)
        parser.extract(value)  # Validate on construction

        new_name: Self = str.__new__(cls, value)
        new_name._parser = parser  # ty:ignore
        return new_name

    def parse(self) -> dict[str, Any]:
        return self.extract(str(self))

    def format(self, keys: dict | list | tuple) -> Name:  # ty:ignore
        """Override str.format with NameParser.format"""  # CHECK:
        new_value: str = self.format(keys)
        return type(self)(new_value)

    def __rich__(self) -> str:
        return f"[bold {self._color}]{self}[/]"
