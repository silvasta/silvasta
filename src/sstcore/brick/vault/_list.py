"""
ListRegistry - Main Variation of the Core Registry

-
"""

__all__: list[str] = [
    "ListRegistry",
]

from typing import TYPE_CHECKING, Any, Literal

from ...port.register import ListRegister
from ._base import BaseRegistry


class ListRegistry[Item](BaseRegistry[Item, list, int, Any]):
    """Implement the Shape of the Registry with List"""

    _prefered: Literal["str", "int"] = "int"

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


if TYPE_CHECKING:
    _instance: ListRegister = ListRegistry()
    _class: type[ListRegister] = ListRegistry
