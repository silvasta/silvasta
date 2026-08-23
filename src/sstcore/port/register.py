"""
Define the Shape of the Core Registry

- 1 Interface for Any type of Items
 -> Make Data handling independant

"""

__all__: list[str] = [
    # root
    "Registry",
    # bases
    "ListRegister",
    "TupleRegister",
    "DictRegister",
    # extenstions
    "MixinRegister",
    "FilterRegister",
    "FuncRegister",
    # TASK: final name for decorator attaching function registry:
    # - FunctionalRegister
    # - FunctorialRegister
    # - FunctorRegister
    # - CallRegister
    # - CallableRegister
    # - DecoratingRegister
    # - DecoRegister
    #
    "Index",
]

from collections.abc import Callable, Iterable
from enum import Enum
from typing import Any, Protocol, Self

from .filter import Filter


class Registry[Item, Key](Protocol):
    """Define the Shape of the General Registry"""

    items: Any

    def add(self, *args, **kwargs) -> Any:
        """Extend Items directly or with processing"""

    def get(self, key: Key) -> Item | list[Item] | None:
        # IDEA: find and get?? raise?
        """Find {0..N} Items by internal identifier Key"""

    def clear(self, key: Key | None = None) -> Any:
        """Delete the entire content"""

    @property
    def all(self) -> Iterable[Item]:
        """Provide all items one by one"""

    def __len__(self) -> int:
        """How many Items?"""

    def __contains__(self, target: Item) -> bool:
        """Is target already member?"""


class ListRegister[Item, Key](Registry[Item, Key], Protocol):
    """Establish the Registry with a List of Items"""

    items: list[Item]

    def add(self, item: Item, *, override: bool) -> int:
        """Add item, override {0..K} items with same Key"""


class DictRegister[Item, Key](Registry[Item, Key], Protocol):
    """Establish the Registry with a Dict of Items"""

    items: dict[Key, Item]


class TupleRegister[Item: Any, int](Registry[Item, int], Protocol):
    """Establish the Registry with locking Tuples"""

    items: tuple[Item, ...]

    def add(self, items: tuple[tuple[Item, int]], **kwargs) -> Self:
        """Rebuild internal Tuple with Num new Items"""


class MixinRegister[Mixin: type](Registry, Protocol):
    """Establish the Registry with Tuples (of Mixins, at least for now)"""

    mixins: tuple[Mixin, ...]


class FuncRegister[Item: Callable](Protocol):
    """Extend the Registry for Functions (LATER: and Functors)"""

    def attach(self: Registry) -> Callable[[Item], Item]:
        """Register new member by Decorator"""


class FilterRegister[Item: Callable](Protocol):
    """Extend the Registry with Filtering"""

    def filter(self, new_active_filter: Filter | None) -> list[Item]:
        """Provide Items that fulfill the active Filter"""

    def set_filter(self, active_filter: Filter) -> Filter:
        """Set and Get attached Filter"""

    def reset_filter(self) -> Filter | None:
        """Remove attached Filter and provide previous"""

    @property
    def active_filter(self) -> Filter:
        """Provide attached Filter, load default first if needed"""


class Index(Enum):  # LATER: move? some data primitives, or to shape?
    """Define enumerated Axis for {0..N} member with 1 purpose"""

    def __str__(self) -> str:
        return f"{self.name.capitalize()}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.value}]::{self}"

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> int:
        """Return the index of the Color inside the Palette"""
        return count


class _IndexRegister[Item, IndexT: Index | tuple[Index, ...]](
    Registry, Protocol
):
    """Establish the Registry with Enum and Tuple"""

    items: tuple[Item, ...]
    index: IndexT | tuple[IndexT]  # LATER: define axes
    # LATER: Create Enum members dynamically -> index and length of registry fixed
