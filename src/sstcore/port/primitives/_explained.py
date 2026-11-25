"""
ExplainedTuple

.
"""

__all__: list[str] = [
    "ExplainedTuple",
]

from collections.abc import Iterable, Mapping
from typing import Any, Self

from ._format import format_explain
from ._tuplebase import TupleBase, TupleField
from ._tuples import _ExplainBase


class ExplainedTuple[T: Any = Any](_ExplainBase[T], TupleBase):
    """Hold explanation data and formatting rules for an origin object or Enum/IntFlag."""

    icon = TupleField[str]("ⓘ")
    sep = TupleField[str](" — ")

    def __str__(self) -> str:
        return self.__format__("")

    def __repr__(self) -> str:
        return self.__format__("vn")

    def __format__(self, format_spec: str, /) -> str:
        return format_explain(self, format_spec)

    def __call__(self, *, brief: bool = False) -> str:
        """Render human-readable explanation (brief title or multiline full)"""
        return self.__format__("t" if brief or not self.detail else "vn")

    def __rich__(self) -> Any:
        from rich.console import Group
        from rich.panel import Panel

        return Group(Panel(str(self.origin)), Panel(self()))

    @classmethod
    def table(cls, *items: Self) -> dict[T, Self]:
        """Build an origin -> ExplainedTuple mapping, rejecting duplicate keys."""
        out: dict[T, Self] = {}
        for item in items:
            if item.origin in out:
                raise ValueError(
                    f"Duplicate ExplainedTuple origin: {item.origin!r}"
                )
            out[item.origin] = item
        return out

    @classmethod
    def _resolve_flag(cls, flag: T) -> ExplainedTuple[T]:
        explain: Any = getattr(flag, "explain", None)
        if isinstance(explain, cls):
            return explain
        for attr in vars(type(flag)).values():
            if type(attr).__name__ == "EnumField":
                val: Any = getattr(flag, attr.public_name, None)
                if isinstance(val, cls):
                    return val
        raise KeyError(flag)

    @classmethod
    def combine(
        cls,
        member: T,
        table: Mapping[T, ExplainedTuple[T]] | None = None,
    ) -> Self:
        """
        Synthesize a composite ExplainedTuple for a combined Flag/IntFlag member

        - Work both as a 1-arg LazyMap fallback and as a 2-arg explicit combiner

        """
        flags: tuple[T, ...] = (
            tuple(member) if isinstance(member, Iterable) else ()
        )
        if not flags or (len(flags) == 1 and flags[0] == member):
            raise KeyError(member)

        if table is not None:
            parts: list[ExplainedTuple[T]] = [table[flag] for flag in flags]
        else:
            parts = [cls._resolve_flag(flag) for flag in flags]

        return cls(
            origin=member,
            title="\n".join(f"[{r.origin.value}] {r.title}" for r in parts),
            detail="\n".join(
                f"[{r.origin.value}] {r.detail}" for r in parts if r.detail
            ),
        )
