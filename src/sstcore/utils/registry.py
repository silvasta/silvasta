"""
Implement the Main Variations of the Core Registry.

- ListRegistry
- DictRegistry

Mix FunctionalRegistry, FilteringRegistry or BaseModel as desired.

"""

__all__: list[str] = [
    "ListRegistry",
    "FilterRegistry",
    "DictRegistry",
]

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from ..port.filter import Filter
from ..port.registry import (
    DictingRegistry,
    FilteringRegistry,
    ListingRegistry,
    Registry,
)


class ListRegistry[ItemT]:
    """Implement the Shape of the Registry with List"""

    items: list[ItemT]

    def __len__(self) -> int:
        return len(self.items)

    def __contains__(self, target: ItemT) -> bool:
        return target in self.items

    @property
    def all(self) -> Iterable[ItemT]:
        yield from self.items

    def _item_identifier(self, item: ItemT) -> Any:
        """Select and set the most important attribute of the Item"""
        raise NotImplementedError(item)

    def add(self, item: ItemT, clear: bool = False) -> int:
        num: int = self.clear(self._item_identifier(item)) if clear else 0
        self.items.append(item)
        return num

    def get(self, key: Any) -> list[ItemT]:
        return [
            item for item in self.items if self._item_identifier(item) == key
        ]

    def clear(self, key: Any | None = None) -> int:
        before: int = len(self)
        if key is None:
            self.items.clear()
        else:
            self.items: list[ItemT] = [  # LATER: improve
                item
                for item in self.items
                if self._item_identifier(item) != key
            ]
        return before - len(self)


class FilterRegistry[ItemT]:
    """Extend the ListRegistry with filtered items"""

    filter: Filter | None
    all: Iterable[ItemT]

    def _prepare_filter(self, filter: Filter | None) -> Filter | None:
        """Cache filter if provided and provide resulting cached Filter"""
        if filter:
            self.filter: Filter = filter
        return self.filter

    def filtered(self, filter: Filter | None = None) -> list[ItemT]:
        """Filter items using provided filter or instance filter."""
        if active_filter := self._prepare_filter(filter):
            return active_filter(self.all)  # ty:ignore # FIX: overload
        return list(self.all)


if TYPE_CHECKING:
    _registry: Registry = ListRegistry()
    _registry: ListingRegistry = ListRegistry()
    _registry: FilteringRegistry = FilterRegistry()


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
        if (exists := key in self.items) and not clear:
            raise KeyError("Item already in Registry!", _item, _key)
        self.items[_key] = _item
        return int(exists)

    def get(self, key: KeyT) -> ItemT | None:
        return self.items.get(key)

    def clear(self, key: KeyT | None = None) -> int:
        if key is None:
            self.items.clear()
        return 0 if self.items.pop(key, None) is None else 1


if TYPE_CHECKING:
    _registry: Registry = DictRegistry()
    _registry: DictingRegistry = DictRegistry()
