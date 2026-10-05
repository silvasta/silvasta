"""
Define and Group the type defs for the Registry

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "Ident",
]

from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Mapping,
    Sequence,
)
from typing import Any

type Ident[Item] = Callable[[Item], Hashable]

type List[T] = list[T]
type Tuple[T] = tuple[T, ...]
type Dict[K, T] = dict[K, T]

type Vault1 = Sequence | Mapping
type Vault2[T] = List[T] | Tuple[T] | Dict[Any, T]

type Key = str
type Index = int | slice
type Predicate[T] = Callable[[T], bool]
type Selector[T] = Key | Index | Predicate[T] | tuple[Any, ...]
type Ident[Item] = Callable[[Item], Hashable]

type Vault = Sequence | Mapping
type Vaults = Sequence | Mapping
type Selector[A] = A | Iterable[A]

type List[T] = list[T]
type Tuple[T] = tuple[T, ...]
type Dict[K, T] = dict[K, T]

type Vault1 = Sequence | Mapping
type Vault2[T] = List[T] | Tuple[T] | Dict[Any, T]

type Key = str
type Index = int | slice
type Predicate[T] = Callable[[T], bool]
type Selector[T] = Key | Index | Predicate[T] | tuple[Any, ...]
type Ident[Item] = Callable[[Item], Hashable]

type Proto = type
type Mixin = type

type Slot = tuple[Mixin, Proto] | Mixin | Proto
type Vaults = Sequence | Mapping
