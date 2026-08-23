"""
ListRegistry - Main Variation of the Core Registry

-
"""

__all__: list[str] = [
    "ListRegistry",
]

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from ...port.register import ListRegister


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

    def add(self, item: ItemT, override: bool = False) -> int:
        num: int = self.clear(self._item_identifier(item)) if override else 0
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


if TYPE_CHECKING:
    _instance: ListRegister = ListRegistry()
    _class: type[ListRegister] = ListRegistry
