"""
Define the Behaviour of DataClasses

- CachedDataclassMeta: Flyweight Cache
- ParamSpec: Root for Input Parsing

"""

__all__: list[str] = [
    "HashedTuple",
    "frozendict",
]


import sys
from collections.abc import Hashable, Iterable, Iterator, Mapping
from functools import partial
from typing import Any, NamedTuple, Self, TypeIs, overload

if sys.version_info >= (3, 15):
    from builtins import frozendict
else:

    class frozendict[K, V](Mapping[K, V]):  # noqa: N801
        """Simulate the FrozenDict for Python 3.14"""

        __slots__ = ("_mapping", "_hash_cache")

        @overload
        def __init__(
            self,
            iterable: Mapping[K, V] | Iterable[tuple[K, V]] = (),
            /,
        ) -> None: ...
        @overload
        def __init__(
            self,
            iterable: Mapping[str, V] | Iterable[tuple[str, V]] = (),
            /,
            **kwargs: V,
        ) -> None: ...
        def __init__(
            self,
            iterable=(),
            /,
            **kwargs,
        ) -> None:
            self._mapping: dict[K, V] = dict(iterable, **kwargs)  # ty:ignore
            self._hash_cache: int | None = None

        def __getitem__(self, key: K) -> V:
            return self._mapping[key]

        def __contains__(self, key: Any) -> bool:
            return key in self._mapping

        def __iter__(self) -> Iterator[K]:
            return iter(self._mapping)

        def __len__(self) -> int:
            return len(self._mapping)

        def __str__(self) -> str:
            return f"{type(self).__name__}[{len(self)}]"

        def __repr__(self) -> str:
            return f"{self}({self._mapping!r})"

        def copy(self) -> Self:
            return self

        def __hash__(self) -> int:
            if self._hash_cache is None:
                self._hash_cache: int = hash(frozenset(self._mapping.items()))
            return self._hash_cache

        def __or__(self, other: Any) -> Self:
            if isinstance(other, Mapping):
                return type(self)({**self._mapping, **other})
            return NotImplemented

        def __ror__(self, other: Any) -> Self:
            if isinstance(other, Mapping):
                return type(self)({**other, **self._mapping})
            return NotImplemented


class _HashedTupleBase(NamedTuple):
    """Assign Attrs and Unlock __new__ for subclasses"""

    name: str
    value: Hashable


class HashedTuple(_HashedTupleBase):
    """Named and auto-ensured Hashable component for deterministic CacheKeys"""

    def __new__(cls, name: str, value: Any, /, *, strict=True):
        """Make value Hashable before instantiation"""
        return tuple.__new__(cls, (name, cls.hash(value, strict=strict)))

    @staticmethod
    def accepts(target) -> bool:
        """Ultimate check if Hash can be generated"""
        try:
            hash(target)
            return True
        except TypeError:
            return False

    @staticmethod
    def hash(target: Any, /, *, strict=True) -> Hashable:
        """
        Transform Mutable or nested structures into Hashable Objects

        - Deterministic Order for reliable Dict caching
        - Base iterables become frozensets
        - Final attempt: Convert unknown iterables to tuple
          - strict=True raises while strict=False converts to (random) string

        """
        if HashedTuple.accepts(target):
            return target

        _hash = partial(HashedTuple.hash, strict=strict)

        match target:
            case list() | tuple():
                return tuple(_hash(value) for value in target)

            case set() | frozenset():
                return frozenset(_hash(value) for value in target)

            case Mapping():
                return frozendict(
                    {_hash(key): _hash(value) for key, value in target.items()}
                )
        return HashedTuple._fallback(target, strict=strict)

    @staticmethod
    def _fallback(target: Any, /, *, strict: bool = True) -> Hashable:
        """Final Attempt to make Target Hashable"""
        try:
            return tuple(HashedTuple.hash(x, strict=strict) for x in target)
        except TypeError as error:
            _target: str = HashedTuple._format(target)
            if not strict:
                return _target
            raise TypeError(f"Unhashable for Cache: {_target}") from error

    @staticmethod
    def _format(target):
        """Subhook for failed target in HashedTuple.hash"""
        return f"{type(target).__name__}::{target}"

    def __str__(self):
        return f"{type(self).__name__}{{{self.name}:{self._show}}}"

    @property
    def _show(self) -> str:
        """Subhook to format infos from HashedTuple.value"""
        length: str = f"[{len(self.value)}]" if is_hash_ittr(self.value) else ""
        return f"{type(self.value).__name__}{length}"


def is_hash_ittr(target: Hashable, /) -> TypeIs[tuple | frozenset | frozendict]:
    return isinstance(target, (tuple, frozenset, frozendict))
