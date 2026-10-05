"""
Mapping Registry - Dict, Map, ...

- Ideas:
  - Adapt the edit/frozen pattern from PortLinks/PortLinkData

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "Mapped",
    "DictVault",
]


from collections.abc import Mapping, Sequence
from typing import Any

from ...port.link import portlink
from ...port.register import DictRegister
from ._base import BaseVault


@portlink(DictRegister)
class Mapped[K, Item](BaseVault[Item, dict[K, Item]]):
    def _empty(self) -> dict[K, Item]:
        return {}

    def _as_vault(self, data: Any) -> dict[K, Item]:
        if data is None:
            return {}
        if isinstance(data, Mapping):
            return dict(data)
        if isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
            return dict(data)  # pairs
        item: Item = self._normalize(data)  # bare item, keyed by ident
        return {self._item_id(item): item}

    def _merge(self, vault, incoming):
        return {**vault, **incoming}

    def _subtract(self, vault, targets):
        removed: dict[K, Item] = {k: vault[k] for k in targets if k in vault}
        kept: dict[K, Item] = {
            k: v for k, v in vault.items() if k not in targets
        }
        return kept, removed

    def _collisions(self, incoming):
        return {k: self.vault[k] for k in incoming if k in self.vault}

    def _iter_items(self):
        yield from self.vault.values()

    def _index_item(self, idx: int) -> Item:
        key: K = list(self.vault)[self._normalize_index(idx)]
        return self.vault[key]

    def _index_put(self, idx: int, item: Item) -> None:
        key = list(self.vault)[self._normalize_index(idx)]
        self.vault[key] = item

    def _key_item(self, key: str) -> Item:
        if key not in self.vault:
            raise KeyError(key)
        return self.vault[key]

    def _key_put(self, key: str, item: Item) -> None:
        self.vault[key] = item

    def _slice(self, s: slice) -> dict[K, Item]:
        return {k: self.vault[k] for k in list(self.vault)[s]}


@portlink(DictRegister)
class DictVault[Item, K](Mapped[Item, K]): ...
