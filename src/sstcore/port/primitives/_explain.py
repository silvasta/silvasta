"""
Visualisation and Explanation Container for Enums and Domain Objects

.
"""

__all__: list[str] = [
    "ExplainTuple",
]

from collections.abc import Iterable, Mapping
from enum import Enum
from typing import Any, NamedTuple, Self

from ..primitives import _zero as _z
from ._field import TupleField


class _ExplainBase[O: Any = Any](NamedTuple):
    origin: O
    title: str
    detail: str = ""


class ExplainTuple[O: Any = Any](_ExplainBase[O], _z.TupleBase):
    """Hold explanation data and formatting rules for an origin object or Enum/IntFlag."""

    icon = TupleField[str]("ⓘ")
    sep = TupleField[str](" — ")

    def __str__(self) -> str:
        return self.__format__("")

    def __repr__(self) -> str:
        return self.__format__("vn")

    def __format__(self, format_spec: str, /) -> str:
        return _z.format_explain(self, format_spec)

    def explain(self, *, brief: bool = False) -> str:
        """Render human-readable explanation (brief title or multiline full)."""
        return self.__format__("t" if brief or not self.detail else "vn")

    def __rich__(self) -> Any:
        from rich.console import Group
        from rich.panel import Panel

        return Group(Panel(str(self.origin)), Panel(self.explain()))

    @classmethod
    def table(cls, *items: Self) -> dict[O, Self]:
        """Build an origin -> ExplainTuple mapping, rejecting duplicate keys."""
        out: dict[O, Self] = {}
        for item in items:
            if item.origin in out:
                raise ValueError(
                    f"Duplicate ExplainTuple origin: {item.origin!r}"
                )
            out[item.origin] = item
        return out

    @classmethod
    def combine[E: Enum](
        cls,
        member: E,
        field: Mapping[E, ExplainTuple[E]] | str = "explaining",
    ) -> ExplainTuple[E]:
        """
        Synthesize a composite ExplainTuple for a combined Flag/IntFlag member.

        Works both as a 1-arg LazyMap fallback and as a 2-arg explicit combiner.
        """
        table: Mapping[E, ExplainTuple[E]] = (
            getattr(type(member), field) if isinstance(field, str) else field
        )
        flags: Iterable[E] = (
            member if isinstance(member, Iterable) else (member,)
        )
        parts: list[ExplainTuple[E]] = [table[flag] for flag in flags]

        return ExplainTuple(
            origin=member,
            title="\n".join(f"[{r.origin.value}] {r.title}" for r in parts),
            detail="\n".join(
                f"[{r.origin.value}] {r.detail}" for r in parts if r.detail
            ),
        )
