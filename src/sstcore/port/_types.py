"""
Group TypeDefs as Classes and Merge them to Modules

- bundle loose type definitions for the different port modules
- belongs to their corresponding port module, import from there, not from here!

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "RegistryTypes",
    "StackTypes",
    "StubTypes",
    "EventTypes",
]

from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Sequence,
)
from typing import Any, ClassVar, Literal, Never, Protocol, runtime_checkable

from .empty import VOID, MayBe


@runtime_checkable
class _Stringable(Protocol):
    def __str__(self) -> str: ...


type _Stringables = Iterable[_Stringable]


class _DataClass(Protocol):
    """Define the minimal Shape for typing a DataClass"""

    __dataclass_fields__: ClassVar[dict[str, Any]]


type DataClassOrType = _DataClass | type[_DataClass]


@runtime_checkable
class _LogStringable(Protocol):
    def __repr__(self) -> str:
        """Concate the Event info directly into a (usually very) long String"""


@runtime_checkable
class _RichView(Protocol):
    def __rich__(self): ...


@runtime_checkable
class _RichConsolable(Protocol):
    def __rich_console__(self, console, options):
        """Just extend the Renderable type"""


#  LINE: -- Locking -- -- - -- -- - -- -- - --


class _LockedClsMeta(type):
    """Disable Mutation and Instantiation for NameSpace Only Classes"""

    _name: str = "Locked"

    def _show(cls, name: str = "") -> str:
        return f"{cls._name}[{cls.__name__}{f'.{name}' if name else ''}]"

    def __call__(cls, *_, **__) -> Never:
        raise TypeError(f"{cls._show()} is Not available as Instance!")

    def __setattr__(cls, name: str, _value: Any) -> Never:
        raise AttributeError(f"{cls._show(name)} is read-only")

    def __delattr__(cls, name: str) -> Never:
        raise AttributeError(f"{cls._show(name)} cannot be deleted")


#  LINE: -- Collected Definitions of: type ... = ... -- -- - -- -- - -- -- - --


class Types(metaclass=_LockedClsMeta):
    """Collect Types.. for Types: Meta, Mixin, Composit Stuff"""

    type Bases[Unit: Any] = tuple[type[Unit], ...]
    type Errors[E: BaseException = Exception] = tuple[type[E], ...]
    type NameSpace = dict[str, Any]

    type Proto = type
    type Mixin = type
    type Slot = tuple[Mixin, Proto] | Mixin | Proto  # CHECK: usage?

    type Tuple[T: Any = Any] = tuple[T, ...]
    type Dict[K, V] = dict[K, V]
    type StrDict[T: Any = Any] = dict[str, T]
    type Map[K, V] = Mapping[K, V]
    type StrMap[V: Any = Any] = Mapping[str, V]
    type Seq[T] = Sequence[T]

    type _Intersect[T, S] = type[T & S]  # ty:ignore
    type _NoIntersect[T, S] = type[T]


# NEXT: KeyView for (Mapping)[str,Any]??


class RegistryTypes(metaclass=_LockedClsMeta):
    """
    Collect all Types for the Registry:

    - Definition: port.register
    - Production: brick.vault
    - Manufacture: forge.registry (not already exists)
    """

    type Key = str
    type Index = int | slice
    type Selector[T] = (
        RegistryTypes.Key
        | RegistryTypes.Index
        | RegistryTypes.Predicate[T]
        | tuple[Any, ...]
        | Hashable
    )
    type Predicate[T] = Callable[[T], bool]
    type Ident[Item] = Callable[[Item], Hashable]

    # INFO: used for parametrized class parametrization

    type List[T] = list[T]  # REMOVE: why?
    type Tuple[T] = tuple[T, ...]  # CHECK:

    type ItrB[T] = Iterable[T]
    type ItrO[T] = Iterator[T]

    type Map[K, T] = Mapping[K, T]  # CHECK: where used
    type Dict[K, T] = dict[K, T]  # CHECK: defaults, overlap

    type Vault = Sequence | Mapping
    type TypedVault[T] = (
        RegistryTypes.List[T]
        | RegistryTypes.Tuple[T]
        | RegistryTypes.Dict[Any, T]
    )


class StackTypes(metaclass=_LockedClsMeta):
    """Types for Stacking Pipeline"""

    type Map[ValueT] = Mapping[str, ValueT]  # CHECK: overlap
    type StackData[ValueT] = ValueT | Callable[..., ValueT]
    type LayerData[ValueT] = StackTypes.Map[StackTypes.StackData[ValueT]]

    type Accumulated[ValueT] = dict[str, list[ValueT]]


class StubTypes(metaclass=_LockedClsMeta):
    type ProtoType = type  # CHECK: overlap
    type AttrName = str
    type RawObject = object
    type PublicMember = tuple[AttrName, RawObject, AttrKind]

    type AttrKind = Literal["property", "method", "attribute"]
    type TypeHints = dict[str, Any]
    type OverLoads = Sequence[Callable[..., Any]]


class _CliSerial(Protocol):
    def __cli__(self):
        """Ignore the CliDTO_covariant return value"""


class EventTypes(metaclass=_LockedClsMeta):
    type Map[Value] = Mapping[str, Value]
    type Tuple[T] = tuple[T, ...]
    type StrDict[V = Any] = dict[str, V]

    type CliSpec = _CliSerial | _RichView | str

    type Content[Value: CliSpec | Tuple[CliSpec]] = EventTypes.Tuple[Value]
    type Vec = Content[CliSpec]
    type Grid = tuple[tuple[CliSpec, ...], ...]


@runtime_checkable
class _ArgCasting[T = Any](Protocol):
    """Cast, Coerce, Resolve and/or Validate Function Input"""

    def __call__(self, target: Any, /, *, default: MayBe[T] = VOID) -> T:
        """Validate Target in ArgCast-Pipeline"""


class CallingTypes(metaclass=_LockedClsMeta):
    type CastPlan = dict[str, _ArgCasting]
    type CastRegistry = dict[Any, _ArgCasting]
    type Castable = Callable[..., Any] | type[Any]
    type Data = MutableMapping[str, Any]
