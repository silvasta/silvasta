"""
DictRegistry - Main Variation of the Core Registry

-
"""

__all__: list[str] = [
    "DictRegistry",
]

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from ...port.register import DictRegister


class DictRegistry[ItemT, KeyT]:
    """Implement the Shape of the Registry with Dict"""

    items: dict[KeyT, ItemT]

    def __len__(self) -> int:
        return len(self.items)

    def __contains__(self, target: KeyT) -> bool:
        return target in self.items

    @property
    def all(self) -> Iterable[ItemT]:
        yield from self.items.values()

    def _item_identifier(self, item: ItemT) -> tuple[KeyT, ItemT]:
        raise NotImplementedError(item)

    def add(self, target: Any, *, clear: bool = False, **kwargs) -> int:
        _key, _item = self._item_identifier(target, **kwargs)
        if _key in self.items and not clear:
            raise KeyError("Item already in Registry!", _item, _key)
        self.items[_key] = _item
        return 1  # amount of new items

    def get(self, key: KeyT) -> ItemT | None:
        return self.items.get(key)

    def clear(self, key: KeyT | None = None) -> int:
        if key is None:
            self.items.clear()
        return 0 if self.items.pop(key, None) is None else 1


if TYPE_CHECKING:
    _instance: DictRegister = DictRegistry()
    _class: type[DictRegister] = DictRegistry
