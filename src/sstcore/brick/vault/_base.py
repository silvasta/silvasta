"""
BaseVault - Final assembled brick ready to be built

-
"""

from typing import Any

__all__: list[str] = [
    "BaseVault",
]


from collections.abc import Iterable, Iterator, Mapping

from ...brick.field import StrategyField
from ...port.link import portlink
from ...port.register import Register, VaultPolicy
from ...port.register import registry_types as _r
from ..field import PolicyField
from ._access import VaultAccess


@portlink(Register)
class BaseVault[Item, V: _r.Vault](VaultAccess[Item, V]):
    """Establish the port definition for further specification"""

    policy = PolicyField(VaultPolicy)
    ident = StrategyField(lambda item: item)

    def __init__(
        self,
        initial: V | Iterable | Mapping | None = None,
        *,
        ident: _r.Ident[Item] | None = None,
        policy: VaultPolicy | None = None,
    ) -> None:
        if ident is not None:
            self.ident: _r.Ident[Item] = ident
        if policy is not None:
            self.policy: VaultPolicy = policy
        self.vault: V = self._as_vault(initial)

    def add(self, data: Item | V) -> V:
        incoming: V = self._as_vault(data)
        collisions: V = self._collisions(incoming)
        if not collisions:
            self.vault: V = self._merge(self.vault, incoming)
            return self._empty()

        match self.policy:
            case VaultPolicy.RAISE:
                raise ValueError("vault collision")

            case VaultPolicy.SKIP:
                _fresh, _skipped = self._subtract(incoming, collisions)
                self.vault: V = self._merge(self.vault, _fresh)
                return _skipped

            case VaultPolicy.MERGE:
                self.vault, _displaced = self._subtract(self.vault, collisions)
                self.vault: V = self._merge(self.vault, incoming)
                return _displaced
            case _:
                raise TypeError(f"Unsupported policy: {self.policy!r}")

    def clear(self, query: _r.Selector[Item] | None = None) -> V:
        if query is None:
            displaced, self.vault = self.vault, self._empty()
            return displaced
        displaced: V = self.find(query)
        self.vault, _ = self._subtract(self.vault, displaced)
        return displaced

    def find(self, query: _r.Selector[Item]) -> V:
        q: Any = query
        match q:
            case int() as idx if not isinstance(idx, bool):
                return self._box_index(idx)
            case str() as key:
                return self._box_key(key)
            case slice() | tuple() as many:
                return self[many]
            case fn if callable(fn):
                return self._where(fn)
            case _:
                raise TypeError(f"Unsupported: {type(query).__name__}")

    def count(self, query: _r.Selector[Item]) -> int:
        return len(self.find(query))

    # NOTE: beside the gap here (filled by core) it follows perfectly the protocol

    def __len__(self) -> int:
        return len(self.vault)

    def __iter__(self) -> Iterator[Item]:
        yield from self._iter_items()

    def __contains__(self, target: Item) -> bool:
        return any(item == target for item in self._iter_items())

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def _replace_where(self, fn: _r.Predicate[Item], item: Item) -> None:
        hits: list[int] = [i for i, current in enumerate(self) if fn(current)]
        for i in hits:
            self._index_put(i, item)
