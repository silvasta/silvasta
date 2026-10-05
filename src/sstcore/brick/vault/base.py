"""
ListRegistry - Main Variation of the Core Registry

-
"""

__all__: list[str] = [
    "BaseVault",
]

from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from typing import Any, overload

from ...port.link import portlink
from ...port.raising import SstCoreError
from ...port.register import Register, VaultPolicy
from ..field import PolicyField
from .vault import V2


class RegistryError(SstCoreError): ...


type Vaults = Sequence | Mapping

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


class CoreVault[Item, Vault: Vaults](V2):
    vault: Vault

    @overload
    def __getitem__(self, query: int) -> Item: ...
    @overload
    def __getitem__(
        self, query: slice | Predicate | tuple[Any, ...]
    ) -> Vault: ...
    @overload
    def __getitem__(self, query: str) -> Item: ...
    def __getitem__(self, query: Selector[Item]) -> Item | Vault:
        """Insert Selector and Extract Values from Vault"""
        match query:
            case int() as idx:
                return self._int_get(idx)
            case slice() as slx:
                return self._slice_get(slx)
            case str() as key:
                return self._str_get(key)
            case tuple() as multi_keys:
                return self._tuple_get(multi_keys)
            case fn if callable(fn):
                return self._call_get(fn)
            case _:
                raise TypeError(f"Unsupported: {type(query).__name__}")

    def _int_get(self, idx: int) -> Item:
        return self.vault[idx]

    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    def _slice_get(self, slx: slice) -> Vault:
        return self.vault[slx]

    def _str_get(self, key: str) -> Item:
        for item in self.vault:
            if item[0] == key:
                return item
        raise KeyError(key)

    def _tuple_get(self, multi_keys: tuple) -> Vault:
        """vault["id1", "id2", 0] -> resolves multiple selectors"""
        matched: list[Item] = []
        for sub_key in multi_keys:
            res = self[sub_key]
            if isinstance(res, type(self)):
                matched.extend(res.vault)
            else:
                matched.append(res)
        return self._as_vault(matched)

    def _call_get(self, fn: Predicate[Item]) -> Vault:
        return self._as_vault(item for item in self.vault if fn(item))

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __setitem__(self, query: Selector[Item], value: Any) -> None:
        """Insert Selector and Value to Update the Vault"""
        match query:
            case int() as idx:
                return self._int_set(idx)
            case slice() as slx:
                return self._slice_set(slx)
            case str() as key:
                return self._str_set(key)
            case tuple() as multi_keys:
                return self._tuple_set(multi_keys)
            case fn if callable(fn):
                return self._call_set(fn)
            case _:
                raise TypeError(f"Unsupported: {type(query).__name__}")

    def _int_set(self, idx: int):
        pass

    def _slice_set(self, slx: slice):
        pass

    def _str_set(self, key: str):
        pass

    def _tuple_set(self, multi_keys: tuple):
        """vault["id1", "id2", 0] -> resolves multiple selectors"""

    def _call_set(self, fn: Predicate[Item]):
        pass


@portlink(Register)
class BaseVault[Item, Vault: Vaults](CoreVault, V2):
    """Provide initial Setup"""

    vault: Vault
    _ident: Ident[Item] | None
    policy = PolicyField(VaultPolicy, default=VaultPolicy.RAISE)

    def __init__(
        self,
        initial: Vault | Iterable | Mapping | None = None,
        *,
        ident: Ident[Item] | None = None,
    ) -> None:
        self._ident: Ident[Item] | None = ident
        self.vault = self._as_vault(initial)

    def add(self, data: Item | Vault, override: bool = False) -> Vault:
        """Extend vault by Items, get removed files back"""

        incoming = self._as_vault(data)
        collisions = self._collisions(incoming)
        if override:
            self.vault, displaced = self._subtract(self.vault, collisions)
            self.vault = self._merge(self.vault, incoming)
            return displaced
        fresh, skipped = self._subtract(incoming, collisions)
        self.vault = self._merge(self.vault, fresh)
        return skipped

    def clear(self, query: Selector[Item] | None = None) -> Vault:
        """Remove all Items or remove filtered  by identifier"""
        if query is None:
            displaced, self.vault = self.vault, self._empty()
            return displaced
        displaced = self.find(query)
        self.vault, _ = self._subtract(self.vault, displaced)
        return displaced

    def find(self, query: Selector[Item]) -> Vault:
        """Provide 0..N items that match the item identifier"""
        return self._select(query)

    def count(self, query: Selector[Item]) -> int:
        """How many items match the item identifier?"""
        return len(self.find(query))

    def __len__(self) -> int:
        """How many items are in the vault?"""
        return len(self.vault)

    def __iter__(self) -> Iterator[Any]:
        """Provide value of all items"""
        yield from self.vault

    def __contains__(self, target: Item) -> bool:
        """Is the target item already member?"""
        return any(item == target for item in self.vault)
