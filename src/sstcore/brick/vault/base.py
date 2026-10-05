"""
ListRegistry - Main Variation of the Core Registry

-
"""

__all__: list[str] = [
    "InitialVault",
    "BaseVault",
    "VaultCore",
]

from collections.abc import Iterable, Iterator, Mapping
from typing import Any, overload

from ...brick.field import StrategyField
from ...port.link import portlink
from ...port.register import Register, VaultPolicy
from ...port.register import registry_types as _reg
from ..field import PolicyField


class InitialVault[Item, V: _reg.Vault]:
    """Define and Ensure the needed Tasks"""

    vault: V

    def _empty(self) -> V:
        raise NotImplementedError

    def _as_vault(self, items: Item | V | Any, /) -> V:
        raise NotImplementedError

    def _merge(self, vault: V, incoming: V) -> V:
        raise NotImplementedError

    def _subtract(self, vault: V, targets: V) -> tuple[V, V]:
        raise NotImplementedError

    def _collisions(self, incoming: V) -> V:
        raise NotImplementedError

    def _at(self, uid) -> Item | None:
        raise NotImplementedError

    def _select(self, id) -> V:
        raise NotImplementedError

    def _slice(self, s: slice) -> V:
        raise ValueError(f"Slicing not supported: {s!r}", s)


class VaultCore[Item, V: _reg.Vault](InitialVault[Item, V]):
    """Keep the powerful tool of the Vault[**]"""

    @overload
    def __getitem__(self, query: int) -> Item: ...
    @overload
    def __getitem__(
        self, query: slice | _reg.Predicate | tuple[Any, ...]
    ) -> V: ...
    @overload
    def __getitem__(self, query: str) -> Item: ...

    def __getitem__(self, query: _reg.Selector[Item]) -> Item | V:
        """Insert Selector and Extract Values from V"""
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
        # TODO: modify self._at without None and strict?
        return self.vault[idx]

    def _slice_get(self, slx: slice) -> V:
        return self._slice(slx)

    def _str_get(self, key: str) -> Item:
        # TODO: this lookss somehow pointless...
        for item in self.vault:
            if item[0] == key:
                return item
        raise KeyError(key)

    def _tuple_get(self, multi_keys: tuple) -> V:
        """vault["id1", "id2", 0] -> resolves multiple selectors"""
        matched: list[Item] = []
        for sub_key in multi_keys:
            res = self[sub_key]
            if isinstance(res, type(self)):
                matched.extend(res.vault)
            else:
                matched.append(res)
        return self._as_vault(matched)

    def _call_get(self, fn: _reg.Predicate[Item]) -> V:
        return self._as_vault(item for item in self.vault if fn(item))

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    # IDEA: GetVault and SetVault? provide 2 mixins for either the same setup or only read
    # - maybe with share match_query function?

    def __setitem__(self, query: _reg.Selector[Item], value: Any) -> None:
        """Insert Selector and Value to Update the V"""
        match query:
            case int() as idx:
                return self._int_set(idx, value)
            case slice() as slx:
                return self._slice_set(slx, value)
            case str() as key:
                return self._str_set(key, value)
            case tuple() as multi_keys:
                return self._tuple_set(multi_keys, value)
            case fn if callable(fn):
                return self._call_set(fn, value)
            case _:
                raise TypeError(f"Unsupported: {type(query).__name__}")

    def _int_set(self, idx: int, value: Any):
        self.vault[idx] = self._normalize(value)

    def _slice_set(self, slx: slice, value: Any):
        self.vault[slx] = [self._normalize(v) for v in value]

    def _str_set(self, key: str, value: Any):
        # TODO:
        norm_val: Item = self._normalize(value)
        for idx, (existing_k, _) in enumerate(self.vault):
            if existing_k == key:
                self.vault[idx] = norm_val
                return
        self.vault.append(norm_val)

    def _tuple_set(self, multi_keys: tuple, value: Any):
        """vault["id1", "id2", 0] -> resolves multiple selectors"""
        values = list(value)
        if len(multi_keys) != len(values):
            raise ValueError(
                f"Cannot unpack {len(values)} values into {len(multi_keys)} selectors"
            )
        for sub_key, sub_val in zip(multi_keys, values, strict=True):
            self[sub_key] = sub_val

    def _call_set(self, fn: _reg.Predicate[Item], value: Any):
        for idx, item in enumerate(self.vault):
            if fn(item):
                # IMPORTANT: dispatch str|int by Mapping|Sequence
                if callable(value):
                    self._items[idx] = self._normalize_item(value(item))
                else:
                    self._items[idx] = self._normalize_item(value)

    def _normalize(self, value: Any, *args, **kwarg) -> Item:
        """Transform the value to a valid Item"""


@portlink(Register)
class BaseVault[Item, V: _reg.Vault](VaultCore[Item, V]):
    """Provide initial Setup"""

    policy = PolicyField(VaultPolicy, default=VaultPolicy.RAISE)
    ident = StrategyField(lambda item: hash(item))

    def __init__(
        self,
        initial: V | Iterable | Mapping | None = None,
        *,
        ident: _reg.Ident[Item] | None = None,
    ) -> None:
        self.ident: _reg.Ident[Item] | None = ident
        self.vault: V = self._as_vault(initial)

    def add(self, data: Item | V, override: bool = False) -> V:
        """Extend vault by Items, get removed files back"""

        incoming: V = self._as_vault(data)
        collisions = self._collisions(incoming)
        if override:
            self.vault, displaced = self._subtract(self.vault, collisions)
            self.vault = self._merge(self.vault, incoming)
            return displaced
        fresh, skipped = self._subtract(incoming, collisions)
        self.vault = self._merge(self.vault, fresh)
        return skipped

    def clear(self, query: _reg.Selector[Item] | None = None) -> V:
        """Remove all Items or remove filtered  by identifier"""
        if query is None:
            displaced, self.vault = self.vault, self._empty()
            return displaced
        displaced = self.find(query)
        self.vault, _ = self._subtract(self.vault, displaced)
        return displaced

    def find(self, query: _reg.Selector[Item]) -> V:
        """Provide 0..N items that match the item identifier"""
        return self._select(query)

    def count(self, query: _reg.Selector[Item]) -> int:
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
