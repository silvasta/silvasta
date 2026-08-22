"""
Define the shape of the Core Registry.

-
"""

__all__: list[str] = [
    "Registry",
    "ListingRegistry",
    "DictingRegistry",
    "FunctionalRegistry",
    "FilteringRegistry",
]

from collections.abc import Callable, Iterable
from enum import Enum
from typing import Any, Protocol

from .filter import Filter


class Registry[ItemT](Protocol):
    """Define the Shape of the general Registry"""

    def __len__(self) -> int:
        """Count all member"""

    def __contains__(self, target: Any) -> bool:
        """Has member?"""

    @property
    def all(self) -> Iterable[ItemT]:
        """Yield all items"""

    def add(self, *args, **kwargs) -> int:
        """Extend members by new item, clear Num existing items by identifier"""

    def get(self, key: Any) -> ItemT | None | list[ItemT]:
        """Provide item by key"""

    def clear(self, key: Any | None = None) -> int:
        """Delete entire content and provide number of cleared items"""


class ListingRegistry[ItemT](Registry, Protocol):
    """Establish the Registry with a List of Items"""

    items: list[ItemT]

    def add(self, item: ItemT, clear) -> int: ...


class DictingRegistry[ItemT, KeyT](Registry, Protocol):
    """Establish the Registry with a Dict of Items"""

    items: dict[KeyT, ItemT]


class FunctionalRegistry[ItemT: Callable](Protocol):
    """Extend the Registry with Functional Items"""

    def attach(self: Registry) -> Callable[[ItemT], ItemT]:
        """Register new member by Decorator"""


class FilteringRegistry[ItemT](Protocol):
    """Extend the Registry with filtered items"""

    # NEXT:
    # NOTE: bacically the same as port.filter.Filtering
    # - check when use and take maybe the other

    filter: Filter[Any, ItemT] | None

    def filtered(
        self, filter: Filter[Any, ItemT] | None = None
    ) -> list[ItemT]:
        """Provide items that pass the given (or internal) filter."""


# TASK: define axes
class IndexingRegistry[ItemT, IndexT: Index | tuple[Index, ...]](
    Registry, Protocol
):
    """Establish the Registry with Enum and Tuple"""

    items: tuple[ItemT, ...]
    index: IndexT | tuple[IndexT]


class Index(Enum):
    """Define one countable Axis"""

    def __str__(self) -> str:
        return f"{self.name.capitalize()}"

    def __repr__(self) -> str:
        return f"{cls_name(self)}[{self.value}]::{self}"

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> int:
        """Return the index of the Color inside the Palette"""
        return count
