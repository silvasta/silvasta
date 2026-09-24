from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from typing import Any

from ....port.raising import SstCoreError

type Vaults = Sequence | Mapping


class RegistryError(SstCoreError): ...


class BaseRegistry[Item, Vault: Vaults, U, A]:
    vault: Vault
    _ident: Callable[[Item], A] | None

    def __init__(
        self,
        initial: Vault | Iterable | Mapping | None = None,
        *,
        ident: Callable[[Item], A] | None = None,
    ) -> None:
        self._ident = ident
        self.vault = self._as_vault(initial)

    # -- protocol: written once -----------------------------------------

    def add(self, items: Vault, override: bool = False) -> Vault:
        # NEXT:
        incoming = self._as_vault(items)
        collisions = self._collisions(incoming)
        if override:
            self.vault, displaced = self._subtract(self.vault, collisions)
            self.vault = self._merge(self.vault, incoming)
            return displaced
        fresh, skipped = self._subtract(incoming, collisions)
        self.vault = self._merge(self.vault, fresh)
        return skipped

    def clear(self, id: A | None = None) -> Vault:
        if id is None:
            displaced, self.vault = self.vault, self._empty()
            return displaced
        displaced = self.find(id)
        self.vault, _ = self._subtract(self.vault, displaced)
        return displaced

    def find(self, id: A) -> Vault:
        return self._select(id)

    def count(self, id: A) -> int:
        return len(self.find(id))

    def get(self, uid: U) -> Item:
        item = self._at(uid)
        if item is None:
            raise RegistryError(f"Registry key {uid!r} not found", uid)
        return item

    def __getitem__(self, index: U | slice) -> Item | Vault:
        if isinstance(index, slice):
            return self._slice(index)
        return self.get(index)

    def __len__(self) -> int:
        return len(self.vault)

    def __iter__(self) -> Iterator[Item]:
        yield from self._items()

    def __contains__(self, target: Item) -> bool:
        return any(item == target for item in self._items())

    # -- primitives (override per family) --------------------------------

    def _empty(self) -> Vault:
        raise NotImplementedError

    def _as_vault(self, items: Any) -> Vault:
        raise NotImplementedError

    def _merge(self, vault: Vault, incoming: Vault) -> Vault:
        raise NotImplementedError

    def _subtract(self, vault: Vault, targets: Vault) -> tuple[Vault, Vault]:
        raise NotImplementedError

    def _collisions(self, incoming: Vault) -> Vault:
        raise NotImplementedError

    def _at(self, uid: U) -> Item | None:
        raise NotImplementedError

    def _select(self, id: A) -> Vault:
        raise NotImplementedError

    def _slice(self, s: slice) -> Vault:
        raise RegistryError(f"Slicing not supported: {s!r}", s)

    def _items(self) -> Iterator[Item]:
        yield from self.vault
