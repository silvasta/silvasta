"""
Mapping Registry - Dict, Map, ...

- Ideas:
  - Adapt the edit/frozen pattern from PortLinks/PortLinkData

                                                       DependencyLevel[0]
"""

from sstcore._types._registry import Predicate

__all__: list[str] = [
    "Mapped",
    "DictVault",
]


from collections.abc import Iterator, Mapping, Sequence
from typing import Any, cast

from ...port.link import portlink
from ...port.register import DictRegister
from ._base import BaseVault


class Mapped[Item, K](BaseVault[Item, dict[K, Item]]):
    """Implement the Contract"""

    def _coerce_key(self, key: str) -> K:  # CHECK: this is a solution?
        return cast(K, key)

    def _empty(self) -> dict[K, Item]:
        return {}

    def _as_vault(self, data: Any) -> dict[K, Item]:
        if data is None:
            return {}
        if isinstance(data, Mapping):
            return {cast(K, k): self._normalize(v) for k, v in data.items()}
        if isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
            items: list[Item] = [self._normalize(x) for x in data]
            return {cast(K, self._item_id(item)): item for item in items}
        item: Item = self._normalize(data)
        return {cast(K, self._item_id(item)): item}

    def _merge(
        self, vault: dict[K, Item], incoming: dict[K, Item]
    ) -> dict[K, Item]:
        return {**vault, **incoming}

    def _subtract(
        self, vault: dict[K, Item], targets: dict[K, Item]
    ) -> tuple[dict[K, Item], dict[K, Item]]:
        removed: dict[K, Item] = {k: vault[k] for k in targets if k in vault}
        kept: dict[K, Item] = {
            k: v for k, v in vault.items() if k not in targets
        }
        return kept, removed

    def _collisions(self, incoming: dict[K, Item]) -> dict[K, Item]:
        return {k: self.vault[k] for k in incoming if k in self.vault}

    def _iter_items(self) -> Iterator[Item]:
        yield from self.vault.values()

    def _index_item(self, idx: int) -> Item:
        key: K = list(self.vault)[self._normalize_index(idx)]
        return self.vault[key]

    def _index_put(self, idx: int, item: Item) -> None:
        key: K = list(self.vault)[self._normalize_index(idx)]
        self.vault[key] = item

    def _key_item(self, key: str) -> Item:
        k: K = self._coerce_key(key)
        if k not in self.vault:
            raise KeyError(key)
        return self.vault[k]

    def _key_put(self, key: str, item: Item) -> None:
        self.vault[self._coerce_key(key)] = item

    def _box_index(self, idx: int) -> dict[K, Item]:
        key: K = list(self.vault)[self._normalize_index(idx)]
        return {key: self.vault[key]}

    def _box_key(self, key: str) -> dict[K, Item]:
        k: K = self._coerce_key(key)
        return {k: self.vault[k]}

    def _slice(self, s: slice) -> dict[K, Item]:
        return {k: self.vault[k] for k in list(self.vault)[s]}

    def _slice_put(self, s: slice, value: Any) -> None:
        pairs: list[tuple[K, Item]] = list(self.vault.items())
        pairs[s] = list(self._as_vault(value).items())
        self.vault: dict[K, Item] = dict(pairs)

    def _where(self, fn: Predicate[Item]) -> dict[K, Item]:
        return {k: v for k, v in self.vault.items() if fn(v)}


@portlink(DictRegister)
class DictVault[Item, K](Mapped[Item, K]): ...
