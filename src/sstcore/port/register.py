"""
Define the shape of the Core Registry.

-
"""

__all__: list[str] = [
    # root
    "Registry",
    # bases
    "ListedRegistry",
    "DictedRegistry",
    "TupleRegistry",  # TODO: setup basic definition
    # extenstions
    "FuncRegistry",  # TODO: rename?
    "FilterRegistry",  # TODO: rename?
]

from collections.abc import Callable, Iterable
from enum import Enum
from typing import Any, Protocol

from .filter import Filter


class Registry[Item](Protocol):
    """Define the Shape of the general Registry"""

    items: Any  # AI: I just set this. items? as the global name?

    def __len__(self) -> int:
        """Count all member"""

    def __contains__(self, target: Any) -> bool:
        """Has member?"""

    @property
    def all(self) -> Iterable[Item]:
        """Yield all items"""

    def add(self, *args, **kwargs) -> int:
        """Extend members by new item, clear Num existing items by identifier"""

    def get(self, key: Any) -> Item | None | list[Item]:
        """Provide item by key"""

    def clear(self, key: Any | None = None) -> int:
        """Delete entire content and provide number of cleared items"""


class ListedRegistry[Item](Registry, Protocol):
    """Establish the Registry with a List of Items"""

    items: list[Item]

    def add(self, item: Item, clear) -> int: ...


class DictedRegistry[Item, Key](Registry, Protocol):
    """Establish the Registry with a Dict of Items"""

    items: dict[Key, Item]


# NEXT: TupleReg, yes it makes sense


class MixingRegistry[Mixin: type](Registry, Protocol):
    """Establish the Registry with Tuples (of Mixins, at least for now)"""

    mixins: tuple


class FunctionalRegistry[Item: Callable](Protocol):
    """Extend the Registry for Functions (LATER: and Functors)"""

    def attach(self: Registry) -> Callable[[Item], Item]:
        """Register new member by Decorator"""


class FilteringRegistry[Item: Callable](Protocol):
    """Extend the Registry with Filtering"""

    def filter(self, new_active_filter: Filter | None = None) -> list[Item]:
        """Provide Items that fulfill the active Filter"""

    def set_filter(self, active_filter: Filter) -> None: ...
    def reset_filter(self) -> None: ...
    @property
    def active_filter(self) -> Filter:
        """Provide attached Filter, load default first if needed"""


# TASK: define axes
class IndexingRegistry[Item, IndexT: Index | tuple[Index, ...]](
    Registry, Protocol
):
    # LATER: Create Enum members dynamically -> index and length of registry fixed
    """Establish the Registry with Enum and Tuple"""

    items: tuple[Item, ...]
    index: IndexT | tuple[IndexT]


class Index(Enum):  # LATER: move - some unique primitive, or to shape
    """Define countable Axis"""

    def __str__(self) -> str:
        return f"{self.name.capitalize()}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.value}]::{self}"

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> int:
        """Return the index of the Color inside the Palette"""
        return count
