"""
Most basic parts

.
"""

__all__: list[str] = [
    "NamedValue",
    "SingleTuple",
    "ExplainedTuple",  # MOVE: maybe too detailed...
]

import builtins as _b
import collections.abc as _cabc
import typing as _typing
from collections.abc import Iterable, Mapping
from enum import Enum
from typing import Any, NamedTuple, Self

from ._format import format_explain, format_named_value
from ._hashed import HashedTuple
from ._tupled import TupleBase, TupleField, get_named_value_item


class NamedValue[T: Any = Any](_typing.NamedTuple):
    name: str
    value: T

    def __bool__(self) -> bool:
        return bool(self.value)

    def __format__(self, spec: str) -> str:
        return format_named_value(self, spec)

    def __getitem__(self, key: str | int) -> T | str:  # ty: ignore
        """Hardcore Encode Default Behaviour plus Var()[name]=value access"""
        return get_named_value_item(self, key)

    def keys(self) -> _cabc.KeysView[str]:
        return _cabc.KeysView({self.name: None})

    def hashed(self, strict: bool = True) -> HashedTuple:
        """Recursively Enforce Freeze and Hash (strict=False -> str(obj))"""
        return HashedTuple(*self, strict=strict)


class SingleTuple[T: Any = Any](_typing.NamedTuple):
    data: T

    @property
    def tuple(self):
        return _b.tuple(self.data)

    @property
    def list(self):
        return _b.list(self.data)

    @property
    def set(self):  # LATER: check for not hashable
        return _b.set(self.data)

    def __iter__(self) -> _cabc.Iterator:
        yield from self.data

    def __len__(self) -> int:  # ty:ignore
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, item: object) -> bool:
        return item in self.data


class _Variadics[A: SingleTuple, K: SingleTuple](_typing.NamedTuple):
    # FAIL: parameter forwarding
    args: SingleTuple
    kwargs: SingleTuple


class _ExplainBase[O: Any = Any](NamedTuple):
    origin: O
    title: str
    detail: str = ""


class ExplainedTuple[O: Any = Any](_ExplainBase[O], TupleBase):  # MOVE:
    # CHECK: TupleMixed??
    """Hold explanation data and formatting rules for an origin object or Enum/IntFlag."""

    icon = TupleField[str]("ⓘ")
    sep = TupleField[str](" — ")

    def __str__(self) -> str:
        return self.__format__("")

    def __repr__(self) -> str:
        return self.__format__("vn")

    def __format__(self, format_spec: str, /) -> str:
        return format_explain(self, format_spec)

    def explain(self, *, brief: bool = False) -> str:
        """Render human-readable explanation (brief title or multiline full)."""
        return self.__format__("t" if brief or not self.detail else "vn")

    # NEXT: __call__ instead of explain! (but forward spec as well, brief:bool|str?)
    # - make ExplainedTuple.brief its own method?
    # - __call__ with all format_specs?

    def __rich__(self) -> Any:
        from rich.console import Group
        from rich.panel import Panel

        return Group(Panel(str(self.origin)), Panel(self.explain()))

    @classmethod
    def table(cls, *items: Self) -> dict[O, Self]:
        """Build an origin -> ExplainedTuple mapping, rejecting duplicate keys."""
        out: dict[O, Self] = {}
        for item in items:
            if item.origin in out:
                raise ValueError(
                    f"Duplicate ExplainedTuple origin: {item.origin!r}"
                )
            out[item.origin] = item
        return out

    @classmethod
    def combine[E: Enum](  # FIX: strange parametization
        cls,
        member: O,
        field: Mapping[E, ExplainedTuple[E]] | str = "explaining",
    ) -> Self:
        """
        Synthesize a composite ExplainedTuple for a combined Flag/IntFlag member.

        Works both as a 1-arg LazyMap fallback and as a 2-arg explicit combiner.
        """
        table: Mapping[E, ExplainedTuple[E]] = (
            getattr(type(member), field) if isinstance(field, str) else field
        )

        # CHECK:
        flags: tuple[E, ...] = (
            tuple(member) if isinstance(member, Iterable) else ()
        )
        # CHECK:
        if not flags or (len(flags) == 1 and flags[0] == member):
            raise KeyError(member)

        parts: list[ExplainedTuple[E]] = [table[flag] for flag in flags]

        return cls(
            origin=member,
            title="\n".join(f"[{r.origin.value}] {r.title}" for r in parts),
            detail="\n".join(
                f"[{r.origin.value}] {r.detail}" for r in parts if r.detail
            ),
        )
