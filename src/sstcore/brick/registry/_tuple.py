"""
TupleRegistry - Main Variation of the Core Registry

-
"""

from pathlib import Path

__all__: list[str] = [
    "TupleRegistry",
]

from collections.abc import Iterable
from typing import TYPE_CHECKING, Self, overload

from ...port.register import TupleRegister


class TupleRegistry[ItemT]:
    """Implement the Shape of the Registry with Tuples"""

    def __init__(self, items: tuple[ItemT, ...], **_kwargs):
        self.items: tuple[ItemT, ...] = tuple(items)

    def add(self, items: tuple[tuple[ItemT, int]], **_kwargs) -> Self:
        """Extend Items directly or with processing"""
        modified_data: list[ItemT] = list(self.items)
        for item, index in items:
            if index in self:
                modified_data[index] = item
        return type(self)(items=tuple(modified_data))

    def get(self, key: int) -> ItemT | None:
        if key in self:
            return self.items[key]
        return None

    @overload
    def clear(self, key: None) -> tuple[ItemT, ...]: ...
    @overload
    def clear(self, key: int) -> ItemT: ...
    def clear(self, key: int | None = None) -> tuple[ItemT, ...] | ItemT:
        """Delete and return full registry or return selected element"""
        old_data: tuple[ItemT, ...] | ItemT = (
            self.items[key]
            if key is not None and key in self
            else tuple(*self.items)
        )
        self.items = ()
        return old_data

    @property
    def all(self) -> Iterable[ItemT]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __contains__(self, target) -> bool:
        # AI: check if that works
        return (target is None) or (0 <= target < len(self))


if TYPE_CHECKING:
    _instance: TupleRegister[Path, int] = TupleRegistry[Path]()
    _class: type[TupleRegister[Path, int]] = TupleRegistry[Path]
