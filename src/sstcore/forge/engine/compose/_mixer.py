"""
Define Functions and Rules to Combine Mixins

- Export as module: 'mixer' ?
- Export as module: 'inject' ?
- Export as module: 'build' ?

"""

__all__: list[str] = [
    "Combine",
    "NameSpace",
]

# LATER: this as 1 out of multiple sort options
from typing import Any


class Combine:
    @staticmethod
    def combine(
        mixins: tuple[type, ...],
        extras: tuple[type, ...],
        *,
        set_pre: bool = True,
    ) -> tuple[type, ...]:
        """Place ephemeral mixins before (override) or after (fallback) the recipe"""
        if not extras:
            return mixins
        return extras + mixins if set_pre else mixins + extras


class NameSpace:
    @staticmethod
    def prepare1(
        cls: type | None = None, extras: dict | None = None
    ) -> dict[str, Any]:
        """Extract module information so the new class belongs to the caller's scope, not the forge."""
        namespace: dict[str, Any] = extras or {}
        if cls:
            namespace.setdefault("__module__", cls.__module__)
            namespace.setdefault("__qualname__", cls.__qualname__)
        return namespace
