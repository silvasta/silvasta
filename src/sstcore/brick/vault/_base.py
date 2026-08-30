"""
ListRegistry - Main Variation of the Core Registry

-
"""

from sstcore.port.error import Error

__all__: list[str] = [
    "ListRegistry",
]

from collections.abc import Iterator
from typing import TYPE_CHECKING, overload

from ...port.register import ListRegister


class RegistryError(Error): ...  # TODO:


type Basic = list | tuple | dict


class BaseRegistry[B: Basic, I, K]:
    """Implement the Shape of the Registry with List"""

    items: B

    def clear(self, *keys: K) -> B:
        if not keys:
            items: B = self.items  # TODO: slice all)
            self._clear_all()
        else:
            keep: list[I] = []
            clear: list[I] = []
            for key in keys:
                for entry in self:
                    return self._clear_by_key(key)

    def _clear_all(self) -> B:
        # NOTE: maybe with descriptors?
        items: B = [*self.items]
        self.items.clear()
        return items

    def _clear_by_key(self, key: K) -> B:
        keep: list[I] = []
        clear: list[I] = []
        for entry in self:
            if self.match(entry, key):
                clear.append(entry)
            else:
                keep.append(entry)
        return clear

    def match(self, entry: I | C, key: K) -> bool:
        raise NotImplementedError

    def find(self, key: K) -> list[I]:
        return [item for item in self if self.match(item, key)]

    def count(self, key: K) -> int:
        return len(self.find(key))

    @overload
    def __getitem__(self, index: slice) -> B: ...
    @overload
    def __getitem__(self, index: int) -> I: ...
    def __getitem__(self, index: int | slice) -> B:
        match index:
            case slice():  # LATER: return maybe sliced registry
                return self.items[index]
            case int():
                return self.items[index]
        raise RegistryError(f"Registry Index[{index}] failed!", index)

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[I]:
        yield from self.items

    def __contains__(self, target: I | K) -> bool:
        return target in self.items

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


if TYPE_CHECKING:
    _instance: ListRegister = ListRegistry()
    _class: type[ListRegister] = ListRegistry
