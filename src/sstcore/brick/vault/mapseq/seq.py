from typing import Any

from .base import BaseRegistry


class SequenceRegistry[Item, Vault: list | tuple, A](
    BaseRegistry[Item, Vault, int, A]
):
    def _empty(self) -> Vault:
        return type(self.vault)()

    def _as_vault(self, items: Any) -> Vault:
        if items is None:
            return self._empty()
        if type(items) is type(self.vault) or isinstance(items, (list, tuple)):
            return type(self.vault)(items)  # type: ignore[call-arg]
        return type(self.vault)(items)  # type: ignore[call-arg]

    def _merge(self, vault: Vault, incoming: Vault) -> Vault:
        return type(vault)((*vault, *incoming))  # type: ignore[call-arg]

    def _subtract(self, vault: Vault, targets: Vault) -> tuple[Vault, Vault]:
        # NEXT:
        wanted = list(targets)
        keep, removed = [], []
        for item in vault:
            bucket = removed if item in wanted else keep
            bucket.append(item)
            if item in wanted:
                wanted.remove(item)  # one-for-one, preserves duplicates
        ctor = type(vault)
        return ctor(keep), ctor(removed)  # type: ignore[call-arg]

    def _collisions(self, incoming: Vault) -> Vault:
        if self._ident is None:
            return type(self.vault)(x for x in self.vault if x in incoming)  # type: ignore[call-arg]
        incoming_ids = {self._ident(x) for x in incoming}
        return type(self.vault)(  # type: ignore[call-arg]
            x for x in self.vault if self._ident(x) in incoming_ids
        )

    def _at(self, uid: int) -> Item | None:
        n = len(self.vault)
        if isinstance(uid, int) and -n <= uid < n:
            return self.vault[uid]
        return None

    def _select(self, id: A) -> Vault:
        if self._ident is None:
            return type(self.vault)(x for x in self.vault if x == id)  # type: ignore[call-arg]
        return type(self.vault)(  # type: ignore[call-arg]
            x for x in self.vault if self._ident(x) == id
        )

    def _slice(self, s: slice) -> Vault:
        return self.vault[s]  # type: ignore[index,return-value]


class ListRegistry[Item, A](SequenceRegistry[Item, list, A]):
    def __init__(self, initial=None, *, ident=None) -> None:
        super().__init__(list(initial or []), ident=ident)


class TupleRegistry[Item, A](SequenceRegistry[Item, tuple, A]):
    def __init__(self, initial=None, *, ident=None) -> None:
        super().__init__(tuple(initial or ()), ident=ident)
