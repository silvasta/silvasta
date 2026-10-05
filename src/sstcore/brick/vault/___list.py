"""
ListRegistry - Main Variation of the Core Registry

-
"""

from typing import Any

__all__: list[str] = [
    "ListRegistry",
]


from ...port.link import portlink
from ...port.register import ListRegister
from .base import BaseVault


@portlink(ListRegister)
class ListRegistry[Item](BaseVault[Item, list, int, Any]):
    """Implement the Shape of the Registry with List"""

    def add(self, items: list[Item], override: bool = False) -> list[Item]:

        # INFO: outdated
        cleared: list[Item] = []
        for item in items:
            if override:
                cleared.extend(self.clear(self._item_identifier(item)))
            self.vault.append(item)
        return cleared

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def _clear_all(self):
        self.vault.clear()

    def _slice_action(self, s: slice) -> list[Item]:
        return self.vault[s]

    def _str_action(self, k: str) -> list[Item]:
        """Implement Filter for string attributes etc later here!"""
        return []

    def _item_action(self, target: Item) -> list[Item]:
        """Implement Filter for class attributes etc later here!"""
        return []

    def _int_action(self, i: int) -> Item | None:
        return self.vault[i]

    def _sanitize(self, result: list[Item] | Item | None) -> list[Item]:
        match result:
            case None:
                return []
            case list():
                return result
            case _:
                return [result]

    def _remove(self, targets: list[Item]) -> list[Item]:
        """Return all removed"""
        raise NotImplementedError

    def _append(self, items: list[Item]) -> list[Item]:
        """Return all duplicated"""
        self.vault.extend(items)

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __contains__(self, target: Item) -> bool:
        return target in self.vault  # Works
