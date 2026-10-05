"""
- Delete after IMPL

 .
"""

from typing import Any


class V1[Item, Vault, U, A: Any]:
    """Provide initial Setup"""

    def _clear_all(self) -> None:
        raise NotImplementedError

    def _slice_action(self, s: slice) -> Any:
        raise NotImplementedError

    def _str_action(self, k: str) -> Any:
        raise NotImplementedError

    def _item_action(self, target: Item) -> Any:
        raise NotImplementedError

    def _int_action(self, i: int) -> Item | None:
        raise NotImplementedError

    def _sanitize(self, result: Vault | Item | None) -> Vault:
        raise NotImplementedError

    def _remove(self, targets: Vault) -> Vault:
        """Return all removed"""
        raise NotImplementedError

    def _append(self, items: Vault) -> Vault:
        """Return all duplicated"""
        raise NotImplementedError

    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
