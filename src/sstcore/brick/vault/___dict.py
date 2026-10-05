"""
DictRegistry - Main Variation of the Core Registry

-
"""

__all__: list[str] = [
    "DictRegistry",
]

from typing import TYPE_CHECKING, Any

from ...port.register import DictRegister
from ._base import BaseRegistry


class DictRegistry[Item](BaseRegistry[Item, dict, int, Any]):
    """Implement the Shape of the Registry with Dict"""

    def add(self, items: dict, override: bool = False) -> dict[str, Item]:
        cleared: dict[str, Item] = {}
        for key, item in items:
            if override:
                cleared.update(self.clear(key))
            self.vault.update(**{key: item})
        return cleared

    def clear(self, *keys) -> [str, Item]:
        # AI: outdated
        cleared: dict[str, Item] = {}
        if not keys:
            self.vault.clear()
        else:
            for key in keys:
                if item := self.vault.pop(key, None):
                    cleared[key] = item
        return cleared

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def _clear_all(self) -> None:
        self.vault.clear()

    def _slice_action(self, s: slice) -> dict[str, Item]:
        return {
            k: v
            for k, v in zip(  # noqa:B905
                list(self.vault.keys())[s],
                list(self.vault.values())[s],
            )
        }

    def _str_action(self, k: str) -> Any:
        return self[k]

    def _item_action(self, target: Item) -> Any:
        return {}

    def _int_action(self, i: int) -> Item | None:
        if 0 < i < len(self):
            return list(self.vault)[i]

    def _sanitize(self, result: dict | Item | None) -> dict:
        match result:
            case None:
                return {}
            case dict():
                return result
            case _:
                return {0: result}  # unclean...

    def _remove(self, targets: dict) -> dict:
        """Return all removed"""
        return {target.pop(k) for k, target in enumerate(targets)}

    def _append(self, vault: dict[str, Item]):
        """Return all duplicated"""
        self.vault.update(vault)

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


if TYPE_CHECKING:
    _instance: DictRegister = DictRegistry()
    _class: type[DictRegister] = DictRegistry
