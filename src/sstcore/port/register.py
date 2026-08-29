"""
Define the Shape of the Core Registry

- 1 Interface for Any type of Items
 -> Make Data handling independant

"""

from functools import partial

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

from collections.abc import Callable, Iterator
from enum import Enum
from typing import Any, Protocol, Self, overload

from .filter import Filter


class Registry[Item, Key](Protocol):
    """Define the Shape of the General Registry"""

    items: Any

    def add(self, *args, **kwargs) -> Any:
        """Extend items directly or with processing"""

    def clear(self, key: Key | None = None) -> list[Item]:
        """Reset and provide content that match the item identifier"""

    def find(self, key: Key) -> list[Item]:
        """Provide 0..N items that match the item identifier"""

    def count(self, key: Key) -> int:
        """How many items match the item identifier?"""

    @overload
    def __getitem__(self, index: slice) -> list[Item]: ...
    @overload
    def __getitem__(self, index: int) -> Item: ...
    def __getitem__(self, index: int | slice) -> Item | list[Item]:
        """Get the value or slice of the Item at the target position"""

    def __len__(self) -> int:
        """How many items are in the vault?"""

    def __iter__(self) -> Iterator[Item]:
        """Provide value of all items"""

    def __contains__(self, target: Item) -> bool:
        """Is the target item already member?"""

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    # TODO:
    # def __call__(self):
    #     """No idea for what but I know that I want to use it for something..."""
    # TODO: use like this?
    # @classmethod
    # def as_field(cls, *args, **kwargs) -> RegistryField:
    #     return RegistryField(cls, *args, **kwargs)


type RegistryLoader = Callable[[], Registry]


class RegistryField:
    # MOVE:
    def __init__(self, registry: type[Registry], *args, **kwargs):
        self.loader: RegistryLoader = partial(registry, *args, **kwargs)

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if not hasattr(instance, self.private_name):
            setattr(instance, self.private_name, self.loader())

        return getattr(instance, self.private_name)


# TODO: check with update in base above
# TODO: check with update in base above
# TODO: check with update in base above
# TODO: check with update in base above


class ListRegister[Item, Key](Registry[Item, Key], Protocol):
    """Establish the Registry with a List of Items"""

    items: list[Item]

    def add(self, *items: Item, override: bool) -> list[Item]:
        """Add item, override {0..K} items with same Key"""


class DictRegister[Item, Key](Registry[Item, Key], Protocol):
    """Establish the Registry with a Dict of Items"""

    items: dict[Key, Item]


class TupleRegister[Item: Any, int](Registry[Item, int], Protocol):
    """Establish the Registry with Tuples"""

    items: tuple[Item, ...]

    def add(self, items: tuple[tuple[Item, int]], **kwargs) -> Self:
        """Rebuild internal Tuple with new Items"""


class MixinRegister[Mixin: type](TupleRegister, Protocol):
    """Provide a stable Container for Compositiions"""

    # IMPORTANT: sorting

    @property
    def mixins(self) -> tuple[Mixin, ...]: ...


class FuncRegister[Item: Callable](Protocol):
    """Extend the Registry for Functions (LATER: and Functors)"""

    def attach(self: Registry) -> Callable[[Item], Item]:
        """Register new member by Decorator"""


class FilterRegister[Item: Callable](Protocol):
    """Extend the Registry with Filtering"""

    # NEXT: this is 1:1 a descriptor task...

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
