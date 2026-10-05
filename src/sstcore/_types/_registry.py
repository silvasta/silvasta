"""
Define and Group the type defs for the Registry

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "Dict",
    "Ident",
    "Index",
    "Key",
    "List",
    "Mixin",
    "Predicate",
    "Proto",
    "Selector",
    "Slot",
    "Tuple",
    "TypedVault",
    "Vault",
]

from collections.abc import Callable as _Callable
from collections.abc import Hashable as _Hashable
from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from collections.abc import Sequence as _Sequence
from typing import Any as _Any

#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type Key = str
type Index = int | slice
type Predicate[T] = _Callable[[T], bool]

type Selector[T] = Key | Index | Predicate[T] | tuple[_Any, ...]

type Ident[Item] = _Callable[[Item], _Hashable]

#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

# INFO: used for parametrized class parametrization

type Seq[T] = _Sequence[T]
type List[T] = list[T]
type Tuple[T] = tuple[T, ...]

type Iter[T] = _Iterable[T]


type Dict[K, T] = dict[K, T]
type Map[K, T] = _Mapping[K, T]


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type Vault = _Sequence | _Mapping
type TypedVault[T] = List[T] | Tuple[T] | Dict[_Any, T]


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


type Proto = type
type Mixin = type
type Slot = tuple[Mixin, Proto] | Mixin | Proto


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --
