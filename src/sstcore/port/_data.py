"""
Define the Behaviour of DataClasses

- CachedDataclassMeta: Flyweight Cache
- ParamSpec: Root for Input Parsing

"""

# LATER: "ParamSpec",

__all__: list[str] = [
    "CachedDataclassMeta",
    "create_field_resolver",
]


import inspect
from dataclasses import MISSING
from typing import Any

from ._frozen import HashedTuple

type CacheKey = tuple[HashedTuple, ...]
type DataClass[T: type] = T  # hint for reader


class CachedDataclassMeta(type):
    """
    Intercept DataClass.__init__ to provide Flyweight Cache

    - Bypass regular instantiation on Cache Hits

    Warning: Limitations & Future Pipeline Pitfalls
     1. Non-Deterministic Factories: Avoid random, UUID, or timestamp
        factories. They execute during cache key generation and again on
        instantiation, causing permanent misses and silent cache bloat.
     2. Immutability (Shared State): Fetched instances are globally shared.
        Mutating an instance post-creation corrupts the cached state for
        all subsequent retrievals.

    """

    def __init__(cls, name: str, bases: tuple, namespace: dict[str, Any]):
        """Setup Cache and lazy load Signature to avoid import-time overhead"""
        super().__init__(name, bases, namespace)
        cls._cache: dict[CacheKey, DataClass] = {}
        cls._sig: inspect.Signature | None = None

    @property
    def __signature__(cls) -> inspect.Signature:
        """Expose DataClass.__init__ signature instead of Meta.__call__"""
        if cls._sig is None:
            sig: inspect.Signature = inspect.signature(cls.__init__)
            cls._sig: inspect.Signature = sig.replace(
                parameters=tuple(sig.parameters.values())[1:]
            )
        return cls._sig

    def __call__(cls, *args, **kwargs):
        """
        Bypass __init__ on cached hits and avoid dataclass FrozenInstanceError

        - Map Arg/Kwargs using the DataClass Signature
        - Build Hashable CacheKey by normalizing unhashable list/set/maps
        - Provide fetched unique Instance, create and cache if needed

        """
        bound: inspect.BoundArguments = cls.__signature__.bind(*args, **kwargs)
        provided_args: set[str] = set(bound.arguments.keys())
        bound.apply_defaults()

        _resolve_field_value = create_field_resolver(cls, provided_args)

        cache_key: CacheKey = tuple(
            HashedTuple(name, _resolve_field_value(name, value))
            for name, value in bound.arguments.items()
        )

        if cache_key not in cls._cache:
            cls._cache[cache_key] = super().__call__(*args, **kwargs)

        return cls._cache[cache_key]


def create_field_resolver(cls: DataClass, provided_args: set[str]):
    """Pre-load dataclass fields to resolve missing defaults"""

    fields: dict[str, Any] = getattr(cls, "__dataclass_fields__", {})

    def resolve(name: str, value: Any) -> Any:
        if name in provided_args or (field := fields.get(name)) is None:
            return value

        if field.default_factory is not MISSING:
            return field.default_factory()
        if field.default is not MISSING:
            return field.default

        return value

    return resolve
