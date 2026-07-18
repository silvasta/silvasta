from pathlib import Path
from typing import Any, Self

from .base import NameParser

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

    def __new__(cls, value: str | Path, **kwargs: Any) -> Self:
        if isinstance(value, Path):
            value = value.name

        parser = NameParser(pattern=getattr(cls, "pattern", value), **kwargs)
        # Validate on construction
        parser.extract(value)

        obj: Self = str.__new__(cls, value)
        obj._parser = parser  # ty:ignore
        return obj

    def parse(self) -> dict[str, Any]:
        return self.extract(str(self))

    def format(self, keys: dict | list | tuple) -> Name:
        new_value = self.format(keys)
        return type(self)(new_value)

    def __rich__(self) -> str:
        return f"[bold cyan]{self}[/]"
