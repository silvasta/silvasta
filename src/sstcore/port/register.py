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
    "FilterRegister",
    "FuncRegister",
    "Index",
]

from collections.abc import Callable, Iterator
from enum import Enum, auto

# TODO:
from typing import Any, NoReturn, Protocol, Self, overload

from .attach import LazyDescriptor, PolicyEnum
from .filter import Filter

type Vaults = list | tuple | dict

# NEXT:
# NEXT:
# NEXT:
# NEXT:
# TASK: finish this, especially mixin
# - base
# - dict
# - tuple/list
# - bisec


class Registry[Vault: Vaults, Item, Key](Protocol):
    """Define the Shape of the General Registry"""

    vault: Vault

    def add(self, *items: Item, override: bool = False) -> Vault | Self:
        # TODO: expand for dict to kwargs?
        # TODO: Self?
        """Extend vault by Items, get removed files back"""

    def clear(self, *keys: Key) -> Vault | Self:
        # TODO: Self?
        """Remove all Items or filter removed by Keys"""

    def find(self, *key: Key) -> list[Item]:
        """Provide 0..N items that match the item identifier"""

    def get(self, key: Key) -> Item | NoReturn:
        # TODO: None?
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
        # TODO: NoReturn?
        # TODO: index: str|Key? Any? (then reduce Any in derived?)
        """Get the value or slice of the Item at the index position"""

    def __len__(self) -> int:
        """How many items are in the vault?"""

    def __iter__(self) -> Iterator[Any]:  # here probably special case for dict
        """Provide value of all items"""

    def __contains__(self, target: Item) -> bool:
        """Is the target item already member?"""


class RegistryDescriptor(LazyDescriptor, Protocol):
    """Mount the vault keeper proper to the classes"""

    @classmethod
    # TODO: where to define? how to use best?
    def as_field(cls, *args, **kwargs) -> Self: ...


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Level 1 Mixins
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

### -- Start of potential SequenceRegistry -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

# IDEA: don't create SequenceRegister here as Protocol,
# but SequenceRegistry as implementation base in brick?


class ListRegister[Item, Key](Registry[list, Item, Key], Protocol):
    """Establish the Registry with a List of Items"""

    # TASK: check how much to get parametrized from the base class
    vault: list[Item]

    def add(self, *items: Item, override: bool = False) -> list[Item]: ...
    def clear(self, *keys: Key) -> list[Item]: ...
    def find(self, *key: Key) -> list[Item]: ...

    @overload
    def __getitem__(self, index: slice) -> list[Item]: ...
    @overload
    def __getitem__(self, index: int) -> Item: ...
    # IMPORTANT: same as base class? remove here?
    def __getitem__(self, index: int | slice) -> Item | list[Item]: ...
    def __iter__(self) -> Iterator[Item]: ...


# INFO: overload will later on be removed, just to silence ty now,
# - and to show that the index and slices reg[1:2] hold everywhere


class TupleRegister[Item, Key](Registry[tuple, Item, Key], Protocol):
    """Establish the Registry with Tuples"""

    # TASK: check how much to get parametrized from the base class
    vault: tuple[Item, ...]

    def add(self, *items: Item, override: bool = False) -> Self: ...
    # NEXT: return just tuple? why Self?
    def clear(self, *keys: Key) -> tuple | Self: ...
    def find(self, *key: Key) -> list[Item]: ...

    @overload
    def __getitem__(self, index: slice) -> list[Item]: ...
    @overload
    def __getitem__(self, index: int) -> Item: ...
    def __getitem__(self, index: int | slice) -> Item | list[Item]: ...


class BisectPolicyBase(PolicyEnum):
    """Build Namespace for PolicyDescriptor"""


class InsertPolicy(BisectPolicyBase):
    """
    Dictate behavior for inserting threshold that already exists

    - ALLOW_LEFT: Place new duplicate BEFORE existing ones
    - ALLOW_RIGHT: Place new duplicate AFTER existing ones
    - OVERWRITE: Replace the existing data at the threshold (left)
    - RAISE: Throw ValueError on duplicated insertion
    """  # TODO: explain maybe in implementation

    OVERRIDE = auto()
    RAISE = auto()
    ALLOW_LEFT = auto()  # WARN: check again how to keep this safe
    ALLOW_RIGHT = auto()  # WARN: check again how to keep this safe


