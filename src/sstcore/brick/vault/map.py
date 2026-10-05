"""
Mapping Registry - Dict, Map, ...

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "Mapped",
    "DictVault",
]


from collections.abc import Iterator
from typing import Any

from ...port.link import portlink
from ...port.register import DictRegister
from .base import BaseVault


@portlink(DictRegister)
class Mapped[Item, K](BaseVault[Item, dict[K, Item]]):
    def _empty(self) -> dict[K, Item]:
        return {}

    def _as_vault(self, items: Any) -> dict[K, Item]:
        if items is None:
            return {}
        return dict(items)

    def _merge(
        self, vault: dict[K, Item], incoming: dict[K, Item]
    ) -> dict[K, Item]:
        return {**vault, **incoming}

    def _subtract(
        self, vault: dict[K, Item], targets: dict[K, Item]
    ) -> tuple[dict[K, Item], dict[K, Item]]:
        _removed = {k: vault[k] for k in targets if k in vault}
        _kept = {k: v for k, v in vault.items() if k not in targets}
        return _kept, _removed

    def _collisions(self, incoming: dict[K, Item]) -> dict[K, Item]:
        return {k: self.vault[k] for k in incoming if k in self.vault}

    def _at(self, uid: K) -> Item | None:
        if uid in self.vault:
            # CHECK: None should not be a valid option!
            # - either return empyt vault or raise
            return self.vault[uid]
        return None

    def _select(self, id: Any) -> dict[K, Item]:
        if id in self.vault:
            return {id: self.vault[id]}
        return {k: v for k, v in self.vault.items() if self.ident(v) == id}

    def _items(self) -> Iterator[Item]:
        yield from self.vault.values()

    def _slice(self, s: slice) -> dict[K, Item]:
        keys = list(self.vault.keys())[s]
        return {k: self.vault[k] for k in keys}


@portlink(DictRegister)
class DictVault[Item, K](Mapped[Item, K]): ...
