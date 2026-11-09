"""
Define the Shape of the Core Register

- 1 Interface for Any type of Vaults -> enable independent data handling

                                    DependencyLevel.sstcore.port[2]
"""

__all__: list[str] = [
    # root
    "Register",
    # bases
    "ListRegister",
    "TupleRegister",
    "DictRegister",
    # extensions
    "MixinRegister",
    "FuncRegister",
    ## bisect
    "BisectRegister",
    "BoundaryPolicy",
    "InsertPolicy",
    "BisectDTO",
    #
    "RegistryTypes",
]

import typing as _t
from collections.abc import Callable, Iterator
from enum import auto
from typing import Any, Protocol, overload

from ._types import RegistryTypes
from ._types import Types as _T  # noqa:N814
from .solid import PolicyEnum  # 1

_RT = RegistryTypes


class Register[Item, Vault: _RT.Vault](Protocol):
    """Define the Shape of the General Register"""

    vault: Vault
    policy: VaultPolicy
    ident: _RT.Ident[Item]

    def add(self, data: Item | Vault) -> Vault:
        """Extend vault by Items, get removed files back"""

    def clear(self, query: _RT.Selector[Item] | None = None) -> Vault:
        """Remove all Items or remove filtered  by identifier"""

    def find(self, query: _RT.Selector[Item]) -> Vault:
        """Provide 0..N items that match the item identifier"""

    def count(self, query: _RT.Selector[Item]) -> int:
        """How many items match the item identifier?"""

    @overload
    def __getitem__(self, query: int) -> Item: ...
    @overload
    def __getitem__(
        self, query: slice | _RT.Predicate | tuple[_t.Any, ...]
    ) -> Vault: ...
    @overload
    def __getitem__(self, query: str) -> Item: ...
    def __getitem__(self, query: _RT.Selector[Item]) -> Item | Vault:
        """Insert Selector and Extract Values from Vault"""

    def __setitem__(self, query: _RT.Selector[Item], value: Any):
        """Insert Selector and Value to Update the Vault"""

    def __len__(self) -> int:
        """How many items are in the vault?"""

    def __iter__(self) -> Iterator[Any]:
        """Provide value of all items"""

    def __contains__(self, target: Item) -> bool:
        """Is the target item already member?"""


class VaultPolicy(PolicyEnum):
    """On Conflict Strategy - Index and Default start on Zero"""

    RAISE = auto()
    SKIP = auto()
    MERGE = auto()


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Level 1 Mixins
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class ListRegister[Item](Register[Item, _RT.List[Item]], Protocol):
    """Establish the Register with a List of Items"""


class TupleRegister[Item](Register[Item, _RT.Tuple[Item]], Protocol):
    """Establish the Register with Tuples"""


class DictRegister[Item, K](Register[Item, _RT.Dict[K, Item]], Protocol):
    """Establish the Register with a Dict of Items"""


#  LINE: -- Extensions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class FuncRegister[Item: Callable](Protocol):
    """Extend the Register for Functions (LATER: and Functors)"""

    # AI: so far no specific implementation, just the ErrorRegistry

    def attach(self) -> Callable[[Item], Item]:
        """Register new member by Decorator"""


class MixinRegister[S: _T.Slot](TupleRegister[_T.Mixin], Protocol):
    """Provide a stable Container for Compositiions"""

    # TODO: check forge.compose.SLOT

    @property
    def mixins(self) -> tuple[S, ...]: ...


#  LINE: -- ongoing bisect project -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class BisectRegister[Item, DTO: BisectDTO](
    Register[Item, _RT.List[Item]], Protocol
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

    - INCLUSIVE (>=) bisect_RTight: Evaluate to its own tier for exact match
    - EXCLUSIVE (>) bisect_left: Fall back to the previous tier for exact match
    """

    INCLUSIVE = auto()
    EXCLUSIVE = auto()
