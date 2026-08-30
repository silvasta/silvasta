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
    "Index",
]

from collections.abc import Callable, Iterator
from enum import Enum
from typing import Any, NoReturn, Protocol, Self, overload

from .attach import LazyDescriptor
from .filter import Filter

type Basic = list | tuple | dict


class Registry[Base: Basic, Item, Key](Protocol):
    """Define the Shape of the General Registry"""

    vault: Base

    # NOTE: expand for dict to kwargs
    def add(self, *items: Item, override: bool = False) -> Base | Self:
        """Extend vault by Items, get removed files back"""

    def clear(self, *keys: Key) -> Base | Self:
        """Remove all Items or filter removed by Keys"""

    def find(self, *key: Key) -> list[Item]:
        """Provide 0..N items that match the item identifier"""

    def get(self, key: Key) -> Item | NoReturn:
        """Find precisely the unique Item to the Key"""

    def count(self, *key: Key) -> int:
        """How many items match the item identifier?"""

    @classmethod
    def as_field(cls, *args, **kwargs) -> RegistryDescriptor: ...

    @overload
    def __getitem__(self, index: slice) -> list[Item]: ...
    @overload
    def __getitem__(self, index: int) -> Item: ...
    def __getitem__(self, index: int | slice) -> Item | list[Item]:
        """Get the value or slice of the Item at the index position"""

    def __len__(self) -> int:
        """How many items are in the vault?"""

    def __iter__(self) -> Iterator[Any]:  # here probably special case for dict
        """Provide value of all items"""

    def __contains__(self, target: Item) -> bool:
        # AI: here i am unsure, any other idea what to allow here?
        # - one idea was to open it widely with a huge dispatch,
        # - but it looked too time consuming for too less gain...
        """Is the target item already member?"""


class RegistryDescriptor(LazyDescriptor, Protocol):
    """Mount the vault keeper proper to the classes"""

    @classmethod
    def as_field(cls, *args, **kwargs) -> Self: ...


class ListRegister[Item, Key](Registry[list, Item, Key], Protocol):
    """Establish the Registry with a List of Items"""

    vault: list[Item]

    def add(self, *items: Item, override: bool = False) -> list[Item]: ...
    def clear(self, *keys: Key) -> list[Item]: ...
    def find(self, *key: Key) -> list[Item]: ...

    @overload
    def __getitem__(self, index: slice) -> list[Item]: ...
    @overload
    def __getitem__(self, index: int) -> Item: ...
    def __getitem__(self, index: int | slice) -> Item | list[Item]: ...
    def __iter__(self) -> Iterator[Item]: ...


# NOTE: overload will later on be removed, just to silence ty now,
# - and to show that the index and slices reg[1:2] hold everywhere


class DictRegister[Item, Key](Registry[dict, Item, Key], Protocol):
    """Establish the Registry with a Dict of Items"""

    vault: dict[Key, Item]

    def add(self, *_, override: bool = False, **kwargs) -> dict[Key, Item]: ...
    def clear(self, *keys: Key) -> dict[Key, Item]: ...
    def find(self, *key: Key) -> list[Item]: ...

    @overload
    def __getitem__(self, index: slice) -> list[Item]: ...
    @overload
    def __getitem__(self, index: int) -> Item: ...
    def __getitem__(self, index: int | slice) -> Item | list[Item]: ...
    def __iter__(self) -> Iterator[tuple[Key, Item]]: ...


class TupleRegister[Item, Key](Registry[tuple, Item, Key], Protocol):
    """Establish the Registry with Tuples"""

    vault: tuple[Item, ...]

    # TODO: returning new tuple or manipulate directly on registry?
    def add(self, *items: Item, override: bool = False) -> Self: ...
    def clear(self, *keys: Key) -> tuple | Self: ...
    def find(self, *key: Key) -> list[Item]: ...

    @overload
    def __getitem__(self, index: slice) -> list[Item]: ...
    @overload
    def __getitem__(self, index: int) -> Item: ...
    def __getitem__(self, index: int | slice) -> Item | list[Item]: ...


class MixinRegister[Mixin: type, Key](TupleRegister[Mixin, Key], Protocol):
    """Provide a stable Container for Compositiions"""

    @property
    # IMPORTANT: sorting mechanism
    def mixins(self) -> tuple[Mixin, ...]: ...


class FuncRegister[Item: Callable](Protocol):
    """Extend the Registry for Functions (LATER: and Functors)"""

    def attach(self) -> Callable[[Item], Item]:
        """Register new member by Decorator"""


class FilterRegister[Item: Callable](Protocol):
    """Extend the Registry with Filtering"""

    # LATER: this is 1:1 a descriptor mock...

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