class BoundaryPolicy(BisectPolicyBase):
    """
    Dictate mathematical boundaries during lookup

    - INCLUSIVE (>=) bisect_right: Evaluate to its own tier for exact match
    - EXCLUSIVE (>) bisect_left: Fall back to the previous tier for exact match
    """  # TODO: explain maybe in implementation

    INCLUSIVE = auto()
    EXCLUSIVE = auto()


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


class BisectRegister[Item, Key, DTO](Registry[list, Item, Key]):
    # TASK: check how much to get parametrized from the base class
    """Define the Registry with sort-and-read bisect access"""

    vault: list[Item]
    dto: BisectData

    # TASK: define PolicyField here?
    # TODO: insert_policy: InsertPolicy = InsertPolicy.RAISE,
    # TODO: boundary_policy: BoundaryPolicy = BoundaryPolicy.INCLUSIVE,
    # AI_QUESTION: how to announce a descriptor here?


### -- END of potential SequenceRegistry -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class DictRegister[Item, Key](Registry[dict, Item, Key], Protocol):
    """Establish the Registry with a Dict of Items"""

    # TASK: check how much to get parametrized from the base class
    vault: dict[Key, Item]

    def add(self, *_, override: bool = False, **kwargs) -> dict[Key, Item]: ...
    def clear(self, *keys: Key) -> dict[Key, Item]: ...
    def find(self, *key: Key) -> list[Item]: ...

    @overload
    def __getitem__(self, index: slice) -> list[Item]: ...
    @overload
    def __getitem__(self, index: int) -> Item: ...
    # IMPORTANT: same as base class? remove here?
    def __getitem__(self, index: int | slice) -> Item | list[Item]: ...
    def __iter__(self) -> Iterator[tuple[Key, Item]]: ...


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Mixin Extensions
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class MixinRegister[Mixin: type, Key](TupleRegister[Mixin, Key], Protocol):
    """Provide a stable Container for Compositiions"""

    @property
    # IMPORTANT: sorting mechanism
    # TODO: type for return? like the mixed mixin protocols??
    def mixins(self) -> tuple[Mixin, ...]: ...


class FuncRegister[Item: Callable](Protocol):
    # TODO: Functor? (FunctorDecorator?)
    """Extend the Registry for Functions (LATER: and Functors)"""

    def attach(self) -> Callable[[Item], Item]:
        # RENAME: sync with bisect
        """Register new member by Decorator"""


class FilterRegister[Item: Callable](Protocol):
    """Extend the Registry with Filtering"""

    # LATER: this is 1:1 a descriptor mock...
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


class Index(Enum):
    # TASK: move to some data primitives, or to shape? port.base?
    """Define enumerated Axis for {0..N} member with 1 purpose"""

    # IDEA: split view! but how to mix it in then? left or right?
    # AI_QUESTION: SstEnum(Index,_EnumView) or opposite?

    def __str__(self) -> str:
        return f"{self.name.capitalize()}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.value}]::{self}"

    # IDEA: use the int|slice|str __getitem__?? somehow unify this!
    # AI_QUESTION: the idea is to create an Enum with member=auto(),
    # starting from index 0 to N_member-1 and a Enum.name.lower()
    # then use 1 access for all, like a classmethod or even like Enum[MultiKey]
    # something like the resolve_color in the file below, but like universal
    # - defined once and proper in the port, use it everywhere out of the box
    # AI_FOCUS: How to achieve this? 2-3 pieces could build the base of most Enums

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> int:
        """Return the index of the Color inside the Palette"""
        return count


class _IndexRegister[Item, IndexT: Index | tuple[Index, ...]](
    Registry, Protocol
):  # NOTE: not urgent
    """Establish the Registry with Enum and Tuple"""

    items: tuple[Item, ...]  # LATER: define axes
    # LATER: Create Enum members dynamically -> index and length of registry fixed
    index: IndexT | tuple[IndexT]
