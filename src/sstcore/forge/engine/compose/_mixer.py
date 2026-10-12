"""
Define Functions and Rules to Combine Mixins

- Export as module: 'mixer' ?
- Export as module: 'inject' ?
- Export as module: 'build' ?

"""

from src.sstcore.port.shape import Builder

__all__: list[str] = [
    "Combine",
    "NameSpace",
]


from typing import Any


class Combine:
    @staticmethod
    def combine(  # LATER: naming!! and sort!
        mixins: tuple[type, ...],
        extras: tuple[type, ...],
        *,
        prepend: bool = True,
    ) -> tuple[type, ...]:
        """Place ephemeral mixins before (override) or after (fallback) the recipe"""
        if not extras:
            return mixins
        return extras + mixins if prepend else mixins + extras


class NameSpace:
    @staticmethod
    def composition(
        cls: type | None = None,
        extras: dict | None = None,
    ) -> dict[str, Any]:
        """Extract module information so the new class belongs to the caller's scope, not the forge."""

        namespace: dict[str, Any] = extras or {}

        if cls:
            namespace.setdefault("__module__", cls.__module__)
            namespace.setdefault("__qualname__", cls.__qualname__)

        return namespace

    @staticmethod
    def injection(
        cls: type,
        extras: dict | None = None,
        spec: Builder | None = None,
    ) -> dict[str, Any]:
        """Extract module information so the new class belongs to the caller's scope, not the forge."""

        namespace: dict[str, Any] = extras or {}

        namespace.setdefault("__module__", cls.__module__)
        namespace.setdefault("__qualname__", cls.__qualname__)
        if spec:
            namespace["__view_spec__"] = spec

        if hasattr(cls, "model_config"):  # Pydantic support
            namespace["model_config"] = getattr(cls, "model_config", {})

        return namespace
