"""
ListRegistry - Main Variation of the Core Registry

-
"""

from sstcore.port.error import Error

__all__: list[str] = [
    "ListRegistry",
]

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, overload

from ...port.register import ListRegister


class RegistryError(Error): ...  # TODO:


class ListRegistry[ItemT, KeyT]:
    """Implement the Shape of the Registry with List"""

    items: list[ItemT]

    def __init__(self, *items: ItemT) -> None:
        self.items: list[ItemT] = [*items]

    def add(self, *items: ItemT, override: bool = False) -> list[ItemT]:
        cleared: list[ItemT] = []
        for item in items:
            if override:
                cleared.extend(self.clear(self._item_identifier(item)))
            self.items.append(item)
        return cleared

    def clear(self, key: KeyT | None = None) -> list[ItemT]:
        if key is None:
            return self._clear_all()
        else:
            return self._clear_by_key(key)

    def find(self, key: KeyT) -> list[ItemT]:
        return [item for item in self if self._item_identifier(item) == key]

    def count(self, key: KeyT) -> int:
        return len(self.find(key))  # LATER: optimise

    @overload
    def __getitem__(self, index: slice) -> list[ItemT]: ...
    @overload
    def __getitem__(self, index: int) -> ItemT: ...
    def __getitem__(self, index: int | slice) -> list[ItemT]:
        if TYPE_CHECKING:
            index: Any = Any  # Avoid grey shadow Error for code not reachable
        match index:
            case slice():  # LATER: return maybe sliced registry
                return self.items[index]
            case int():
                return self.items[index]
        raise RegistryError(f"Registry Index[{index}] failed!", index)

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[ItemT]:
        yield from self.items

    def __contains__(self, target: ItemT) -> bool:
        return target in self.items

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def _clear_all(self) -> list[ItemT]:
        items: list[ItemT] = [*self.items]
        self.items.clear()
        return items

    def _clear_by_key(self, key: KeyT) -> list[ItemT]:
        keep: list[ItemT] = []
        clear: list[ItemT] = []
        # AI: something like this possible: clear.append(item) for item in self if ( self._item_identifier(item) == key ) else keep.append(item) ?
        for item in self:
            if self._item_identifier(item) == key:
                clear.append(item)
            else:
                keep.append(item)
        self.items: list[ItemT] = keep
        return clear

    def _item_identifier(self, item: ItemT) -> KeyT:
        """Select and set the most important attribute of the Item"""
        raise NotImplementedError(item)  # LATER: this with some setter?


if TYPE_CHECKING:
    _instance: ListRegister = ListRegistry()
    _class: type[ListRegister] = ListRegistry
