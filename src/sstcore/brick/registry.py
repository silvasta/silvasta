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

from collections.abc import Callable, Iterable, Iterator
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


class FilterRegistry[ItemT]:  # FIX: why ListRegistry??
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
    _registry: Registry = DictRegistry()
    _registry: DictingRegistry = DictRegistry()


class TupleIndexRegistry[ItemT, IndexT]:
    # FIX:
    # FIX:
    # FIX:
    # FIX:
    # FIX:
    # FIX: or remove
    def __init__(self, index: type[IndexT], items: tuple[ItemT, ...]) -> None:
        if len(items) != len(index):
            raise ValueError(f"need {len(index)} items, got {len(items)}")
        self.index = index
        self.items = items
        self._by_name = {m.name.lower(): m for m in index}

    def __len__(self) -> int:
        return len(self.items)

    def __contains__(self, target: Any) -> bool:
        try:
            self.resolve(target)
            return True
        except KeyError, ValueError:
            return False

    @property
    def all(self) -> Iterable[ItemT]:
        return self.items

    def resolve(self, key: EnumT | int | str) -> EnumT:
        if isinstance(key, self.index):
            return key
        if isinstance(key, int):
            return self.index(key)
        return self._by_name[str(key).lower()]

    def get(self, key: EnumT | int | str) -> ItemT:
        return self.items[self.resolve(key).value]


class TupleRegistry[ItemT]:
    """An immutable, high-speed contiguous array-backed registry."""

    __slots__ = ("_items", "_identifiers")

    def __init__(self, items: Iterable[ItemT], key_fn: Callable[[ItemT], Any]):
        self._items: tuple[ItemT, ...] = tuple(items)
        self._identifiers: tuple[Any, ...] = tuple(
            key_fn(item) for item in self._items
        )

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, key: Any) -> bool:
        return key in self._identifiers

    def __iter__(self) -> Iterator[ItemT]:
        return iter(self._items)

    @property
    def all(self) -> tuple[ItemT, ...]:
        return self._items

    def get(self, key: Any) -> ItemT | None:
        try:
            idx = self._identifiers.index(key)
            return self._items[idx]
        except ValueError:
            return None
