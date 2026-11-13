import inspect
from collections.abc import Callable
from enum import Enum
from typing import Any

from pydantic.v1.generics import CacheKey

from src.sstcore.port.structures._dataclass import create_field_resolver
from src.sstcore.port.structures._enumfield import BoundEnumField

from ._tuple import HashedTuple


class CacheMap[K, V](dict[K, V]):
    """Compute-on-miss storage: the factory travels with the request.

    Use when the factory needs request-time context (args, closures).
    """

    def get_or_create(self, key: K, factory: Callable[[], V]) -> V:
        try:
            return self[key]
        except KeyError:
            self[key] = factory()
            return self[key]


class LazyMap[K, V](dict[K, V]):
    """Compute-on-miss storage: the factory depends on the key only."""

    def __init__(self, compute: Callable[[K], V] | None = None) -> None:
        self._compute_fn: Callable[[K], V] | None = compute

    def compute(self, key: K) -> V:
        """Override in a subclass, or hand the map a callable."""
        if self._compute_fn is None:
            raise NotImplementedError(key)
        return self._compute_fn(key)

    def __missing__(self, key: K) -> V:
        self[key] = self.compute(key)
        return self[key]


class DcMeta(type):
    def __call__(cls, *args, **kwargs):
        bound: inspect.BoundArguments = cls.__signature__.bind(*args, **kwargs)
        provided_args: set[str] = set(bound.arguments.keys())
        bound.apply_defaults()

        _resolve_field_value = create_field_resolver(cls, provided_args)
        cache_key: CacheKey = tuple(
            HashedTuple(name, _resolve_field_value(name, value))
            for name, value in bound.arguments.items()
        )
        create = (
            super().__call__
        )  # bind once: zero-arg super() dies inside a lambda
        return cls._cache.get_or_create(
            cache_key, lambda: create(*args, **kwargs)
        )


class EnumFiiield[ValueT]:
    def _(self):
        self._slots: LazyMap[type[Any], BoundEnumField[Any, ValueT]] = LazyMap(
            lambda owner: BoundEnumField(
                owner=owner,
                name=self._name,
                loader=self._loader,
                default=self._default,
                fallback=self._fallback,
            )
        )

    def _slot_for[E: Enum](self, owner: type[E]) -> BoundEnumField[E, ValueT]:
        return self._slots[owner]


class Lazy[V]:
    """Call-once thunk: the '_loader_ran' flag as an object."""

    def __init__(self, source: Callable[[], V]) -> None:
        self._source = source
        self._value: V | None = None
        self._done = False

    def __call__(self) -> V:
        if not self._done:
            self._value = self._source()
            self._done = True
        return self._value
