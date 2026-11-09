"""
Create Mapping Container with Key and Value

                     DependencyLevel.sstcore.port.structures[0.1.0]
"""

__all__: list[str] = [
    "frozendict",
]

# NEXT: LinkRegistry, EditRegistry (better name, switch for (im-)mutable)

import sys
from collections.abc import Iterable, Iterator, Mapping
from typing import Any, Self, overload

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
