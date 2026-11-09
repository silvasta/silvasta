"""
Mixin for Functor Registries (FuncRegister)

- Ensures all registered and incoming functors have their `_emit` wired

                         DependencyLevel.sstcore.brick.vault[1.2.0]
"""

__all__: list[str] = [
    "FuncVault",
]

from collections.abc import Callable
from typing import Any

from ...port.functorial import Functorial


class FuncVault[Item: Functorial]:
    """Wire `_emit` across all existing and future functors in the vault"""

    _emit_hook: Callable[..., None] | None = None
    _iter_items: Any

    def wire(self, emit: Callable[..., None]) -> None:
        """Attach _emit to all currently and future stored Functors"""
        self._emit_hook = emit
        for functor in self._iter_items():
            functor._emit = emit

    def _bind_emit(self, item: Item) -> Item:
        """Attach _emit to Functors in _normalize"""
        if self._emit_hook is not None:
            item._emit = self._emit_hook
        return item
