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

    def attach(self, item: ItemT, *args, clear: bool = False, **kwargs) -> int:
        """Extend member by new item, clear Num existing items with same identifier"""

    def get(self, key: Any) -> ItemT | None | list[ItemT]:
        """Provide item by key"""

    def clear(self, key: Any | None = None) -> int:
        """Delete entire content and provide number of cleared items"""


class ListingRegistry[ItemT](Registry, Protocol):
    """Establish the Registry with a List of Items"""

    items: list[ItemT]


class DictingRegistry[ItemT, KeyT](Registry, Protocol):
    """Establish the Registry with a Dict of Items"""

    items: dict[KeyT, ItemT]

    def attach(self, key: KeyT, item: ItemT, *, clear: bool = False) -> int:
        """Extend member by new item"""


class FunctionalRegistry[ItemT: Callable](Protocol):
    """Extend the Registry with Functional Items"""

    items: Callable

    def register(self: Registry) -> Callable[[Callable], Callable]:
        """Attach new member by Decorator"""


class FilteringRegistry[ItemT](Protocol):
    """Extend the Registry with filtered items"""

    # NOTE: basivally the same as port.filter.Filtering
    # - check when use and take maybe the other

    filter: Filter[Any, ItemT] | None

    def filtered(
        self, filter: Filter[Any, ItemT] | None = None
    ) -> list[ItemT]:
        """Provide items that pass the given (or internal) filter."""
