"""
Define the Behaviour of DataClasses

- CachedDataclassMeta: Flyweight Cache
- ParamSpec: Root for Input Parsing

                     DependencyLevel.sstcore.port.structures[0.1.2]
"""

__all__: list[str] = [
    "DataClass",
    "CachedDataclassMeta",
    "create_field_resolver",
    "SpecBase",
    "DataClassSpec",
    "ParamSpec",
    "ArgSpec",
]


import dataclasses as _dc
import inspect
import typing as _t
from collections.abc import Mapping
from dataclasses import MISSING
from typing import TYPE_CHECKING, Any, ClassVar, Self

from .._types import _DataClass as DataClass
from ..empty import VOID, MayBe, MayNot
from ..primitives import FieldSet, HashedTuple
from ._gate import CacheGate

type _CacheKey = tuple[HashedTuple, ...]


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

    if TYPE_CHECKING:
        __dataclass_fields__: ClassVar[dict[str, _dc.Field[Any]]]

    def __init__(cls, name: str, bases: tuple, namespace: dict[str, Any]):
        """Setup Cache and lazy load Signature to avoid import-time overhead"""
        super().__init__(name, bases, namespace)

        max_size: int | None = namespace.get(
            "__cache_max__", getattr(cls, "__cache_max__", None)
        )
        cls._cache: CacheGate[_CacheKey, DataClass] = CacheGate[
            _CacheKey, DataClass
        ](owner=cls, max_size=max_size)  # ty:ignore
        cls._sig: MayNot[inspect.Signature] = None

    @property
    def cache(cls) -> CacheGate[_CacheKey, Any]:
        """Public class-level gate: e.g. AttrFilter.cache.hits or print(AttrFilter.cache)"""
        return cls._cache

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
        - Build Hashable _CacheKey by normalizing unhashable list/set/maps
        - Provide fetched unique Instance, create and cache if needed

        """
        bound: inspect.BoundArguments = cls.__signature__.bind(*args, **kwargs)
        provided_args: set[str] = set(bound.arguments.keys())
        bound.apply_defaults()

        _resolve_field_value = create_field_resolver(cls, provided_args)

        cache_key: _CacheKey = tuple(
            HashedTuple(name, _resolve_field_value(name, value))
            for name, value in bound.arguments.items()
        )

        return cls._cache.fetch(
            cache_key,
            factory=lambda: super(CachedDataclassMeta, cls).__call__(
                *bound.args, **bound.kwargs
            ),
        )


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


#  LINE: -- Specs -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SpecBase:
    """Collect Utils for DataClasses and Specs"""

    if TYPE_CHECKING:
        __dataclass_fields__: ClassVar[dict[str, _dc.Field[Any]]]

    def evolve(self, **changes: Any) -> Self:
        """Provide new instance with updated fields"""
        return _dc.replace(self, **changes)

    def to_dict(self):
        """Extract all fields into dict without deepcopy"""
        return self.field_names().pull(self)

    @classmethod
    def field_names(cls, prefix: str = "") -> FieldSet:
        """Cached set of dataclass field names."""
        return FieldSet.absorb(cls, prefix=prefix)

    @classmethod
    def absorb(
        cls,
        kwargs: Mapping[str, Any],
        /,
        *,
        prefix: str = "",
        destroy: bool = True,
        **defaults: Any,
    ) -> Self:
        """Extract matching fields from kwargs to create new instance"""
        _plucked = cls.field_names(prefix=prefix).pluck(kwargs, destroy=destroy)
        return cls(**(defaults | _plucked))

    @classmethod
    def merge(cls, *specs: DataClass, **overrides: Any) -> Self:
        """Merge multiple partial specs shallowly into a composite spec."""
        return cls(**(cls.field_names().pull(*specs) | overrides))

    def extract[S: SpecBase](self, target_cls: type[S], **overrides) -> S:
        """Project matching fields from self into a target Spec class."""
        return target_cls.merge(self, **overrides)


#  LINE: -- Spec Origin -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_t.dataclass_transform(kw_only_default=True, frozen_default=True)
class DataClassSpec(SpecBase):
    """Base for Input-Sanitizing dataclass Specs"""

    def __init_subclass__(
        cls,
        *,
        kw_only: bool = True,
        frozen: bool | None = None,
        abstract: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        if not abstract:
            if frozen is None:
                frozen: bool = _has_frozen_base(cls)
            _dc.dataclass(kw_only=kw_only, frozen=frozen)(cls)


def _has_frozen_base(cls) -> bool:
    return any(
        getattr(base, "__dataclass_params__", None) is not None
        and base.__dataclass_params__.frozen
        for base in cls.__mro__[1:]
    )


#  LINE: -- Applied Specs -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ParamSpec(DataClassSpec, abstract=True):
    """Confirm Input and apply Defaults - Pair with TypedDict"""


class ArgSpec[T](DataClassSpec, frozen=True):
    """Single-Target Validation with ArgCast"""

    target: T

    @classmethod
    def ok(cls, target: MayBe[_t.Any] = VOID, /, **kwargs) -> T:
        """Execute all Steps and provide confirmed Target"""
        return cls.normalize(target, **kwargs).validate()

    @classmethod
    def normalize(cls, target: MayBe[_t.Any] = VOID, /) -> _t.Self:
        """Create ArgSpec with confirmed Input"""
        raise NotImplementedError(target)

    def validate(self) -> T:
        """Execute all Checks that the Target must fulfill"""
        return self.target


if __name__ == "__main__":
    from dataclasses import dataclass, field

    from rich import print

    @dataclass(frozen=True)
    class QueryFilter(metaclass=CachedDataclassMeta):
        __cache_max__ = 2  # small FIFO cap to show evictions

        name: str
        tags: list[str] = field(default_factory=lambda: ["core"])
        flags: dict[str, bool] = field(default_factory=dict)

    print(CacheGate.report())
    # 1. Miss -> creates and caches instance (unhashable list/dict normalized)
    f1 = QueryFilter("alpha", ["a", "b"], {"strict": True})
    print(CacheGate.report())

    # 2. Hit -> identical normalized key returns the exact same object
    f2 = QueryFilter(name="alpha", tags=["a", "b"], flags={"strict": True})
    assert f1 is f2

    print(CacheGate.report())
    # 3. Second unique entry (default_factory resolves to ["core"])
    f3 = QueryFilter("beta")

    print(CacheGate.report())
    # 4. Third unique entry exceeds __cache_max__ = 2 -> evicts "alpha" (FIFO)
    f4 = QueryFilter("gamma")

    print(CacheGate.report())
    # Inspect class-level CacheGate stats
    gate = QueryFilter.cache
    print(gate)
    # CacheGate[QueryFilter::+1|-3=4::(2)::Loader[empty]]
    print(
        f"hits={gate.hits}, misses={gate.misses}, "
        f"evictions={gate.evictions}, hit_rate={gate.hit_rate:.0%}"
    )
    # hits=1, misses=3, evictions=1, hit_rate=25%

    # Inspect all CacheGate instances registered across the process
    print(CacheGate.report())
    print()
    print(CachedDataclassMeta.cache)
    print()
    print(f"{CachedDataclassMeta.cache}")
    print()
    print(f"{QueryFilter.cache!r}")
    print(f"{QueryFilter.cache._data!r}")
