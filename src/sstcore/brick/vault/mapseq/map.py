from collections.abc import Iterator
from typing import Any

from .base import BaseRegistry


class MappingRegistry[Item, K, A](BaseRegistry[Item, dict[K, Item], K, A]):
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
        removed = {k: vault[k] for k in targets if k in vault}
        kept = {k: v for k, v in vault.items() if k not in targets}
        return kept, removed

    def _collisions(self, incoming: dict[K, Item]) -> dict[K, Item]:
        return {k: self.vault[k] for k in incoming if k in self.vault}

    def _at(self, uid: K) -> Item | None:
        if uid in self.vault:
            return self.vault[uid]
        return None

    def _select(self, id: A) -> dict[K, Item]:
        if id in self.vault:  # type: ignore[operator]
            return {id: self.vault[id]}  # type: ignore[index,dict-item]
        if self._ident is None:
            return {}
        return {k: v for k, v in self.vault.items() if self._ident(v) == id}

    def _items(self) -> Iterator[Item]:
        yield from self.vault.values()

    def _slice(self, s: slice) -> dict[K, Item]:
        keys = list(self.vault.keys())[s]
        return {k: self.vault[k] for k in keys}


class DictRegistry[Item, K, A](MappingRegistry[Item, K, A]): ...
