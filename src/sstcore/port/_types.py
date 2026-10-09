"""
Group TypeDefs as Classes and Merge them to Modules

- bundle loose type definitions for the different port modules
- belongs to their corresponding port module, import from there, not from here!

                                                 DependencyLevel[-]
"""

__all__: list[str] = [
    "Registry",
    "registry_types",
]

from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from typing import Any


class Registry:
    """
    Collect all Types for the Registry:

    - Definition: port.register
    - Production: brick.vault
    - Manufactur: forge.registry (not already exists)
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
