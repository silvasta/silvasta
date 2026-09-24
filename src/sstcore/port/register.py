"""
Define the Shape of the Core Registry

- 1 Interface for Any type of Vaults -> enable independent data handling

                                                 DependencyLevel[2]
                                                        - filter(1)
"""

__all__: list[str] = [
    # root
    "Registry",
    # bases
    "ListRegister",
    "TupleRegister",
    "DictRegister",
    ## bisect
    "BoundaryPolicy",
    "InsertPolicy",
    "BisectRegister",
    # extenstions
    "MixinRegister",
    "FuncRegister",
]

from collections.abc import Callable, Iterator, Mapping, Sequence
from enum import auto
from typing import Any, NoReturn, Protocol, Self, overload

from .attach import LazyDescriptor, PolicyEnum
from .filter import Filter
from .govern import Index

# NEXT:
type _Vaults = list | tuple | dict
type Vaults = Sequence | Mapping


class Registry[Item, Vault: Vaults, U, A: Any](Protocol):
    """Define the Shape of the General Registry"""

    vault: Vault

    def add(self, items: Vault, override: bool = False) -> Vault:
        """Extend vault by Items, get removed files back"""

    def clear(self, id: A | None = None) -> Vault:
        """Remove all Items or remove filtered  by identifier"""

    def find(self, id: A) -> Vault:
        """Provide 0..N items that match the item identifier"""

    def count(self, key: A) -> int:
        """How many items match the item identifier?"""

    @overload
    def __getitem__(self, index: A) -> list[Item]: ...
    @overload
    def __getitem__(self, index: U) -> Item: ...
    def __getitem__(
        self, index: int | slice | str | tuple | Callable
    ) -> Item | list[Item] | NoReturn:
        """Get the value or slice of the Item at the index position"""

    def __len__(self) -> int:
        """How many items are in the vault?"""

    def __iter__(self) -> Iterator[Any]:
        """Provide value of all items"""

    def __contains__(self, target: Item) -> bool:
        """Is the target item already member?"""

    @classmethod
    def as_field(cls, *args, **kwargs) -> RegistryDescriptor: ...


class RegistryDescriptor(LazyDescriptor, Protocol):
    @classmethod
    def as_field(cls, *args, **kwargs) -> Self:
        """Mount the vault keeper proper to the classes"""


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Level 1 Mixins
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class ListRegister[Item, A](Registry[Item, list, int, A], Protocol):
    """Establish the Registry with a List of Items"""


class TupleRegister[Item, A](Registry[Item, list, int, A], Protocol):
    """Establish the Registry with Tuples"""


class DictRegister[Item, K, A](Registry[Item, dict, K, A], Protocol):
    """Establish the Registry with a Dict of Items"""

    vault: dict[K, Item]


class BisectRegister[Item, DTO: BisectData](
    Registry[Item, list, int, None]  # CHECK: value for A??
):
    """Define the Registry with sort-and-read bisect access"""

    dto: DTO  # CHECK:


class BisectData[ThreshT: int | float](Protocol):
    """Define the Shape of the BisectDTOs"""

    @property
    def threshold(self) -> ThreshT:
        """The value for the sorting"""

    @property
    def label(self) -> str:
        """Present the Item in 1 sentence"""

    def key(self) -> ThreshT:
        """Extract the sorting value from the Self-DTO"""


class BisectPolicyBase(PolicyEnum):
    """Build Namespace for PolicyDescriptor"""


class InsertPolicy(BisectPolicyBase):
    # TODO: explain maybe in implementation
    """
    Dictate behavior for inserting threshold that already exists

    - ALLOW_LEFT: Place new duplicate BEFORE existing ones
    - ALLOW_RIGHT: Place new duplicate AFTER existing ones
    - OVERWRITE: Replace the existing data at the threshold (left)
    - RAISE: Throw ValueError on duplicated insertion
    """

    OVERRIDE = auto()
    RAISE = auto()
    ALLOW_LEFT = auto()
    # WARN: check again how to keep this safe
    ALLOW_RIGHT = auto()


class BoundaryPolicy(BisectPolicyBase):
    # TODO: explain maybe in implementation
    """
    Dictate mathematical boundaries during lookup

    - INCLUSIVE (>=) bisect_right: Evaluate to its own tier for exact match
    - EXCLUSIVE (>) bisect_left: Fall back to the previous tier for exact match
    """

    INCLUSIVE = auto()
    EXCLUSIVE = auto()


#  LINE: -- Mixin Extensions -- -- - -- -- - -- -- - -- -- - -- -- - -- --

type Proto = type
type Mixin = type

type Slot = tuple[Mixin, Proto] | Mixin | Proto


class MixinRegister[S: Slot](TupleRegister[Mixin, None], Protocol):
    # TODO: check in forge.compose.SLOT
    """Provide a stable Container for Compositiions"""

    @property
    def mixins(self) -> tuple[S, ...]: ...


class FuncRegister[Item: Callable](Protocol):
    """Extend the Registry for Functions (LATER: and Functors)"""

    # NEXT: check with fields/attach
    def attach(self) -> Callable[[Item], Item]:  # RENAME: sync with bisect
        """Register new member by Decorator"""


class _IndexRegister[Item, Axes: tuple[Index, ...]](
    Registry[Item, tuple, Axes, None], Protocol
):  # TODO: find proper setup
    """Build the ultimate robust and stable container"""

    axes: Axes

    @property
    def n_axes(self) -> int: ...


class _FilterRegister[Item: Callable](Protocol):
    """Extend the Registry with Filtering"""

    # TODO: build FilterField
    # TASK: this is 1:1 a descriptor mock...
    # - find the proper descriptor for filters and remove this

    def filter(self, new_active_filter: Filter | None) -> list[Item]:
        """Provide Items that fulfill the active Filter"""

    def set_filter(self, active_filter: Filter) -> Filter:
        """Set and Get attached Filter"""

    def reset_filter(self) -> Filter | None:
        """Remove attached Filter and provide previous"""

    @property
    def active_filter(self) -> Filter:
        """Provide attached Filter, load default first if needed"""

    """Establish the Registry with Enum and Tuple"""
