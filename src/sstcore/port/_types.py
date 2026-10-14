"""
Group TypeDefs as Classes and Merge them to Modules

- bundle loose type definitions for the different port modules
- belongs to their corresponding port module, import from there, not from here!

                                                 DependencyLevel[-]
"""

__all__: list[str] = [
    "Registry",
    "registry_types",
    "Stack",
    "stacking_types",
    "Stub",
    "stub_types",
]

from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from typing import Any, Literal, Protocol, runtime_checkable

#  LINE: -- Port internal views (exposed in port.represent) -- -- - -- -- - --


@runtime_checkable
class _Stringable(Protocol):
    def __str__(self) -> str: ...


@runtime_checkable
class _LogStringable(Protocol):
    def __repr__(self) -> str:
        """Concate the Event info directly into a (usually very) long String"""


@runtime_checkable
class _RichView(Protocol):
    def __rich__(self): ...


@runtime_checkable
class _RichConsolable(Protocol):
    def __rich_console__(self):
        """Just extend the Renderable type"""


_Richable = _RichView | _RichConsolable | str

#  LINE: -- Collected Definitions of: type ... = ... -- -- - -- -- - -- -- - --


class Registry:
    """
    Collect all Types for the Registry:

    - Definition: port.register
    - Production: brick.vault
    - Manufacture: forge.registry (not already exists)
    """

    type Key = str
    type Index = int | slice
    type Selector[T] = (
        Registry.Key | Registry.Index | Registry.Predicate[T] | tuple[Any, ...]
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
        Registry.List[T] | Registry.Tuple[T] | Registry.Dict[Any, T]
    )

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    type Proto = type
    type Mixin = type
    type Slot = tuple[Mixin, Proto] | Mixin | Proto


registry_types = Registry()


class Stack:
    """Types for Stacking Pipeline"""

    type Map[ValueT] = Mapping[str, ValueT]
    type StackData[ValueT] = ValueT | Callable[..., ValueT]
    type LayerData[ValueT] = Stack.Map[Stack.StackData[ValueT]]

    type Accumulated[ValueT] = dict[str, list[ValueT]]


stacking_types = Stack()


class Stub:
    type ProtoType = type
    type AttrName = str
    type RawObject = object
    type PublicMember = tuple[AttrName, RawObject, AttrKind]

    type AttrKind = Literal["property", "method", "attribute"]
    type TypeHints = dict[str, Any]
    type OverLoads = Sequence[Callable[..., Any]]


stub_types = Stub()
