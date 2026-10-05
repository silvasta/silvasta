"""
BaseVault - Final assembled brick ready to be built

-
"""

__all__: list[str] = [
    "BaseVault",
]


from collections.abc import Iterable, Iterator, Mapping

from ...brick.field import StrategyField
from ...port.register import VaultPolicy
from ...port.register import registry_types as _reg
from ..field import PolicyField
from ._kernel import VaultCore


class BaseVault[Item, V: _reg.Vault](VaultCore[Item, V]):
    policy = PolicyField(VaultPolicy, default=VaultPolicy.RAISE)
    ident = StrategyField(lambda item: hash(item))  # WARN: proper default?

    def __init__(
        self,
        initial: V | Iterable | Mapping | None = None,
        *,
        ident: _reg.Ident[Item] | None = None,
        policy: VaultPolicy | None = None,
    ) -> None:
        if ident is not None:
            self.ident: _reg.Ident[Item] = ident
        if policy is not None:
            self.policy: VaultPolicy = policy
        self.vault: V = self._as_vault(initial)

    def add(self, data: Item | V) -> V:
        incoming: V = self._as_vault(data)
        collisions: V = self._collisions(incoming)
        if not collisions:
            self.vault: V = self._merge(self.vault, incoming)
            return self._empty()

        match self.policy:  # NOTE: this as well for __setitem__?
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

    def clear(self, query: _reg.Selector[Item] | None = None) -> V:
        if query is None:
            displaced, self.vault = self.vault, self._empty()
            return displaced
        displaced: V = self.find(query)
        self.vault, _ = self._subtract(self.vault, displaced)
        return displaced

    def find(self, query: _reg.Selector[Item]) -> V:
        match query:
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

    def count(self, query: _reg.Selector[Item]) -> int:
        return len(self.find(query))

    # IDEA: move below to abstract or to core?
    def __len__(self) -> int:
        return len(self.vault)

    def __iter__(self) -> Iterator[Item]:
        yield from self._iter_items()

    def __contains__(self, target: Item) -> bool:
        return any(item == target for item in self._iter_items())
