"""
Group TypeDefs as Classes and Merge them to Modules

- bundle loose type definitions for the different port modules
- belongs to their corresponding port module, import from there, not from here!

                                                 DependencyLevel[-]
"""  # TODO:

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
    Sequence,
)
from typing import Any, Literal, Never, Protocol, runtime_checkable

#  LINE: -- Port internal views (exposed in port.represent) -- -- - -- -- - --


@runtime_checkable
class _Stringable(Protocol):
    def __str__(self) -> str: ...


type _Stringables = Iterable[_Stringable]


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

    type Bases = tuple[type, ...]
    type NameSpace = dict[str, Any]

    type Proto = type
    type Mixin = type
    type Slot = tuple[Mixin, Proto] | Mixin | Proto  # CHECK: usage?


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

    type List[T] = list[T]
    type Tuple[T] = tuple[T, ...]
    type Seq[T] = Sequence[T]

    type ItrB[T] = Iterable[T]
    type ItrO[T] = Iterator[T]

    type Map[K, T] = Mapping[K, T]
    type Dict[K, T] = dict[K, T]

    type Vault = Sequence | Mapping
    type TypedVault[T] = (
        RegistryTypes.List[T]
        | RegistryTypes.Tuple[T]
        | RegistryTypes.Dict[Any, T]
    )

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class StackTypes(metaclass=_LockedClsMeta):
    """Types for Stacking Pipeline"""

    type Map[ValueT] = Mapping[str, ValueT]
    type StackData[ValueT] = ValueT | Callable[..., ValueT]
    type LayerData[ValueT] = StackTypes.Map[StackTypes.StackData[ValueT]]

    type Accumulated[ValueT] = dict[str, list[ValueT]]


class StubTypes(metaclass=_LockedClsMeta):
    type ProtoType = type
    type AttrName = str
    type RawObject = object
    type PublicMember = tuple[AttrName, RawObject, AttrKind]

    type AttrKind = Literal["property", "method", "attribute"]
    type TypeHints = dict[str, Any]
    type OverLoads = Sequence[Callable[..., Any]]


class EventTypes(metaclass=_LockedClsMeta):
    type Map[Value] = Mapping[str, Value]
    type Tuple[T] = tuple[T, ...]
