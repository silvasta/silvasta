"""
Define the Shape of the Core Register

- 1 Interface for Any type of Vaults -> enable independent data handling

                                    DependencyLevel.sstcore.port[5]
"""

__all__: list[str] = [
    # root
    "Register",
    # bases
    "ListRegister",
    "TupleRegister",
    "DictRegister",
    # extenstions
    "MixinRegister",
    "FuncRegister",
    ## bisect
    "BisectRegister",
    "BoundaryPolicy",
    "InsertPolicy",
    "BisectDTO",
    #
    "registry_types",
]

from collections.abc import Callable, Iterator
from enum import auto
from typing import Any, Protocol, Self, overload

from .._types import _registry as registry_types
from .attach import LazyDescriptor, PolicyDescriptor  # 3
from .filter import Filter  # 4
from .solid import EnumIndex, PolicyEnum  # 1

_reg = registry_types


class Register[Item, Vault: _reg.Vault](Protocol):
    """Define the Shape of the General Register"""

    vault: Vault

    policy: PolicyDescriptor[VaultPolicy]
    ident: _reg.Ident[Item] | None

    def add(self, data: Item | Vault) -> Vault:
        """Extend vault by Items, get removed files back"""

    def clear(self, query: _reg.Selector[Item] | None = None) -> Vault:
        """Remove all Items or remove filtered  by identifier"""

    def find(self, query: _reg.Selector[Item]) -> Vault:
        """Provide 0..N items that match the item identifier"""

    def count(self, query: _reg.Selector[Item]) -> int:
        """How many items match the item identifier?"""

    @overload
    def __getitem__(self, query: int) -> Item: ...
    @overload
    def __getitem__(
        self, query: slice | _reg.Predicate | tuple[Any, ...]
    ) -> Vault: ...
    @overload
    def __getitem__(self, query: str) -> Item: ...
    def __getitem__(self, query: _reg.Selector[Item]) -> Item | Vault:
        """Insert Selector and Extract Values from Vault"""

    def __setitem__(self, query: _reg.Selector[Item], value: Any):
        """Insert Selector and Value to Update the Vault"""

    def __len__(self) -> int:
        """How many items are in the vault?"""

    def __iter__(self) -> Iterator[Any]:
        """Provide value of all items"""

    def __contains__(self, target: Item) -> bool:
        """Is the target item already member?"""


class VaultPolicy(PolicyEnum):
    """On Conflic Strategy - Index and Default start on Zero"""

    RAISE = auto()
    SKIP = auto()
    MERGE = auto()


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Level 1 Mixins
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class ListRegister[Item](Register[Item, _reg.List[Item]], Protocol):
    """Establish the Register with a List of Items"""


class TupleRegister[Item](Register[Item, _reg.Tuple[Item]], Protocol):
    """Establish the Register with Tuples"""


class DictRegister[Item, K](Register[Item, _reg.Dict[K, Item]], Protocol):
    """Establish the Register with a Dict of Items"""


#  LINE: -- Extensions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class MixinRegister[S: _reg.Slot](TupleRegister[_reg.Mixin], Protocol):
    # TODO: check in forge.compose.SLOT
    """Provide a stable Container for Compositiions"""

    @property
    def mixins(self) -> tuple[S, ...]: ...


class RegisterDescriptor(LazyDescriptor, Protocol):
    @classmethod
    def as_field(cls, *args, **kwargs) -> Self:
        """Mount the vault keeper proper to the classes"""


class FuncRegister[Item: Callable](Protocol):
    """Extend the Register for Functions (LATER: and Functors)"""

    # RENAME: check conflicts with with fields and bisect register
    def attach(self) -> Callable[[Item], Item]:
        """Register new member by Decorator"""


#  LINE: -- ongoing bisect project -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class BisectRegister[Item, DTO: BisectDTO](
    Register[Item, _reg.List[Item]], Protocol
):
    """Define the Register with sort-and-read bisect access"""

    dto: DTO


class BisectDTO[ThreshT: int | float](Protocol):
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


#  LINE: -- Experiments -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _IndexRegister[Item, Axes: tuple[EnumIndex, ...]](Protocol):
    # TASK: colorgrid!!
    """Build the ultimate robust and stable container"""

    axes: Axes

    @property
    def n_axes(self) -> int: ...


class _FilterRegister[Item: Callable](Protocol):
    """Extend the Register with Filtering"""

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

    """Establish the Register with Enum and Tuple"""
