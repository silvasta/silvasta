"""
Mixin for Functor Registries (FuncRegister)

- Ensures all registered and incoming functors have their `_emit` wired

                         DependencyLevel.sstcore.brick.vault[1.2.0]
"""

from copy import replace

__all__: list[str] = [
    "FuncVault",
]

from collections.abc import Callable
from typing import Any

from ...port.event.emit import LogEmit
from ...port.functorial import Functorial


class FuncVault[Item: Functorial]:
    """Wire `_emit` across all existing and future functors in the vault"""

    __getitem__: Any

    def wire(self, emit: Callable[..., None]) -> None:
        """Attach _emit to all currently and future stored Functors"""
        self._emit = emit
        for functor in self:
            functor._emit = (
                replace(emit, sender=emit.sender or functor.__name__)  # ty:ignore
                if isinstance(emit, LogEmit)
                else emit
            )

    def _bind_emit(self, functor: Item) -> Item:
        """Attach _emit to Functors in _normalize"""
        if (emit := getattr(self, "_emit", None)) is not None:
            functor._emit = (
                emit.bind(sender=functor.__name__)
                if hasattr(emit, "bind")
                else emit
            )
        return functor
