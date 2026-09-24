"""
TupleRegistry - Main Variation of the Core Registry

-
"""

from pathlib import Path

__all__: list[str] = [
    "TupleRegistry",
]

from typing import TYPE_CHECKING, Any, overload

from ...port.register import TupleRegister
from ._base import BaseRegistry


class TupleRegistry[Item](BaseRegistry[Item, tuple, int, Any]):
    """Implement the Shape of the Registry with Tuples"""

    def add(self, items: tuple[tuple[Item, int]], **_kwargs):
        # AI: outdated
        """Extend Items directly or with processing"""
        modified_data: list[Item] = list(self.vault)
        for item, index in items:
            if index in self:
                # TASK: insertion order
                # - find system to solve this
                modified_data.insert(index, item)
        return type(self)(items=tuple(modified_data))

    @overload
    def clear(self, key: None) -> tuple[Item, ...]: ...
    @overload
    def clear(self, key: int) -> Item: ...
    def clear(self, key: int | None = None) -> tuple[Item, ...] | Item:
        """Delete and return full registry or return selected element"""
        # AI: outdated
        old_data: tuple[Item, ...] | Item = (
            self.vault[key]
            if key is not None and key in self
            else tuple(*self.vault)
        )
        self.vault = ()
        return old_data

    def __contains__(self, target) -> bool:
        return (target is None) or (0 <= target < len(self))

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def _clear_all(self) -> None:
        self.vault = ()

    def _slice_action(self, s: slice) -> Any:
        return tuple(self[s])

    def _str_action(self, k: str) -> Any:
        return ()

    def _item_action(self, target: Item) -> Any:
        return ()

    def _int_action(self, i: int) -> Item | None:
        if 0 < i < len(self):
            return self.vault[i]

    def _sanitize(self, result: tuple[Item] | Item | None) -> tuple:
        match result:
            case None:
                return ()
            case dict():
                return result
            case _:
                return (result,)

    def _remove(self, targets: tuple[Item]) -> tuple[Item]:
        """Return all removed"""
        keep = []
        remove = []
        for item in self:
            if item in targets:
                remove.append(item)
            else:
                keep.append(item)
        self.vault = tuple(keep)
        return tuple(remove)

    def _append(self, items: tuple[Item]):
        """Return all duplicated"""
        new: tuple[Item] = self.vault + items
        self.vault = new

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


if TYPE_CHECKING:
    _instance: TupleRegister[Path, int] = TupleRegistry[Path](tuple(Path()))
    _class: type[TupleRegister[Path, int]] = TupleRegistry[Path]
